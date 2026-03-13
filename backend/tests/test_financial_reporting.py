"""Tests for cost-model-aware financial reporting (Section 8.3)."""

import uuid
from datetime import date, timedelta
from decimal import Decimal

import pytest
import pytest_asyncio
from fastapi import HTTPException

from app.models.enums import (
    CFSStatus,
    CompletionStatus,
    CostModel,
    ECBudgetCategory,
    FinancialStatementStatus,
    Programme,
    ProjectRole,
    UnitCostStatus,
    UnitType,
)
from app.models.financial import BudgetCategoryMapping, Expense
from app.models.financial_reporting import (
    FinancialStatement,
    UnitDeliveryRecord,
    WPCompletionDeclaration,
)
from app.models.project import Project
from app.models.reporting import ReportingPeriod
from app.models.work_package import WorkPackage
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


# --- Fixtures ---


@pytest_asyncio.fixture
async def actual_cost_project(db):
    """Create an actual-cost project."""
    p = Project(
        acronym="ACTCOST",
        full_title="Actual Cost Test Project",
        programme=Programme.HORIZON_EUROPE,
        cost_model=CostModel.ACTUAL_COSTS,
        role=ProjectRole.COORDINATOR,
        start_date=date(2024, 1, 1),
        end_date=date(2027, 6, 30),
        duration_months=42,
        total_budget=Decimal("1000000.00"),
        eu_contribution=Decimal("800000.00"),
        funding_rate=Decimal("80.00"),
    )
    db.add(p)
    await db.flush()
    await db.refresh(p)
    return p


@pytest_asyncio.fixture
async def lump_sum_project(db):
    """Create a lump-sum project."""
    p = Project(
        acronym="LUMPSUM",
        full_title="Lump Sum Test Project",
        programme=Programme.HORIZON_EUROPE,
        cost_model=CostModel.LUMP_SUM,
        role=ProjectRole.COORDINATOR,
        start_date=date(2024, 1, 1),
        end_date=date(2026, 12, 31),
        duration_months=36,
        total_budget=Decimal("500000.00"),
        eu_contribution=Decimal("500000.00"),
    )
    db.add(p)
    await db.flush()
    await db.refresh(p)
    return p


@pytest_asyncio.fixture
async def unit_cost_project(db):
    """Create a unit-cost project."""
    p = Project(
        acronym="UNITCST",
        full_title="Unit Cost Test Project",
        programme=Programme.DIGITAL_EUROPE,
        cost_model=CostModel.UNIT_COSTS,
        role=ProjectRole.PARTNER,
        start_date=date(2024, 6, 1),
        end_date=date(2026, 5, 31),
        duration_months=24,
        total_budget=Decimal("300000.00"),
        eu_contribution=Decimal("240000.00"),
        funding_rate=Decimal("80.00"),
    )
    db.add(p)
    await db.flush()
    await db.refresh(p)
    return p


@pytest_asyncio.fixture
async def reporting_period(db, actual_cost_project):
    """Create a reporting period."""
    rp = ReportingPeriod(
        project_id=actual_cost_project.id,
        period_number=1,
        start_date=date(2024, 1, 1),
        end_date=date(2025, 6, 30),
        technical_report_deadline=date(2025, 8, 29),
    )
    db.add(rp)
    await db.flush()
    await db.refresh(rp)
    return rp


@pytest_asyncio.fixture
async def lump_sum_period(db, lump_sum_project):
    """Create a reporting period for lump sum project."""
    rp = ReportingPeriod(
        project_id=lump_sum_project.id,
        period_number=1,
        start_date=date(2024, 1, 1),
        end_date=date(2025, 6, 30),
        technical_report_deadline=date(2025, 8, 29),
    )
    db.add(rp)
    await db.flush()
    await db.refresh(rp)
    return rp


@pytest_asyncio.fixture
async def unit_cost_period(db, unit_cost_project):
    """Create a reporting period for unit cost project."""
    rp = ReportingPeriod(
        project_id=unit_cost_project.id,
        period_number=1,
        start_date=date(2024, 6, 1),
        end_date=date(2025, 5, 31),
        technical_report_deadline=date(2025, 7, 30),
    )
    db.add(rp)
    await db.flush()
    await db.refresh(rp)
    return rp


@pytest_asyncio.fixture
async def work_package(db, lump_sum_project):
    """Create a work package for lump sum project."""
    wp = WorkPackage(
        project_id=lump_sum_project.id,
        wp_number=1,
        title="WP1 - Research",
        start_month=1,
        end_month=18,
        total_pm=Decimal("24.00"),
    )
    db.add(wp)
    await db.flush()
    await db.refresh(wp)
    return wp


async def _add_expenses(db, project_id, period_start, period_end):
    """Add sample expenses across EC categories."""
    expenses = [
        Expense(
            project_id=project_id,
            description="Researcher salary",
            amount_gross=Decimal("50000.00"),
            date_incurred=period_start + timedelta(days=30),
            ec_category=ECBudgetCategory.A_PERSONNEL,
            ec_eligible=True,
        ),
        Expense(
            project_id=project_id,
            description="Subcontractor",
            amount_gross=Decimal("20000.00"),
            date_incurred=period_start + timedelta(days=60),
            ec_category=ECBudgetCategory.B_SUBCONTRACTING,
            ec_eligible=True,
        ),
        Expense(
            project_id=project_id,
            description="Conference travel",
            amount_gross=Decimal("5000.00"),
            date_incurred=period_start + timedelta(days=90),
            ec_category=ECBudgetCategory.C1_TRAVEL,
            ec_eligible=True,
        ),
        Expense(
            project_id=project_id,
            description="Server equipment",
            amount_gross=Decimal("10000.00"),
            date_incurred=period_start + timedelta(days=120),
            ec_category=ECBudgetCategory.D_OTHER_COSTS,
            ec_eligible=True,
        ),
    ]
    for e in expenses:
        db.add(e)
    await db.flush()
    return expenses


# --- Financial Statement (Form C) Tests ---


class TestFinancialStatement:
    """Tests for Form C financial statement generation and workflow."""

    async def test_generate_financial_statement(
        self, db, actual_cost_project, reporting_period
    ):
        """Generate a financial statement from expenses."""
        await _add_expenses(
            db, actual_cost_project.id,
            reporting_period.start_date, reporting_period.end_date,
        )

        stmt = await generate_financial_statement(
            db, actual_cost_project.id, reporting_period.id
        )

        assert stmt.status == FinancialStatementStatus.DRAFT
        assert stmt.category_a_personnel == Decimal("50000.00")
        assert stmt.category_b_subcontracting == Decimal("20000.00")
        # C1_TRAVEL goes into category_c_travel
        assert stmt.total_direct_costs > Decimal("0.00")
        # Indirect = 25% on (A + C + D) = 25% * (50000 + 5000 + 10000) = 16250
        assert stmt.indirect_costs == Decimal("16250.00")

    async def test_generate_duplicate_rejected(
        self, db, actual_cost_project, reporting_period
    ):
        """Generating a duplicate statement raises 409."""
        await generate_financial_statement(
            db, actual_cost_project.id, reporting_period.id
        )

        with pytest.raises(HTTPException) as exc:
            await generate_financial_statement(
                db, actual_cost_project.id, reporting_period.id
            )
        assert exc.value.status_code == 409

    async def test_list_financial_statements(
        self, db, actual_cost_project, reporting_period
    ):
        """List financial statements for a project."""
        await generate_financial_statement(
            db, actual_cost_project.id, reporting_period.id
        )

        items = await list_financial_statements(db, actual_cost_project.id)
        assert len(items) == 1
        assert items[0].project_id == actual_cost_project.id

    async def test_advance_workflow(
        self, db, actual_cost_project, reporting_period
    ):
        """Advance through the full approval workflow."""
        stmt = await generate_financial_statement(
            db, actual_cost_project.id, reporting_period.id
        )
        assert stmt.status == FinancialStatementStatus.DRAFT

        # DRAFT -> PARTNER_SUBMITTED
        stmt = await advance_financial_statement_status(
            db, stmt.id, "Partner User"
        )
        assert stmt.status == FinancialStatementStatus.PARTNER_SUBMITTED
        assert stmt.partner_signed_by == "Partner User"
        assert stmt.partner_signed_at is not None

        # PARTNER_SUBMITTED -> COORDINATOR_REVIEW
        stmt = await advance_financial_statement_status(db, stmt.id)
        assert stmt.status == FinancialStatementStatus.COORDINATOR_REVIEW

        # COORDINATOR_REVIEW -> COORDINATOR_APPROVED
        stmt = await advance_financial_statement_status(
            db, stmt.id, "Coordinator"
        )
        assert stmt.status == FinancialStatementStatus.COORDINATOR_APPROVED
        assert stmt.coordinator_approved_by == "Coordinator"

        # COORDINATOR_APPROVED -> REPORTED_TO_EC
        stmt = await advance_financial_statement_status(db, stmt.id)
        assert stmt.status == FinancialStatementStatus.REPORTED_TO_EC
        assert stmt.reported_to_ec_at is not None

        # REPORTED_TO_EC -> EC_APPROVED
        stmt = await advance_financial_statement_status(db, stmt.id)
        assert stmt.status == FinancialStatementStatus.EC_APPROVED

    async def test_advance_from_terminal_fails(
        self, db, actual_cost_project, reporting_period
    ):
        """Cannot advance from EC_APPROVED."""
        stmt = await generate_financial_statement(
            db, actual_cost_project.id, reporting_period.id
        )
        # Move to terminal
        for _ in range(5):
            stmt = await advance_financial_statement_status(db, stmt.id)

        with pytest.raises(HTTPException) as exc:
            await advance_financial_statement_status(db, stmt.id)
        assert exc.value.status_code == 400

    async def test_cfs_tracking(self, db, actual_cost_project, reporting_period):
        """CFS required when cumulative > EUR 430k."""
        # Add large expenses
        e = Expense(
            project_id=actual_cost_project.id,
            description="Large personnel",
            amount_gross=Decimal("500000.00"),
            date_incurred=date(2024, 6, 1),
            ec_category=ECBudgetCategory.A_PERSONNEL,
            ec_eligible=True,
        )
        db.add(e)
        await db.flush()

        stmt = await generate_financial_statement(
            db, actual_cost_project.id, reporting_period.id
        )
        # 500k direct + 25% indirect on 500k = 625k > 430k
        assert stmt.cfs_required is True
        assert stmt.cfs_status == CFSStatus.PENDING


# --- WP Completion Declaration Tests ---


class TestWPCompletionDeclaration:
    """Tests for lump sum WP completion declarations."""

    async def test_create_declaration(
        self, db, lump_sum_project, lump_sum_period, work_package
    ):
        """Create a WP completion declaration."""
        decl = await create_wp_completion_declaration(
            db,
            lump_sum_project.id,
            lump_sum_period.id,
            work_package.id,
            Decimal("150000.00"),
        )

        assert decl.completion_status == CompletionStatus.NOT_STARTED
        assert decl.lump_sum_amount == Decimal("150000.00")
        assert decl.amount_claimed == Decimal("0.00")

    async def test_create_duplicate_rejected(
        self, db, lump_sum_project, lump_sum_period, work_package
    ):
        """Duplicate WP/period declaration is rejected."""
        await create_wp_completion_declaration(
            db, lump_sum_project.id, lump_sum_period.id,
            work_package.id, Decimal("150000.00"),
        )
        with pytest.raises(HTTPException) as exc:
            await create_wp_completion_declaration(
                db, lump_sum_project.id, lump_sum_period.id,
                work_package.id, Decimal("150000.00"),
            )
        assert exc.value.status_code == 409

    async def test_complete_declaration(
        self, db, lump_sum_project, lump_sum_period, work_package
    ):
        """Mark a declaration as completed."""
        decl = await create_wp_completion_declaration(
            db, lump_sum_project.id, lump_sum_period.id,
            work_package.id, Decimal("150000.00"),
        )

        decl = await update_wp_completion_declaration(db, decl.id, {
            "completion_status": CompletionStatus.COMPLETED,
            "declared_by": "PI User",
        })

        assert decl.completion_status == CompletionStatus.COMPLETED
        assert decl.completion_percentage == 100
        assert decl.amount_claimed == Decimal("150000.00")
        assert decl.declared_at is not None

    async def test_partial_completion(
        self, db, lump_sum_project, lump_sum_period, work_package
    ):
        """Partial completion calculates proportional claim."""
        decl = await create_wp_completion_declaration(
            db, lump_sum_project.id, lump_sum_period.id,
            work_package.id, Decimal("100000.00"),
        )

        decl = await update_wp_completion_declaration(db, decl.id, {
            "completion_status": CompletionStatus.PARTIALLY_COMPLETED,
            "completion_percentage": 60,
            "partial_completion_justification": "Deliverables 1.1 and 1.2 done",
        })

        assert decl.completion_percentage == 60
        assert decl.amount_claimed == Decimal("60000.00")

    async def test_list_declarations(
        self, db, lump_sum_project, lump_sum_period, work_package
    ):
        """List declarations for a project."""
        await create_wp_completion_declaration(
            db, lump_sum_project.id, lump_sum_period.id,
            work_package.id, Decimal("150000.00"),
        )

        items = await list_wp_completion_declarations(db, lump_sum_project.id)
        assert len(items) == 1


# --- Unit Delivery Record Tests ---


class TestUnitDeliveryRecord:
    """Tests for unit cost delivery tracking."""

    async def test_create_record(
        self, db, unit_cost_project, unit_cost_period
    ):
        """Create a unit delivery record."""
        record = await create_unit_delivery_record(
            db, unit_cost_project.id, unit_cost_period.id,
            {
                "description": "Training sessions",
                "unit_type": UnitType.TRAINING_HOUR,
                "planned_units": Decimal("100.00"),
                "unit_rate": Decimal("250.00"),
            },
        )

        assert record.status == UnitCostStatus.PLANNED
        assert record.planned_units == Decimal("100.00")
        assert record.unit_rate == Decimal("250.00")
        assert record.total_cost == Decimal("0.00")  # No actual yet

    async def test_update_actual_units(
        self, db, unit_cost_project, unit_cost_period
    ):
        """Update actual units recalculates total cost."""
        record = await create_unit_delivery_record(
            db, unit_cost_project.id, unit_cost_period.id,
            {
                "description": "Publications",
                "unit_type": UnitType.PUBLICATION,
                "planned_units": Decimal("5.00"),
                "unit_rate": Decimal("1500.00"),
            },
        )

        record = await update_unit_delivery_record(db, record.id, {
            "actual_units": Decimal("3.00"),
            "status": UnitCostStatus.REPORTED,
            "reported_by": "Researcher",
        })

        assert record.actual_units == Decimal("3.00")
        assert record.total_cost == Decimal("4500.00")  # 3 * 1500
        assert record.status == UnitCostStatus.REPORTED
        assert record.reported_at is not None

    async def test_list_records(
        self, db, unit_cost_project, unit_cost_period
    ):
        """List unit delivery records."""
        await create_unit_delivery_record(
            db, unit_cost_project.id, unit_cost_period.id,
            {
                "description": "Events organized",
                "unit_type": UnitType.EVENT,
                "planned_units": Decimal("3.00"),
                "unit_rate": Decimal("5000.00"),
            },
        )

        items = await list_unit_delivery_records(db, unit_cost_project.id)
        assert len(items) == 1


# --- Cost-Model-Aware Report Tests ---


class TestCostModelReports:
    """Tests for cost-model-aware report generation."""

    async def test_form_c_report(
        self, db, actual_cost_project, reporting_period
    ):
        """Generate Form C report for actual cost project."""
        await _add_expenses(
            db, actual_cost_project.id,
            reporting_period.start_date, reporting_period.end_date,
        )

        report = await generate_form_c_report(
            db, actual_cost_project.id, reporting_period.id
        )

        assert report.project_acronym == "ACTCOST"
        assert len(report.category_breakdown) > 0
        assert report.indirect_rate == Decimal("0.25")
        assert report.total_direct_costs > Decimal("0.00")
        assert report.indirect_costs > Decimal("0.00")

    async def test_lump_sum_report(
        self, db, lump_sum_project, lump_sum_period, work_package
    ):
        """Generate lump sum report from declarations."""
        await create_wp_completion_declaration(
            db, lump_sum_project.id, lump_sum_period.id,
            work_package.id, Decimal("150000.00"),
        )

        report = await generate_lump_sum_report(
            db, lump_sum_project.id, lump_sum_period.id
        )

        assert report.project_acronym == "LUMPSUM"
        assert len(report.declarations) == 1
        assert report.total_lump_sum == Decimal("150000.00")

    async def test_unit_cost_report(
        self, db, unit_cost_project, unit_cost_period
    ):
        """Generate unit cost report."""
        record = await create_unit_delivery_record(
            db, unit_cost_project.id, unit_cost_period.id,
            {
                "description": "Training",
                "unit_type": UnitType.TRAINING_HOUR,
                "planned_units": Decimal("50.00"),
                "unit_rate": Decimal("200.00"),
            },
        )
        await update_unit_delivery_record(db, record.id, {
            "actual_units": Decimal("40.00"),
        })

        report = await generate_unit_cost_report(
            db, unit_cost_project.id, unit_cost_period.id
        )

        assert report.project_acronym == "UNITCST"
        assert len(report.records) == 1
        assert report.total_planned_cost == Decimal("10000.00")  # 50 * 200
        assert report.total_actual_cost == Decimal("8000.00")  # 40 * 200

    async def test_institutional_report(
        self, db, actual_cost_project, reporting_period
    ):
        """Generate institutional parallel report."""
        await _add_expenses(
            db, actual_cost_project.id,
            reporting_period.start_date, reporting_period.end_date,
        )

        # Add a university mapping
        mapping = BudgetCategoryMapping(
            project_id=actual_cost_project.id,
            ec_category=ECBudgetCategory.A_PERSONNEL,
            university_account_code="641100",
            university_category_name="Personnel Costs",
        )
        db.add(mapping)
        await db.flush()

        report = await generate_institutional_report(
            db, actual_cost_project.id,
            reporting_period.start_date, reporting_period.end_date,
        )

        assert report.project_acronym == "ACTCOST"
        assert len(report.rows) > 0
        assert report.total_ec > Decimal("0.00")

    async def test_cost_model_aware_actual(
        self, db, actual_cost_project, reporting_period
    ):
        """Cost-model-aware report returns Form C for actual costs."""
        await _add_expenses(
            db, actual_cost_project.id,
            reporting_period.start_date, reporting_period.end_date,
        )

        report = await get_cost_model_financial_report(
            db, actual_cost_project.id, reporting_period.id
        )

        assert report.cost_model == "ACTUAL_COSTS"
        assert report.form_c is not None
        assert report.lump_sum is None
        assert report.unit_cost is None
        assert report.institutional_report is not None

    async def test_cost_model_aware_lump_sum(
        self, db, lump_sum_project, lump_sum_period, work_package
    ):
        """Cost-model-aware report returns lump sum for lump sum projects."""
        await create_wp_completion_declaration(
            db, lump_sum_project.id, lump_sum_period.id,
            work_package.id, Decimal("100000.00"),
        )

        report = await get_cost_model_financial_report(
            db, lump_sum_project.id, lump_sum_period.id
        )

        assert report.cost_model == "LUMP_SUM"
        assert report.form_c is None
        assert report.lump_sum is not None
        assert report.unit_cost is None

    async def test_cost_model_aware_unit_cost(
        self, db, unit_cost_project, unit_cost_period
    ):
        """Cost-model-aware report returns unit cost for unit cost projects."""
        await create_unit_delivery_record(
            db, unit_cost_project.id, unit_cost_period.id,
            {
                "description": "Datasets",
                "unit_type": UnitType.DATASET,
                "planned_units": Decimal("10.00"),
                "unit_rate": Decimal("5000.00"),
            },
        )

        report = await get_cost_model_financial_report(
            db, unit_cost_project.id, unit_cost_period.id
        )

        assert report.cost_model == "UNIT_COSTS"
        assert report.form_c is None
        assert report.lump_sum is None
        assert report.unit_cost is not None

    async def test_cost_model_without_period(
        self, db, actual_cost_project
    ):
        """Cost-model-aware report without period returns institutional only."""
        report = await get_cost_model_financial_report(
            db, actual_cost_project.id
        )

        assert report.form_c is None
        assert report.institutional_report is not None
