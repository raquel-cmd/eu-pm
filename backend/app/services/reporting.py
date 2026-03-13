"""Service layer for reporting engine (Section 8).

Handles reporting period auto-generation, reporting calendar with
automated reminders, technical report workflow, and auto-generated
report sections from deliverable/milestone/financial data.
"""

import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.enums import (
    ReminderType,
    ReportingPeriodType,
    ReportSectionStatus,
    ReportSectionType,
    ReportStatus,
    RiskLevel,
    RiskStatus,
)
from app.models.project import Project
from app.models.reporting import (
    ReportingPeriod,
    ReportReminder,
    ReportSection,
    Risk,
    TechnicalReport,
)
from app.models.researcher import EffortAllocation, TimesheetEntry
from app.models.work_package import Deliverable, Milestone, WorkPackage
from app.schemas.reporting import (
    CalendarReminderItem,
    DeliverableSummaryItem,
    MilestoneSummaryItem,
    PartB2AutoData,
    PartB3AutoData,
    PartB4AutoData,
    ReportingCalendarResponse,
    ReportingPeriodCreate,
    ReportingPeriodResponse,
    RiskCreate,
    RiskSummaryItem,
    RiskUpdate,
    WPResourceRow,
    WorkflowStepInfo,
)
from app.services.timesheet import calculate_person_months

ZERO = Decimal("0.00")

# Reminder offsets: (ReminderType, days_before_deadline, description, recipients)
REMINDER_SCHEDULE = [
    (ReminderType.T_90, 90, "Report shell created; WP leaders and partners notified",
     "PI, WP Leaders, Partners"),
    (ReminderType.T_60, 60, "WP input collection window; deadline for WP leader drafts",
     "WP Leaders"),
    (ReminderType.T_45, 45, "Partner validation deadline",
     "Partners"),
    (ReminderType.T_30, 30, "PI/Coordinator consolidation phase begins",
     "PI"),
    (ReminderType.T_20, 20, "Institutional review phase — Central Finance PM cross-check",
     "Central Finance PM"),
    (ReminderType.T_15, 15, "Final review phase begins",
     "PI, Central Finance PM"),
    (ReminderType.T_7, 7, "Final edits, PDF generation, annexes preparation",
     "PI"),
]

WORKFLOW_STEPS = [
    (1, "Initiate", "System / PI", 90),
    (2, "WP Input", "WP Leaders", 60),
    (3, "Partner Input", "Partners", 45),
    (4, "Consolidation", "PI / Coordinator", 30),
    (5, "Internal Review", "PI + Central Finance PM", 15),
    (6, "Final Review", "PI", 7),
    (7, "Submission", "PI / Coordinator", 0),
]


def _q(value: Decimal | int | float | None) -> Decimal:
    """Quantize a decimal to 2 places."""
    if value is None:
        return ZERO
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# ──────────────────────────────────────────────────────
#  Reporting Period CRUD & Auto-Generation
# ──────────────────────────────────────────────────────


async def auto_generate_reporting_periods(
    db: AsyncSession, project_id: uuid.UUID
) -> list[ReportingPeriod]:
    """Auto-generate reporting periods from project grant agreement data.

    Uses project start_date, end_date, and the reporting_periods JSONB field
    (which contains period definitions from the grant agreement). If no JSONB
    data exists, generates 18-month periodic periods + a final period.
    """
    proj = await _get_project(db, project_id)
    if proj.start_date is None or proj.end_date is None:
        raise HTTPException(
            status_code=422,
            detail="Project must have start_date and end_date to generate periods",
        )

    # Check for existing periods
    existing = await list_reporting_periods(db, project_id)
    if existing:
        raise HTTPException(
            status_code=409,
            detail="Reporting periods already exist for this project",
        )

    # Parse from JSONB if available
    periods_data = proj.reporting_periods
    created: list[ReportingPeriod] = []

    if periods_data and isinstance(periods_data, list):
        for pd in periods_data:
            rp = ReportingPeriod(
                project_id=project_id,
                period_number=pd.get("period_number", len(created) + 1),
                period_type=ReportingPeriodType(
                    pd.get("period_type", "PERIODIC")
                ),
                start_date=date.fromisoformat(pd["start_date"]),
                end_date=date.fromisoformat(pd["end_date"]),
                technical_report_deadline=date.fromisoformat(
                    pd.get(
                        "technical_report_deadline",
                        (
                            date.fromisoformat(pd["end_date"])
                            + timedelta(days=60)
                        ).isoformat(),
                    )
                ),
                financial_report_deadline=(
                    date.fromisoformat(pd["financial_report_deadline"])
                    if pd.get("financial_report_deadline")
                    else None
                ),
            )
            db.add(rp)
            created.append(rp)
    else:
        # Default: 18-month periods
        period_months = 18
        current_start = proj.start_date
        period_num = 1

        while current_start < proj.end_date:
            period_end = _add_months(current_start, period_months)
            if period_end >= proj.end_date:
                period_end = proj.end_date
                p_type = ReportingPeriodType.FINAL
            else:
                p_type = ReportingPeriodType.PERIODIC

            deadline = period_end + timedelta(days=60)
            rp = ReportingPeriod(
                project_id=project_id,
                period_number=period_num,
                period_type=p_type,
                start_date=current_start,
                end_date=period_end,
                technical_report_deadline=deadline,
            )
            db.add(rp)
            created.append(rp)

            current_start = period_end + timedelta(days=1)
            period_num += 1

    await db.flush()
    for rp in created:
        await db.refresh(rp)
        await _generate_reminders_for_period(db, rp)

    await db.flush()
    return created


def _add_months(start: date, months: int) -> date:
    """Add months to a date, clamping to end of month."""
    month = start.month + months
    year = start.year + (month - 1) // 12
    month = (month - 1) % 12 + 1
    import calendar
    day = min(start.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


async def _generate_reminders_for_period(
    db: AsyncSession, period: ReportingPeriod
) -> list[ReportReminder]:
    """Generate all reminder records for a reporting period."""
    deadline = period.technical_report_deadline
    reminders: list[ReportReminder] = []

    for r_type, days_before, description, recipients in REMINDER_SCHEDULE:
        scheduled = deadline - timedelta(days=days_before)
        reminder = ReportReminder(
            reporting_period_id=period.id,
            reminder_type=r_type,
            scheduled_date=scheduled,
            recipient_description=recipients,
        )
        db.add(reminder)
        reminders.append(reminder)

    return reminders


async def create_reporting_period(
    db: AsyncSession,
    project_id: uuid.UUID,
    data: ReportingPeriodCreate,
) -> ReportingPeriod:
    """Manually create a reporting period."""
    await _get_project(db, project_id)
    rp = ReportingPeriod(project_id=project_id, **data.model_dump())
    db.add(rp)
    await db.flush()
    await db.refresh(rp)
    await _generate_reminders_for_period(db, rp)
    await db.flush()
    return rp


async def list_reporting_periods(
    db: AsyncSession, project_id: uuid.UUID
) -> list[ReportingPeriod]:
    """List all reporting periods for a project."""
    stmt = (
        select(ReportingPeriod)
        .where(
            ReportingPeriod.project_id == project_id,
            ReportingPeriod.deleted_at.is_(None),
        )
        .order_by(ReportingPeriod.period_number)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_reporting_period(
    db: AsyncSession, period_id: uuid.UUID
) -> ReportingPeriod | None:
    """Get a single reporting period."""
    stmt = select(ReportingPeriod).where(
        ReportingPeriod.id == period_id,
        ReportingPeriod.deleted_at.is_(None),
    )
    return (await db.execute(stmt)).scalar_one_or_none()


async def delete_reporting_period(
    db: AsyncSession, period_id: uuid.UUID
) -> bool:
    """Soft-delete a reporting period."""
    rp = await get_reporting_period(db, period_id)
    if rp is None:
        return False
    rp.deleted_at = datetime.now(timezone.utc)
    await db.flush()
    return True


# ──────────────────────────────────────────────────────
#  Reporting Calendar
# ──────────────────────────────────────────────────────


async def get_reporting_calendar(
    db: AsyncSession, project_id: uuid.UUID | None = None
) -> ReportingCalendarResponse:
    """Build the reporting calendar with upcoming deadlines and reminders."""
    today = date.today()

    # Get all active reporting periods
    stmt = select(ReportingPeriod).where(
        ReportingPeriod.deleted_at.is_(None),
    )
    if project_id is not None:
        stmt = stmt.where(ReportingPeriod.project_id == project_id)
    stmt = stmt.order_by(ReportingPeriod.technical_report_deadline)

    periods = list((await db.execute(stmt)).scalars().all())

    # Build period responses with days_until_deadline
    upcoming: list[ReportingPeriodResponse] = []
    for p in periods:
        days_until = (p.technical_report_deadline - today).days
        if days_until >= -30:  # Include recently past deadlines
            proj_stmt = select(Project.acronym).where(Project.id == p.project_id)
            upcoming.append(
                ReportingPeriodResponse(
                    id=p.id,
                    project_id=p.project_id,
                    period_number=p.period_number,
                    period_type=p.period_type,
                    start_date=p.start_date,
                    end_date=p.end_date,
                    technical_report_deadline=p.technical_report_deadline,
                    financial_report_deadline=p.financial_report_deadline,
                    review_meeting_date=p.review_meeting_date,
                    days_until_deadline=days_until,
                    created_at=p.created_at,
                    updated_at=p.updated_at,
                )
            )

    # Get all reminders
    period_ids = [p.id for p in periods]
    reminders: list[CalendarReminderItem] = []
    overdue: list[CalendarReminderItem] = []

    if period_ids:
        rem_stmt = (
            select(ReportReminder)
            .where(ReportReminder.reporting_period_id.in_(period_ids))
            .order_by(ReportReminder.scheduled_date)
        )
        rem_result = await db.execute(rem_stmt)
        all_reminders = list(rem_result.scalars().all())

        # Build project acronym lookup
        proj_ids = list({p.project_id for p in periods})
        proj_stmt = select(Project.id, Project.acronym).where(
            Project.id.in_(proj_ids)
        )
        proj_map = {
            row[0]: row[1] for row in (await db.execute(proj_stmt)).all()
        }

        period_map = {p.id: p for p in periods}

        for rem in all_reminders:
            period = period_map.get(rem.reporting_period_id)
            if period is None:
                continue

            item = CalendarReminderItem(
                reporting_period_id=rem.reporting_period_id,
                project_id=period.project_id,
                project_acronym=proj_map.get(period.project_id, ""),
                period_number=period.period_number,
                reminder_type=rem.reminder_type,
                scheduled_date=rem.scheduled_date,
                sent=rem.sent_at is not None,
                description=rem.recipient_description or "",
            )

            if rem.scheduled_date < today and rem.sent_at is None:
                overdue.append(item)
            elif rem.scheduled_date >= today:
                reminders.append(item)

    return ReportingCalendarResponse(
        upcoming_deadlines=upcoming,
        reminders=reminders,
        overdue_items=overdue,
    )


async def send_due_reminders(db: AsyncSession) -> list[ReportReminder]:
    """Mark due reminders as sent. Returns the reminders that were updated.

    In a real system this would also dispatch emails/notifications.
    """
    today = date.today()
    stmt = select(ReportReminder).where(
        ReportReminder.scheduled_date <= today,
        ReportReminder.sent_at.is_(None),
    )
    result = await db.execute(stmt)
    due = list(result.scalars().all())

    now = datetime.now(timezone.utc)
    for rem in due:
        rem.sent_at = now

    await db.flush()
    return due


# ──────────────────────────────────────────────────────
#  Risk Register
# ──────────────────────────────────────────────────────


async def create_risk(
    db: AsyncSession, project_id: uuid.UUID, data: RiskCreate
) -> Risk:
    """Create a risk entry in the project risk register."""
    await _get_project(db, project_id)
    risk = Risk(project_id=project_id, **data.model_dump())
    db.add(risk)
    await db.flush()
    await db.refresh(risk)
    return risk


async def list_risks(
    db: AsyncSession,
    project_id: uuid.UUID,
    *,
    status: RiskStatus | None = None,
) -> list[Risk]:
    """List risks for a project."""
    stmt = select(Risk).where(
        Risk.project_id == project_id,
        Risk.deleted_at.is_(None),
    )
    if status is not None:
        stmt = stmt.where(Risk.status == status)
    stmt = stmt.order_by(Risk.created_at)
    return list((await db.execute(stmt)).scalars().all())


async def get_risk(db: AsyncSession, risk_id: uuid.UUID) -> Risk | None:
    """Get a single risk."""
    stmt = select(Risk).where(
        Risk.id == risk_id, Risk.deleted_at.is_(None)
    )
    return (await db.execute(stmt)).scalar_one_or_none()


async def update_risk(
    db: AsyncSession, risk_id: uuid.UUID, data: RiskUpdate
) -> Risk | None:
    """Update a risk entry."""
    risk = await get_risk(db, risk_id)
    if risk is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(risk, field, value)
    await db.flush()
    await db.refresh(risk)
    return risk


async def delete_risk(db: AsyncSession, risk_id: uuid.UUID) -> bool:
    """Soft-delete a risk."""
    risk = await get_risk(db, risk_id)
    if risk is None:
        return False
    risk.deleted_at = datetime.now(timezone.utc)
    await db.flush()
    return True


# ──────────────────────────────────────────────────────
#  Technical Report Workflow
# ──────────────────────────────────────────────────────


async def create_report_shell(
    db: AsyncSession, reporting_period_id: uuid.UUID
) -> TechnicalReport:
    """Auto-create a technical report shell at T-90 days.

    Creates the report with all section placeholders and sets status to DRAFT.
    """
    period = await get_reporting_period(db, reporting_period_id)
    if period is None:
        raise HTTPException(status_code=404, detail="Reporting period not found")

    # Check for existing report
    existing_stmt = select(TechnicalReport).where(
        TechnicalReport.reporting_period_id == reporting_period_id,
        TechnicalReport.deleted_at.is_(None),
    )
    existing = (await db.execute(existing_stmt)).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail="Technical report already exists for this period",
        )

    project = await _get_project(db, period.project_id)

    report = TechnicalReport(
        project_id=period.project_id,
        reporting_period_id=reporting_period_id,
        report_type=period.period_type,
        status=ReportStatus.DRAFT,
    )
    db.add(report)
    await db.flush()
    await db.refresh(report)

    # Create Part A section
    part_a = ReportSection(
        technical_report_id=report.id,
        section_type=ReportSectionType.PART_A_SUMMARY,
        status=ReportSectionStatus.DRAFT,
        assigned_to="PI",
    )
    db.add(part_a)

    # Create Part B1 sections per WP
    wp_stmt = select(WorkPackage).where(
        WorkPackage.project_id == period.project_id,
        WorkPackage.deleted_at.is_(None),
    ).order_by(WorkPackage.wp_number)
    wps = list((await db.execute(wp_stmt)).scalars().all())

    for wp in wps:
        b1_section = ReportSection(
            technical_report_id=report.id,
            section_type=ReportSectionType.PART_B1_WP_NARRATIVE,
            work_package_id=wp.id,
            status=ReportSectionStatus.DRAFT,
            assigned_to="WP Leader",
        )
        db.add(b1_section)

    # Create Part B2 (auto-generated from deliverables/milestones)
    part_b2 = ReportSection(
        technical_report_id=report.id,
        section_type=ReportSectionType.PART_B2_DELIVERABLES,
        status=ReportSectionStatus.DRAFT,
        assigned_to="System",
    )
    db.add(part_b2)

    # Create Part B3 (from risk register)
    part_b3 = ReportSection(
        technical_report_id=report.id,
        section_type=ReportSectionType.PART_B3_RISKS,
        status=ReportSectionStatus.DRAFT,
        assigned_to="PI",
    )
    db.add(part_b3)

    # Create Part B4 (auto-generated from financial data)
    part_b4 = ReportSection(
        technical_report_id=report.id,
        section_type=ReportSectionType.PART_B4_RESOURCES,
        status=ReportSectionStatus.DRAFT,
        assigned_to="System",
    )
    db.add(part_b4)

    await db.flush()
    await db.refresh(report)
    return report


async def get_technical_report(
    db: AsyncSession, report_id: uuid.UUID
) -> TechnicalReport | None:
    """Get a technical report with sections."""
    stmt = (
        select(TechnicalReport)
        .options(selectinload(TechnicalReport.sections))
        .where(
            TechnicalReport.id == report_id,
            TechnicalReport.deleted_at.is_(None),
        )
    )
    return (await db.execute(stmt)).scalar_one_or_none()


async def list_technical_reports(
    db: AsyncSession, project_id: uuid.UUID
) -> list[TechnicalReport]:
    """List technical reports for a project."""
    stmt = (
        select(TechnicalReport)
        .options(selectinload(TechnicalReport.sections))
        .where(
            TechnicalReport.project_id == project_id,
            TechnicalReport.deleted_at.is_(None),
        )
        .order_by(TechnicalReport.created_at)
    )
    return list((await db.execute(stmt)).scalars().all())


async def update_technical_report(
    db: AsyncSession,
    report_id: uuid.UUID,
    part_a_summary: str | None = None,
    status: ReportStatus | None = None,
    ec_feedback: str | None = None,
) -> TechnicalReport | None:
    """Update a technical report."""
    report = await get_technical_report(db, report_id)
    if report is None:
        return None
    if part_a_summary is not None:
        report.part_a_summary = part_a_summary
    if status is not None:
        report.status = status
        if status == ReportStatus.SUBMITTED:
            report.submitted_at = datetime.now(timezone.utc)
    if ec_feedback is not None:
        report.ec_feedback = ec_feedback
    await db.flush()
    await db.refresh(report)
    return report


async def advance_report_workflow(
    db: AsyncSession, report_id: uuid.UUID
) -> TechnicalReport:
    """Advance a report to the next workflow step."""
    report = await get_technical_report(db, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")

    transitions = {
        ReportStatus.DRAFT: ReportStatus.WP_INPUT,
        ReportStatus.WP_INPUT: ReportStatus.PARTNER_REVIEW,
        ReportStatus.PARTNER_REVIEW: ReportStatus.CONSOLIDATION,
        ReportStatus.CONSOLIDATION: ReportStatus.INTERNAL_REVIEW,
        ReportStatus.INTERNAL_REVIEW: ReportStatus.FINAL_REVIEW,
        ReportStatus.FINAL_REVIEW: ReportStatus.SUBMITTED,
        ReportStatus.SUBMITTED: ReportStatus.EC_APPROVED,
    }

    next_status = transitions.get(report.status)
    if next_status is None:
        raise HTTPException(
            status_code=422,
            detail=f"Cannot advance from status {report.status.value}",
        )

    report.status = next_status
    if next_status == ReportStatus.SUBMITTED:
        report.submitted_at = datetime.now(timezone.utc)

    await db.flush()
    await db.refresh(report)
    return report


async def update_report_section(
    db: AsyncSession,
    section_id: uuid.UUID,
    *,
    content: dict | None = None,
    narrative: str | None = None,
    status: ReportSectionStatus | None = None,
    assigned_to: str | None = None,
) -> ReportSection | None:
    """Update a report section."""
    stmt = select(ReportSection).where(ReportSection.id == section_id)
    section = (await db.execute(stmt)).scalar_one_or_none()
    if section is None:
        return None

    if content is not None:
        section.content = content
    if narrative is not None:
        section.narrative = narrative
    if status is not None:
        section.status = status
    if assigned_to is not None:
        section.assigned_to = assigned_to

    await db.flush()
    await db.refresh(section)
    return section


# ──────────────────────────────────────────────────────
#  Auto-Generated Section Data
# ──────────────────────────────────────────────────────


async def generate_part_b2_data(
    db: AsyncSession, project_id: uuid.UUID, period_end: date
) -> PartB2AutoData:
    """Auto-generate Part B Section 2 from deliverable/milestone tracking data."""
    project = await _get_project(db, project_id)

    # Get all deliverables via work packages
    del_stmt = (
        select(Deliverable, WorkPackage.start_month)
        .join(WorkPackage, Deliverable.work_package_id == WorkPackage.id)
        .where(
            WorkPackage.project_id == project_id,
            Deliverable.deleted_at.is_(None),
            WorkPackage.deleted_at.is_(None),
        )
        .order_by(Deliverable.deliverable_number)
    )
    del_result = await db.execute(del_stmt)

    deliverables: list[DeliverableSummaryItem] = []
    for d, wp_start_month in del_result.all():
        is_delayed = False
        if d.due_month is not None and d.submission_date is not None:
            # Check if submitted after due month
            if project.start_date:
                due_date = _add_months(project.start_date, d.due_month)
                is_delayed = d.submission_date > due_date
        elif d.due_month is not None and d.submission_date is None:
            # Not yet submitted — check if past due
            if project.start_date:
                due_date = _add_months(project.start_date, d.due_month)
                is_delayed = date.today() > due_date

        deliverables.append(
            DeliverableSummaryItem(
                deliverable_number=d.deliverable_number,
                title=d.title,
                type=d.type.value,
                dissemination_level=d.dissemination_level.value,
                due_month=d.due_month,
                submission_date=d.submission_date,
                ec_review_status=d.ec_review_status.value,
                traffic_light=d.traffic_light.value,
                is_delayed=is_delayed,
            )
        )

    # Milestones
    ms_stmt = (
        select(Milestone, WorkPackage.wp_number)
        .join(WorkPackage, Milestone.work_package_id == WorkPackage.id)
        .where(
            WorkPackage.project_id == project_id,
            WorkPackage.deleted_at.is_(None),
        )
        .order_by(Milestone.milestone_number)
    )
    ms_result = await db.execute(ms_stmt)

    milestones: list[MilestoneSummaryItem] = []
    for m, wp_num in ms_result.all():
        milestones.append(
            MilestoneSummaryItem(
                milestone_number=m.milestone_number,
                title=m.title,
                wp_number=wp_num,
                due_month=m.due_month,
                achieved=m.achieved,
                achievement_date=m.achievement_date,
            )
        )

    return PartB2AutoData(deliverables=deliverables, milestones=milestones)


async def generate_part_b3_data(
    db: AsyncSession, project_id: uuid.UUID
) -> PartB3AutoData:
    """Auto-generate Part B Section 3 from risk register."""
    risks = await list_risks(db, project_id)

    high_priority: list[RiskSummaryItem] = []
    other: list[RiskSummaryItem] = []

    for r in risks:
        if r.status == RiskStatus.CLOSED:
            continue
        item = RiskSummaryItem(
            risk_id=r.id,
            description=r.description,
            category=r.category,
            probability=r.probability,
            impact=r.impact,
            mitigation_strategy=r.mitigation_strategy,
            owner=r.owner,
            status=r.status,
            actions_taken=r.actions_taken,
        )
        if (
            r.probability == RiskLevel.HIGH
            or r.impact == RiskLevel.HIGH
        ):
            high_priority.append(item)
        else:
            other.append(item)

    return PartB3AutoData(
        high_priority_risks=high_priority,
        other_risks=other,
    )


async def generate_part_b4_data(
    db: AsyncSession,
    project_id: uuid.UUID,
    period_start: date,
    period_end: date,
) -> PartB4AutoData:
    """Auto-generate Part B Section 4 from financial/timesheet data."""
    # Get WPs
    wp_stmt = (
        select(WorkPackage)
        .where(
            WorkPackage.project_id == project_id,
            WorkPackage.deleted_at.is_(None),
        )
        .order_by(WorkPackage.wp_number)
    )
    wps = list((await db.execute(wp_stmt)).scalars().all())

    rows: list[WPResourceRow] = []
    total_planned = ZERO
    total_actual = ZERO
    total_cost = ZERO

    for wp in wps:
        # Planned PM from effort allocations
        plan_stmt = select(
            func.coalesce(func.sum(EffortAllocation.planned_pm), 0)
        ).where(
            EffortAllocation.project_id == project_id,
            EffortAllocation.work_package_id == wp.id,
            EffortAllocation.period_start < period_end,
            EffortAllocation.period_end > period_start,
        )
        planned_pm = _q((await db.execute(plan_stmt)).scalar_one())

        # Actual hours from timesheets
        hrs_stmt = select(
            func.coalesce(func.sum(TimesheetEntry.hours), 0)
        ).where(
            TimesheetEntry.project_id == project_id,
            TimesheetEntry.work_package_id == wp.id,
            TimesheetEntry.date >= period_start,
            TimesheetEntry.date <= period_end,
        )
        actual_hours = _q((await db.execute(hrs_stmt)).scalar_one())
        actual_pm = calculate_person_months(actual_hours, 1720)

        # Personnel cost estimate (hours * average rate)
        from app.models.researcher import Researcher

        rate_stmt = select(
            func.coalesce(func.avg(Researcher.hourly_rate), 0)
        ).where(Researcher.deleted_at.is_(None))
        avg_rate = _q((await db.execute(rate_stmt)).scalar_one())
        personnel_cost = _q(actual_hours * avg_rate)

        rows.append(
            WPResourceRow(
                wp_number=wp.wp_number,
                wp_title=wp.title,
                planned_pm=planned_pm,
                actual_pm=actual_pm,
                variance_pm=_q(actual_pm - planned_pm),
                personnel_cost=personnel_cost,
            )
        )
        total_planned += planned_pm
        total_actual += actual_pm
        total_cost += personnel_cost

    return PartB4AutoData(
        rows=rows,
        total_planned_pm=total_planned,
        total_actual_pm=total_actual,
        total_personnel_cost=total_cost,
    )


async def get_workflow_steps(
    db: AsyncSession, report_id: uuid.UUID
) -> list[WorkflowStepInfo]:
    """Get workflow step info with deadlines for a report."""
    report = await get_technical_report(db, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")

    period = await get_reporting_period(db, report.reporting_period_id)
    if period is None:
        raise HTTPException(status_code=404, detail="Period not found")

    deadline = period.technical_report_deadline
    today = date.today()

    # Map report status to completed step number
    status_step_map = {
        ReportStatus.DRAFT: 0,
        ReportStatus.WP_INPUT: 1,
        ReportStatus.PARTNER_REVIEW: 2,
        ReportStatus.CONSOLIDATION: 3,
        ReportStatus.INTERNAL_REVIEW: 4,
        ReportStatus.FINAL_REVIEW: 5,
        ReportStatus.SUBMITTED: 6,
        ReportStatus.EC_APPROVED: 7,
    }
    current_step = status_step_map.get(report.status, 0)

    steps: list[WorkflowStepInfo] = []
    for step_num, name, actor, days_before in WORKFLOW_STEPS:
        step_deadline = deadline - timedelta(days=days_before)

        if step_num <= current_step:
            step_status = "completed"
        elif step_num == current_step + 1:
            step_status = "active"
            if step_deadline < today:
                step_status = "overdue"
        else:
            step_status = "pending"

        steps.append(
            WorkflowStepInfo(
                step_number=step_num,
                name=name,
                actor=actor,
                deadline_days_before=days_before,
                deadline_date=step_deadline,
                status=step_status,
            )
        )

    return steps


# ──────────────────────────────────────────────────────
#  Helpers
# ──────────────────────────────────────────────────────


async def _get_project(db: AsyncSession, project_id: uuid.UUID) -> Project:
    """Get a project or raise 404."""
    stmt = select(Project).where(
        Project.id == project_id, Project.deleted_at.is_(None)
    )
    project = (await db.execute(stmt)).scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
