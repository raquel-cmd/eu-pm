"""Mission and Travel template definitions (Section 7.2.4).

Templates managing the complete travel lifecycle from request through
post-travel reporting. Per diem rates and cost categories are adapted
based on cost model.
"""

from app.models.enums import TemplateCategory

_MISSION_PROJECT_FIELDS = [
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
        "required": False,
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
        "name": "cost_model",
        "label": "Cost Model",
        "field_type": "auto",
        "data_type": "text",
        "data_source": "project.cost_model",
        "required": True,
    },
    {
        "name": "cost_center",
        "label": "Internal Cost Center",
        "field_type": "auto",
        "data_type": "text",
        "data_source": "project.internal_cost_center",
        "required": False,
    },
]

_MISSION_RESEARCHER_FIELDS = [
    {
        "name": "researcher_name",
        "label": "Researcher Name",
        "field_type": "auto",
        "data_type": "text",
        "data_source": "researcher.name",
        "required": True,
    },
    {
        "name": "researcher_email",
        "label": "Email",
        "field_type": "auto",
        "data_type": "text",
        "data_source": "researcher.email",
        "required": False,
    },
    {
        "name": "position",
        "label": "Position",
        "field_type": "auto",
        "data_type": "text",
        "data_source": "researcher.position",
        "required": True,
    },
]

# Cost-model-aware conditional sections for mission/travel
_MISSION_COST_MODEL_CONDITIONS = {
    "actual_costs_documentation": {
        "section_name": "Post-Travel Documentation (Actual Costs)",
        "condition_field": "project.cost_model",
        "condition_value": "ACTUAL_COSTS",
        "condition_operator": "eq",
        "content_label": (
            "Post-travel documentation is mandatory. Required documents: "
            "boarding passes, hotel invoices, transport tickets, per diem "
            "declarations. The system will reconcile estimated vs actual "
            "costs and verify EC eligibility. Final expenses are categorized "
            "under EC budget line C.1 (travel and subsistence). All "
            "documentation must be linked for audit purposes."
        ),
    },
    "lump_sum_documentation": {
        "section_name": "Travel Documentation (Lump Sum)",
        "condition_field": "project.cost_model",
        "condition_value": "LUMP_SUM",
        "condition_operator": "eq",
        "content_label": (
            "Internal approval workflow applies. University travel policies "
            "must be followed regardless of EC cost model. Post-travel "
            "documentation requirements are simplified. Costs are recorded "
            "for internal budget monitoring without enforcing EC eligibility "
            "rules. No boarding passes or individual receipts required for "
            "EC reporting purposes."
        ),
    },
    "unit_costs_documentation": {
        "section_name": "Unit-Linked Travel Documentation",
        "condition_field": "project.cost_model",
        "condition_value": "UNIT_COSTS",
        "condition_operator": "eq",
        "content_label": (
            "If travel is part of a defined unit (e.g., training event), "
            "this mission is linked to the unit record rather than claimed "
            "as an individual expense. The system tracks the mission as "
            "evidence of unit delivery."
        ),
    },
}


def _mission_request_manual_fields() -> list[dict]:
    """Manual input fields for Mission Request / Travel Authorization."""
    return [
        {
            "name": "destination",
            "label": "Destination (City, Country)",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "purpose",
            "label": "Purpose of Mission",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
            "help_text": (
                "Conference, consortium meeting, fieldwork, training, etc."
            ),
        },
        {
            "name": "start_date",
            "label": "Travel Start Date",
            "field_type": "manual",
            "data_type": "date",
            "required": True,
        },
        {
            "name": "end_date",
            "label": "Travel End Date",
            "field_type": "manual",
            "data_type": "date",
            "required": True,
        },
        {
            "name": "work_package",
            "label": "Related Work Package",
            "field_type": "manual",
            "data_type": "text",
            "required": False,
        },
        {
            "name": "estimated_travel_costs",
            "label": "Estimated Travel Costs (EUR)",
            "field_type": "manual",
            "data_type": "decimal",
            "required": True,
        },
        {
            "name": "estimated_accommodation",
            "label": "Estimated Accommodation Costs (EUR)",
            "field_type": "manual",
            "data_type": "decimal",
            "required": False,
        },
        {
            "name": "estimated_subsistence",
            "label": "Estimated Subsistence / Per Diem (EUR)",
            "field_type": "manual",
            "data_type": "decimal",
            "required": False,
        },
        {
            "name": "estimated_registration",
            "label": "Estimated Registration Fees (EUR)",
            "field_type": "manual",
            "data_type": "decimal",
            "required": False,
        },
    ]


def _expense_report_manual_fields() -> list[dict]:
    """Manual input fields for Mission Expense Report."""
    return [
        {
            "name": "destination",
            "label": "Destination",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "travel_dates",
            "label": "Travel Dates (from - to)",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "actual_travel_costs",
            "label": "Actual Travel Costs (EUR)",
            "field_type": "manual",
            "data_type": "decimal",
            "required": True,
        },
        {
            "name": "actual_accommodation",
            "label": "Actual Accommodation Costs (EUR)",
            "field_type": "manual",
            "data_type": "decimal",
            "required": False,
        },
        {
            "name": "actual_subsistence",
            "label": "Actual Subsistence / Per Diem (EUR)",
            "field_type": "manual",
            "data_type": "decimal",
            "required": False,
        },
        {
            "name": "actual_registration",
            "label": "Actual Registration Fees (EUR)",
            "field_type": "manual",
            "data_type": "decimal",
            "required": False,
        },
        {
            "name": "actual_other_costs",
            "label": "Other Costs (EUR)",
            "field_type": "manual",
            "data_type": "decimal",
            "required": False,
        },
        {
            "name": "receipts_summary",
            "label": "Receipts and Supporting Documents",
            "field_type": "manual",
            "data_type": "text",
            "required": False,
            "help_text": "List attached receipts and invoices.",
        },
    ]


def _per_diem_declaration_manual_fields() -> list[dict]:
    """Manual input fields for Per Diem Declaration."""
    return [
        {
            "name": "destination",
            "label": "Destination (City, Country)",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "travel_start_date",
            "label": "Travel Start Date",
            "field_type": "manual",
            "data_type": "date",
            "required": True,
        },
        {
            "name": "travel_end_date",
            "label": "Travel End Date",
            "field_type": "manual",
            "data_type": "date",
            "required": True,
        },
        {
            "name": "daily_rate",
            "label": "Daily Per Diem Rate (EUR)",
            "field_type": "manual",
            "data_type": "decimal",
            "required": True,
            "help_text": "Per institutional travel policy rate tables.",
        },
        {
            "name": "number_of_full_days",
            "label": "Number of Full Days",
            "field_type": "manual",
            "data_type": "integer",
            "required": True,
        },
        {
            "name": "partial_day_adjustments",
            "label": "Partial Day Adjustments",
            "field_type": "manual",
            "data_type": "text",
            "required": False,
            "help_text": (
                "Departure/arrival day adjustments, meals provided, etc."
            ),
        },
        {
            "name": "total_per_diem",
            "label": "Total Per Diem Claimed (EUR)",
            "field_type": "manual",
            "data_type": "decimal",
            "required": True,
        },
    ]


def _conference_justification_manual_fields() -> list[dict]:
    """Manual input fields for Conference Attendance Justification."""
    return [
        {
            "name": "conference_name",
            "label": "Conference Name",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "conference_location",
            "label": "Conference Location",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "conference_dates",
            "label": "Conference Dates",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "relevance_to_project",
            "label": "Relevance to Project Work Packages",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
            "help_text": "Explain how attendance relates to project WPs.",
        },
        {
            "name": "estimated_cost",
            "label": "Estimated Total Cost (EUR)",
            "field_type": "manual",
            "data_type": "decimal",
            "required": True,
        },
        {
            "name": "dissemination_value",
            "label": "Dissemination Value",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
            "help_text": (
                "Expected dissemination outcomes: presentation, poster, "
                "paper, networking."
            ),
        },
        {
            "name": "presentation_details",
            "label": "Presentation / Paper Details",
            "field_type": "manual",
            "data_type": "text",
            "required": False,
            "help_text": "Title and type of any accepted contribution.",
        },
    ]


MISSION_TRAVEL_TEMPLATE_DEFINITIONS: dict[str, dict] = {
    "mission-request": {
        "name": "Mission Request / Travel Authorization",
        "slug": "mission-request",
        "description": (
            "Pre-travel authorization request. Auto-fills researcher "
            "details, project, WP, budget line, and per diem rates."
        ),
        "category": TemplateCategory.MISSION_TRAVEL,
        "personnel_type": None,
        "field_definitions": {
            "fields": _MISSION_PROJECT_FIELDS
            + _MISSION_RESEARCHER_FIELDS
            + _mission_request_manual_fields()
        },
        "conditional_sections": _MISSION_COST_MODEL_CONDITIONS,
    },
    "expense-report": {
        "name": "Mission Expense Report",
        "slug": "expense-report",
        "description": (
            "Post-travel expense report. Auto-fills mission details, "
            "dates, destination, and pre-filled cost categories."
        ),
        "category": TemplateCategory.MISSION_TRAVEL,
        "personnel_type": None,
        "field_definitions": {
            "fields": _MISSION_PROJECT_FIELDS
            + _MISSION_RESEARCHER_FIELDS
            + _expense_report_manual_fields()
        },
        "conditional_sections": _MISSION_COST_MODEL_CONDITIONS,
    },
    "per-diem-declaration": {
        "name": "Per Diem Declaration",
        "slug": "per-diem-declaration",
        "description": (
            "Declaration for subsistence claimed as flat rate. "
            "Auto-populates destination rates and partial day calculations."
        ),
        "category": TemplateCategory.MISSION_TRAVEL,
        "personnel_type": None,
        "field_definitions": {
            "fields": _MISSION_PROJECT_FIELDS
            + _MISSION_RESEARCHER_FIELDS
            + _per_diem_declaration_manual_fields()
        },
        "conditional_sections": _MISSION_COST_MODEL_CONDITIONS,
    },
    "conference-justification": {
        "name": "Conference Attendance Justification",
        "slug": "conference-justification",
        "description": (
            "Justification for conference attendance and registration. "
            "Links to project WPs, estimated costs, and dissemination value."
        ),
        "category": TemplateCategory.MISSION_TRAVEL,
        "personnel_type": None,
        "field_definitions": {
            "fields": _MISSION_PROJECT_FIELDS
            + _MISSION_RESEARCHER_FIELDS
            + _conference_justification_manual_fields()
        },
        "conditional_sections": _MISSION_COST_MODEL_CONDITIONS,
    },
}
