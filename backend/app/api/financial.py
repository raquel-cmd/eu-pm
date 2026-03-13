"""API routes for financial entities (Section 4).

All routes are nested under /api/projects/{project_id}/.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.financial import (
    BudgetCategoryMappingCreate,
    BudgetCategoryMappingListResponse,
    BudgetCategoryMappingResponse,
    BudgetCategoryMappingUpdate,
    ExpenseCreate,
    ExpenseListResponse,
    ExpenseResponse,
    ExpenseUpdate,
    FundDistributionCreate,
    FundDistributionListResponse,
    FundDistributionResponse,
    FundDistributionUpdate,
    MissionApprove,
    MissionComplete,
    MissionCreate,
    MissionListResponse,
    MissionResponse,
    MissionUpdate,
    ProcurementCreate,
    ProcurementListResponse,
    ProcurementResponse,
    ProcurementUpdate,
)
from app.services import financial as financial_service

router = APIRouter(prefix="/api/projects/{project_id}", tags=["financial"])


# --- Budget Category Mappings ---


@router.post(
    "/budget-mappings",
    response_model=BudgetCategoryMappingResponse,
    status_code=201,
)
async def create_budget_mapping(
    project_id: uuid.UUID,
    data: BudgetCategoryMappingCreate,
    db: AsyncSession = Depends(get_db),
) -> BudgetCategoryMappingResponse:
    """Create a budget category mapping for a project."""
    mapping = await financial_service.create_budget_mapping(
        db, project_id, data
    )
    return BudgetCategoryMappingResponse.model_validate(mapping)


@router.get(
    "/budget-mappings",
    response_model=BudgetCategoryMappingListResponse,
)
async def list_budget_mappings(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> BudgetCategoryMappingListResponse:
    """List budget category mappings for a project."""
    items, total = await financial_service.list_budget_mappings(
        db, project_id
    )
    return BudgetCategoryMappingListResponse(
        items=[
            BudgetCategoryMappingResponse.model_validate(m) for m in items
        ],
        total=total,
    )


@router.put(
    "/budget-mappings/{mapping_id}",
    response_model=BudgetCategoryMappingResponse,
)
async def update_budget_mapping(
    project_id: uuid.UUID,
    mapping_id: uuid.UUID,
    data: BudgetCategoryMappingUpdate,
    db: AsyncSession = Depends(get_db),
) -> BudgetCategoryMappingResponse:
    """Update a budget category mapping."""
    mapping = await financial_service.update_budget_mapping(
        db, mapping_id, data
    )
    if mapping is None:
        raise HTTPException(status_code=404, detail="Mapping not found")
    return BudgetCategoryMappingResponse.model_validate(mapping)


@router.delete("/budget-mappings/{mapping_id}", status_code=204)
async def delete_budget_mapping(
    project_id: uuid.UUID,
    mapping_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a budget category mapping."""
    deleted = await financial_service.delete_budget_mapping(db, mapping_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Mapping not found")


# --- Expenses ---


@router.post(
    "/expenses", response_model=ExpenseResponse, status_code=201
)
async def create_expense(
    project_id: uuid.UUID,
    data: ExpenseCreate,
    db: AsyncSession = Depends(get_db),
) -> ExpenseResponse:
    """Create an expense with cost-model-aware validation."""
    expense = await financial_service.create_expense(db, project_id, data)
    return ExpenseResponse.model_validate(expense)


@router.get("/expenses", response_model=ExpenseListResponse)
async def list_expenses(
    project_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> ExpenseListResponse:
    """List expenses for a project."""
    items, total = await financial_service.list_expenses(
        db, project_id, skip=skip, limit=limit
    )
    return ExpenseListResponse(
        items=[ExpenseResponse.model_validate(e) for e in items],
        total=total,
    )


@router.get(
    "/expenses/{expense_id}", response_model=ExpenseResponse
)
async def get_expense(
    project_id: uuid.UUID,
    expense_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ExpenseResponse:
    """Get a single expense."""
    expense = await financial_service.get_expense(db, expense_id)
    if expense is None or expense.project_id != project_id:
        raise HTTPException(status_code=404, detail="Expense not found")
    return ExpenseResponse.model_validate(expense)


@router.put(
    "/expenses/{expense_id}", response_model=ExpenseResponse
)
async def update_expense(
    project_id: uuid.UUID,
    expense_id: uuid.UUID,
    data: ExpenseUpdate,
    db: AsyncSession = Depends(get_db),
) -> ExpenseResponse:
    """Update an expense."""
    expense = await financial_service.update_expense(
        db, project_id, expense_id, data
    )
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return ExpenseResponse.model_validate(expense)


@router.delete("/expenses/{expense_id}", status_code=204)
async def delete_expense(
    project_id: uuid.UUID,
    expense_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Soft-delete an expense."""
    deleted = await financial_service.delete_expense(
        db, project_id, expense_id
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Expense not found")


# --- Missions ---


@router.post(
    "/missions", response_model=MissionResponse, status_code=201
)
async def create_mission(
    project_id: uuid.UUID,
    data: MissionCreate,
    db: AsyncSession = Depends(get_db),
) -> MissionResponse:
    """Create a mission with cost-model-aware validation."""
    mission = await financial_service.create_mission(db, project_id, data)
    return MissionResponse.model_validate(mission)


@router.get("/missions", response_model=MissionListResponse)
async def list_missions(
    project_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> MissionListResponse:
    """List missions for a project."""
    items, total = await financial_service.list_missions(
        db, project_id, skip=skip, limit=limit
    )
    return MissionListResponse(
        items=[MissionResponse.model_validate(m) for m in items],
        total=total,
    )


@router.get(
    "/missions/{mission_id}", response_model=MissionResponse
)
async def get_mission(
    project_id: uuid.UUID,
    mission_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> MissionResponse:
    """Get a single mission."""
    mission = await financial_service.get_mission(db, mission_id)
    if mission is None or mission.project_id != project_id:
        raise HTTPException(status_code=404, detail="Mission not found")
    return MissionResponse.model_validate(mission)


@router.put(
    "/missions/{mission_id}", response_model=MissionResponse
)
async def update_mission(
    project_id: uuid.UUID,
    mission_id: uuid.UUID,
    data: MissionUpdate,
    db: AsyncSession = Depends(get_db),
) -> MissionResponse:
    """Update a mission."""
    mission = await financial_service.update_mission(
        db, project_id, mission_id, data
    )
    if mission is None:
        raise HTTPException(status_code=404, detail="Mission not found")
    return MissionResponse.model_validate(mission)


@router.put(
    "/missions/{mission_id}/approve", response_model=MissionResponse
)
async def approve_mission(
    project_id: uuid.UUID,
    mission_id: uuid.UUID,
    data: MissionApprove,
    db: AsyncSession = Depends(get_db),
) -> MissionResponse:
    """Approve a mission (advances through approval chain)."""
    mission = await financial_service.approve_mission(
        db, project_id, mission_id, data
    )
    return MissionResponse.model_validate(mission)


@router.put(
    "/missions/{mission_id}/complete", response_model=MissionResponse
)
async def complete_mission(
    project_id: uuid.UUID,
    mission_id: uuid.UUID,
    data: MissionComplete,
    db: AsyncSession = Depends(get_db),
) -> MissionResponse:
    """Complete a mission with actual receipts."""
    mission = await financial_service.complete_mission(
        db, project_id, mission_id, data
    )
    return MissionResponse.model_validate(mission)


@router.put(
    "/missions/{mission_id}/cancel", response_model=MissionResponse
)
async def cancel_mission(
    project_id: uuid.UUID,
    mission_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> MissionResponse:
    """Cancel a mission."""
    mission = await financial_service.cancel_mission(
        db, project_id, mission_id
    )
    return MissionResponse.model_validate(mission)


@router.delete("/missions/{mission_id}", status_code=204)
async def delete_mission(
    project_id: uuid.UUID,
    mission_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Soft-delete a mission."""
    deleted = await financial_service.delete_mission(
        db, project_id, mission_id
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Mission not found")


# --- Procurements ---


@router.post(
    "/procurements",
    response_model=ProcurementResponse,
    status_code=201,
)
async def create_procurement(
    project_id: uuid.UUID,
    data: ProcurementCreate,
    db: AsyncSession = Depends(get_db),
) -> ProcurementResponse:
    """Create a procurement record."""
    procurement = await financial_service.create_procurement(
        db, project_id, data
    )
    return ProcurementResponse.model_validate(procurement)


@router.get(
    "/procurements", response_model=ProcurementListResponse
)
async def list_procurements(
    project_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> ProcurementListResponse:
    """List procurements for a project."""
    items, total = await financial_service.list_procurements(
        db, project_id, skip=skip, limit=limit
    )
    return ProcurementListResponse(
        items=[ProcurementResponse.model_validate(p) for p in items],
        total=total,
    )


@router.get(
    "/procurements/{procurement_id}",
    response_model=ProcurementResponse,
)
async def get_procurement(
    project_id: uuid.UUID,
    procurement_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ProcurementResponse:
    """Get a single procurement."""
    procurement = await financial_service.get_procurement(
        db, procurement_id
    )
    if procurement is None or procurement.project_id != project_id:
        raise HTTPException(
            status_code=404, detail="Procurement not found"
        )
    return ProcurementResponse.model_validate(procurement)


@router.put(
    "/procurements/{procurement_id}",
    response_model=ProcurementResponse,
)
async def update_procurement(
    project_id: uuid.UUID,
    procurement_id: uuid.UUID,
    data: ProcurementUpdate,
    db: AsyncSession = Depends(get_db),
) -> ProcurementResponse:
    """Update a procurement."""
    procurement = await financial_service.update_procurement(
        db, project_id, procurement_id, data
    )
    if procurement is None:
        raise HTTPException(
            status_code=404, detail="Procurement not found"
        )
    return ProcurementResponse.model_validate(procurement)


@router.delete("/procurements/{procurement_id}", status_code=204)
async def delete_procurement(
    project_id: uuid.UUID,
    procurement_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Soft-delete a procurement."""
    deleted = await financial_service.delete_procurement(
        db, project_id, procurement_id
    )
    if not deleted:
        raise HTTPException(
            status_code=404, detail="Procurement not found"
        )


# --- Fund Distributions ---


@router.post(
    "/fund-distributions",
    response_model=FundDistributionResponse,
    status_code=201,
)
async def create_fund_distribution(
    project_id: uuid.UUID,
    data: FundDistributionCreate,
    db: AsyncSession = Depends(get_db),
) -> FundDistributionResponse:
    """Create a fund distribution record."""
    distribution = await financial_service.create_fund_distribution(
        db, project_id, data
    )
    return FundDistributionResponse.model_validate(distribution)


@router.get(
    "/fund-distributions",
    response_model=FundDistributionListResponse,
)
async def list_fund_distributions(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> FundDistributionListResponse:
    """List fund distributions for a project."""
    items, total = await financial_service.list_fund_distributions(
        db, project_id
    )
    return FundDistributionListResponse(
        items=[
            FundDistributionResponse.model_validate(d) for d in items
        ],
        total=total,
    )


@router.put(
    "/fund-distributions/{distribution_id}",
    response_model=FundDistributionResponse,
)
async def update_fund_distribution(
    project_id: uuid.UUID,
    distribution_id: uuid.UUID,
    data: FundDistributionUpdate,
    db: AsyncSession = Depends(get_db),
) -> FundDistributionResponse:
    """Update a fund distribution record."""
    distribution = await financial_service.update_fund_distribution(
        db, project_id, distribution_id, data
    )
    if distribution is None:
        raise HTTPException(
            status_code=404, detail="Fund distribution not found"
        )
    return FundDistributionResponse.model_validate(distribution)


@router.delete(
    "/fund-distributions/{distribution_id}", status_code=204
)
async def delete_fund_distribution(
    project_id: uuid.UUID,
    distribution_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a fund distribution record."""
    deleted = await financial_service.delete_fund_distribution(
        db, project_id, distribution_id
    )
    if not deleted:
        raise HTTPException(
            status_code=404, detail="Fund distribution not found"
        )
