"""API routes for effort allocations and timesheets (Sections 5.2-5.3).

All routes nested under /api/projects/{project_id}/.
"""

import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.researcher import (
    ComplianceReportResponse,
    EffortAllocationCreate,
    EffortAllocationListResponse,
    EffortAllocationResponse,
    ProjectEffortSummaryResponse,
    TimesheetEntryCreate,
    TimesheetEntryListResponse,
    TimesheetEntryResponse,
    TimesheetEntryUpdate,
    TimesheetSubmit,
)
from app.services import timesheet as timesheet_service

router = APIRouter(prefix="/api/projects/{project_id}", tags=["timesheets"])


# --- Effort Allocations ---


@router.post("/effort-allocations", response_model=EffortAllocationResponse, status_code=201)
async def create_effort_allocation(
    project_id: uuid.UUID,
    data: EffortAllocationCreate,
    db: AsyncSession = Depends(get_db),
) -> EffortAllocationResponse:
    """Create an effort allocation for a researcher on this project."""
    allocation = await timesheet_service.create_effort_allocation(db, project_id, data)
    return EffortAllocationResponse.model_validate(allocation)


@router.get("/effort-allocations", response_model=EffortAllocationListResponse)
async def list_effort_allocations(
    project_id: uuid.UUID,
    researcher_id: uuid.UUID | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> EffortAllocationListResponse:
    """List effort allocations for this project."""
    items, total = await timesheet_service.list_effort_allocations(
        db, project_id, researcher_id, skip, limit
    )
    return EffortAllocationListResponse(
        items=[EffortAllocationResponse.model_validate(a) for a in items],
        total=total,
    )


@router.delete("/effort-allocations/{allocation_id}", status_code=204)
async def delete_effort_allocation(
    project_id: uuid.UUID,
    allocation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete an effort allocation."""
    await timesheet_service.delete_effort_allocation(db, allocation_id)


# --- Timesheet Entries ---


@router.post("/timesheets", response_model=TimesheetEntryResponse, status_code=201)
async def create_timesheet_entry(
    project_id: uuid.UUID,
    data: TimesheetEntryCreate,
    db: AsyncSession = Depends(get_db),
) -> TimesheetEntryResponse:
    """Create a timesheet entry."""
    entry = await timesheet_service.create_timesheet_entry(db, project_id, data)
    return TimesheetEntryResponse.model_validate(entry)


@router.get("/timesheets", response_model=TimesheetEntryListResponse)
async def list_timesheet_entries(
    project_id: uuid.UUID,
    researcher_id: uuid.UUID | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> TimesheetEntryListResponse:
    """List timesheet entries with filters."""
    items, total = await timesheet_service.list_timesheet_entries(
        db, project_id, researcher_id, date_from, date_to, skip, limit
    )
    return TimesheetEntryListResponse(
        items=[TimesheetEntryResponse.model_validate(e) for e in items],
        total=total,
    )


@router.put("/timesheets/{entry_id}", response_model=TimesheetEntryResponse)
async def update_timesheet_entry(
    project_id: uuid.UUID,
    entry_id: uuid.UUID,
    data: TimesheetEntryUpdate,
    db: AsyncSession = Depends(get_db),
) -> TimesheetEntryResponse:
    """Update a timesheet entry (only if not submitted)."""
    entry = await timesheet_service.update_timesheet_entry(db, entry_id, data)
    return TimesheetEntryResponse.model_validate(entry)


@router.delete("/timesheets/{entry_id}", status_code=204)
async def delete_timesheet_entry(
    project_id: uuid.UUID,
    entry_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a timesheet entry (only if not submitted)."""
    await timesheet_service.delete_timesheet_entry(db, entry_id)


@router.put("/timesheets/submit", response_model=list[TimesheetEntryResponse])
async def submit_timesheets(
    project_id: uuid.UUID,
    data: TimesheetSubmit,
    db: AsyncSession = Depends(get_db),
) -> list[TimesheetEntryResponse]:
    """Batch submit timesheet entries."""
    entries = await timesheet_service.submit_timesheets(db, data)
    return [TimesheetEntryResponse.model_validate(e) for e in entries]


@router.put("/timesheets/approve", response_model=list[TimesheetEntryResponse])
async def approve_timesheets(
    project_id: uuid.UUID,
    data: TimesheetSubmit,
    db: AsyncSession = Depends(get_db),
) -> list[TimesheetEntryResponse]:
    """Batch approve timesheet entries."""
    entries = await timesheet_service.approve_timesheets(db, data)
    return [TimesheetEntryResponse.model_validate(e) for e in entries]


# --- Project Effort Summary ---


@router.get("/effort/summary", response_model=ProjectEffortSummaryResponse)
async def get_project_effort_summary(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ProjectEffortSummaryResponse:
    """Get planned vs actual PMs per WP."""
    return await timesheet_service.get_project_effort_summary(db, project_id)


# --- Compliance ---


@router.get("/effort/compliance", response_model=ComplianceReportResponse)
async def get_compliance_report(
    project_id: uuid.UUID,
    period_start: date = Query(...),
    period_end: date = Query(...),
    db: AsyncSession = Depends(get_db),
) -> ComplianceReportResponse:
    """Get compliance report for a project period."""
    return await timesheet_service.get_compliance_report(
        db, project_id, period_start, period_end
    )
