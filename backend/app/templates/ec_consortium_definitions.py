"""EC and Consortium document template definitions (Section 7.2.2).

Templates for inter-organizational agreements required by the European
Commission and consortium governance.
"""

from app.models.enums import TemplateCategory

# Common auto-populated project fields for EC / consortium documents
_EC_PROJECT_FIELDS = [
    {
        "name": "project_acronym",
        "label": "Project Acronym",
        "field_type": "auto",
        "data_type": "text",
        "data_source": "project.acronym",
        "required": True,
    },
    {
        "name": "grant_agreement_number",
        "label": "Grant Agreement Number",
        "field_type": "auto",
        "data_type": "text",
        "data_source": "project.grant_agreement_number",
        "required": True,
    },
    {
        "name": "project_title",
        "label": "Project Full Title",
        "field_type": "auto",
        "data_type": "text",
        "data_source": "project.full_title",
        "required": True,
    },
    {
        "name": "programme",
        "label": "Funding Programme",
        "field_type": "auto",
        "data_type": "text",
        "data_source": "project.programme",
        "required": True,
    },
    {
        "name": "project_role",
        "label": "Project Role",
        "field_type": "auto",
        "data_type": "text",
        "data_source": "project.role",
        "required": True,
    },
    {
        "name": "project_start_date",
        "label": "Project Start Date",
        "field_type": "auto",
        "data_type": "date",
        "data_source": "project.start_date",
        "required": False,
    },
    {
        "name": "project_end_date",
        "label": "Project End Date",
        "field_type": "auto",
        "data_type": "date",
        "data_source": "project.end_date",
        "required": False,
    },
    {
        "name": "total_budget",
        "label": "Total Budget (EUR)",
        "field_type": "auto",
        "data_type": "decimal",
        "data_source": "project.total_budget",
        "required": False,
    },
    {
        "name": "eu_contribution",
        "label": "EU Contribution (EUR)",
        "field_type": "auto",
        "data_type": "decimal",
        "data_source": "project.eu_contribution",
        "required": False,
    },
    {
        "name": "ec_project_officer",
        "label": "EC Project Officer",
        "field_type": "auto",
        "data_type": "text",
        "data_source": "project.ec_project_officer",
        "required": False,
    },
]

# Conditional sections for coordinator vs partner role
_ROLE_CONDITIONS = {
    "coordinator_obligations": {
        "section_name": "Coordinator Obligations",
        "condition_field": "project.role",
        "condition_value": "COORDINATOR",
        "condition_operator": "eq",
        "content_label": (
            "As coordinator, the institution is responsible for the overall "
            "management of the consortium, including financial distribution, "
            "periodic reporting to the EC, and organizing review meetings."
        ),
    },
    "partner_obligations": {
        "section_name": "Partner Obligations",
        "condition_field": "project.role",
        "condition_value": "PARTNER",
        "condition_operator": "eq",
        "content_label": (
            "As partner, the institution is responsible for delivering its "
            "assigned work packages, submitting financial claims to the "
            "coordinator, and participating in consortium meetings."
        ),
    },
}


def _consortium_agreement_manual_fields() -> list[dict]:
    """Manual input fields for Consortium Agreement."""
    return [
        {
            "name": "partner_list",
            "label": "Partner List (names and PIC numbers)",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
            "help_text": "List all consortium partners with PIC numbers.",
        },
        {
            "name": "wp_structure_summary",
            "label": "Work Package Structure Summary",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
            "help_text": "Outline of WP structure and partner responsibilities.",
        },
        {
            "name": "ip_background_list",
            "label": "IP Background List",
            "field_type": "manual",
            "data_type": "text",
            "required": False,
            "help_text": "List of pre-existing IP brought into the project.",
        },
        {
            "name": "governance_structure",
            "label": "Governance Structure",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
            "help_text": (
                "Decision-making bodies: General Assembly, Steering "
                "Committee, etc."
            ),
        },
        {
            "name": "legal_signatory",
            "label": "Legal Signatory Name and Title",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
    ]


def _partnership_agreement_manual_fields() -> list[dict]:
    """Manual input fields for Partnership Agreement."""
    return [
        {
            "name": "partner_legal_name",
            "label": "Partner Legal Name",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "partner_pic_number",
            "label": "Partner PIC Number",
            "field_type": "manual",
            "data_type": "text",
            "required": False,
        },
        {
            "name": "scope_of_work",
            "label": "Scope of Collaboration",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
            "help_text": "WP scope and deliverables for this partnership.",
        },
        {
            "name": "budget_allocation",
            "label": "Budget Allocation (EUR)",
            "field_type": "manual",
            "data_type": "decimal",
            "required": True,
        },
        {
            "name": "ip_clauses",
            "label": "Intellectual Property Clauses",
            "field_type": "manual",
            "data_type": "text",
            "required": False,
            "help_text": "Specific IP arrangements for this partnership.",
        },
        {
            "name": "legal_signatory",
            "label": "Legal Signatory Name and Title",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
    ]


def _ga_amendment_manual_fields() -> list[dict]:
    """Manual input fields for Grant Agreement Amendment."""
    return [
        {
            "name": "amendment_type",
            "label": "Amendment Type",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
            "help_text": (
                "E.g., budget transfer, timeline change, partner change."
            ),
        },
        {
            "name": "current_provision",
            "label": "Current GA Provision",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
            "help_text": "The current text or value being amended.",
        },
        {
            "name": "proposed_change",
            "label": "Proposed Change",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "justification",
            "label": "Justification for Amendment",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "impact_assessment",
            "label": "Impact on Project Objectives and Budget",
            "field_type": "manual",
            "data_type": "text",
            "required": False,
        },
    ]


def _subcontracting_agreement_manual_fields() -> list[dict]:
    """Manual input fields for Subcontracting Agreement."""
    return [
        {
            "name": "subcontractor_name",
            "label": "Subcontractor Legal Name",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "scope_of_work",
            "label": "Scope of Subcontracted Work",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "subcontract_value",
            "label": "Subcontract Value (EUR)",
            "field_type": "manual",
            "data_type": "decimal",
            "required": True,
        },
        {
            "name": "procurement_procedure",
            "label": "Procurement Procedure Used",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
            "help_text": (
                "Describe the procurement process following EC rules."
            ),
        },
        {
            "name": "deliverables_description",
            "label": "Expected Deliverables",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "timeline",
            "label": "Delivery Timeline",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
    ]


EC_CONSORTIUM_TEMPLATE_DEFINITIONS: dict[str, dict] = {
    "consortium-agreement": {
        "name": "Consortium Agreement (DESCA-based)",
        "slug": "consortium-agreement",
        "description": (
            "Consortium agreement for new projects, based on DESCA model. "
            "Auto-fills partner details, WP structure, and IP background."
        ),
        "category": TemplateCategory.EC_CONSORTIUM,
        "personnel_type": None,
        "field_definitions": {
            "fields": _EC_PROJECT_FIELDS
            + _consortium_agreement_manual_fields()
        },
        "conditional_sections": _ROLE_CONDITIONS,
    },
    "partnership-agreement": {
        "name": "Partnership Agreement",
        "slug": "partnership-agreement",
        "description": (
            "Bilateral partnership agreement with a specific partner. "
            "Auto-fills project details and partner scope."
        ),
        "category": TemplateCategory.EC_CONSORTIUM,
        "personnel_type": None,
        "field_definitions": {
            "fields": _EC_PROJECT_FIELDS
            + _partnership_agreement_manual_fields()
        },
        "conditional_sections": _ROLE_CONDITIONS,
    },
    "ga-amendment": {
        "name": "Grant Agreement Amendment",
        "slug": "ga-amendment",
        "description": (
            "Request for amendment to the Grant Agreement. Auto-fills "
            "current GA details and justification framework."
        ),
        "category": TemplateCategory.EC_CONSORTIUM,
        "personnel_type": None,
        "field_definitions": {
            "fields": _EC_PROJECT_FIELDS
            + _ga_amendment_manual_fields()
        },
        "conditional_sections": None,
    },
    "subcontracting-agreement": {
        "name": "Subcontracting Agreement",
        "slug": "subcontracting-agreement",
        "description": (
            "Subcontracting agreement following EC procurement rules. "
            "Auto-fills project details and budget line information."
        ),
        "category": TemplateCategory.EC_CONSORTIUM,
        "personnel_type": None,
        "field_definitions": {
            "fields": _EC_PROJECT_FIELDS
            + _subcontracting_agreement_manual_fields()
        },
        "conditional_sections": None,
    },
}
