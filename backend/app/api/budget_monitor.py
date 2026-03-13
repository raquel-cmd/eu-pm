"""API routes for budget monitoring (Section 4.3).

All routes are nested under /api/projects/{project_id}/budget/.
"""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.budget_monitor import (
    BudgetSummaryResponse,
    BurnRateResponse,
    ByPartnerResponse,
    CashFlowForecastResponse,
    CategoryDetailResponse,
)
from app.services import budget_monitor as budget_service

router = APIRouter(
    prefix="/api/projects/{project_id}/budget", tags=["budget-monitoring"]
)


@router.get("/summary", response_model=BudgetSummaryResponse)
async def get_budget_summary(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> BudgetSummaryResponse:
    """Get overall budget summary for a project."""
    return await budget_service.get_budget_summary(db, project_id)


@router.get("/by-category", response_model=CategoryDetailResponse)
async def get_budget_by_category(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> CategoryDetailResponse:
    """Get detailed spending per EC category."""
    return await budget_service.get_budget_by_category(db, project_id)


@router.get("/by-partner", response_model=ByPartnerResponse)
async def get_budget_by_partner(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ByPartnerResponse:
    """Get spending breakdown by partner."""
    return await budget_service.get_budget_by_partner(db, project_id)


@router.get("/burn-rate", response_model=BurnRateResponse)
async def get_burn_rate(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> BurnRateResponse:
    """Get burn rate analysis."""
    return await budget_service.get_burn_rate(db, project_id)


@router.get("/cash-flow-forecast", response_model=CashFlowForecastResponse)
async def get_cash_flow_forecast(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> CashFlowForecastResponse:
    """Get cash flow forecast based on EC payment schedule."""
    return await budget_service.get_cash_flow_forecast(db, project_id)
