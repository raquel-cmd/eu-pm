"""Service layer for researcher profiles and timesheets (Section 5).

Handles researcher CRUD, effort allocation with 100% capacity validation,
timesheet entries with person-month calculation, and compliance reports.
"""

import uuid
from datetime import date, datetime, timezone
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.enums import CostModel
from app.models.project import Project
from app.models.researcher import EffortAllocation, Researcher, TimesheetEntry
from app.models.work_package import WorkPackage
from app.schemas.researcher import (
    ComplianceIssue,
    ComplianceReportResponse,
    EffortAllocationCreate,
    ProjectAllocationDetail,
    ProjectEffortSummaryResponse,
    ResearcherAllocationResponse,
    ResearcherCreate,
    ResearcherUpdate,
    TimesheetEntryCreate,
    TimesheetEntryUpdate,
    TimesheetSubmit,
    WPEffortRow,
)


# --- Person-Month Calculation ---


def calculate_person_months(hours: Decimal, productive_hours: int) -> Decimal:
    """Calculate person-months from hours worked.

    PM = hours / productive_hours (EC standard: 1720 annual hours).
    """
    if productive_hours <= 0:
        return Decimal("0.00")
    return (hours / Decimal(productive_hours)).quantize(Decimal("0.01"))


# --- Researcher CRUD ---


async def create_researcher(
    db: AsyncSession, data: ResearcherCreate
) -> Researcher:
    """Create a researcher profile, computing hourly_rate from annual cost."""
    hourly_rate = None
    if data.annual_gross_cost is not None:
        hourly_rate = (data.annual_gross_cost / Decimal(data.productive_hours)).quantize(
            Decimal("0.01")
        )

    researcher = Researcher(
        name=data.name,
        email=data.email,
        position=data.position,
        contract_type=data.contract_type,
        fte=data.fte,
        annual_gross_cost=data.annual_gross_cost,
        productive_hours=data.productive_hours,
        hourly_rate=hourly_rate,
        start_date=data.start_date,
        end_date=data.end_date,
    )
    db.add(researcher)
    await db.flush()
    return researcher


async def get_researcher(
    db: AsyncSession, researcher_id: uuid.UUID
) -> Researcher:
    """Get a researcher by ID. Raises 404 if not found or soft-deleted."""
    stmt = select(Researcher).where(
        Researcher.id == researcher_id, Researcher.deleted_at.is_(None)
    )
    result = await db.execute(stmt)
    researcher = result.scalar_one_or_none()
    if researcher is None:
        raise HTTPException(status_code=404, detail="Researcher not found")
    return researcher


async def list_researchers(
    db: AsyncSession, skip: int = 0, limit: int = 50, project_id: uuid.UUID | None = None
) -> tuple[list[Researcher], int]:
    """List researchers with optional project filter."""
    base = select(Researcher).where(Researcher.deleted_at.is_(None))

    if project_id is not None:
        # Filter to researchers with allocations on this project
        subq = select(EffortAllocation.researcher_id).where(
            EffortAllocation.project_id == project_id
        ).distinct()
        base = base.where(Researcher.id.in_(subq))

    count_stmt = select(func.count()).select_from(base.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    stmt = base.order_by(Researcher.name).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all()), total


async def update_researcher(
    db: AsyncSession, researcher_id: uuid.UUID, data: ResearcherUpdate
) -> Researcher:
    """Update a researcher profile. Recomputes hourly_rate if cost/hours change."""
    researcher = await get_researcher(db, researcher_id)
    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(researcher, field, value)

    # Recompute hourly rate
    if researcher.annual_gross_cost is not None and researcher.productive_hours > 0:
        researcher.hourly_rate = (
            researcher.annual_gross_cost / Decimal(researcher.productive_hours)
        ).quantize(Decimal("0.01"))
    else:
        researcher.hourly_rate = None

    await db.flush()
    return researcher


async def delete_researcher(
    db: AsyncSession, researcher_id: uuid.UUID
) -> None:
    """Soft-delete a researcher."""
    researcher = await get_researcher(db, researcher_id)
    researcher.deleted_at = datetime.now(timezone.utc)
    await db.flush()


# --- Effort Allocation CRUD ---


async def validate_researcher_capacity(
    db: AsyncSession,
    researcher_id: uuid.UUID,
    period_start: date,
    period_end: date,
    exclude_allocation_id: uuid.UUID | None = None,
) -> Decimal:
    """Validate that adding an allocation won't exceed 100% FTE.

    Returns remaining capacity as a percentage.
    Raises 422 if the researcher would exceed their FTE.
    """
    researcher = await get_researcher(db, researcher_id)

    # Sum existing FTE percentages for overlapping periods
    stmt = select(func.coalesce(func.sum(EffortAllocation.planned_fte_percentage), 0)).where(
        EffortAllocation.researcher_id == researcher_id,
        EffortAllocation.period_start < period_end,
        EffortAllocation.period_end > period_start,
    )
    if exclude_allocation_id is not None:
        stmt = stmt.where(EffortAllocation.id != exclude_allocation_id)

    result = await db.execute(stmt)
    current_total = Decimal(str(result.scalar_one()))

    max_capacity = researcher.fte * Decimal("100")
    remaining = max_capacity - current_total
    return remaining


async def create_effort_allocation(
    db: AsyncSession, project_id: uuid.UUID, data: EffortAllocationCreate
) -> EffortAllocation:
    """Create an effort allocation with capacity validation."""
    # Validate project exists
    proj_stmt = select(Project.id).where(
        Project.id == project_id, Project.deleted_at.is_(None)
    )
    proj = (await db.execute(proj_stmt)).scalar_one_or_none()
    if proj is None:
        raise HTTPException(status_code=404, detail="Project not found")

    # Validate capacity if FTE percentage is provided
    if data.planned_fte_percentage is not None:
        remaining = await validate_researcher_capacity(
            db, data.researcher_id, data.period_start, data.period_end
        )
        if data.planned_fte_percentage > remaining:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"Researcher would exceed 100% FTE. "
                    f"Remaining capacity: {remaining}%, requested: {data.planned_fte_percentage}%"
                ),
            )

    allocation = EffortAllocation(
        researcher_id=data.researcher_id,
        project_id=project_id,
        work_package_id=data.work_package_id,
        period_start=data.period_start,
        period_end=data.period_end,
        planned_pm=data.planned_pm,
        planned_fte_percentage=data.planned_fte_percentage,
        notes=data.notes,
    )
    db.add(allocation)
    await db.flush()
    return allocation


async def list_effort_allocations(
    db: AsyncSession,
    project_id: uuid.UUID,
    researcher_id: uuid.UUID | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[EffortAllocation], int]:
    """List effort allocations for a project, optionally filtered by researcher."""
    base = select(EffortAllocation).where(EffortAllocation.project_id == project_id)
    if researcher_id is not None:
        base = base.where(EffortAllocation.researcher_id == researcher_id)

    count_stmt = select(func.count()).select_from(base.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    stmt = base.order_by(EffortAllocation.period_start).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all()), total


async def delete_effort_allocation(
    db: AsyncSession, allocation_id: uuid.UUID
) -> None:
    """Delete an effort allocation."""
    stmt = select(EffortAllocation).where(EffortAllocation.id == allocation_id)
    result = await db.execute(stmt)
    allocation = result.scalar_one_or_none()
    if allocation is None:
        raise HTTPException(status_code=404, detail="Effort allocation not found")
    await db.delete(allocation)
    await db.flush()


# --- Timesheet Entry CRUD ---


async def create_timesheet_entry(
    db: AsyncSession, project_id: uuid.UUID, data: TimesheetEntryCreate
) -> TimesheetEntry:
    """Create a timesheet entry with validation."""
    # Validate project exists
    proj_stmt = select(Project).where(
        Project.id == project_id, Project.deleted_at.is_(None)
    )
    proj_result = await db.execute(proj_stmt)
    project = proj_result.scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    # For UNIT_COSTS, WP is required
    if project.cost_model == CostModel.UNIT_COSTS and data.work_package_id is None:
        raise HTTPException(
            status_code=422,
            detail="work_package_id is required for unit costs projects",
        )

    entry = TimesheetEntry(
        researcher_id=data.researcher_id,
        project_id=project_id,
        work_package_id=data.work_package_id,
        date=data.date,
        hours=data.hours,
        description=data.description,
    )
    db.add(entry)
    await db.flush()
    return entry


async def list_timesheet_entries(
    db: AsyncSession,
    project_id: uuid.UUID,
    researcher_id: uuid.UUID | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[TimesheetEntry], int]:
    """List timesheet entries with filters."""
    base = select(TimesheetEntry).where(TimesheetEntry.project_id == project_id)
    if researcher_id is not None:
        base = base.where(TimesheetEntry.researcher_id == researcher_id)
    if date_from is not None:
        base = base.where(TimesheetEntry.date >= date_from)
    if date_to is not None:
        base = base.where(TimesheetEntry.date <= date_to)

    count_stmt = select(func.count()).select_from(base.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    stmt = base.order_by(TimesheetEntry.date.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all()), total


async def update_timesheet_entry(
    db: AsyncSession, entry_id: uuid.UUID, data: TimesheetEntryUpdate
) -> TimesheetEntry:
    """Update a timesheet entry. Only allowed if not yet submitted."""
    stmt = select(TimesheetEntry).where(TimesheetEntry.id == entry_id)
    result = await db.execute(stmt)
    entry = result.scalar_one_or_none()
    if entry is None:
        raise HTTPException(status_code=404, detail="Timesheet entry not found")
    if entry.submitted_at is not None:
        raise HTTPException(
            status_code=409, detail="Cannot edit a submitted timesheet entry"
        )

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(entry, field, value)
    await db.flush()
    return entry


async def delete_timesheet_entry(
    db: AsyncSession, entry_id: uuid.UUID
) -> None:
    """Delete a timesheet entry. Only allowed if not yet submitted."""
    stmt = select(TimesheetEntry).where(TimesheetEntry.id == entry_id)
    result = await db.execute(stmt)
    entry = result.scalar_one_or_none()
    if entry is None:
        raise HTTPException(status_code=404, detail="Timesheet entry not found")
    if entry.submitted_at is not None:
        raise HTTPException(
            status_code=409, detail="Cannot delete a submitted timesheet entry"
        )
    await db.delete(entry)
    await db.flush()


async def submit_timesheets(
    db: AsyncSession, data: TimesheetSubmit
) -> list[TimesheetEntry]:
    """Batch submit timesheet entries (set submitted_at)."""
    now = datetime.now(timezone.utc)
    stmt = select(TimesheetEntry).where(TimesheetEntry.id.in_(data.entry_ids))
    result = await db.execute(stmt)
    entries = list(result.scalars().all())

    if len(entries) != len(data.entry_ids):
        raise HTTPException(status_code=404, detail="Some timesheet entries not found")

    for entry in entries:
        if entry.submitted_at is not None:
            raise HTTPException(
                status_code=409,
                detail=f"Entry {entry.id} is already submitted",
            )
        entry.submitted_at = now

    await db.flush()
    return entries


async def approve_timesheets(
    db: AsyncSession, data: TimesheetSubmit
) -> list[TimesheetEntry]:
    """Batch approve timesheet entries (set approved_at)."""
    now = datetime.now(timezone.utc)
    stmt = select(TimesheetEntry).where(TimesheetEntry.id.in_(data.entry_ids))
    result = await db.execute(stmt)
    entries = list(result.scalars().all())

    if len(entries) != len(data.entry_ids):
        raise HTTPException(status_code=404, detail="Some timesheet entries not found")

    for entry in entries:
        if entry.submitted_at is None:
            raise HTTPException(
                status_code=409,
                detail=f"Entry {entry.id} must be submitted before approval",
            )
        entry.approved_at = now

    await db.flush()
    return entries


# --- Cross-Project Views ---


async def get_researcher_allocation(
    db: AsyncSession, researcher_id: uuid.UUID
) -> ResearcherAllocationResponse:
    """Get cross-project allocation overview for a researcher."""
    researcher = await get_researcher(db, researcher_id)

    # Get all active projects for this researcher via allocations
    alloc_stmt = (
        select(
            EffortAllocation.project_id,
            func.sum(EffortAllocation.planned_pm).label("committed_pm"),
        )
        .where(EffortAllocation.researcher_id == researcher_id)
        .group_by(EffortAllocation.project_id)
    )
    alloc_result = await db.execute(alloc_stmt)
    project_allocations = alloc_result.all()

    allocations = []
    for row in project_allocations:
        proj_id = row.project_id
        committed = Decimal(str(row.committed_pm))

        # Get project acronym
        proj_stmt = select(Project.acronym).where(Project.id == proj_id)
        acronym = (await db.execute(proj_stmt)).scalar_one_or_none() or "N/A"

        # Calculate actual PMs from timesheets
        hours_stmt = select(func.coalesce(func.sum(TimesheetEntry.hours), 0)).where(
            TimesheetEntry.researcher_id == researcher_id,
            TimesheetEntry.project_id == proj_id,
        )
        total_hours = Decimal(str((await db.execute(hours_stmt)).scalar_one()))
        actual_pm = calculate_person_months(total_hours, researcher.productive_hours)

        allocations.append(
            ProjectAllocationDetail(
                project_id=proj_id,
                acronym=acronym,
                committed_pm=committed,
                actual_pm=actual_pm,
                available_capacity=committed - actual_pm,
            )
        )

    return ResearcherAllocationResponse(
        researcher_id=researcher.id,
        researcher_name=researcher.name,
        fte=researcher.fte,
        allocations=allocations,
    )


async def get_project_effort_summary(
    db: AsyncSession, project_id: uuid.UUID
) -> ProjectEffortSummaryResponse:
    """Get planned vs actual PMs per WP for a project."""
    # Planned PMs per WP
    planned_stmt = (
        select(
            EffortAllocation.work_package_id,
            func.sum(EffortAllocation.planned_pm).label("planned_pm"),
        )
        .where(EffortAllocation.project_id == project_id)
        .group_by(EffortAllocation.work_package_id)
    )
    planned_result = await db.execute(planned_stmt)
    planned_by_wp = {row.work_package_id: Decimal(str(row.planned_pm)) for row in planned_result}

    # Actual hours per WP
    actual_stmt = (
        select(
            TimesheetEntry.work_package_id,
            func.sum(TimesheetEntry.hours).label("total_hours"),
        )
        .where(TimesheetEntry.project_id == project_id)
        .group_by(TimesheetEntry.work_package_id)
    )
    actual_result = await db.execute(actual_stmt)
    actual_by_wp = {row.work_package_id: Decimal(str(row.total_hours)) for row in actual_result}

    # Get WP details
    all_wp_ids = set(planned_by_wp.keys()) | set(actual_by_wp.keys())
    wp_info: dict[uuid.UUID | None, tuple[int | None, str | None]] = {None: (None, "Unassigned")}
    if all_wp_ids - {None}:
        wp_stmt = select(WorkPackage.id, WorkPackage.number, WorkPackage.title).where(
            WorkPackage.id.in_([wid for wid in all_wp_ids if wid is not None])
        )
        wp_result = await db.execute(wp_stmt)
        for row in wp_result:
            wp_info[row.id] = (row.number, row.title)

    # Use a default productive_hours of 1720 for PM calculation
    productive_hours = 1720

    rows = []
    total_planned = Decimal("0")
    total_actual = Decimal("0")
    for wp_id in sorted(all_wp_ids, key=lambda x: (x is None, str(x))):
        planned = planned_by_wp.get(wp_id, Decimal("0"))
        hours = actual_by_wp.get(wp_id, Decimal("0"))
        actual = calculate_person_months(hours, productive_hours)
        info = wp_info.get(wp_id, (None, None))
        rows.append(
            WPEffortRow(
                wp_number=info[0],
                wp_title=info[1],
                planned_pm=planned,
                actual_pm=actual,
                variance=planned - actual,
            )
        )
        total_planned += planned
        total_actual += actual

    return ProjectEffortSummaryResponse(
        project_id=project_id,
        rows=rows,
        total_planned_pm=total_planned,
        total_actual_pm=total_actual,
    )


# --- Compliance Report ---


async def get_compliance_report(
    db: AsyncSession,
    project_id: uuid.UUID,
    period_start: date,
    period_end: date,
) -> ComplianceReportResponse:
    """Generate compliance report for a project period.

    Checks for:
    - Missing timesheets: researchers with allocations but no entries
    - Late submissions: entries submitted > 15 days after period end
    - Over-capacity: researchers exceeding 100% FTE across projects
    """
    issues: list[ComplianceIssue] = []
    period_str = f"{period_start} to {period_end}"

    # 1. Missing timesheets
    alloc_stmt = (
        select(EffortAllocation.researcher_id)
        .where(
            EffortAllocation.project_id == project_id,
            EffortAllocation.period_start < period_end,
            EffortAllocation.period_end > period_start,
        )
        .distinct()
    )
    alloc_result = await db.execute(alloc_stmt)
    allocated_researcher_ids = [row[0] for row in alloc_result]

    for r_id in allocated_researcher_ids:
        entry_stmt = select(func.count()).where(
            TimesheetEntry.researcher_id == r_id,
            TimesheetEntry.project_id == project_id,
            TimesheetEntry.date >= period_start,
            TimesheetEntry.date <= period_end,
        )
        count = (await db.execute(entry_stmt)).scalar_one()
        if count == 0:
            r = await get_researcher(db, r_id)
            issues.append(
                ComplianceIssue(
                    researcher_name=r.name,
                    issue_type="missing_timesheet",
                    details="No timesheet entries found for allocation period",
                    period=period_str,
                )
            )

    # 2. Late submissions (submitted > 15 days after period end)
    from datetime import timedelta

    grace_deadline = datetime(
        period_end.year, period_end.month, period_end.day,
        tzinfo=timezone.utc,
    ) + timedelta(days=15)

    late_stmt = (
        select(TimesheetEntry)
        .where(
            TimesheetEntry.project_id == project_id,
            TimesheetEntry.date >= period_start,
            TimesheetEntry.date <= period_end,
            TimesheetEntry.submitted_at.is_not(None),
            TimesheetEntry.submitted_at > grace_deadline,
        )
    )
    late_result = await db.execute(late_stmt)
    for entry in late_result.scalars():
        r = await get_researcher(db, entry.researcher_id)
        issues.append(
            ComplianceIssue(
                researcher_name=r.name,
                issue_type="late_submission",
                details=f"Timesheet for {entry.date} submitted on {entry.submitted_at.date()}",
                period=period_str,
            )
        )

    # 3. Over-capacity check
    for r_id in allocated_researcher_ids:
        r = await get_researcher(db, r_id)
        cap_stmt = select(
            func.coalesce(func.sum(EffortAllocation.planned_fte_percentage), 0)
        ).where(
            EffortAllocation.researcher_id == r_id,
            EffortAllocation.period_start < period_end,
            EffortAllocation.period_end > period_start,
        )
        total_pct = Decimal(str((await db.execute(cap_stmt)).scalar_one()))
        max_cap = r.fte * Decimal("100")
        if total_pct > max_cap:
            issues.append(
                ComplianceIssue(
                    researcher_name=r.name,
                    issue_type="over_capacity",
                    details=f"Allocated {total_pct}% FTE, max is {max_cap}%",
                    period=period_str,
                )
            )

    return ComplianceReportResponse(issues=issues, total_issues=len(issues))
