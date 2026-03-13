"""Pydantic schemas for institutional reporting (Section 6)."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel

from app.models.enums import (
    CostModel,
    ContractType,
    ECBudgetCategory,
    Programme,
    ProjectStatus,
    ResearcherPosition,
)


# --- Dashboard Schemas ---


class ProjectFinancialRow(BaseModel):
    """Per-project financial summary row."""

    project_id: uuid.UUID
    acronym: str
    programme: Programme
    status: ProjectStatus
    cost_model: CostModel
    start_date: date | None
    end_date: date | None
    total_budget: Decimal
    eu_contribution: Decimal
    total_spent: Decimal
    burn_rate_percentage: Decimal
    burn_rate_status: str  # on_track, under_spending, over_spending
    pm_compliance_rate: Decimal
    flags: list[str]


class UpcomingECPayment(BaseModel):
    """Expected EC payment entry."""

    project_id: uuid.UUID
    acronym: str
    payment_type: str
    expected_amount: Decimal
    expected_date: date


class RecruitmentPlanItem(BaseModel):
    """Researcher with contract ending soon."""

    project_id: uuid.UUID
    acronym: str
    researcher_name: str
    position: ResearcherPosition
    contract_type: ContractType
    contract_end: date | None
    funding_source_budget_remaining: Decimal


class FlaggedItem(BaseModel):
    """An item requiring attention."""

    project_id: uuid.UUID
    acronym: str
    flag_type: str  # BUDGET_ALERT, COMPLIANCE, PROCUREMENT
    severity: str  # WARNING, CRITICAL
    description: str


class FinanceDashboardResponse(BaseModel):
    """Top-level finance dashboard response."""

    projects: list[ProjectFinancialRow]
    total_budget_all_projects: Decimal
    total_spent_all_projects: Decimal
    overall_burn_rate: Decimal
    upcoming_ec_payments: list[UpcomingECPayment]
    recruitment_plans: list[RecruitmentPlanItem]
    flagged_items: list[FlaggedItem]
    generated_at: datetime


# --- PM Declarations ---


class PMDeclarationLine(BaseModel):
    """Single researcher PM declaration line."""

    researcher_name: str
    researcher_position: ResearcherPosition
    project_acronym: str
    period_start: date
    period_end: date
    planned_pm: Decimal
    actual_hours: Decimal
    actual_pm: Decimal
    hourly_rate: Decimal | None
    personnel_cost: Decimal
    submitted: bool
    approved: bool


class PMDeclarationsResponse(BaseModel):
    """PM declarations for a project and period."""

    project_id: uuid.UUID
    period_start: date
    period_end: date
    declarations: list[PMDeclarationLine]
    total_pm: Decimal
    total_cost: Decimal


# --- Cost Statement ---


class CostStatementLine(BaseModel):
    """Per-category cost statement line."""

    ec_category: ECBudgetCategory
    university_account_code: str | None
    university_category_name: str | None
    budgeted: Decimal
    incurred: Decimal
    ec_eligible_amount: Decimal


class CostStatementResponse(BaseModel):
    """Cost statement for a project."""

    project_id: uuid.UUID
    acronym: str
    period_start: date | None
    period_end: date | None
    lines: list[CostStatementLine]
    total_incurred: Decimal
    total_eligible: Decimal
    indirect_costs: Decimal
    grand_total: Decimal


# --- Overhead Calculations ---


class OverheadCategoryBreakdown(BaseModel):
    """Category spending for overhead calculation."""

    category: ECBudgetCategory
    amount: Decimal


class OverheadCalculationResponse(BaseModel):
    """Overhead calculation for a project."""

    project_id: uuid.UUID
    acronym: str
    cost_model: CostModel
    direct_costs_base: Decimal
    indirect_rate: Decimal
    indirect_costs: Decimal
    subcontracting_excluded: Decimal
    breakdown: list[OverheadCategoryBreakdown]


# --- Annual Summary ---


class AnnualCategorySpending(BaseModel):
    """Category spending for annual summary."""

    category: ECBudgetCategory
    amount: Decimal


class AnnualSummaryProject(BaseModel):
    """Per-project annual summary."""

    project_id: uuid.UUID
    acronym: str
    year: int
    total_budget: Decimal
    eu_contribution: Decimal
    total_spent_year: Decimal
    total_spent_cumulative: Decimal
    budget_remaining: Decimal
    spending_by_category: list[AnnualCategorySpending]
    pm_planned: Decimal
    pm_actual: Decimal
    funds_received_cumulative: Decimal
    funds_received_year: Decimal


class AnnualSummaryResponse(BaseModel):
    """Annual summary report."""

    year: int
    projects: list[AnnualSummaryProject]
    total_budget: Decimal
    total_spent_year: Decimal
    total_spent_cumulative: Decimal
