"""Service layer for cost-model-aware financial reporting (Section 8.3).

Handles Form C generation (actual costs), WP completion declarations
(lump sum), unit delivery tracking (unit costs), and institutional
parallel reporting (EC-to-university mapping).
"""

import uuid
from datetime import date, datetime, timezone
from decimal import ROUND_HALF_UP, Decimal

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import (
    CFSStatus,
    CompletionStatus,
    CostModel,
    ECBudgetCategory,
    FinancialStatementStatus,
    UnitCostStatus,
)
from app.models.financial import BudgetCategoryMapping, Expense, Mission
from app.models.financial_reporting import (
    FinancialStatement,
    UnitDeliveryRecord,
    WPCompletionDeclaration,
)
from app.models.project import Project
from app.models.reporting import ReportingPeriod
from app.schemas.financial_reporting import (
    CategoryBreakdownRow,
    CostModelFinancialReport,
    FinancialStatementResponse,
    FormCReport,
    InstitutionalMappingRow,
    InstitutionalReport,
    LumpSumReport,
    UnitCostReport,
    UnitDeliveryRecordResponse,
    WPCompletionDeclarationResponse,
)

ZERO = Decimal("0.00")
INDIRECT_RATE = Decimal("0.25")
CFS_THRESHOLD = Decimal("430000.00")

INDIRECT_BASE_CATEGORIES = {
    ECBudgetCategory.A_PERSONNEL,
    ECBudgetCategory.C1_TRAVEL,
    ECBudgetCategory.C2_EQUIPMENT,
    ECBudgetCategory.C3_OTHER_GOODS,
    ECBudgetCategory.D_OTHER_COSTS,
}


def _q(value: Decimal | int | float | None) -> Decimal:
    """Quantize a decimal to 2 places, treating None as zero."""
    if value is None:
        return ZERO
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# --- Financial Statement (Form C) CRUD ---


async def generate_financial_statement(
    db: AsyncSession,
    project_id: uuid.UUID,
    reporting_period_id: uuid.UUID,
    partner_id: uuid.UUID | None = None,
) -> FinancialStatement:
    """Generate a Form C financial statement from expense data."""
    project = await _get_project(db, project_id)
    period = await _get_period(db, reporting_period_id)

    # Check for duplicate
    dup_stmt = select(FinancialStatement).where(
        FinancialStatement.project_id == project_id,
        FinancialStatement.reporting_period_id == reporting_period_id,
        FinancialStatement.partner_id == partner_id,
        FinancialStatement.deleted_at.is_(None),
    )
    existing = (await db.execute(dup_stmt)).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=409,
            detail="Financial statement already exists for this period/partner",
        )

    # Aggregate expenses by EC category for this period and partner
    cat_totals = await _get_category_totals(
        db, project_id, period.start_date, period.end_date, partner_id
    )

    cat_a = cat_totals.get(ECBudgetCategory.A_PERSONNEL, ZERO)
    cat_b = cat_totals.get(ECBudgetCategory.B_SUBCONTRACTING, ZERO)
    cat_c = (
        cat_totals.get(ECBudgetCategory.C1_TRAVEL, ZERO)
        + cat_totals.get(ECBudgetCategory.C2_EQUIPMENT, ZERO)
        + cat_totals.get(ECBudgetCategory.C3_OTHER_GOODS, ZERO)
    )
    cat_d = cat_totals.get(ECBudgetCategory.D_OTHER_COSTS, ZERO)
    cat_e = cat_totals.get(ECBudgetCategory.E_INDIRECT, ZERO)

    total_direct = cat_a + cat_b + cat_c + cat_d + cat_e

    # Indirect costs: 25% on A + C + D (excluding B)
    indirect_base = sum(
        cat_totals.get(cat, ZERO)
        for cat in INDIRECT_BASE_CATEGORIES
    )
    indirect = _q(indirect_base * INDIRECT_RATE)

    total_eligible = total_direct + indirect

    # EC contribution requested based on funding rate
    funding_rate = _q(project.funding_rate) if project.funding_rate else ZERO
    ec_requested = _q(total_eligible * funding_rate / Decimal("100")) if funding_rate > ZERO else total_eligible

    # CFS: check cumulative claims
    cum_stmt = select(
        func.coalesce(func.sum(FinancialStatement.total_eligible_costs), 0)
    ).where(
        FinancialStatement.project_id == project_id,
        FinancialStatement.partner_id == partner_id,
        FinancialStatement.deleted_at.is_(None),
    )
    prev_cumulative = _q((await db.execute(cum_stmt)).scalar_one())
    cumulative = prev_cumulative + total_eligible
    cfs_required = cumulative >= CFS_THRESHOLD

    stmt = FinancialStatement(
        project_id=project_id,
        reporting_period_id=reporting_period_id,
        partner_id=partner_id,
        status=FinancialStatementStatus.DRAFT,
        category_a_personnel=cat_a,
        category_b_subcontracting=cat_b,
        category_c_travel=cat_c,
        category_d_equipment=cat_d,
        category_e_other=cat_e,
        total_direct_costs=total_direct,
        indirect_costs=indirect,
        total_eligible_costs=total_eligible,
        ec_contribution_requested=ec_requested,
        cumulative_claimed=cumulative,
        cfs_required=cfs_required,
        cfs_status=CFSStatus.PENDING if cfs_required else CFSStatus.NOT_REQUIRED,
    )
    db.add(stmt)
    await db.flush()
    await db.refresh(stmt)
    return stmt


async def get_financial_statement(
    db: AsyncSession, statement_id: uuid.UUID
) -> FinancialStatement:
    """Get a financial statement by ID."""
    stmt = select(FinancialStatement).where(
        FinancialStatement.id == statement_id,
        FinancialStatement.deleted_at.is_(None),
    )
    result = (await db.execute(stmt)).scalar_one_or_none()
    if not result:
        raise HTTPException(status_code=404, detail="Financial statement not found")
    return result


async def list_financial_statements(
    db: AsyncSession,
    project_id: uuid.UUID,
    reporting_period_id: uuid.UUID | None = None,
) -> list[FinancialStatement]:
    """List financial statements for a project."""
    stmt = select(FinancialStatement).where(
        FinancialStatement.project_id == project_id,
        FinancialStatement.deleted_at.is_(None),
    )
    if reporting_period_id:
        stmt = stmt.where(
            FinancialStatement.reporting_period_id == reporting_period_id
        )
    stmt = stmt.order_by(FinancialStatement.created_at)
    return list((await db.execute(stmt)).scalars().all())


async def advance_financial_statement_status(
    db: AsyncSession,
    statement_id: uuid.UUID,
    actor: str | None = None,
) -> FinancialStatement:
    """Advance the financial statement through the approval workflow."""
    fs = await get_financial_statement(db, statement_id)

    transitions = {
        FinancialStatementStatus.DRAFT: FinancialStatementStatus.PARTNER_SUBMITTED,
        FinancialStatementStatus.PARTNER_SUBMITTED: FinancialStatementStatus.COORDINATOR_REVIEW,
        FinancialStatementStatus.COORDINATOR_REVIEW: FinancialStatementStatus.COORDINATOR_APPROVED,
        FinancialStatementStatus.COORDINATOR_APPROVED: FinancialStatementStatus.REPORTED_TO_EC,
        FinancialStatementStatus.REPORTED_TO_EC: FinancialStatementStatus.EC_APPROVED,
    }

    next_status = transitions.get(fs.status)
    if next_status is None:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot advance from {fs.status.value}",
        )

    now = datetime.now(timezone.utc)
    fs.status = next_status

    if next_status == FinancialStatementStatus.PARTNER_SUBMITTED:
        fs.partner_signed_by = actor
        fs.partner_signed_at = now
    elif next_status == FinancialStatementStatus.COORDINATOR_APPROVED:
        fs.coordinator_approved_by = actor
        fs.coordinator_approved_at = now
    elif next_status == FinancialStatementStatus.REPORTED_TO_EC:
        fs.reported_to_ec_at = now

    await db.flush()
    await db.refresh(fs)
    return fs


# --- WP Completion Declaration (Lump Sum) CRUD ---


async def create_wp_completion_declaration(
    db: AsyncSession,
    project_id: uuid.UUID,
    reporting_period_id: uuid.UUID,
    work_package_id: uuid.UUID,
    lump_sum_amount: Decimal,
) -> WPCompletionDeclaration:
    """Create a WP completion declaration for a lump sum project."""
    project = await _get_project(db, project_id)

    # Check duplicate
    dup_stmt = select(WPCompletionDeclaration).where(
        WPCompletionDeclaration.project_id == project_id,
        WPCompletionDeclaration.reporting_period_id == reporting_period_id,
        WPCompletionDeclaration.work_package_id == work_package_id,
        WPCompletionDeclaration.deleted_at.is_(None),
    )
    existing = (await db.execute(dup_stmt)).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=409,
            detail="Declaration already exists for this WP/period",
        )

    decl = WPCompletionDeclaration(
        project_id=project_id,
        reporting_period_id=reporting_period_id,
        work_package_id=work_package_id,
        lump_sum_amount=lump_sum_amount,
        completion_status=CompletionStatus.NOT_STARTED,
    )
    db.add(decl)
    await db.flush()
    await db.refresh(decl)
    return decl


async def update_wp_completion_declaration(
    db: AsyncSession,
    declaration_id: uuid.UUID,
    data: dict,
) -> WPCompletionDeclaration:
    """Update a WP completion declaration."""
    stmt = select(WPCompletionDeclaration).where(
        WPCompletionDeclaration.id == declaration_id,
        WPCompletionDeclaration.deleted_at.is_(None),
    )
    decl = (await db.execute(stmt)).scalar_one_or_none()
    if not decl:
        raise HTTPException(status_code=404, detail="Declaration not found")

    now = datetime.now(timezone.utc)
    for key, value in data.items():
        if value is not None and hasattr(decl, key):
            setattr(decl, key, value)

    # Auto-calculate amount_claimed based on completion
    if decl.completion_status == CompletionStatus.COMPLETED:
        decl.amount_claimed = decl.lump_sum_amount
        decl.completion_percentage = 100
    elif decl.completion_status == CompletionStatus.PARTIALLY_COMPLETED:
        decl.amount_claimed = _q(
            decl.lump_sum_amount * Decimal(decl.completion_percentage) / Decimal("100")
        )

    if "declared_by" in data and data["declared_by"]:
        decl.declared_at = now
    if "approved_by" in data and data["approved_by"]:
        decl.approved_at = now

    await db.flush()
    await db.refresh(decl)
    return decl


async def list_wp_completion_declarations(
    db: AsyncSession,
    project_id: uuid.UUID,
    reporting_period_id: uuid.UUID | None = None,
) -> list[WPCompletionDeclaration]:
    """List WP completion declarations for a project."""
    stmt = select(WPCompletionDeclaration).where(
        WPCompletionDeclaration.project_id == project_id,
        WPCompletionDeclaration.deleted_at.is_(None),
    )
    if reporting_period_id:
        stmt = stmt.where(
            WPCompletionDeclaration.reporting_period_id == reporting_period_id
        )
    stmt = stmt.order_by(WPCompletionDeclaration.created_at)
    return list((await db.execute(stmt)).scalars().all())


# --- Unit Delivery Record CRUD ---


async def create_unit_delivery_record(
    db: AsyncSession,
    project_id: uuid.UUID,
    reporting_period_id: uuid.UUID,
    data: dict,
) -> UnitDeliveryRecord:
    """Create a unit delivery record."""
    await _get_project(db, project_id)

    record = UnitDeliveryRecord(
        project_id=project_id,
        reporting_period_id=reporting_period_id,
        description=data["description"],
        unit_type=data["unit_type"],
        planned_units=data["planned_units"],
        unit_rate=data["unit_rate"],
        work_package_id=data.get("work_package_id"),
        total_cost=ZERO,
        status=UnitCostStatus.PLANNED,
    )
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return record


async def update_unit_delivery_record(
    db: AsyncSession,
    record_id: uuid.UUID,
    data: dict,
) -> UnitDeliveryRecord:
    """Update a unit delivery record."""
    stmt = select(UnitDeliveryRecord).where(
        UnitDeliveryRecord.id == record_id,
        UnitDeliveryRecord.deleted_at.is_(None),
    )
    record = (await db.execute(stmt)).scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Unit delivery record not found")

    now = datetime.now(timezone.utc)
    for key, value in data.items():
        if value is not None and hasattr(record, key):
            setattr(record, key, value)

    # Recalculate total_cost = actual_units * unit_rate
    record.total_cost = _q(record.actual_units * record.unit_rate)

    if "reported_by" in data and data["reported_by"]:
        record.reported_at = now
    if "approved_by" in data and data["approved_by"]:
        record.approved_at = now

    await db.flush()
    await db.refresh(record)
    return record


async def list_unit_delivery_records(
    db: AsyncSession,
    project_id: uuid.UUID,
    reporting_period_id: uuid.UUID | None = None,
) -> list[UnitDeliveryRecord]:
    """List unit delivery records for a project."""
    stmt = select(UnitDeliveryRecord).where(
        UnitDeliveryRecord.project_id == project_id,
        UnitDeliveryRecord.deleted_at.is_(None),
    )
    if reporting_period_id:
        stmt = stmt.where(
            UnitDeliveryRecord.reporting_period_id == reporting_period_id
        )
    stmt = stmt.order_by(UnitDeliveryRecord.created_at)
    return list((await db.execute(stmt)).scalars().all())


# --- Cost-Model-Aware Report Generation ---


async def generate_form_c_report(
    db: AsyncSession,
    project_id: uuid.UUID,
    reporting_period_id: uuid.UUID,
    partner_id: uuid.UUID | None = None,
) -> FormCReport:
    """Generate a Form C report for an actual-cost project."""
    project = await _get_project(db, project_id)
    period = await _get_period(db, reporting_period_id)

    cat_totals = await _get_category_totals(
        db, project_id, period.start_date, period.end_date, partner_id
    )

    # University mappings
    map_stmt = select(BudgetCategoryMapping).where(
        BudgetCategoryMapping.project_id == project_id
    )
    mappings = {
        m.ec_category: m
        for m in (await db.execute(map_stmt)).scalars().all()
    }

    rows: list[CategoryBreakdownRow] = []
    indirect_base = ZERO
    total_direct = ZERO

    for cat in ECBudgetCategory:
        if cat == ECBudgetCategory.E_INDIRECT:
            continue
        amount = cat_totals.get(cat, ZERO)
        mapping = mappings.get(cat)
        rows.append(CategoryBreakdownRow(
            ec_category=cat.value,
            university_account_code=mapping.university_account_code if mapping else None,
            university_category_name=mapping.university_category_name if mapping else None,
            incurred=amount,
            ec_eligible=amount,
        ))
        total_direct += amount
        if cat in INDIRECT_BASE_CATEGORIES:
            indirect_base += amount

    indirect = _q(indirect_base * INDIRECT_RATE)
    total_eligible = total_direct + indirect

    funding_rate = _q(project.funding_rate) if project.funding_rate else ZERO
    ec_requested = (
        _q(total_eligible * funding_rate / Decimal("100"))
        if funding_rate > ZERO
        else total_eligible
    )

    # Cumulative claimed
    cum_stmt = select(
        func.coalesce(func.sum(FinancialStatement.total_eligible_costs), 0)
    ).where(
        FinancialStatement.project_id == project_id,
        FinancialStatement.partner_id == partner_id,
        FinancialStatement.deleted_at.is_(None),
    )
    cumulative = _q((await db.execute(cum_stmt)).scalar_one()) + total_eligible
    cfs_required = cumulative >= CFS_THRESHOLD

    return FormCReport(
        project_id=project_id,
        project_acronym=project.acronym,
        reporting_period_id=reporting_period_id,
        partner_id=partner_id,
        period_start=period.start_date,
        period_end=period.end_date,
        category_breakdown=rows,
        total_direct_costs=total_direct,
        indirect_costs=indirect,
        indirect_rate=INDIRECT_RATE,
        total_eligible_costs=total_eligible,
        ec_contribution_requested=ec_requested,
        cumulative_claimed=cumulative,
        cfs_required=cfs_required,
        cfs_status=CFSStatus.PENDING if cfs_required else CFSStatus.NOT_REQUIRED,
    )


async def generate_lump_sum_report(
    db: AsyncSession,
    project_id: uuid.UUID,
    reporting_period_id: uuid.UUID,
) -> LumpSumReport:
    """Generate a lump sum report from WP completion declarations."""
    project = await _get_project(db, project_id)

    declarations = await list_wp_completion_declarations(
        db, project_id, reporting_period_id
    )

    total_lump_sum = sum(
        (_q(d.lump_sum_amount) for d in declarations), ZERO
    )
    total_claimed = sum(
        (_q(d.amount_claimed) for d in declarations), ZERO
    )

    return LumpSumReport(
        project_id=project_id,
        project_acronym=project.acronym,
        reporting_period_id=reporting_period_id,
        declarations=[
            WPCompletionDeclarationResponse.model_validate(d)
            for d in declarations
        ],
        total_lump_sum=total_lump_sum,
        total_claimed=total_claimed,
    )


async def generate_unit_cost_report(
    db: AsyncSession,
    project_id: uuid.UUID,
    reporting_period_id: uuid.UUID,
) -> UnitCostReport:
    """Generate a unit cost report from delivery records."""
    project = await _get_project(db, project_id)

    records = await list_unit_delivery_records(
        db, project_id, reporting_period_id
    )

    total_planned = sum(
        (_q(r.planned_units * r.unit_rate) for r in records), ZERO
    )
    total_actual = sum((_q(r.total_cost) for r in records), ZERO)

    return UnitCostReport(
        project_id=project_id,
        project_acronym=project.acronym,
        reporting_period_id=reporting_period_id,
        records=[
            UnitDeliveryRecordResponse.model_validate(r) for r in records
        ],
        total_planned_cost=total_planned,
        total_actual_cost=total_actual,
    )


async def generate_institutional_report(
    db: AsyncSession,
    project_id: uuid.UUID,
    period_start: date | None = None,
    period_end: date | None = None,
) -> InstitutionalReport:
    """Generate the institutional parallel report (EC vs university view)."""
    project = await _get_project(db, project_id)

    cat_totals = await _get_category_totals(
        db, project_id, period_start, period_end
    )

    # University mappings
    map_stmt = select(BudgetCategoryMapping).where(
        BudgetCategoryMapping.project_id == project_id
    )
    mappings = {
        m.ec_category: m
        for m in (await db.execute(map_stmt)).scalars().all()
    }

    rows: list[InstitutionalMappingRow] = []
    total_ec = ZERO
    total_uni = ZERO
    total_disc = ZERO
    has_discrepancies = False

    for cat in ECBudgetCategory:
        if cat == ECBudgetCategory.E_INDIRECT:
            continue
        ec_amount = cat_totals.get(cat, ZERO)
        mapping = mappings.get(cat)

        # University amount — same as EC unless there's a mapping override
        uni_amount = ec_amount
        discrepancy = ZERO

        if mapping:
            # In real implementation, university amounts might differ due to
            # overhead methodology, VAT treatment, etc.
            discrepancy = _q(ec_amount - uni_amount)

        if discrepancy != ZERO:
            has_discrepancies = True

        rows.append(InstitutionalMappingRow(
            ec_category=cat.value,
            ec_amount=ec_amount,
            university_account_code=mapping.university_account_code if mapping else None,
            university_category_name=mapping.university_category_name if mapping else None,
            university_amount=uni_amount,
            discrepancy=discrepancy,
        ))

        total_ec += ec_amount
        total_uni += uni_amount
        total_disc += discrepancy

    return InstitutionalReport(
        project_id=project_id,
        project_acronym=project.acronym,
        rows=rows,
        total_ec=total_ec,
        total_university=total_uni,
        total_discrepancy=total_disc,
        has_discrepancies=has_discrepancies,
    )


async def get_cost_model_financial_report(
    db: AsyncSession,
    project_id: uuid.UUID,
    reporting_period_id: uuid.UUID | None = None,
) -> CostModelFinancialReport:
    """Generate a cost-model-aware financial report.

    Auto-detects project cost model and returns the appropriate
    report type (Form C, lump sum, or unit cost).
    """
    project = await _get_project(db, project_id)

    form_c = None
    lump_sum = None
    unit_cost = None
    institutional = None

    if reporting_period_id:
        period = await _get_period(db, reporting_period_id)

        if project.cost_model == CostModel.ACTUAL_COSTS:
            form_c = await generate_form_c_report(
                db, project_id, reporting_period_id
            )
        elif project.cost_model == CostModel.LUMP_SUM:
            lump_sum = await generate_lump_sum_report(
                db, project_id, reporting_period_id
            )
        elif project.cost_model == CostModel.UNIT_COSTS:
            unit_cost = await generate_unit_cost_report(
                db, project_id, reporting_period_id
            )
        elif project.cost_model == CostModel.MIXED:
            # Mixed: generate both Form C and lump sum
            form_c = await generate_form_c_report(
                db, project_id, reporting_period_id
            )
            lump_sum = await generate_lump_sum_report(
                db, project_id, reporting_period_id
            )

        institutional = await generate_institutional_report(
            db, project_id, period.start_date, period.end_date
        )
    else:
        institutional = await generate_institutional_report(db, project_id)

    return CostModelFinancialReport(
        project_id=project_id,
        project_acronym=project.acronym,
        cost_model=project.cost_model.value,
        reporting_period_id=reporting_period_id,
        form_c=form_c,
        lump_sum=lump_sum,
        unit_cost=unit_cost,
        institutional_report=institutional,
    )


# --- Helpers ---


async def _get_project(db: AsyncSession, project_id: uuid.UUID) -> Project:
    """Get project or raise 404."""
    stmt = select(Project).where(
        Project.id == project_id, Project.deleted_at.is_(None)
    )
    project = (await db.execute(stmt)).scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


async def _get_period(
    db: AsyncSession, period_id: uuid.UUID
) -> ReportingPeriod:
    """Get reporting period or raise 404."""
    stmt = select(ReportingPeriod).where(
        ReportingPeriod.id == period_id,
        ReportingPeriod.deleted_at.is_(None),
    )
    period = (await db.execute(stmt)).scalar_one_or_none()
    if not period:
        raise HTTPException(status_code=404, detail="Reporting period not found")
    return period


async def _get_category_totals(
    db: AsyncSession,
    project_id: uuid.UUID,
    period_start: date | None = None,
    period_end: date | None = None,
    partner_id: uuid.UUID | None = None,
) -> dict[ECBudgetCategory, Decimal]:
    """Get expense totals by EC category for a period."""
    exp_stmt = (
        select(
            Expense.ec_category,
            func.coalesce(func.sum(Expense.amount_gross), 0).label("total"),
        )
        .where(
            Expense.project_id == project_id,
            Expense.deleted_at.is_(None),
        )
        .group_by(Expense.ec_category)
    )

    if period_start:
        exp_stmt = exp_stmt.where(Expense.date_incurred >= period_start)
    if period_end:
        exp_stmt = exp_stmt.where(Expense.date_incurred <= period_end)
    if partner_id is not None:
        exp_stmt = exp_stmt.where(Expense.partner_id == partner_id)

    result = await db.execute(exp_stmt)
    totals: dict[ECBudgetCategory, Decimal] = {}
    for row in result.all():
        if row.ec_category is not None:
            totals[row.ec_category] = _q(row.total)

    # Add missions to C1_TRAVEL
    m_stmt = select(
        func.coalesce(func.sum(Mission.total_cost), 0)
    ).where(
        Mission.project_id == project_id,
        Mission.deleted_at.is_(None),
    )
    if period_start:
        m_stmt = m_stmt.where(Mission.start_date >= period_start)
    if period_end:
        m_stmt = m_stmt.where(Mission.start_date <= period_end)
    m_total = _q((await db.execute(m_stmt)).scalar_one())
    if m_total > ZERO:
        totals[ECBudgetCategory.C1_TRAVEL] = (
            totals.get(ECBudgetCategory.C1_TRAVEL, ZERO) + m_total
        )

    return totals
