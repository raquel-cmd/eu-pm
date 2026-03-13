"""Tests for the project service layer."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import CostModel, Programme, ProjectRole, ProjectStatus
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.services import project as project_service


def _make_project_data(**overrides) -> ProjectCreate:
    """Helper to create project data with defaults."""
    defaults = {
        "acronym": "TEST-PROJ",
        "full_title": "Test Project for Unit Testing",
        "programme": Programme.HORIZON_EUROPE,
        "cost_model": CostModel.ACTUAL_COSTS,
        "role": ProjectRole.COORDINATOR,
        "status": ProjectStatus.ACTIVE,
    }
    defaults.update(overrides)
    return ProjectCreate(**defaults)


@pytest.mark.asyncio
async def test_create_project(db: AsyncSession):
    """Test creating a project."""
    data = _make_project_data()
    project = await project_service.create_project(db, data)

    assert project.id is not None
    assert project.acronym == "TEST-PROJ"
    assert project.programme == Programme.HORIZON_EUROPE
    assert project.cost_model == CostModel.ACTUAL_COSTS
    assert project.role == ProjectRole.COORDINATOR
    assert project.created_at is not None


@pytest.mark.asyncio
async def test_get_project(db: AsyncSession):
    """Test getting a project by ID."""
    data = _make_project_data(acronym="GET-TEST")
    created = await project_service.create_project(db, data)

    fetched = await project_service.get_project(db, created.id)
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.acronym == "GET-TEST"


@pytest.mark.asyncio
async def test_get_project_not_found(db: AsyncSession):
    """Test getting a non-existent project returns None."""
    import uuid
    result = await project_service.get_project(db, uuid.uuid4())
    assert result is None


@pytest.mark.asyncio
async def test_list_projects(db: AsyncSession):
    """Test listing projects."""
    await project_service.create_project(db, _make_project_data(acronym="LIST-1"))
    await project_service.create_project(db, _make_project_data(acronym="LIST-2"))

    items, total = await project_service.list_projects(db)
    assert total >= 2
    acronyms = [p.acronym for p in items]
    assert "LIST-1" in acronyms
    assert "LIST-2" in acronyms


@pytest.mark.asyncio
async def test_list_projects_filter_by_status(db: AsyncSession):
    """Test filtering projects by status."""
    await project_service.create_project(
        db, _make_project_data(acronym="ACTIVE-1", status=ProjectStatus.ACTIVE)
    )
    await project_service.create_project(
        db, _make_project_data(acronym="CLOSED-1", status=ProjectStatus.CLOSED)
    )

    items, total = await project_service.list_projects(
        db, status=ProjectStatus.ACTIVE
    )
    acronyms = [p.acronym for p in items]
    assert "ACTIVE-1" in acronyms
    assert "CLOSED-1" not in acronyms


@pytest.mark.asyncio
async def test_list_projects_filter_by_cost_model(db: AsyncSession):
    """Test filtering projects by cost model."""
    await project_service.create_project(
        db, _make_project_data(acronym="AC-1", cost_model=CostModel.ACTUAL_COSTS)
    )
    await project_service.create_project(
        db, _make_project_data(acronym="LS-1", cost_model=CostModel.LUMP_SUM)
    )

    items, _ = await project_service.list_projects(
        db, cost_model=CostModel.LUMP_SUM
    )
    acronyms = [p.acronym for p in items]
    assert "LS-1" in acronyms
    assert "AC-1" not in acronyms


@pytest.mark.asyncio
async def test_update_project(db: AsyncSession):
    """Test updating a project."""
    data = _make_project_data(acronym="UPDATE-ME")
    project = await project_service.create_project(db, data)

    update = ProjectUpdate(acronym="UPDATED", status=ProjectStatus.SUSPENDED)
    updated = await project_service.update_project(db, project.id, update)

    assert updated is not None
    assert updated.acronym == "UPDATED"
    assert updated.status == ProjectStatus.SUSPENDED
    # Unchanged fields should remain
    assert updated.programme == Programme.HORIZON_EUROPE


@pytest.mark.asyncio
async def test_update_project_not_found(db: AsyncSession):
    """Test updating a non-existent project returns None."""
    import uuid
    update = ProjectUpdate(acronym="NOPE")
    result = await project_service.update_project(db, uuid.uuid4(), update)
    assert result is None


@pytest.mark.asyncio
async def test_delete_project(db: AsyncSession):
    """Test soft-deleting a project."""
    data = _make_project_data(acronym="DELETE-ME")
    project = await project_service.create_project(db, data)

    deleted = await project_service.delete_project(db, project.id)
    assert deleted is True

    # Should not be found after deletion
    fetched = await project_service.get_project(db, project.id)
    assert fetched is None


@pytest.mark.asyncio
async def test_delete_project_not_found(db: AsyncSession):
    """Test deleting a non-existent project returns False."""
    import uuid
    result = await project_service.delete_project(db, uuid.uuid4())
    assert result is False
