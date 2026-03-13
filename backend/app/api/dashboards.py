"""API endpoints for role-based dashboards (Section 10)."""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.dashboards import (
    PIDashboardResponse,
    ProjectDashboardResponse,
    ResearcherDashboardResponse,
)
from app.services.dashboards import (
    get_pi_dashboard,
    get_project_dashboard,
    get_researcher_dashboard,
)

router = APIRouter(prefix="/api/dashboards", tags=["dashboards"])


@router.get("/pi", response_model=PIDashboardResponse)
async def pi_dashboard(
    db: AsyncSession = Depends(get_db),
) -> PIDashboardResponse:
    """PI portfolio overview dashboard.

    Returns aggregated metrics across all projects: traffic lights,
    budget health, team sizes, open risks, and cross-project deadlines.
    """
    return await get_pi_dashboard(db)


@router.get(
    "/researcher/{researcher_id}",
    response_model=ResearcherDashboardResponse,
)
async def researcher_dashboard(
    researcher_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ResearcherDashboardResponse:
    """Researcher personal dashboard.

    Returns effort allocations, timesheet status, and upcoming deadlines
    for the specified researcher.
    """
    return await get_researcher_dashboard(db, researcher_id)


@router.get(
    "/project/{project_id}",
    response_model=ProjectDashboardResponse,
)
async def project_dashboard(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ProjectDashboardResponse:
    """Detailed project dashboard.

    Returns WP progress, deliverable timeline, budget by category,
    partner status, risk summary, and key performance metrics.
    """
    return await get_project_dashboard(db, project_id)
