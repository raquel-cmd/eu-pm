"""Pydantic schemas for WorkPackage, Deliverable, and Milestone entities."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import (
    DeliverableType,
    DisseminationLevel,
    ECReviewStatus,
    TrafficLight,
    WPStatus,
)


# --- Work Package ---


class WorkPackageCreate(BaseModel):
    """Schema for creating a work package."""

    wp_number: int
    title: str = Field(..., max_length=500)
    lead_partner_id: uuid.UUID | None = None
    start_month: int | None = None
    end_month: int | None = None
    total_pm: Decimal | None = Field(None, decimal_places=2)
    objectives: str | None = None
    status: WPStatus = WPStatus.NOT_STARTED


class WorkPackageUpdate(BaseModel):
    """Schema for updating a work package."""

    wp_number: int | None = None
    title: str | None = Field(None, max_length=500)
    lead_partner_id: uuid.UUID | None = None
    start_month: int | None = None
    end_month: int | None = None
    total_pm: Decimal | None = Field(None, decimal_places=2)
    objectives: str | None = None
    status: WPStatus | None = None


class WorkPackageResponse(BaseModel):
    """Schema for work package responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    wp_number: int
    title: str
    lead_partner_id: uuid.UUID | None
    start_month: int | None
    end_month: int | None
    total_pm: Decimal | None
    objectives: str | None
    status: WPStatus
    created_at: datetime
    updated_at: datetime


class WorkPackageListResponse(BaseModel):
    """List of work packages."""

    items: list[WorkPackageResponse]
    total: int


# --- Deliverable ---


class DeliverableCreate(BaseModel):
    """Schema for creating a deliverable."""

    deliverable_number: str = Field(..., max_length=20)
    title: str = Field(..., max_length=500)
    type: DeliverableType
    dissemination_level: DisseminationLevel
    lead_partner_id: uuid.UUID | None = None
    due_month: int | None = None
    submission_date: date | None = None
    ec_review_status: ECReviewStatus = ECReviewStatus.PENDING
    traffic_light: TrafficLight = TrafficLight.GREEN
    file_reference: str | None = Field(None, max_length=500)


class DeliverableUpdate(BaseModel):
    """Schema for updating a deliverable."""

    deliverable_number: str | None = Field(None, max_length=20)
    title: str | None = Field(None, max_length=500)
    type: DeliverableType | None = None
    dissemination_level: DisseminationLevel | None = None
    lead_partner_id: uuid.UUID | None = None
    due_month: int | None = None
    submission_date: date | None = None
    ec_review_status: ECReviewStatus | None = None
    traffic_light: TrafficLight | None = None
    file_reference: str | None = Field(None, max_length=500)


class DeliverableResponse(BaseModel):
    """Schema for deliverable responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    work_package_id: uuid.UUID
    deliverable_number: str
    title: str
    type: DeliverableType
    dissemination_level: DisseminationLevel
    lead_partner_id: uuid.UUID | None
    due_month: int | None
    submission_date: date | None
    ec_review_status: ECReviewStatus
    traffic_light: TrafficLight
    file_reference: str | None
    created_at: datetime
    updated_at: datetime


class DeliverableListResponse(BaseModel):
    """List of deliverables."""

    items: list[DeliverableResponse]
    total: int


# --- Milestone ---


class MilestoneCreate(BaseModel):
    """Schema for creating a milestone."""

    milestone_number: str = Field(..., max_length=20)
    title: str = Field(..., max_length=500)
    due_month: int | None = None
    verification_means: str | None = None
    achieved: bool = False
    achievement_date: date | None = None


class MilestoneUpdate(BaseModel):
    """Schema for updating a milestone."""

    milestone_number: str | None = Field(None, max_length=20)
    title: str | None = Field(None, max_length=500)
    due_month: int | None = None
    verification_means: str | None = None
    achieved: bool | None = None
    achievement_date: date | None = None


class MilestoneResponse(BaseModel):
    """Schema for milestone responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    work_package_id: uuid.UUID
    milestone_number: str
    title: str
    due_month: int | None
    verification_means: str | None
    achieved: bool
    achievement_date: date | None
    created_at: datetime
    updated_at: datetime


class MilestoneListResponse(BaseModel):
    """List of milestones."""

    items: list[MilestoneResponse]
    total: int
