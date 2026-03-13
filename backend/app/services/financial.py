"""Service layer for financial entities (Section 4).

Includes cost-model-aware validation: for ACTUAL_COSTS projects,
ec_eligible is enforced and supporting_docs are required.
For LUMP_SUM projects, ec_eligible defaults to false and
supporting_docs are optional for EC purposes.
"""

import uuid
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from decimal import Decimal

from app.models.enums import ApprovalStatus, CostModel, ExpenseStatus
from app.models.financial import (
    BudgetCategoryMapping,
    Expense,
    FundDistribution,
    Mission,
    Procurement,
)
from app.models.project import Project
from app.schemas.financial import (
    BudgetCategoryMappingCreate,
    BudgetCategoryMappingUpdate,
    ExpenseCreate,
    ExpenseUpdate,
    FundDistributionCreate,
    FundDistributionUpdate,
    MissionApprove,
    MissionComplete,
    MissionCreate,
    MissionUpdate,
    ProcurementCreate,
    ProcurementUpdate,
)


# --- Helpers ---


async def _get_project_cost_model(
    db: AsyncSession, project_id: uuid.UUID
) -> CostModel:
    """Fetch the cost model for a project. Raises 404 if not found."""
    stmt = select(Project.cost_model).where(
        Project.id == project_id, Project.deleted_at.is_(None)
    )
    result = await db.execute(stmt)
    cost_model = result.scalar_one_or_none()
    if cost_model is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return cost_model


def _apply_cost_model_rules_expense(
    data: ExpenseCreate, cost_model: CostModel
) -> ExpenseCreate:
    """Apply cost-model-aware validation rules to an expense.

    For ACTUAL_COSTS: ec_eligible is enforced, ec_category required,
    supporting_docs required when submitting.
    For LUMP_SUM: ec_eligible defaults to false, supporting_docs optional
    for EC purposes.
    """
    if cost_model == CostModel.LUMP_SUM:
        data = data.model_copy(
            update={"ec_eligible": False}
        )
    elif cost_model == CostModel.ACTUAL_COSTS:
        if data.ec_category is None:
            raise HTTPException(
                status_code=422,
                detail=(
                    "ec_category is required for actual costs projects"
                ),
            )
        if (
            data.status != ExpenseStatus.DRAFT
            and not data.supporting_docs
        ):
            raise HTTPException(
                status_code=422,
                detail=(
                    "supporting_docs are required for non-draft expenses "
                    "in actual costs projects"
                ),
            )
    return data


# Mission workflow constants
CENTRAL_APPROVAL_THRESHOLD = Decimal("5000.00")
EU_COUNTRY_NAMES = {
    "austria", "belgium", "bulgaria", "croatia", "cyprus", "czechia",
    "czech republic", "denmark", "estonia", "finland", "france",
    "germany", "greece", "hungary", "ireland", "italy", "latvia",
    "lithuania", "luxembourg", "malta", "netherlands", "poland",
    "portugal", "romania", "slovakia", "slovenia", "spain", "sweden",
}

# Valid mission status transitions
_MISSION_TRANSITIONS: dict[ApprovalStatus, set[ApprovalStatus]] = {
    ApprovalStatus.REQUESTED: {
        ApprovalStatus.PI_APPROVED,
        ApprovalStatus.CANCELLED,
    },
    ApprovalStatus.PI_APPROVED: {
        ApprovalStatus.CENTRALLY_APPROVED,
        ApprovalStatus.COMPLETED,
        ApprovalStatus.CANCELLED,
    },
    ApprovalStatus.CENTRALLY_APPROVED: {
        ApprovalStatus.COMPLETED,
        ApprovalStatus.CANCELLED,
    },
    ApprovalStatus.COMPLETED: set(),
    ApprovalStatus.CANCELLED: set(),
}


def _validate_mission_status_transition(
    current: ApprovalStatus, target: ApprovalStatus
) -> None:
    """Validate that a mission status transition is allowed."""
    allowed = _MISSION_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Cannot transition from {current.value} to "
                f"{target.value}"
            ),
        )


def _check_requires_central_approval(
    data: MissionCreate, cost_model: CostModel
) -> tuple[bool, bool]:
    """Determine if a mission requires central approval.

    Returns (requires_central, is_international).
    """
    if cost_model == CostModel.LUMP_SUM:
        return False, data.is_international

    # Check if destination is international (not in EU)
    is_international = data.is_international
    if not is_international:
        dest_lower = data.destination.lower()
        is_international = not any(
            country in dest_lower for country in EU_COUNTRY_NAMES
        )

    requires_central = is_international

    # Also require central approval for above-threshold costs
    if (
        data.total_cost is not None
        and data.total_cost >= CENTRAL_APPROVAL_THRESHOLD
    ):
        requires_central = True

    return requires_central, is_international


def _apply_cost_model_rules_mission(
    data: MissionCreate, cost_model: CostModel
) -> MissionCreate:
    """Apply cost-model-aware validation rules to a mission.

    For LUMP_SUM: ec_eligible defaults to false.
    For ACTUAL_COSTS: ec_eligible remains true (full documentation needed).
    For UNIT_COSTS: work_package_id is required.
    """
    if cost_model == CostModel.LUMP_SUM:
        data = data.model_copy(update={"ec_eligible": False})
    elif cost_model == CostModel.UNIT_COSTS:
        if data.work_package_id is None:
            raise HTTPException(
                status_code=422,
                detail=(
                    "work_package_id is required for unit costs "
                    "projects"
                ),
            )
    return data


# --- Budget Category Mapping (Section 4.1) ---


async def create_budget_mapping(
    db: AsyncSession,
    project_id: uuid.UUID,
    data: BudgetCategoryMappingCreate,
) -> BudgetCategoryMapping:
    """Create a budget category mapping for a project."""
    mapping = BudgetCategoryMapping(
        project_id=project_id, **data.model_dump()
    )
    db.add(mapping)
    await db.flush()
    await db.refresh(mapping)
    return mapping


async def list_budget_mappings(
    db: AsyncSession, project_id: uuid.UUID
) -> tuple[list[BudgetCategoryMapping], int]:
    """List all budget category mappings for a project."""
    stmt = (
        select(BudgetCategoryMapping)
        .where(BudgetCategoryMapping.project_id == project_id)
        .order_by(BudgetCategoryMapping.ec_category)
    )
    count_stmt = select(func.count(BudgetCategoryMapping.id)).where(
        BudgetCategoryMapping.project_id == project_id
    )
    result = await db.execute(stmt)
    items = list(result.scalars().all())
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()
    return items, total


async def update_budget_mapping(
    db: AsyncSession,
    mapping_id: uuid.UUID,
    data: BudgetCategoryMappingUpdate,
) -> BudgetCategoryMapping | None:
    """Update a budget category mapping."""
    stmt = select(BudgetCategoryMapping).where(
        BudgetCategoryMapping.id == mapping_id
    )
    result = await db.execute(stmt)
    mapping = result.scalar_one_or_none()
    if mapping is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(mapping, field, value)
    await db.flush()
    await db.refresh(mapping)
    return mapping


async def delete_budget_mapping(
    db: AsyncSession, mapping_id: uuid.UUID
) -> bool:
    """Delete a budget category mapping (hard delete)."""
    stmt = select(BudgetCategoryMapping).where(
        BudgetCategoryMapping.id == mapping_id
    )
    result = await db.execute(stmt)
    mapping = result.scalar_one_or_none()
    if mapping is None:
        return False
    await db.delete(mapping)
    await db.flush()
    return True


# --- Expense (Section 4.2) ---


async def create_expense(
    db: AsyncSession,
    project_id: uuid.UUID,
    data: ExpenseCreate,
) -> Expense:
    """Create an expense with cost-model-aware validation."""
    cost_model = await _get_project_cost_model(db, project_id)
    data = _apply_cost_model_rules_expense(data, cost_model)

    expense = Expense(project_id=project_id, **data.model_dump())
    db.add(expense)
    await db.flush()
    await db.refresh(expense)
    return expense


async def get_expense(
    db: AsyncSession, expense_id: uuid.UUID
) -> Expense | None:
    """Get a single expense by ID, excluding soft-deleted."""
    stmt = select(Expense).where(
        Expense.id == expense_id, Expense.deleted_at.is_(None)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_expenses(
    db: AsyncSession,
    project_id: uuid.UUID,
    *,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[Expense], int]:
    """List expenses for a project."""
    base = (
        Expense.project_id == project_id,
        Expense.deleted_at.is_(None),
    )
    stmt = (
        select(Expense)
        .where(*base)
        .order_by(Expense.date_incurred.desc())
        .offset(skip)
        .limit(limit)
    )
    count_stmt = select(func.count(Expense.id)).where(*base)
    result = await db.execute(stmt)
    items = list(result.scalars().all())
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()
    return items, total


async def update_expense(
    db: AsyncSession,
    project_id: uuid.UUID,
    expense_id: uuid.UUID,
    data: ExpenseUpdate,
) -> Expense | None:
    """Update an expense."""
    expense = await get_expense(db, expense_id)
    if expense is None or expense.project_id != project_id:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(expense, field, value)
    await db.flush()
    await db.refresh(expense)
    return expense


async def delete_expense(
    db: AsyncSession, project_id: uuid.UUID, expense_id: uuid.UUID
) -> bool:
    """Soft-delete an expense."""
    expense = await get_expense(db, expense_id)
    if expense is None or expense.project_id != project_id:
        return False
    expense.deleted_at = datetime.now(timezone.utc)
    await db.flush()
    return True


# --- Mission (Section 4.5) ---


async def create_mission(
    db: AsyncSession,
    project_id: uuid.UUID,
    data: MissionCreate,
) -> Mission:
    """Create a mission with cost-model-aware validation."""
    cost_model = await _get_project_cost_model(db, project_id)
    data = _apply_cost_model_rules_mission(data, cost_model)

    # Force initial status and compute workflow flags
    data = data.model_copy(
        update={"approval_status": ApprovalStatus.REQUESTED}
    )
    requires_central, is_international = _check_requires_central_approval(
        data, cost_model
    )

    dump = data.model_dump()
    dump["estimated_total_cost"] = dump.get("total_cost")
    dump["is_international"] = is_international
    dump["requires_central_approval"] = requires_central

    mission = Mission(project_id=project_id, **dump)
    db.add(mission)
    await db.flush()
    await db.refresh(mission)
    return mission


async def get_mission(
    db: AsyncSession, mission_id: uuid.UUID
) -> Mission | None:
    """Get a single mission by ID, excluding soft-deleted."""
    stmt = select(Mission).where(
        Mission.id == mission_id, Mission.deleted_at.is_(None)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_missions(
    db: AsyncSession,
    project_id: uuid.UUID,
    *,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[Mission], int]:
    """List missions for a project."""
    base = (
        Mission.project_id == project_id,
        Mission.deleted_at.is_(None),
    )
    stmt = (
        select(Mission)
        .where(*base)
        .order_by(Mission.start_date.desc())
        .offset(skip)
        .limit(limit)
    )
    count_stmt = select(func.count(Mission.id)).where(*base)
    result = await db.execute(stmt)
    items = list(result.scalars().all())
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()
    return items, total


async def update_mission(
    db: AsyncSession,
    project_id: uuid.UUID,
    mission_id: uuid.UUID,
    data: MissionUpdate,
) -> Mission | None:
    """Update a mission."""
    mission = await get_mission(db, mission_id)
    if mission is None or mission.project_id != project_id:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(mission, field, value)
    await db.flush()
    await db.refresh(mission)
    return mission


async def delete_mission(
    db: AsyncSession, project_id: uuid.UUID, mission_id: uuid.UUID
) -> bool:
    """Soft-delete a mission."""
    mission = await get_mission(db, mission_id)
    if mission is None or mission.project_id != project_id:
        return False
    mission.deleted_at = datetime.now(timezone.utc)
    await db.flush()
    return True


async def approve_mission(
    db: AsyncSession,
    project_id: uuid.UUID,
    mission_id: uuid.UUID,
    data: MissionApprove,
) -> Mission:
    """Advance a mission through the approval chain.

    REQUESTED -> PI_APPROVED (first call)
    PI_APPROVED -> CENTRALLY_APPROVED (second call, if central needed)
    """
    mission = await get_mission(db, mission_id)
    if mission is None or mission.project_id != project_id:
        raise HTTPException(
            status_code=404, detail="Mission not found"
        )

    now = datetime.now(timezone.utc)

    if mission.approval_status == ApprovalStatus.REQUESTED:
        _validate_mission_status_transition(
            mission.approval_status, ApprovalStatus.PI_APPROVED
        )
        mission.approval_status = ApprovalStatus.PI_APPROVED
        mission.approved_by_pi_at = now
    elif mission.approval_status == ApprovalStatus.PI_APPROVED:
        if mission.requires_central_approval:
            _validate_mission_status_transition(
                mission.approval_status,
                ApprovalStatus.CENTRALLY_APPROVED,
            )
            mission.approval_status = ApprovalStatus.CENTRALLY_APPROVED
            mission.approved_centrally_at = now
        else:
            raise HTTPException(
                status_code=409,
                detail=(
                    "Mission is already PI-approved and does not "
                    "require central approval. Use the complete "
                    "endpoint to finalize."
                ),
            )
    else:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Cannot approve mission in "
                f"{mission.approval_status.value} status"
            ),
        )

    await db.flush()
    await db.refresh(mission)
    return mission


async def complete_mission(
    db: AsyncSession,
    project_id: uuid.UUID,
    mission_id: uuid.UUID,
    data: MissionComplete,
) -> Mission:
    """Complete a mission by submitting actual receipts.

    Validates that the mission is in an approved state, enforces
    cost-model-aware rules, and reconciles estimated vs actual costs.
    """
    mission = await get_mission(db, mission_id)
    if mission is None or mission.project_id != project_id:
        raise HTTPException(
            status_code=404, detail="Mission not found"
        )

    # Determine valid pre-completion statuses
    if mission.requires_central_approval:
        if mission.approval_status != ApprovalStatus.CENTRALLY_APPROVED:
            raise HTTPException(
                status_code=409,
                detail=(
                    "Mission requires central approval before "
                    "completion"
                ),
            )
    else:
        if mission.approval_status not in (
            ApprovalStatus.PI_APPROVED,
            ApprovalStatus.CENTRALLY_APPROVED,
        ):
            raise HTTPException(
                status_code=409,
                detail="Mission must be approved before completion",
            )

    # Cost-model-aware completion rules
    cost_model = await _get_project_cost_model(db, project_id)
    if cost_model == CostModel.ACTUAL_COSTS:
        if not data.actual_receipts:
            raise HTTPException(
                status_code=422,
                detail=(
                    "actual_receipts are required for actual costs "
                    "projects"
                ),
            )

    # Update actual cost fields
    mission.actual_total_cost = data.actual_total_cost
    mission.actual_receipts = data.actual_receipts
    if data.actual_travel_costs is not None:
        mission.travel_costs = data.actual_travel_costs
    if data.actual_accommodation_costs is not None:
        mission.accommodation_costs = data.actual_accommodation_costs
    if data.actual_subsistence is not None:
        mission.subsistence = data.actual_subsistence
    if data.actual_registration_fees is not None:
        mission.registration_fees = data.actual_registration_fees
    if data.actual_other_costs is not None:
        mission.other_costs = data.actual_other_costs
    if data.university_travel_order is not None:
        mission.university_travel_order = data.university_travel_order

    # Update total_cost to actual for budget monitoring
    mission.total_cost = data.actual_total_cost

    # Reconciliation
    estimated = mission.estimated_total_cost
    actual = data.actual_total_cost
    if estimated and estimated > 0:
        variance = actual - estimated
        pct = (variance / estimated * 100).quantize(
            Decimal("0.01")
        )
        direction = "over" if variance > 0 else "under"
        mission.reconciliation_notes = (
            f"Actual {direction} estimate by "
            f"{abs(variance):.2f} EUR ({abs(pct):.1f}%)"
        )
    else:
        mission.reconciliation_notes = (
            f"Actual total: {actual:.2f} EUR (no estimate provided)"
        )

    mission.approval_status = ApprovalStatus.COMPLETED
    mission.completed_at = datetime.now(timezone.utc)

    await db.flush()
    await db.refresh(mission)
    return mission


async def cancel_mission(
    db: AsyncSession,
    project_id: uuid.UUID,
    mission_id: uuid.UUID,
) -> Mission:
    """Cancel a mission."""
    mission = await get_mission(db, mission_id)
    if mission is None or mission.project_id != project_id:
        raise HTTPException(
            status_code=404, detail="Mission not found"
        )

    _validate_mission_status_transition(
        mission.approval_status, ApprovalStatus.CANCELLED
    )
    mission.approval_status = ApprovalStatus.CANCELLED
    await db.flush()
    await db.refresh(mission)
    return mission


# --- Procurement (Section 4.6) ---


async def create_procurement(
    db: AsyncSession,
    project_id: uuid.UUID,
    data: ProcurementCreate,
) -> Procurement:
    """Create a procurement record."""
    await _get_project_cost_model(db, project_id)  # verify project exists
    procurement = Procurement(project_id=project_id, **data.model_dump())
    db.add(procurement)
    await db.flush()
    await db.refresh(procurement)
    return procurement


async def get_procurement(
    db: AsyncSession, procurement_id: uuid.UUID
) -> Procurement | None:
    """Get a single procurement by ID, excluding soft-deleted."""
    stmt = select(Procurement).where(
        Procurement.id == procurement_id,
        Procurement.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_procurements(
    db: AsyncSession,
    project_id: uuid.UUID,
    *,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[Procurement], int]:
    """List procurements for a project."""
    base = (
        Procurement.project_id == project_id,
        Procurement.deleted_at.is_(None),
    )
    stmt = (
        select(Procurement)
        .where(*base)
        .order_by(Procurement.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    count_stmt = select(func.count(Procurement.id)).where(*base)
    result = await db.execute(stmt)
    items = list(result.scalars().all())
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()
    return items, total


async def update_procurement(
    db: AsyncSession,
    project_id: uuid.UUID,
    procurement_id: uuid.UUID,
    data: ProcurementUpdate,
) -> Procurement | None:
    """Update a procurement."""
    procurement = await get_procurement(db, procurement_id)
    if procurement is None or procurement.project_id != project_id:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(procurement, field, value)
    await db.flush()
    await db.refresh(procurement)
    return procurement


async def delete_procurement(
    db: AsyncSession,
    project_id: uuid.UUID,
    procurement_id: uuid.UUID,
) -> bool:
    """Soft-delete a procurement."""
    procurement = await get_procurement(db, procurement_id)
    if procurement is None or procurement.project_id != project_id:
        return False
    procurement.deleted_at = datetime.now(timezone.utc)
    await db.flush()
    return True


# --- Fund Distribution (Section 4.4) ---


async def create_fund_distribution(
    db: AsyncSession,
    project_id: uuid.UUID,
    data: FundDistributionCreate,
) -> FundDistribution:
    """Create a fund distribution record."""
    await _get_project_cost_model(db, project_id)  # verify project exists
    distribution = FundDistribution(
        project_id=project_id, **data.model_dump()
    )
    db.add(distribution)
    await db.flush()
    await db.refresh(distribution)
    return distribution


async def list_fund_distributions(
    db: AsyncSession,
    project_id: uuid.UUID,
) -> tuple[list[FundDistribution], int]:
    """List fund distributions for a project."""
    stmt = (
        select(FundDistribution)
        .where(FundDistribution.project_id == project_id)
        .order_by(FundDistribution.distribution_date.desc())
    )
    count_stmt = select(func.count(FundDistribution.id)).where(
        FundDistribution.project_id == project_id
    )
    result = await db.execute(stmt)
    items = list(result.scalars().all())
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()
    return items, total


async def update_fund_distribution(
    db: AsyncSession,
    project_id: uuid.UUID,
    distribution_id: uuid.UUID,
    data: FundDistributionUpdate,
) -> FundDistribution | None:
    """Update a fund distribution record."""
    stmt = select(FundDistribution).where(
        FundDistribution.id == distribution_id,
        FundDistribution.project_id == project_id,
    )
    result = await db.execute(stmt)
    distribution = result.scalar_one_or_none()
    if distribution is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(distribution, field, value)
    await db.flush()
    await db.refresh(distribution)
    return distribution


async def delete_fund_distribution(
    db: AsyncSession,
    project_id: uuid.UUID,
    distribution_id: uuid.UUID,
) -> bool:
    """Delete a fund distribution record (hard delete)."""
    stmt = select(FundDistribution).where(
        FundDistribution.id == distribution_id,
        FundDistribution.project_id == project_id,
    )
    result = await db.execute(stmt)
    distribution = result.scalar_one_or_none()
    if distribution is None:
        return False
    await db.delete(distribution)
    await db.flush()
    return True
