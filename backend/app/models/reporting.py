"""Reporting models — Section 8 of the technical specification.

Includes ReportingPeriod, TechnicalReport, ReportSection, Risk,
and ReportReminder for the reporting and compliance engine.
"""

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ENUM, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import (
    ReminderType,
    ReportingPeriodType,
    ReportSectionStatus,
    ReportSectionType,
    ReportStatus,
    RiskCategory,
    RiskLevel,
    RiskStatus,
)


class ReportingPeriod(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """A reporting period derived from grant agreement data."""

    __tablename__ = "reporting_periods"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True
    )
    period_number: Mapped[int] = mapped_column(Integer, nullable=False)
    period_type: Mapped[ReportingPeriodType] = mapped_column(
        ENUM(
            ReportingPeriodType,
            name="reporting_period_type",
            create_type=True,
        ),
        nullable=False,
        default=ReportingPeriodType.PERIODIC,
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    technical_report_deadline: Mapped[date] = mapped_column(Date, nullable=False)
    financial_report_deadline: Mapped[date | None] = mapped_column(
        Date, nullable=True
    )
    review_meeting_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="report_periods")
    technical_reports: Mapped[list["TechnicalReport"]] = relationship(
        "TechnicalReport", back_populates="reporting_period", cascade="all, delete-orphan"
    )
    reminders: Mapped[list["ReportReminder"]] = relationship(
        "ReportReminder", back_populates="reporting_period", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<ReportingPeriod P{self.period_number} "
            f"({self.start_date} - {self.end_date})>"
        )


class TechnicalReport(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """A technical report for a reporting period."""

    __tablename__ = "technical_reports"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True
    )
    reporting_period_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reporting_periods.id"),
        nullable=False,
        index=True,
    )
    report_type: Mapped[ReportingPeriodType] = mapped_column(
        ENUM(
            ReportingPeriodType,
            name="reporting_period_type",
            create_type=False,
        ),
        nullable=False,
        default=ReportingPeriodType.PERIODIC,
    )
    status: Mapped[ReportStatus] = mapped_column(
        ENUM(ReportStatus, name="report_status_type", create_type=True),
        nullable=False,
        default=ReportStatus.DRAFT,
        index=True,
    )
    part_a_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_by: Mapped[str | None] = mapped_column(String(200), nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    ec_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    project: Mapped["Project"] = relationship("Project")
    reporting_period: Mapped["ReportingPeriod"] = relationship(
        "ReportingPeriod", back_populates="technical_reports"
    )
    sections: Mapped[list["ReportSection"]] = relationship(
        "ReportSection", back_populates="technical_report", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<TechnicalReport {self.status.value} for period {self.reporting_period_id}>"


class ReportSection(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A section within a technical report (Part B1-B4)."""

    __tablename__ = "report_sections"

    technical_report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("technical_reports.id"),
        nullable=False,
        index=True,
    )
    section_type: Mapped[ReportSectionType] = mapped_column(
        ENUM(
            ReportSectionType,
            name="report_section_type",
            create_type=True,
        ),
        nullable=False,
    )
    work_package_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("work_packages.id"), nullable=True
    )
    content: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    narrative: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ReportSectionStatus] = mapped_column(
        ENUM(
            ReportSectionStatus,
            name="report_section_status_type",
            create_type=True,
        ),
        nullable=False,
        default=ReportSectionStatus.DRAFT,
    )
    assigned_to: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # Relationships
    technical_report: Mapped["TechnicalReport"] = relationship(
        "TechnicalReport", back_populates="sections"
    )

    def __repr__(self) -> str:
        return f"<ReportSection {self.section_type.value} ({self.status.value})>"


class Risk(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """A project risk for the risk register."""

    __tablename__ = "risks"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True
    )
    work_package_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("work_packages.id"), nullable=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[RiskCategory] = mapped_column(
        ENUM(RiskCategory, name="risk_category_type", create_type=True),
        nullable=False,
    )
    probability: Mapped[RiskLevel] = mapped_column(
        ENUM(RiskLevel, name="risk_level_type", create_type=True),
        nullable=False,
    )
    impact: Mapped[RiskLevel] = mapped_column(
        ENUM(RiskLevel, name="risk_level_type", create_type=False),
        nullable=False,
    )
    mitigation_strategy: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner: Mapped[str | None] = mapped_column(String(200), nullable=True)
    status: Mapped[RiskStatus] = mapped_column(
        ENUM(RiskStatus, name="risk_status_type", create_type=True),
        nullable=False,
        default=RiskStatus.OPEN,
    )
    actions_taken: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="risks")

    def __repr__(self) -> str:
        return f"<Risk {self.category.value}: {self.description[:40]}>"


class ReportReminder(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """An automated reminder for a reporting deadline."""

    __tablename__ = "report_reminders"

    reporting_period_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reporting_periods.id"),
        nullable=False,
        index=True,
    )
    reminder_type: Mapped[ReminderType] = mapped_column(
        ENUM(ReminderType, name="reminder_type", create_type=True),
        nullable=False,
    )
    scheduled_date: Mapped[date] = mapped_column(Date, nullable=False)
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    recipient_description: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )

    # Relationships
    reporting_period: Mapped["ReportingPeriod"] = relationship(
        "ReportingPeriod", back_populates="reminders"
    )

    def __repr__(self) -> str:
        sent = "sent" if self.sent_at else "pending"
        return f"<ReportReminder {self.reminder_type.value} ({sent})>"
