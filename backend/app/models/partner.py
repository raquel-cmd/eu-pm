"""Partner and ProjectPartner models — Section 3.2 of the technical specification."""

import uuid
from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import OrgType


class Partner(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """Organization that participates in one or more projects."""

    __tablename__ = "partners"

    pic_number: Mapped[str | None] = mapped_column(
        String(20), nullable=True, unique=True
    )
    legal_name: Mapped[str] = mapped_column(String(500), nullable=False)
    short_name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    org_type: Mapped[OrgType | None] = mapped_column(
        ENUM(OrgType, name="org_type", create_type=True), nullable=True
    )
    is_sme: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    contact_person: Mapped[str | None] = mapped_column(String(500), nullable=True)
    bank_account_validated: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    accession_form_signed: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # Relationships
    project_partners: Mapped[list["ProjectPartner"]] = relationship(
        "ProjectPartner", back_populates="partner", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Partner {self.short_name}>"


class ProjectPartner(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Many-to-many link between projects and partners with per-project data."""

    __tablename__ = "project_partners"

    project_id: Mapped["uuid.UUID"] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True
    )
    partner_id: Mapped["uuid.UUID"] = mapped_column(
        UUID(as_uuid=True), ForeignKey("partners.id"), nullable=False, index=True
    )
    partner_budget: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=15, scale=2), nullable=True
    )
    partner_eu_contribution: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=15, scale=2), nullable=True
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="project_partners")
    partner: Mapped["Partner"] = relationship("Partner", back_populates="project_partners")

    def __repr__(self) -> str:
        return f"<ProjectPartner project={self.project_id} partner={self.partner_id}>"
