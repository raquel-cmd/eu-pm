"""Pydantic schemas for financial reporting (Section 8.3)."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import (
    CFSStatus,
    CompletionStatus,
    FinancialStatementStatus,
    UnitCostStatus,
    UnitType,
)


# --- Financial Statement (Form C) ---


class FinancialStatementCreate(BaseModel):
    """Create a Form C financial statement for a partner in a reporting period."""

    reporting_period_id: uuid.UUID
    partner_id: uuid.UUID | None = None


class FinancialStatementUpdate(BaseModel):
    """Update a financial statement."""

    status: FinancialStatementStatus | None = None
    category_a_personnel: Decimal | None = None
    category_b_subcontracting: Decimal | None = None
    category_c_travel: Decimal | None = None
    category_d_equipment: Decimal | None = None
    category_e_other: Decimal | None = None
    notes: str | None = None
    partner_signed_by: str | None = None
    coordinator_approved_by: str | None = None


class FinancialStatementResponse(BaseModel):
    """Response for a Form C financial statement."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    reporting_period_id: uuid.UUID
    partner_id: uuid.UUID | None
    status: FinancialStatementStatus
    category_a_personnel: Decimal
    category_b_subcontracting: Decimal
    category_c_travel: Decimal
    category_d_equipment: Decimal
    category_e_other: Decimal
    total_direct_costs: Decimal
    indirect_costs: Decimal
    total_eligible_costs: Decimal
    ec_contribution_requested: Decimal
    cumulative_claimed: Decimal
    cfs_required: bool
    cfs_status: CFSStatus
    partner_signed_by: str | None
    partner_signed_at: datetime | None
    coordinator_approved_by: str | None
    coordinator_approved_at: datetime | None
    reported_to_ec_at: datetime | None
    university_report_data: dict | None
    discrepancies: dict | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


class FinancialStatementListResponse(BaseModel):
    """List of financial statements."""

    items: list[FinancialStatementResponse]
    total: int


# --- WP Completion Declaration (Lump Sum) ---


class WPCompletionDeclarationCreate(BaseModel):
    """Create a WP completion declaration."""

    reporting_period_id: uuid.UUID
    work_package_id: uuid.UUID
    lump_sum_amount: Decimal = Field(..., ge=0)


class WPCompletionDeclarationUpdate(BaseModel):
    """Update a WP completion declaration."""

    completion_status: CompletionStatus | None = None
    completion_percentage: int | None = Field(None, ge=0, le=100)
    amount_claimed: Decimal | None = None
    partial_completion_justification: str | None = None
    evidence_documents: dict | None = None
    deliverables_completed: dict | None = None
    declared_by: str | None = None
    approved_by: str | None = None
    notes: str | None = None


class WPCompletionDeclarationResponse(BaseModel):
    """Response for a WP completion declaration."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    reporting_period_id: uuid.UUID
    work_package_id: uuid.UUID
    completion_status: CompletionStatus
    completion_percentage: int
    lump_sum_amount: Decimal
    amount_claimed: Decimal
    evidence_documents: dict | None
    partial_completion_justification: str | None
    deliverables_completed: dict | None
    declared_by: str | None
    declared_at: datetime | None
    approved_by: str | None
    approved_at: datetime | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


class WPCompletionDeclarationListResponse(BaseModel):
    """List of WP completion declarations."""

    items: list[WPCompletionDeclarationResponse]
    total: int


# --- Unit Delivery Record (Unit Costs) ---


class UnitDeliveryRecordCreate(BaseModel):
    """Create a unit delivery record."""

    reporting_period_id: uuid.UUID
    work_package_id: uuid.UUID | None = None
    description: str = Field(..., min_length=1)
    unit_type: UnitType
    planned_units: Decimal = Field(..., ge=0)
    unit_rate: Decimal = Field(..., ge=0)


class UnitDeliveryRecordUpdate(BaseModel):
    """Update a unit delivery record."""

    actual_units: Decimal | None = None
    status: UnitCostStatus | None = None
    evidence_documents: dict | None = None
    evidence_description: str | None = None
    reported_by: str | None = None
    approved_by: str | None = None
    notes: str | None = None


class UnitDeliveryRecordResponse(BaseModel):
    """Response for a unit delivery record."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    reporting_period_id: uuid.UUID
    work_package_id: uuid.UUID | None
    description: str
    unit_type: UnitType
    planned_units: Decimal
    actual_units: Decimal
    unit_rate: Decimal
    total_cost: Decimal
    status: UnitCostStatus
    evidence_documents: dict | None
    evidence_description: str | None
    reported_by: str | None
    reported_at: datetime | None
    approved_by: str | None
    approved_at: datetime | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


class UnitDeliveryRecordListResponse(BaseModel):
    """List of unit delivery records."""

    items: list[UnitDeliveryRecordResponse]
    total: int


# --- Cost-Model-Aware Financial Report ---


class CategoryBreakdownRow(BaseModel):
    """A row in the EC category breakdown for Form C."""

    ec_category: str
    university_account_code: str | None = None
    university_category_name: str | None = None
    budgeted: Decimal = Decimal("0.00")
    incurred: Decimal = Decimal("0.00")
    ec_eligible: Decimal = Decimal("0.00")


class FormCReport(BaseModel):
    """Generated Form C report for actual cost projects."""

    project_id: uuid.UUID
    project_acronym: str
    reporting_period_id: uuid.UUID
    partner_id: uuid.UUID | None
    period_start: date
    period_end: date
    category_breakdown: list[CategoryBreakdownRow]
    total_direct_costs: Decimal
    indirect_costs: Decimal
    indirect_rate: Decimal
    total_eligible_costs: Decimal
    ec_contribution_requested: Decimal
    cumulative_claimed: Decimal
    cfs_required: bool
    cfs_status: CFSStatus


class LumpSumReport(BaseModel):
    """Generated lump sum report for WP completion declarations."""

    project_id: uuid.UUID
    project_acronym: str
    reporting_period_id: uuid.UUID
    declarations: list[WPCompletionDeclarationResponse]
    total_lump_sum: Decimal
    total_claimed: Decimal


class UnitCostReport(BaseModel):
    """Generated unit cost report."""

    project_id: uuid.UUID
    project_acronym: str
    reporting_period_id: uuid.UUID
    records: list[UnitDeliveryRecordResponse]
    total_planned_cost: Decimal
    total_actual_cost: Decimal


class InstitutionalMappingRow(BaseModel):
    """A row in the institutional parallel report."""

    ec_category: str
    ec_amount: Decimal
    university_account_code: str | None = None
    university_category_name: str | None = None
    university_amount: Decimal
    discrepancy: Decimal


class InstitutionalReport(BaseModel):
    """Institutional parallel report showing EC vs university view."""

    project_id: uuid.UUID
    project_acronym: str
    rows: list[InstitutionalMappingRow]
    total_ec: Decimal
    total_university: Decimal
    total_discrepancy: Decimal
    has_discrepancies: bool


class CostModelFinancialReport(BaseModel):
    """Cost-model-aware financial report that adapts to project type."""

    project_id: uuid.UUID
    project_acronym: str
    cost_model: str
    reporting_period_id: uuid.UUID | None = None
    form_c: FormCReport | None = None
    lump_sum: LumpSumReport | None = None
    unit_cost: UnitCostReport | None = None
    institutional_report: InstitutionalReport | None = None
