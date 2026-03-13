"""API routes for WorkPackage, Deliverable, and Milestone entities."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.work_package import (
    DeliverableCreate,
    DeliverableListResponse,
    DeliverableResponse,
    DeliverableUpdate,
    MilestoneCreate,
    MilestoneListResponse,
    MilestoneResponse,
    MilestoneUpdate,
    WorkPackageCreate,
    WorkPackageListResponse,
    WorkPackageResponse,
    WorkPackageUpdate,
)
from app.services import work_package as wp_service

router = APIRouter(prefix="/api/projects/{project_id}", tags=["work-packages"])


# --- Work Packages ---


@router.post("/work-packages", response_model=WorkPackageResponse, status_code=201)
async def create_work_package(
    project_id: uuid.UUID,
    data: WorkPackageCreate,
    db: AsyncSession = Depends(get_db),
) -> WorkPackageResponse:
    """Create a work package under a project."""
    wp = await wp_service.create_work_package(db, project_id, data)
    return WorkPackageResponse.model_validate(wp)


@router.get("/work-packages", response_model=WorkPackageListResponse)
async def list_work_packages(
    project_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> WorkPackageListResponse:
    """List all work packages for a project."""
    items, total = await wp_service.list_work_packages(db, project_id)
    return WorkPackageListResponse(
        items=[WorkPackageResponse.model_validate(wp) for wp in items],
        total=total,
    )


@router.get("/work-packages/{wp_id}", response_model=WorkPackageResponse)
async def get_work_package(
    project_id: uuid.UUID,
    wp_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> WorkPackageResponse:
    """Get a work package by ID."""
    wp = await wp_service.get_work_package(db, project_id, wp_id)
    if wp is None:
        raise HTTPException(status_code=404, detail="Work package not found")
    return WorkPackageResponse.model_validate(wp)


@router.put("/work-packages/{wp_id}", response_model=WorkPackageResponse)
async def update_work_package(
    project_id: uuid.UUID,
    wp_id: uuid.UUID,
    data: WorkPackageUpdate,
    db: AsyncSession = Depends(get_db),
) -> WorkPackageResponse:
    """Update a work package."""
    wp = await wp_service.update_work_package(db, project_id, wp_id, data)
    if wp is None:
        raise HTTPException(status_code=404, detail="Work package not found")
    return WorkPackageResponse.model_validate(wp)


@router.delete("/work-packages/{wp_id}", status_code=204)
async def delete_work_package(
    project_id: uuid.UUID,
    wp_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Soft-delete a work package."""
    deleted = await wp_service.delete_work_package(db, project_id, wp_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Work package not found")


# --- Deliverables (nested under work packages) ---


@router.post(
    "/work-packages/{wp_id}/deliverables",
    response_model=DeliverableResponse,
    status_code=201,
)
async def create_deliverable(
    project_id: uuid.UUID,
    wp_id: uuid.UUID,
    data: DeliverableCreate,
    db: AsyncSession = Depends(get_db),
) -> DeliverableResponse:
    """Create a deliverable under a work package."""
    d = await wp_service.create_deliverable(db, wp_id, data)
    return DeliverableResponse.model_validate(d)


@router.get(
    "/work-packages/{wp_id}/deliverables",
    response_model=DeliverableListResponse,
)
async def list_deliverables(
    project_id: uuid.UUID,
    wp_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> DeliverableListResponse:
    """List all deliverables for a work package."""
    items, total = await wp_service.list_deliverables(db, wp_id)
    return DeliverableListResponse(
        items=[DeliverableResponse.model_validate(d) for d in items],
        total=total,
    )


@router.get(
    "/work-packages/{wp_id}/deliverables/{deliverable_id}",
    response_model=DeliverableResponse,
)
async def get_deliverable(
    project_id: uuid.UUID,
    wp_id: uuid.UUID,
    deliverable_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> DeliverableResponse:
    """Get a deliverable by ID."""
    d = await wp_service.get_deliverable(db, wp_id, deliverable_id)
    if d is None:
        raise HTTPException(status_code=404, detail="Deliverable not found")
    return DeliverableResponse.model_validate(d)


@router.put(
    "/work-packages/{wp_id}/deliverables/{deliverable_id}",
    response_model=DeliverableResponse,
)
async def update_deliverable(
    project_id: uuid.UUID,
    wp_id: uuid.UUID,
    deliverable_id: uuid.UUID,
    data: DeliverableUpdate,
    db: AsyncSession = Depends(get_db),
) -> DeliverableResponse:
    """Update a deliverable."""
    d = await wp_service.update_deliverable(db, wp_id, deliverable_id, data)
    if d is None:
        raise HTTPException(status_code=404, detail="Deliverable not found")
    return DeliverableResponse.model_validate(d)


@router.delete(
    "/work-packages/{wp_id}/deliverables/{deliverable_id}", status_code=204
)
async def delete_deliverable(
    project_id: uuid.UUID,
    wp_id: uuid.UUID,
    deliverable_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Soft-delete a deliverable."""
    deleted = await wp_service.delete_deliverable(db, wp_id, deliverable_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Deliverable not found")


# --- Milestones (nested under work packages) ---


@router.post(
    "/work-packages/{wp_id}/milestones",
    response_model=MilestoneResponse,
    status_code=201,
)
async def create_milestone(
    project_id: uuid.UUID,
    wp_id: uuid.UUID,
    data: MilestoneCreate,
    db: AsyncSession = Depends(get_db),
) -> MilestoneResponse:
    """Create a milestone under a work package."""
    m = await wp_service.create_milestone(db, wp_id, data)
    return MilestoneResponse.model_validate(m)


@router.get(
    "/work-packages/{wp_id}/milestones",
    response_model=MilestoneListResponse,
)
async def list_milestones(
    project_id: uuid.UUID,
    wp_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> MilestoneListResponse:
    """List all milestones for a work package."""
    items, total = await wp_service.list_milestones(db, wp_id)
    return MilestoneListResponse(
        items=[MilestoneResponse.model_validate(m) for m in items],
        total=total,
    )


@router.get(
    "/work-packages/{wp_id}/milestones/{milestone_id}",
    response_model=MilestoneResponse,
)
async def get_milestone(
    project_id: uuid.UUID,
    wp_id: uuid.UUID,
    milestone_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> MilestoneResponse:
    """Get a milestone by ID."""
    m = await wp_service.get_milestone(db, wp_id, milestone_id)
    if m is None:
        raise HTTPException(status_code=404, detail="Milestone not found")
    return MilestoneResponse.model_validate(m)


@router.put(
    "/work-packages/{wp_id}/milestones/{milestone_id}",
    response_model=MilestoneResponse,
)
async def update_milestone(
    project_id: uuid.UUID,
    wp_id: uuid.UUID,
    milestone_id: uuid.UUID,
    data: MilestoneUpdate,
    db: AsyncSession = Depends(get_db),
) -> MilestoneResponse:
    """Update a milestone."""
    m = await wp_service.update_milestone(db, wp_id, milestone_id, data)
    if m is None:
        raise HTTPException(status_code=404, detail="Milestone not found")
    return MilestoneResponse.model_validate(m)


@router.delete(
    "/work-packages/{wp_id}/milestones/{milestone_id}", status_code=204
)
async def delete_milestone(
    project_id: uuid.UUID,
    wp_id: uuid.UUID,
    milestone_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Soft-delete a milestone."""
    deleted = await wp_service.delete_milestone(db, wp_id, milestone_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Milestone not found")
