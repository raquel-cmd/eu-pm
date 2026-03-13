"""API endpoints for template library (Section 7).

Provides template browsing, field preview with auto-population,
document generation, and generated document management.
"""

import uuid

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.enums import GeneratedDocumentStatus, TemplateCategory
from app.schemas.template import (
    DocumentTemplateListResponse,
    DocumentTemplateResponse,
    GenerateDocumentRequest,
    GeneratedDocumentListResponse,
    GeneratedDocumentResponse,
    TemplatePreviewRequest,
    TemplatePreviewResponse,
)
from app.services.template_engine import (
    generate_document,
    generate_document_bytes,
    get_generated_document,
    get_template,
    list_generated_documents,
    list_templates,
    preview_template,
    seed_all_templates,
    update_document_status,
)

router = APIRouter(prefix="/api/templates", tags=["templates"])


# --- Template Library ---


@router.post("/seed", response_model=DocumentTemplateListResponse)
async def seed_templates(
    db: AsyncSession = Depends(get_db),
) -> DocumentTemplateListResponse:
    """Seed all built-in templates into the database."""
    created = await seed_all_templates(db)
    await db.commit()
    all_templates = await list_templates(db)
    return DocumentTemplateListResponse(
        items=[
            DocumentTemplateResponse.model_validate(t)
            for t in all_templates
        ],
        total=len(all_templates),
    )


@router.get("", response_model=DocumentTemplateListResponse)
async def get_templates(
    category: TemplateCategory | None = None,
    db: AsyncSession = Depends(get_db),
) -> DocumentTemplateListResponse:
    """List all templates, optionally filtered by category."""
    items = await list_templates(db, category)
    return DocumentTemplateListResponse(
        items=[
            DocumentTemplateResponse.model_validate(t) for t in items
        ],
        total=len(items),
    )


@router.get("/{template_id}", response_model=DocumentTemplateResponse)
async def get_template_detail(
    template_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> DocumentTemplateResponse:
    """Get a template by ID."""
    template = await get_template(db, template_id)
    return DocumentTemplateResponse.model_validate(template)


@router.post(
    "/{template_id}/preview",
    response_model=TemplatePreviewResponse,
)
async def preview_template_fields(
    template_id: uuid.UUID,
    body: TemplatePreviewRequest,
    db: AsyncSession = Depends(get_db),
) -> TemplatePreviewResponse:
    """Preview template fields with auto-populated values."""
    return await preview_template(
        db, template_id, body.project_id, body.researcher_id
    )


# --- Document Generation ---


@router.post(
    "/generate",
    response_model=GeneratedDocumentResponse,
    status_code=201,
)
async def generate_doc(
    body: GenerateDocumentRequest,
    db: AsyncSession = Depends(get_db),
) -> GeneratedDocumentResponse:
    """Generate a DOCX document from a template and save to filesystem."""
    doc = await generate_document(
        db,
        body.template_id,
        body.project_id,
        body.researcher_id,
        body.manual_fields,
        body.generated_by,
    )
    await db.commit()
    await db.refresh(doc)
    return GeneratedDocumentResponse.model_validate(doc)


@router.post("/{template_id}/download")
async def download_document(
    template_id: uuid.UUID,
    body: TemplatePreviewRequest,
    manual_fields: dict | None = None,
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """Generate and stream a DOCX document for download."""
    buf, filename = await generate_document_bytes(
        db, template_id, body.project_id, body.researcher_id,
        manual_fields,
    )
    return StreamingResponse(
        buf,
        media_type=(
            "application/vnd.openxmlformats-officedocument"
            ".wordprocessingml.document"
        ),
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        },
    )


# --- Generated Documents ---


@router.get(
    "/documents/list",
    response_model=GeneratedDocumentListResponse,
)
async def get_generated_docs(
    template_id: uuid.UUID | None = None,
    project_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
) -> GeneratedDocumentListResponse:
    """List generated documents."""
    items = await list_generated_documents(db, template_id, project_id)
    return GeneratedDocumentListResponse(
        items=[
            GeneratedDocumentResponse.model_validate(d) for d in items
        ],
        total=len(items),
    )


@router.get(
    "/documents/{doc_id}",
    response_model=GeneratedDocumentResponse,
)
async def get_generated_doc(
    doc_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> GeneratedDocumentResponse:
    """Get a generated document by ID."""
    doc = await get_generated_document(db, doc_id)
    return GeneratedDocumentResponse.model_validate(doc)


@router.put(
    "/documents/{doc_id}/status",
    response_model=GeneratedDocumentResponse,
)
async def update_doc_status(
    doc_id: uuid.UUID,
    status: GeneratedDocumentStatus = Query(...),
    db: AsyncSession = Depends(get_db),
) -> GeneratedDocumentResponse:
    """Update the status of a generated document."""
    doc = await update_document_status(db, doc_id, status)
    await db.commit()
    await db.refresh(doc)
    return GeneratedDocumentResponse.model_validate(doc)
