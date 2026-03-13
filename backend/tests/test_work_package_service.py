"""Tests for the work package, deliverable, and milestone service layers."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import (
    CostModel,
    DeliverableType,
    DisseminationLevel,
    Programme,
    ProjectRole,
    WPStatus,
)
from app.schemas.project import ProjectCreate
from app.schemas.work_package import (
    DeliverableCreate,
    MilestoneCreate,
    WorkPackageCreate,
    WorkPackageUpdate,
)
from app.services import project as project_service
from app.services import work_package as wp_service


async def _create_project(db: AsyncSession, acronym: str = "WP-TEST"):
    return await project_service.create_project(
        db,
        ProjectCreate(
            acronym=acronym,
            full_title="WP Test Project",
            programme=Programme.HORIZON_EUROPE,
            cost_model=CostModel.ACTUAL_COSTS,
            role=ProjectRole.COORDINATOR,
        ),
    )


@pytest.mark.asyncio
async def test_create_work_package(db: AsyncSession):
    """Test creating a work package."""
    project = await _create_project(db, "WP-C")
    wp = await wp_service.create_work_package(
        db,
        project.id,
        WorkPackageCreate(wp_number=1, title="Management"),
    )
    assert wp.id is not None
    assert wp.wp_number == 1
    assert wp.project_id == project.id
    assert wp.status == WPStatus.NOT_STARTED


@pytest.mark.asyncio
async def test_list_work_packages(db: AsyncSession):
    """Test listing work packages for a project."""
    project = await _create_project(db, "WP-L")
    await wp_service.create_work_package(
        db, project.id, WorkPackageCreate(wp_number=1, title="WP1")
    )
    await wp_service.create_work_package(
        db, project.id, WorkPackageCreate(wp_number=2, title="WP2")
    )
    items, total = await wp_service.list_work_packages(db, project.id)
    assert total == 2
    assert items[0].wp_number == 1


@pytest.mark.asyncio
async def test_update_work_package(db: AsyncSession):
    """Test updating a work package."""
    project = await _create_project(db, "WP-U")
    wp = await wp_service.create_work_package(
        db, project.id, WorkPackageCreate(wp_number=1, title="Old Title")
    )
    updated = await wp_service.update_work_package(
        db,
        project.id,
        wp.id,
        WorkPackageUpdate(title="New Title", status=WPStatus.IN_PROGRESS),
    )
    assert updated is not None
    assert updated.title == "New Title"
    assert updated.status == WPStatus.IN_PROGRESS


@pytest.mark.asyncio
async def test_delete_work_package(db: AsyncSession):
    """Test soft-deleting a work package."""
    project = await _create_project(db, "WP-D")
    wp = await wp_service.create_work_package(
        db, project.id, WorkPackageCreate(wp_number=1, title="Delete Me")
    )
    assert await wp_service.delete_work_package(db, project.id, wp.id) is True
    assert await wp_service.get_work_package(db, project.id, wp.id) is None


@pytest.mark.asyncio
async def test_create_deliverable(db: AsyncSession):
    """Test creating a deliverable."""
    project = await _create_project(db, "DEL-C")
    wp = await wp_service.create_work_package(
        db, project.id, WorkPackageCreate(wp_number=1, title="WP1")
    )
    d = await wp_service.create_deliverable(
        db,
        wp.id,
        DeliverableCreate(
            deliverable_number="D1.1",
            title="First Deliverable",
            type=DeliverableType.REPORT,
            dissemination_level=DisseminationLevel.PU,
            due_month=12,
        ),
    )
    assert d.deliverable_number == "D1.1"
    assert d.work_package_id == wp.id


@pytest.mark.asyncio
async def test_list_deliverables(db: AsyncSession):
    """Test listing deliverables for a work package."""
    project = await _create_project(db, "DEL-L")
    wp = await wp_service.create_work_package(
        db, project.id, WorkPackageCreate(wp_number=1, title="WP1")
    )
    await wp_service.create_deliverable(
        db,
        wp.id,
        DeliverableCreate(
            deliverable_number="D1.1",
            title="Del 1",
            type=DeliverableType.REPORT,
            dissemination_level=DisseminationLevel.PU,
        ),
    )
    await wp_service.create_deliverable(
        db,
        wp.id,
        DeliverableCreate(
            deliverable_number="D1.2",
            title="Del 2",
            type=DeliverableType.SOFTWARE,
            dissemination_level=DisseminationLevel.PU,
        ),
    )
    items, total = await wp_service.list_deliverables(db, wp.id)
    assert total == 2


@pytest.mark.asyncio
async def test_create_milestone(db: AsyncSession):
    """Test creating a milestone."""
    project = await _create_project(db, "MS-C")
    wp = await wp_service.create_work_package(
        db, project.id, WorkPackageCreate(wp_number=1, title="WP1")
    )
    m = await wp_service.create_milestone(
        db,
        wp.id,
        MilestoneCreate(
            milestone_number="MS1",
            title="First Milestone",
            due_month=6,
            verification_means="Prototype demo",
        ),
    )
    assert m.milestone_number == "MS1"
    assert m.achieved is False


@pytest.mark.asyncio
async def test_delete_milestone(db: AsyncSession):
    """Test soft-deleting a milestone."""
    project = await _create_project(db, "MS-D")
    wp = await wp_service.create_work_package(
        db, project.id, WorkPackageCreate(wp_number=1, title="WP1")
    )
    m = await wp_service.create_milestone(
        db,
        wp.id,
        MilestoneCreate(milestone_number="MS-DEL", title="Delete Me"),
    )
    assert await wp_service.delete_milestone(db, wp.id, m.id) is True
    assert await wp_service.get_milestone(db, wp.id, m.id) is None
