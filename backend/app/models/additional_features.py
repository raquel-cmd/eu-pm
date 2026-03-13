"""Database models for Section 9 — Additional Features.

Covers IP tracking, dissemination log, KPI indicators, ethics/DMP,
amendment tracking, collaboration network, and notification system.
"""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin
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


class IPAsset(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """Intellectual property asset — background or foreground IP."""

    __tablename__ = "ip_assets"

    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    partner_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("partners.id"), nullable=True
    )
    work_package_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("work_packages.id"), nullable=True
    )
    deliverable_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("deliverables.id"), nullable=True
    )
    ip_type: Mapped[IPType] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[IPStatus] = mapped_column(
        nullable=False, default=IPStatus.IDENTIFIED
    )
    owner: Mapped[str | None] = mapped_column(String(300), nullable=True)
    patent_reference: Mapped[str | None] = mapped_column(
        String(200), nullable=True
    )
    patent_filing_date: Mapped[date | None] = mapped_column(
        Date, nullable=True
    )
    licensing_details: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    exploitation_plan: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    access_rights: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True
    )

    project = relationship("Project", back_populates="ip_assets")


# --- 9.3 Communication and Dissemination Log ---


class DisseminationActivity(
    UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base
):
    """Communication or dissemination activity record."""

    __tablename__ = "dissemination_activities"

    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    work_package_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("work_packages.id"), nullable=True
    )
    deliverable_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("deliverables.id"), nullable=True
    )
    activity_type: Mapped[DisseminationActivityType] = mapped_column(
        nullable=False
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    authors: Mapped[str | None] = mapped_column(Text, nullable=True)
    venue: Mapped[str | None] = mapped_column(String(500), nullable=True)
    activity_date: Mapped[date | None] = mapped_column(
        Date, nullable=True
    )
    doi: Mapped[str | None] = mapped_column(String(200), nullable=True)
    url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    open_access_status: Mapped[OpenAccessStatus] = mapped_column(
        nullable=False, default=OpenAccessStatus.NOT_APPLICABLE
    )
    target_audience: Mapped[str | None] = mapped_column(
        String(300), nullable=True
    )
    countries_reached: Mapped[list | None] = mapped_column(
        JSONB, nullable=True
    )
    evidence_documents: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True
    )

    project = relationship("Project", back_populates="dissemination_activities")


# --- 9.4 KPI and Indicator Tracking ---


class KPIDefinition(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Programme-specific KPI/indicator definition."""

    __tablename__ = "kpi_definitions"

    name: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_type: Mapped[KPIDataType] = mapped_column(nullable=False)
    unit: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    programme: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )
    is_standard: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )


class KPIValue(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """KPI indicator value for a project at a point in time."""

    __tablename__ = "kpi_values"

    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    kpi_definition_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("kpi_definitions.id"),
        nullable=False,
    )
    reporting_period_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reporting_periods.id"),
        nullable=True,
    )
    value_integer: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    value_decimal: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    value_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    value_boolean: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True
    )
    target_value: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    recorded_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    project = relationship("Project", back_populates="kpi_values")
    kpi_definition = relationship("KPIDefinition")


# --- 9.5 Ethics and Data Management ---


class EthicsRequirement(
    UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base
):
    """Ethics requirement or deliverable linked to a project."""

    __tablename__ = "ethics_requirements"

    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    deliverable_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("deliverables.id"), nullable=True
    )
    requirement_type: Mapped[str] = mapped_column(
        String(200), nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[EthicsStatus] = mapped_column(
        nullable=False, default=EthicsStatus.PENDING
    )
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    submitted_date: Mapped[date | None] = mapped_column(
        Date, nullable=True
    )
    approval_date: Mapped[date | None] = mapped_column(
        Date, nullable=True
    )
    ethics_committee_ref: Mapped[str | None] = mapped_column(
        String(200), nullable=True
    )
    informed_consent_obtained: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    dpia_required: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    dpia_reference: Mapped[str | None] = mapped_column(
        String(200), nullable=True
    )
    supporting_documents: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True
    )

    project = relationship("Project", back_populates="ethics_requirements")


class DataManagementRecord(
    UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base
):
    """Data management plan record tracking DMP compliance."""

    __tablename__ = "data_management_records"

    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    dataset_name: Mapped[str] = mapped_column(
        String(300), nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    repository: Mapped[str | None] = mapped_column(
        String(300), nullable=True
    )
    repository_url: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )
    dmp_status: Mapped[DMPStatus] = mapped_column(
        nullable=False, default=DMPStatus.DRAFT
    )
    fair_findable: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    fair_accessible: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    fair_interoperable: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    fair_reusable: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    data_format: Mapped[str | None] = mapped_column(
        String(200), nullable=True
    )
    retention_period: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    project = relationship(
        "Project", back_populates="data_management_records"
    )


# --- 9.6 Collaboration Network ---


class CollaborationRecord(
    UUIDPrimaryKeyMixin, TimestampMixin, Base
):
    """Cross-project collaboration history with a partner."""

    __tablename__ = "collaboration_records"

    partner_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("partners.id"), nullable=False
    )
    project_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True
    )
    expertise_areas: Mapped[list | None] = mapped_column(
        JSONB, nullable=True
    )
    reliability_rating: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    collaboration_notes: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    contact_person: Mapped[str | None] = mapped_column(
        String(300), nullable=True
    )
    contact_email: Mapped[str | None] = mapped_column(
        String(300), nullable=True
    )
    co_publications: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    last_collaboration_date: Mapped[date | None] = mapped_column(
        Date, nullable=True
    )

    partner = relationship("Partner")
    project = relationship("Project")


# --- 9.7 Amendment Tracking ---


class Amendment(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """Grant agreement amendment record."""

    __tablename__ = "amendments"

    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    amendment_number: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    amendment_type: Mapped[AmendmentType] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[AmendmentStatus] = mapped_column(
        nullable=False, default=AmendmentStatus.DRAFT
    )
    request_date: Mapped[date | None] = mapped_column(
        Date, nullable=True
    )
    submission_date: Mapped[date | None] = mapped_column(
        Date, nullable=True
    )
    ec_decision_date: Mapped[date | None] = mapped_column(
        Date, nullable=True
    )
    changes_summary: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True
    )
    affected_partners: Mapped[list | None] = mapped_column(
        JSONB, nullable=True
    )
    affected_work_packages: Mapped[list | None] = mapped_column(
        JSONB, nullable=True
    )
    budget_impact: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True
    )
    submitted_by: Mapped[str | None] = mapped_column(
        String(200), nullable=True
    )

    project = relationship("Project", back_populates="amendments")


# --- 9.8 Notification System ---


class Notification(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """System notification/alert record."""

    __tablename__ = "notifications"

    project_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True
    )
    notification_type: Mapped[NotificationType] = mapped_column(
        nullable=False
    )
    priority: Mapped[NotificationPriority] = mapped_column(
        nullable=False, default=NotificationPriority.MEDIUM
    )
    status: Mapped[NotificationStatus] = mapped_column(
        nullable=False, default=NotificationStatus.PENDING
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    recipient_role: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    recipient_email: Mapped[str | None] = mapped_column(
        String(300), nullable=True
    )
    trigger_entity_type: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    trigger_entity_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    dismissed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    extra_data: Mapped[dict | None] = mapped_column(
        "metadata", JSONB, nullable=True
    )

    project = relationship("Project", back_populates="notifications")
