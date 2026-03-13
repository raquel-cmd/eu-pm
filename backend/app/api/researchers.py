"""API routes for researcher profiles (Section 5.1).

Top-level routes not nested under projects.
"""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.researcher import (
    ResearcherAllocationResponse,
    ResearcherCreate,
    ResearcherListResponse,
    ResearcherResponse,
    ResearcherUpdate,
)
from app.services import timesheet as timesheet_service

router = APIRouter(prefix="/api/researchers", tags=["researchers"])


@router.post("", response_model=ResearcherResponse, status_code=201)
async def create_researcher(
    data: ResearcherCreate,
    db: AsyncSession = Depends(get_db),
) -> ResearcherResponse:
    """Create a new researcher profile."""
    researcher = await timesheet_service.create_researcher(db, data)
    return ResearcherResponse.model_validate(researcher)


@router.get("", response_model=ResearcherListResponse)
async def list_researchers(
    project_id: uuid.UUID | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> ResearcherListResponse:
    """List researchers with optional project filter."""
    items, total = await timesheet_service.list_researchers(db, skip, limit, project_id)
    return ResearcherListResponse(
        items=[ResearcherResponse.model_validate(r) for r in items],
        total=total,
    )


@router.get("/{researcher_id}", response_model=ResearcherResponse)
async def get_researcher(
    researcher_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ResearcherResponse:
    """Get a researcher by ID."""
    researcher = await timesheet_service.get_researcher(db, researcher_id)
    return ResearcherResponse.model_validate(researcher)


@router.put("/{researcher_id}", response_model=ResearcherResponse)
async def update_researcher(
    researcher_id: uuid.UUID,
    data: ResearcherUpdate,
    db: AsyncSession = Depends(get_db),
) -> ResearcherResponse:
    """Update a researcher profile."""
    researcher = await timesheet_service.update_researcher(db, researcher_id, data)
    return ResearcherResponse.model_validate(researcher)


@router.delete("/{researcher_id}", status_code=204)
async def delete_researcher(
    researcher_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Soft-delete a researcher."""
    await timesheet_service.delete_researcher(db, researcher_id)


@router.get("/{researcher_id}/allocation", response_model=ResearcherAllocationResponse)
async def get_researcher_allocation(
    researcher_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ResearcherAllocationResponse:
    """Get cross-project allocation overview for a researcher."""
    return await timesheet_service.get_researcher_allocation(db, researcher_id)
