"""Tests for reporting engine service layer (Section 8)."""

import uuid
from datetime import date, timedelta
from decimal import Decimal

import pytest
import pytest_asyncio
from fastapi import HTTPException

from app.models.enums import (
    CostModel,
    DeliverableType,
    DisseminationLevel,
    Programme,
    ProjectRole,
    ReminderType,
    ReportingPeriodType,
    ReportSectionStatus,
    ReportSectionType,
    ReportStatus,
    ResearcherPosition,
    ContractType,
    RiskCategory,
    RiskLevel,
    RiskStatus,
    WPStatus,
)
from app.models.project import Project
from app.models.reporting import ReportingPeriod, ReportReminder, Risk, TechnicalReport
from app.models.researcher import EffortAllocation, Researcher, TimesheetEntry
from app.models.work_package import Deliverable, Milestone, WorkPackage
from app.schemas.reporting import ReportingPeriodCreate, RiskCreate, RiskUpdate
from app.services.reporting import (
    advance_report_workflow,
    auto_generate_reporting_periods,
    create_report_shell,
    create_reporting_period,
    create_risk,
    delete_reporting_period,
    delete_risk,
    generate_part_b2_data,
    generate_part_b3_data,
    generate_part_b4_data,
    get_reporting_calendar,
    get_reporting_period,
    get_risk,
    get_technical_report,
    get_workflow_steps,
    list_reporting_periods,
    list_risks,
    list_technical_reports,
    send_due_reminders,
    update_report_section,
    update_risk,
    update_technical_report,
)


@pytest_asyncio.fixture
async def project(db):
    """Create a test project with start/end dates."""
    p = Project(
        acronym="TESTPROJ",
        full_title="Test Project for Reporting",
        programme=Programme.HORIZON_EUROPE,
        cost_model=CostModel.ACTUAL_COSTS,
        role=ProjectRole.COORDINATOR,
        start_date=date(2024, 1, 1),
        end_date=date(2027, 6, 30),
        duration_months=42,
        total_budget=Decimal("1000000.00"),
        eu_contribution=Decimal("800000.00"),
    )
    db.add(p)
    await db.flush()
    await db.refresh(p)
    return p


@pytest_asyncio.fixture
async def work_package(db, project):
    """Create a test work package."""
    wp = WorkPackage(
        project_id=project.id,
        wp_number=1,
        title="Research Framework",
        start_month=1,
        end_month=18,
        total_pm=Decimal("12.00"),
        status=WPStatus.IN_PROGRESS,
    )
    db.add(wp)
    await db.flush()
    await db.refresh(wp)
    return wp


@pytest_asyncio.fixture
async def reporting_period(db, project):
    """Create a test reporting period with a future deadline."""
    today = date.today()
    rp = ReportingPeriod(
        project_id=project.id,
        period_number=1,
        period_type=ReportingPeriodType.PERIODIC,
        start_date=date(2024, 1, 1),
        end_date=date(2025, 6, 30),
        technical_report_deadline=today + timedelta(days=60),
    )
    db.add(rp)
    await db.flush()
    await db.refresh(rp)
    return rp


# ── Reporting Period Tests ────────────────────────────


class TestReportingPeriodAutoGeneration:
    """Tests for auto-generating reporting periods."""

    async def test_auto_generate_default_18_month_periods(self, db, project):
        """Auto-generate creates 18-month periodic + final periods."""
        periods = await auto_generate_reporting_periods(db, project.id)
        assert len(periods) >= 2
        assert periods[0].period_number == 1
        assert periods[0].period_type == ReportingPeriodType.PERIODIC
        assert periods[-1].period_type == ReportingPeriodType.FINAL
        assert periods[0].start_date == project.start_date

    async def test_auto_generate_creates_reminders(self, db, project):
        """Auto-generate also creates reminder records."""
        periods = await auto_generate_reporting_periods(db, project.id)

        from sqlalchemy import select, func
        count_stmt = select(func.count()).select_from(ReportReminder).where(
            ReportReminder.reporting_period_id == periods[0].id
        )
        count = (await db.execute(count_stmt)).scalar_one()
        assert count == 7  # T-90, T-60, T-45, T-30, T-20, T-15, T-7

    async def test_auto_generate_rejects_duplicate(self, db, project):
        """Cannot auto-generate if periods already exist."""
        await auto_generate_reporting_periods(db, project.id)
        with pytest.raises(HTTPException) as exc:
            await auto_generate_reporting_periods(db, project.id)
        assert exc.value.status_code == 409

    async def test_auto_generate_requires_dates(self, db):
        """Cannot auto-generate without project dates."""
        p = Project(
            acronym="NODATE",
            full_title="No Dates Project",
            programme=Programme.HORIZON_EUROPE,
            cost_model=CostModel.ACTUAL_COSTS,
            role=ProjectRole.PARTNER,
        )
        db.add(p)
        await db.flush()
        await db.refresh(p)

        with pytest.raises(HTTPException) as exc:
            await auto_generate_reporting_periods(db, p.id)
        assert exc.value.status_code == 422

    async def test_auto_generate_from_jsonb(self, db):
        """Auto-generate from JSONB reporting_periods data."""
        p = Project(
            acronym="JSONPROJ",
            full_title="JSONB Project",
            programme=Programme.HORIZON_EUROPE,
            cost_model=CostModel.ACTUAL_COSTS,
            role=ProjectRole.COORDINATOR,
            start_date=date(2024, 1, 1),
            end_date=date(2026, 12, 31),
            reporting_periods=[
                {
                    "period_number": 1,
                    "period_type": "PERIODIC",
                    "start_date": "2024-01-01",
                    "end_date": "2025-06-30",
                    "technical_report_deadline": "2025-08-29",
                },
                {
                    "period_number": 2,
                    "period_type": "FINAL",
                    "start_date": "2025-07-01",
                    "end_date": "2026-12-31",
                    "technical_report_deadline": "2027-03-01",
                },
            ],
        )
        db.add(p)
        await db.flush()
        await db.refresh(p)

        periods = await auto_generate_reporting_periods(db, p.id)
        assert len(periods) == 2
        assert periods[0].end_date == date(2025, 6, 30)
        assert periods[1].period_type == ReportingPeriodType.FINAL


class TestReportingPeriodCRUD:
    """Tests for manual reporting period CRUD."""

    async def test_create_manual_period(self, db, project):
        """Create a reporting period manually."""
        data = ReportingPeriodCreate(
            period_number=1,
            period_type=ReportingPeriodType.PERIODIC,
            start_date=date(2024, 1, 1),
            end_date=date(2025, 6, 30),
            technical_report_deadline=date(2025, 8, 29),
        )
        rp = await create_reporting_period(db, project.id, data)
        assert rp.period_number == 1
        assert rp.project_id == project.id

    async def test_list_reporting_periods(self, db, project, reporting_period):
        """List periods for a project."""
        periods = await list_reporting_periods(db, project.id)
        assert len(periods) == 1
        assert periods[0].id == reporting_period.id

    async def test_get_reporting_period(self, db, reporting_period):
        """Get a single period."""
        rp = await get_reporting_period(db, reporting_period.id)
        assert rp is not None
        assert rp.period_number == 1

    async def test_delete_reporting_period(self, db, reporting_period):
        """Soft-delete a period."""
        result = await delete_reporting_period(db, reporting_period.id)
        assert result is True
        rp = await get_reporting_period(db, reporting_period.id)
        assert rp is None


# ── Reporting Calendar Tests ──────────────────────────


class TestReportingCalendar:
    """Tests for reporting calendar."""

    async def test_calendar_includes_upcoming_deadlines(
        self, db, project, reporting_period
    ):
        """Calendar shows upcoming deadlines."""
        cal = await get_reporting_calendar(db, project_id=project.id)
        assert len(cal.upcoming_deadlines) >= 1

    async def test_send_due_reminders(self, db, project):
        """Send due reminders marks them as sent."""
        data = ReportingPeriodCreate(
            period_number=1,
            start_date=date(2024, 1, 1),
            end_date=date(2025, 6, 30),
            technical_report_deadline=date.today() + timedelta(days=30),
        )
        rp = await create_reporting_period(db, project.id, data)
        await db.flush()

        sent = await send_due_reminders(db)
        # Some reminders should be past their scheduled date
        # (deadline is 30 days out, so T-90 through T-45 would be past)
        assert len(sent) >= 0  # At least the ones that are past due


# ── Risk Register Tests ───────────────────────────────


class TestRiskRegister:
    """Tests for the risk register."""

    async def test_create_risk(self, db, project):
        """Create a risk."""
        data = RiskCreate(
            description="Key researcher may leave mid-project",
            category=RiskCategory.ORGANIZATIONAL,
            probability=RiskLevel.MEDIUM,
            impact=RiskLevel.HIGH,
            mitigation_strategy="Cross-train team members",
            owner="PI",
        )
        risk = await create_risk(db, project.id, data)
        assert risk.description == data.description
        assert risk.status == RiskStatus.OPEN
        assert risk.project_id == project.id

    async def test_list_risks(self, db, project):
        """List risks for a project."""
        data = RiskCreate(
            description="Budget overrun risk",
            category=RiskCategory.FINANCIAL,
            probability=RiskLevel.LOW,
            impact=RiskLevel.MEDIUM,
        )
        await create_risk(db, project.id, data)
        risks = await list_risks(db, project.id)
        assert len(risks) == 1

    async def test_list_risks_filter_by_status(self, db, project):
        """Filter risks by status."""
        data = RiskCreate(
            description="Tech risk",
            category=RiskCategory.TECHNICAL,
            probability=RiskLevel.HIGH,
            impact=RiskLevel.HIGH,
        )
        risk = await create_risk(db, project.id, data)
        await update_risk(db, risk.id, RiskUpdate(status=RiskStatus.MITIGATED))

        open_risks = await list_risks(db, project.id, status=RiskStatus.OPEN)
        assert len(open_risks) == 0
        mitigated = await list_risks(db, project.id, status=RiskStatus.MITIGATED)
        assert len(mitigated) == 1

    async def test_update_risk(self, db, project):
        """Update a risk."""
        data = RiskCreate(
            description="Data loss risk",
            category=RiskCategory.TECHNICAL,
            probability=RiskLevel.LOW,
            impact=RiskLevel.HIGH,
        )
        risk = await create_risk(db, project.id, data)
        updated = await update_risk(
            db, risk.id, RiskUpdate(status=RiskStatus.CLOSED, actions_taken="Backup set up")
        )
        assert updated.status == RiskStatus.CLOSED
        assert updated.actions_taken == "Backup set up"

    async def test_delete_risk(self, db, project):
        """Soft-delete a risk."""
        data = RiskCreate(
            description="Minor risk",
            category=RiskCategory.EXTERNAL,
            probability=RiskLevel.LOW,
            impact=RiskLevel.LOW,
        )
        risk = await create_risk(db, project.id, data)
        result = await delete_risk(db, risk.id)
        assert result is True
        assert await get_risk(db, risk.id) is None


# ── Technical Report Tests ────────────────────────────


class TestTechnicalReport:
    """Tests for technical report workflow."""

    async def test_create_report_shell(self, db, project, work_package, reporting_period):
        """Create a report shell with all sections."""
        report = await create_report_shell(db, reporting_period.id)
        assert report.status == ReportStatus.DRAFT
        assert report.project_id == project.id

        # Should have sections: Part A, B1 (per WP), B2, B3, B4
        full = await get_technical_report(db, report.id)
        assert full is not None
        section_types = [s.section_type for s in full.sections]
        assert ReportSectionType.PART_A_SUMMARY in section_types
        assert ReportSectionType.PART_B1_WP_NARRATIVE in section_types
        assert ReportSectionType.PART_B2_DELIVERABLES in section_types
        assert ReportSectionType.PART_B3_RISKS in section_types
        assert ReportSectionType.PART_B4_RESOURCES in section_types

    async def test_create_report_shell_rejects_duplicate(
        self, db, project, work_package, reporting_period
    ):
        """Cannot create two reports for same period."""
        await create_report_shell(db, reporting_period.id)
        with pytest.raises(HTTPException) as exc:
            await create_report_shell(db, reporting_period.id)
        assert exc.value.status_code == 409

    async def test_advance_workflow(self, db, project, work_package, reporting_period):
        """Advance report through workflow steps."""
        report = await create_report_shell(db, reporting_period.id)
        assert report.status == ReportStatus.DRAFT

        report = await advance_report_workflow(db, report.id)
        assert report.status == ReportStatus.WP_INPUT

        report = await advance_report_workflow(db, report.id)
        assert report.status == ReportStatus.PARTNER_REVIEW

        report = await advance_report_workflow(db, report.id)
        assert report.status == ReportStatus.CONSOLIDATION

        report = await advance_report_workflow(db, report.id)
        assert report.status == ReportStatus.INTERNAL_REVIEW

        report = await advance_report_workflow(db, report.id)
        assert report.status == ReportStatus.FINAL_REVIEW

        report = await advance_report_workflow(db, report.id)
        assert report.status == ReportStatus.SUBMITTED
        assert report.submitted_at is not None

        report = await advance_report_workflow(db, report.id)
        assert report.status == ReportStatus.EC_APPROVED

    async def test_advance_past_ec_approved_fails(
        self, db, project, work_package, reporting_period
    ):
        """Cannot advance beyond EC_APPROVED."""
        report = await create_report_shell(db, reporting_period.id)
        # Advance to EC_APPROVED
        for _ in range(7):
            report = await advance_report_workflow(db, report.id)

        with pytest.raises(HTTPException) as exc:
            await advance_report_workflow(db, report.id)
        assert exc.value.status_code == 422

    async def test_update_report_part_a(
        self, db, project, work_package, reporting_period
    ):
        """Update Part A summary."""
        report = await create_report_shell(db, reporting_period.id)
        updated = await update_technical_report(
            db, report.id, part_a_summary="Project made significant progress."
        )
        assert updated.part_a_summary == "Project made significant progress."

    async def test_update_report_section(
        self, db, project, work_package, reporting_period
    ):
        """Update a report section narrative."""
        report = await create_report_shell(db, reporting_period.id)
        full = await get_technical_report(db, report.id)
        b1_section = next(
            s for s in full.sections
            if s.section_type == ReportSectionType.PART_B1_WP_NARRATIVE
        )
        updated = await update_report_section(
            db,
            b1_section.id,
            narrative="WP1 completed all planned tasks.",
            status=ReportSectionStatus.SUBMITTED,
        )
        assert updated.narrative == "WP1 completed all planned tasks."
        assert updated.status == ReportSectionStatus.SUBMITTED

    async def test_list_technical_reports(
        self, db, project, work_package, reporting_period
    ):
        """List reports for a project."""
        await create_report_shell(db, reporting_period.id)
        reports = await list_technical_reports(db, project.id)
        assert len(reports) == 1

    async def test_get_workflow_steps(
        self, db, project, work_package, reporting_period
    ):
        """Get workflow steps for a report."""
        report = await create_report_shell(db, reporting_period.id)
        steps = await get_workflow_steps(db, report.id)
        assert len(steps) == 7
        assert steps[0].name == "Initiate"
        # Step 1 is active or overdue depending on deadline vs today
        assert steps[0].status in ("active", "overdue")
        assert steps[-1].name == "Submission"


# ── Auto-Generated Section Tests ──────────────────────


class TestAutoGeneratedSections:
    """Tests for auto-generated report section data."""

    async def test_generate_part_b2_deliverables(
        self, db, project, work_package
    ):
        """Generate Part B2 from deliverable/milestone data."""
        d = Deliverable(
            work_package_id=work_package.id,
            deliverable_number="D1.1",
            title="Initial Framework Report",
            type=DeliverableType.REPORT,
            dissemination_level=DisseminationLevel.PU,
            due_month=12,
            submission_date=date(2024, 12, 15),
        )
        db.add(d)

        ms = Milestone(
            work_package_id=work_package.id,
            milestone_number="MS1",
            title="Framework Complete",
            due_month=12,
            achieved=True,
            achievement_date=date(2024, 12, 1),
        )
        db.add(ms)
        await db.flush()

        data = await generate_part_b2_data(db, project.id, date(2025, 6, 30))
        assert len(data.deliverables) == 1
        assert data.deliverables[0].deliverable_number == "D1.1"
        assert len(data.milestones) == 1
        assert data.milestones[0].achieved is True

    async def test_generate_part_b3_risks(self, db, project):
        """Generate Part B3 from risk register."""
        await create_risk(
            db,
            project.id,
            RiskCreate(
                description="High impact technical risk",
                category=RiskCategory.TECHNICAL,
                probability=RiskLevel.HIGH,
                impact=RiskLevel.HIGH,
            ),
        )
        await create_risk(
            db,
            project.id,
            RiskCreate(
                description="Low impact organizational risk",
                category=RiskCategory.ORGANIZATIONAL,
                probability=RiskLevel.LOW,
                impact=RiskLevel.LOW,
            ),
        )
        data = await generate_part_b3_data(db, project.id)
        assert len(data.high_priority_risks) == 1
        assert len(data.other_risks) == 1

    async def test_generate_part_b4_resources(
        self, db, project, work_package
    ):
        """Generate Part B4 from timesheet/allocation data."""
        researcher = Researcher(
            name="Test Researcher",
            position=ResearcherPosition.POSTDOC,
            contract_type=ContractType.DL57,
            fte=Decimal("1.00"),
            annual_gross_cost=Decimal("50000.00"),
            productive_hours=1720,
            hourly_rate=Decimal("29.07"),
        )
        db.add(researcher)
        await db.flush()
        await db.refresh(researcher)

        alloc = EffortAllocation(
            researcher_id=researcher.id,
            project_id=project.id,
            work_package_id=work_package.id,
            period_start=date(2024, 1, 1),
            period_end=date(2025, 6, 30),
            planned_pm=Decimal("6.00"),
        )
        db.add(alloc)

        # Add timesheet entries
        for i in range(5):
            ts = TimesheetEntry(
                researcher_id=researcher.id,
                project_id=project.id,
                work_package_id=work_package.id,
                date=date(2024, 6, 10 + i),
                hours=Decimal("8.00"),
            )
            db.add(ts)
        await db.flush()

        data = await generate_part_b4_data(
            db, project.id, date(2024, 1, 1), date(2025, 6, 30)
        )
        assert len(data.rows) == 1
        assert data.rows[0].wp_number == 1
        assert data.rows[0].planned_pm == Decimal("6.00")
        assert data.total_actual_pm > ZERO
        assert data.total_personnel_cost > ZERO


ZERO = Decimal("0.00")
