"""Pydantic schemas for financial entities (Section 4)."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import (
    ApprovalStatus,
    ECBudgetCategory,
    ExpenseStatus,
    MissionPurpose,
    ProcurementApprovalStatus,
    ProcurementMethod,
    UniversityThreshold,
)


# --- Budget Category Mapping (Section 4.1) ---


class BudgetCategoryMappingCreate(BaseModel):
    """Schema for creating a budget category mapping."""

    ec_category: ECBudgetCategory
    university_account_code: str = Field(..., max_length=100)
    university_category_name: str | None = Field(None, max_length=200)
    description: str | None = None


class BudgetCategoryMappingUpdate(BaseModel):
    """Schema for updating a budget category mapping."""

    ec_category: ECBudgetCategory | None = None
    university_account_code: str | None = Field(None, max_length=100)
    university_category_name: str | None = Field(None, max_length=200)
    description: str | None = None


class BudgetCategoryMappingResponse(BaseModel):
    """Schema for budget category mapping responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    ec_category: ECBudgetCategory
    university_account_code: str
    university_category_name: str | None
    description: str | None
    created_at: datetime
    updated_at: datetime


class BudgetCategoryMappingListResponse(BaseModel):
    """List of budget category mappings."""

    items: list[BudgetCategoryMappingResponse]
    total: int


# --- Expense (Section 4.2) ---


class ExpenseCreate(BaseModel):
    """Schema for creating an expense."""

    work_package_id: uuid.UUID | None = None
    partner_id: uuid.UUID | None = None
    ec_category: ECBudgetCategory | None = None
    university_account_code: str | None = Field(None, max_length=100)
    description: str
    amount_gross: Decimal = Field(..., decimal_places=2)
    amount_net: Decimal | None = Field(None, decimal_places=2)
    vat_amount: Decimal | None = Field(None, decimal_places=2)
    currency: str = Field("EUR", max_length=3)
    exchange_rate: Decimal | None = Field(None, decimal_places=6)
    amount_eur: Decimal | None = Field(None, decimal_places=2)
    date_incurred: date
    reporting_period_id: int | None = None
    status: ExpenseStatus = ExpenseStatus.DRAFT
    ec_eligible: bool = True
    supporting_docs: dict | list | None = None


class ExpenseUpdate(BaseModel):
    """Schema for updating an expense."""

    work_package_id: uuid.UUID | None = None
    partner_id: uuid.UUID | None = None
    ec_category: ECBudgetCategory | None = None
    university_account_code: str | None = Field(None, max_length=100)
    description: str | None = None
    amount_gross: Decimal | None = Field(None, decimal_places=2)
    amount_net: Decimal | None = Field(None, decimal_places=2)
    vat_amount: Decimal | None = Field(None, decimal_places=2)
    currency: str | None = Field(None, max_length=3)
    exchange_rate: Decimal | None = Field(None, decimal_places=6)
    amount_eur: Decimal | None = Field(None, decimal_places=2)
    date_incurred: date | None = None
    reporting_period_id: int | None = None
    status: ExpenseStatus | None = None
    ec_eligible: bool | None = None
    supporting_docs: dict | list | None = None


class ExpenseResponse(BaseModel):
    """Schema for expense responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    work_package_id: uuid.UUID | None
    partner_id: uuid.UUID | None
    ec_category: ECBudgetCategory | None
    university_account_code: str | None
    description: str
    amount_gross: Decimal
    amount_net: Decimal | None
    vat_amount: Decimal | None
    currency: str
    exchange_rate: Decimal | None
    amount_eur: Decimal | None
    date_incurred: date
    reporting_period_id: int | None
    status: ExpenseStatus
    ec_eligible: bool
    supporting_docs: dict | list | None
    created_at: datetime
    updated_at: datetime


class ExpenseListResponse(BaseModel):
    """Paginated list of expenses."""

    items: list[ExpenseResponse]
    total: int


# --- Mission (Section 4.5) ---


class MissionCreate(BaseModel):
    """Schema for creating a mission."""

    work_package_id: uuid.UUID | None = None
    researcher_name: str = Field(..., max_length=200)
    purpose: MissionPurpose
    destination: str = Field(..., max_length=200)
    start_date: date
    end_date: date
    approval_status: ApprovalStatus = ApprovalStatus.REQUESTED
    travel_costs: Decimal | None = Field(None, decimal_places=2)
    accommodation_costs: Decimal | None = Field(None, decimal_places=2)
    subsistence: Decimal | None = Field(None, decimal_places=2)
    registration_fees: Decimal | None = Field(None, decimal_places=2)
    other_costs: Decimal | None = Field(None, decimal_places=2)
    total_cost: Decimal | None = Field(None, decimal_places=2)
    currency: str = Field("EUR", max_length=3)
    amount_eur: Decimal | None = Field(None, decimal_places=2)
    ec_eligible: bool = True
    supporting_docs: dict | list | None = None
    university_travel_order: str | None = Field(None, max_length=100)
    is_international: bool = False


class MissionApprove(BaseModel):
    """Schema for approving a mission (PI or central)."""

    approval_notes: str | None = None


class MissionComplete(BaseModel):
    """Schema for completing a mission with actual receipts."""

    actual_travel_costs: Decimal | None = Field(None, decimal_places=2)
    actual_accommodation_costs: Decimal | None = Field(
        None, decimal_places=2
    )
    actual_subsistence: Decimal | None = Field(None, decimal_places=2)
    actual_registration_fees: Decimal | None = Field(
        None, decimal_places=2
    )
    actual_other_costs: Decimal | None = Field(None, decimal_places=2)
    actual_total_cost: Decimal = Field(..., decimal_places=2)
    actual_receipts: dict | list | None = None
    university_travel_order: str | None = Field(None, max_length=100)


class MissionUpdate(BaseModel):
    """Schema for updating a mission."""

    work_package_id: uuid.UUID | None = None
    researcher_name: str | None = Field(None, max_length=200)
    purpose: MissionPurpose | None = None
    destination: str | None = Field(None, max_length=200)
    start_date: date | None = None
    end_date: date | None = None
    approval_status: ApprovalStatus | None = None
    travel_costs: Decimal | None = Field(None, decimal_places=2)
    accommodation_costs: Decimal | None = Field(None, decimal_places=2)
    subsistence: Decimal | None = Field(None, decimal_places=2)
    registration_fees: Decimal | None = Field(None, decimal_places=2)
    other_costs: Decimal | None = Field(None, decimal_places=2)
    total_cost: Decimal | None = Field(None, decimal_places=2)
    currency: str | None = Field(None, max_length=3)
    amount_eur: Decimal | None = Field(None, decimal_places=2)
    ec_eligible: bool | None = None
    supporting_docs: dict | list | None = None
    university_travel_order: str | None = Field(None, max_length=100)


class MissionResponse(BaseModel):
    """Schema for mission responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    work_package_id: uuid.UUID | None
    researcher_name: str
    purpose: MissionPurpose
    destination: str
    start_date: date
    end_date: date
    approval_status: ApprovalStatus
    travel_costs: Decimal | None
    accommodation_costs: Decimal | None
    subsistence: Decimal | None
    registration_fees: Decimal | None
    other_costs: Decimal | None
    total_cost: Decimal | None
    currency: str
    amount_eur: Decimal | None
    ec_eligible: bool
    supporting_docs: dict | list | None
    university_travel_order: str | None
    estimated_total_cost: Decimal | None
    actual_total_cost: Decimal | None
    is_international: bool
    requires_central_approval: bool
    approved_by_pi_at: datetime | None
    approved_centrally_at: datetime | None
    completed_at: datetime | None
    reconciliation_notes: str | None
    actual_receipts: dict | list | None
    created_at: datetime
    updated_at: datetime


class MissionListResponse(BaseModel):
    """Paginated list of missions."""

    items: list[MissionResponse]
    total: int


# --- Procurement (Section 4.6) ---


class ProcurementCreate(BaseModel):
    """Schema for creating a procurement."""

    work_package_id: uuid.UUID | None = None
    ec_category: ECBudgetCategory | None = None
    description: str
    estimated_cost: Decimal | None = Field(None, decimal_places=2)
    actual_cost: Decimal | None = Field(None, decimal_places=2)
    supplier: str | None = Field(None, max_length=300)
    procurement_method: ProcurementMethod | None = None
    university_threshold: UniversityThreshold | None = None
    depreciation_applicable: bool = False
    depreciation_rate: Decimal | None = Field(None, decimal_places=2)
    eligible_amount: Decimal | None = Field(None, decimal_places=2)
    purchase_date: date | None = None
    invoice_reference: str | None = Field(None, max_length=100)
    supporting_docs: dict | list | None = None
    approval_status: ProcurementApprovalStatus = (
        ProcurementApprovalStatus.REQUESTED
    )


class ProcurementUpdate(BaseModel):
    """Schema for updating a procurement."""

    work_package_id: uuid.UUID | None = None
    ec_category: ECBudgetCategory | None = None
    description: str | None = None
    estimated_cost: Decimal | None = Field(None, decimal_places=2)
    actual_cost: Decimal | None = Field(None, decimal_places=2)
    supplier: str | None = Field(None, max_length=300)
    procurement_method: ProcurementMethod | None = None
    university_threshold: UniversityThreshold | None = None
    depreciation_applicable: bool | None = None
    depreciation_rate: Decimal | None = Field(None, decimal_places=2)
    eligible_amount: Decimal | None = Field(None, decimal_places=2)
    purchase_date: date | None = None
    invoice_reference: str | None = Field(None, max_length=100)
    supporting_docs: dict | list | None = None
    approval_status: ProcurementApprovalStatus | None = None


class ProcurementResponse(BaseModel):
    """Schema for procurement responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    work_package_id: uuid.UUID | None
    ec_category: ECBudgetCategory | None
    description: str
    estimated_cost: Decimal | None
    actual_cost: Decimal | None
    supplier: str | None
    procurement_method: ProcurementMethod | None
    university_threshold: UniversityThreshold | None
    depreciation_applicable: bool
    depreciation_rate: Decimal | None
    eligible_amount: Decimal | None
    purchase_date: date | None
    invoice_reference: str | None
    supporting_docs: dict | list | None
    approval_status: ProcurementApprovalStatus
    created_at: datetime
    updated_at: datetime


class ProcurementListResponse(BaseModel):
    """Paginated list of procurements."""

    items: list[ProcurementResponse]
    total: int


# --- Fund Distribution (Section 4.4) ---


class FundDistributionCreate(BaseModel):
    """Schema for creating a fund distribution record."""

    partner_id: uuid.UUID | None = None
    distribution_type: str = Field(..., max_length=50)
    amount: Decimal = Field(..., decimal_places=2)
    currency: str = Field("EUR", max_length=3)
    distribution_date: date
    bank_transfer_reference: str | None = Field(None, max_length=200)
    notes: str | None = None


class FundDistributionUpdate(BaseModel):
    """Schema for updating a fund distribution record."""

    partner_id: uuid.UUID | None = None
    distribution_type: str | None = Field(None, max_length=50)
    amount: Decimal | None = Field(None, decimal_places=2)
    currency: str | None = Field(None, max_length=3)
    distribution_date: date | None = None
    bank_transfer_reference: str | None = Field(None, max_length=200)
    notes: str | None = None


class FundDistributionResponse(BaseModel):
    """Schema for fund distribution responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    partner_id: uuid.UUID | None
    distribution_type: str
    amount: Decimal
    currency: str
    distribution_date: date
    bank_transfer_reference: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


class FundDistributionListResponse(BaseModel):
    """Paginated list of fund distributions."""

    items: list[FundDistributionResponse]
    total: int
