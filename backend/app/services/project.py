"""Service layer for Project CRUD operations."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import CostModel, Programme, ProjectRole, ProjectStatus
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


async def create_project(db: AsyncSession, data: ProjectCreate) -> Project:
    """Create a new project."""
    project = Project(**data.model_dump())
    db.add(project)
    await db.flush()
    await db.refresh(project)
    return project


async def get_project(db: AsyncSession, project_id: uuid.UUID) -> Project | None:
    """Get a single project by ID, excluding soft-deleted."""
    stmt = select(Project).where(
        Project.id == project_id, Project.deleted_at.is_(None)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_projects(
    db: AsyncSession,
    *,
    status: ProjectStatus | None = None,
    programme: Programme | None = None,
    cost_model: CostModel | None = None,
    role: ProjectRole | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[Project], int]:
    """List projects with optional filters. Returns (items, total_count)."""
    stmt = select(Project).where(Project.deleted_at.is_(None))
    count_stmt = select(func.count(Project.id)).where(Project.deleted_at.is_(None))

    if status is not None:
        stmt = stmt.where(Project.status == status)
        count_stmt = count_stmt.where(Project.status == status)
    if programme is not None:
        stmt = stmt.where(Project.programme == programme)
        count_stmt = count_stmt.where(Project.programme == programme)
    if cost_model is not None:
        stmt = stmt.where(Project.cost_model == cost_model)
        count_stmt = count_stmt.where(Project.cost_model == cost_model)
    if role is not None:
        stmt = stmt.where(Project.role == role)
        count_stmt = count_stmt.where(Project.role == role)

    stmt = stmt.order_by(Project.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(stmt)
    items = list(result.scalars().all())

    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    return items, total


async def update_project(
    db: AsyncSession, project_id: uuid.UUID, data: ProjectUpdate
) -> Project | None:
    """Update a project. Returns None if not found."""
    project = await get_project(db, project_id)
    if project is None:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    await db.flush()
    await db.refresh(project)
    return project


async def delete_project(db: AsyncSession, project_id: uuid.UUID) -> bool:
    """Soft-delete a project. Returns False if not found."""
    project = await get_project(db, project_id)
    if project is None:
        return False

    project.deleted_at = datetime.now(timezone.utc)
    await db.flush()
    return True
