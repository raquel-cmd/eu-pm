"""Pydantic schemas for researcher profiles and timesheets (Section 5)."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ContractType, ResearcherPosition


# --- Researcher (Section 5.1) ---


class ResearcherCreate(BaseModel):
    """Schema for creating a researcher profile."""

    name: str = Field(..., max_length=200)
    email: str | None = Field(None, max_length=200)
    position: ResearcherPosition
    contract_type: ContractType
    fte: Decimal = Field(default=Decimal("1.00"), ge=0, le=Decimal("1.00"))
    annual_gross_cost: Decimal | None = Field(None, ge=0)
    productive_hours: int = Field(default=1720, gt=0)
    start_date: date | None = None
    end_date: date | None = None


class ResearcherUpdate(BaseModel):
    """Schema for updating a researcher profile."""

    name: str | None = Field(None, max_length=200)
    email: str | None = Field(None, max_length=200)
    position: ResearcherPosition | None = None
    contract_type: ContractType | None = None
    fte: Decimal | None = Field(None, ge=0, le=Decimal("1.00"))
    annual_gross_cost: Decimal | None = Field(None, ge=0)
    productive_hours: int | None = Field(None, gt=0)
    start_date: date | None = None
    end_date: date | None = None


class ResearcherResponse(BaseModel):
    """Schema for researcher profile responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    email: str | None
    position: ResearcherPosition
    contract_type: ContractType
    fte: Decimal
    annual_gross_cost: Decimal | None
    productive_hours: int
    hourly_rate: Decimal | None
    start_date: date | None
    end_date: date | None
    created_at: datetime
    updated_at: datetime


class ResearcherListResponse(BaseModel):
    """List of researchers."""

    items: list[ResearcherResponse]
    total: int


# --- Effort Allocation (Section 5.2) ---


class EffortAllocationCreate(BaseModel):
    """Schema for creating an effort allocation."""

    researcher_id: uuid.UUID
    work_package_id: uuid.UUID | None = None
    period_start: date
    period_end: date
    planned_pm: Decimal = Field(..., ge=0)
    planned_fte_percentage: Decimal | None = Field(None, ge=0, le=100)
    notes: str | None = None


class EffortAllocationResponse(BaseModel):
    """Schema for effort allocation responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    researcher_id: uuid.UUID
    project_id: uuid.UUID
    work_package_id: uuid.UUID | None
    period_start: date
    period_end: date
    planned_pm: Decimal
    planned_fte_percentage: Decimal | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


class EffortAllocationListResponse(BaseModel):
    """List of effort allocations."""

    items: list[EffortAllocationResponse]
    total: int


# --- Timesheet Entry (Section 5.3) ---


class TimesheetEntryCreate(BaseModel):
    """Schema for creating a timesheet entry."""

    researcher_id: uuid.UUID
    work_package_id: uuid.UUID | None = None
    date: date
    hours: Decimal = Field(..., gt=0, le=24)
    description: str | None = None


class TimesheetEntryUpdate(BaseModel):
    """Schema for updating a timesheet entry."""

    hours: Decimal | None = Field(None, gt=0, le=24)
    description: str | None = None


class TimesheetEntryResponse(BaseModel):
    """Schema for timesheet entry responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    researcher_id: uuid.UUID
    project_id: uuid.UUID
    work_package_id: uuid.UUID | None
    date: date
    hours: Decimal
    description: str | None
    submitted_at: datetime | None
    approved_at: datetime | None
    person_months: Decimal | None = None
    created_at: datetime
    updated_at: datetime


class TimesheetEntryListResponse(BaseModel):
    """List of timesheet entries."""

    items: list[TimesheetEntryResponse]
    total: int


class TimesheetSubmit(BaseModel):
    """Schema for batch submitting timesheet entries."""

    entry_ids: list[uuid.UUID]


# --- Cross-Project Views ---


class ProjectAllocationDetail(BaseModel):
    """Per-project allocation detail for a researcher."""

    project_id: uuid.UUID
    acronym: str
    committed_pm: Decimal
    actual_pm: Decimal
    available_capacity: Decimal


class ResearcherAllocationResponse(BaseModel):
    """Cross-project allocation overview for a researcher."""

    researcher_id: uuid.UUID
    researcher_name: str
    fte: Decimal
    allocations: list[ProjectAllocationDetail]


class WPEffortRow(BaseModel):
    """Per-WP effort row in project effort summary."""

    wp_number: int | None
    wp_title: str | None
    planned_pm: Decimal
    actual_pm: Decimal
    variance: Decimal


class ProjectEffortSummaryResponse(BaseModel):
    """Project-level effort summary by work package."""

    project_id: uuid.UUID
    rows: list[WPEffortRow]
    total_planned_pm: Decimal
    total_actual_pm: Decimal


# --- Compliance ---


class ComplianceIssue(BaseModel):
    """A single compliance issue."""

    researcher_name: str
    issue_type: str  # "missing_timesheet", "late_submission", "over_capacity"
    details: str
    period: str


class ComplianceReportResponse(BaseModel):
    """Compliance report for a project period."""

    issues: list[ComplianceIssue]
    total_issues: int
