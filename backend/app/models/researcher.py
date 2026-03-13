"""Researcher, effort allocation, and timesheet models — Section 5 of the spec.

Covers researcher profiles (5.1), effort allocations (5.2),
and timesheet entries (5.3) for person-month tracking.
"""

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import ContractType, ResearcherPosition


class Researcher(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """A researcher who can be allocated to projects and log timesheets."""

    __tablename__ = "researchers"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str | None] = mapped_column(String(200), unique=True, nullable=True)
    position: Mapped[ResearcherPosition] = mapped_column(
        ENUM(ResearcherPosition, name="researcherposition", create_type=False),
        nullable=False,
    )
    contract_type: Mapped[ContractType] = mapped_column(
        ENUM(ContractType, name="contracttype", create_type=False),
        nullable=False,
    )
    fte: Mapped[Decimal] = mapped_column(Numeric(3, 2), nullable=False, default=Decimal("1.00"))
    annual_gross_cost: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    productive_hours: Mapped[int] = mapped_column(Integer, nullable=False, default=1720)
    hourly_rate: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Relationships
    effort_allocations: Mapped[list["EffortAllocation"]] = relationship(
        back_populates="researcher", cascade="all, delete-orphan"
    )
    timesheet_entries: Mapped[list["TimesheetEntry"]] = relationship(
        back_populates="researcher", cascade="all, delete-orphan"
    )


class EffortAllocation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Planned person-month allocation for a researcher on a project/WP."""

    __tablename__ = "effort_allocations"
    __table_args__ = (
        UniqueConstraint(
            "researcher_id", "project_id", "work_package_id", "period_start",
            name="uq_effort_allocation_researcher_project_wp_period",
        ),
    )

    researcher_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("researchers.id"), nullable=False, index=True
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True
    )
    work_package_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("work_packages.id"), nullable=True
    )
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    planned_pm: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    planned_fte_percentage: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    researcher: Mapped["Researcher"] = relationship(back_populates="effort_allocations")
    project: Mapped["Project"] = relationship()  # noqa: F821
    work_package: Mapped["WorkPackage | None"] = relationship()  # noqa: F821


class TimesheetEntry(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Actual hours logged by a researcher on a project/WP on a given day."""

    __tablename__ = "timesheet_entries"
    __table_args__ = (
        UniqueConstraint(
            "researcher_id", "project_id", "work_package_id", "date",
            name="uq_timesheet_entry_researcher_project_wp_date",
        ),
    )

    researcher_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("researchers.id"), nullable=False, index=True
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True
    )
    work_package_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("work_packages.id"), nullable=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    hours: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    researcher: Mapped["Researcher"] = relationship(back_populates="timesheet_entries")
    project: Mapped["Project"] = relationship()  # noqa: F821
    work_package: Mapped["WorkPackage | None"] = relationship()  # noqa: F821
