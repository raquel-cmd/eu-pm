"""Dashboard aggregation service (Section 10).

Provides data for PI, Researcher, and Project dashboards by
aggregating existing model data (projects, work packages, deliverables,
expenses, missions, procurements, risks, amendments, effort allocations,
timesheet entries, and reporting periods).
"""

import uuid
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

from fastapi import HTTPException
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.additional_features import Amendment
from app.models.enums import (
    AmendmentStatus,
    ECBudgetCategory,
    RiskStatus,
    TrafficLight,
    WPStatus,
)
from app.models.financial import Expense, Mission, Procurement
from app.models.partner import Partner, ProjectPartner
from app.models.project import Project
from app.models.reporting import ReportingPeriod, Risk
from app.models.researcher import EffortAllocation, Researcher, TimesheetEntry
from app.models.work_package import Deliverable, WorkPackage
from app.schemas.dashboards import (
    BudgetCategoryItem,
    CrossProjectDeadline,
    DeliverableTimelineItem,
    PartnerStatusItem,
    PIDashboardResponse,
    PIProjectSummary,
    ProjectDashboardResponse,
    ProjectRiskSummary,
    ResearcherAllocationSummary,
    ResearcherDashboardResponse,
    ResearcherDeadline,
    TimesheetStatusItem,
    WPProgressItem,
)

ZERO = Decimal("0.00")

# EC budget category display labels
EC_CATEGORY_LABELS: dict[str, str] = {
    "A_PERSONNEL": "A – Personnel",
    "B_SUBCONTRACTING": "B – Subcontracting",
    "C1_TRAVEL": "C.1 – Travel",
    "C2_EQUIPMENT": "C.2 – Equipment",
    "C3_OTHER_GOODS": "C.3 – Other Goods",
    "D_OTHER_COSTS": "D – Other Costs",
    "E_INDIRECT": "E – Indirect",
}


def _q(value: Decimal | int | float | None) -> Decimal:
    """Quantize a decimal to 2 places, treating None as zero."""
    if value is None:
        return ZERO
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# ── PI Dashboard ─────────────────────────────────────────


async def get_pi_dashboard(db: AsyncSession) -> PIDashboardResponse:
    """Build the PI portfolio overview dashboard.

    Aggregates project-level metrics: traffic light, budget health,
    team size, open risks, active amendments, and cross-project deadlines.
    """
    # Fetch all active projects
    stmt = (
        select(Project)
        .where(Project.deleted_at.is_(None))
        .order_by(Project.acronym)
    )
    result = await db.execute(stmt)
    projects = result.scalars().all()

    summaries: list[PIProjectSummary] = []
    deadlines: list[CrossProjectDeadline] = []
    total_budget = ZERO
    total_spent = ZERO
    today = date.today()

    for proj in projects:
        # ── Traffic light: worst deliverable status ──
        tl_stmt = (
            select(Deliverable.traffic_light)
            .join(WorkPackage, Deliverable.work_package_id == WorkPackage.id)
            .where(
                WorkPackage.project_id == proj.id,
                WorkPackage.deleted_at.is_(None),
                Deliverable.deleted_at.is_(None),
            )
        )
        tl_result = await db.execute(tl_stmt)
        tl_values = [row[0] for row in tl_result.all()]
        if any(t == TrafficLight.RED for t in tl_values):
            traffic = "RED"
        elif any(t == TrafficLight.AMBER for t in tl_values):
            traffic = "AMBER"
        else:
            traffic = "GREEN"

        # ── Next deadline (from reporting periods) ──
        deadline_stmt = (
            select(ReportingPeriod)
            .where(
                ReportingPeriod.project_id == proj.id,
                ReportingPeriod.deleted_at.is_(None),
                ReportingPeriod.technical_report_deadline >= today,
            )
            .order_by(ReportingPeriod.technical_report_deadline)
            .limit(1)
        )
        deadline_result = await db.execute(deadline_stmt)
        next_rp = deadline_result.scalar_one_or_none()
        next_deadline = next_rp.technical_report_deadline if next_rp else None
        next_deadline_type = "Technical Report" if next_rp else None

        # ── Budget health ──
        budget_total = _q(proj.total_budget)
        spent = await _get_project_spending(db, proj.id)
        burn_rate = (
            _q((spent / budget_total) * 100)
            if budget_total > ZERO
            else ZERO
        )

        # ── Team size (distinct researchers allocated) ──
        team_stmt = select(
            func.count(func.distinct(EffortAllocation.researcher_id))
        ).where(EffortAllocation.project_id == proj.id)
        team_result = await db.execute(team_stmt)
        team_size = team_result.scalar_one() or 0

        # ── Open risks ──
        risk_stmt = select(func.count(Risk.id)).where(
            Risk.project_id == proj.id,
            Risk.deleted_at.is_(None),
            Risk.status == RiskStatus.OPEN,
        )
        risk_result = await db.execute(risk_stmt)
        open_risks = risk_result.scalar_one() or 0

        # ── Active amendments ──
        amend_stmt = select(func.count(Amendment.id)).where(
            Amendment.project_id == proj.id,
            Amendment.deleted_at.is_(None),
            Amendment.status.in_([
                AmendmentStatus.DRAFT,
                AmendmentStatus.SUBMITTED,
                AmendmentStatus.UNDER_REVIEW,
            ]),
        )
        amend_result = await db.execute(amend_stmt)
        active_amendments = amend_result.scalar_one() or 0

        total_budget += budget_total
        total_spent += spent

        summaries.append(
            PIProjectSummary(
                project_id=proj.id,
                acronym=proj.acronym,
                programme=proj.programme,
                status=proj.status,
                traffic_light=traffic,
                next_deadline=next_deadline,
                next_deadline_type=next_deadline_type,
                budget_total=budget_total,
                budget_spent=spent,
                burn_rate_pct=burn_rate,
                team_size=team_size,
                open_risks=open_risks,
                active_amendments=active_amendments,
            )
        )

        # ── Cross-project deadlines ──
        if next_deadline:
            days_until = (next_deadline - today).days
            deadlines.append(
                CrossProjectDeadline(
                    project_acronym=proj.acronym,
                    project_id=proj.id,
                    deadline_type="Technical Report",
                    date=next_deadline,
                    days_until=days_until,
                )
            )
        # Also include financial report deadlines
        fin_stmt = (
            select(ReportingPeriod)
            .where(
                ReportingPeriod.project_id == proj.id,
                ReportingPeriod.deleted_at.is_(None),
                ReportingPeriod.financial_report_deadline.isnot(None),
                ReportingPeriod.financial_report_deadline >= today,
            )
            .order_by(ReportingPeriod.financial_report_deadline)
            .limit(1)
        )
        fin_result = await db.execute(fin_stmt)
        fin_rp = fin_result.scalar_one_or_none()
        if fin_rp and fin_rp.financial_report_deadline:
            days_until_fin = (fin_rp.financial_report_deadline - today).days
            deadlines.append(
                CrossProjectDeadline(
                    project_acronym=proj.acronym,
                    project_id=proj.id,
                    deadline_type="Financial Report",
                    date=fin_rp.financial_report_deadline,
                    days_until=days_until_fin,
                )
            )

    # Sort deadlines by date
    deadlines.sort(key=lambda d: d.date)

    overall_burn = (
        _q((total_spent / total_budget) * 100)
        if total_budget > ZERO
        else ZERO
    )

    return PIDashboardResponse(
        projects=summaries,
        cross_project_deadlines=deadlines,
        total_budget=total_budget,
        total_spent=total_spent,
        overall_burn_rate=overall_burn,
        active_project_count=len(
            [s for s in summaries if s.status.value == "ACTIVE"]
        ),
    )


# ── Researcher Dashboard ─────────────────────────────────


async def get_researcher_dashboard(
    db: AsyncSession, researcher_id: uuid.UUID
) -> ResearcherDashboardResponse:
    """Build the researcher personal dashboard.

    Shows effort allocations, timesheet status, and upcoming deadlines
    for all projects the researcher is allocated to.
    """
    # Verify researcher exists
    r_stmt = select(Researcher).where(
        Researcher.id == researcher_id,
        Researcher.deleted_at.is_(None),
    )
    r_result = await db.execute(r_stmt)
    researcher = r_result.scalar_one_or_none()
    if researcher is None:
        raise HTTPException(status_code=404, detail="Researcher not found")

    # ── Effort allocations ──
    alloc_stmt = (
        select(EffortAllocation)
        .options(selectinload(EffortAllocation.project))
        .options(selectinload(EffortAllocation.work_package))
        .where(EffortAllocation.researcher_id == researcher_id)
        .order_by(EffortAllocation.period_start)
    )
    alloc_result = await db.execute(alloc_stmt)
    allocations_raw = alloc_result.scalars().all()

    allocations: list[ResearcherAllocationSummary] = []
    project_ids: set[uuid.UUID] = set()
    total_planned = ZERO
    total_actual = ZERO

    for alloc in allocations_raw:
        project_ids.add(alloc.project_id)

        # Sum actual PM from timesheet hours for this allocation
        ts_stmt = select(
            func.coalesce(func.sum(TimesheetEntry.hours), 0)
        ).where(
            TimesheetEntry.researcher_id == researcher_id,
            TimesheetEntry.project_id == alloc.project_id,
            TimesheetEntry.date >= alloc.period_start,
            TimesheetEntry.date <= alloc.period_end,
        )
        if alloc.work_package_id:
            ts_stmt = ts_stmt.where(
                TimesheetEntry.work_package_id == alloc.work_package_id
            )
        ts_result = await db.execute(ts_stmt)
        hours = _q(ts_result.scalar_one())
        # Convert hours to PM (assuming 143.33 hours/PM = 1720/12)
        actual_pm = _q(hours / Decimal("143.33")) if hours > ZERO else ZERO

        planned = _q(alloc.planned_pm)
        total_planned += planned
        total_actual += actual_pm

        allocations.append(
            ResearcherAllocationSummary(
                project_id=alloc.project_id,
                project_acronym=(
                    alloc.project.acronym if alloc.project else "Unknown"
                ),
                wp_title=(
                    alloc.work_package.title if alloc.work_package else None
                ),
                planned_pm=planned,
                actual_pm=actual_pm,
                period_start=alloc.period_start,
                period_end=alloc.period_end,
            )
        )

    # ── Timesheet status (month-by-project) ──
    timesheet_status: list[TimesheetStatusItem] = []
    today = date.today()

    for pid in project_ids:
        # Get project acronym
        p_stmt = select(Project.acronym).where(Project.id == pid)
        p_result = await db.execute(p_stmt)
        acronym = p_result.scalar_one_or_none() or "Unknown"

        # Check last 3 months
        for months_ago in range(3):
            if months_ago == 0:
                month_start = today.replace(day=1)
            else:
                # Go back months_ago months
                m = today.month - months_ago
                y = today.year
                while m <= 0:
                    m += 12
                    y -= 1
                month_start = date(y, m, 1)

            # Calculate month end
            if month_start.month == 12:
                month_end = date(month_start.year + 1, 1, 1) - timedelta(days=1)
            else:
                month_end = (
                    date(month_start.year, month_start.month + 1, 1)
                    - timedelta(days=1)
                )

            # Sum hours logged this month
            ts_stmt = select(
                func.coalesce(func.sum(TimesheetEntry.hours), 0)
            ).where(
                TimesheetEntry.researcher_id == researcher_id,
                TimesheetEntry.project_id == pid,
                TimesheetEntry.date >= month_start,
                TimesheetEntry.date <= month_end,
            )
            ts_result = await db.execute(ts_stmt)
            logged = _q(ts_result.scalar_one())

            # Expected hours from effort allocation (rough estimate)
            expected = _q(Decimal("143.33"))  # 1 PM default

            if logged >= expected:
                status = "complete"
            elif logged > ZERO:
                status = "incomplete"
            else:
                status = "not_started"

            timesheet_status.append(
                TimesheetStatusItem(
                    project_acronym=acronym,
                    project_id=pid,
                    month=month_start.strftime("%Y-%m"),
                    hours_logged=logged,
                    hours_expected=expected,
                    status=status,
                )
            )

    # ── Upcoming deadlines ──
    upcoming_deadlines: list[ResearcherDeadline] = []

    for pid in project_ids:
        p_stmt = select(Project.acronym).where(Project.id == pid)
        p_result = await db.execute(p_stmt)
        acronym = p_result.scalar_one_or_none() or "Unknown"

        # Deliverable deadlines (from WPs the researcher is allocated to)
        wp_ids_stmt = (
            select(func.distinct(EffortAllocation.work_package_id))
            .where(
                EffortAllocation.researcher_id == researcher_id,
                EffortAllocation.project_id == pid,
                EffortAllocation.work_package_id.isnot(None),
            )
        )
        wp_ids_result = await db.execute(wp_ids_stmt)
        wp_ids = [row[0] for row in wp_ids_result.all()]

        if wp_ids:
            del_stmt = (
                select(Deliverable)
                .where(
                    Deliverable.work_package_id.in_(wp_ids),
                    Deliverable.deleted_at.is_(None),
                    Deliverable.submission_date.is_(None),
                    Deliverable.due_month.isnot(None),
                )
            )
            del_result = await db.execute(del_stmt)
            deliverables = del_result.scalars().all()

            # Get project start date to calculate due date
            proj_stmt = select(Project.start_date).where(Project.id == pid)
            proj_result = await db.execute(proj_stmt)
            start_date = proj_result.scalar_one_or_none()

            for d in deliverables:
                if start_date and d.due_month:
                    # Calculate approximate due date from project start + months
                    due_y = start_date.year + (
                        (start_date.month + d.due_month - 1) // 12
                    )
                    due_m = ((start_date.month + d.due_month - 1) % 12) + 1
                    try:
                        due_date = date(due_y, due_m, 1)
                    except ValueError:
                        continue
                    if due_date >= today:
                        upcoming_deadlines.append(
                            ResearcherDeadline(
                                project_acronym=acronym,
                                project_id=pid,
                                deadline_type="Deliverable",
                                title=f"{d.deliverable_number}: {d.title}",
                                due_date=due_date,
                                days_until=(due_date - today).days,
                            )
                        )

        # Reporting deadlines
        rp_stmt = (
            select(ReportingPeriod)
            .where(
                ReportingPeriod.project_id == pid,
                ReportingPeriod.deleted_at.is_(None),
                ReportingPeriod.technical_report_deadline >= today,
            )
            .order_by(ReportingPeriod.technical_report_deadline)
            .limit(1)
        )
        rp_result = await db.execute(rp_stmt)
        rp = rp_result.scalar_one_or_none()
        if rp:
            upcoming_deadlines.append(
                ResearcherDeadline(
                    project_acronym=acronym,
                    project_id=pid,
                    deadline_type="Technical Report",
                    title=f"Period {rp.period_number} Report",
                    due_date=rp.technical_report_deadline,
                    days_until=(
                        rp.technical_report_deadline - today
                    ).days,
                )
            )

    upcoming_deadlines.sort(key=lambda d: d.due_date)

    return ResearcherDashboardResponse(
        researcher_name=researcher.name,
        researcher_id=researcher.id,
        allocations=allocations,
        timesheet_status=timesheet_status,
        upcoming_deadlines=upcoming_deadlines,
        total_planned_pm=total_planned,
        total_actual_pm=total_actual,
    )


# ── Project Dashboard ────────────────────────────────────


async def get_project_dashboard(
    db: AsyncSession, project_id: uuid.UUID
) -> ProjectDashboardResponse:
    """Build the detailed project dashboard.

    Includes WP progress, deliverable timeline, budget by EC category,
    partner status, risk summary, and key performance metrics.
    """
    # Verify project exists
    p_stmt = select(Project).where(
        Project.id == project_id, Project.deleted_at.is_(None)
    )
    p_result = await db.execute(p_stmt)
    project = p_result.scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    # ── WP progress ──
    wp_stmt = (
        select(WorkPackage)
        .where(
            WorkPackage.project_id == project_id,
            WorkPackage.deleted_at.is_(None),
        )
        .order_by(WorkPackage.wp_number)
    )
    wp_result = await db.execute(wp_stmt)
    work_packages = wp_result.scalars().all()

    wp_progress: list[WPProgressItem] = []
    total_deliverables = 0
    completed_deliverables = 0

    for wp in work_packages:
        d_stmt = select(Deliverable).where(
            Deliverable.work_package_id == wp.id,
            Deliverable.deleted_at.is_(None),
        )
        d_result = await db.execute(d_stmt)
        deliverables = d_result.scalars().all()

        d_total = len(deliverables)
        d_completed = sum(
            1 for d in deliverables if d.submission_date is not None
        )
        total_deliverables += d_total
        completed_deliverables += d_completed

        progress = (
            _q(Decimal(d_completed) / Decimal(d_total) * 100)
            if d_total > 0
            else ZERO
        )

        wp_progress.append(
            WPProgressItem(
                wp_number=wp.wp_number,
                wp_title=wp.title,
                status=wp.status,
                deliverables_total=d_total,
                deliverables_completed=d_completed,
                progress_pct=progress,
            )
        )

    # ── Deliverable timeline ──
    all_del_stmt = (
        select(Deliverable)
        .join(WorkPackage, Deliverable.work_package_id == WorkPackage.id)
        .where(
            WorkPackage.project_id == project_id,
            WorkPackage.deleted_at.is_(None),
            Deliverable.deleted_at.is_(None),
        )
        .order_by(Deliverable.due_month)
    )
    all_del_result = await db.execute(all_del_stmt)
    all_deliverables = all_del_result.scalars().all()

    deliverable_timeline: list[DeliverableTimelineItem] = [
        DeliverableTimelineItem(
            deliverable_number=d.deliverable_number,
            title=d.title,
            deliverable_type=d.type,
            due_month=d.due_month,
            submission_date=d.submission_date,
            ec_review_status=d.ec_review_status,
            traffic_light=d.traffic_light,
        )
        for d in all_deliverables
    ]

    # ── Budget by EC category ──
    budget_by_category = await _get_budget_by_category(db, project_id)

    # ── Partner status ──
    partner_status = await _get_partner_status(db, project_id)

    # ── Risks ──
    risk_stmt = (
        select(Risk)
        .where(
            Risk.project_id == project_id,
            Risk.deleted_at.is_(None),
        )
        .order_by(Risk.status, Risk.category)
    )
    risk_result = await db.execute(risk_stmt)
    risks_raw = risk_result.scalars().all()

    risks: list[ProjectRiskSummary] = [
        ProjectRiskSummary(
            risk_id=r.id,
            description=r.description,
            category=r.category,
            probability=r.probability,
            impact=r.impact,
            status=r.status,
            owner=r.owner,
        )
        for r in risks_raw
    ]

    # ── Key metrics ──
    total_budget = _q(project.total_budget)
    total_spent = await _get_project_spending(db, project_id)
    burn_rate = (
        _q((total_spent / total_budget) * 100)
        if total_budget > ZERO
        else ZERO
    )

    # Burn rate status
    if burn_rate >= Decimal("95"):
        burn_status = "critical"
    elif burn_rate >= Decimal("80"):
        burn_status = "warning"
    else:
        burn_status = "healthy"

    # PM compliance: planned vs actual from effort allocations + timesheets
    pm_compliance = await _get_pm_compliance(db, project_id)

    # Deliverable completion rate
    del_completion = (
        _q(Decimal(completed_deliverables) / Decimal(total_deliverables) * 100)
        if total_deliverables > 0
        else ZERO
    )

    return ProjectDashboardResponse(
        project_id=project.id,
        acronym=project.acronym,
        wp_progress=wp_progress,
        deliverable_timeline=deliverable_timeline,
        budget_by_category=budget_by_category,
        partner_status=partner_status,
        risks=risks,
        burn_rate=burn_rate,
        burn_rate_status=burn_status,
        pm_compliance_rate=pm_compliance,
        deliverable_completion_rate=del_completion,
        total_budget=total_budget,
        total_spent=total_spent,
    )


# ── Helpers ──────────────────────────────────────────────


async def _get_project_spending(
    db: AsyncSession, project_id: uuid.UUID
) -> Decimal:
    """Total spending: expenses + missions + procurements."""
    expense_stmt = select(
        func.coalesce(func.sum(Expense.amount_gross), 0)
    ).where(
        Expense.project_id == project_id,
        Expense.deleted_at.is_(None),
    )
    mission_stmt = select(
        func.coalesce(func.sum(Mission.total_cost), 0)
    ).where(
        Mission.project_id == project_id,
        Mission.deleted_at.is_(None),
    )
    procurement_stmt = select(
        func.coalesce(
            func.sum(
                case(
                    (
                        Procurement.actual_cost.isnot(None),
                        Procurement.actual_cost,
                    ),
                    else_=func.coalesce(Procurement.estimated_cost, 0),
                )
            ),
            0,
        )
    ).where(
        Procurement.project_id == project_id,
        Procurement.deleted_at.is_(None),
    )

    e = await db.execute(expense_stmt)
    m = await db.execute(mission_stmt)
    p = await db.execute(procurement_stmt)

    return _q(e.scalar_one()) + _q(m.scalar_one()) + _q(p.scalar_one())


async def _get_budget_by_category(
    db: AsyncSession, project_id: uuid.UUID
) -> list[BudgetCategoryItem]:
    """Break down spending by EC category.

    Note: per-category budgeted amounts are not yet stored in the DB,
    so budgeted is reported as zero (matching budget_monitor behavior).
    """
    # Get spending by category from expenses
    spent_stmt = (
        select(
            Expense.ec_category,
            func.coalesce(func.sum(Expense.amount_gross), 0),
        )
        .where(
            Expense.project_id == project_id,
            Expense.deleted_at.is_(None),
        )
        .group_by(Expense.ec_category)
    )
    spent_result = await db.execute(spent_stmt)
    spent_map: dict[ECBudgetCategory | None, Decimal] = {
        row[0]: _q(row[1]) for row in spent_result.all()
    }

    items: list[BudgetCategoryItem] = []
    for cat in sorted(spent_map.keys(), key=lambda c: c.value if c else "Z"):
        if cat is None:
            continue
        s = spent_map[cat]
        items.append(
            BudgetCategoryItem(
                category=cat.value,
                category_label=EC_CATEGORY_LABELS.get(cat.value, cat.value),
                budgeted=ZERO,
                spent=s,
                remaining=ZERO,
                pct_used=ZERO,
            )
        )

    return items


async def _get_partner_status(
    db: AsyncSession, project_id: uuid.UUID
) -> list[PartnerStatusItem]:
    """Get per-partner spending vs allocated budget."""
    # Get project partners with budget info
    pp_stmt = (
        select(ProjectPartner, Partner)
        .join(Partner, ProjectPartner.partner_id == Partner.id)
        .where(
            ProjectPartner.project_id == project_id,
            Partner.deleted_at.is_(None),
        )
    )
    pp_result = await db.execute(pp_stmt)
    partner_rows = pp_result.all()

    items: list[PartnerStatusItem] = []
    for pp, partner in partner_rows:
        # Per-partner spending from expenses
        spend_stmt = select(
            func.coalesce(func.sum(Expense.amount_gross), 0)
        ).where(
            Expense.project_id == project_id,
            Expense.partner_id == partner.id,
            Expense.deleted_at.is_(None),
        )
        spend_result = await db.execute(spend_stmt)
        spent = _q(spend_result.scalar_one())
        allocated = _q(pp.partner_budget)
        pct = _q((spent / allocated) * 100) if allocated > ZERO else ZERO

        items.append(
            PartnerStatusItem(
                partner_name=partner.legal_name,
                partner_id=partner.id,
                country=partner.country,
                allocated_budget=allocated,
                spent=spent,
                pct_used=pct,
            )
        )

    return items


async def _get_pm_compliance(
    db: AsyncSession, project_id: uuid.UUID
) -> Decimal:
    """Calculate PM compliance rate: actual hours vs planned PM."""
    # Total planned PM
    planned_stmt = select(
        func.coalesce(func.sum(EffortAllocation.planned_pm), 0)
    ).where(EffortAllocation.project_id == project_id)
    planned_result = await db.execute(planned_stmt)
    total_planned = _q(planned_result.scalar_one())

    if total_planned <= ZERO:
        return ZERO

    # Total actual hours
    actual_stmt = select(
        func.coalesce(func.sum(TimesheetEntry.hours), 0)
    ).where(TimesheetEntry.project_id == project_id)
    actual_result = await db.execute(actual_stmt)
    total_hours = _q(actual_result.scalar_one())

    # Convert hours to PM
    actual_pm = _q(total_hours / Decimal("143.33"))

    return _q((actual_pm / total_planned) * 100)
