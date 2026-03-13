"""Pydantic schemas for budget monitoring (Section 4.3)."""

import uuid
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.enums import ECBudgetCategory, WPStatus


# --- Budget Summary ---


class CategorySpending(BaseModel):
    """Spending breakdown for a single EC budget category."""

    category: ECBudgetCategory
    budgeted: Decimal
    spent: Decimal
    remaining: Decimal
    percentage_used: Decimal


class BudgetSummaryResponse(BaseModel):
    """Overall budget summary for a project."""

    project_id: uuid.UUID
    total_budget: Decimal
    eu_contribution: Decimal
    total_spent: Decimal
    total_remaining: Decimal
    percentage_used: Decimal
    indirect_costs_calculated: Decimal
    categories: list[CategorySpending]
    alerts: list[str]


# --- By Category ---


class CategoryDetailResponse(BaseModel):
    """Detailed spending per EC category with transfer tracking."""

    project_id: uuid.UUID
    categories: list[CategorySpending]
    indirect_costs_calculated: Decimal
    indirect_costs_base: Decimal
    transfers: list["BudgetTransfer"]
    alerts: list[str]


class BudgetTransfer(BaseModel):
    """A budget transfer between categories with 20% rule validation."""

    from_category: ECBudgetCategory
    to_category: ECBudgetCategory
    amount: Decimal
    is_within_20_percent_rule: bool


# --- By Partner ---


class PartnerSpending(BaseModel):
    """Spending breakdown for a single partner."""

    partner_id: uuid.UUID
    partner_name: str
    budgeted: Decimal
    spent: Decimal
    remaining: Decimal
    percentage_used: Decimal


class ByPartnerResponse(BaseModel):
    """Spending breakdown by partner."""

    project_id: uuid.UUID
    partners: list[PartnerSpending]
    unassigned_spending: Decimal
    alerts: list[str]


# --- Burn Rate ---


class BurnRateResponse(BaseModel):
    """Burn rate analysis comparing spending rate to time elapsed."""

    project_id: uuid.UUID
    total_budget: Decimal
    total_spent: Decimal
    elapsed_ratio: Decimal
    budget_ratio: Decimal
    burn_rate_status: str  # "on_track", "under_spending", "over_spending"
    monthly_burn_rate: Decimal
    projected_total_spend: Decimal
    months_elapsed: int
    months_total: int
    months_remaining: int


# --- Cash Flow Forecast ---


class CashFlowEntry(BaseModel):
    """A single cash flow event."""

    entry_type: str  # "pre_financing", "interim_payment", "final_payment", "spending"
    description: str
    amount: Decimal
    date: date
    cumulative_balance: Decimal


class CashFlowForecastResponse(BaseModel):
    """Cash flow forecast based on EC payment schedule."""

    project_id: uuid.UUID
    eu_contribution: Decimal
    total_received: Decimal
    total_spent: Decimal
    current_balance: Decimal
    forecast: list[CashFlowEntry]


# --- Lump Sum WP Tracking ---


class WPCompletionStatus(BaseModel):
    """Work package completion status for lump sum projects."""

    work_package_id: uuid.UUID
    wp_number: int
    title: str
    status: WPStatus
    total_spending: Decimal
    deliverables_total: int
    deliverables_submitted: int
    milestones_total: int
    milestones_achieved: int
    completion_percentage: Decimal


# Rebuild model for forward reference
CategoryDetailResponse.model_rebuild()
