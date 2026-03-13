"""WorkPackage, Deliverable, and Milestone models — Section 3.3 of the spec."""
import uuid

from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Date, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import (
    DeliverableType,
    DisseminationLevel,
    ECReviewStatus,
    TrafficLight,
    WPStatus,
)


class WorkPackage(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """Work package within a project."""

    __tablename__ = "work_packages"

    project_id: Mapped["uuid.UUID"] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True
    )
    wp_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    lead_partner_id: Mapped["uuid.UUID | None"] = mapped_column(
        UUID(as_uuid=True), ForeignKey("partners.id"), nullable=True
    )
    start_month: Mapped[int | None] = mapped_column(Integer, nullable=True)
    end_month: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_pm: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=8, scale=2), nullable=True
    )
    objectives: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[WPStatus] = mapped_column(
        ENUM(WPStatus, name="wp_status_type", create_type=True),
        nullable=False,
        default=WPStatus.NOT_STARTED,
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="work_packages")
    lead_partner: Mapped["Partner | None"] = relationship("Partner", lazy="joined")
    deliverables: Mapped[list["Deliverable"]] = relationship(
        "Deliverable", back_populates="work_package", cascade="all, delete-orphan"
    )
    milestones: Mapped[list["Milestone"]] = relationship(
        "Milestone", back_populates="work_package", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<WorkPackage WP{self.wp_number}: {self.title}>"


class Deliverable(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """Deliverable produced by a work package."""

    __tablename__ = "deliverables"

    work_package_id: Mapped["uuid.UUID"] = mapped_column(
        UUID(as_uuid=True), ForeignKey("work_packages.id"), nullable=False, index=True
    )
    deliverable_number: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    type: Mapped[DeliverableType] = mapped_column(
        ENUM(DeliverableType, name="deliverable_type", create_type=True),
        nullable=False,
    )
    dissemination_level: Mapped[DisseminationLevel] = mapped_column(
        ENUM(DisseminationLevel, name="dissemination_level_type", create_type=True),
        nullable=False,
    )
    lead_partner_id: Mapped["uuid.UUID | None"] = mapped_column(
        UUID(as_uuid=True), ForeignKey("partners.id"), nullable=True
    )
    due_month: Mapped[int | None] = mapped_column(Integer, nullable=True)
    submission_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    ec_review_status: Mapped[ECReviewStatus] = mapped_column(
        ENUM(ECReviewStatus, name="ec_review_status_type", create_type=True),
        nullable=False,
        default=ECReviewStatus.PENDING,
    )
    traffic_light: Mapped[TrafficLight] = mapped_column(
        ENUM(TrafficLight, name="traffic_light_type", create_type=True),
        nullable=False,
        default=TrafficLight.GREEN,
    )
    file_reference: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    work_package: Mapped["WorkPackage"] = relationship(
        "WorkPackage", back_populates="deliverables"
    )
    lead_partner: Mapped["Partner | None"] = relationship("Partner", lazy="joined")

    def __repr__(self) -> str:
        return f"<Deliverable {self.deliverable_number}: {self.title}>"


class Milestone(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """Milestone checkpoint within a work package."""

    __tablename__ = "milestones"

    work_package_id: Mapped["uuid.UUID"] = mapped_column(
        UUID(as_uuid=True), ForeignKey("work_packages.id"), nullable=False, index=True
    )
    milestone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    due_month: Mapped[int | None] = mapped_column(Integer, nullable=True)
    verification_means: Mapped[str | None] = mapped_column(Text, nullable=True)
    achieved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    achievement_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Relationships
    work_package: Mapped["WorkPackage"] = relationship(
        "WorkPackage", back_populates="milestones"
    )

    def __repr__(self) -> str:
        return f"<Milestone {self.milestone_number}: {self.title}>"
