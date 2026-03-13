"""Service layer for Partner and ProjectPartner CRUD operations."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.partner import Partner, ProjectPartner
from app.schemas.partner import (
    PartnerCreate,
    PartnerUpdate,
    ProjectPartnerCreate,
    ProjectPartnerUpdate,
)


# --- Partner ---


async def create_partner(db: AsyncSession, data: PartnerCreate) -> Partner:
    """Create a new partner organization."""
    partner = Partner(**data.model_dump())
    db.add(partner)
    await db.flush()
    await db.refresh(partner)
    return partner


async def get_partner(db: AsyncSession, partner_id: uuid.UUID) -> Partner | None:
    """Get a single partner by ID."""
    stmt = select(Partner).where(
        Partner.id == partner_id, Partner.deleted_at.is_(None)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_partners(
    db: AsyncSession, *, skip: int = 0, limit: int = 50
) -> tuple[list[Partner], int]:
    """List all partners."""
    stmt = (
        select(Partner)
        .where(Partner.deleted_at.is_(None))
        .order_by(Partner.short_name)
        .offset(skip)
        .limit(limit)
    )
    count_stmt = select(func.count(Partner.id)).where(Partner.deleted_at.is_(None))

    result = await db.execute(stmt)
    items = list(result.scalars().all())
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()
    return items, total


async def update_partner(
    db: AsyncSession, partner_id: uuid.UUID, data: PartnerUpdate
) -> Partner | None:
    """Update a partner."""
    partner = await get_partner(db, partner_id)
    if partner is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(partner, field, value)
    await db.flush()
    await db.refresh(partner)
    return partner


async def delete_partner(db: AsyncSession, partner_id: uuid.UUID) -> bool:
    """Soft-delete a partner."""
    partner = await get_partner(db, partner_id)
    if partner is None:
        return False
    partner.deleted_at = datetime.now(timezone.utc)
    await db.flush()
    return True


# --- ProjectPartner ---


async def add_partner_to_project(
    db: AsyncSession,
    project_id: uuid.UUID,
    data: ProjectPartnerCreate,
) -> ProjectPartner:
    """Link a partner to a project."""
    pp = ProjectPartner(
        project_id=project_id,
        partner_id=data.partner_id,
        partner_budget=data.partner_budget,
        partner_eu_contribution=data.partner_eu_contribution,
    )
    db.add(pp)
    await db.flush()
    # Eagerly load partner for the response
    stmt = (
        select(ProjectPartner)
        .options(joinedload(ProjectPartner.partner))
        .where(ProjectPartner.id == pp.id)
    )
    result = await db.execute(stmt)
    return result.scalar_one()


async def list_project_partners(
    db: AsyncSession, project_id: uuid.UUID
) -> list[ProjectPartner]:
    """List all partners for a project."""
    stmt = (
        select(ProjectPartner)
        .options(joinedload(ProjectPartner.partner))
        .where(ProjectPartner.project_id == project_id)
        .order_by(ProjectPartner.created_at)
    )
    result = await db.execute(stmt)
    return list(result.scalars().unique().all())


async def update_project_partner(
    db: AsyncSession,
    project_id: uuid.UUID,
    partner_link_id: uuid.UUID,
    data: ProjectPartnerUpdate,
) -> ProjectPartner | None:
    """Update a project-partner link."""
    stmt = (
        select(ProjectPartner)
        .options(joinedload(ProjectPartner.partner))
        .where(
            ProjectPartner.id == partner_link_id,
            ProjectPartner.project_id == project_id,
        )
    )
    result = await db.execute(stmt)
    pp = result.scalar_one_or_none()
    if pp is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(pp, field, value)
    await db.flush()
    await db.refresh(pp)
    return pp


async def remove_partner_from_project(
    db: AsyncSession, project_id: uuid.UUID, partner_link_id: uuid.UUID
) -> bool:
    """Remove a partner from a project."""
    stmt = select(ProjectPartner).where(
        ProjectPartner.id == partner_link_id,
        ProjectPartner.project_id == project_id,
    )
    result = await db.execute(stmt)
    pp = result.scalar_one_or_none()
    if pp is None:
        return False
    await db.delete(pp)
    await db.flush()
    return True
