"""Financial models — Section 4 of the technical specification.

Covers expenses (4.2), budget category mappings (4.1),
fund distributions (4.4), missions (4.5), and procurements (4.6).
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
    ApprovalStatus,
    ECBudgetCategory,
    ExpenseStatus,
    MissionPurpose,
    ProcurementApprovalStatus,
    ProcurementMethod,
    UniversityThreshold,
)


class BudgetCategoryMapping(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Configurable mapping between EC budget categories and university
    account codes (Section 4.1 dual accounting view)."""

    __tablename__ = "budget_category_mappings"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ec_category: Mapped[ECBudgetCategory] = mapped_column(
        ENUM(ECBudgetCategory, name="ec_budget_category_type", create_type=True),
        nullable=False,
    )
    university_account_code: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    university_category_name: Mapped[str | None] = mapped_column(
        String(200), nullable=True
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    project: Mapped["Project"] = relationship(  # noqa: F821
        "Project", back_populates="budget_category_mappings"
    )

    def __repr__(self) -> str:
        return (
            f"<BudgetCategoryMapping {self.ec_category.value} -> "
            f"{self.university_account_code}>"
        )


class Expense(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """Expense tracking entity (Section 4.2).

    Supports dual-view accounting: ec_category for EC reporting,
    university_account_code for internal reporting.
    Cost-model-aware: validation behavior varies by project cost model.
    """

    __tablename__ = "expenses"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    work_package_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("work_packages.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    partner_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("partners.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Dual-view fields
    ec_category: Mapped[ECBudgetCategory | None] = mapped_column(
        ENUM(ECBudgetCategory, name="ec_budget_category_type", create_type=False),
        nullable=True,
    )
    university_account_code: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    description: Mapped[str] = mapped_column(Text, nullable=False)
    amount_gross: Mapped[Decimal] = mapped_column(
        Numeric(precision=15, scale=2), nullable=False
    )
    amount_net: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=15, scale=2), nullable=True
    )
    vat_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=15, scale=2), nullable=True
    )
    currency: Mapped[str] = mapped_column(
        String(3), nullable=False, default="EUR"
    )
    exchange_rate: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=12, scale=6), nullable=True
    )
    amount_eur: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=15, scale=2), nullable=True
    )
    date_incurred: Mapped[date] = mapped_column(Date, nullable=False)
    reporting_period_id: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    status: Mapped[ExpenseStatus] = mapped_column(
        ENUM(ExpenseStatus, name="expense_status_type", create_type=True),
        nullable=False,
        default=ExpenseStatus.DRAFT,
        index=True,
    )
    ec_eligible: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )
    supporting_docs: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    project: Mapped["Project"] = relationship(  # noqa: F821
        "Project", back_populates="expenses"
    )

    def __repr__(self) -> str:
        return f"<Expense {self.description[:30]} EUR {self.amount_gross}>"


class Mission(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """Mission/travel record (Section 4.5).

    Tracks travel costs with full documentation for actual costs projects,
    simplified tracking for lump sum projects.
    """

    __tablename__ = "missions"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    work_package_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("work_packages.id", ondelete="SET NULL"),
        nullable=True,
    )
    researcher_name: Mapped[str] = mapped_column(String(200), nullable=False)
    purpose: Mapped[MissionPurpose] = mapped_column(
        ENUM(MissionPurpose, name="mission_purpose_type", create_type=True),
        nullable=False,
    )
    destination: Mapped[str] = mapped_column(String(200), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    approval_status: Mapped[ApprovalStatus] = mapped_column(
        ENUM(ApprovalStatus, name="approval_status_type", create_type=True),
        nullable=False,
        default=ApprovalStatus.REQUESTED,
    )
    travel_costs: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=15, scale=2), nullable=True
    )
    accommodation_costs: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=15, scale=2), nullable=True
    )
    subsistence: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=15, scale=2), nullable=True
    )
    registration_fees: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=15, scale=2), nullable=True
    )
    other_costs: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=15, scale=2), nullable=True
    )
    total_cost: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=15, scale=2), nullable=True
    )
    currency: Mapped[str] = mapped_column(
        String(3), nullable=False, default="EUR"
    )
    amount_eur: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=15, scale=2), nullable=True
    )
    ec_eligible: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )
    supporting_docs: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    university_travel_order: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    # Workflow fields
    estimated_total_cost: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=15, scale=2), nullable=True
    )
    actual_total_cost: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=15, scale=2), nullable=True
    )
    is_international: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    requires_central_approval: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    approved_by_pi_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    approved_centrally_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    reconciliation_notes: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    actual_receipts: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True
    )

    # Relationships
    project: Mapped["Project"] = relationship(  # noqa: F821
        "Project", back_populates="missions"
    )

    def __repr__(self) -> str:
        return (
            f"<Mission {self.researcher_name} -> {self.destination} "
            f"({self.start_date})>"
        )


class Procurement(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """Equipment and other costs procurement (Section 4.6)."""

    __tablename__ = "procurements"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    work_package_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("work_packages.id", ondelete="SET NULL"),
        nullable=True,
    )
    ec_category: Mapped[ECBudgetCategory | None] = mapped_column(
        ENUM(ECBudgetCategory, name="ec_budget_category_type", create_type=False),
        nullable=True,
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    estimated_cost: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=15, scale=2), nullable=True
    )
    actual_cost: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=15, scale=2), nullable=True
    )
    supplier: Mapped[str | None] = mapped_column(String(300), nullable=True)
    procurement_method: Mapped[ProcurementMethod | None] = mapped_column(
        ENUM(
            ProcurementMethod,
            name="procurement_method_type",
            create_type=True,
        ),
        nullable=True,
    )
    university_threshold: Mapped[UniversityThreshold | None] = mapped_column(
        ENUM(
            UniversityThreshold,
            name="university_threshold_type",
            create_type=True,
        ),
        nullable=True,
    )
    depreciation_applicable: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    depreciation_rate: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=5, scale=2), nullable=True
    )
    eligible_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=15, scale=2), nullable=True
    )
    purchase_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    invoice_reference: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    supporting_docs: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    approval_status: Mapped[ProcurementApprovalStatus] = mapped_column(
        ENUM(
            ProcurementApprovalStatus,
            name="procurement_approval_status_type",
            create_type=True,
        ),
        nullable=False,
        default=ProcurementApprovalStatus.REQUESTED,
    )

    # Relationships
    project: Mapped["Project"] = relationship(  # noqa: F821
        "Project", back_populates="procurements"
    )

    def __repr__(self) -> str:
        return f"<Procurement {self.description[:30]}>"


class FundDistribution(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Coordinator fund distribution tracking (Section 4.4).

    Tracks the flow of funds from EC through to partners:
    pre-financing, distributions, interim/final payments.
    """

    __tablename__ = "fund_distributions"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    partner_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("partners.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    distribution_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # pre_financing, distribution, interim_payment, final_payment, retention
    amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=15, scale=2), nullable=False
    )
    currency: Mapped[str] = mapped_column(
        String(3), nullable=False, default="EUR"
    )
    distribution_date: Mapped[date] = mapped_column(Date, nullable=False)
    bank_transfer_reference: Mapped[str | None] = mapped_column(
        String(200), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    project: Mapped["Project"] = relationship(  # noqa: F821
        "Project", back_populates="fund_distributions"
    )

    def __repr__(self) -> str:
        return (
            f"<FundDistribution {self.distribution_type} "
            f"EUR {self.amount}>"
        )
