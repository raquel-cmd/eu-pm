"""Pydantic schemas for Project entity."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import CostModel, Programme, ProjectRole, ProjectStatus


class ProjectCreate(BaseModel):
    """Schema for creating a new project."""

    acronym: str = Field(..., max_length=50)
    full_title: str = Field(..., max_length=500)
    grant_agreement_number: str | None = Field(None, max_length=50)
    programme: Programme
    call_identifier: str | None = Field(None, max_length=100)
    cost_model: CostModel
    role: ProjectRole
    start_date: date | None = None
    end_date: date | None = None
    duration_months: int | None = None
    total_budget: Decimal | None = Field(None, decimal_places=2)
    eu_contribution: Decimal | None = Field(None, decimal_places=2)
    funding_rate: Decimal | None = Field(None, decimal_places=2)
    reporting_periods: dict | list | None = None
    status: ProjectStatus = ProjectStatus.PROPOSAL
    ec_project_officer: str | None = Field(None, max_length=200)
    internal_cost_center: str | None = Field(None, max_length=50)


class ProjectUpdate(BaseModel):
    """Schema for updating a project. All fields optional."""

    acronym: str | None = Field(None, max_length=50)
    full_title: str | None = Field(None, max_length=500)
    grant_agreement_number: str | None = Field(None, max_length=50)
    programme: Programme | None = None
    call_identifier: str | None = Field(None, max_length=100)
    cost_model: CostModel | None = None
    role: ProjectRole | None = None
    start_date: date | None = None
    end_date: date | None = None
    duration_months: int | None = None
    total_budget: Decimal | None = Field(None, decimal_places=2)
    eu_contribution: Decimal | None = Field(None, decimal_places=2)
    funding_rate: Decimal | None = Field(None, decimal_places=2)
    reporting_periods: dict | list | None = None
    status: ProjectStatus | None = None
    ec_project_officer: str | None = Field(None, max_length=200)
    internal_cost_center: str | None = Field(None, max_length=50)


class ProjectResponse(BaseModel):
    """Schema for project API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    acronym: str
    full_title: str
    grant_agreement_number: str | None
    programme: Programme
    call_identifier: str | None
    cost_model: CostModel
    role: ProjectRole
    start_date: date | None
    end_date: date | None
    duration_months: int | None
    total_budget: Decimal | None
    eu_contribution: Decimal | None
    funding_rate: Decimal | None
    reporting_periods: dict | list | None
    status: ProjectStatus
    ec_project_officer: str | None
    internal_cost_center: str | None
    created_at: datetime
    updated_at: datetime


class ProjectListResponse(BaseModel):
    """Paginated list of projects."""

    items: list[ProjectResponse]
    total: int
