"""Tests for the partner service layer."""

from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import (
    CostModel,
    OrgType,
    Programme,
    ProjectRole,
    ProjectStatus,
)
from app.schemas.partner import (
    PartnerCreate,
    PartnerUpdate,
    ProjectPartnerCreate,
)
from app.schemas.project import ProjectCreate
from app.services import partner as partner_service
from app.services import project as project_service


def _make_partner_data(**overrides) -> PartnerCreate:
    defaults = {
        "legal_name": "Test University",
        "short_name": "TU",
        "country": "Portugal",
        "org_type": OrgType.HES,
    }
    defaults.update(overrides)
    return PartnerCreate(**defaults)


@pytest.mark.asyncio
async def test_create_partner(db: AsyncSession):
    """Test creating a partner."""
    data = _make_partner_data(short_name="CREATE-P")
    partner = await partner_service.create_partner(db, data)
    assert partner.id is not None
    assert partner.short_name == "CREATE-P"
    assert partner.org_type == OrgType.HES


@pytest.mark.asyncio
async def test_list_partners(db: AsyncSession):
    """Test listing partners."""
    await partner_service.create_partner(db, _make_partner_data(short_name="AA"))
    await partner_service.create_partner(db, _make_partner_data(short_name="BB"))
    items, total = await partner_service.list_partners(db)
    assert total >= 2


@pytest.mark.asyncio
async def test_update_partner(db: AsyncSession):
    """Test updating a partner."""
    partner = await partner_service.create_partner(
        db, _make_partner_data(short_name="UPD-P")
    )
    updated = await partner_service.update_partner(
        db, partner.id, PartnerUpdate(country="Spain")
    )
    assert updated is not None
    assert updated.country == "Spain"


@pytest.mark.asyncio
async def test_delete_partner(db: AsyncSession):
    """Test soft-deleting a partner."""
    partner = await partner_service.create_partner(
        db, _make_partner_data(short_name="DEL-P")
    )
    assert await partner_service.delete_partner(db, partner.id) is True
    assert await partner_service.get_partner(db, partner.id) is None


@pytest.mark.asyncio
async def test_add_partner_to_project(db: AsyncSession):
    """Test linking a partner to a project."""
    project = await project_service.create_project(
        db,
        ProjectCreate(
            acronym="PP-TEST",
            full_title="ProjectPartner Test",
            programme=Programme.HORIZON_EUROPE,
            cost_model=CostModel.ACTUAL_COSTS,
            role=ProjectRole.COORDINATOR,
        ),
    )
    partner = await partner_service.create_partner(
        db, _make_partner_data(short_name="PP-PARTNER")
    )

    pp = await partner_service.add_partner_to_project(
        db,
        project.id,
        ProjectPartnerCreate(
            partner_id=partner.id,
            partner_budget=Decimal("100000.00"),
            partner_eu_contribution=Decimal("70000.00"),
        ),
    )
    assert pp.project_id == project.id
    assert pp.partner_id == partner.id
    assert pp.partner_budget == Decimal("100000.00")


@pytest.mark.asyncio
async def test_list_project_partners(db: AsyncSession):
    """Test listing partners for a project."""
    project = await project_service.create_project(
        db,
        ProjectCreate(
            acronym="PP-LIST",
            full_title="List Partners Test",
            programme=Programme.HORIZON_EUROPE,
            cost_model=CostModel.ACTUAL_COSTS,
            role=ProjectRole.COORDINATOR,
        ),
    )
    p1 = await partner_service.create_partner(
        db, _make_partner_data(short_name="LP1")
    )
    p2 = await partner_service.create_partner(
        db, _make_partner_data(short_name="LP2")
    )
    await partner_service.add_partner_to_project(
        db, project.id, ProjectPartnerCreate(partner_id=p1.id)
    )
    await partner_service.add_partner_to_project(
        db, project.id, ProjectPartnerCreate(partner_id=p2.id)
    )

    items = await partner_service.list_project_partners(db, project.id)
    assert len(items) == 2
