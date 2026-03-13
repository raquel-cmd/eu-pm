"""Tests for the timesheet service layer (Section 5)."""

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import (
    ContractType,
    CostModel,
    Programme,
    ProjectRole,
    ResearcherPosition,
)
from app.schemas.project import ProjectCreate
from app.schemas.researcher import (
    EffortAllocationCreate,
    ResearcherCreate,
    ResearcherUpdate,
    TimesheetEntryCreate,
    TimesheetEntryUpdate,
    TimesheetSubmit,
)
from app.services import project as project_service
from app.services import timesheet as timesheet_service


async def _create_project(
    db: AsyncSession, cost_model: CostModel = CostModel.ACTUAL_COSTS
) -> "Project":
    """Helper to create a project."""
    data = ProjectCreate(
        acronym=f"TS-{cost_model.value[:4]}",
        full_title="Timesheet Test Project",
        programme=Programme.HORIZON_EUROPE,
        cost_model=cost_model,
        role=ProjectRole.COORDINATOR,
    )
    return await project_service.create_project(db, data)


async def _create_researcher(
    db: AsyncSession,
    name: str = "Alice Test",
    annual_gross_cost: Decimal | None = Decimal("51600.00"),
    productive_hours: int = 1720,
    fte: Decimal = Decimal("1.00"),
) -> "Researcher":
    """Helper to create a researcher."""
    data = ResearcherCreate(
        name=name,
        email=f"{name.lower().replace(' ', '.')}@test.pt",
        position=ResearcherPosition.POSTDOC,
        contract_type=ContractType.DL57,
        fte=fte,
        annual_gross_cost=annual_gross_cost,
        productive_hours=productive_hours,
    )
    return await timesheet_service.create_researcher(db, data)


# --- Researcher CRUD Tests ---


@pytest.mark.asyncio
async def test_create_researcher_hourly_rate(db: AsyncSession):
    """Hourly rate is computed from annual_gross_cost / productive_hours."""
    researcher = await _create_researcher(db, annual_gross_cost=Decimal("51600.00"))
    assert researcher.hourly_rate == Decimal("30.00")
    assert researcher.productive_hours == 1720


@pytest.mark.asyncio
async def test_create_researcher_no_cost(db: AsyncSession):
    """Hourly rate is None when no annual_gross_cost is provided."""
    researcher = await _create_researcher(
        db, name="No Cost", annual_gross_cost=None
    )
    assert researcher.hourly_rate is None


@pytest.mark.asyncio
async def test_update_researcher_recalculates_rate(db: AsyncSession):
    """Updating annual_gross_cost recalculates hourly_rate."""
    researcher = await _create_researcher(db)
    updated = await timesheet_service.update_researcher(
        db,
        researcher.id,
        ResearcherUpdate(annual_gross_cost=Decimal("34400.00")),
    )
    assert updated.hourly_rate == Decimal("20.00")


@pytest.mark.asyncio
async def test_list_researchers(db: AsyncSession):
    """List researchers returns correct count."""
    await _create_researcher(db, name="R1")
    await _create_researcher(db, name="R2")
    items, total = await timesheet_service.list_researchers(db)
    assert total == 2
    assert len(items) == 2


@pytest.mark.asyncio
async def test_delete_researcher_soft(db: AsyncSession):
    """Delete sets deleted_at, get raises 404."""
    researcher = await _create_researcher(db)
    await timesheet_service.delete_researcher(db, researcher.id)
    with pytest.raises(HTTPException) as exc:
        await timesheet_service.get_researcher(db, researcher.id)
    assert exc.value.status_code == 404


# --- Effort Allocation Tests ---


@pytest.mark.asyncio
async def test_create_effort_allocation(db: AsyncSession):
    """Create allocation with valid capacity."""
    project = await _create_project(db)
    researcher = await _create_researcher(db)
    data = EffortAllocationCreate(
        researcher_id=researcher.id,
        period_start=date(2026, 1, 1),
        period_end=date(2026, 6, 30),
        planned_pm=Decimal("3.00"),
        planned_fte_percentage=Decimal("50.00"),
    )
    alloc = await timesheet_service.create_effort_allocation(db, project.id, data)
    assert alloc.planned_pm == Decimal("3.00")
    assert alloc.planned_fte_percentage == Decimal("50.00")


@pytest.mark.asyncio
async def test_capacity_validation_rejects_over_100(db: AsyncSession):
    """Allocations exceeding 100% FTE are rejected with 422."""
    project1 = await _create_project(db)
    researcher = await _create_researcher(db)

    # First allocation: 70%
    data1 = EffortAllocationCreate(
        researcher_id=researcher.id,
        period_start=date(2026, 1, 1),
        period_end=date(2026, 6, 30),
        planned_pm=Decimal("4.00"),
        planned_fte_percentage=Decimal("70.00"),
    )
    await timesheet_service.create_effort_allocation(db, project1.id, data1)

    # Second allocation overlapping: 40% -> total 110% -> rejected
    project2 = await _create_project(db)
    data2 = EffortAllocationCreate(
        researcher_id=researcher.id,
        period_start=date(2026, 3, 1),
        period_end=date(2026, 9, 30),
        planned_pm=Decimal("3.00"),
        planned_fte_percentage=Decimal("40.00"),
    )
    with pytest.raises(HTTPException) as exc:
        await timesheet_service.create_effort_allocation(db, project2.id, data2)
    assert exc.value.status_code == 422
    assert "100% FTE" in exc.value.detail


@pytest.mark.asyncio
async def test_non_overlapping_periods_ok(db: AsyncSession):
    """Non-overlapping allocations don't count toward capacity."""
    project1 = await _create_project(db)
    project2 = await _create_project(db)
    researcher = await _create_researcher(db)

    # Jan-Jun: 80%
    data1 = EffortAllocationCreate(
        researcher_id=researcher.id,
        period_start=date(2026, 1, 1),
        period_end=date(2026, 6, 30),
        planned_pm=Decimal("4.00"),
        planned_fte_percentage=Decimal("80.00"),
    )
    await timesheet_service.create_effort_allocation(db, project1.id, data1)

    # Jul-Dec: 80% (non-overlapping, so OK)
    data2 = EffortAllocationCreate(
        researcher_id=researcher.id,
        period_start=date(2026, 7, 1),
        period_end=date(2026, 12, 31),
        planned_pm=Decimal("4.00"),
        planned_fte_percentage=Decimal("80.00"),
    )
    alloc = await timesheet_service.create_effort_allocation(db, project2.id, data2)
    assert alloc.id is not None


# --- Timesheet Entry Tests ---


@pytest.mark.asyncio
async def test_create_timesheet_entry(db: AsyncSession):
    """Create a basic timesheet entry."""
    project = await _create_project(db)
    researcher = await _create_researcher(db)
    data = TimesheetEntryCreate(
        researcher_id=researcher.id,
        date=date(2026, 3, 10),
        hours=Decimal("8.00"),
        description="Development work",
    )
    entry = await timesheet_service.create_timesheet_entry(db, project.id, data)
    assert entry.hours == Decimal("8.00")
    assert entry.submitted_at is None


@pytest.mark.asyncio
async def test_person_month_calculation(db: AsyncSession):
    """Person-months = hours / productive_hours."""
    pm = timesheet_service.calculate_person_months(Decimal("172.00"), 1720)
    assert pm == Decimal("0.10")

    pm2 = timesheet_service.calculate_person_months(Decimal("1720.00"), 1720)
    assert pm2 == Decimal("1.00")


@pytest.mark.asyncio
async def test_unit_costs_requires_wp(db: AsyncSession):
    """UNIT_COSTS projects require work_package_id on timesheets."""
    project = await _create_project(db, CostModel.UNIT_COSTS)
    researcher = await _create_researcher(db)
    data = TimesheetEntryCreate(
        researcher_id=researcher.id,
        date=date(2026, 3, 10),
        hours=Decimal("8.00"),
    )
    with pytest.raises(HTTPException) as exc:
        await timesheet_service.create_timesheet_entry(db, project.id, data)
    assert exc.value.status_code == 422
    assert "work_package_id" in exc.value.detail


@pytest.mark.asyncio
async def test_submit_timesheets(db: AsyncSession):
    """Batch submit sets submitted_at."""
    project = await _create_project(db)
    researcher = await _create_researcher(db)
    entry = await timesheet_service.create_timesheet_entry(
        db,
        project.id,
        TimesheetEntryCreate(
            researcher_id=researcher.id,
            date=date(2026, 3, 10),
            hours=Decimal("8.00"),
        ),
    )
    submitted = await timesheet_service.submit_timesheets(
        db, TimesheetSubmit(entry_ids=[entry.id])
    )
    assert submitted[0].submitted_at is not None


@pytest.mark.asyncio
async def test_approve_requires_submission(db: AsyncSession):
    """Approval fails if entry not yet submitted."""
    project = await _create_project(db)
    researcher = await _create_researcher(db)
    entry = await timesheet_service.create_timesheet_entry(
        db,
        project.id,
        TimesheetEntryCreate(
            researcher_id=researcher.id,
            date=date(2026, 3, 10),
            hours=Decimal("8.00"),
        ),
    )
    with pytest.raises(HTTPException) as exc:
        await timesheet_service.approve_timesheets(
            db, TimesheetSubmit(entry_ids=[entry.id])
        )
    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_cannot_edit_submitted_entry(db: AsyncSession):
    """Editing a submitted entry raises 409."""
    project = await _create_project(db)
    researcher = await _create_researcher(db)
    entry = await timesheet_service.create_timesheet_entry(
        db,
        project.id,
        TimesheetEntryCreate(
            researcher_id=researcher.id,
            date=date(2026, 3, 10),
            hours=Decimal("8.00"),
        ),
    )
    await timesheet_service.submit_timesheets(
        db, TimesheetSubmit(entry_ids=[entry.id])
    )
    with pytest.raises(HTTPException) as exc:
        await timesheet_service.update_timesheet_entry(
            db, entry.id, TimesheetEntryUpdate(hours=Decimal("7.00"))
        )
    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_cannot_delete_submitted_entry(db: AsyncSession):
    """Deleting a submitted entry raises 409."""
    project = await _create_project(db)
    researcher = await _create_researcher(db)
    entry = await timesheet_service.create_timesheet_entry(
        db,
        project.id,
        TimesheetEntryCreate(
            researcher_id=researcher.id,
            date=date(2026, 3, 10),
            hours=Decimal("8.00"),
        ),
    )
    await timesheet_service.submit_timesheets(
        db, TimesheetSubmit(entry_ids=[entry.id])
    )
    with pytest.raises(HTTPException) as exc:
        await timesheet_service.delete_timesheet_entry(db, entry.id)
    assert exc.value.status_code == 409


# --- Cross-Project Views ---


@pytest.mark.asyncio
async def test_researcher_allocation_view(db: AsyncSession):
    """Cross-project allocation shows committed and actual PMs."""
    project = await _create_project(db)
    researcher = await _create_researcher(db)

    # Add allocation
    await timesheet_service.create_effort_allocation(
        db,
        project.id,
        EffortAllocationCreate(
            researcher_id=researcher.id,
            period_start=date(2026, 1, 1),
            period_end=date(2026, 6, 30),
            planned_pm=Decimal("3.00"),
        ),
    )

    # Add timesheet hours across multiple days (8h * 5 = 40h)
    for day_offset in range(5):
        await timesheet_service.create_timesheet_entry(
            db,
            project.id,
            TimesheetEntryCreate(
                researcher_id=researcher.id,
                date=date(2026, 3, 10) + timedelta(days=day_offset),
                hours=Decimal("8.00"),
            ),
        )

    view = await timesheet_service.get_researcher_allocation(db, researcher.id)
    assert view.researcher_name == researcher.name
    assert len(view.allocations) == 1
    assert view.allocations[0].committed_pm == Decimal("3.00")
    # 40h / 1720 = 0.02 PM
    assert view.allocations[0].actual_pm == Decimal("0.02")


@pytest.mark.asyncio
async def test_project_effort_summary(db: AsyncSession):
    """Project effort summary shows planned vs actual per WP."""
    project = await _create_project(db)
    researcher = await _create_researcher(db)

    # Allocation without WP
    await timesheet_service.create_effort_allocation(
        db,
        project.id,
        EffortAllocationCreate(
            researcher_id=researcher.id,
            period_start=date(2026, 1, 1),
            period_end=date(2026, 12, 31),
            planned_pm=Decimal("6.00"),
        ),
    )

    # Timesheet entries: 8h * 5 days = 40h
    for day_offset in range(5):
        await timesheet_service.create_timesheet_entry(
            db,
            project.id,
            TimesheetEntryCreate(
                researcher_id=researcher.id,
                date=date(2026, 3, 10) + timedelta(days=day_offset),
                hours=Decimal("8.00"),
            ),
        )

    summary = await timesheet_service.get_project_effort_summary(db, project.id)
    assert summary.total_planned_pm == Decimal("6.00")
    # 40h / 1720 = 0.02 PM
    assert summary.total_actual_pm == Decimal("0.02")


# --- Compliance Report ---


@pytest.mark.asyncio
async def test_compliance_missing_timesheet(db: AsyncSession):
    """Detects researchers with allocations but no timesheet entries."""
    project = await _create_project(db)
    researcher = await _create_researcher(db)

    # Allocation but no timesheets
    await timesheet_service.create_effort_allocation(
        db,
        project.id,
        EffortAllocationCreate(
            researcher_id=researcher.id,
            period_start=date(2026, 1, 1),
            period_end=date(2026, 3, 31),
            planned_pm=Decimal("3.00"),
        ),
    )

    report = await timesheet_service.get_compliance_report(
        db, project.id, date(2026, 1, 1), date(2026, 3, 31)
    )
    assert report.total_issues >= 1
    missing = [i for i in report.issues if i.issue_type == "missing_timesheet"]
    assert len(missing) == 1
    assert missing[0].researcher_name == researcher.name
