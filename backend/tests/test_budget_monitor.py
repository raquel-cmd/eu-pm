"""Tests for the budget monitoring service (Section 4.3)."""

from datetime import date
from decimal import Decimal

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import (
    CostModel,
    DeliverableType,
    DisseminationLevel,
    ECBudgetCategory,
    MissionPurpose,
    Programme,
    ProjectRole,
    WPStatus,
)
from app.schemas.financial import (
    ExpenseCreate,
    FundDistributionCreate,
    MissionCreate,
    ProcurementCreate,
)
from app.schemas.partner import PartnerCreate, ProjectPartnerCreate
from app.schemas.project import ProjectCreate
from app.schemas.work_package import (
    DeliverableCreate,
    MilestoneCreate,
    WorkPackageCreate,
)
from app.services import budget_monitor
from app.services import financial as financial_service
from app.services import partner as partner_service
from app.services import project as project_service
from app.services import work_package as wp_service


async def _create_project(
    db: AsyncSession,
    cost_model: CostModel = CostModel.ACTUAL_COSTS,
    total_budget: Decimal | None = Decimal("500000.00"),
    eu_contribution: Decimal | None = Decimal("400000.00"),
    start_date: date | None = date(2025, 1, 1),
    end_date: date | None = date(2027, 12, 31),
    duration_months: int | None = 36,
):
    """Helper to create a project with budget details."""
    data = ProjectCreate(
        acronym=f"BM-{cost_model.value[:4]}",
        full_title="Budget Monitor Test Project",
        programme=Programme.HORIZON_EUROPE,
        cost_model=cost_model,
        role=ProjectRole.COORDINATOR,
        total_budget=total_budget,
        eu_contribution=eu_contribution,
        start_date=start_date,
        end_date=end_date,
        duration_months=duration_months,
    )
    return await project_service.create_project(db, data)


# --- Budget Summary Tests ---


@pytest.mark.asyncio
async def test_budget_summary_empty_project(db: AsyncSession):
    """Test budget summary for a project with no expenses."""
    project = await _create_project(db)
    summary = await budget_monitor.get_budget_summary(db, project.id)

    assert summary.project_id == project.id
    assert summary.total_budget == Decimal("500000.00")
    assert summary.eu_contribution == Decimal("400000.00")
    assert summary.total_spent == Decimal("0.00")
    assert summary.total_remaining == Decimal("500000.00")
    assert summary.percentage_used == Decimal("0.00")
    assert summary.indirect_costs_calculated == Decimal("0.00")
    assert len(summary.alerts) == 0


@pytest.mark.asyncio
async def test_budget_summary_with_expenses(db: AsyncSession):
    """Test budget summary includes expense totals."""
    project = await _create_project(db)
    await financial_service.create_expense(
        db,
        project.id,
        ExpenseCreate(
            ec_category=ECBudgetCategory.A_PERSONNEL,
            description="Salary",
            amount_gross=Decimal("10000.00"),
            date_incurred=date(2025, 3, 1),
        ),
    )
    await financial_service.create_expense(
        db,
        project.id,
        ExpenseCreate(
            ec_category=ECBudgetCategory.C1_TRAVEL,
            description="Flight",
            amount_gross=Decimal("500.00"),
            date_incurred=date(2025, 3, 15),
        ),
    )

    summary = await budget_monitor.get_budget_summary(db, project.id)

    # Indirect = 25% of (10000 A + 500 C1) = 2625
    assert summary.indirect_costs_calculated == Decimal("2625.00")
    # Total = 10000 + 500 + 2625 = 13125
    assert summary.total_spent == Decimal("13125.00")


@pytest.mark.asyncio
async def test_budget_summary_lump_sum_no_indirect(db: AsyncSession):
    """Test that lump sum projects don't get indirect cost calculation."""
    project = await _create_project(db, CostModel.LUMP_SUM)
    await financial_service.create_expense(
        db,
        project.id,
        ExpenseCreate(
            description="Internal expense",
            amount_gross=Decimal("5000.00"),
            date_incurred=date(2025, 3, 1),
        ),
    )

    summary = await budget_monitor.get_budget_summary(db, project.id)
    assert summary.indirect_costs_calculated == Decimal("0.00")


@pytest.mark.asyncio
async def test_budget_summary_includes_missions(db: AsyncSession):
    """Test that mission costs are included in summary."""
    project = await _create_project(db)
    await financial_service.create_mission(
        db,
        project.id,
        MissionCreate(
            researcher_name="Dr. Test",
            purpose=MissionPurpose.CONFERENCE,
            destination="Berlin",
            start_date=date(2025, 6, 1),
            end_date=date(2025, 6, 3),
            total_cost=Decimal("1000.00"),
        ),
    )

    summary = await budget_monitor.get_budget_summary(db, project.id)
    # Mission adds to C1_TRAVEL, indirect = 25% of 1000 = 250
    # Total = 1000 + 250 = 1250
    assert summary.total_spent == Decimal("1250.00")


@pytest.mark.asyncio
async def test_budget_summary_includes_procurements(db: AsyncSession):
    """Test that procurement costs are included in summary."""
    project = await _create_project(db)
    await financial_service.create_procurement(
        db,
        project.id,
        ProcurementCreate(
            description="Server",
            estimated_cost=Decimal("5000.00"),
        ),
    )

    summary = await budget_monitor.get_budget_summary(db, project.id)
    # Procurement adds to C2_EQUIPMENT, indirect = 25% of 5000 = 1250
    assert summary.total_spent == Decimal("6250.00")


@pytest.mark.asyncio
async def test_budget_summary_alert_warning(db: AsyncSession):
    """Test 80% threshold warning alert."""
    project = await _create_project(
        db, total_budget=Decimal("10000.00")
    )
    await financial_service.create_expense(
        db,
        project.id,
        ExpenseCreate(
            ec_category=ECBudgetCategory.B_SUBCONTRACTING,
            description="Subcontract",
            amount_gross=Decimal("8500.00"),
            date_incurred=date(2025, 6, 1),
        ),
    )

    summary = await budget_monitor.get_budget_summary(db, project.id)
    assert any("WARNING" in a for a in summary.alerts)


@pytest.mark.asyncio
async def test_budget_summary_alert_critical(db: AsyncSession):
    """Test 95% threshold critical alert."""
    project = await _create_project(
        db, total_budget=Decimal("10000.00")
    )
    await financial_service.create_expense(
        db,
        project.id,
        ExpenseCreate(
            ec_category=ECBudgetCategory.B_SUBCONTRACTING,
            description="Subcontract",
            amount_gross=Decimal("9600.00"),
            date_incurred=date(2025, 6, 1),
        ),
    )

    summary = await budget_monitor.get_budget_summary(db, project.id)
    assert any("CRITICAL" in a for a in summary.alerts)


@pytest.mark.asyncio
async def test_budget_summary_not_found(db: AsyncSession):
    """Test 404 for nonexistent project."""
    import uuid

    with pytest.raises(HTTPException) as exc_info:
        await budget_monitor.get_budget_summary(db, uuid.uuid4())
    assert exc_info.value.status_code == 404


# --- Indirect Costs Tests ---


@pytest.mark.asyncio
async def test_indirect_costs_25_percent_flat_rate(db: AsyncSession):
    """Test 25% flat rate on A+C+D (excluding B subcontracting)."""
    project = await _create_project(db)
    # A: Personnel
    await financial_service.create_expense(
        db,
        project.id,
        ExpenseCreate(
            ec_category=ECBudgetCategory.A_PERSONNEL,
            description="Personnel",
            amount_gross=Decimal("20000.00"),
            date_incurred=date(2025, 3, 1),
        ),
    )
    # B: Subcontracting (excluded from indirect base)
    await financial_service.create_expense(
        db,
        project.id,
        ExpenseCreate(
            ec_category=ECBudgetCategory.B_SUBCONTRACTING,
            description="Subcontract",
            amount_gross=Decimal("10000.00"),
            date_incurred=date(2025, 3, 1),
        ),
    )
    # D: Other costs
    await financial_service.create_expense(
        db,
        project.id,
        ExpenseCreate(
            ec_category=ECBudgetCategory.D_OTHER_COSTS,
            description="Other",
            amount_gross=Decimal("4000.00"),
            date_incurred=date(2025, 3, 1),
        ),
    )

    summary = await budget_monitor.get_budget_summary(db, project.id)
    # Indirect base = A(20000) + D(4000) = 24000 (B excluded)
    # Indirect = 24000 * 0.25 = 6000
    assert summary.indirect_costs_calculated == Decimal("6000.00")


# --- By Category Tests ---


@pytest.mark.asyncio
async def test_by_category(db: AsyncSession):
    """Test category breakdown response."""
    project = await _create_project(db)
    await financial_service.create_expense(
        db,
        project.id,
        ExpenseCreate(
            ec_category=ECBudgetCategory.A_PERSONNEL,
            description="Salary",
            amount_gross=Decimal("10000.00"),
            date_incurred=date(2025, 3, 1),
        ),
    )

    result = await budget_monitor.get_budget_by_category(db, project.id)
    assert result.project_id == project.id
    assert result.indirect_costs_calculated == Decimal("2500.00")
    assert result.indirect_costs_base == Decimal("10000.00")

    # Find A_PERSONNEL category
    a_cat = next(
        c for c in result.categories
        if c.category == ECBudgetCategory.A_PERSONNEL
    )
    assert a_cat.spent == Decimal("10000.00")


# --- By Partner Tests ---


@pytest.mark.asyncio
async def test_by_partner(db: AsyncSession):
    """Test partner spending breakdown."""
    project = await _create_project(db)
    partner = await partner_service.create_partner(
        db,
        PartnerCreate(
            legal_name="Test University",
            short_name="TU",
        ),
    )
    await partner_service.add_partner_to_project(
        db,
        project.id,
        ProjectPartnerCreate(
            partner_id=partner.id,
            partner_budget=Decimal("100000.00"),
        ),
    )

    # Expense assigned to partner
    await financial_service.create_expense(
        db,
        project.id,
        ExpenseCreate(
            ec_category=ECBudgetCategory.A_PERSONNEL,
            description="Partner salary",
            amount_gross=Decimal("5000.00"),
            date_incurred=date(2025, 3, 1),
            partner_id=partner.id,
        ),
    )
    # Unassigned expense
    await financial_service.create_expense(
        db,
        project.id,
        ExpenseCreate(
            ec_category=ECBudgetCategory.C1_TRAVEL,
            description="Unassigned travel",
            amount_gross=Decimal("1000.00"),
            date_incurred=date(2025, 4, 1),
        ),
    )

    result = await budget_monitor.get_budget_by_partner(db, project.id)
    assert len(result.partners) == 1
    assert result.partners[0].partner_name == "TU"
    assert result.partners[0].spent == Decimal("5000.00")
    assert result.partners[0].budgeted == Decimal("100000.00")
    assert result.unassigned_spending == Decimal("1000.00")


@pytest.mark.asyncio
async def test_by_partner_alert(db: AsyncSession):
    """Test partner spending alerts."""
    project = await _create_project(db)
    partner = await partner_service.create_partner(
        db,
        PartnerCreate(
            legal_name="Small Partner",
            short_name="SP",
        ),
    )
    await partner_service.add_partner_to_project(
        db,
        project.id,
        ProjectPartnerCreate(
            partner_id=partner.id,
            partner_budget=Decimal("10000.00"),
        ),
    )
    await financial_service.create_expense(
        db,
        project.id,
        ExpenseCreate(
            ec_category=ECBudgetCategory.A_PERSONNEL,
            description="Big expense",
            amount_gross=Decimal("9600.00"),
            date_incurred=date(2025, 3, 1),
            partner_id=partner.id,
        ),
    )

    result = await budget_monitor.get_budget_by_partner(db, project.id)
    assert any("CRITICAL" in a for a in result.alerts)


# --- Burn Rate Tests ---


@pytest.mark.asyncio
async def test_burn_rate_empty(db: AsyncSession):
    """Test burn rate for a project with no spending."""
    project = await _create_project(db)
    result = await budget_monitor.get_burn_rate(db, project.id)

    assert result.project_id == project.id
    assert result.total_budget == Decimal("500000.00")
    assert result.total_spent == Decimal("0.00")
    assert result.months_total == 36
    assert result.burn_rate_status == "on_track"


@pytest.mark.asyncio
async def test_burn_rate_with_spending(db: AsyncSession):
    """Test burn rate calculation with expenses."""
    project = await _create_project(db)
    await financial_service.create_expense(
        db,
        project.id,
        ExpenseCreate(
            ec_category=ECBudgetCategory.A_PERSONNEL,
            description="Salary",
            amount_gross=Decimal("50000.00"),
            date_incurred=date(2025, 6, 1),
        ),
    )

    result = await budget_monitor.get_burn_rate(db, project.id)
    assert result.total_spent > Decimal("0.00")
    assert result.months_total == 36


@pytest.mark.asyncio
async def test_burn_rate_no_dates(db: AsyncSession):
    """Test burn rate when project has no dates."""
    project = await _create_project(
        db,
        start_date=None,
        end_date=None,
        duration_months=None,
    )

    result = await budget_monitor.get_burn_rate(db, project.id)
    assert result.months_elapsed == 0
    assert result.months_total == 0


# --- Cash Flow Forecast Tests ---


@pytest.mark.asyncio
async def test_cash_flow_forecast_empty(db: AsyncSession):
    """Test cash flow forecast with no distributions."""
    project = await _create_project(db)
    result = await budget_monitor.get_cash_flow_forecast(db, project.id)

    assert result.project_id == project.id
    assert result.eu_contribution == Decimal("400000.00")
    assert result.total_received == Decimal("0.00")
    # Should have forecast entries for expected payments
    assert len(result.forecast) >= 2  # pre-financing + interim at minimum


@pytest.mark.asyncio
async def test_cash_flow_with_distributions(db: AsyncSession):
    """Test cash flow forecast with received distributions."""
    project = await _create_project(db)
    await financial_service.create_fund_distribution(
        db,
        project.id,
        FundDistributionCreate(
            distribution_type="pre_financing",
            amount=Decimal("160000.00"),
            distribution_date=date(2025, 3, 1),
        ),
    )

    result = await budget_monitor.get_cash_flow_forecast(db, project.id)
    assert result.total_received == Decimal("160000.00")
    # Pre-financing received, so forecast should not include another one
    pre_financing_forecast = [
        e for e in result.forecast
        if e.entry_type == "pre_financing"
        and "Received" in e.description
    ]
    assert len(pre_financing_forecast) == 1


@pytest.mark.asyncio
async def test_cash_flow_balance(db: AsyncSession):
    """Test current balance = received - spent."""
    project = await _create_project(db)
    await financial_service.create_fund_distribution(
        db,
        project.id,
        FundDistributionCreate(
            distribution_type="pre_financing",
            amount=Decimal("100000.00"),
            distribution_date=date(2025, 2, 1),
        ),
    )
    await financial_service.create_expense(
        db,
        project.id,
        ExpenseCreate(
            ec_category=ECBudgetCategory.A_PERSONNEL,
            description="Salary",
            amount_gross=Decimal("30000.00"),
            date_incurred=date(2025, 3, 1),
        ),
    )

    result = await budget_monitor.get_cash_flow_forecast(db, project.id)
    assert result.current_balance == Decimal("70000.00")


# --- WP Completion (Lump Sum) Tests ---


@pytest.mark.asyncio
async def test_wp_completion_lump_sum(db: AsyncSession):
    """Test WP completion tracking for lump sum projects."""
    project = await _create_project(db, CostModel.LUMP_SUM)
    wp = await wp_service.create_work_package(
        db,
        project.id,
        WorkPackageCreate(
            wp_number=1,
            title="WP1 Research",
            status=WPStatus.IN_PROGRESS,
        ),
    )

    # Add deliverable (submitted)
    await wp_service.create_deliverable(
        db,
        wp.id,
        DeliverableCreate(
            deliverable_number="D1.1",
            title="Report",
            type=DeliverableType.REPORT,
            dissemination_level=DisseminationLevel.PU,
            submission_date=date(2025, 6, 1),
        ),
    )
    # Add deliverable (not submitted)
    await wp_service.create_deliverable(
        db,
        wp.id,
        DeliverableCreate(
            deliverable_number="D1.2",
            title="Software",
            type=DeliverableType.SOFTWARE,
            dissemination_level=DisseminationLevel.PU,
        ),
    )
    # Add milestone (achieved)
    await wp_service.create_milestone(
        db,
        wp.id,
        MilestoneCreate(
            milestone_number="M1.1",
            title="Prototype",
            achieved=True,
        ),
    )

    # Add an expense on this WP
    await financial_service.create_expense(
        db,
        project.id,
        ExpenseCreate(
            description="WP1 expense",
            amount_gross=Decimal("2000.00"),
            date_incurred=date(2025, 5, 1),
            work_package_id=wp.id,
        ),
    )

    result = await budget_monitor.get_wp_completion_status(db, project.id)
    assert len(result) == 1
    wp_status = result[0]
    assert wp_status.wp_number == 1
    assert wp_status.deliverables_total == 2
    assert wp_status.deliverables_submitted == 1
    assert wp_status.milestones_total == 1
    assert wp_status.milestones_achieved == 1
    assert wp_status.total_spending == Decimal("2000.00")
    # 2 of 3 items completed = 66.67%
    assert wp_status.completion_percentage == Decimal("66.67")


@pytest.mark.asyncio
async def test_wp_completion_not_lump_sum_fails(db: AsyncSession):
    """Test that WP completion tracking fails for non-lump sum projects."""
    project = await _create_project(db, CostModel.ACTUAL_COSTS)
    with pytest.raises(HTTPException) as exc_info:
        await budget_monitor.get_wp_completion_status(db, project.id)
    assert exc_info.value.status_code == 400


# --- Budget Transfer Validation ---


def test_validate_budget_transfer_within_limit():
    """Test transfer within 20% limit."""
    assert budget_monitor.validate_budget_transfer(
        Decimal("100000.00"), Decimal("19000.00")
    ) is True


def test_validate_budget_transfer_exceeds_limit():
    """Test transfer exceeding 20% limit."""
    assert budget_monitor.validate_budget_transfer(
        Decimal("100000.00"), Decimal("21000.00")
    ) is False


def test_validate_budget_transfer_at_boundary():
    """Test transfer at exactly 20%."""
    assert budget_monitor.validate_budget_transfer(
        Decimal("100000.00"), Decimal("20000.00")
    ) is True


def test_validate_budget_transfer_zero_budget():
    """Test transfer with zero budget."""
    assert budget_monitor.validate_budget_transfer(
        Decimal("0.00"), Decimal("100.00")
    ) is False
