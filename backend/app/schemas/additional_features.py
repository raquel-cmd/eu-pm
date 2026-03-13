"""Pydantic schemas for Section 9 — Additional Features."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import (
    AmendmentStatus,
    AmendmentType,
    DisseminationActivityType,
    DMPStatus,
    EthicsStatus,
    IPStatus,
    IPType,
    KPIDataType,
    NotificationPriority,
    NotificationStatus,
    NotificationType,
    OpenAccessStatus,
)


# --- 9.1 IP and Exploitation Tracking ---


class IPAssetCreate(BaseModel):
    """Create an IP asset."""

    partner_id: uuid.UUID | None = None
    work_package_id: uuid.UUID | None = None
    deliverable_id: uuid.UUID | None = None
    ip_type: IPType
    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    status: IPStatus = IPStatus.IDENTIFIED
    owner: str | None = None
    patent_reference: str | None = None
    patent_filing_date: date | None = None
    licensing_details: str | None = None
    exploitation_plan: str | None = None
    access_rights: dict | None = None


class IPAssetUpdate(BaseModel):
    """Update an IP asset."""

    partner_id: uuid.UUID | None = None
    work_package_id: uuid.UUID | None = None
    deliverable_id: uuid.UUID | None = None
    ip_type: IPType | None = None
    title: str | None = None
    description: str | None = None
    status: IPStatus | None = None
    owner: str | None = None
    patent_reference: str | None = None
    patent_filing_date: date | None = None
    licensing_details: str | None = None
    exploitation_plan: str | None = None
    access_rights: dict | None = None


class IPAssetResponse(BaseModel):
    """Response for an IP asset."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    partner_id: uuid.UUID | None
    work_package_id: uuid.UUID | None
    deliverable_id: uuid.UUID | None
    ip_type: IPType
    title: str
    description: str | None
    status: IPStatus
    owner: str | None
    patent_reference: str | None
    patent_filing_date: date | None
    licensing_details: str | None
    exploitation_plan: str | None
    access_rights: dict | None
    created_at: datetime
    updated_at: datetime


class IPAssetListResponse(BaseModel):
    """List of IP assets."""

    items: list[IPAssetResponse]
    total: int


# --- 9.3 Communication and Dissemination Log ---


class DisseminationActivityCreate(BaseModel):
    """Create a dissemination activity."""

    work_package_id: uuid.UUID | None = None
    deliverable_id: uuid.UUID | None = None
    activity_type: DisseminationActivityType
    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    authors: str | None = None
    venue: str | None = None
    activity_date: date | None = None
    doi: str | None = None
    url: str | None = None
    open_access_status: OpenAccessStatus = OpenAccessStatus.NOT_APPLICABLE
    target_audience: str | None = None
    countries_reached: list | None = None
    evidence_documents: dict | None = None


class DisseminationActivityUpdate(BaseModel):
    """Update a dissemination activity."""

    work_package_id: uuid.UUID | None = None
    deliverable_id: uuid.UUID | None = None
    activity_type: DisseminationActivityType | None = None
    title: str | None = None
    description: str | None = None
    authors: str | None = None
    venue: str | None = None
    activity_date: date | None = None
    doi: str | None = None
    url: str | None = None
    open_access_status: OpenAccessStatus | None = None
    target_audience: str | None = None
    countries_reached: list | None = None
    evidence_documents: dict | None = None


class DisseminationActivityResponse(BaseModel):
    """Response for a dissemination activity."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    work_package_id: uuid.UUID | None
    deliverable_id: uuid.UUID | None
    activity_type: DisseminationActivityType
    title: str
    description: str | None
    authors: str | None
    venue: str | None
    activity_date: date | None
    doi: str | None
    url: str | None
    open_access_status: OpenAccessStatus
    target_audience: str | None
    countries_reached: list | None
    evidence_documents: dict | None
    created_at: datetime
    updated_at: datetime


class DisseminationActivityListResponse(BaseModel):
    """List of dissemination activities."""

    items: list[DisseminationActivityResponse]
    total: int


# --- 9.4 KPI and Indicator Tracking ---


class KPIDefinitionCreate(BaseModel):
    """Create a KPI definition."""

    name: str = Field(..., min_length=1, max_length=300)
    description: str | None = None
    data_type: KPIDataType
    unit: str | None = None
    programme: str | None = None
    is_standard: bool = True


class KPIDefinitionUpdate(BaseModel):
    """Update a KPI definition."""

    name: str | None = None
    description: str | None = None
    data_type: KPIDataType | None = None
    unit: str | None = None
    programme: str | None = None
    is_standard: bool | None = None


class KPIDefinitionResponse(BaseModel):
    """Response for a KPI definition."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None
    data_type: KPIDataType
    unit: str | None
    programme: str | None
    is_standard: bool
    created_at: datetime
    updated_at: datetime


class KPIDefinitionListResponse(BaseModel):
    """List of KPI definitions."""

    items: list[KPIDefinitionResponse]
    total: int


class KPIValueCreate(BaseModel):
    """Create a KPI value."""

    kpi_definition_id: uuid.UUID
    reporting_period_id: uuid.UUID | None = None
    value_integer: int | None = None
    value_decimal: Decimal | None = None
    value_text: str | None = None
    value_boolean: bool | None = None
    target_value: str | None = None
    notes: str | None = None
    recorded_at: datetime | None = None


class KPIValueUpdate(BaseModel):
    """Update a KPI value."""

    kpi_definition_id: uuid.UUID | None = None
    reporting_period_id: uuid.UUID | None = None
    value_integer: int | None = None
    value_decimal: Decimal | None = None
    value_text: str | None = None
    value_boolean: bool | None = None
    target_value: str | None = None
    notes: str | None = None
    recorded_at: datetime | None = None


class KPIValueResponse(BaseModel):
    """Response for a KPI value."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    kpi_definition_id: uuid.UUID
    reporting_period_id: uuid.UUID | None
    value_integer: int | None
    value_decimal: Decimal | None
    value_text: str | None
    value_boolean: bool | None
    target_value: str | None
    notes: str | None
    recorded_at: datetime | None
    created_at: datetime
    updated_at: datetime


class KPIValueListResponse(BaseModel):
    """List of KPI values."""

    items: list[KPIValueResponse]
    total: int


# --- 9.5 Ethics and Data Management ---


class EthicsRequirementCreate(BaseModel):
    """Create an ethics requirement."""

    deliverable_id: uuid.UUID | None = None
    requirement_type: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    status: EthicsStatus = EthicsStatus.PENDING
    due_date: date | None = None
    submitted_date: date | None = None
    approval_date: date | None = None
    ethics_committee_ref: str | None = None
    informed_consent_obtained: bool = False
    dpia_required: bool = False
    dpia_reference: str | None = None
    supporting_documents: dict | None = None


class EthicsRequirementUpdate(BaseModel):
    """Update an ethics requirement."""

    deliverable_id: uuid.UUID | None = None
    requirement_type: str | None = None
    description: str | None = None
    status: EthicsStatus | None = None
    due_date: date | None = None
    submitted_date: date | None = None
    approval_date: date | None = None
    ethics_committee_ref: str | None = None
    informed_consent_obtained: bool | None = None
    dpia_required: bool | None = None
    dpia_reference: str | None = None
    supporting_documents: dict | None = None


class EthicsRequirementResponse(BaseModel):
    """Response for an ethics requirement."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    deliverable_id: uuid.UUID | None
    requirement_type: str
    description: str | None
    status: EthicsStatus
    due_date: date | None
    submitted_date: date | None
    approval_date: date | None
    ethics_committee_ref: str | None
    informed_consent_obtained: bool
    dpia_required: bool
    dpia_reference: str | None
    supporting_documents: dict | None
    created_at: datetime
    updated_at: datetime


class EthicsRequirementListResponse(BaseModel):
    """List of ethics requirements."""

    items: list[EthicsRequirementResponse]
    total: int


class DataManagementRecordCreate(BaseModel):
    """Create a data management record."""

    dataset_name: str = Field(..., min_length=1, max_length=300)
    description: str | None = None
    repository: str | None = None
    repository_url: str | None = None
    dmp_status: DMPStatus = DMPStatus.DRAFT
    fair_findable: bool = False
    fair_accessible: bool = False
    fair_interoperable: bool = False
    fair_reusable: bool = False
    data_format: str | None = None
    retention_period: str | None = None
    notes: str | None = None


class DataManagementRecordUpdate(BaseModel):
    """Update a data management record."""

    dataset_name: str | None = None
    description: str | None = None
    repository: str | None = None
    repository_url: str | None = None
    dmp_status: DMPStatus | None = None
    fair_findable: bool | None = None
    fair_accessible: bool | None = None
    fair_interoperable: bool | None = None
    fair_reusable: bool | None = None
    data_format: str | None = None
    retention_period: str | None = None
    notes: str | None = None


class DataManagementRecordResponse(BaseModel):
    """Response for a data management record."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    dataset_name: str
    description: str | None
    repository: str | None
    repository_url: str | None
    dmp_status: DMPStatus
    fair_findable: bool
    fair_accessible: bool
    fair_interoperable: bool
    fair_reusable: bool
    data_format: str | None
    retention_period: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


class DataManagementRecordListResponse(BaseModel):
    """List of data management records."""

    items: list[DataManagementRecordResponse]
    total: int


# --- 9.6 Collaboration Network ---


class CollaborationRecordCreate(BaseModel):
    """Create a collaboration record."""

    partner_id: uuid.UUID
    project_id: uuid.UUID | None = None
    expertise_areas: list | None = None
    reliability_rating: int | None = Field(None, ge=1, le=5)
    collaboration_notes: str | None = None
    contact_person: str | None = None
    contact_email: str | None = None
    co_publications: int = 0
    last_collaboration_date: date | None = None


class CollaborationRecordUpdate(BaseModel):
    """Update a collaboration record."""

    partner_id: uuid.UUID | None = None
    project_id: uuid.UUID | None = None
    expertise_areas: list | None = None
    reliability_rating: int | None = Field(None, ge=1, le=5)
    collaboration_notes: str | None = None
    contact_person: str | None = None
    contact_email: str | None = None
    co_publications: int | None = None
    last_collaboration_date: date | None = None


class CollaborationRecordResponse(BaseModel):
    """Response for a collaboration record."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    partner_id: uuid.UUID
    project_id: uuid.UUID | None
    expertise_areas: list | None
    reliability_rating: int | None
    collaboration_notes: str | None
    contact_person: str | None
    contact_email: str | None
    co_publications: int
    last_collaboration_date: date | None
    created_at: datetime
    updated_at: datetime


class CollaborationRecordListResponse(BaseModel):
    """List of collaboration records."""

    items: list[CollaborationRecordResponse]
    total: int


# --- 9.7 Amendment Tracking ---


class AmendmentCreate(BaseModel):
    """Create an amendment."""

    amendment_number: int = Field(..., ge=1)
    amendment_type: AmendmentType
    title: str = Field(..., min_length=1, max_length=300)
    description: str
    rationale: str | None = None
    status: AmendmentStatus = AmendmentStatus.DRAFT
    request_date: date | None = None
    submission_date: date | None = None
    ec_decision_date: date | None = None
    changes_summary: dict | None = None
    affected_partners: list | None = None
    affected_work_packages: list | None = None
    budget_impact: dict | None = None
    submitted_by: str | None = None


class AmendmentUpdate(BaseModel):
    """Update an amendment."""

    amendment_number: int | None = None
    amendment_type: AmendmentType | None = None
    title: str | None = None
    description: str | None = None
    rationale: str | None = None
    status: AmendmentStatus | None = None
    request_date: date | None = None
    submission_date: date | None = None
    ec_decision_date: date | None = None
    changes_summary: dict | None = None
    affected_partners: list | None = None
    affected_work_packages: list | None = None
    budget_impact: dict | None = None
    submitted_by: str | None = None


class AmendmentResponse(BaseModel):
    """Response for an amendment."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    amendment_number: int
    amendment_type: AmendmentType
    title: str
    description: str
    rationale: str | None
    status: AmendmentStatus
    request_date: date | None
    submission_date: date | None
    ec_decision_date: date | None
    changes_summary: dict | None
    affected_partners: list | None
    affected_work_packages: list | None
    budget_impact: dict | None
    submitted_by: str | None
    created_at: datetime
    updated_at: datetime


class AmendmentListResponse(BaseModel):
    """List of amendments."""

    items: list[AmendmentResponse]
    total: int


# --- 9.8 Notification System ---


class NotificationCreate(BaseModel):
    """Create a notification."""

    project_id: uuid.UUID | None = None
    notification_type: NotificationType
    priority: NotificationPriority = NotificationPriority.MEDIUM
    title: str = Field(..., min_length=1, max_length=300)
    message: str
    recipient_role: str | None = None
    recipient_email: str | None = None
    trigger_entity_type: str | None = None
    trigger_entity_id: uuid.UUID | None = None
    scheduled_at: datetime | None = None
    extra_data: dict | None = None


class NotificationUpdate(BaseModel):
    """Update a notification."""

    status: NotificationStatus | None = None
    priority: NotificationPriority | None = None
    title: str | None = None
    message: str | None = None
    extra_data: dict | None = None


class NotificationResponse(BaseModel):
    """Response for a notification."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID | None
    notification_type: NotificationType
    priority: NotificationPriority
    status: NotificationStatus
    title: str
    message: str
    recipient_role: str | None
    recipient_email: str | None
    trigger_entity_type: str | None
    trigger_entity_id: uuid.UUID | None
    scheduled_at: datetime | None
    sent_at: datetime | None
    read_at: datetime | None
    dismissed_at: datetime | None
    extra_data: dict | None
    created_at: datetime
    updated_at: datetime


class NotificationListResponse(BaseModel):
    """List of notifications."""

    items: list[NotificationResponse]
    total: int
