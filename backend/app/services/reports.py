"""Service layer for institutional reporting (Section 6).

Provides the Central Finance PM dashboard, PM declarations,
cost statements, overhead calculations, and annual summaries.
All functions are read-only aggregations over existing data.
"""

import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal

from fastapi import HTTPException
from sqlalchemy import case, extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import CostModel, ECBudgetCategory
from app.models.financial import (
    BudgetCategoryMapping,
    Expense,
    FundDistribution,
    Mission,
    Procurement,
)
from app.models.project import Project
from app.models.researcher import EffortAllocation, Researcher, TimesheetEntry
from app.schemas.reports import (
    AnnualCategorySpending,
    AnnualSummaryProject,
    AnnualSummaryResponse,
    CostStatementLine,
    CostStatementResponse,
    FinanceDashboardResponse,
    FlaggedItem,
    OverheadCalculationResponse,
    OverheadCategoryBreakdown,
    PMDeclarationLine,
    PMDeclarationsResponse,
    ProjectFinancialRow,
    RecruitmentPlanItem,
    UpcomingECPayment,
)
from app.services.timesheet import calculate_person_months

ZERO = Decimal("0.00")
INDIRECT_RATE = Decimal("0.25")
ALERT_THRESHOLD_CRITICAL = Decimal("0.95")
ALERT_THRESHOLD_WARNING = Decimal("0.80")

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
    return Decimal(str(value)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )


async def _get_total_spending_for_project(
    db: AsyncSession, project_id: uuid.UUID
) -> Decimal:
    """Get total spending for a single project."""
    e_stmt = select(
        func.coalesce(func.sum(Expense.amount_gross), 0)
    ).where(Expense.project_id == project_id, Expense.deleted_at.is_(None))

    m_stmt = select(
        func.coalesce(func.sum(Mission.total_cost), 0)
    ).where(Mission.project_id == project_id, Mission.deleted_at.is_(None))

    p_stmt = select(
        func.coalesce(
            func.sum(
                case(
                    (
                        Procurement.actual_cost.isnot(None),
                        Procurement.actual_cost,
                    ),
                    else_=func.coalesce(Procurement.estimated_cost, 0),
                )
            ),
            0,
        )
    ).where(
        Procurement.project_id == project_id,
        Procurement.deleted_at.is_(None),
    )

    e = _q((await db.execute(e_stmt)).scalar_one())
    m = _q((await db.execute(m_stmt)).scalar_one())
    p = _q((await db.execute(p_stmt)).scalar_one())
    return e + m + p


# --- Finance Dashboard ---


async def get_finance_dashboard(
    db: AsyncSession,
) -> FinanceDashboardResponse:
    """Build the cross-project finance dashboard."""
    # 1. All active projects
    proj_stmt = select(Project).where(Project.deleted_at.is_(None))
    projects = list((await db.execute(proj_stmt)).scalars().all())

    rows: list[ProjectFinancialRow] = []
    total_budget = ZERO
    total_spent = ZERO
    flagged: list[FlaggedItem] = []
    upcoming: list[UpcomingECPayment] = []
    recruitment: list[RecruitmentPlanItem] = []

    today = date.today()

    for proj in projects:
        budget = _q(proj.total_budget)
        eu_contrib = _q(proj.eu_contribution)
        spent = await _get_total_spending_for_project(db, proj.id)

        # Burn rate
        if budget > ZERO:
            burn_pct = _q((spent / budget) * 100)
        else:
            burn_pct = ZERO

        if burn_pct >= 95:
            burn_status = "over_spending"
        elif burn_pct >= 80:
            burn_status = "under_spending"
        else:
            burn_status = "on_track"

        # PM compliance rate
        alloc_stmt = select(
            EffortAllocation.researcher_id
        ).where(
            EffortAllocation.project_id == proj.id
        ).distinct()
        alloc_rids = [
            r[0] for r in (await db.execute(alloc_stmt)).all()
        ]

        pm_compliance = Decimal("100.00")
        if alloc_rids:
            with_ts = 0
            for rid in alloc_rids:
                ts_count = (
                    await db.execute(
                        select(func.count()).where(
                            TimesheetEntry.researcher_id == rid,
                            TimesheetEntry.project_id == proj.id,
                        )
                    )
                ).scalar_one()
                if ts_count > 0:
                    with_ts += 1
            pm_compliance = _q(
                Decimal(with_ts) / Decimal(len(alloc_rids)) * 100
            )

        # Flags
        proj_flags: list[str] = []
        if burn_pct >= 95:
            proj_flags.append("OVER_BUDGET")
            flagged.append(
                FlaggedItem(
                    project_id=proj.id,
                    acronym=proj.acronym,
                    flag_type="BUDGET_ALERT",
                    severity="CRITICAL",
                    description=(
                        f"Budget usage at {burn_pct}%"
                    ),
                )
            )
        elif burn_pct >= 80:
            proj_flags.append("HIGH_BURN")
            flagged.append(
                FlaggedItem(
                    project_id=proj.id,
                    acronym=proj.acronym,
                    flag_type="BUDGET_ALERT",
                    severity="WARNING",
                    description=(
                        f"Budget usage at {burn_pct}%"
                    ),
                )
            )

        if pm_compliance < 100 and alloc_rids:
            proj_flags.append("MISSING_TIMESHEETS")
            flagged.append(
                FlaggedItem(
                    project_id=proj.id,
                    acronym=proj.acronym,
                    flag_type="COMPLIANCE",
                    severity="WARNING",
                    description=(
                        f"PM compliance at {pm_compliance}%"
                    ),
                )
            )

        rows.append(
            ProjectFinancialRow(
                project_id=proj.id,
                acronym=proj.acronym,
                programme=proj.programme,
                status=proj.status,
                cost_model=proj.cost_model,
                start_date=proj.start_date,
                end_date=proj.end_date,
                total_budget=budget,
                eu_contribution=eu_contrib,
                total_spent=spent,
                burn_rate_percentage=burn_pct,
                burn_rate_status=burn_status,
                pm_compliance_rate=pm_compliance,
                flags=proj_flags,
            )
        )
        total_budget += budget
        total_spent += spent

        # Upcoming EC payments (fund distributions expected)
        if eu_contrib > ZERO:
            fd_stmt = select(
                func.coalesce(func.sum(FundDistribution.amount), 0)
            ).where(FundDistribution.project_id == proj.id)
            received = _q(
                (await db.execute(fd_stmt)).scalar_one()
            )
            remaining = eu_contrib - received
            if remaining > ZERO and proj.end_date:
                upcoming.append(
                    UpcomingECPayment(
                        project_id=proj.id,
                        acronym=proj.acronym,
                        payment_type="interim_payment",
                        expected_amount=remaining,
                        expected_date=proj.end_date,
                    )
                )

        # Recruitment plans
        r_stmt = (
            select(Researcher, EffortAllocation.project_id)
            .join(
                EffortAllocation,
                EffortAllocation.researcher_id == Researcher.id,
            )
            .where(
                EffortAllocation.project_id == proj.id,
                Researcher.deleted_at.is_(None),
                Researcher.end_date.isnot(None),
                Researcher.end_date <= today + timedelta(days=180),
            )
        )
        r_result = await db.execute(r_stmt)
        for r_row in r_result.unique().all():
            researcher = r_row[0]
            budget_remaining = budget - spent
            recruitment.append(
                RecruitmentPlanItem(
                    project_id=proj.id,
                    acronym=proj.acronym,
                    researcher_name=researcher.name,
                    position=researcher.position,
                    contract_type=researcher.contract_type,
                    contract_end=researcher.end_date,
                    funding_source_budget_remaining=budget_remaining,
                )
            )

    overall_burn = ZERO
    if total_budget > ZERO:
        overall_burn = _q((total_spent / total_budget) * 100)

    return FinanceDashboardResponse(
        projects=rows,
        total_budget_all_projects=total_budget,
        total_spent_all_projects=total_spent,
        overall_burn_rate=overall_burn,
        upcoming_ec_payments=upcoming,
        recruitment_plans=recruitment,
        flagged_items=flagged,
        generated_at=datetime.now(timezone.utc),
    )


# --- PM Declarations ---


async def get_pm_declarations(
    db: AsyncSession,
    project_id: uuid.UUID,
    period_start: date,
    period_end: date,
) -> PMDeclarationsResponse:
    """Generate PM declaration sheets per researcher."""
    proj_stmt = select(Project).where(
        Project.id == project_id, Project.deleted_at.is_(None)
    )
    project = (await db.execute(proj_stmt)).scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    # Allocations for this project+period
    alloc_stmt = (
        select(
            EffortAllocation.researcher_id,
            func.sum(EffortAllocation.planned_pm).label("planned_pm"),
        )
        .where(
            EffortAllocation.project_id == project_id,
            EffortAllocation.period_start < period_end,
            EffortAllocation.period_end > period_start,
        )
        .group_by(EffortAllocation.researcher_id)
    )
    alloc_result = await db.execute(alloc_stmt)
    allocations = {
        row.researcher_id: _q(row.planned_pm)
        for row in alloc_result.all()
    }

    declarations: list[PMDeclarationLine] = []
    total_pm = ZERO
    total_cost = ZERO

    for r_id, planned_pm in allocations.items():
        r_stmt = select(Researcher).where(Researcher.id == r_id)
        researcher = (await db.execute(r_stmt)).scalar_one_or_none()
        if researcher is None:
            continue

        # Timesheet hours for this period
        hrs_stmt = select(
            func.coalesce(func.sum(TimesheetEntry.hours), 0)
        ).where(
            TimesheetEntry.researcher_id == r_id,
            TimesheetEntry.project_id == project_id,
            TimesheetEntry.date >= period_start,
            TimesheetEntry.date <= period_end,
        )
        actual_hours = _q((await db.execute(hrs_stmt)).scalar_one())
        actual_pm = calculate_person_months(
            actual_hours, researcher.productive_hours
        )

        # Personnel cost
        rate = _q(researcher.hourly_rate)
        cost = _q(actual_hours * rate)

        # Submission/approval status
        sub_stmt = select(func.count()).where(
            TimesheetEntry.researcher_id == r_id,
            TimesheetEntry.project_id == project_id,
            TimesheetEntry.date >= period_start,
            TimesheetEntry.date <= period_end,
            TimesheetEntry.submitted_at.isnot(None),
        )
        submitted_count = (await db.execute(sub_stmt)).scalar_one()

        appr_stmt = select(func.count()).where(
            TimesheetEntry.researcher_id == r_id,
            TimesheetEntry.project_id == project_id,
            TimesheetEntry.date >= period_start,
            TimesheetEntry.date <= period_end,
            TimesheetEntry.approved_at.isnot(None),
        )
        approved_count = (await db.execute(appr_stmt)).scalar_one()

        total_count_stmt = select(func.count()).where(
            TimesheetEntry.researcher_id == r_id,
            TimesheetEntry.project_id == project_id,
            TimesheetEntry.date >= period_start,
            TimesheetEntry.date <= period_end,
        )
        total_count = (await db.execute(total_count_stmt)).scalar_one()

        all_submitted = (
            total_count > 0 and submitted_count == total_count
        )
        all_approved = (
            total_count > 0 and approved_count == total_count
        )

        declarations.append(
            PMDeclarationLine(
                researcher_name=researcher.name,
                researcher_position=researcher.position,
                project_acronym=project.acronym,
                period_start=period_start,
                period_end=period_end,
                planned_pm=planned_pm,
                actual_hours=actual_hours,
                actual_pm=actual_pm,
                hourly_rate=researcher.hourly_rate,
                personnel_cost=cost,
                submitted=all_submitted,
                approved=all_approved,
            )
        )
        total_pm += actual_pm
        total_cost += cost

    return PMDeclarationsResponse(
        project_id=project_id,
        period_start=period_start,
        period_end=period_end,
        declarations=declarations,
        total_pm=total_pm,
        total_cost=total_cost,
    )


# --- Cost Statement ---


async def get_cost_statement(
    db: AsyncSession,
    project_id: uuid.UUID,
    period_start: date | None = None,
    period_end: date | None = None,
) -> CostStatementResponse:
    """Generate a cost statement reconcilable with university system."""
    proj_stmt = select(Project).where(
        Project.id == project_id, Project.deleted_at.is_(None)
    )
    project = (await db.execute(proj_stmt)).scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    # Expenses by category
    exp_base = select(
        Expense.ec_category,
        func.coalesce(func.sum(Expense.amount_gross), 0).label(
            "incurred"
        ),
        func.coalesce(
            func.sum(
                case(
                    (Expense.ec_eligible.is_(True), Expense.amount_gross),
                    else_=0,
                )
            ),
            0,
        ).label("eligible"),
    ).where(
        Expense.project_id == project_id,
        Expense.deleted_at.is_(None),
    )

    if period_start is not None:
        exp_base = exp_base.where(Expense.date_incurred >= period_start)
    if period_end is not None:
        exp_base = exp_base.where(Expense.date_incurred <= period_end)

    exp_base = exp_base.group_by(Expense.ec_category)
    exp_result = await db.execute(exp_base)
    cat_data: dict[ECBudgetCategory, dict] = {}
    for row in exp_result.all():
        if row.ec_category is not None:
            cat_data[row.ec_category] = {
                "incurred": _q(row.incurred),
                "eligible": _q(row.eligible),
            }

    # Add missions to C1_TRAVEL
    m_stmt = select(
        func.coalesce(func.sum(Mission.total_cost), 0)
    ).where(
        Mission.project_id == project_id,
        Mission.deleted_at.is_(None),
    )
    if period_start is not None:
        m_stmt = m_stmt.where(Mission.start_date >= period_start)
    if period_end is not None:
        m_stmt = m_stmt.where(Mission.start_date <= period_end)
    m_total = _q((await db.execute(m_stmt)).scalar_one())
    if m_total > ZERO:
        c1 = cat_data.get(ECBudgetCategory.C1_TRAVEL, {})
        cat_data[ECBudgetCategory.C1_TRAVEL] = {
            "incurred": c1.get("incurred", ZERO) + m_total,
            "eligible": c1.get("eligible", ZERO) + m_total,
        }

    # University mappings
    map_stmt = select(BudgetCategoryMapping).where(
        BudgetCategoryMapping.project_id == project_id
    )
    map_result = await db.execute(map_stmt)
    mappings = {
        m.ec_category: m for m in map_result.scalars().all()
    }

    lines: list[CostStatementLine] = []
    total_incurred = ZERO
    total_eligible = ZERO
    indirect_base = ZERO

    for cat in ECBudgetCategory:
        if cat == ECBudgetCategory.E_INDIRECT:
            continue
        data = cat_data.get(cat, {})
        incurred = data.get("incurred", ZERO)
        eligible = data.get("eligible", ZERO)
        mapping = mappings.get(cat)

        lines.append(
            CostStatementLine(
                ec_category=cat,
                university_account_code=(
                    mapping.university_account_code if mapping else None
                ),
                university_category_name=(
                    mapping.university_category_name if mapping else None
                ),
                budgeted=ZERO,  # Would come from budget plan
                incurred=incurred,
                ec_eligible_amount=eligible,
            )
        )
        total_incurred += incurred
        total_eligible += eligible
        if cat in INDIRECT_BASE_CATEGORIES:
            indirect_base += incurred

    # Indirect costs
    indirect = ZERO
    if project.cost_model != CostModel.LUMP_SUM:
        indirect = _q(indirect_base * INDIRECT_RATE)

    return CostStatementResponse(
        project_id=project_id,
        acronym=project.acronym,
        period_start=period_start,
        period_end=period_end,
        lines=lines,
        total_incurred=total_incurred,
        total_eligible=total_eligible,
        indirect_costs=indirect,
        grand_total=total_eligible + indirect,
    )


# --- Overhead Calculations ---


async def get_overhead_calculations(
    db: AsyncSession,
    project_id: uuid.UUID,
) -> OverheadCalculationResponse:
    """Calculate overhead costs for a project."""
    proj_stmt = select(Project).where(
        Project.id == project_id, Project.deleted_at.is_(None)
    )
    project = (await db.execute(proj_stmt)).scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    # Expenses by category
    exp_stmt = (
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
    exp_result = await db.execute(exp_stmt)
    cat_spending = {
        row[0]: _q(row[1]) for row in exp_result.all() if row[0]
    }

    # Add missions to C1_TRAVEL
    m_stmt = select(
        func.coalesce(func.sum(Mission.total_cost), 0)
    ).where(
        Mission.project_id == project_id,
        Mission.deleted_at.is_(None),
    )
    m_total = _q((await db.execute(m_stmt)).scalar_one())
    if m_total > ZERO:
        cat_spending[ECBudgetCategory.C1_TRAVEL] = (
            cat_spending.get(ECBudgetCategory.C1_TRAVEL, ZERO) + m_total
        )

    # Build breakdown
    breakdown = [
        OverheadCategoryBreakdown(category=cat, amount=amt)
        for cat, amt in sorted(
            cat_spending.items(), key=lambda x: x[0].value
        )
    ]

    # Calculate indirect
    sub_excluded = cat_spending.get(
        ECBudgetCategory.B_SUBCONTRACTING, ZERO
    )
    indirect_base = sum(
        amt for cat, amt in cat_spending.items()
        if cat in INDIRECT_BASE_CATEGORIES
    )

    indirect = ZERO
    if project.cost_model != CostModel.LUMP_SUM:
        indirect = _q(indirect_base * INDIRECT_RATE)

    return OverheadCalculationResponse(
        project_id=project_id,
        acronym=project.acronym,
        cost_model=project.cost_model,
        direct_costs_base=_q(indirect_base),
        indirect_rate=INDIRECT_RATE,
        indirect_costs=indirect,
        subcontracting_excluded=sub_excluded,
        breakdown=breakdown,
    )


# --- Annual Summary ---


async def get_annual_summary(
    db: AsyncSession,
    year: int,
    project_id: uuid.UUID | None = None,
) -> AnnualSummaryResponse:
    """Generate annual summary report."""
    year_start = date(year, 1, 1)
    year_end = date(year, 12, 31)

    proj_stmt = select(Project).where(Project.deleted_at.is_(None))
    if project_id is not None:
        proj_stmt = proj_stmt.where(Project.id == project_id)
    projects = list(
        (await db.execute(proj_stmt)).scalars().all()
    )

    if project_id and not projects:
        raise HTTPException(
            status_code=404, detail="Project not found"
        )

    summary_projects: list[AnnualSummaryProject] = []
    grand_budget = ZERO
    grand_spent_year = ZERO
    grand_spent_cumulative = ZERO

    for proj in projects:
        budget = _q(proj.total_budget)
        eu_contrib = _q(proj.eu_contribution)

        # Year expenses by category
        yr_stmt = (
            select(
                Expense.ec_category,
                func.coalesce(func.sum(Expense.amount_gross), 0),
            )
            .where(
                Expense.project_id == proj.id,
                Expense.deleted_at.is_(None),
                Expense.date_incurred >= year_start,
                Expense.date_incurred <= year_end,
            )
            .group_by(Expense.ec_category)
        )
        yr_result = await db.execute(yr_stmt)
        yr_cats = {
            row[0]: _q(row[1]) for row in yr_result.all() if row[0]
        }
        spent_year = sum(yr_cats.values(), ZERO)

        # Cumulative expenses
        cum_stmt = select(
            func.coalesce(func.sum(Expense.amount_gross), 0)
        ).where(
            Expense.project_id == proj.id,
            Expense.deleted_at.is_(None),
            Expense.date_incurred <= year_end,
        )
        spent_cumulative = _q(
            (await db.execute(cum_stmt)).scalar_one()
        )

        # Fund distributions
        fd_yr_stmt = select(
            func.coalesce(func.sum(FundDistribution.amount), 0)
        ).where(
            FundDistribution.project_id == proj.id,
            FundDistribution.distribution_date >= year_start,
            FundDistribution.distribution_date <= year_end,
        )
        funds_year = _q((await db.execute(fd_yr_stmt)).scalar_one())

        fd_cum_stmt = select(
            func.coalesce(func.sum(FundDistribution.amount), 0)
        ).where(
            FundDistribution.project_id == proj.id,
            FundDistribution.distribution_date <= year_end,
        )
        funds_cumulative = _q(
            (await db.execute(fd_cum_stmt)).scalar_one()
        )

        # PM data
        pm_planned_stmt = select(
            func.coalesce(func.sum(EffortAllocation.planned_pm), 0)
        ).where(
            EffortAllocation.project_id == proj.id,
            EffortAllocation.period_start <= year_end,
            EffortAllocation.period_end >= year_start,
        )
        pm_planned = _q(
            (await db.execute(pm_planned_stmt)).scalar_one()
        )

        pm_hours_stmt = select(
            func.coalesce(func.sum(TimesheetEntry.hours), 0)
        ).where(
            TimesheetEntry.project_id == proj.id,
            TimesheetEntry.date >= year_start,
            TimesheetEntry.date <= year_end,
        )
        pm_hours = _q(
            (await db.execute(pm_hours_stmt)).scalar_one()
        )
        pm_actual = calculate_person_months(pm_hours, 1720)

        spending_by_cat = [
            AnnualCategorySpending(category=cat, amount=amt)
            for cat, amt in sorted(
                yr_cats.items(), key=lambda x: x[0].value
            )
        ]

        summary_projects.append(
            AnnualSummaryProject(
                project_id=proj.id,
                acronym=proj.acronym,
                year=year,
                total_budget=budget,
                eu_contribution=eu_contrib,
                total_spent_year=spent_year,
                total_spent_cumulative=spent_cumulative,
                budget_remaining=budget - spent_cumulative,
                spending_by_category=spending_by_cat,
                pm_planned=pm_planned,
                pm_actual=pm_actual,
                funds_received_cumulative=funds_cumulative,
                funds_received_year=funds_year,
            )
        )

        grand_budget += budget
        grand_spent_year += spent_year
        grand_spent_cumulative += spent_cumulative

    return AnnualSummaryResponse(
        year=year,
        projects=summary_projects,
        total_budget=grand_budget,
        total_spent_year=grand_spent_year,
        total_spent_cumulative=grand_spent_cumulative,
    )
