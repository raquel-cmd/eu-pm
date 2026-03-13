"""Pydantic schemas for role-based dashboards (Section 10)."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.enums import (
    DeliverableType,
    DisseminationLevel,
    ECReviewStatus,
    Programme,
    ProjectStatus,
    RiskCategory,
    RiskLevel,
    RiskStatus,
    TrafficLight,
    WPStatus,
)


# ── PI Dashboard ──────────────────────────────────────


class PIProjectSummary(BaseModel):
    """Per-project summary row in the PI dashboard."""

    project_id: uuid.UUID
    acronym: str
    programme: Programme
    status: ProjectStatus
    traffic_light: str  # GREEN, AMBER, RED
    next_deadline: date | None
    next_deadline_type: str | None
    budget_total: Decimal
    budget_spent: Decimal
    burn_rate_pct: Decimal
    team_size: int
    open_risks: int
    active_amendments: int


class CrossProjectDeadline(BaseModel):
    """A deadline across all projects."""

    project_acronym: str
    project_id: uuid.UUID
    deadline_type: str
    date: date
    days_until: int


class PIDashboardResponse(BaseModel):
    """PI dashboard response — portfolio overview."""

    projects: list[PIProjectSummary]
    cross_project_deadlines: list[CrossProjectDeadline]
    total_budget: Decimal
    total_spent: Decimal
    overall_burn_rate: Decimal
    active_project_count: int


# ── Researcher Dashboard ──────────────────────────────


class ResearcherAllocationSummary(BaseModel):
    """Effort allocation summary for researcher dashboard."""

    project_id: uuid.UUID
    project_acronym: str
    wp_title: str | None
    planned_pm: Decimal
    actual_pm: Decimal
    period_start: date | None
    period_end: date | None


class TimesheetStatusItem(BaseModel):
    """Monthly timesheet status for a project."""

    project_acronym: str
    project_id: uuid.UUID
    month: str  # YYYY-MM
    hours_logged: Decimal
    hours_expected: Decimal
    status: str  # complete, incomplete, not_started


class ResearcherDeadline(BaseModel):
    """An upcoming deadline relevant to the researcher."""

    project_acronym: str
    project_id: uuid.UUID
    deadline_type: str
    title: str
    due_date: date
    days_until: int


class ResearcherDashboardResponse(BaseModel):
    """Researcher dashboard response."""

    researcher_name: str
    researcher_id: uuid.UUID
    allocations: list[ResearcherAllocationSummary]
    timesheet_status: list[TimesheetStatusItem]
    upcoming_deadlines: list[ResearcherDeadline]
    total_planned_pm: Decimal
    total_actual_pm: Decimal


# ── Project Dashboard ─────────────────────────────────


class WPProgressItem(BaseModel):
    """Work package progress for the project dashboard."""

    wp_number: int | None
    wp_title: str | None
    status: WPStatus
    deliverables_total: int
    deliverables_completed: int
    progress_pct: Decimal


class DeliverableTimelineItem(BaseModel):
    """Deliverable timeline entry."""

    deliverable_number: str | None
    title: str
    deliverable_type: DeliverableType
    due_month: int | None
    submission_date: date | None
    ec_review_status: ECReviewStatus
    traffic_light: TrafficLight


class BudgetCategoryItem(BaseModel):
    """Budget breakdown by EC category."""

    category: str
    category_label: str
    budgeted: Decimal
    spent: Decimal
    remaining: Decimal
    pct_used: Decimal


class PartnerStatusItem(BaseModel):
    """Partner status in the project."""

    partner_name: str
    partner_id: uuid.UUID
    country: str | None
    allocated_budget: Decimal
    spent: Decimal
    pct_used: Decimal


class ProjectRiskSummary(BaseModel):
    """Risk summary for the project dashboard."""

    risk_id: uuid.UUID
    description: str
    category: RiskCategory
    probability: RiskLevel
    impact: RiskLevel
    status: RiskStatus
    owner: str | None


class ProjectDashboardResponse(BaseModel):
    """Project dashboard response — detailed single-project view."""

    project_id: uuid.UUID
    acronym: str
    wp_progress: list[WPProgressItem]
    deliverable_timeline: list[DeliverableTimelineItem]
    budget_by_category: list[BudgetCategoryItem]
    partner_status: list[PartnerStatusItem]
    risks: list[ProjectRiskSummary]
    burn_rate: Decimal
    burn_rate_status: str
    pm_compliance_rate: Decimal
    deliverable_completion_rate: Decimal
    total_budget: Decimal
    total_spent: Decimal
