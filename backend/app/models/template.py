"""Template library models — Section 7 of the technical specification.

Stores template definitions with versioned schemas, field definitions,
conditional sections, and generated document records.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ENUM, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import (
    GeneratedDocumentStatus,
    PersonnelTemplateType,
    TemplateCategory,
)


class DocumentTemplate(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A document template definition with versioned schema.

    Stores the template metadata, field definitions, conditional logic,
    and DOCX generation configuration. Templates are versioned: each
    schema change increments the version.
    """

    __tablename__ = "document_templates"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True, index=True
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[TemplateCategory] = mapped_column(
        ENUM(
            TemplateCategory,
            name="template_category_type",
            create_type=True,
        ),
        nullable=False,
        index=True,
    )
    personnel_type: Mapped[PersonnelTemplateType | None] = mapped_column(
        ENUM(
            PersonnelTemplateType,
            name="personnel_template_type",
            create_type=True,
        ),
        nullable=True,
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Field definitions stored as JSONB
    # Structure: list of field dicts with keys:
    #   name, label, field_type (auto|manual|conditional),
    #   data_source (for auto fields), validation (for manual),
    #   condition (for conditional sections)
    field_definitions: Mapped[dict] = mapped_column(
        JSONB, nullable=False, default=dict
    )

    # Conditional sections configuration
    # Keys: section_name -> {condition_field, condition_value, content}
    conditional_sections: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True
    )

    # Supported cost models, programmes, roles (filters)
    supported_cost_models: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True
    )
    supported_programmes: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True
    )

    # Relationships
    generated_documents: Mapped[list["GeneratedDocument"]] = relationship(
        "GeneratedDocument",
        back_populates="template",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<DocumentTemplate {self.slug} v{self.version}>"


class GeneratedDocument(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A document generated from a template.

    Tracks the template version used, input data, generated file path,
    and approval status for audit traceability.
    """

    __tablename__ = "generated_documents"

    template_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("document_templates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    researcher_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("researchers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    template_version: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    generated_by: Mapped[str | None] = mapped_column(
        String(200), nullable=True
    )
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # Input data snapshot (all field values at generation time)
    input_data: Mapped[dict] = mapped_column(
        JSONB, nullable=False, default=dict
    )

    # Output file path
    file_path: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )
    file_name: Mapped[str] = mapped_column(
        String(200), nullable=False
    )

    status: Mapped[GeneratedDocumentStatus] = mapped_column(
        ENUM(
            GeneratedDocumentStatus,
            name="generated_document_status_type",
            create_type=True,
        ),
        nullable=False,
        default=GeneratedDocumentStatus.DRAFT,
        index=True,
    )

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    template: Mapped["DocumentTemplate"] = relationship(
        "DocumentTemplate", back_populates="generated_documents"
    )

    def __repr__(self) -> str:
        return (
            f"<GeneratedDocument {self.file_name} "
            f"({self.status.value})>"
        )
