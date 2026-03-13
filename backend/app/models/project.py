"""Project model — Section 3.1 of the technical specification."""

from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import ENUM, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import CostModel, Programme, ProjectRole, ProjectStatus


class Project(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """Central entity capturing all grant agreement metadata."""

    __tablename__ = "projects"

    acronym: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    full_title: Mapped[str] = mapped_column(String(500), nullable=False)
    grant_agreement_number: Mapped[str | None] = mapped_column(
        String(50), nullable=True, unique=True
    )
    programme: Mapped[Programme] = mapped_column(
        ENUM(Programme, name="programme_type", create_type=True),
        nullable=False,
        index=True,
    )
    call_identifier: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cost_model: Mapped[CostModel] = mapped_column(
        ENUM(CostModel, name="cost_model_type", create_type=True),
        nullable=False,
        index=True,
    )
    role: Mapped[ProjectRole] = mapped_column(
        ENUM(ProjectRole, name="project_role_type", create_type=True),
        nullable=False,
        index=True,
    )
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    duration_months: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_budget: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=15, scale=2), nullable=True
    )
    eu_contribution: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=15, scale=2), nullable=True
    )
    funding_rate: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=5, scale=2), nullable=True
    )
    reporting_periods: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[ProjectStatus] = mapped_column(
        ENUM(ProjectStatus, name="project_status_type", create_type=True),
        nullable=False,
        default=ProjectStatus.PROPOSAL,
        index=True,
    )
    ec_project_officer: Mapped[str | None] = mapped_column(String(200), nullable=True)
    internal_cost_center: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )

    # Relationships
    project_partners: Mapped[list["ProjectPartner"]] = relationship(
        "ProjectPartner", back_populates="project", cascade="all, delete-orphan"
    )
    work_packages: Mapped[list["WorkPackage"]] = relationship(
        "WorkPackage", back_populates="project", cascade="all, delete-orphan"
    )
    expenses: Mapped[list["Expense"]] = relationship(
        "Expense", back_populates="project", cascade="all, delete-orphan"
    )
    missions: Mapped[list["Mission"]] = relationship(
        "Mission", back_populates="project", cascade="all, delete-orphan"
    )
    procurements: Mapped[list["Procurement"]] = relationship(
        "Procurement", back_populates="project", cascade="all, delete-orphan"
    )
    budget_category_mappings: Mapped[list["BudgetCategoryMapping"]] = relationship(
        "BudgetCategoryMapping",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    fund_distributions: Mapped[list["FundDistribution"]] = relationship(
        "FundDistribution",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    report_periods: Mapped[list["ReportingPeriod"]] = relationship(
        "ReportingPeriod",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    risks: Mapped[list["Risk"]] = relationship(
        "Risk",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    financial_statements: Mapped[list["FinancialStatement"]] = relationship(
        "FinancialStatement",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    wp_completion_declarations: Mapped[list["WPCompletionDeclaration"]] = relationship(
        "WPCompletionDeclaration",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    unit_delivery_records: Mapped[list["UnitDeliveryRecord"]] = relationship(
        "UnitDeliveryRecord",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    ip_assets: Mapped[list["IPAsset"]] = relationship(
        "IPAsset",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    dissemination_activities: Mapped[list["DisseminationActivity"]] = relationship(
        "DisseminationActivity",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    kpi_values: Mapped[list["KPIValue"]] = relationship(
        "KPIValue",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    ethics_requirements: Mapped[list["EthicsRequirement"]] = relationship(
        "EthicsRequirement",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    data_management_records: Mapped[list["DataManagementRecord"]] = relationship(
        "DataManagementRecord",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    amendments: Mapped[list["Amendment"]] = relationship(
        "Amendment",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Project {self.acronym} ({self.status.value})>"
