"""Pydantic schemas for template library (Section 7)."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import (
    GeneratedDocumentStatus,
    PersonnelTemplateType,
    TemplateCategory,
)


# --- Template Field Definitions ---


class TemplateFieldDef(BaseModel):
    """Definition of a single field in a template."""

    name: str
    label: str
    field_type: str  # "auto", "manual", "conditional"
    data_type: str = "text"  # "text", "date", "decimal", "integer", "boolean"
    data_source: str | None = None  # e.g. "project.acronym"
    required: bool = True
    default_value: str | None = None
    validation_rule: str | None = None
    help_text: str | None = None


class ConditionalSectionDef(BaseModel):
    """Definition of a conditional section in a template."""

    section_name: str
    condition_field: str  # e.g. "project.cost_model"
    condition_value: str  # e.g. "ACTUAL_COSTS"
    condition_operator: str = "eq"  # "eq", "neq", "in"
    content_label: str = ""


# --- Document Template ---


class DocumentTemplateCreate(BaseModel):
    """Create a document template."""

    name: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    category: TemplateCategory
    personnel_type: PersonnelTemplateType | None = None
    field_definitions: dict = Field(default_factory=dict)
    conditional_sections: dict | None = None
    supported_cost_models: dict | None = None
    supported_programmes: dict | None = None


class DocumentTemplateResponse(BaseModel):
    """Response for a document template."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    description: str | None
    category: TemplateCategory
    personnel_type: PersonnelTemplateType | None
    version: int
    field_definitions: dict
    conditional_sections: dict | None
    supported_cost_models: dict | None
    supported_programmes: dict | None
    created_at: datetime
    updated_at: datetime


class DocumentTemplateListResponse(BaseModel):
    """List of document templates."""

    items: list[DocumentTemplateResponse]
    total: int


# --- Generated Document ---


class GenerateDocumentRequest(BaseModel):
    """Request to generate a document from a template."""

    template_id: uuid.UUID
    project_id: uuid.UUID | None = None
    researcher_id: uuid.UUID | None = None
    manual_fields: dict = Field(default_factory=dict)
    generated_by: str | None = None


class GeneratedDocumentResponse(BaseModel):
    """Response for a generated document."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    template_id: uuid.UUID
    project_id: uuid.UUID | None
    researcher_id: uuid.UUID | None
    template_version: int
    generated_by: str | None
    generated_at: datetime
    input_data: dict
    file_path: str | None
    file_name: str
    status: GeneratedDocumentStatus
    notes: str | None
    created_at: datetime
    updated_at: datetime


class GeneratedDocumentListResponse(BaseModel):
    """List of generated documents."""

    items: list[GeneratedDocumentResponse]
    total: int


# --- Template Preview ---


class TemplatePreviewRequest(BaseModel):
    """Request a preview of auto-populated fields for a template."""

    project_id: uuid.UUID | None = None
    researcher_id: uuid.UUID | None = None


class TemplateFieldPreview(BaseModel):
    """Preview of a single field with auto-populated value."""

    name: str
    label: str
    field_type: str
    data_type: str
    value: str | None = None
    required: bool = True
    help_text: str | None = None


class TemplatePreviewResponse(BaseModel):
    """Preview of all fields with auto-populated values filled in."""

    template_id: uuid.UUID
    template_name: str
    template_version: int
    fields: list[TemplateFieldPreview]
    conditional_sections_active: list[str] = []
