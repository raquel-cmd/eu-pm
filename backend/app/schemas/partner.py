"""Pydantic schemas for Partner and ProjectPartner entities."""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import OrgType


class PartnerCreate(BaseModel):
    """Schema for creating a new partner."""

    pic_number: str | None = Field(None, max_length=20)
    legal_name: str = Field(..., max_length=500)
    short_name: str = Field(..., max_length=50)
    country: str | None = Field(None, max_length=100)
    org_type: OrgType | None = None
    is_sme: bool = False
    contact_person: str | None = Field(None, max_length=500)
    bank_account_validated: bool = False
    accession_form_signed: bool = False


class PartnerUpdate(BaseModel):
    """Schema for updating a partner."""

    pic_number: str | None = Field(None, max_length=20)
    legal_name: str | None = Field(None, max_length=500)
    short_name: str | None = Field(None, max_length=50)
    country: str | None = Field(None, max_length=100)
    org_type: OrgType | None = None
    is_sme: bool | None = None
    contact_person: str | None = Field(None, max_length=500)
    bank_account_validated: bool | None = None
    accession_form_signed: bool | None = None


class PartnerResponse(BaseModel):
    """Schema for partner API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    pic_number: str | None
    legal_name: str
    short_name: str
    country: str | None
    org_type: OrgType | None
    is_sme: bool
    contact_person: str | None
    bank_account_validated: bool
    accession_form_signed: bool
    created_at: datetime
    updated_at: datetime


class PartnerListResponse(BaseModel):
    """Paginated list of partners."""

    items: list[PartnerResponse]
    total: int


class ProjectPartnerCreate(BaseModel):
    """Schema for linking a partner to a project."""

    partner_id: uuid.UUID
    partner_budget: Decimal | None = Field(None, decimal_places=2)
    partner_eu_contribution: Decimal | None = Field(None, decimal_places=2)


class ProjectPartnerUpdate(BaseModel):
    """Schema for updating a project-partner link."""

    partner_budget: Decimal | None = Field(None, decimal_places=2)
    partner_eu_contribution: Decimal | None = Field(None, decimal_places=2)


class ProjectPartnerResponse(BaseModel):
    """Schema for project-partner link responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    partner_id: uuid.UUID
    partner_budget: Decimal | None
    partner_eu_contribution: Decimal | None
    partner: PartnerResponse
    created_at: datetime
    updated_at: datetime
