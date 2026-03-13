"""Pydantic schemas for reporting engine (Section 8)."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import (
    ReminderType,
    ReportingPeriodType,
    ReportSectionStatus,
    ReportSectionType,
    ReportStatus,
    RiskCategory,
    RiskLevel,
    RiskStatus,
)


# --- ReportingPeriod ---


class ReportingPeriodCreate(BaseModel):
    """Create a reporting period manually."""

    period_number: int = Field(..., ge=1)
    period_type: ReportingPeriodType = ReportingPeriodType.PERIODIC
    start_date: date
    end_date: date
    technical_report_deadline: date
    financial_report_deadline: date | None = None
    review_meeting_date: date | None = None


class ReportingPeriodResponse(BaseModel):
    """Response for a reporting period."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    period_number: int
    period_type: ReportingPeriodType
    start_date: date
    end_date: date
    technical_report_deadline: date
    financial_report_deadline: date | None
    review_meeting_date: date | None
    days_until_deadline: int | None = None
    created_at: datetime
    updated_at: datetime


class ReportingPeriodListResponse(BaseModel):
    """List of reporting periods."""

    items: list[ReportingPeriodResponse]
    total: int


# --- Reporting Calendar ---


class CalendarReminderItem(BaseModel):
    """A single reminder in the reporting calendar."""

    reporting_period_id: uuid.UUID
    project_id: uuid.UUID
    project_acronym: str
    period_number: int
    reminder_type: ReminderType
    scheduled_date: date
    sent: bool
    description: str


class ReportingCalendarResponse(BaseModel):
    """Full reporting calendar view."""

    upcoming_deadlines: list[ReportingPeriodResponse]
    reminders: list[CalendarReminderItem]
    overdue_items: list[CalendarReminderItem]


# --- Risk Register ---


class RiskCreate(BaseModel):
    """Create a risk entry."""

    description: str = Field(..., min_length=1)
    category: RiskCategory
    probability: RiskLevel
    impact: RiskLevel
    mitigation_strategy: str | None = None
    owner: str | None = None
    work_package_id: uuid.UUID | None = None
    actions_taken: str | None = None


class RiskUpdate(BaseModel):
    """Update a risk entry."""

    description: str | None = None
    category: RiskCategory | None = None
    probability: RiskLevel | None = None
    impact: RiskLevel | None = None
    mitigation_strategy: str | None = None
    owner: str | None = None
    status: RiskStatus | None = None
    work_package_id: uuid.UUID | None = None
    actions_taken: str | None = None


class RiskResponse(BaseModel):
    """Response for a risk entry."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    work_package_id: uuid.UUID | None
    description: str
    category: RiskCategory
    probability: RiskLevel
    impact: RiskLevel
    mitigation_strategy: str | None
    owner: str | None
    status: RiskStatus
    actions_taken: str | None
    created_at: datetime
    updated_at: datetime


class RiskListResponse(BaseModel):
    """List of risks."""

    items: list[RiskResponse]
    total: int


# --- TechnicalReport ---


class TechnicalReportResponse(BaseModel):
    """Response for a technical report."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    reporting_period_id: uuid.UUID
    report_type: ReportingPeriodType
    status: ReportStatus
    part_a_summary: str | None
    submitted_by: str | None
    submitted_at: datetime | None
    ec_feedback: str | None
    sections: list["ReportSectionResponse"] = []
    created_at: datetime
    updated_at: datetime


class TechnicalReportListResponse(BaseModel):
    """List of technical reports."""

    items: list[TechnicalReportResponse]
    total: int


class TechnicalReportUpdate(BaseModel):
    """Update a technical report."""

    part_a_summary: str | None = None
    status: ReportStatus | None = None
    ec_feedback: str | None = None


# --- ReportSection ---


class ReportSectionResponse(BaseModel):
    """Response for a report section."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    technical_report_id: uuid.UUID
    section_type: ReportSectionType
    work_package_id: uuid.UUID | None
    content: dict | None
    narrative: str | None
    status: ReportSectionStatus
    assigned_to: str | None
    created_at: datetime
    updated_at: datetime


class ReportSectionUpdate(BaseModel):
    """Update a report section."""

    content: dict | None = None
    narrative: str | None = None
    status: ReportSectionStatus | None = None
    assigned_to: str | None = None


# --- Auto-generated section data ---


class DeliverableSummaryItem(BaseModel):
    """Deliverable summary for Part B Section 2 auto-generation."""

    deliverable_number: str
    title: str
    type: str
    dissemination_level: str
    due_month: int | None
    submission_date: date | None
    ec_review_status: str
    traffic_light: str
    is_delayed: bool


class MilestoneSummaryItem(BaseModel):
    """Milestone summary for Part B Section 2 auto-generation."""

    milestone_number: str
    title: str
    wp_number: int | None
    due_month: int | None
    achieved: bool
    achievement_date: date | None


class PartB2AutoData(BaseModel):
    """Auto-generated Part B Section 2 data."""

    deliverables: list[DeliverableSummaryItem]
    milestones: list[MilestoneSummaryItem]


class WPResourceRow(BaseModel):
    """Resource usage per WP for Part B Section 4."""

    wp_number: int | None
    wp_title: str | None
    planned_pm: Decimal
    actual_pm: Decimal
    variance_pm: Decimal
    personnel_cost: Decimal


class PartB4AutoData(BaseModel):
    """Auto-generated Part B Section 4 data."""

    rows: list[WPResourceRow]
    total_planned_pm: Decimal
    total_actual_pm: Decimal
    total_personnel_cost: Decimal


class RiskSummaryItem(BaseModel):
    """Risk summary for Part B Section 3."""

    risk_id: uuid.UUID
    description: str
    category: RiskCategory
    probability: RiskLevel
    impact: RiskLevel
    mitigation_strategy: str | None
    owner: str | None
    status: RiskStatus
    actions_taken: str | None


class PartB3AutoData(BaseModel):
    """Auto-generated Part B Section 3 data."""

    high_priority_risks: list[RiskSummaryItem]
    other_risks: list[RiskSummaryItem]


# --- Workflow step ---


class WorkflowStepInfo(BaseModel):
    """Information about a workflow step."""

    step_number: int
    name: str
    actor: str
    deadline_days_before: int
    deadline_date: date | None
    status: str  # pending, active, completed, overdue
