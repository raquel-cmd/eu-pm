"""Tests for Section 10 — Role-Based Dashboards."""

import uuid
from datetime import date, timedelta
from decimal import Decimal

import pytest
import pytest_asyncio

from app.models.additional_features import Amendment
from app.models.enums import (
    AmendmentStatus,
    AmendmentType,
    ContractType,
    CostModel,
    DeliverableType,
    DisseminationLevel,
    ECBudgetCategory,
    ECReviewStatus,
    Programme,
    ProjectRole,
    ResearcherPosition,
    RiskCategory,
    RiskLevel,
    RiskStatus,
    TrafficLight,
    WPStatus,
)
from app.models.financial import Expense
from app.models.partner import Partner, ProjectPartner
from app.models.project import Project
from app.models.reporting import ReportingPeriod, Risk
from app.models.researcher import EffortAllocation, Researcher, TimesheetEntry
from app.models.work_package import Deliverable, WorkPackage
from app.services.dashboards import (
    get_pi_dashboard,
    get_project_dashboard,
    get_researcher_dashboard,
)


# ── Fixtures ─────────────────────────────────────────────


@pytest_asyncio.fixture
async def project(db):
    """Create a test project."""
    p = Project(
        acronym="DASH",
        full_title="Dashboard Test Project",
        programme=Programme.HORIZON_EUROPE,
        cost_model=CostModel.ACTUAL_COSTS,
        role=ProjectRole.COORDINATOR,
        total_budget=Decimal("500000.00"),
        start_date=date(2025, 1, 1),
        end_date=date(2027, 12, 31),
    )
    db.add(p)
    await db.flush()
    return p


@pytest_asyncio.fixture
async def project2(db):
    """Create a second test project."""
    p = Project(
        acronym="DASH2",
        full_title="Dashboard Test Project 2",
        programme=Programme.DIGITAL_EUROPE,
        cost_model=CostModel.ACTUAL_COSTS,
        role=ProjectRole.PARTNER,
        total_budget=Decimal("200000.00"),
        start_date=date(2025, 6, 1),
        end_date=date(2028, 5, 31),
    )
    db.add(p)
    await db.flush()
    return p


@pytest_asyncio.fixture
async def work_package(db, project):
    """Create a test work package."""
    wp = WorkPackage(
        project_id=project.id,
        wp_number=1,
        title="WP1 - Core Development",
        status=WPStatus.IN_PROGRESS,
        start_month=1,
        end_month=24,
        total_pm=Decimal("12.00"),
    )
    db.add(wp)
    await db.flush()
    return wp


@pytest_asyncio.fixture
async def deliverables(db, work_package):
    """Create test deliverables with mixed statuses."""
    d1 = Deliverable(
        work_package_id=work_package.id,
        deliverable_number="D1.1",
        title="Requirements Report",
        type=DeliverableType.REPORT,
        dissemination_level=DisseminationLevel.PU,
        due_month=6,
        submission_date=date(2025, 6, 15),
        ec_review_status=ECReviewStatus.APPROVED,
        traffic_light=TrafficLight.GREEN,
    )
    d2 = Deliverable(
        work_package_id=work_package.id,
        deliverable_number="D1.2",
        title="Software Prototype",
        type=DeliverableType.SOFTWARE,
        dissemination_level=DisseminationLevel.PU,
        due_month=12,
        ec_review_status=ECReviewStatus.PENDING,
        traffic_light=TrafficLight.AMBER,
    )
    d3 = Deliverable(
        work_package_id=work_package.id,
        deliverable_number="D1.3",
        title="Final Report",
        type=DeliverableType.REPORT,
        dissemination_level=DisseminationLevel.PU,
        due_month=24,
        ec_review_status=ECReviewStatus.PENDING,
        traffic_light=TrafficLight.GREEN,
    )
    db.add_all([d1, d2, d3])
    await db.flush()
    return [d1, d2, d3]


@pytest_asyncio.fixture
async def researcher(db):
    """Create a test researcher."""
    r = Researcher(
        name="Dr. Jane Smith",
        email="jane.smith@test.eu",
        position=ResearcherPosition.POSTDOC,
        contract_type=ContractType.DL57,
        fte=Decimal("1.00"),
    )
    db.add(r)
    await db.flush()
    return r


@pytest_asyncio.fixture
async def partner(db):
    """Create a test partner."""
    p = Partner(
        legal_name="Test University",
        short_name="TU",
        country="DE",
    )
    db.add(p)
    await db.flush()
    return p


# ── PI Dashboard Tests ───────────────────────────────────


class TestPIDashboard:
    """Tests for the PI portfolio dashboard."""

    @pytest.mark.asyncio
    async def test_empty_state(self, db):
        """PI dashboard with no projects returns empty response."""
        result = await get_pi_dashboard(db)
        assert result.projects == []
        assert result.cross_project_deadlines == []
        assert result.total_budget == Decimal("0.00")
        assert result.active_project_count == 0

    @pytest.mark.asyncio
    async def test_single_project_summary(self, db, project, work_package, deliverables):
        """PI dashboard shows correct project summary metrics."""
        result = await get_pi_dashboard(db)
        assert len(result.projects) == 1

        summary = result.projects[0]
        assert summary.acronym == "DASH"
        assert summary.programme == Programme.HORIZON_EUROPE
        # Has AMBER deliverable → traffic light AMBER
        assert summary.traffic_light == "AMBER"
        assert summary.budget_total == Decimal("500000.00")
        assert summary.budget_spent == Decimal("0.00")
        assert summary.burn_rate_pct == Decimal("0.00")

    @pytest.mark.asyncio
    async def test_traffic_light_red(self, db, project, work_package):
        """RED deliverable makes project traffic light RED."""
        d = Deliverable(
            work_package_id=work_package.id,
            deliverable_number="D1.1",
            title="Delayed Report",
            type=DeliverableType.REPORT,
            dissemination_level=DisseminationLevel.PU,
            due_month=3,
            traffic_light=TrafficLight.RED,
        )
        db.add(d)
        await db.flush()

        result = await get_pi_dashboard(db)
        assert result.projects[0].traffic_light == "RED"

    @pytest.mark.asyncio
    async def test_multi_project_aggregation(
        self, db, project, project2, work_package
    ):
        """PI dashboard aggregates metrics across multiple projects."""
        result = await get_pi_dashboard(db)
        assert len(result.projects) == 2
        assert result.total_budget == Decimal("700000.00")

    @pytest.mark.asyncio
    async def test_cross_project_deadlines(self, db, project):
        """Reporting period deadlines appear in cross-project deadlines."""
        future = date.today() + timedelta(days=30)
        rp = ReportingPeriod(
            project_id=project.id,
            period_number=1,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            technical_report_deadline=future,
        )
        db.add(rp)
        await db.flush()

        result = await get_pi_dashboard(db)
        assert len(result.cross_project_deadlines) >= 1
        dl = result.cross_project_deadlines[0]
        assert dl.project_acronym == "DASH"
        assert dl.deadline_type == "Technical Report"
        assert dl.days_until > 0

    @pytest.mark.asyncio
    async def test_open_risks_count(self, db, project, work_package):
        """Open risks are counted per project."""
        risk = Risk(
            project_id=project.id,
            description="Test risk",
            category=RiskCategory.TECHNICAL,
            probability=RiskLevel.HIGH,
            impact=RiskLevel.MEDIUM,
            status=RiskStatus.OPEN,
        )
        db.add(risk)
        await db.flush()

        result = await get_pi_dashboard(db)
        assert result.projects[0].open_risks == 1

    @pytest.mark.asyncio
    async def test_active_amendments_count(self, db, project):
        """Active amendments are counted per project."""
        amendment = Amendment(
            project_id=project.id,
            amendment_number=1,
            amendment_type=AmendmentType.BUDGET_TRANSFER,
            title="Budget reallocation",
            description="Transfer from WP1 to WP2",
            status=AmendmentStatus.SUBMITTED,
        )
        db.add(amendment)
        await db.flush()

        result = await get_pi_dashboard(db)
        assert result.projects[0].active_amendments == 1

    @pytest.mark.asyncio
    async def test_budget_health(self, db, project):
        """Budget spent and burn rate are calculated correctly."""
        expense = Expense(
            project_id=project.id,
            description="Personnel cost",
            amount_gross=Decimal("50000.00"),
            date_incurred=date(2025, 3, 1),
            ec_category=ECBudgetCategory.A_PERSONNEL,
        )
        db.add(expense)
        await db.flush()

        result = await get_pi_dashboard(db)
        summary = result.projects[0]
        assert summary.budget_spent == Decimal("50000.00")
        assert summary.burn_rate_pct == Decimal("10.00")


# ── Researcher Dashboard Tests ───────────────────────────


class TestResearcherDashboard:
    """Tests for the researcher personal dashboard."""

    @pytest.mark.asyncio
    async def test_researcher_not_found(self, db):
        """404 when researcher doesn't exist."""
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc:
            await get_researcher_dashboard(db, uuid.uuid4())
        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_allocations_shown(
        self, db, project, work_package, researcher
    ):
        """Researcher allocations are returned."""
        alloc = EffortAllocation(
            researcher_id=researcher.id,
            project_id=project.id,
            work_package_id=work_package.id,
            period_start=date(2025, 1, 1),
            period_end=date(2025, 6, 30),
            planned_pm=Decimal("3.00"),
        )
        db.add(alloc)
        await db.flush()

        result = await get_researcher_dashboard(db, researcher.id)
        assert result.researcher_name == "Dr. Jane Smith"
        assert len(result.allocations) == 1
        assert result.allocations[0].project_acronym == "DASH"
        assert result.allocations[0].planned_pm == Decimal("3.00")
        assert result.total_planned_pm == Decimal("3.00")

    @pytest.mark.asyncio
    async def test_timesheet_status(
        self, db, project, work_package, researcher
    ):
        """Timesheet status is calculated per month."""
        alloc = EffortAllocation(
            researcher_id=researcher.id,
            project_id=project.id,
            period_start=date(2025, 1, 1),
            period_end=date(2026, 12, 31),
            planned_pm=Decimal("6.00"),
        )
        db.add(alloc)
        await db.flush()

        result = await get_researcher_dashboard(db, researcher.id)
        # Should have timesheet entries for last 3 months
        assert len(result.timesheet_status) >= 1

    @pytest.mark.asyncio
    async def test_upcoming_deadlines(
        self, db, project, work_package, researcher
    ):
        """Upcoming reporting deadlines are listed."""
        alloc = EffortAllocation(
            researcher_id=researcher.id,
            project_id=project.id,
            period_start=date(2025, 1, 1),
            period_end=date(2026, 12, 31),
            planned_pm=Decimal("6.00"),
        )
        rp = ReportingPeriod(
            project_id=project.id,
            period_number=1,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            technical_report_deadline=date.today() + timedelta(days=60),
        )
        db.add_all([alloc, rp])
        await db.flush()

        result = await get_researcher_dashboard(db, researcher.id)
        report_deadlines = [
            d for d in result.upcoming_deadlines
            if d.deadline_type == "Technical Report"
        ]
        assert len(report_deadlines) == 1
        assert report_deadlines[0].project_acronym == "DASH"


# ── Project Dashboard Tests ──────────────────────────────


class TestProjectDashboard:
    """Tests for the project detail dashboard."""

    @pytest.mark.asyncio
    async def test_project_not_found(self, db):
        """404 when project doesn't exist."""
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc:
            await get_project_dashboard(db, uuid.uuid4())
        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_wp_progress(
        self, db, project, work_package, deliverables
    ):
        """WP progress is calculated from deliverable completion."""
        result = await get_project_dashboard(db, project.id)
        assert len(result.wp_progress) == 1

        wp = result.wp_progress[0]
        assert wp.wp_number == 1
        assert wp.deliverables_total == 3
        assert wp.deliverables_completed == 1  # Only D1.1 has submission_date
        assert wp.progress_pct == Decimal("33.33")

    @pytest.mark.asyncio
    async def test_deliverable_timeline(
        self, db, project, work_package, deliverables
    ):
        """All deliverables appear in the timeline."""
        result = await get_project_dashboard(db, project.id)
        assert len(result.deliverable_timeline) == 3
        assert result.deliverable_timeline[0].deliverable_number == "D1.1"

    @pytest.mark.asyncio
    async def test_budget_by_category(self, db, project):
        """Expenses are grouped by EC budget category."""
        e1 = Expense(
            project_id=project.id,
            description="Salary",
            amount_gross=Decimal("30000.00"),
            date_incurred=date(2025, 3, 1),
            ec_category=ECBudgetCategory.A_PERSONNEL,
        )
        e2 = Expense(
            project_id=project.id,
            description="Flight",
            amount_gross=Decimal("1500.00"),
            date_incurred=date(2025, 4, 1),
            ec_category=ECBudgetCategory.C1_TRAVEL,
        )
        db.add_all([e1, e2])
        await db.flush()

        result = await get_project_dashboard(db, project.id)
        cats = {c.category: c for c in result.budget_by_category}
        assert "A_PERSONNEL" in cats
        assert cats["A_PERSONNEL"].spent == Decimal("30000.00")
        assert "C1_TRAVEL" in cats
        assert cats["C1_TRAVEL"].spent == Decimal("1500.00")

    @pytest.mark.asyncio
    async def test_partner_status(self, db, project, partner):
        """Partner status includes allocated budget and spending."""
        pp = ProjectPartner(
            project_id=project.id,
            partner_id=partner.id,
            partner_budget=Decimal("100000.00"),
        )
        expense = Expense(
            project_id=project.id,
            partner_id=partner.id,
            description="Partner personnel",
            amount_gross=Decimal("25000.00"),
            date_incurred=date(2025, 5, 1),
            ec_category=ECBudgetCategory.A_PERSONNEL,
        )
        db.add_all([pp, expense])
        await db.flush()

        result = await get_project_dashboard(db, project.id)
        assert len(result.partner_status) == 1
        ps = result.partner_status[0]
        assert ps.partner_name == "Test University"
        assert ps.allocated_budget == Decimal("100000.00")
        assert ps.spent == Decimal("25000.00")
        assert ps.pct_used == Decimal("25.00")

    @pytest.mark.asyncio
    async def test_risk_summary(self, db, project):
        """Project risks are included in the dashboard."""
        risk = Risk(
            project_id=project.id,
            description="Key personnel leaving",
            category=RiskCategory.ORGANIZATIONAL,
            probability=RiskLevel.MEDIUM,
            impact=RiskLevel.HIGH,
            status=RiskStatus.OPEN,
            owner="PI",
        )
        db.add(risk)
        await db.flush()

        result = await get_project_dashboard(db, project.id)
        assert len(result.risks) == 1
        assert result.risks[0].category == RiskCategory.ORGANIZATIONAL
        assert result.risks[0].owner == "PI"

    @pytest.mark.asyncio
    async def test_burn_rate_and_metrics(
        self, db, project, work_package, deliverables
    ):
        """Key metrics (burn rate, deliverable completion) are correct."""
        expense = Expense(
            project_id=project.id,
            description="Equipment",
            amount_gross=Decimal("100000.00"),
            date_incurred=date(2025, 2, 1),
            ec_category=ECBudgetCategory.C2_EQUIPMENT,
        )
        db.add(expense)
        await db.flush()

        result = await get_project_dashboard(db, project.id)
        assert result.total_budget == Decimal("500000.00")
        assert result.total_spent == Decimal("100000.00")
        assert result.burn_rate == Decimal("20.00")
        assert result.burn_rate_status == "healthy"
        # 1 of 3 deliverables completed
        assert result.deliverable_completion_rate == Decimal("33.33")
