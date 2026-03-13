"""Tests for the financial service layer (Section 4)."""

from datetime import date
from decimal import Decimal

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import (
    ApprovalStatus,
    CostModel,
    ECBudgetCategory,
    ExpenseStatus,
    MissionPurpose,
    Programme,
    ProcurementApprovalStatus,
    ProcurementMethod,
    ProjectRole,
)
from app.schemas.financial import (
    BudgetCategoryMappingCreate,
    BudgetCategoryMappingUpdate,
    ExpenseCreate,
    ExpenseUpdate,
    FundDistributionCreate,
    MissionApprove,
    MissionComplete,
    MissionCreate,
    MissionUpdate,
    ProcurementCreate,
)
from app.schemas.project import ProjectCreate
from app.services import financial as financial_service
from app.services import project as project_service


async def _create_project(
    db: AsyncSession, cost_model: CostModel = CostModel.ACTUAL_COSTS
) -> "Project":
    """Helper to create a project with a given cost model."""
    data = ProjectCreate(
        acronym=f"FIN-{cost_model.value[:4]}",
        full_title="Financial Test Project",
        programme=Programme.HORIZON_EUROPE,
        cost_model=cost_model,
        role=ProjectRole.COORDINATOR,
    )
    return await project_service.create_project(db, data)


# --- Budget Category Mapping Tests ---


@pytest.mark.asyncio
async def test_create_budget_mapping(db: AsyncSession):
    """Test creating a budget category mapping."""
    project = await _create_project(db)
    data = BudgetCategoryMappingCreate(
        ec_category=ECBudgetCategory.A_PERSONNEL,
        university_account_code="HR-001",
        university_category_name="Personnel Costs",
    )
    mapping = await financial_service.create_budget_mapping(
        db, project.id, data
    )
    assert mapping.id is not None
    assert mapping.ec_category == ECBudgetCategory.A_PERSONNEL
    assert mapping.university_account_code == "HR-001"


@pytest.mark.asyncio
async def test_list_budget_mappings(db: AsyncSession):
    """Test listing budget category mappings."""
    project = await _create_project(db)
    await financial_service.create_budget_mapping(
        db,
        project.id,
        BudgetCategoryMappingCreate(
            ec_category=ECBudgetCategory.A_PERSONNEL,
            university_account_code="HR-001",
        ),
    )
    await financial_service.create_budget_mapping(
        db,
        project.id,
        BudgetCategoryMappingCreate(
            ec_category=ECBudgetCategory.C1_TRAVEL,
            university_account_code="TRAVEL-001",
        ),
    )
    items, total = await financial_service.list_budget_mappings(
        db, project.id
    )
    assert total == 2


@pytest.mark.asyncio
async def test_update_budget_mapping(db: AsyncSession):
    """Test updating a budget category mapping."""
    project = await _create_project(db)
    mapping = await financial_service.create_budget_mapping(
        db,
        project.id,
        BudgetCategoryMappingCreate(
            ec_category=ECBudgetCategory.A_PERSONNEL,
            university_account_code="HR-001",
        ),
    )
    updated = await financial_service.update_budget_mapping(
        db,
        mapping.id,
        BudgetCategoryMappingUpdate(university_account_code="HR-002"),
    )
    assert updated is not None
    assert updated.university_account_code == "HR-002"


@pytest.mark.asyncio
async def test_delete_budget_mapping(db: AsyncSession):
    """Test deleting a budget category mapping."""
    project = await _create_project(db)
    mapping = await financial_service.create_budget_mapping(
        db,
        project.id,
        BudgetCategoryMappingCreate(
            ec_category=ECBudgetCategory.B_SUBCONTRACTING,
            university_account_code="SUB-001",
        ),
    )
    assert await financial_service.delete_budget_mapping(db, mapping.id) is True
    items, total = await financial_service.list_budget_mappings(
        db, project.id
    )
    assert total == 0


# --- Expense Tests ---


@pytest.mark.asyncio
async def test_create_expense_actual_costs(db: AsyncSession):
    """Test creating an expense for an actual costs project."""
    project = await _create_project(db, CostModel.ACTUAL_COSTS)
    data = ExpenseCreate(
        ec_category=ECBudgetCategory.C1_TRAVEL,
        description="Conference travel",
        amount_gross=Decimal("1500.00"),
        date_incurred=date(2025, 6, 15),
    )
    expense = await financial_service.create_expense(db, project.id, data)
    assert expense.id is not None
    assert expense.ec_eligible is True
    assert expense.ec_category == ECBudgetCategory.C1_TRAVEL


@pytest.mark.asyncio
async def test_create_expense_actual_costs_requires_ec_category(
    db: AsyncSession,
):
    """Test that actual costs projects require ec_category."""
    project = await _create_project(db, CostModel.ACTUAL_COSTS)
    data = ExpenseCreate(
        description="Missing category",
        amount_gross=Decimal("100.00"),
        date_incurred=date(2025, 6, 15),
    )
    with pytest.raises(HTTPException) as exc_info:
        await financial_service.create_expense(db, project.id, data)
    assert exc_info.value.status_code == 422
    assert "ec_category" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_create_expense_actual_costs_requires_docs_on_submit(
    db: AsyncSession,
):
    """Test that non-draft expenses in actual costs require supporting_docs."""
    project = await _create_project(db, CostModel.ACTUAL_COSTS)
    data = ExpenseCreate(
        ec_category=ECBudgetCategory.A_PERSONNEL,
        description="Personnel cost",
        amount_gross=Decimal("3000.00"),
        date_incurred=date(2025, 6, 15),
        status=ExpenseStatus.SUBMITTED,
    )
    with pytest.raises(HTTPException) as exc_info:
        await financial_service.create_expense(db, project.id, data)
    assert exc_info.value.status_code == 422
    assert "supporting_docs" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_create_expense_lump_sum_sets_ec_eligible_false(
    db: AsyncSession,
):
    """Test that lump sum projects set ec_eligible to false."""
    project = await _create_project(db, CostModel.LUMP_SUM)
    data = ExpenseCreate(
        description="Internal tracking expense",
        amount_gross=Decimal("500.00"),
        date_incurred=date(2025, 6, 15),
        ec_eligible=True,  # should be overridden to false
    )
    expense = await financial_service.create_expense(db, project.id, data)
    assert expense.ec_eligible is False


@pytest.mark.asyncio
async def test_list_expenses(db: AsyncSession):
    """Test listing expenses."""
    project = await _create_project(db, CostModel.ACTUAL_COSTS)
    for i in range(3):
        await financial_service.create_expense(
            db,
            project.id,
            ExpenseCreate(
                ec_category=ECBudgetCategory.C1_TRAVEL,
                description=f"Expense {i}",
                amount_gross=Decimal("100.00"),
                date_incurred=date(2025, 6, i + 1),
            ),
        )
    items, total = await financial_service.list_expenses(db, project.id)
    assert total == 3


@pytest.mark.asyncio
async def test_update_expense(db: AsyncSession):
    """Test updating an expense."""
    project = await _create_project(db, CostModel.ACTUAL_COSTS)
    expense = await financial_service.create_expense(
        db,
        project.id,
        ExpenseCreate(
            ec_category=ECBudgetCategory.C2_EQUIPMENT,
            description="Laptop",
            amount_gross=Decimal("1200.00"),
            date_incurred=date(2025, 7, 1),
        ),
    )
    updated = await financial_service.update_expense(
        db,
        project.id,
        expense.id,
        ExpenseUpdate(description="Laptop + accessories"),
    )
    assert updated is not None
    assert updated.description == "Laptop + accessories"


@pytest.mark.asyncio
async def test_delete_expense(db: AsyncSession):
    """Test soft-deleting an expense."""
    project = await _create_project(db, CostModel.ACTUAL_COSTS)
    expense = await financial_service.create_expense(
        db,
        project.id,
        ExpenseCreate(
            ec_category=ECBudgetCategory.A_PERSONNEL,
            description="To delete",
            amount_gross=Decimal("50.00"),
            date_incurred=date(2025, 7, 1),
        ),
    )
    assert (
        await financial_service.delete_expense(
            db, project.id, expense.id
        )
        is True
    )
    assert await financial_service.get_expense(db, expense.id) is None


# --- Mission Tests ---


@pytest.mark.asyncio
async def test_create_mission_actual_costs(db: AsyncSession):
    """Test creating a mission for an actual costs project."""
    project = await _create_project(db, CostModel.ACTUAL_COSTS)
    data = MissionCreate(
        researcher_name="Dr. Smith",
        purpose=MissionPurpose.CONFERENCE,
        destination="Brussels, Belgium",
        start_date=date(2025, 9, 1),
        end_date=date(2025, 9, 3),
        travel_costs=Decimal("350.00"),
        accommodation_costs=Decimal("300.00"),
        total_cost=Decimal("650.00"),
    )
    mission = await financial_service.create_mission(db, project.id, data)
    assert mission.id is not None
    assert mission.ec_eligible is True


@pytest.mark.asyncio
async def test_create_mission_lump_sum_sets_ec_eligible_false(
    db: AsyncSession,
):
    """Test that lump sum missions set ec_eligible to false."""
    project = await _create_project(db, CostModel.LUMP_SUM)
    data = MissionCreate(
        researcher_name="Dr. Jones",
        purpose=MissionPurpose.CONSORTIUM_MEETING,
        destination="Lisbon, Portugal",
        start_date=date(2025, 10, 1),
        end_date=date(2025, 10, 2),
    )
    mission = await financial_service.create_mission(db, project.id, data)
    assert mission.ec_eligible is False


@pytest.mark.asyncio
async def test_list_missions(db: AsyncSession):
    """Test listing missions."""
    project = await _create_project(db, CostModel.ACTUAL_COSTS)
    await financial_service.create_mission(
        db,
        project.id,
        MissionCreate(
            researcher_name="Dr. A",
            purpose=MissionPurpose.FIELDWORK,
            destination="Berlin",
            start_date=date(2025, 8, 1),
            end_date=date(2025, 8, 5),
        ),
    )
    await financial_service.create_mission(
        db,
        project.id,
        MissionCreate(
            researcher_name="Dr. B",
            purpose=MissionPurpose.TRAINING,
            destination="Paris",
            start_date=date(2025, 9, 1),
            end_date=date(2025, 9, 2),
        ),
    )
    items, total = await financial_service.list_missions(db, project.id)
    assert total == 2


@pytest.mark.asyncio
async def test_delete_mission(db: AsyncSession):
    """Test soft-deleting a mission."""
    project = await _create_project(db, CostModel.ACTUAL_COSTS)
    mission = await financial_service.create_mission(
        db,
        project.id,
        MissionCreate(
            researcher_name="Dr. Delete",
            purpose=MissionPurpose.OTHER,
            destination="Madrid",
            start_date=date(2025, 11, 1),
            end_date=date(2025, 11, 1),
        ),
    )
    assert (
        await financial_service.delete_mission(
            db, project.id, mission.id
        )
        is True
    )
    assert await financial_service.get_mission(db, mission.id) is None


# --- Mission Workflow Tests ---


@pytest.mark.asyncio
async def test_create_mission_sets_requested_status(db: AsyncSession):
    """Test that create_mission forces REQUESTED status."""
    project = await _create_project(db, CostModel.ACTUAL_COSTS)
    data = MissionCreate(
        researcher_name="Dr. Smith",
        purpose=MissionPurpose.CONFERENCE,
        destination="Brussels, Belgium",
        start_date=date(2025, 9, 1),
        end_date=date(2025, 9, 3),
        total_cost=Decimal("650.00"),
    )
    mission = await financial_service.create_mission(db, project.id, data)
    assert mission.approval_status == ApprovalStatus.REQUESTED
    assert mission.estimated_total_cost == Decimal("650.00")


@pytest.mark.asyncio
async def test_create_mission_detects_international(db: AsyncSession):
    """Test that destinations outside EU are flagged as international."""
    project = await _create_project(db, CostModel.ACTUAL_COSTS)
    data = MissionCreate(
        researcher_name="Dr. Smith",
        purpose=MissionPurpose.CONFERENCE,
        destination="New York, USA",
        start_date=date(2025, 9, 1),
        end_date=date(2025, 9, 5),
        total_cost=Decimal("2000.00"),
    )
    mission = await financial_service.create_mission(db, project.id, data)
    assert mission.is_international is True
    assert mission.requires_central_approval is True


@pytest.mark.asyncio
async def test_create_mission_eu_destination_not_international(
    db: AsyncSession,
):
    """Test that EU destinations are not flagged as international."""
    project = await _create_project(db, CostModel.ACTUAL_COSTS)
    data = MissionCreate(
        researcher_name="Dr. Smith",
        purpose=MissionPurpose.CONFERENCE,
        destination="Berlin, Germany",
        start_date=date(2025, 9, 1),
        end_date=date(2025, 9, 3),
        total_cost=Decimal("500.00"),
    )
    mission = await financial_service.create_mission(db, project.id, data)
    assert mission.is_international is False
    assert mission.requires_central_approval is False


@pytest.mark.asyncio
async def test_create_mission_high_cost_requires_central(
    db: AsyncSession,
):
    """Test that missions >= 5000 EUR require central approval."""
    project = await _create_project(db, CostModel.ACTUAL_COSTS)
    data = MissionCreate(
        researcher_name="Dr. Smith",
        purpose=MissionPurpose.CONFERENCE,
        destination="Paris, France",
        start_date=date(2025, 9, 1),
        end_date=date(2025, 9, 5),
        total_cost=Decimal("5000.00"),
    )
    mission = await financial_service.create_mission(db, project.id, data)
    assert mission.requires_central_approval is True


@pytest.mark.asyncio
async def test_create_mission_lump_sum_skips_central(db: AsyncSession):
    """Test that lump sum missions never require central approval."""
    project = await _create_project(db, CostModel.LUMP_SUM)
    data = MissionCreate(
        researcher_name="Dr. Jones",
        purpose=MissionPurpose.CONFERENCE,
        destination="New York, USA",
        start_date=date(2025, 10, 1),
        end_date=date(2025, 10, 5),
        total_cost=Decimal("8000.00"),
        is_international=True,
    )
    mission = await financial_service.create_mission(db, project.id, data)
    assert mission.requires_central_approval is False
    assert mission.ec_eligible is False


@pytest.mark.asyncio
async def test_create_mission_unit_costs_requires_wp(db: AsyncSession):
    """Test that unit costs missions require work_package_id."""
    project = await _create_project(db, CostModel.UNIT_COSTS)
    data = MissionCreate(
        researcher_name="Dr. Smith",
        purpose=MissionPurpose.FIELDWORK,
        destination="Berlin, Germany",
        start_date=date(2025, 9, 1),
        end_date=date(2025, 9, 3),
    )
    with pytest.raises(HTTPException) as exc_info:
        await financial_service.create_mission(db, project.id, data)
    assert exc_info.value.status_code == 422
    assert "work_package_id" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_approve_mission_pi(db: AsyncSession):
    """Test PI approval of a mission."""
    project = await _create_project(db, CostModel.ACTUAL_COSTS)
    mission = await financial_service.create_mission(
        db,
        project.id,
        MissionCreate(
            researcher_name="Dr. Smith",
            purpose=MissionPurpose.CONFERENCE,
            destination="Brussels, Belgium",
            start_date=date(2025, 9, 1),
            end_date=date(2025, 9, 3),
            total_cost=Decimal("650.00"),
        ),
    )
    approved = await financial_service.approve_mission(
        db, project.id, mission.id, MissionApprove()
    )
    assert approved.approval_status == ApprovalStatus.PI_APPROVED
    assert approved.approved_by_pi_at is not None


@pytest.mark.asyncio
async def test_approve_mission_central_chain(db: AsyncSession):
    """Test full approval chain: PI -> Central."""
    project = await _create_project(db, CostModel.ACTUAL_COSTS)
    mission = await financial_service.create_mission(
        db,
        project.id,
        MissionCreate(
            researcher_name="Dr. Smith",
            purpose=MissionPurpose.CONFERENCE,
            destination="New York, USA",
            start_date=date(2025, 9, 1),
            end_date=date(2025, 9, 5),
            total_cost=Decimal("6000.00"),
        ),
    )
    assert mission.requires_central_approval is True

    # PI approval
    mission = await financial_service.approve_mission(
        db, project.id, mission.id, MissionApprove()
    )
    assert mission.approval_status == ApprovalStatus.PI_APPROVED

    # Central approval
    mission = await financial_service.approve_mission(
        db, project.id, mission.id, MissionApprove()
    )
    assert mission.approval_status == ApprovalStatus.CENTRALLY_APPROVED
    assert mission.approved_centrally_at is not None


@pytest.mark.asyncio
async def test_approve_mission_invalid_transition(db: AsyncSession):
    """Test that approving a completed mission raises 409."""
    project = await _create_project(db, CostModel.ACTUAL_COSTS)
    mission = await financial_service.create_mission(
        db,
        project.id,
        MissionCreate(
            researcher_name="Dr. Smith",
            purpose=MissionPurpose.CONFERENCE,
            destination="Brussels, Belgium",
            start_date=date(2025, 9, 1),
            end_date=date(2025, 9, 3),
            total_cost=Decimal("650.00"),
        ),
    )
    # Approve then complete
    await financial_service.approve_mission(
        db, project.id, mission.id, MissionApprove()
    )
    await financial_service.complete_mission(
        db,
        project.id,
        mission.id,
        MissionComplete(
            actual_total_cost=Decimal("620.00"),
            actual_receipts={"receipt": "data"},
        ),
    )
    # Try to approve again
    with pytest.raises(HTTPException) as exc_info:
        await financial_service.approve_mission(
            db, project.id, mission.id, MissionApprove()
        )
    assert exc_info.value.status_code == 409


@pytest.mark.asyncio
async def test_complete_mission_with_actual_costs(db: AsyncSession):
    """Test completing a mission with actual cost data."""
    project = await _create_project(db, CostModel.ACTUAL_COSTS)
    mission = await financial_service.create_mission(
        db,
        project.id,
        MissionCreate(
            researcher_name="Dr. Smith",
            purpose=MissionPurpose.CONFERENCE,
            destination="Brussels, Belgium",
            start_date=date(2025, 9, 1),
            end_date=date(2025, 9, 3),
            total_cost=Decimal("650.00"),
        ),
    )
    await financial_service.approve_mission(
        db, project.id, mission.id, MissionApprove()
    )
    completed = await financial_service.complete_mission(
        db,
        project.id,
        mission.id,
        MissionComplete(
            actual_total_cost=Decimal("720.00"),
            actual_travel_costs=Decimal("400.00"),
            actual_accommodation_costs=Decimal("320.00"),
            actual_receipts={"flight": "receipt.pdf"},
        ),
    )
    assert completed.approval_status == ApprovalStatus.COMPLETED
    assert completed.actual_total_cost == Decimal("720.00")
    assert completed.completed_at is not None
    assert "over" in completed.reconciliation_notes


@pytest.mark.asyncio
async def test_complete_mission_reconciliation_under_budget(
    db: AsyncSession,
):
    """Test reconciliation notes when actual < estimated."""
    project = await _create_project(db, CostModel.ACTUAL_COSTS)
    mission = await financial_service.create_mission(
        db,
        project.id,
        MissionCreate(
            researcher_name="Dr. Smith",
            purpose=MissionPurpose.CONFERENCE,
            destination="Brussels, Belgium",
            start_date=date(2025, 9, 1),
            end_date=date(2025, 9, 3),
            total_cost=Decimal("1000.00"),
        ),
    )
    await financial_service.approve_mission(
        db, project.id, mission.id, MissionApprove()
    )
    completed = await financial_service.complete_mission(
        db,
        project.id,
        mission.id,
        MissionComplete(
            actual_total_cost=Decimal("800.00"),
            actual_receipts={"receipt": "data"},
        ),
    )
    assert "under" in completed.reconciliation_notes


@pytest.mark.asyncio
async def test_complete_mission_actual_costs_requires_receipts(
    db: AsyncSession,
):
    """Test that actual costs projects require receipts on completion."""
    project = await _create_project(db, CostModel.ACTUAL_COSTS)
    mission = await financial_service.create_mission(
        db,
        project.id,
        MissionCreate(
            researcher_name="Dr. Smith",
            purpose=MissionPurpose.CONFERENCE,
            destination="Brussels, Belgium",
            start_date=date(2025, 9, 1),
            end_date=date(2025, 9, 3),
            total_cost=Decimal("650.00"),
        ),
    )
    await financial_service.approve_mission(
        db, project.id, mission.id, MissionApprove()
    )
    with pytest.raises(HTTPException) as exc_info:
        await financial_service.complete_mission(
            db,
            project.id,
            mission.id,
            MissionComplete(actual_total_cost=Decimal("620.00")),
        )
    assert exc_info.value.status_code == 422
    assert "actual_receipts" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_complete_mission_lump_sum_no_receipts_needed(
    db: AsyncSession,
):
    """Test that lump sum missions don't require receipts."""
    project = await _create_project(db, CostModel.LUMP_SUM)
    mission = await financial_service.create_mission(
        db,
        project.id,
        MissionCreate(
            researcher_name="Dr. Jones",
            purpose=MissionPurpose.CONFERENCE,
            destination="Lisbon, Portugal",
            start_date=date(2025, 10, 1),
            end_date=date(2025, 10, 2),
            total_cost=Decimal("400.00"),
        ),
    )
    await financial_service.approve_mission(
        db, project.id, mission.id, MissionApprove()
    )
    completed = await financial_service.complete_mission(
        db,
        project.id,
        mission.id,
        MissionComplete(actual_total_cost=Decimal("380.00")),
    )
    assert completed.approval_status == ApprovalStatus.COMPLETED


@pytest.mark.asyncio
async def test_cancel_mission(db: AsyncSession):
    """Test canceling a mission."""
    project = await _create_project(db, CostModel.ACTUAL_COSTS)
    mission = await financial_service.create_mission(
        db,
        project.id,
        MissionCreate(
            researcher_name="Dr. Smith",
            purpose=MissionPurpose.CONFERENCE,
            destination="Brussels, Belgium",
            start_date=date(2025, 9, 1),
            end_date=date(2025, 9, 3),
        ),
    )
    cancelled = await financial_service.cancel_mission(
        db, project.id, mission.id
    )
    assert cancelled.approval_status == ApprovalStatus.CANCELLED


@pytest.mark.asyncio
async def test_cancel_completed_mission_fails(db: AsyncSession):
    """Test that canceling a completed mission raises 409."""
    project = await _create_project(db, CostModel.ACTUAL_COSTS)
    mission = await financial_service.create_mission(
        db,
        project.id,
        MissionCreate(
            researcher_name="Dr. Smith",
            purpose=MissionPurpose.CONFERENCE,
            destination="Brussels, Belgium",
            start_date=date(2025, 9, 1),
            end_date=date(2025, 9, 3),
            total_cost=Decimal("650.00"),
        ),
    )
    await financial_service.approve_mission(
        db, project.id, mission.id, MissionApprove()
    )
    await financial_service.complete_mission(
        db,
        project.id,
        mission.id,
        MissionComplete(
            actual_total_cost=Decimal("650.00"),
            actual_receipts={"receipt": "data"},
        ),
    )
    with pytest.raises(HTTPException) as exc_info:
        await financial_service.cancel_mission(
            db, project.id, mission.id
        )
    assert exc_info.value.status_code == 409


# --- Procurement Tests ---


@pytest.mark.asyncio
async def test_create_procurement(db: AsyncSession):
    """Test creating a procurement."""
    project = await _create_project(db)
    data = ProcurementCreate(
        ec_category=ECBudgetCategory.C2_EQUIPMENT,
        description="Lab spectrometer",
        estimated_cost=Decimal("25000.00"),
        procurement_method=ProcurementMethod.THREE_QUOTES,
    )
    procurement = await financial_service.create_procurement(
        db, project.id, data
    )
    assert procurement.id is not None
    assert procurement.ec_category == ECBudgetCategory.C2_EQUIPMENT
    assert (
        procurement.approval_status
        == ProcurementApprovalStatus.REQUESTED
    )


@pytest.mark.asyncio
async def test_list_procurements(db: AsyncSession):
    """Test listing procurements."""
    project = await _create_project(db)
    await financial_service.create_procurement(
        db,
        project.id,
        ProcurementCreate(
            description="Item 1",
            estimated_cost=Decimal("100.00"),
        ),
    )
    await financial_service.create_procurement(
        db,
        project.id,
        ProcurementCreate(
            description="Item 2",
            estimated_cost=Decimal("200.00"),
        ),
    )
    items, total = await financial_service.list_procurements(
        db, project.id
    )
    assert total == 2


@pytest.mark.asyncio
async def test_delete_procurement(db: AsyncSession):
    """Test soft-deleting a procurement."""
    project = await _create_project(db)
    procurement = await financial_service.create_procurement(
        db,
        project.id,
        ProcurementCreate(description="To delete"),
    )
    assert (
        await financial_service.delete_procurement(
            db, project.id, procurement.id
        )
        is True
    )
    assert (
        await financial_service.get_procurement(db, procurement.id)
        is None
    )


# --- Fund Distribution Tests ---


@pytest.mark.asyncio
async def test_create_fund_distribution(db: AsyncSession):
    """Test creating a fund distribution."""
    project = await _create_project(db)
    data = FundDistributionCreate(
        distribution_type="pre_financing",
        amount=Decimal("100000.00"),
        distribution_date=date(2025, 1, 15),
        bank_transfer_reference="BT-2025-001",
    )
    distribution = await financial_service.create_fund_distribution(
        db, project.id, data
    )
    assert distribution.id is not None
    assert distribution.distribution_type == "pre_financing"
    assert distribution.amount == Decimal("100000.00")


@pytest.mark.asyncio
async def test_list_fund_distributions(db: AsyncSession):
    """Test listing fund distributions."""
    project = await _create_project(db)
    await financial_service.create_fund_distribution(
        db,
        project.id,
        FundDistributionCreate(
            distribution_type="pre_financing",
            amount=Decimal("50000.00"),
            distribution_date=date(2025, 1, 1),
        ),
    )
    await financial_service.create_fund_distribution(
        db,
        project.id,
        FundDistributionCreate(
            distribution_type="distribution",
            amount=Decimal("20000.00"),
            distribution_date=date(2025, 3, 1),
        ),
    )
    items, total = await financial_service.list_fund_distributions(
        db, project.id
    )
    assert total == 2


@pytest.mark.asyncio
async def test_delete_fund_distribution(db: AsyncSession):
    """Test deleting a fund distribution (hard delete)."""
    project = await _create_project(db)
    distribution = await financial_service.create_fund_distribution(
        db,
        project.id,
        FundDistributionCreate(
            distribution_type="retention",
            amount=Decimal("5000.00"),
            distribution_date=date(2025, 6, 1),
        ),
    )
    assert (
        await financial_service.delete_fund_distribution(
            db, project.id, distribution.id
        )
        is True
    )
    items, total = await financial_service.list_fund_distributions(
        db, project.id
    )
    assert total == 0
