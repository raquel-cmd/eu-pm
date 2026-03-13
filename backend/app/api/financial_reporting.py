"""API endpoints for cost-model-aware financial reporting (Section 8.3).

Provides endpoints for Form C financial statements, WP completion
declarations, unit delivery records, and cost-model-aware reports.
"""

import uuid
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.financial_reporting import (
    CostModelFinancialReport,
    FinancialStatementCreate,
    FinancialStatementListResponse,
    FinancialStatementResponse,
    FinancialStatementUpdate,
    FormCReport,
    InstitutionalReport,
    LumpSumReport,
    UnitCostReport,
    UnitDeliveryRecordCreate,
    UnitDeliveryRecordListResponse,
    UnitDeliveryRecordResponse,
    UnitDeliveryRecordUpdate,
    WPCompletionDeclarationCreate,
    WPCompletionDeclarationListResponse,
    WPCompletionDeclarationResponse,
    WPCompletionDeclarationUpdate,
)
from app.services.financial_reporting import (
    advance_financial_statement_status,
    create_unit_delivery_record,
    create_wp_completion_declaration,
    generate_financial_statement,
    generate_form_c_report,
    generate_institutional_report,
    generate_lump_sum_report,
    generate_unit_cost_report,
    get_cost_model_financial_report,
    get_financial_statement,
    list_financial_statements,
    list_unit_delivery_records,
    list_wp_completion_declarations,
    update_unit_delivery_record,
    update_wp_completion_declaration,
)

router = APIRouter(prefix="/api", tags=["financial-reporting"])


# --- Financial Statements (Form C) ---


@router.post(
    "/projects/{project_id}/financial-statements",
    response_model=FinancialStatementResponse,
    status_code=201,
)
async def create_financial_statement(
    project_id: uuid.UUID,
    body: FinancialStatementCreate,
    db: AsyncSession = Depends(get_db),
) -> FinancialStatementResponse:
    """Generate a Form C financial statement for a reporting period."""
    stmt = await generate_financial_statement(
        db, project_id, body.reporting_period_id, body.partner_id
    )
    await db.commit()
    await db.refresh(stmt)
    return FinancialStatementResponse.model_validate(stmt)


@router.get(
    "/projects/{project_id}/financial-statements",
    response_model=FinancialStatementListResponse,
)
async def get_financial_statements(
    project_id: uuid.UUID,
    reporting_period_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
) -> FinancialStatementListResponse:
    """List financial statements for a project."""
    items = await list_financial_statements(db, project_id, reporting_period_id)
    return FinancialStatementListResponse(
        items=[FinancialStatementResponse.model_validate(i) for i in items],
        total=len(items),
    )


@router.get(
    "/financial-statements/{statement_id}",
    response_model=FinancialStatementResponse,
)
async def get_financial_statement_detail(
    statement_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> FinancialStatementResponse:
    """Get a financial statement by ID."""
    stmt = await get_financial_statement(db, statement_id)
    return FinancialStatementResponse.model_validate(stmt)


@router.post(
    "/financial-statements/{statement_id}/advance",
    response_model=FinancialStatementResponse,
)
async def advance_statement(
    statement_id: uuid.UUID,
    actor: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> FinancialStatementResponse:
    """Advance the financial statement workflow."""
    stmt = await advance_financial_statement_status(db, statement_id, actor)
    await db.commit()
    await db.refresh(stmt)
    return FinancialStatementResponse.model_validate(stmt)


# --- WP Completion Declarations (Lump Sum) ---


@router.post(
    "/projects/{project_id}/wp-declarations",
    response_model=WPCompletionDeclarationResponse,
    status_code=201,
)
async def create_declaration(
    project_id: uuid.UUID,
    body: WPCompletionDeclarationCreate,
    db: AsyncSession = Depends(get_db),
) -> WPCompletionDeclarationResponse:
    """Create a WP completion declaration."""
    decl = await create_wp_completion_declaration(
        db,
        project_id,
        body.reporting_period_id,
        body.work_package_id,
        body.lump_sum_amount,
    )
    await db.commit()
    await db.refresh(decl)
    return WPCompletionDeclarationResponse.model_validate(decl)


@router.get(
    "/projects/{project_id}/wp-declarations",
    response_model=WPCompletionDeclarationListResponse,
)
async def get_declarations(
    project_id: uuid.UUID,
    reporting_period_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
) -> WPCompletionDeclarationListResponse:
    """List WP completion declarations for a project."""
    items = await list_wp_completion_declarations(
        db, project_id, reporting_period_id
    )
    return WPCompletionDeclarationListResponse(
        items=[
            WPCompletionDeclarationResponse.model_validate(i)
            for i in items
        ],
        total=len(items),
    )


@router.put(
    "/wp-declarations/{declaration_id}",
    response_model=WPCompletionDeclarationResponse,
)
async def update_declaration(
    declaration_id: uuid.UUID,
    body: WPCompletionDeclarationUpdate,
    db: AsyncSession = Depends(get_db),
) -> WPCompletionDeclarationResponse:
    """Update a WP completion declaration."""
    decl = await update_wp_completion_declaration(
        db, declaration_id, body.model_dump(exclude_unset=True)
    )
    await db.commit()
    await db.refresh(decl)
    return WPCompletionDeclarationResponse.model_validate(decl)


# --- Unit Delivery Records ---


@router.post(
    "/projects/{project_id}/unit-records",
    response_model=UnitDeliveryRecordResponse,
    status_code=201,
)
async def create_unit_record(
    project_id: uuid.UUID,
    body: UnitDeliveryRecordCreate,
    db: AsyncSession = Depends(get_db),
) -> UnitDeliveryRecordResponse:
    """Create a unit delivery record."""
    record = await create_unit_delivery_record(
        db, project_id, body.reporting_period_id, body.model_dump()
    )
    await db.commit()
    await db.refresh(record)
    return UnitDeliveryRecordResponse.model_validate(record)


@router.get(
    "/projects/{project_id}/unit-records",
    response_model=UnitDeliveryRecordListResponse,
)
async def get_unit_records(
    project_id: uuid.UUID,
    reporting_period_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
) -> UnitDeliveryRecordListResponse:
    """List unit delivery records for a project."""
    items = await list_unit_delivery_records(
        db, project_id, reporting_period_id
    )
    return UnitDeliveryRecordListResponse(
        items=[UnitDeliveryRecordResponse.model_validate(i) for i in items],
        total=len(items),
    )


@router.put(
    "/unit-records/{record_id}",
    response_model=UnitDeliveryRecordResponse,
)
async def update_unit_record(
    record_id: uuid.UUID,
    body: UnitDeliveryRecordUpdate,
    db: AsyncSession = Depends(get_db),
) -> UnitDeliveryRecordResponse:
    """Update a unit delivery record."""
    record = await update_unit_delivery_record(
        db, record_id, body.model_dump(exclude_unset=True)
    )
    await db.commit()
    await db.refresh(record)
    return UnitDeliveryRecordResponse.model_validate(record)


# --- Cost-Model-Aware Reports ---


@router.get(
    "/projects/{project_id}/financial-report",
    response_model=CostModelFinancialReport,
)
async def get_financial_report(
    project_id: uuid.UUID,
    reporting_period_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
) -> CostModelFinancialReport:
    """Get a cost-model-aware financial report for a project."""
    return await get_cost_model_financial_report(
        db, project_id, reporting_period_id
    )


@router.get(
    "/projects/{project_id}/form-c",
    response_model=FormCReport,
)
async def get_form_c(
    project_id: uuid.UUID,
    reporting_period_id: uuid.UUID = Query(...),
    partner_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
) -> FormCReport:
    """Generate a Form C report for an actual cost project."""
    return await generate_form_c_report(
        db, project_id, reporting_period_id, partner_id
    )


@router.get(
    "/projects/{project_id}/lump-sum-report",
    response_model=LumpSumReport,
)
async def get_lump_sum(
    project_id: uuid.UUID,
    reporting_period_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
) -> LumpSumReport:
    """Generate a lump sum report."""
    return await generate_lump_sum_report(db, project_id, reporting_period_id)


@router.get(
    "/projects/{project_id}/unit-cost-report",
    response_model=UnitCostReport,
)
async def get_unit_cost(
    project_id: uuid.UUID,
    reporting_period_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
) -> UnitCostReport:
    """Generate a unit cost report."""
    return await generate_unit_cost_report(
        db, project_id, reporting_period_id
    )


@router.get(
    "/projects/{project_id}/institutional-report",
    response_model=InstitutionalReport,
)
async def get_institutional(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> InstitutionalReport:
    """Generate the institutional parallel report."""
    return await generate_institutional_report(db, project_id)
