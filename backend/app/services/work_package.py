"""Service layer for WorkPackage, Deliverable, and Milestone CRUD operations."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.work_package import Deliverable, Milestone, WorkPackage
from app.schemas.work_package import (
    DeliverableCreate,
    DeliverableUpdate,
    MilestoneCreate,
    MilestoneUpdate,
    WorkPackageCreate,
    WorkPackageUpdate,
)


# --- WorkPackage ---


async def create_work_package(
    db: AsyncSession, project_id: uuid.UUID, data: WorkPackageCreate
) -> WorkPackage:
    """Create a work package under a project."""
    wp = WorkPackage(project_id=project_id, **data.model_dump())
    db.add(wp)
    await db.flush()
    await db.refresh(wp)
    return wp


async def get_work_package(
    db: AsyncSession, project_id: uuid.UUID, wp_id: uuid.UUID
) -> WorkPackage | None:
    """Get a work package by ID within a project."""
    stmt = select(WorkPackage).where(
        WorkPackage.id == wp_id,
        WorkPackage.project_id == project_id,
        WorkPackage.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_work_packages(
    db: AsyncSession, project_id: uuid.UUID
) -> tuple[list[WorkPackage], int]:
    """List all work packages for a project."""
    stmt = (
        select(WorkPackage)
        .where(
            WorkPackage.project_id == project_id,
            WorkPackage.deleted_at.is_(None),
        )
        .order_by(WorkPackage.wp_number)
    )
    count_stmt = select(func.count(WorkPackage.id)).where(
        WorkPackage.project_id == project_id,
        WorkPackage.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    items = list(result.scalars().all())
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()
    return items, total


async def update_work_package(
    db: AsyncSession,
    project_id: uuid.UUID,
    wp_id: uuid.UUID,
    data: WorkPackageUpdate,
) -> WorkPackage | None:
    """Update a work package."""
    wp = await get_work_package(db, project_id, wp_id)
    if wp is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(wp, field, value)
    await db.flush()
    await db.refresh(wp)
    return wp


async def delete_work_package(
    db: AsyncSession, project_id: uuid.UUID, wp_id: uuid.UUID
) -> bool:
    """Soft-delete a work package."""
    wp = await get_work_package(db, project_id, wp_id)
    if wp is None:
        return False
    wp.deleted_at = datetime.now(timezone.utc)
    await db.flush()
    return True


# --- Deliverable ---


async def create_deliverable(
    db: AsyncSession, wp_id: uuid.UUID, data: DeliverableCreate
) -> Deliverable:
    """Create a deliverable under a work package."""
    d = Deliverable(work_package_id=wp_id, **data.model_dump())
    db.add(d)
    await db.flush()
    await db.refresh(d)
    return d


async def get_deliverable(
    db: AsyncSession, wp_id: uuid.UUID, deliverable_id: uuid.UUID
) -> Deliverable | None:
    """Get a deliverable by ID within a work package."""
    stmt = select(Deliverable).where(
        Deliverable.id == deliverable_id,
        Deliverable.work_package_id == wp_id,
        Deliverable.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_deliverables(
    db: AsyncSession, wp_id: uuid.UUID
) -> tuple[list[Deliverable], int]:
    """List all deliverables for a work package."""
    stmt = (
        select(Deliverable)
        .where(
            Deliverable.work_package_id == wp_id,
            Deliverable.deleted_at.is_(None),
        )
        .order_by(Deliverable.deliverable_number)
    )
    count_stmt = select(func.count(Deliverable.id)).where(
        Deliverable.work_package_id == wp_id,
        Deliverable.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    items = list(result.scalars().all())
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()
    return items, total


async def update_deliverable(
    db: AsyncSession,
    wp_id: uuid.UUID,
    deliverable_id: uuid.UUID,
    data: DeliverableUpdate,
) -> Deliverable | None:
    """Update a deliverable."""
    d = await get_deliverable(db, wp_id, deliverable_id)
    if d is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(d, field, value)
    await db.flush()
    await db.refresh(d)
    return d


async def delete_deliverable(
    db: AsyncSession, wp_id: uuid.UUID, deliverable_id: uuid.UUID
) -> bool:
    """Soft-delete a deliverable."""
    d = await get_deliverable(db, wp_id, deliverable_id)
    if d is None:
        return False
    d.deleted_at = datetime.now(timezone.utc)
    await db.flush()
    return True


# --- Milestone ---


async def create_milestone(
    db: AsyncSession, wp_id: uuid.UUID, data: MilestoneCreate
) -> Milestone:
    """Create a milestone under a work package."""
    m = Milestone(work_package_id=wp_id, **data.model_dump())
    db.add(m)
    await db.flush()
    await db.refresh(m)
    return m


async def get_milestone(
    db: AsyncSession, wp_id: uuid.UUID, milestone_id: uuid.UUID
) -> Milestone | None:
    """Get a milestone by ID within a work package."""
    stmt = select(Milestone).where(
        Milestone.id == milestone_id,
        Milestone.work_package_id == wp_id,
        Milestone.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_milestones(
    db: AsyncSession, wp_id: uuid.UUID
) -> tuple[list[Milestone], int]:
    """List all milestones for a work package."""
    stmt = (
        select(Milestone)
        .where(
            Milestone.work_package_id == wp_id,
            Milestone.deleted_at.is_(None),
        )
        .order_by(Milestone.milestone_number)
    )
    count_stmt = select(func.count(Milestone.id)).where(
        Milestone.work_package_id == wp_id,
        Milestone.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    items = list(result.scalars().all())
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()
    return items, total


async def update_milestone(
    db: AsyncSession,
    wp_id: uuid.UUID,
    milestone_id: uuid.UUID,
    data: MilestoneUpdate,
) -> Milestone | None:
    """Update a milestone."""
    m = await get_milestone(db, wp_id, milestone_id)
    if m is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(m, field, value)
    await db.flush()
    await db.refresh(m)
    return m


async def delete_milestone(
    db: AsyncSession, wp_id: uuid.UUID, milestone_id: uuid.UUID
) -> bool:
    """Soft-delete a milestone."""
    m = await get_milestone(db, wp_id, milestone_id)
    if m is None:
        return False
    m.deleted_at = datetime.now(timezone.utc)
    await db.flush()
    return True
