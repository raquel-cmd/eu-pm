"""API endpoints for institutional reporting (Section 6)."""

import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import require_finance_pm
from app.core.database import get_db
from app.models.enums import UserRole
from app.schemas.reports import (
    AnnualSummaryResponse,
    CostStatementResponse,
    FinanceDashboardResponse,
    OverheadCalculationResponse,
    PMDeclarationsResponse,
)
from app.services.reports import (
    get_annual_summary,
    get_cost_statement,
    get_finance_dashboard,
    get_overhead_calculations,
    get_pm_declarations,
)

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/finance-dashboard", response_model=FinanceDashboardResponse)
async def finance_dashboard(
    db: AsyncSession = Depends(get_db),
    _role: UserRole = Depends(require_finance_pm),
) -> FinanceDashboardResponse:
    """Get cross-project financial dashboard for Central Finance PM."""
    return await get_finance_dashboard(db)


@router.get("/pm-declarations", response_model=PMDeclarationsResponse)
async def pm_declarations(
    project_id: uuid.UUID = Query(..., description="Project ID"),
    period_start: date = Query(..., description="Period start date"),
    period_end: date = Query(..., description="Period end date"),
    db: AsyncSession = Depends(get_db),
    _role: UserRole = Depends(require_finance_pm),
) -> PMDeclarationsResponse:
    """Get person-month declarations for a project and period."""
    return await get_pm_declarations(db, project_id, period_start, period_end)


@router.get("/cost-statements", response_model=CostStatementResponse)
async def cost_statements(
    project_id: uuid.UUID = Query(..., description="Project ID"),
    period_start: date | None = Query(None, description="Period start date"),
    period_end: date | None = Query(None, description="Period end date"),
    db: AsyncSession = Depends(get_db),
    _role: UserRole = Depends(require_finance_pm),
) -> CostStatementResponse:
    """Get cost statement by EC budget category for a project."""
    return await get_cost_statement(db, project_id, period_start, period_end)


@router.get("/overhead-calculations", response_model=OverheadCalculationResponse)
async def overhead_calculations(
    project_id: uuid.UUID = Query(..., description="Project ID"),
    db: AsyncSession = Depends(get_db),
    _role: UserRole = Depends(require_finance_pm),
) -> OverheadCalculationResponse:
    """Get overhead (indirect cost) calculation for a project."""
    return await get_overhead_calculations(db, project_id)


@router.get("/annual-summary", response_model=AnnualSummaryResponse)
async def annual_summary(
    year: int = Query(..., description="Reporting year"),
    project_id: uuid.UUID | None = Query(None, description="Optional project filter"),
    db: AsyncSession = Depends(get_db),
    _role: UserRole = Depends(require_finance_pm),
) -> AnnualSummaryResponse:
    """Get annual financial summary across projects."""
    return await get_annual_summary(db, year, project_id)
