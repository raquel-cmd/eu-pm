"""Financial reporting models — Section 8.3 of the technical specification.

Covers Form C financial statements (8.3.1), WP completion declarations
for lump sum projects (8.3.2), and unit delivery records for unit cost
projects (8.3.3). Also includes institutional parallel reporting support (8.3.4).
"""

import uuid
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
from sqlalchemy.dialects.postgresql import ENUM, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import (
    CFSStatus,
    CompletionStatus,
    FinancialStatementStatus,
    UnitCostStatus,
    UnitType,
)


class FinancialStatement(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """Form C financial statement per partner per reporting period (Section 8.3.1).

    Tracks category-level costs (A-E), indirect costs at 25% flat rate,
    CFS requirement status, and partner sign-off / coordinator approval workflow.
    """

    __tablename__ = "financial_statements"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    reporting_period_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reporting_periods.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    partner_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("partners.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Status workflow
    status: Mapped[FinancialStatementStatus] = mapped_column(
        ENUM(
            FinancialStatementStatus,
            name="financial_statement_status_type",
            create_type=True,
        ),
        nullable=False,
        default=FinancialStatementStatus.DRAFT,
        index=True,
    )

    # Category breakdown (EC categories A-E)
    category_a_personnel: Mapped[Decimal] = mapped_column(
        Numeric(precision=15, scale=2), nullable=False, default=Decimal("0.00")
    )
    category_b_subcontracting: Mapped[Decimal] = mapped_column(
        Numeric(precision=15, scale=2), nullable=False, default=Decimal("0.00")
    )
    category_c_travel: Mapped[Decimal] = mapped_column(
        Numeric(precision=15, scale=2), nullable=False, default=Decimal("0.00")
    )
    category_d_equipment: Mapped[Decimal] = mapped_column(
        Numeric(precision=15, scale=2), nullable=False, default=Decimal("0.00")
    )
    category_e_other: Mapped[Decimal] = mapped_column(
        Numeric(precision=15, scale=2), nullable=False, default=Decimal("0.00")
    )

    # Calculated fields
    total_direct_costs: Mapped[Decimal] = mapped_column(
        Numeric(precision=15, scale=2), nullable=False, default=Decimal("0.00")
    )
    indirect_costs: Mapped[Decimal] = mapped_column(
        Numeric(precision=15, scale=2), nullable=False, default=Decimal("0.00")
    )
    total_eligible_costs: Mapped[Decimal] = mapped_column(
        Numeric(precision=15, scale=2), nullable=False, default=Decimal("0.00")
    )
    ec_contribution_requested: Mapped[Decimal] = mapped_column(
        Numeric(precision=15, scale=2), nullable=False, default=Decimal("0.00")
    )

    # CFS tracking (EUR 430k threshold)
    cumulative_claimed: Mapped[Decimal] = mapped_column(
        Numeric(precision=15, scale=2), nullable=False, default=Decimal("0.00")
    )
    cfs_required: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    cfs_status: Mapped[CFSStatus] = mapped_column(
        ENUM(CFSStatus, name="cfs_status_type", create_type=True),
        nullable=False,
        default=CFSStatus.NOT_REQUIRED,
    )

    # Approval workflow
    partner_signed_by: Mapped[str | None] = mapped_column(
        String(200), nullable=True
    )
    partner_signed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    coordinator_approved_by: Mapped[str | None] = mapped_column(
        String(200), nullable=True
    )
    coordinator_approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    reported_to_ec_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Institutional parallel reporting (Section 8.3.4)
    university_report_data: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True
    )
    discrepancies: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    project: Mapped["Project"] = relationship(  # noqa: F821
        "Project", back_populates="financial_statements"
    )
    reporting_period: Mapped["ReportingPeriod"] = relationship(  # noqa: F821
        "ReportingPeriod"
    )

    def __repr__(self) -> str:
        return (
            f"<FinancialStatement {self.status.value} "
            f"period={self.reporting_period_id}>"
        )


class WPCompletionDeclaration(
    UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base
):
    """WP completion declaration for lump sum projects (Section 8.3.2).

    Tracks WP-level completion status, evidence documents, and partial
    completion justification for lump sum cost model projects.
    """

    __tablename__ = "wp_completion_declarations"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    reporting_period_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reporting_periods.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    work_package_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("work_packages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    completion_status: Mapped[CompletionStatus] = mapped_column(
        ENUM(
            CompletionStatus,
            name="completion_status_type",
            create_type=True,
        ),
        nullable=False,
        default=CompletionStatus.NOT_STARTED,
    )
    completion_percentage: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    lump_sum_amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=15, scale=2), nullable=False, default=Decimal("0.00")
    )
    amount_claimed: Mapped[Decimal] = mapped_column(
        Numeric(precision=15, scale=2), nullable=False, default=Decimal("0.00")
    )

    # Evidence and justification
    evidence_documents: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    partial_completion_justification: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    deliverables_completed: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True
    )

    # Approval
    declared_by: Mapped[str | None] = mapped_column(String(200), nullable=True)
    declared_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    approved_by: Mapped[str | None] = mapped_column(String(200), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    project: Mapped["Project"] = relationship(  # noqa: F821
        "Project", back_populates="wp_completion_declarations"
    )
    work_package: Mapped["WorkPackage"] = relationship("WorkPackage")  # noqa: F821
    reporting_period: Mapped["ReportingPeriod"] = relationship(  # noqa: F821
        "ReportingPeriod"
    )

    def __repr__(self) -> str:
        return (
            f"<WPCompletionDeclaration WP={self.work_package_id} "
            f"{self.completion_status.value} {self.completion_percentage}%>"
        )


class UnitDeliveryRecord(
    UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base
):
    """Unit delivery tracking for unit cost projects (Section 8.3.3).

    Tracks unit type, planned/actual quantities, rate per unit,
    evidence of delivery, and approval status.
    """

    __tablename__ = "unit_delivery_records"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    reporting_period_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reporting_periods.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    work_package_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("work_packages.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    description: Mapped[str] = mapped_column(Text, nullable=False)
    unit_type: Mapped[UnitType] = mapped_column(
        ENUM(UnitType, name="unit_type_type", create_type=True),
        nullable=False,
    )
    planned_units: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2), nullable=False, default=Decimal("0.00")
    )
    actual_units: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2), nullable=False, default=Decimal("0.00")
    )
    unit_rate: Mapped[Decimal] = mapped_column(
        Numeric(precision=15, scale=2), nullable=False, default=Decimal("0.00")
    )
    total_cost: Mapped[Decimal] = mapped_column(
        Numeric(precision=15, scale=2), nullable=False, default=Decimal("0.00")
    )

    status: Mapped[UnitCostStatus] = mapped_column(
        ENUM(UnitCostStatus, name="unit_cost_status_type", create_type=True),
        nullable=False,
        default=UnitCostStatus.PLANNED,
    )

    # Evidence
    evidence_documents: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    evidence_description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Approval
    reported_by: Mapped[str | None] = mapped_column(String(200), nullable=True)
    reported_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    approved_by: Mapped[str | None] = mapped_column(String(200), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    project: Mapped["Project"] = relationship(  # noqa: F821
        "Project", back_populates="unit_delivery_records"
    )
    reporting_period: Mapped["ReportingPeriod"] = relationship(  # noqa: F821
        "ReportingPeriod"
    )

    def __repr__(self) -> str:
        return (
            f"<UnitDeliveryRecord {self.unit_type.value} "
            f"{self.actual_units}/{self.planned_units} @ {self.unit_rate}>"
        )
