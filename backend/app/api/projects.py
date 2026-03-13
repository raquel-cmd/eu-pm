"""API routes for Project entity."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.enums import CostModel, Programme, ProjectRole, ProjectStatus
from app.schemas.project import (
    ProjectCreate,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdate,
)
from app.services import project as project_service

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(
    data: ProjectCreate, db: AsyncSession = Depends(get_db)
) -> ProjectResponse:
    """Create a new project."""
    project = await project_service.create_project(db, data)
    return ProjectResponse.model_validate(project)


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    status: ProjectStatus | None = None,
    programme: Programme | None = None,
    cost_model: CostModel | None = None,
    role: ProjectRole | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> ProjectListResponse:
    """List projects with optional filters."""
    items, total = await project_service.list_projects(
        db,
        status=status,
        programme=programme,
        cost_model=cost_model,
        role=role,
        skip=skip,
        limit=limit,
    )
    return ProjectListResponse(
        items=[ProjectResponse.model_validate(p) for p in items],
        total=total,
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> ProjectResponse:
    """Get a single project by ID."""
    project = await project_service.get_project(db, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectResponse.model_validate(project)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: uuid.UUID,
    data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    """Update a project."""
    project = await project_service.update_project(db, project_id, data)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectResponse.model_validate(project)


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> None:
    """Soft-delete a project."""
    deleted = await project_service.delete_project(db, project_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Project not found")
