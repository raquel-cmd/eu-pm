"""Reporting template definitions (Section 7.2.3).

Templates for EC and institutional reporting, including technical reports,
Form C, deliverable cover pages, cost claim summaries, and university
internal reports.
"""

from app.models.enums import TemplateCategory

_REPORTING_PROJECT_FIELDS = [
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
        "name": "cost_model",
        "label": "Cost Model",
        "field_type": "auto",
        "data_type": "text",
        "data_source": "project.cost_model",
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
        "name": "funding_rate",
        "label": "Funding Rate (%)",
        "field_type": "auto",
        "data_type": "decimal",
        "data_source": "project.funding_rate",
        "required": False,
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

# Cost-model-aware conditional sections for reporting templates
_REPORTING_COST_MODEL_CONDITIONS = {
    "actual_costs_reporting": {
        "section_name": "Actual Costs Financial Reporting",
        "condition_field": "project.cost_model",
        "condition_value": "ACTUAL_COSTS",
        "condition_operator": "eq",
        "content_label": (
            "Financial report follows EC Form C format with detailed "
            "cost breakdown per category A-E. All expenses require "
            "supporting documentation references. Indirect costs "
            "calculated at 25% flat rate on categories A+C+D."
        ),
    },
    "lump_sum_reporting": {
        "section_name": "Lump Sum Financial Reporting",
        "condition_field": "project.cost_model",
        "condition_value": "LUMP_SUM",
        "condition_operator": "eq",
        "content_label": (
            "Financial report uses WP completion declarations showing "
            "deliverable links and payment trigger conditions. No "
            "individual expense tracking required for EC reporting."
        ),
    },
    "unit_costs_reporting": {
        "section_name": "Unit Costs Financial Reporting",
        "condition_field": "project.cost_model",
        "condition_value": "UNIT_COSTS",
        "condition_operator": "eq",
        "content_label": (
            "Financial report shows units delivered multiplied by "
            "pre-agreed rate, with evidence of unit delivery."
        ),
    },
}


def _periodic_technical_report_manual_fields() -> list[dict]:
    """Manual input fields for Periodic Technical Report."""
    return [
        {
            "name": "reporting_period",
            "label": "Reporting Period (e.g., RP1, RP2)",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "period_start_date",
            "label": "Period Start Date",
            "field_type": "manual",
            "data_type": "date",
            "required": True,
        },
        {
            "name": "period_end_date",
            "label": "Period End Date",
            "field_type": "manual",
            "data_type": "date",
            "required": True,
        },
        {
            "name": "executive_summary",
            "label": "Executive Summary",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
            "help_text": "High-level summary of progress during this period.",
        },
        {
            "name": "wp_progress_narrative",
            "label": "Work Package Progress Narrative",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
            "help_text": "Narrative for each WP describing activities and results.",
        },
        {
            "name": "deviations",
            "label": "Deviations from Work Plan",
            "field_type": "manual",
            "data_type": "text",
            "required": False,
            "help_text": "Describe any deviations and corrective actions.",
        },
    ]


def _form_c_manual_fields() -> list[dict]:
    """Manual input fields for Form C (Periodic Financial Report)."""
    return [
        {
            "name": "reporting_period",
            "label": "Reporting Period",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "partner_name",
            "label": "Partner Name",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "category_a_personnel",
            "label": "Category A - Personnel Costs (EUR)",
            "field_type": "manual",
            "data_type": "decimal",
            "required": True,
        },
        {
            "name": "category_b_subcontracting",
            "label": "Category B - Subcontracting (EUR)",
            "field_type": "manual",
            "data_type": "decimal",
            "required": False,
        },
        {
            "name": "category_c_travel",
            "label": "Category C - Travel and Subsistence (EUR)",
            "field_type": "manual",
            "data_type": "decimal",
            "required": False,
        },
        {
            "name": "category_d_equipment",
            "label": "Category D - Equipment and Other (EUR)",
            "field_type": "manual",
            "data_type": "decimal",
            "required": False,
        },
        {
            "name": "supporting_docs_reference",
            "label": "Supporting Documentation Reference",
            "field_type": "manual",
            "data_type": "text",
            "required": False,
            "help_text": "References to attached supporting documents.",
        },
    ]


def _deliverable_cover_page_manual_fields() -> list[dict]:
    """Manual input fields for Deliverable Cover Page."""
    return [
        {
            "name": "deliverable_number",
            "label": "Deliverable Number (e.g., D1.1)",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "deliverable_title",
            "label": "Deliverable Title",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "work_package_number",
            "label": "Work Package Number",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "authors",
            "label": "Authors",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "dissemination_level",
            "label": "Dissemination Level (PU/SEN/CO)",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "due_date",
            "label": "Due Date (Month)",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "submission_date",
            "label": "Actual Submission Date",
            "field_type": "manual",
            "data_type": "date",
            "required": True,
        },
        {
            "name": "revision_history",
            "label": "Revision History",
            "field_type": "manual",
            "data_type": "text",
            "required": False,
            "help_text": "Version, date, author, description of changes.",
        },
    ]


def _cost_claim_summary_manual_fields() -> list[dict]:
    """Manual input fields for Cost Claim Summary."""
    return [
        {
            "name": "reporting_period",
            "label": "Reporting Period",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "partner_name",
            "label": "Partner Name",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "expenses_summary",
            "label": "Expenses Summary per Category",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
            "help_text": "Breakdown of expenses by EC budget category.",
        },
        {
            "name": "exchange_rate_applied",
            "label": "Exchange Rate Applied (if applicable)",
            "field_type": "manual",
            "data_type": "text",
            "required": False,
        },
        {
            "name": "supporting_doc_references",
            "label": "Supporting Document References",
            "field_type": "manual",
            "data_type": "text",
            "required": False,
        },
    ]


def _university_internal_report_manual_fields() -> list[dict]:
    """Manual input fields for University Internal Report."""
    return [
        {
            "name": "reporting_year",
            "label": "Reporting Year",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "budget_execution_summary",
            "label": "Budget Execution Summary",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
            "help_text": (
                "Overview of budget burn rate and spending by category."
            ),
        },
        {
            "name": "pm_summary",
            "label": "Person-Month Summary",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "recruitment_status",
            "label": "Recruitment Status",
            "field_type": "manual",
            "data_type": "text",
            "required": False,
            "help_text": "Current and planned recruitment on the project.",
        },
        {
            "name": "cash_flow_status",
            "label": "Cash Flow Status",
            "field_type": "manual",
            "data_type": "text",
            "required": False,
            "help_text": "EC payments received vs expenditure.",
        },
        {
            "name": "overhead_calculation_notes",
            "label": "Overhead Calculation Notes",
            "field_type": "manual",
            "data_type": "text",
            "required": False,
            "help_text": "Notes on university overhead methodology applied.",
        },
    ]


REPORTING_TEMPLATE_DEFINITIONS: dict[str, dict] = {
    "periodic-technical-report": {
        "name": "Periodic Technical Report",
        "slug": "periodic-technical-report",
        "description": (
            "Template for EC periodic technical reports. Auto-populates "
            "project info, period dates, WP structure, and partner list."
        ),
        "category": TemplateCategory.REPORTING,
        "personnel_type": None,
        "field_definitions": {
            "fields": _REPORTING_PROJECT_FIELDS
            + _periodic_technical_report_manual_fields()
        },
        "conditional_sections": _REPORTING_COST_MODEL_CONDITIONS,
    },
    "form-c-template": {
        "name": "Periodic Financial Report (Form C)",
        "slug": "form-c-template",
        "description": (
            "EC Form C financial report template. Auto-fills partner "
            "cost categories, PM claims, and indirect cost calculations."
        ),
        "category": TemplateCategory.REPORTING,
        "personnel_type": None,
        "field_definitions": {
            "fields": _REPORTING_PROJECT_FIELDS
            + _form_c_manual_fields()
        },
        "conditional_sections": _REPORTING_COST_MODEL_CONDITIONS,
    },
    "deliverable-cover-page": {
        "name": "Deliverable Cover Page",
        "slug": "deliverable-cover-page",
        "description": (
            "Cover page for deliverable submissions. Auto-fills D number, "
            "title, authors, revision history, and dissemination level."
        ),
        "category": TemplateCategory.REPORTING,
        "personnel_type": None,
        "field_definitions": {
            "fields": _REPORTING_PROJECT_FIELDS
            + _deliverable_cover_page_manual_fields()
        },
        "conditional_sections": None,
    },
    "cost-claim-summary": {
        "name": "Cost Claim Summary",
        "slug": "cost-claim-summary",
        "description": (
            "Per-partner cost claim summary with expenses per category, "
            "exchange rates, and supporting document references."
        ),
        "category": TemplateCategory.REPORTING,
        "personnel_type": None,
        "field_definitions": {
            "fields": _REPORTING_PROJECT_FIELDS
            + _cost_claim_summary_manual_fields()
        },
        "conditional_sections": _REPORTING_COST_MODEL_CONDITIONS,
    },
    "university-internal-report": {
        "name": "University Internal Report",
        "slug": "university-internal-report",
        "description": (
            "Internal report mapping EC budget categories to institutional "
            "account codes, with overhead calculations following university "
            "methodology."
        ),
        "category": TemplateCategory.REPORTING,
        "personnel_type": None,
        "field_definitions": {
            "fields": _REPORTING_PROJECT_FIELDS
            + _university_internal_report_manual_fields()
        },
        "conditional_sections": _REPORTING_COST_MODEL_CONDITIONS,
    },
}
