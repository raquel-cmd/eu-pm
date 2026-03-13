"""API routes for Partner and ProjectPartner entities."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.partner import (
    PartnerCreate,
    PartnerListResponse,
    PartnerResponse,
    PartnerUpdate,
    ProjectPartnerCreate,
    ProjectPartnerResponse,
    ProjectPartnerUpdate,
)
from app.services import partner as partner_service

router = APIRouter(tags=["partners"])


# --- Standalone Partner CRUD ---


@router.post("/api/partners", response_model=PartnerResponse, status_code=201)
async def create_partner(
    data: PartnerCreate, db: AsyncSession = Depends(get_db)
) -> PartnerResponse:
    """Create a new partner organization."""
    partner = await partner_service.create_partner(db, data)
    return PartnerResponse.model_validate(partner)


@router.get("/api/partners", response_model=PartnerListResponse)
async def list_partners(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> PartnerListResponse:
    """List all partners."""
    items, total = await partner_service.list_partners(db, skip=skip, limit=limit)
    return PartnerListResponse(
        items=[PartnerResponse.model_validate(p) for p in items],
        total=total,
    )


@router.get("/api/partners/{partner_id}", response_model=PartnerResponse)
async def get_partner(
    partner_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> PartnerResponse:
    """Get a single partner by ID."""
    partner = await partner_service.get_partner(db, partner_id)
    if partner is None:
        raise HTTPException(status_code=404, detail="Partner not found")
    return PartnerResponse.model_validate(partner)


@router.put("/api/partners/{partner_id}", response_model=PartnerResponse)
async def update_partner(
    partner_id: uuid.UUID,
    data: PartnerUpdate,
    db: AsyncSession = Depends(get_db),
) -> PartnerResponse:
    """Update a partner."""
    partner = await partner_service.update_partner(db, partner_id, data)
    if partner is None:
        raise HTTPException(status_code=404, detail="Partner not found")
    return PartnerResponse.model_validate(partner)


@router.delete("/api/partners/{partner_id}", status_code=204)
async def delete_partner(
    partner_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> None:
    """Soft-delete a partner."""
    deleted = await partner_service.delete_partner(db, partner_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Partner not found")


# --- ProjectPartner (nested under projects) ---


@router.post(
    "/api/projects/{project_id}/partners",
    response_model=ProjectPartnerResponse,
    status_code=201,
)
async def add_partner_to_project(
    project_id: uuid.UUID,
    data: ProjectPartnerCreate,
    db: AsyncSession = Depends(get_db),
) -> ProjectPartnerResponse:
    """Link a partner to a project."""
    pp = await partner_service.add_partner_to_project(db, project_id, data)
    return ProjectPartnerResponse.model_validate(pp)


@router.get(
    "/api/projects/{project_id}/partners",
    response_model=list[ProjectPartnerResponse],
)
async def list_project_partners(
    project_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> list[ProjectPartnerResponse]:
    """List all partners for a project."""
    items = await partner_service.list_project_partners(db, project_id)
    return [ProjectPartnerResponse.model_validate(pp) for pp in items]


@router.put(
    "/api/projects/{project_id}/partners/{link_id}",
    response_model=ProjectPartnerResponse,
)
async def update_project_partner(
    project_id: uuid.UUID,
    link_id: uuid.UUID,
    data: ProjectPartnerUpdate,
    db: AsyncSession = Depends(get_db),
) -> ProjectPartnerResponse:
    """Update a project-partner link."""
    pp = await partner_service.update_project_partner(db, project_id, link_id, data)
    if pp is None:
        raise HTTPException(status_code=404, detail="Project-partner link not found")
    return ProjectPartnerResponse.model_validate(pp)


@router.delete("/api/projects/{project_id}/partners/{link_id}", status_code=204)
async def remove_partner_from_project(
    project_id: uuid.UUID,
    link_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Remove a partner from a project."""
    removed = await partner_service.remove_partner_from_project(
        db, project_id, link_id
    )
    if not removed:
        raise HTTPException(status_code=404, detail="Project-partner link not found")
