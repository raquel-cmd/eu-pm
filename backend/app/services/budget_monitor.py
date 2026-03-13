"""Budget monitoring service (Section 4.3).

Provides budget consumption calculations, burn rate analysis,
automatic indirect costs (25% flat rate on A+C+D), budget transfer
validation (20% rule), threshold alerts, lump sum WP-level tracking,
and cash flow forecasting.
"""

import uuid
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

from fastapi import HTTPException
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import CostModel, ECBudgetCategory, WPStatus
from app.models.financial import Expense, FundDistribution, Mission, Procurement
from app.models.partner import Partner, ProjectPartner
from app.models.project import Project
from app.models.work_package import Deliverable, Milestone, WorkPackage
from app.schemas.budget_monitor import (
    BudgetSummaryResponse,
    BudgetTransfer,
    BurnRateResponse,
    ByPartnerResponse,
    CashFlowEntry,
    CashFlowForecastResponse,
    CategoryDetailResponse,
    CategorySpending,
    PartnerSpending,
    WPCompletionStatus,
)

ZERO = Decimal("0.00")
INDIRECT_RATE = Decimal("0.25")
TRANSFER_LIMIT = Decimal("0.20")
ALERT_THRESHOLD_WARNING = Decimal("0.80")
ALERT_THRESHOLD_CRITICAL = Decimal("0.95")

# Categories that form the base for indirect cost calculation
INDIRECT_BASE_CATEGORIES = {
    ECBudgetCategory.A_PERSONNEL,
    ECBudgetCategory.C1_TRAVEL,
    ECBudgetCategory.C2_EQUIPMENT,
    ECBudgetCategory.C3_OTHER_GOODS,
    ECBudgetCategory.D_OTHER_COSTS,
}


def _q(value: Decimal | int | None) -> Decimal:
    """Quantize a decimal to 2 places, treating None as zero."""
    if value is None:
        return ZERO
    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


async def _get_project(
    db: AsyncSession, project_id: uuid.UUID
) -> Project:
    """Fetch a project or raise 404."""
    stmt = select(Project).where(
        Project.id == project_id, Project.deleted_at.is_(None)
    )
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


async def _get_expense_totals_by_category(
    db: AsyncSession, project_id: uuid.UUID
) -> dict[ECBudgetCategory | None, Decimal]:
    """Sum expenses by EC category for a project (excluding soft-deleted)."""
    stmt = (
        select(
            Expense.ec_category,
            func.coalesce(func.sum(Expense.amount_gross), 0),
        )
        .where(
            Expense.project_id == project_id,
            Expense.deleted_at.is_(None),
        )
        .group_by(Expense.ec_category)
    )
    result = await db.execute(stmt)
    return {row[0]: _q(row[1]) for row in result.all()}


async def _get_mission_total(
    db: AsyncSession, project_id: uuid.UUID
) -> Decimal:
    """Sum mission total_cost for a project (excluding soft-deleted)."""
    stmt = select(
        func.coalesce(func.sum(Mission.total_cost), 0)
    ).where(
        Mission.project_id == project_id,
        Mission.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    return _q(result.scalar_one())


async def _get_procurement_total(
    db: AsyncSession, project_id: uuid.UUID
) -> Decimal:
    """Sum procurement actual_cost (or estimated_cost as fallback)."""
    stmt = select(
        func.coalesce(
            func.sum(
                case(
                    (Procurement.actual_cost.isnot(None), Procurement.actual_cost),
                    else_=func.coalesce(Procurement.estimated_cost, 0),
                )
            ),
            0,
        )
    ).where(
        Procurement.project_id == project_id,
        Procurement.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    return _q(result.scalar_one())


async def _get_total_spending(
    db: AsyncSession, project_id: uuid.UUID
) -> Decimal:
    """Get total spending across expenses, missions, and procurements."""
    expense_stmt = select(
        func.coalesce(func.sum(Expense.amount_gross), 0)
    ).where(
        Expense.project_id == project_id,
        Expense.deleted_at.is_(None),
    )
    mission_stmt = select(
        func.coalesce(func.sum(Mission.total_cost), 0)
    ).where(
        Mission.project_id == project_id,
        Mission.deleted_at.is_(None),
    )
    procurement_stmt = select(
        func.coalesce(
            func.sum(
                case(
                    (Procurement.actual_cost.isnot(None), Procurement.actual_cost),
                    else_=func.coalesce(Procurement.estimated_cost, 0),
                )
            ),
            0,
        )
    ).where(
        Procurement.project_id == project_id,
        Procurement.deleted_at.is_(None),
    )
    e_result = await db.execute(expense_stmt)
    m_result = await db.execute(mission_stmt)
    p_result = await db.execute(procurement_stmt)
    return (
        _q(e_result.scalar_one())
        + _q(m_result.scalar_one())
        + _q(p_result.scalar_one())
    )


def _calculate_indirect_costs(
    category_spending: dict[ECBudgetCategory | None, Decimal],
) -> Decimal:
    """Calculate 25% flat rate indirect costs on A+C+D categories."""
    base = sum(
        amount
        for cat, amount in category_spending.items()
        if cat in INDIRECT_BASE_CATEGORIES
    )
    return _q(Decimal(base) * INDIRECT_RATE)


def _generate_alerts(
    category_spending: dict[ECBudgetCategory | None, Decimal],
    total_budget: Decimal,
    total_spent: Decimal,
) -> list[str]:
    """Generate threshold alerts at 80% and 95%."""
    alerts: list[str] = []
    if total_budget > ZERO:
        ratio = total_spent / total_budget
        if ratio >= ALERT_THRESHOLD_CRITICAL:
            alerts.append(
                f"CRITICAL: Overall spending at {ratio * 100:.1f}% of budget"
            )
        elif ratio >= ALERT_THRESHOLD_WARNING:
            alerts.append(
                f"WARNING: Overall spending at {ratio * 100:.1f}% of budget"
            )
    return alerts


# --- Public API ---


async def get_budget_summary(
    db: AsyncSession, project_id: uuid.UUID
) -> BudgetSummaryResponse:
    """Get overall budget summary for a project."""
    project = await _get_project(db, project_id)
    total_budget = _q(project.total_budget) if project.total_budget else ZERO
    eu_contribution = (
        _q(project.eu_contribution) if project.eu_contribution else ZERO
    )

    category_spending = await _get_expense_totals_by_category(db, project_id)
    mission_total = await _get_mission_total(db, project_id)
    procurement_total = await _get_procurement_total(db, project_id)

    # Add mission costs to C1_TRAVEL category
    travel_key = ECBudgetCategory.C1_TRAVEL
    category_spending[travel_key] = (
        category_spending.get(travel_key, ZERO) + mission_total
    )

    # Add procurement costs to their respective categories or C2_EQUIPMENT
    if procurement_total > ZERO:
        equip_key = ECBudgetCategory.C2_EQUIPMENT
        category_spending[equip_key] = (
            category_spending.get(equip_key, ZERO) + procurement_total
        )

    # Calculate indirect costs for actual costs projects
    indirect = ZERO
    if project.cost_model == CostModel.ACTUAL_COSTS:
        indirect = _calculate_indirect_costs(category_spending)

    total_spent = sum(category_spending.values()) + indirect

    categories = []
    for cat in ECBudgetCategory:
        spent = category_spending.get(cat, ZERO)
        if cat == ECBudgetCategory.E_INDIRECT:
            spent = indirect
        categories.append(
            CategorySpending(
                category=cat,
                budgeted=ZERO,  # no per-category budget stored yet
                spent=spent,
                remaining=ZERO,
                percentage_used=ZERO,
            )
        )

    total_remaining = total_budget - total_spent
    percentage_used = (
        _q(total_spent / total_budget * 100) if total_budget > ZERO else ZERO
    )

    alerts = _generate_alerts(category_spending, total_budget, total_spent)

    return BudgetSummaryResponse(
        project_id=project_id,
        total_budget=total_budget,
        eu_contribution=eu_contribution,
        total_spent=_q(total_spent),
        total_remaining=_q(total_remaining),
        percentage_used=percentage_used,
        indirect_costs_calculated=indirect,
        categories=categories,
        alerts=alerts,
    )


async def get_budget_by_category(
    db: AsyncSession, project_id: uuid.UUID
) -> CategoryDetailResponse:
    """Get detailed spending per EC category with transfer tracking."""
    project = await _get_project(db, project_id)
    category_spending = await _get_expense_totals_by_category(db, project_id)

    # Add mission costs to travel
    mission_total = await _get_mission_total(db, project_id)
    travel_key = ECBudgetCategory.C1_TRAVEL
    category_spending[travel_key] = (
        category_spending.get(travel_key, ZERO) + mission_total
    )

    # Add procurement costs
    procurement_total = await _get_procurement_total(db, project_id)
    if procurement_total > ZERO:
        equip_key = ECBudgetCategory.C2_EQUIPMENT
        category_spending[equip_key] = (
            category_spending.get(equip_key, ZERO) + procurement_total
        )

    indirect = ZERO
    indirect_base = ZERO
    if project.cost_model == CostModel.ACTUAL_COSTS:
        indirect_base = sum(
            amount
            for cat, amount in category_spending.items()
            if cat in INDIRECT_BASE_CATEGORIES
        )
        indirect = _q(Decimal(indirect_base) * INDIRECT_RATE)

    categories = []
    for cat in ECBudgetCategory:
        spent = category_spending.get(cat, ZERO)
        if cat == ECBudgetCategory.E_INDIRECT:
            spent = indirect
        categories.append(
            CategorySpending(
                category=cat,
                budgeted=ZERO,
                spent=spent,
                remaining=ZERO,
                percentage_used=ZERO,
            )
        )

    total_budget = _q(project.total_budget) if project.total_budget else ZERO
    total_spent = sum(category_spending.values()) + indirect
    alerts = _generate_alerts(category_spending, total_budget, total_spent)

    return CategoryDetailResponse(
        project_id=project_id,
        categories=categories,
        indirect_costs_calculated=indirect,
        indirect_costs_base=_q(indirect_base),
        transfers=[],  # transfers tracked when budget allocations are set
        alerts=alerts,
    )


async def get_budget_by_partner(
    db: AsyncSession, project_id: uuid.UUID
) -> ByPartnerResponse:
    """Get spending breakdown by partner."""
    await _get_project(db, project_id)

    # Get partner budgets from project_partners
    pp_stmt = (
        select(
            ProjectPartner.partner_id,
            Partner.short_name,
            ProjectPartner.partner_budget,
        )
        .join(Partner, ProjectPartner.partner_id == Partner.id)
        .where(ProjectPartner.project_id == project_id)
    )
    pp_result = await db.execute(pp_stmt)
    partner_budgets = {
        row[0]: (row[1], _q(row[2]) if row[2] else ZERO)
        for row in pp_result.all()
    }

    # Get expense spending by partner
    expense_stmt = (
        select(
            Expense.partner_id,
            func.coalesce(func.sum(Expense.amount_gross), 0),
        )
        .where(
            Expense.project_id == project_id,
            Expense.deleted_at.is_(None),
        )
        .group_by(Expense.partner_id)
    )
    expense_result = await db.execute(expense_stmt)
    partner_spending: dict[uuid.UUID | None, Decimal] = {
        row[0]: _q(row[1]) for row in expense_result.all()
    }

    partners = []
    for pid, (name, budgeted) in partner_budgets.items():
        spent = partner_spending.pop(pid, ZERO)
        remaining = budgeted - spent
        pct = _q(spent / budgeted * 100) if budgeted > ZERO else ZERO
        partners.append(
            PartnerSpending(
                partner_id=pid,
                partner_name=name,
                budgeted=budgeted,
                spent=spent,
                remaining=remaining,
                percentage_used=pct,
            )
        )

    # Unassigned = spending with no partner_id
    unassigned = partner_spending.pop(None, ZERO)
    # Also add remaining spending from partners not in project_partners
    for spent in partner_spending.values():
        unassigned += spent

    alerts: list[str] = []
    for ps in partners:
        if ps.budgeted > ZERO:
            ratio = ps.spent / ps.budgeted
            if ratio >= ALERT_THRESHOLD_CRITICAL:
                alerts.append(
                    f"CRITICAL: {ps.partner_name} spending at "
                    f"{ratio * 100:.1f}% of budget"
                )
            elif ratio >= ALERT_THRESHOLD_WARNING:
                alerts.append(
                    f"WARNING: {ps.partner_name} spending at "
                    f"{ratio * 100:.1f}% of budget"
                )

    return ByPartnerResponse(
        project_id=project_id,
        partners=partners,
        unassigned_spending=unassigned,
        alerts=alerts,
    )


async def get_burn_rate(
    db: AsyncSession, project_id: uuid.UUID
) -> BurnRateResponse:
    """Calculate burn rate comparing spending rate to time elapsed."""
    project = await _get_project(db, project_id)
    total_budget = _q(project.total_budget) if project.total_budget else ZERO
    total_spent = await _get_total_spending(db, project_id)

    # Add indirect costs for actual costs projects
    if project.cost_model == CostModel.ACTUAL_COSTS:
        cat_spending = await _get_expense_totals_by_category(db, project_id)
        mission_total = await _get_mission_total(db, project_id)
        cat_spending[ECBudgetCategory.C1_TRAVEL] = (
            cat_spending.get(ECBudgetCategory.C1_TRAVEL, ZERO) + mission_total
        )
        indirect = _calculate_indirect_costs(cat_spending)
        total_spent += indirect

    months_total = project.duration_months or 0
    start = project.start_date
    today = date.today()

    if start and months_total > 0:
        months_elapsed = max(
            0,
            (today.year - start.year) * 12 + (today.month - start.month),
        )
        months_elapsed = min(months_elapsed, months_total)
    else:
        months_elapsed = 0

    months_remaining = max(0, months_total - months_elapsed)
    elapsed_ratio = (
        _q(Decimal(months_elapsed) / Decimal(months_total) * 100)
        if months_total > 0
        else ZERO
    )
    budget_ratio = (
        _q(total_spent / total_budget * 100) if total_budget > ZERO else ZERO
    )

    monthly_burn = (
        _q(total_spent / Decimal(months_elapsed))
        if months_elapsed > 0
        else ZERO
    )
    projected_total = (
        _q(monthly_burn * Decimal(months_total))
        if months_total > 0
        else ZERO
    )

    # Determine status
    if elapsed_ratio == ZERO or budget_ratio == ZERO:
        status = "on_track"
    elif budget_ratio > elapsed_ratio * Decimal("1.15"):
        status = "over_spending"
    elif budget_ratio < elapsed_ratio * Decimal("0.85"):
        status = "under_spending"
    else:
        status = "on_track"

    return BurnRateResponse(
        project_id=project_id,
        total_budget=total_budget,
        total_spent=_q(total_spent),
        elapsed_ratio=elapsed_ratio,
        budget_ratio=budget_ratio,
        burn_rate_status=status,
        monthly_burn_rate=monthly_burn,
        projected_total_spend=projected_total,
        months_elapsed=months_elapsed,
        months_total=months_total,
        months_remaining=months_remaining,
    )


async def get_cash_flow_forecast(
    db: AsyncSession, project_id: uuid.UUID
) -> CashFlowForecastResponse:
    """Generate cash flow forecast based on EC payment schedule."""
    project = await _get_project(db, project_id)
    eu_contribution = (
        _q(project.eu_contribution) if project.eu_contribution else ZERO
    )

    # Get all fund distributions (received payments)
    dist_stmt = (
        select(FundDistribution)
        .where(FundDistribution.project_id == project_id)
        .order_by(FundDistribution.distribution_date)
    )
    dist_result = await db.execute(dist_stmt)
    distributions = list(dist_result.scalars().all())

    total_received = sum(_q(d.amount) for d in distributions)
    total_spent = await _get_total_spending(db, project_id)

    forecast: list[CashFlowEntry] = []
    cumulative = ZERO

    # Add received fund distributions
    for d in distributions:
        cumulative += _q(d.amount)
        forecast.append(
            CashFlowEntry(
                entry_type=d.distribution_type,
                description=f"Received: {d.distribution_type.replace('_', ' ')}",
                amount=_q(d.amount),
                date=d.distribution_date,
                cumulative_balance=_q(cumulative),
            )
        )

    # Standard EC payment schedule forecast
    start = project.start_date
    end = project.end_date
    if start and end and eu_contribution > ZERO:
        # Pre-financing: typically at project start
        pre_financing_received = any(
            d.distribution_type == "pre_financing" for d in distributions
        )
        if not pre_financing_received:
            pre_financing_amount = _q(eu_contribution * Decimal("0.40"))
            cumulative += pre_financing_amount
            forecast.append(
                CashFlowEntry(
                    entry_type="pre_financing",
                    description="Expected pre-financing (40%)",
                    amount=pre_financing_amount,
                    date=start + timedelta(days=60),
                    cumulative_balance=_q(cumulative),
                )
            )

        # Interim payment: mid-project
        interim_received = any(
            d.distribution_type == "interim_payment" for d in distributions
        )
        if not interim_received:
            duration = (end - start).days
            mid_date = start + timedelta(days=duration // 2 + 90)
            interim_amount = _q(eu_contribution * Decimal("0.40"))
            cumulative += interim_amount
            forecast.append(
                CashFlowEntry(
                    entry_type="interim_payment",
                    description="Expected interim payment (40%)",
                    amount=interim_amount,
                    date=mid_date,
                    cumulative_balance=_q(cumulative),
                )
            )

        # Final payment: after project end
        final_received = any(
            d.distribution_type == "final_payment" for d in distributions
        )
        if not final_received:
            remaining_eu = eu_contribution - total_received
            if not pre_financing_received:
                remaining_eu -= _q(eu_contribution * Decimal("0.40"))
            if not interim_received:
                remaining_eu -= _q(eu_contribution * Decimal("0.40"))
            if remaining_eu > ZERO:
                cumulative += _q(remaining_eu)
                forecast.append(
                    CashFlowEntry(
                        entry_type="final_payment",
                        description="Expected final payment (remaining)",
                        amount=_q(remaining_eu),
                        date=end + timedelta(days=180),
                        cumulative_balance=_q(cumulative),
                    )
                )

    # Sort forecast by date
    forecast.sort(key=lambda e: e.date)

    # Recalculate cumulative after sort
    cumulative = ZERO
    for entry in forecast:
        cumulative += entry.amount
        entry.cumulative_balance = _q(cumulative)

    current_balance = total_received - total_spent

    return CashFlowForecastResponse(
        project_id=project_id,
        eu_contribution=eu_contribution,
        total_received=_q(total_received),
        total_spent=_q(total_spent),
        current_balance=_q(current_balance),
        forecast=forecast,
    )


async def get_wp_completion_status(
    db: AsyncSession, project_id: uuid.UUID
) -> list[WPCompletionStatus]:
    """Get WP-level completion tracking for lump sum projects."""
    project = await _get_project(db, project_id)
    if project.cost_model != CostModel.LUMP_SUM:
        raise HTTPException(
            status_code=400,
            detail="WP completion tracking is only for lump sum projects",
        )

    wp_stmt = (
        select(WorkPackage)
        .where(
            WorkPackage.project_id == project_id,
            WorkPackage.deleted_at.is_(None),
        )
        .order_by(WorkPackage.wp_number)
    )
    wp_result = await db.execute(wp_stmt)
    work_packages = list(wp_result.scalars().all())

    results = []
    for wp in work_packages:
        # Spending on this WP
        expense_stmt = select(
            func.coalesce(func.sum(Expense.amount_gross), 0)
        ).where(
            Expense.project_id == project_id,
            Expense.work_package_id == wp.id,
            Expense.deleted_at.is_(None),
        )
        expense_result = await db.execute(expense_stmt)
        wp_spending = _q(expense_result.scalar_one())

        # Deliverables
        del_stmt = select(
            func.count(Deliverable.id),
            func.count(
                case(
                    (Deliverable.submission_date.isnot(None), Deliverable.id),
                )
            ),
        ).where(
            Deliverable.work_package_id == wp.id,
            Deliverable.deleted_at.is_(None),
        )
        del_result = await db.execute(del_stmt)
        del_row = del_result.one()
        del_total = del_row[0]
        del_submitted = del_row[1]

        # Milestones
        ms_stmt = select(
            func.count(Milestone.id),
            func.count(case((Milestone.achieved.is_(True), Milestone.id))),
        ).where(Milestone.work_package_id == wp.id)
        ms_result = await db.execute(ms_stmt)
        ms_row = ms_result.one()
        ms_total = ms_row[0]
        ms_achieved = ms_row[1]

        total_items = del_total + ms_total
        completed_items = del_submitted + ms_achieved
        completion_pct = (
            _q(Decimal(completed_items) / Decimal(total_items) * 100)
            if total_items > 0
            else ZERO
        )

        results.append(
            WPCompletionStatus(
                work_package_id=wp.id,
                wp_number=wp.wp_number,
                title=wp.title,
                status=wp.status,
                total_spending=wp_spending,
                deliverables_total=del_total,
                deliverables_submitted=del_submitted,
                milestones_total=ms_total,
                milestones_achieved=ms_achieved,
                completion_percentage=completion_pct,
            )
        )

    return results


def validate_budget_transfer(
    original_budget: Decimal,
    transfer_amount: Decimal,
) -> bool:
    """Check if a budget transfer is within the 20% flexibility rule.

    EC rule: budget transfers between categories are allowed
    up to 20% of the original category budget without amendment.
    """
    if original_budget <= ZERO:
        return False
    return transfer_amount <= original_budget * TRANSFER_LIMIT
