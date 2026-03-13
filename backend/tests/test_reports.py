"""Tests for the institutional reporting service (Section 6)."""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import (
    ContractType,
    CostModel,
    ECBudgetCategory,
    ExpenseStatus,
    MissionPurpose,
    Programme,
    ProjectRole,
    ResearcherPosition,
)
from app.schemas.financial import (
    BudgetCategoryMappingCreate,
    ExpenseCreate,
    FundDistributionCreate,
    MissionCreate,
)
from app.schemas.project import ProjectCreate
from app.schemas.researcher import (
    EffortAllocationCreate,
    ResearcherCreate,
    TimesheetEntryCreate,
)
from app.services import financial as financial_service
from app.services import project as project_service
from app.services import reports as reports_service
from app.services import timesheet as timesheet_service


# --- Helpers ---


async def _create_project(
    db: AsyncSession,
    acronym: str = "RPT-TEST",
    cost_model: CostModel = CostModel.ACTUAL_COSTS,
    total_budget: Decimal = Decimal("100000.00"),
    eu_contribution: Decimal = Decimal("80000.00"),
    end_date: date | None = date(2026, 12, 31),
) -> "Project":
    """Helper to create a project."""
    data = ProjectCreate(
        acronym=acronym,
        full_title=f"Report Test - {acronym}",
        programme=Programme.HORIZON_EUROPE,
        cost_model=cost_model,
        role=ProjectRole.COORDINATOR,
        total_budget=total_budget,
        eu_contribution=eu_contribution,
        start_date=date(2025, 1, 1),
        end_date=end_date,
    )
    return await project_service.create_project(db, data)


async def _create_researcher(
    db: AsyncSession,
    name: str = "Test Researcher",
    annual_gross_cost: Decimal = Decimal("51600.00"),
    end_date: date | None = None,
) -> "Researcher":
    """Helper to create a researcher."""
    data = ResearcherCreate(
        name=name,
        email=f"{name.lower().replace(' ', '.')}@test.pt",
        position=ResearcherPosition.POSTDOC,
        contract_type=ContractType.DL57,
        fte=Decimal("1.00"),
        annual_gross_cost=annual_gross_cost,
        productive_hours=1720,
        start_date=date(2025, 1, 1),
        end_date=end_date,
    )
    return await timesheet_service.create_researcher(db, data)


async def _create_expense(
    db: AsyncSession,
    project_id,
    amount: Decimal = Decimal("1000.00"),
    category: ECBudgetCategory = ECBudgetCategory.A_PERSONNEL,
    date_incurred: date = date(2025, 6, 15),
) -> "Expense":
    """Helper to create an expense."""
    data = ExpenseCreate(
        description="Test expense",
        amount_gross=amount,
        currency="EUR",
        date_incurred=date_incurred,
        ec_category=category,
        ec_eligible=True,
    )
    return await financial_service.create_expense(db, project_id, data)


# --- Dashboard Tests ---


@pytest.mark.asyncio
async def test_dashboard_empty(db: AsyncSession):
    """Dashboard with no projects returns zero totals."""
    result = await reports_service.get_finance_dashboard(db)
    assert result.projects == []
    assert result.total_budget_all_projects == Decimal("0.00")
    assert result.total_spent_all_projects == Decimal("0.00")
    assert result.overall_burn_rate == Decimal("0.00")


@pytest.mark.asyncio
async def test_dashboard_single_project_with_expense(db: AsyncSession):
    """Dashboard shows correct totals for a single project with expenses."""
    project = await _create_project(db)
    await _create_expense(db, project.id, Decimal("25000.00"))

    result = await reports_service.get_finance_dashboard(db)
    assert len(result.projects) == 1
    row = result.projects[0]
    assert row.acronym == "RPT-TEST"
    assert row.total_budget == Decimal("100000.00")
    assert row.total_spent == Decimal("25000.00")
    assert row.burn_rate_percentage == Decimal("25.00")
    assert row.burn_rate_status == "on_track"
    assert result.total_budget_all_projects == Decimal("100000.00")
    assert result.total_spent_all_projects == Decimal("25000.00")


@pytest.mark.asyncio
async def test_dashboard_multi_project_aggregation(db: AsyncSession):
    """Dashboard aggregates across multiple projects."""
    p1 = await _create_project(db, acronym="RPT-P1")
    p2 = await _create_project(
        db, acronym="RPT-P2",
        total_budget=Decimal("200000.00"),
        eu_contribution=Decimal("150000.00"),
    )
    await _create_expense(db, p1.id, Decimal("10000.00"))
    await _create_expense(db, p2.id, Decimal("20000.00"))

    result = await reports_service.get_finance_dashboard(db)
    assert len(result.projects) == 2
    assert result.total_budget_all_projects == Decimal("300000.00")
    assert result.total_spent_all_projects == Decimal("30000.00")
    assert result.overall_burn_rate == Decimal("10.00")


@pytest.mark.asyncio
async def test_dashboard_budget_alert_critical(db: AsyncSession):
    """Dashboard flags CRITICAL when burn rate >= 95%."""
    project = await _create_project(
        db, total_budget=Decimal("10000.00"),
        eu_contribution=Decimal("8000.00"),
    )
    await _create_expense(db, project.id, Decimal("9600.00"))

    result = await reports_service.get_finance_dashboard(db)
    row = result.projects[0]
    assert row.burn_rate_percentage == Decimal("96.00")
    assert row.burn_rate_status == "over_spending"
    assert "OVER_BUDGET" in row.flags
    assert any(f.severity == "CRITICAL" for f in result.flagged_items)


@pytest.mark.asyncio
async def test_dashboard_upcoming_ec_payment(db: AsyncSession):
    """Dashboard shows upcoming EC payments when funds remain."""
    project = await _create_project(db)
    # No fund distributions yet → full EU contribution is remaining
    result = await reports_service.get_finance_dashboard(db)
    assert len(result.upcoming_ec_payments) == 1
    assert result.upcoming_ec_payments[0].expected_amount == Decimal("80000.00")


@pytest.mark.asyncio
async def test_dashboard_pm_compliance(db: AsyncSession):
    """Dashboard calculates PM compliance rate."""
    project = await _create_project(db)
    r1 = await _create_researcher(db, name="Researcher One")
    r2 = await _create_researcher(db, name="Researcher Two")

    # Both have allocations
    alloc1 = EffortAllocationCreate(
        researcher_id=r1.id,
        period_start=date(2025, 1, 1),
        period_end=date(2025, 12, 31),
        planned_pm=Decimal("6.00"),
        planned_fte_percentage=Decimal("50.00"),
    )
    await timesheet_service.create_effort_allocation(db, project.id, alloc1)
    alloc2 = EffortAllocationCreate(
        researcher_id=r2.id,
        period_start=date(2025, 1, 1),
        period_end=date(2025, 12, 31),
        planned_pm=Decimal("6.00"),
        planned_fte_percentage=Decimal("50.00"),
    )
    await timesheet_service.create_effort_allocation(db, project.id, alloc2)

    # Only r1 has timesheets
    ts_data = TimesheetEntryCreate(
        researcher_id=r1.id,
        date=date(2025, 3, 3),
        hours=Decimal("8.00"),
    )
    await timesheet_service.create_timesheet_entry(db, project.id, ts_data)

    result = await reports_service.get_finance_dashboard(db)
    row = result.projects[0]
    assert row.pm_compliance_rate == Decimal("50.00")


# --- PM Declarations Tests ---


@pytest.mark.asyncio
async def test_pm_declarations_basic(db: AsyncSession):
    """PM declarations shows researcher hours and cost."""
    project = await _create_project(db)
    researcher = await _create_researcher(db)

    # Allocation
    alloc_data = EffortAllocationCreate(
        researcher_id=researcher.id,
        period_start=date(2025, 1, 1),
        period_end=date(2025, 6, 30),
        planned_pm=Decimal("3.00"),
        planned_fte_percentage=Decimal("50.00"),
    )
    await timesheet_service.create_effort_allocation(db, project.id, alloc_data)

    # 5 days of 8h timesheets
    for i in range(5):
        ts_data = TimesheetEntryCreate(
            researcher_id=researcher.id,
            date=date(2025, 3, 3) + timedelta(days=i),
            hours=Decimal("8.00"),
        )
        await timesheet_service.create_timesheet_entry(db, project.id, ts_data)

    result = await reports_service.get_pm_declarations(
        db, project.id, date(2025, 1, 1), date(2025, 6, 30)
    )
    assert len(result.declarations) == 1
    decl = result.declarations[0]
    assert decl.actual_hours == Decimal("40.00")
    # 40 / 1720 = 0.02 PM
    assert decl.actual_pm == Decimal("0.02")
    # 40 * 30.00 = 1200.00
    assert decl.personnel_cost == Decimal("1200.00")
    assert decl.planned_pm == Decimal("3.00")


@pytest.mark.asyncio
async def test_pm_declarations_no_timesheets(db: AsyncSession):
    """PM declarations shows zero when no timesheets exist."""
    project = await _create_project(db)
    researcher = await _create_researcher(db)

    alloc_data = EffortAllocationCreate(
        researcher_id=researcher.id,
        period_start=date(2025, 1, 1),
        period_end=date(2025, 6, 30),
        planned_pm=Decimal("3.00"),
        planned_fte_percentage=Decimal("50.00"),
    )
    await timesheet_service.create_effort_allocation(db, project.id, alloc_data)

    result = await reports_service.get_pm_declarations(
        db, project.id, date(2025, 1, 1), date(2025, 6, 30)
    )
    assert len(result.declarations) == 1
    assert result.declarations[0].actual_hours == Decimal("0.00")
    assert result.declarations[0].actual_pm == Decimal("0.00")
    assert result.declarations[0].personnel_cost == Decimal("0.00")


@pytest.mark.asyncio
async def test_pm_declarations_not_found(db: AsyncSession):
    """PM declarations raises 404 for nonexistent project."""
    import uuid

    with pytest.raises(HTTPException) as exc_info:
        await reports_service.get_pm_declarations(
            db, uuid.uuid4(), date(2025, 1, 1), date(2025, 6, 30)
        )
    assert exc_info.value.status_code == 404


# --- Cost Statement Tests ---


@pytest.mark.asyncio
async def test_cost_statement_by_category(db: AsyncSession):
    """Cost statement groups expenses by EC category."""
    project = await _create_project(db)
    await _create_expense(
        db, project.id, Decimal("5000.00"), ECBudgetCategory.A_PERSONNEL
    )
    await _create_expense(
        db, project.id, Decimal("2000.00"), ECBudgetCategory.C1_TRAVEL
    )

    result = await reports_service.get_cost_statement(db, project.id)
    cat_map = {line.ec_category: line for line in result.lines}
    assert cat_map[ECBudgetCategory.A_PERSONNEL].incurred == Decimal("5000.00")
    assert cat_map[ECBudgetCategory.C1_TRAVEL].incurred == Decimal("2000.00")
    assert result.total_incurred == Decimal("7000.00")


@pytest.mark.asyncio
async def test_cost_statement_with_indirect(db: AsyncSession):
    """Cost statement calculates 25% indirect on A+C+D categories."""
    project = await _create_project(db)
    await _create_expense(
        db, project.id, Decimal("10000.00"), ECBudgetCategory.A_PERSONNEL
    )
    await _create_expense(
        db, project.id, Decimal("4000.00"), ECBudgetCategory.D_OTHER_COSTS
    )

    result = await reports_service.get_cost_statement(db, project.id)
    # Indirect base = 10000 + 4000 = 14000, 25% = 3500
    assert result.indirect_costs == Decimal("3500.00")
    assert result.grand_total == Decimal("17500.00")


@pytest.mark.asyncio
async def test_cost_statement_university_mapping(db: AsyncSession):
    """Cost statement includes university account code mappings."""
    project = await _create_project(db)
    await _create_expense(
        db, project.id, Decimal("5000.00"), ECBudgetCategory.A_PERSONNEL
    )

    # Create a mapping
    mapping_data = BudgetCategoryMappingCreate(
        ec_category=ECBudgetCategory.A_PERSONNEL,
        university_account_code="6311.01",
        university_category_name="Personnel Costs",
    )
    await financial_service.create_budget_mapping(db, project.id, mapping_data)

    result = await reports_service.get_cost_statement(db, project.id)
    a_line = next(
        l for l in result.lines
        if l.ec_category == ECBudgetCategory.A_PERSONNEL
    )
    assert a_line.university_account_code == "6311.01"
    assert a_line.university_category_name == "Personnel Costs"


# --- Overhead Calculation Tests ---


@pytest.mark.asyncio
async def test_overhead_actual_costs(db: AsyncSession):
    """Overhead calculation applies 25% rate for actual cost projects."""
    project = await _create_project(db)
    await _create_expense(
        db, project.id, Decimal("10000.00"), ECBudgetCategory.A_PERSONNEL
    )
    await _create_expense(
        db, project.id, Decimal("3000.00"), ECBudgetCategory.B_SUBCONTRACTING
    )

    result = await reports_service.get_overhead_calculations(db, project.id)
    # Base = A (10000), B excluded from indirect base
    assert result.direct_costs_base == Decimal("10000.00")
    assert result.indirect_rate == Decimal("0.25")
    assert result.indirect_costs == Decimal("2500.00")
    assert result.subcontracting_excluded == Decimal("3000.00")


@pytest.mark.asyncio
async def test_overhead_lump_sum_no_indirect(db: AsyncSession):
    """Lump sum projects have zero indirect costs."""
    project = await _create_project(db, cost_model=CostModel.LUMP_SUM)
    await _create_expense(
        db, project.id, Decimal("10000.00"), ECBudgetCategory.A_PERSONNEL
    )

    result = await reports_service.get_overhead_calculations(db, project.id)
    assert result.indirect_costs == Decimal("0.00")
    assert result.cost_model == CostModel.LUMP_SUM


# --- Annual Summary Tests ---


@pytest.mark.asyncio
async def test_annual_summary_year_filter(db: AsyncSession):
    """Annual summary filters expenses by year."""
    project = await _create_project(db)
    await _create_expense(
        db, project.id, Decimal("5000.00"),
        date_incurred=date(2025, 6, 15),
    )
    await _create_expense(
        db, project.id, Decimal("3000.00"),
        date_incurred=date(2026, 3, 15),
    )

    result = await reports_service.get_annual_summary(db, 2025)
    assert len(result.projects) == 1
    assert result.projects[0].total_spent_year == Decimal("5000.00")


@pytest.mark.asyncio
async def test_annual_summary_cumulative(db: AsyncSession):
    """Annual summary shows cumulative totals up to end of year."""
    project = await _create_project(db)
    await _create_expense(
        db, project.id, Decimal("5000.00"),
        date_incurred=date(2025, 3, 15),
    )
    await _create_expense(
        db, project.id, Decimal("7000.00"),
        date_incurred=date(2025, 9, 15),
    )

    result = await reports_service.get_annual_summary(db, 2025)
    proj = result.projects[0]
    assert proj.total_spent_year == Decimal("12000.00")
    assert proj.total_spent_cumulative == Decimal("12000.00")
    assert proj.budget_remaining == Decimal("88000.00")


@pytest.mark.asyncio
async def test_annual_summary_fund_distributions(db: AsyncSession):
    """Annual summary includes fund distribution data."""
    project = await _create_project(db)

    fd_data = FundDistributionCreate(
        distribution_type="pre_financing",
        amount=Decimal("40000.00"),
        distribution_date=date(2025, 4, 1),
    )
    await financial_service.create_fund_distribution(db, project.id, fd_data)

    result = await reports_service.get_annual_summary(db, 2025)
    proj = result.projects[0]
    assert proj.funds_received_year == Decimal("40000.00")
    assert proj.funds_received_cumulative == Decimal("40000.00")


# --- Role Access Tests ---


@pytest.mark.asyncio
async def test_role_access_non_finance_pm_rejected():
    """Non-finance PM role is rejected by require_finance_pm."""
    from app.models.enums import UserRole
    from app.core.auth import require_finance_pm

    with pytest.raises(HTTPException) as exc_info:
        await require_finance_pm(role=UserRole.PI)
    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_role_access_finance_pm_allowed():
    """Central Finance PM role passes require_finance_pm."""
    from app.models.enums import UserRole
    from app.core.auth import require_finance_pm

    result = await require_finance_pm(role=UserRole.CENTRAL_FINANCE_PM)
    assert result == UserRole.CENTRAL_FINANCE_PM
