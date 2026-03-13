"""Tests for Section 9 — Additional Features service layer."""

import uuid
from datetime import date, datetime, timezone
from decimal import Decimal

import pytest
import pytest_asyncio

from app.models.enums import (
    AmendmentStatus,
    AmendmentType,
    CostModel,
    DisseminationActivityType,
    DMPStatus,
    EthicsStatus,
    IPStatus,
    IPType,
    KPIDataType,
    NotificationPriority,
    NotificationStatus,
    NotificationType,
    OpenAccessStatus,
    Programme,
    ProjectRole,
)
from app.models.partner import Partner
from app.models.project import Project
from app.schemas.additional_features import (
    AmendmentCreate,
    AmendmentUpdate,
    CollaborationRecordCreate,
    CollaborationRecordUpdate,
    DataManagementRecordCreate,
    DataManagementRecordUpdate,
    DisseminationActivityCreate,
    DisseminationActivityUpdate,
    EthicsRequirementCreate,
    EthicsRequirementUpdate,
    IPAssetCreate,
    IPAssetUpdate,
    KPIDefinitionCreate,
    KPIDefinitionUpdate,
    KPIValueCreate,
    KPIValueUpdate,
    NotificationCreate,
    NotificationUpdate,
)
from app.services.additional_features import (
    create_amendment,
    create_collaboration_record,
    create_data_management_record,
    create_dissemination_activity,
    create_ethics_requirement,
    create_ip_asset,
    create_kpi_definition,
    create_kpi_value,
    create_notification,
    delete_amendment,
    delete_collaboration_record,
    delete_data_management_record,
    delete_dissemination_activity,
    delete_ethics_requirement,
    delete_ip_asset,
    delete_kpi_definition,
    delete_kpi_value,
    delete_notification,
    dismiss_notification,
    get_amendment,
    get_collaboration_record,
    get_data_management_record,
    get_dissemination_activity,
    get_ethics_requirement,
    get_ip_asset,
    get_kpi_definition,
    get_kpi_value,
    get_notification,
    list_amendments,
    list_collaboration_records,
    list_data_management_records,
    list_dissemination_activities,
    list_ethics_requirements,
    list_ip_assets,
    list_kpi_definitions,
    list_kpi_values,
    list_notifications,
    mark_notification_read,
    mark_notification_sent,
    update_amendment,
    update_collaboration_record,
    update_data_management_record,
    update_dissemination_activity,
    update_ethics_requirement,
    update_ip_asset,
    update_kpi_definition,
    update_kpi_value,
    update_notification,
)


@pytest_asyncio.fixture
async def project(db):
    """Create a test project."""
    p = Project(
        acronym="IPTEST",
        full_title="IP and Additional Features Test Project",
        programme=Programme.HORIZON_EUROPE,
        cost_model=CostModel.ACTUAL_COSTS,
        role=ProjectRole.COORDINATOR,
        start_date=date(2024, 1, 1),
        end_date=date(2027, 6, 30),
        duration_months=42,
        total_budget=Decimal("500000.00"),
        eu_contribution=Decimal("400000.00"),
    )
    db.add(p)
    await db.flush()
    await db.refresh(p)
    return p


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
    await db.refresh(p)
    return p


# ── 9.1 IP and Exploitation Tracking ─────────────────


class TestIPAssets:
    """Tests for IP asset CRUD."""

    async def test_create_ip_asset(self, db, project):
        """Create a foreground IP asset."""
        data = IPAssetCreate(
            ip_type=IPType.FOREGROUND,
            title="Novel Algorithm for Data Processing",
            description="A new algorithm developed in WP3",
            status=IPStatus.IDENTIFIED,
            owner="PI Name",
        )
        asset = await create_ip_asset(db, project.id, data)
        assert asset.title == "Novel Algorithm for Data Processing"
        assert asset.ip_type == IPType.FOREGROUND
        assert asset.project_id == project.id

    async def test_list_ip_assets(self, db, project):
        """List IP assets for a project."""
        for i in range(3):
            data = IPAssetCreate(
                ip_type=IPType.FOREGROUND,
                title=f"IP Asset {i}",
            )
            await create_ip_asset(db, project.id, data)
        items = await list_ip_assets(db, project.id)
        assert len(items) == 3

    async def test_list_ip_assets_filter_status(self, db, project):
        """Filter IP assets by status."""
        await create_ip_asset(
            db, project.id,
            IPAssetCreate(ip_type=IPType.FOREGROUND, title="FG1"),
        )
        asset2 = await create_ip_asset(
            db, project.id,
            IPAssetCreate(
                ip_type=IPType.BACKGROUND, title="BG1",
                status=IPStatus.PATENT_FILED,
            ),
        )
        items = await list_ip_assets(
            db, project.id, status=IPStatus.PATENT_FILED
        )
        assert len(items) == 1
        assert items[0].id == asset2.id

    async def test_update_ip_asset(self, db, project):
        """Update an IP asset status."""
        asset = await create_ip_asset(
            db, project.id,
            IPAssetCreate(ip_type=IPType.FOREGROUND, title="Test IP"),
        )
        updated = await update_ip_asset(
            db, asset.id,
            IPAssetUpdate(status=IPStatus.PATENT_GRANTED),
        )
        assert updated.status == IPStatus.PATENT_GRANTED

    async def test_delete_ip_asset(self, db, project):
        """Soft-delete an IP asset."""
        asset = await create_ip_asset(
            db, project.id,
            IPAssetCreate(ip_type=IPType.FOREGROUND, title="To Delete"),
        )
        deleted = await delete_ip_asset(db, asset.id)
        assert deleted is True
        result = await get_ip_asset(db, asset.id)
        assert result is None

    async def test_delete_nonexistent_ip_asset(self, db):
        """Delete a nonexistent IP asset returns False."""
        deleted = await delete_ip_asset(db, uuid.uuid4())
        assert deleted is False


# ── 9.3 Dissemination Log ────────────────────────────


class TestDisseminationActivities:
    """Tests for dissemination activity CRUD."""

    async def test_create_dissemination_activity(self, db, project):
        """Create a publication record."""
        data = DisseminationActivityCreate(
            activity_type=DisseminationActivityType.PUBLICATION,
            title="A Novel Approach to Data Processing",
            authors="Author A, Author B",
            venue="IEEE Journal",
            activity_date=date(2025, 3, 15),
            doi="10.1234/test.2025",
            open_access_status=OpenAccessStatus.GOLD,
        )
        activity = await create_dissemination_activity(
            db, project.id, data
        )
        assert activity.activity_type == DisseminationActivityType.PUBLICATION
        assert activity.open_access_status == OpenAccessStatus.GOLD

    async def test_list_filter_by_type(self, db, project):
        """Filter dissemination activities by type."""
        await create_dissemination_activity(
            db, project.id,
            DisseminationActivityCreate(
                activity_type=DisseminationActivityType.PUBLICATION,
                title="Paper 1",
            ),
        )
        await create_dissemination_activity(
            db, project.id,
            DisseminationActivityCreate(
                activity_type=DisseminationActivityType.CONFERENCE,
                title="Conference Talk 1",
            ),
        )
        pubs = await list_dissemination_activities(
            db, project.id,
            activity_type=DisseminationActivityType.PUBLICATION,
        )
        assert len(pubs) == 1
        assert pubs[0].title == "Paper 1"

    async def test_update_dissemination_activity(self, db, project):
        """Update a dissemination activity."""
        activity = await create_dissemination_activity(
            db, project.id,
            DisseminationActivityCreate(
                activity_type=DisseminationActivityType.PUBLICATION,
                title="Draft Paper",
            ),
        )
        updated = await update_dissemination_activity(
            db, activity.id,
            DisseminationActivityUpdate(title="Final Paper"),
        )
        assert updated.title == "Final Paper"

    async def test_delete_dissemination_activity(self, db, project):
        """Soft-delete a dissemination activity."""
        activity = await create_dissemination_activity(
            db, project.id,
            DisseminationActivityCreate(
                activity_type=DisseminationActivityType.WORKSHOP,
                title="Workshop 1",
            ),
        )
        deleted = await delete_dissemination_activity(db, activity.id)
        assert deleted is True
        result = await get_dissemination_activity(db, activity.id)
        assert result is None


# ── 9.4 KPI and Indicator Tracking ───────────────────


class TestKPITracking:
    """Tests for KPI definitions and values."""

    async def test_create_kpi_definition(self, db):
        """Create a KPI definition."""
        data = KPIDefinitionCreate(
            name="Publications Count",
            description="Number of peer-reviewed publications",
            data_type=KPIDataType.INTEGER,
            unit="publications",
            programme="HORIZON_EUROPE",
            is_standard=True,
        )
        defn = await create_kpi_definition(db, data)
        assert defn.name == "Publications Count"
        assert defn.data_type == KPIDataType.INTEGER

    async def test_list_kpi_definitions_filter_programme(self, db):
        """Filter KPI definitions by programme."""
        await create_kpi_definition(
            db,
            KPIDefinitionCreate(
                name="KPI A", data_type=KPIDataType.INTEGER,
                programme="HE",
            ),
        )
        await create_kpi_definition(
            db,
            KPIDefinitionCreate(
                name="KPI B", data_type=KPIDataType.DECIMAL,
                programme="DE",
            ),
        )
        he_items = await list_kpi_definitions(db, programme="HE")
        assert len(he_items) == 1
        assert he_items[0].name == "KPI A"

    async def test_create_kpi_value(self, db, project):
        """Create a KPI value for a project."""
        defn = await create_kpi_definition(
            db,
            KPIDefinitionCreate(
                name="Patents Filed", data_type=KPIDataType.INTEGER,
            ),
        )
        data = KPIValueCreate(
            kpi_definition_id=defn.id,
            value_integer=3,
            target_value="5",
            notes="Q1 2025 count",
        )
        value = await create_kpi_value(db, project.id, data)
        assert value.value_integer == 3
        assert value.kpi_definition_id == defn.id

    async def test_list_kpi_values(self, db, project):
        """List KPI values for a project."""
        defn = await create_kpi_definition(
            db,
            KPIDefinitionCreate(
                name="Test KPI", data_type=KPIDataType.INTEGER,
            ),
        )
        for i in range(2):
            await create_kpi_value(
                db, project.id,
                KPIValueCreate(
                    kpi_definition_id=defn.id, value_integer=i + 1,
                ),
            )
        items = await list_kpi_values(db, project.id)
        assert len(items) == 2

    async def test_update_kpi_definition(self, db):
        """Update a KPI definition."""
        defn = await create_kpi_definition(
            db,
            KPIDefinitionCreate(
                name="Original", data_type=KPIDataType.TEXT,
            ),
        )
        updated = await update_kpi_definition(
            db, defn.id,
            KPIDefinitionUpdate(name="Updated KPI"),
        )
        assert updated.name == "Updated KPI"

    async def test_delete_kpi_definition(self, db):
        """Delete a KPI definition."""
        defn = await create_kpi_definition(
            db,
            KPIDefinitionCreate(
                name="To Delete", data_type=KPIDataType.BOOLEAN,
            ),
        )
        deleted = await delete_kpi_definition(db, defn.id)
        assert deleted is True
        result = await get_kpi_definition(db, defn.id)
        assert result is None


# ── 9.5 Ethics and Data Management ───────────────────


class TestEthicsAndDMP:
    """Tests for ethics requirements and data management."""

    async def test_create_ethics_requirement(self, db, project):
        """Create an ethics requirement."""
        data = EthicsRequirementCreate(
            requirement_type="Human Subjects Research",
            description="Ethics approval for survey data collection",
            status=EthicsStatus.PENDING,
            due_date=date(2025, 6, 1),
            dpia_required=True,
        )
        req = await create_ethics_requirement(db, project.id, data)
        assert req.requirement_type == "Human Subjects Research"
        assert req.dpia_required is True

    async def test_update_ethics_requirement(self, db, project):
        """Update ethics requirement status."""
        req = await create_ethics_requirement(
            db, project.id,
            EthicsRequirementCreate(
                requirement_type="Animal Research",
                status=EthicsStatus.PENDING,
            ),
        )
        updated = await update_ethics_requirement(
            db, req.id,
            EthicsRequirementUpdate(
                status=EthicsStatus.APPROVED,
                approval_date=date(2025, 4, 1),
            ),
        )
        assert updated.status == EthicsStatus.APPROVED
        assert updated.approval_date == date(2025, 4, 1)

    async def test_delete_ethics_requirement(self, db, project):
        """Soft-delete an ethics requirement."""
        req = await create_ethics_requirement(
            db, project.id,
            EthicsRequirementCreate(requirement_type="Test"),
        )
        deleted = await delete_ethics_requirement(db, req.id)
        assert deleted is True
        result = await get_ethics_requirement(db, req.id)
        assert result is None

    async def test_create_data_management_record(self, db, project):
        """Create a data management record."""
        data = DataManagementRecordCreate(
            dataset_name="Survey Responses Dataset",
            description="Raw and processed survey data",
            repository="Zenodo",
            repository_url="https://zenodo.org/records/123",
            dmp_status=DMPStatus.SUBMITTED,
            fair_findable=True,
            fair_accessible=True,
            data_format="CSV, JSON",
            retention_period="10 years",
        )
        record = await create_data_management_record(
            db, project.id, data
        )
        assert record.dataset_name == "Survey Responses Dataset"
        assert record.fair_findable is True
        assert record.dmp_status == DMPStatus.SUBMITTED

    async def test_list_data_management_records(self, db, project):
        """List data management records for a project."""
        for i in range(2):
            await create_data_management_record(
                db, project.id,
                DataManagementRecordCreate(
                    dataset_name=f"Dataset {i}",
                ),
            )
        items = await list_data_management_records(db, project.id)
        assert len(items) == 2

    async def test_update_data_management_record(self, db, project):
        """Update a data management record."""
        record = await create_data_management_record(
            db, project.id,
            DataManagementRecordCreate(dataset_name="Draft DMP"),
        )
        updated = await update_data_management_record(
            db, record.id,
            DataManagementRecordUpdate(
                dmp_status=DMPStatus.COMPLIANT,
                fair_reusable=True,
            ),
        )
        assert updated.dmp_status == DMPStatus.COMPLIANT
        assert updated.fair_reusable is True


# ── 9.6 Collaboration Network ────────────────────────


class TestCollaborationNetwork:
    """Tests for collaboration records."""

    async def test_create_collaboration_record(self, db, partner, project):
        """Create a collaboration record."""
        data = CollaborationRecordCreate(
            partner_id=partner.id,
            project_id=project.id,
            expertise_areas=["AI", "Data Science"],
            reliability_rating=4,
            contact_person="Dr. Smith",
            contact_email="smith@tu.de",
            co_publications=5,
        )
        record = await create_collaboration_record(db, data)
        assert record.partner_id == partner.id
        assert record.reliability_rating == 4
        assert record.co_publications == 5

    async def test_list_collaboration_records_filter(
        self, db, partner, project
    ):
        """Filter collaboration records by partner."""
        await create_collaboration_record(
            db,
            CollaborationRecordCreate(
                partner_id=partner.id, project_id=project.id,
            ),
        )
        items = await list_collaboration_records(
            db, partner_id=partner.id
        )
        assert len(items) == 1

    async def test_update_collaboration_record(self, db, partner):
        """Update a collaboration record."""
        record = await create_collaboration_record(
            db,
            CollaborationRecordCreate(
                partner_id=partner.id, co_publications=0,
            ),
        )
        updated = await update_collaboration_record(
            db, record.id,
            CollaborationRecordUpdate(co_publications=3),
        )
        assert updated.co_publications == 3

    async def test_delete_collaboration_record(self, db, partner):
        """Delete a collaboration record."""
        record = await create_collaboration_record(
            db,
            CollaborationRecordCreate(partner_id=partner.id),
        )
        deleted = await delete_collaboration_record(db, record.id)
        assert deleted is True
        result = await get_collaboration_record(db, record.id)
        assert result is None


# ── 9.7 Amendment Tracking ───────────────────────────


class TestAmendmentTracking:
    """Tests for amendment CRUD."""

    async def test_create_amendment(self, db, project):
        """Create an amendment."""
        data = AmendmentCreate(
            amendment_number=1,
            amendment_type=AmendmentType.BUDGET_TRANSFER,
            title="Budget reallocation WP2 to WP3",
            description="Move 50k from WP2 travel to WP3 equipment",
            rationale="Equipment costs exceeded initial estimates",
            status=AmendmentStatus.DRAFT,
            budget_impact={"wp2": -50000, "wp3": 50000},
        )
        amendment = await create_amendment(db, project.id, data)
        assert amendment.amendment_number == 1
        assert amendment.amendment_type == AmendmentType.BUDGET_TRANSFER
        assert amendment.budget_impact == {"wp2": -50000, "wp3": 50000}

    async def test_list_amendments_ordered(self, db, project):
        """Amendments listed by amendment_number."""
        for i in [3, 1, 2]:
            await create_amendment(
                db, project.id,
                AmendmentCreate(
                    amendment_number=i,
                    amendment_type=AmendmentType.OTHER,
                    title=f"Amendment {i}",
                    description=f"Description {i}",
                ),
            )
        items = await list_amendments(db, project.id)
        assert [a.amendment_number for a in items] == [1, 2, 3]

    async def test_update_amendment_status(self, db, project):
        """Update amendment status through workflow."""
        amendment = await create_amendment(
            db, project.id,
            AmendmentCreate(
                amendment_number=1,
                amendment_type=AmendmentType.TIMELINE_CHANGE,
                title="Extension request",
                description="6-month extension",
            ),
        )
        updated = await update_amendment(
            db, amendment.id,
            AmendmentUpdate(
                status=AmendmentStatus.SUBMITTED,
                submission_date=date(2025, 6, 1),
            ),
        )
        assert updated.status == AmendmentStatus.SUBMITTED
        assert updated.submission_date == date(2025, 6, 1)

    async def test_delete_amendment(self, db, project):
        """Soft-delete an amendment."""
        amendment = await create_amendment(
            db, project.id,
            AmendmentCreate(
                amendment_number=1,
                amendment_type=AmendmentType.SCOPE_CHANGE,
                title="Scope change",
                description="Remove task 3.4",
            ),
        )
        deleted = await delete_amendment(db, amendment.id)
        assert deleted is True
        result = await get_amendment(db, amendment.id)
        assert result is None


# ── 9.8 Notification System ──────────────────────────


class TestNotificationSystem:
    """Tests for notification CRUD and status transitions."""

    async def test_create_notification(self, db, project):
        """Create a notification."""
        data = NotificationCreate(
            project_id=project.id,
            notification_type=NotificationType.REPORTING_DEADLINE,
            priority=NotificationPriority.HIGH,
            title="Report due in 30 days",
            message="Periodic report RP1 is due on 2025-07-01",
            recipient_email="pi@university.edu",
        )
        notification = await create_notification(db, data)
        assert notification.notification_type == (
            NotificationType.REPORTING_DEADLINE
        )
        assert notification.priority == NotificationPriority.HIGH

    async def test_list_notifications_filter_status(self, db, project):
        """Filter notifications by status."""
        n1 = await create_notification(
            db,
            NotificationCreate(
                project_id=project.id,
                notification_type=NotificationType.TIMESHEET_REMINDER,
                title="Timesheet reminder",
                message="Submit your timesheet",
            ),
        )
        n2 = await create_notification(
            db,
            NotificationCreate(
                project_id=project.id,
                notification_type=NotificationType.BUDGET_THRESHOLD,
                title="Budget alert",
                message="Budget threshold exceeded",
            ),
        )
        # Mark one as sent
        await mark_notification_sent(db, n2.id)

        pending = await list_notifications(
            db, status=NotificationStatus.PENDING
        )
        assert len(pending) == 1
        assert pending[0].id == n1.id

    async def test_mark_notification_read(self, db, project):
        """Mark a notification as read."""
        n = await create_notification(
            db,
            NotificationCreate(
                project_id=project.id,
                notification_type=NotificationType.DELIVERABLE_DUE,
                title="Deliverable due",
                message="D2.1 is due next week",
            ),
        )
        read = await mark_notification_read(db, n.id)
        assert read.status == NotificationStatus.READ
        assert read.read_at is not None

    async def test_dismiss_notification(self, db, project):
        """Dismiss a notification."""
        n = await create_notification(
            db,
            NotificationCreate(
                project_id=project.id,
                notification_type=NotificationType.CONTRACT_EXPIRY,
                title="Contract expiring",
                message="Researcher contract ends in 30 days",
            ),
        )
        dismissed = await dismiss_notification(db, n.id)
        assert dismissed.status == NotificationStatus.DISMISSED
        assert dismissed.dismissed_at is not None

    async def test_list_notifications_filter_recipient(self, db, project):
        """Filter notifications by recipient email."""
        await create_notification(
            db,
            NotificationCreate(
                project_id=project.id,
                notification_type=NotificationType.TIMESHEET_REMINDER,
                title="Reminder A",
                message="Submit timesheet",
                recipient_email="alice@uni.edu",
            ),
        )
        await create_notification(
            db,
            NotificationCreate(
                project_id=project.id,
                notification_type=NotificationType.TIMESHEET_REMINDER,
                title="Reminder B",
                message="Submit timesheet",
                recipient_email="bob@uni.edu",
            ),
        )
        alice_notifs = await list_notifications(
            db, recipient_email="alice@uni.edu"
        )
        assert len(alice_notifs) == 1
        assert alice_notifs[0].title == "Reminder A"

    async def test_delete_notification(self, db, project):
        """Delete a notification."""
        n = await create_notification(
            db,
            NotificationCreate(
                project_id=project.id,
                notification_type=NotificationType.EC_FEEDBACK,
                title="EC feedback",
                message="Feedback received",
            ),
        )
        deleted = await delete_notification(db, n.id)
        assert deleted is True
        result = await get_notification(db, n.id)
        assert result is None

    async def test_update_notification(self, db, project):
        """Update notification fields."""
        n = await create_notification(
            db,
            NotificationCreate(
                project_id=project.id,
                notification_type=NotificationType.RISK_ESCALATION,
                title="Risk escalated",
                message="Risk R1 has been escalated",
                priority=NotificationPriority.MEDIUM,
            ),
        )
        updated = await update_notification(
            db, n.id,
            NotificationUpdate(priority=NotificationPriority.CRITICAL),
        )
        assert updated.priority == NotificationPriority.CRITICAL
