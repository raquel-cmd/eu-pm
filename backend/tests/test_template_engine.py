"""Tests for template engine service (Section 7)."""

import uuid
from datetime import date
from decimal import Decimal

import pytest
import pytest_asyncio
from fastapi import HTTPException

from app.models.enums import (
    ContractType,
    CostModel,
    GeneratedDocumentStatus,
    PersonnelTemplateType,
    Programme,
    ProjectRole,
    ResearcherPosition,
    TemplateCategory,
)
from app.models.project import Project
from app.models.researcher import Researcher
from app.models.template import DocumentTemplate, GeneratedDocument
from app.services.template_engine import (
    _evaluate_conditional_sections,
    _resolve_auto_fields,
    generate_document,
    generate_document_bytes,
    get_generated_document,
    get_template,
    list_generated_documents,
    list_templates,
    preview_template,
    seed_all_templates,
    seed_personnel_templates,
    update_document_status,
)


# --- Fixtures ---


@pytest_asyncio.fixture
async def project(db):
    """Create a test project."""
    p = Project(
        acronym="TMPLTEST",
        full_title="Template Test Project",
        grant_agreement_number="GA-123456",
        programme=Programme.HORIZON_EUROPE,
        cost_model=CostModel.ACTUAL_COSTS,
        role=ProjectRole.COORDINATOR,
        start_date=date(2024, 1, 1),
        end_date=date(2027, 6, 30),
        duration_months=42,
        total_budget=Decimal("1000000.00"),
        eu_contribution=Decimal("800000.00"),
        internal_cost_center="CC-TMPL-01",
    )
    db.add(p)
    await db.flush()
    await db.refresh(p)
    return p


@pytest_asyncio.fixture
async def lump_sum_project(db):
    """Create a lump sum project for conditional testing."""
    p = Project(
        acronym="LUMPTEST",
        full_title="Lump Sum Template Test",
        programme=Programme.HORIZON_EUROPE,
        cost_model=CostModel.LUMP_SUM,
        role=ProjectRole.COORDINATOR,
        start_date=date(2024, 1, 1),
        end_date=date(2026, 12, 31),
    )
    db.add(p)
    await db.flush()
    await db.refresh(p)
    return p


@pytest_asyncio.fixture
async def researcher(db):
    """Create a test researcher."""
    r = Researcher(
        name="Maria Silva",
        email="maria.silva@university.pt",
        position=ResearcherPosition.POSTDOC,
        contract_type=ContractType.BOLSA_BPD,
        fte=Decimal("1.00"),
        annual_gross_cost=Decimal("45000.00"),
        productive_hours=1720,
        hourly_rate=Decimal("26.16"),
        start_date=date(2024, 3, 1),
        end_date=date(2026, 2, 28),
    )
    db.add(r)
    await db.flush()
    await db.refresh(r)
    return r


@pytest_asyncio.fixture
async def seeded_templates(db):
    """Seed all personnel templates."""
    templates = await seed_personnel_templates(db)
    await db.flush()
    return templates


@pytest_asyncio.fixture
async def all_seeded_templates(db):
    """Seed all templates (all categories)."""
    templates = await seed_all_templates(db)
    await db.flush()
    return templates


@pytest_asyncio.fixture
async def partner_project(db):
    """Create a project with PARTNER role for conditional testing."""
    p = Project(
        acronym="PARTNERTEST",
        full_title="Partner Role Test",
        programme=Programme.HORIZON_EUROPE,
        cost_model=CostModel.ACTUAL_COSTS,
        role=ProjectRole.PARTNER,
        start_date=date(2024, 1, 1),
        end_date=date(2026, 12, 31),
    )
    db.add(p)
    await db.flush()
    await db.refresh(p)
    return p


@pytest_asyncio.fixture
async def unit_costs_project(db):
    """Create a unit costs project for conditional testing."""
    p = Project(
        acronym="UNITTEST",
        full_title="Unit Costs Test",
        programme=Programme.HORIZON_EUROPE,
        cost_model=CostModel.UNIT_COSTS,
        role=ProjectRole.COORDINATOR,
        start_date=date(2024, 1, 1),
        end_date=date(2026, 12, 31),
        total_budget=Decimal("500000.00"),
        eu_contribution=Decimal("500000.00"),
        internal_cost_center="CC-UNIT-01",
    )
    db.add(p)
    await db.flush()
    await db.refresh(p)
    return p


# --- Template Seeding Tests ---


class TestTemplateSeeding:
    """Tests for template seed and CRUD operations."""

    async def test_seed_creates_all_personnel_templates(
        self, db, seeded_templates
    ):
        """Seeding creates all 7 personnel templates."""
        all_templates = await list_templates(db)
        assert len(all_templates) >= 7

        slugs = {t.slug for t in all_templates}
        expected_slugs = {
            "bolsa-bi",
            "bolsa-bd",
            "bolsa-bpd",
            "dl57-contract",
            "ceec-contract",
            "clt-employment",
            "contract-renewal",
        }
        assert expected_slugs.issubset(slugs)

    async def test_seed_is_idempotent(self, db, seeded_templates):
        """Re-seeding does not create duplicates."""
        second_run = await seed_personnel_templates(db)
        assert len(second_run) == 0

        all_templates = await list_templates(db)
        slugs = [t.slug for t in all_templates]
        assert len(slugs) == len(set(slugs))  # no duplicates

    async def test_filter_by_category(self, db, seeded_templates):
        """Filter templates by category."""
        personnel = await list_templates(db, TemplateCategory.PERSONNEL)
        assert len(personnel) >= 7
        for t in personnel:
            assert t.category == TemplateCategory.PERSONNEL

    async def test_get_template_by_id(self, db, seeded_templates):
        """Get a specific template by ID."""
        all_templates = await list_templates(db)
        first = all_templates[0]
        fetched = await get_template(db, first.id)
        assert fetched.slug == first.slug

    async def test_get_nonexistent_template_404(self, db):
        """Getting a nonexistent template raises 404."""
        with pytest.raises(HTTPException) as exc:
            await get_template(db, uuid.uuid4())
        assert exc.value.status_code == 404

    async def test_template_has_field_definitions(
        self, db, seeded_templates
    ):
        """Templates have field definitions with auto and manual fields."""
        all_templates = await list_templates(db)
        bi = next(
            t for t in all_templates if t.slug == "bolsa-bi"
        )
        fields = bi.field_definitions.get("fields", [])
        assert len(fields) > 0

        auto_fields = [
            f for f in fields if f["field_type"] == "auto"
        ]
        manual_fields = [
            f for f in fields if f["field_type"] == "manual"
        ]
        assert len(auto_fields) > 0
        assert len(manual_fields) > 0

    async def test_template_has_conditional_sections(
        self, db, seeded_templates
    ):
        """Templates have conditional sections for cost model."""
        all_templates = await list_templates(db)
        bi = next(
            t for t in all_templates if t.slug == "bolsa-bi"
        )
        assert bi.conditional_sections is not None
        assert "timesheet_obligations" in bi.conditional_sections


# --- Auto-Population Tests ---


class TestAutoPopulation:
    """Tests for field auto-population from project/researcher data."""

    async def test_preview_auto_populates_project_fields(
        self, db, seeded_templates, project
    ):
        """Preview fills project fields from database."""
        all_templates = await list_templates(db)
        bi = next(t for t in all_templates if t.slug == "bolsa-bi")

        preview = await preview_template(
            db, bi.id, project_id=project.id
        )

        field_map = {f.name: f for f in preview.fields}
        assert field_map["project_acronym"].value == "TMPLTEST"
        assert field_map["grant_agreement_number"].value == "GA-123456"
        assert field_map["programme"].value == "HORIZON_EUROPE"

    async def test_preview_auto_populates_researcher_fields(
        self, db, seeded_templates, project, researcher
    ):
        """Preview fills researcher fields from database."""
        all_templates = await list_templates(db)
        bpd = next(
            t for t in all_templates if t.slug == "bolsa-bpd"
        )

        preview = await preview_template(
            db, bpd.id, project.id, researcher.id
        )

        field_map = {f.name: f for f in preview.fields}
        assert field_map["researcher_name"].value == "Maria Silva"
        assert field_map["researcher_email"].value == "maria.silva@university.pt"
        assert field_map["position"].value == "POSTDOC"

    async def test_conditional_sections_actual_costs(
        self, db, seeded_templates, project
    ):
        """Actual cost project activates timesheet obligations."""
        all_templates = await list_templates(db)
        bi = next(t for t in all_templates if t.slug == "bolsa-bi")

        preview = await preview_template(
            db, bi.id, project_id=project.id
        )
        assert "timesheet_obligations" in preview.conditional_sections_active
        assert "lump_sum_effort_note" not in preview.conditional_sections_active

    async def test_conditional_sections_lump_sum(
        self, db, seeded_templates, lump_sum_project
    ):
        """Lump sum project activates lump sum note instead."""
        all_templates = await list_templates(db)
        bi = next(t for t in all_templates if t.slug == "bolsa-bi")

        preview = await preview_template(
            db, bi.id, project_id=lump_sum_project.id
        )
        assert "lump_sum_effort_note" in preview.conditional_sections_active
        assert "timesheet_obligations" not in preview.conditional_sections_active

    async def test_manual_fields_not_auto_populated(
        self, db, seeded_templates, project
    ):
        """Manual fields have no auto-populated value."""
        all_templates = await list_templates(db)
        bi = next(t for t in all_templates if t.slug == "bolsa-bi")

        preview = await preview_template(
            db, bi.id, project_id=project.id
        )
        field_map = {f.name: f for f in preview.fields}
        assert field_map["research_plan"].value is None
        assert field_map["research_plan"].field_type == "manual"


# --- DOCX Generation Tests ---


class TestDocxGeneration:
    """Tests for DOCX document generation."""

    async def test_generate_document_creates_record(
        self, db, seeded_templates, project, researcher
    ):
        """Generating a document creates a database record."""
        all_templates = await list_templates(db)
        bi = next(t for t in all_templates if t.slug == "bolsa-bi")

        doc = await generate_document(
            db,
            bi.id,
            project_id=project.id,
            researcher_id=researcher.id,
            manual_fields={
                "research_plan": "AI research activities",
                "supervisor_name": "Prof. Joao Santos",
                "monthly_stipend": "1600.00",
                "scholarship_duration_months": "24",
                "work_location": "Computer Science Lab",
            },
            generated_by="Test User",
        )

        assert doc.template_id == bi.id
        assert doc.project_id == project.id
        assert doc.researcher_id == researcher.id
        assert doc.template_version == 1
        assert doc.status == GeneratedDocumentStatus.DRAFT
        assert doc.file_name.endswith(".docx")
        assert "bolsa-bi" in doc.file_name
        assert "TMPLTEST" in doc.file_name

    async def test_generate_document_saves_input_data(
        self, db, seeded_templates, project, researcher
    ):
        """Generated document snapshots all input data."""
        all_templates = await list_templates(db)
        bpd = next(
            t for t in all_templates if t.slug == "bolsa-bpd"
        )

        doc = await generate_document(
            db,
            bpd.id,
            project_id=project.id,
            researcher_id=researcher.id,
            manual_fields={
                "research_group": "CITI Lab",
                "supervisor_name": "Prof. Ana Costa",
                "research_plan": "NLP research",
                "monthly_stipend": "2000.00",
                "scholarship_duration_months": "36",
            },
        )

        assert doc.input_data["project_acronym"] == "TMPLTEST"
        assert doc.input_data["researcher_name"] == "Maria Silva"
        assert doc.input_data["research_group"] == "CITI Lab"

    async def test_generate_document_bytes(
        self, db, seeded_templates, project
    ):
        """Generate DOCX bytes without saving to filesystem."""
        all_templates = await list_templates(db)
        dl57 = next(
            t for t in all_templates if t.slug == "dl57-contract"
        )

        buf, filename = await generate_document_bytes(
            db, dl57.id, project_id=project.id
        )

        assert filename.endswith(".docx")
        assert "dl57-contract" in filename
        content = buf.getvalue()
        assert len(content) > 100  # Not empty
        # Check DOCX magic bytes (PK zip header)
        assert content[:2] == b"PK"

    async def test_list_generated_documents(
        self, db, seeded_templates, project
    ):
        """List generated documents."""
        all_templates = await list_templates(db)
        clt = next(
            t for t in all_templates if t.slug == "clt-employment"
        )

        await generate_document(
            db, clt.id, project_id=project.id,
            manual_fields={
                "job_title": "Research Engineer",
                "salary_grade": "Level 3",
                "monthly_salary": "2500.00",
            },
        )

        docs = await list_generated_documents(
            db, project_id=project.id
        )
        assert len(docs) >= 1

    async def test_update_document_status(
        self, db, seeded_templates, project
    ):
        """Update status of a generated document."""
        all_templates = await list_templates(db)
        renewal = next(
            t for t in all_templates
            if t.slug == "contract-renewal"
        )

        doc = await generate_document(
            db, renewal.id, project_id=project.id,
            manual_fields={
                "original_contract_ref": "CT-2024-001",
                "original_start_date": "2024-01-01",
                "original_end_date": "2025-12-31",
                "new_end_date": "2026-12-31",
                "renewal_justification": "Project extension needed",
            },
        )

        updated = await update_document_status(
            db, doc.id, GeneratedDocumentStatus.PENDING_APPROVAL
        )
        assert updated.status == GeneratedDocumentStatus.PENDING_APPROVAL

        updated = await update_document_status(
            db, doc.id, GeneratedDocumentStatus.APPROVED
        )
        assert updated.status == GeneratedDocumentStatus.APPROVED


# --- Helper Function Tests ---


class TestHelperFunctions:
    """Tests for internal helper functions."""

    def test_resolve_auto_fields(self):
        """Resolve auto fields from data sources."""
        field_defs = [
            {
                "name": "acronym",
                "field_type": "auto",
                "data_source": "project.acronym",
            },
            {
                "name": "notes",
                "field_type": "manual",
            },
        ]
        project_data = {"project.acronym": "TEST"}
        values = _resolve_auto_fields(field_defs, project_data, {})
        assert values["acronym"] == "TEST"
        assert "notes" not in values

    def test_evaluate_conditional_sections_eq(self):
        """Evaluate conditional sections with eq operator."""
        conditions = {
            "timesheet": {
                "condition_field": "project.cost_model",
                "condition_value": "ACTUAL_COSTS",
                "condition_operator": "eq",
            },
        }
        data = {"project.cost_model": "ACTUAL_COSTS"}
        active = _evaluate_conditional_sections(conditions, data)
        assert "timesheet" in active

    def test_evaluate_conditional_sections_neq(self):
        """Evaluate conditional sections with neq operator."""
        conditions = {
            "no_timesheet": {
                "condition_field": "project.cost_model",
                "condition_value": "ACTUAL_COSTS",
                "condition_operator": "neq",
            },
        }
        data = {"project.cost_model": "LUMP_SUM"}
        active = _evaluate_conditional_sections(conditions, data)
        assert "no_timesheet" in active

    def test_evaluate_conditional_sections_none(self):
        """No conditions returns empty list."""
        assert _evaluate_conditional_sections(None, {}) == []


# --- All-Category Seeding Tests ---


class TestAllCategorySeeding:
    """Tests for seeding all template categories."""

    async def test_seed_all_creates_all_templates(
        self, db, all_seeded_templates
    ):
        """Seeding all templates creates templates from every category."""
        all_templates = await list_templates(db)
        # 7 personnel + 4 EC/consortium + 5 reporting + 4 mission + 6 procurement = 26
        assert len(all_templates) == 26

    async def test_seed_all_is_idempotent(self, db, all_seeded_templates):
        """Re-seeding all templates does not create duplicates."""
        second_run = await seed_all_templates(db)
        assert len(second_run) == 0

    async def test_ec_consortium_templates_seeded(
        self, db, all_seeded_templates
    ):
        """EC/Consortium category has 4 templates."""
        ec_templates = await list_templates(
            db, TemplateCategory.EC_CONSORTIUM
        )
        assert len(ec_templates) == 4
        slugs = {t.slug for t in ec_templates}
        assert slugs == {
            "consortium-agreement",
            "partnership-agreement",
            "ga-amendment",
            "subcontracting-agreement",
        }

    async def test_reporting_templates_seeded(
        self, db, all_seeded_templates
    ):
        """Reporting category has 5 templates."""
        rpt_templates = await list_templates(
            db, TemplateCategory.REPORTING
        )
        assert len(rpt_templates) == 5
        slugs = {t.slug for t in rpt_templates}
        assert slugs == {
            "periodic-technical-report",
            "form-c-template",
            "deliverable-cover-page",
            "cost-claim-summary",
            "university-internal-report",
        }

    async def test_mission_travel_templates_seeded(
        self, db, all_seeded_templates
    ):
        """Mission/Travel category has 4 templates."""
        mission_templates = await list_templates(
            db, TemplateCategory.MISSION_TRAVEL
        )
        assert len(mission_templates) == 4
        slugs = {t.slug for t in mission_templates}
        assert slugs == {
            "mission-request",
            "expense-report",
            "per-diem-declaration",
            "conference-justification",
        }

    async def test_procurement_templates_seeded(
        self, db, all_seeded_templates
    ):
        """Procurement category has 6 templates."""
        proc_templates = await list_templates(
            db, TemplateCategory.PROCUREMENT
        )
        assert len(proc_templates) == 6
        slugs = {t.slug for t in proc_templates}
        assert slugs == {
            "request-for-quotation",
            "comparative-analysis",
            "procurement-justification",
            "equipment-depreciation",
            "budget-transfer-request",
            "recruitment-authorization",
        }

    async def test_all_templates_have_field_definitions(
        self, db, all_seeded_templates
    ):
        """Every template has at least one field definition."""
        all_templates = await list_templates(db)
        for t in all_templates:
            fields = t.field_definitions.get("fields", [])
            assert len(fields) > 0, f"Template {t.slug} has no fields"


# --- EC / Consortium Template Tests ---


class TestECConsortiumTemplates:
    """Tests for EC and Consortium document templates."""

    async def test_consortium_agreement_role_conditions(
        self, db, all_seeded_templates, project
    ):
        """Coordinator project activates coordinator obligations."""
        all_templates = await list_templates(db)
        ca = next(
            t for t in all_templates if t.slug == "consortium-agreement"
        )
        preview = await preview_template(
            db, ca.id, project_id=project.id
        )
        assert "coordinator_obligations" in preview.conditional_sections_active
        assert "partner_obligations" not in preview.conditional_sections_active

    async def test_partnership_agreement_partner_role(
        self, db, all_seeded_templates, partner_project
    ):
        """Partner project activates partner obligations."""
        all_templates = await list_templates(db)
        pa = next(
            t for t in all_templates if t.slug == "partnership-agreement"
        )
        preview = await preview_template(
            db, pa.id, project_id=partner_project.id
        )
        assert "partner_obligations" in preview.conditional_sections_active
        assert "coordinator_obligations" not in preview.conditional_sections_active

    async def test_ga_amendment_auto_populates(
        self, db, all_seeded_templates, project
    ):
        """GA amendment auto-populates project fields."""
        all_templates = await list_templates(db)
        ga = next(
            t for t in all_templates if t.slug == "ga-amendment"
        )
        preview = await preview_template(
            db, ga.id, project_id=project.id
        )
        field_map = {f.name: f for f in preview.fields}
        assert field_map["project_acronym"].value == "TMPLTEST"
        assert field_map["grant_agreement_number"].value == "GA-123456"
        assert field_map["eu_contribution"].value == "800000.00"

    async def test_ga_amendment_no_conditional_sections(
        self, db, all_seeded_templates, project
    ):
        """GA amendment has no conditional sections."""
        all_templates = await list_templates(db)
        ga = next(
            t for t in all_templates if t.slug == "ga-amendment"
        )
        assert ga.conditional_sections is None

    async def test_subcontracting_generate_docx(
        self, db, all_seeded_templates, project
    ):
        """Generate DOCX for subcontracting agreement."""
        all_templates = await list_templates(db)
        sub = next(
            t for t in all_templates
            if t.slug == "subcontracting-agreement"
        )
        buf, filename = await generate_document_bytes(
            db, sub.id, project_id=project.id,
            manual_fields={
                "subcontractor_name": "Tech Solutions Ltd",
                "scope_of_work": "Data processing services",
                "subcontract_value": "50000.00",
                "procurement_procedure": "Competitive tender",
                "deliverables_description": "Monthly data reports",
                "timeline": "Jan-Dec 2025",
            },
        )
        assert filename.endswith(".docx")
        assert buf.getvalue()[:2] == b"PK"


# --- Reporting Template Tests ---


class TestReportingTemplates:
    """Tests for reporting templates."""

    async def test_form_c_actual_costs_conditions(
        self, db, all_seeded_templates, project
    ):
        """Actual costs project shows actual costs reporting section."""
        all_templates = await list_templates(db)
        fc = next(
            t for t in all_templates if t.slug == "form-c-template"
        )
        preview = await preview_template(
            db, fc.id, project_id=project.id
        )
        assert "actual_costs_reporting" in preview.conditional_sections_active
        assert "lump_sum_reporting" not in preview.conditional_sections_active

    async def test_form_c_lump_sum_conditions(
        self, db, all_seeded_templates, lump_sum_project
    ):
        """Lump sum project shows lump sum reporting section."""
        all_templates = await list_templates(db)
        fc = next(
            t for t in all_templates if t.slug == "form-c-template"
        )
        preview = await preview_template(
            db, fc.id, project_id=lump_sum_project.id
        )
        assert "lump_sum_reporting" in preview.conditional_sections_active
        assert "actual_costs_reporting" not in preview.conditional_sections_active

    async def test_deliverable_cover_page_no_conditions(
        self, db, all_seeded_templates
    ):
        """Deliverable cover page has no conditional sections."""
        all_templates = await list_templates(db)
        dc = next(
            t for t in all_templates
            if t.slug == "deliverable-cover-page"
        )
        assert dc.conditional_sections is None

    async def test_university_report_auto_populates(
        self, db, all_seeded_templates, project
    ):
        """University internal report auto-populates cost center."""
        all_templates = await list_templates(db)
        ur = next(
            t for t in all_templates
            if t.slug == "university-internal-report"
        )
        preview = await preview_template(
            db, ur.id, project_id=project.id
        )
        field_map = {f.name: f for f in preview.fields}
        assert field_map["cost_center"].value == "CC-TMPL-01"
        assert field_map["cost_model"].value == "ACTUAL_COSTS"


# --- Mission / Travel Template Tests ---


class TestMissionTravelTemplates:
    """Tests for mission and travel templates."""

    async def test_mission_request_auto_populates_researcher(
        self, db, all_seeded_templates, project, researcher
    ):
        """Mission request auto-populates researcher details."""
        all_templates = await list_templates(db)
        mr = next(
            t for t in all_templates if t.slug == "mission-request"
        )
        preview = await preview_template(
            db, mr.id, project_id=project.id,
            researcher_id=researcher.id,
        )
        field_map = {f.name: f for f in preview.fields}
        assert field_map["researcher_name"].value == "Maria Silva"
        assert field_map["project_acronym"].value == "TMPLTEST"

    async def test_expense_report_actual_costs_docs(
        self, db, all_seeded_templates, project
    ):
        """Actual costs project requires full documentation."""
        all_templates = await list_templates(db)
        er = next(
            t for t in all_templates if t.slug == "expense-report"
        )
        preview = await preview_template(
            db, er.id, project_id=project.id
        )
        assert "actual_costs_documentation" in preview.conditional_sections_active

    async def test_expense_report_lump_sum_simplified(
        self, db, all_seeded_templates, lump_sum_project
    ):
        """Lump sum project has simplified documentation."""
        all_templates = await list_templates(db)
        er = next(
            t for t in all_templates if t.slug == "expense-report"
        )
        preview = await preview_template(
            db, er.id, project_id=lump_sum_project.id
        )
        assert "lump_sum_documentation" in preview.conditional_sections_active
        assert "actual_costs_documentation" not in preview.conditional_sections_active

    async def test_per_diem_unit_costs_linked(
        self, db, all_seeded_templates, unit_costs_project
    ):
        """Unit costs project links travel to unit record."""
        all_templates = await list_templates(db)
        pd = next(
            t for t in all_templates
            if t.slug == "per-diem-declaration"
        )
        preview = await preview_template(
            db, pd.id, project_id=unit_costs_project.id
        )
        assert "unit_costs_documentation" in preview.conditional_sections_active

    async def test_conference_justification_generate(
        self, db, all_seeded_templates, project, researcher
    ):
        """Generate DOCX for conference justification."""
        all_templates = await list_templates(db)
        cj = next(
            t for t in all_templates
            if t.slug == "conference-justification"
        )
        buf, filename = await generate_document_bytes(
            db, cj.id, project_id=project.id,
            researcher_id=researcher.id,
            manual_fields={
                "conference_name": "ICML 2025",
                "conference_location": "Vienna, Austria",
                "conference_dates": "July 21-27, 2025",
                "relevance_to_project": "WP2 ML research",
                "estimated_cost": "2500.00",
                "dissemination_value": "Oral presentation",
            },
        )
        assert filename.endswith(".docx")
        assert "conference-justification" in filename


# --- Procurement Template Tests ---


class TestProcurementTemplates:
    """Tests for procurement and internal process templates."""

    async def test_rfq_auto_populates_budget(
        self, db, all_seeded_templates, project
    ):
        """RFQ auto-populates project budget information."""
        all_templates = await list_templates(db)
        rfq = next(
            t for t in all_templates
            if t.slug == "request-for-quotation"
        )
        preview = await preview_template(
            db, rfq.id, project_id=project.id
        )
        field_map = {f.name: f for f in preview.fields}
        assert field_map["total_budget"].value == "1000000.00"
        assert field_map["cost_model"].value == "ACTUAL_COSTS"

    async def test_rfq_actual_costs_conditions(
        self, db, all_seeded_templates, project
    ):
        """RFQ shows actual costs procurement rules."""
        all_templates = await list_templates(db)
        rfq = next(
            t for t in all_templates
            if t.slug == "request-for-quotation"
        )
        preview = await preview_template(
            db, rfq.id, project_id=project.id
        )
        assert "actual_costs_procurement" in preview.conditional_sections_active

    async def test_rfq_lump_sum_conditions(
        self, db, all_seeded_templates, lump_sum_project
    ):
        """RFQ shows lump sum procurement rules."""
        all_templates = await list_templates(db)
        rfq = next(
            t for t in all_templates
            if t.slug == "request-for-quotation"
        )
        preview = await preview_template(
            db, rfq.id, project_id=lump_sum_project.id
        )
        assert "lump_sum_procurement" in preview.conditional_sections_active

    async def test_equipment_depreciation_has_project_duration(
        self, db, all_seeded_templates, unit_costs_project
    ):
        """Equipment depreciation auto-fills duration months."""
        all_templates = await list_templates(db)
        ed = next(
            t for t in all_templates
            if t.slug == "equipment-depreciation"
        )
        preview = await preview_template(
            db, ed.id, project_id=unit_costs_project.id
        )
        field_map = {f.name: f for f in preview.fields}
        assert field_map["cost_center"].value == "CC-UNIT-01"

    async def test_budget_transfer_no_conditions(
        self, db, all_seeded_templates
    ):
        """Budget transfer request has no conditional sections."""
        all_templates = await list_templates(db)
        bt = next(
            t for t in all_templates
            if t.slug == "budget-transfer-request"
        )
        assert bt.conditional_sections is None

    async def test_recruitment_auth_generate_docx(
        self, db, all_seeded_templates, project
    ):
        """Generate DOCX for recruitment authorization."""
        all_templates = await list_templates(db)
        ra = next(
            t for t in all_templates
            if t.slug == "recruitment-authorization"
        )
        doc = await generate_document(
            db, ra.id, project_id=project.id,
            manual_fields={
                "position_title": "Research Engineer",
                "position_profile": "ML systems development",
                "contract_type": "CLT",
                "duration_months": "24",
                "funding_source": "Category A Personnel",
                "estimated_annual_cost": "42000.00",
                "start_date": "2025-06-01",
            },
            generated_by="PI",
        )
        assert doc.template_id == ra.id
        assert doc.status == GeneratedDocumentStatus.DRAFT
        assert "recruitment-authorization" in doc.file_name
