"""Procurement and Internal Process template definitions (Section 7.2.5).

Templates for procurement governance, budget management, equipment
depreciation, and recruitment authorization.
"""

from app.models.enums import TemplateCategory

_PROCUREMENT_PROJECT_FIELDS = [
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
        "name": "total_budget",
        "label": "Total Budget (EUR)",
        "field_type": "auto",
        "data_type": "decimal",
        "data_source": "project.total_budget",
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
        "name": "duration_months",
        "label": "Project Duration (months)",
        "field_type": "auto",
        "data_type": "integer",
        "data_source": "project.duration_months",
        "required": False,
    },
]

# Cost-model-aware procurement conditions
_PROCUREMENT_COST_MODEL_CONDITIONS = {
    "actual_costs_procurement": {
        "section_name": "Procurement Rules (Actual Costs)",
        "condition_field": "project.cost_model",
        "condition_value": "ACTUAL_COSTS",
        "condition_operator": "eq",
        "content_label": (
            "Under the actual costs model, all procurement must follow "
            "EC procurement rules. Purchases above the threshold require "
            "competitive bidding. All invoices and receipts must be "
            "maintained for audit purposes. Equipment is charged based "
            "on depreciation over the project lifetime."
        ),
    },
    "lump_sum_procurement": {
        "section_name": "Procurement Rules (Lump Sum)",
        "condition_field": "project.cost_model",
        "condition_value": "LUMP_SUM",
        "condition_operator": "eq",
        "content_label": (
            "Under the lump sum model, EC procurement rules do not "
            "apply to individual purchases. However, university internal "
            "procurement policies must still be followed. Purchases are "
            "tracked for internal budget monitoring."
        ),
    },
    "unit_costs_procurement": {
        "section_name": "Procurement Rules (Unit Costs)",
        "condition_field": "project.cost_model",
        "condition_value": "UNIT_COSTS",
        "condition_operator": "eq",
        "content_label": (
            "Under the unit costs model, equipment or services that "
            "are part of a defined unit should be linked to the "
            "corresponding unit record. Procurement follows standard "
            "institutional policies."
        ),
    },
}


def _rfq_manual_fields() -> list[dict]:
    """Manual input fields for Request for Quotation."""
    return [
        {
            "name": "item_description",
            "label": "Item / Service Description",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "budget_line",
            "label": "Budget Line / EC Category",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
            "help_text": "E.g., C.2 Equipment, D. Other Costs.",
        },
        {
            "name": "estimated_value",
            "label": "Estimated Value (EUR)",
            "field_type": "manual",
            "data_type": "decimal",
            "required": True,
        },
        {
            "name": "technical_specifications",
            "label": "Technical Specifications",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "evaluation_criteria",
            "label": "Evaluation Criteria",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
            "help_text": "Criteria for evaluating quotes (price, quality, etc.).",
        },
        {
            "name": "submission_deadline",
            "label": "Quotation Submission Deadline",
            "field_type": "manual",
            "data_type": "date",
            "required": True,
        },
    ]


def _comparative_analysis_manual_fields() -> list[dict]:
    """Manual input fields for Comparative Analysis Form."""
    return [
        {
            "name": "item_description",
            "label": "Item / Service Description",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "supplier_1_name",
            "label": "Supplier 1 Name",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "supplier_1_price",
            "label": "Supplier 1 Price (EUR)",
            "field_type": "manual",
            "data_type": "decimal",
            "required": True,
        },
        {
            "name": "supplier_2_name",
            "label": "Supplier 2 Name",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "supplier_2_price",
            "label": "Supplier 2 Price (EUR)",
            "field_type": "manual",
            "data_type": "decimal",
            "required": True,
        },
        {
            "name": "supplier_3_name",
            "label": "Supplier 3 Name",
            "field_type": "manual",
            "data_type": "text",
            "required": False,
        },
        {
            "name": "supplier_3_price",
            "label": "Supplier 3 Price (EUR)",
            "field_type": "manual",
            "data_type": "decimal",
            "required": False,
        },
        {
            "name": "scoring_summary",
            "label": "Scoring Matrix Summary",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
            "help_text": "Summary of scoring based on evaluation criteria.",
        },
        {
            "name": "recommended_supplier",
            "label": "Recommended Supplier",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
    ]


def _procurement_justification_manual_fields() -> list[dict]:
    """Manual input fields for Procurement Justification."""
    return [
        {
            "name": "item_description",
            "label": "Item / Service Description",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "procurement_type",
            "label": "Procurement Type",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
            "help_text": "Single-source, above threshold, framework, etc.",
        },
        {
            "name": "supplier_name",
            "label": "Proposed Supplier",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "value",
            "label": "Procurement Value (EUR)",
            "field_type": "manual",
            "data_type": "decimal",
            "required": True,
        },
        {
            "name": "justification",
            "label": "Justification",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
            "help_text": (
                "Explain why competitive bidding was not possible or "
                "why this supplier was selected."
            ),
        },
        {
            "name": "applicable_rules",
            "label": "Applicable EC and University Rules",
            "field_type": "manual",
            "data_type": "text",
            "required": False,
            "help_text": "Reference to applicable procurement regulations.",
        },
    ]


def _equipment_depreciation_manual_fields() -> list[dict]:
    """Manual input fields for Equipment Depreciation Calculation."""
    return [
        {
            "name": "equipment_description",
            "label": "Equipment Description",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "purchase_cost",
            "label": "Purchase Cost (EUR)",
            "field_type": "manual",
            "data_type": "decimal",
            "required": True,
        },
        {
            "name": "purchase_date",
            "label": "Purchase Date",
            "field_type": "manual",
            "data_type": "date",
            "required": True,
        },
        {
            "name": "useful_life_years",
            "label": "Useful Life (years)",
            "field_type": "manual",
            "data_type": "integer",
            "required": True,
            "help_text": "Depreciation period per institutional policy.",
        },
        {
            "name": "usage_percentage",
            "label": "Project Usage Percentage (%)",
            "field_type": "manual",
            "data_type": "decimal",
            "required": True,
            "help_text": "Percentage of time used on this project.",
        },
        {
            "name": "eligible_amount",
            "label": "Eligible Amount for Project (EUR)",
            "field_type": "manual",
            "data_type": "decimal",
            "required": True,
            "help_text": (
                "Calculated: (cost / useful_life) * project_duration_months "
                "/ 12 * usage_percentage / 100."
            ),
        },
    ]


def _budget_transfer_manual_fields() -> list[dict]:
    """Manual input fields for Budget Transfer Request."""
    return [
        {
            "name": "transfer_from_category",
            "label": "Transfer From (EC Category)",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
            "help_text": "EC budget category to transfer from.",
        },
        {
            "name": "transfer_to_category",
            "label": "Transfer To (EC Category)",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "transfer_amount",
            "label": "Transfer Amount (EUR)",
            "field_type": "manual",
            "data_type": "decimal",
            "required": True,
        },
        {
            "name": "current_from_budget",
            "label": "Current Budget in Source Category (EUR)",
            "field_type": "manual",
            "data_type": "decimal",
            "required": True,
        },
        {
            "name": "current_to_budget",
            "label": "Current Budget in Target Category (EUR)",
            "field_type": "manual",
            "data_type": "decimal",
            "required": True,
        },
        {
            "name": "justification",
            "label": "Justification for Transfer",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "impact_assessment",
            "label": "Impact on Deliverables and Objectives",
            "field_type": "manual",
            "data_type": "text",
            "required": False,
        },
    ]


def _recruitment_authorization_manual_fields() -> list[dict]:
    """Manual input fields for Recruitment Authorization."""
    return [
        {
            "name": "position_title",
            "label": "Position Title",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "position_profile",
            "label": "Position Profile / Description",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "contract_type",
            "label": "Contract Type",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
            "help_text": "DL57, CEEC, BI, BD, BPD, CLT, etc.",
        },
        {
            "name": "duration_months",
            "label": "Contract Duration (months)",
            "field_type": "manual",
            "data_type": "integer",
            "required": True,
        },
        {
            "name": "funding_source",
            "label": "Funding Source and Budget Line",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
            "help_text": "Project budget line funding this position.",
        },
        {
            "name": "estimated_annual_cost",
            "label": "Estimated Annual Cost (EUR)",
            "field_type": "manual",
            "data_type": "decimal",
            "required": True,
        },
        {
            "name": "work_package",
            "label": "Work Package Assignment",
            "field_type": "manual",
            "data_type": "text",
            "required": False,
        },
        {
            "name": "start_date",
            "label": "Expected Start Date",
            "field_type": "manual",
            "data_type": "date",
            "required": True,
        },
    ]


PROCUREMENT_TEMPLATE_DEFINITIONS: dict[str, dict] = {
    "request-for-quotation": {
        "name": "Request for Quotation",
        "slug": "request-for-quotation",
        "description": (
            "Request for quotation for purchases above threshold. "
            "Pre-populates project and budget line information."
        ),
        "category": TemplateCategory.PROCUREMENT,
        "personnel_type": None,
        "field_definitions": {
            "fields": _PROCUREMENT_PROJECT_FIELDS
            + _rfq_manual_fields()
        },
        "conditional_sections": _PROCUREMENT_COST_MODEL_CONDITIONS,
    },
    "comparative-analysis": {
        "name": "Comparative Analysis Form",
        "slug": "comparative-analysis",
        "description": (
            "Supplier comparison form with auto-generated scoring "
            "framework for evaluating multiple quotes."
        ),
        "category": TemplateCategory.PROCUREMENT,
        "personnel_type": None,
        "field_definitions": {
            "fields": _PROCUREMENT_PROJECT_FIELDS
            + _comparative_analysis_manual_fields()
        },
        "conditional_sections": _PROCUREMENT_COST_MODEL_CONDITIONS,
    },
    "procurement-justification": {
        "name": "Procurement Justification",
        "slug": "procurement-justification",
        "description": (
            "Justification for single-source or above-threshold "
            "procurement with applicable EC and university rules."
        ),
        "category": TemplateCategory.PROCUREMENT,
        "personnel_type": None,
        "field_definitions": {
            "fields": _PROCUREMENT_PROJECT_FIELDS
            + _procurement_justification_manual_fields()
        },
        "conditional_sections": _PROCUREMENT_COST_MODEL_CONDITIONS,
    },
    "equipment-depreciation": {
        "name": "Equipment Depreciation Calculation",
        "slug": "equipment-depreciation",
        "description": (
            "Equipment depreciation calculation for multi-project usage. "
            "Auto-fills purchase cost, project duration, and calculates "
            "eligible project amount."
        ),
        "category": TemplateCategory.PROCUREMENT,
        "personnel_type": None,
        "field_definitions": {
            "fields": _PROCUREMENT_PROJECT_FIELDS
            + _equipment_depreciation_manual_fields()
        },
        "conditional_sections": _PROCUREMENT_COST_MODEL_CONDITIONS,
    },
    "budget-transfer-request": {
        "name": "Budget Transfer Request",
        "slug": "budget-transfer-request",
        "description": (
            "Internal budget reallocation request showing current "
            "breakdown, proposed change, and justification."
        ),
        "category": TemplateCategory.PROCUREMENT,
        "personnel_type": None,
        "field_definitions": {
            "fields": _PROCUREMENT_PROJECT_FIELDS
            + _budget_transfer_manual_fields()
        },
        "conditional_sections": None,
    },
    "recruitment-authorization": {
        "name": "Recruitment Authorization",
        "slug": "recruitment-authorization",
        "description": (
            "Authorization request for new hire on project funding. "
            "Auto-fills project details, position profile, and funding source."
        ),
        "category": TemplateCategory.PROCUREMENT,
        "personnel_type": None,
        "field_definitions": {
            "fields": _PROCUREMENT_PROJECT_FIELDS
            + _recruitment_authorization_manual_fields()
        },
        "conditional_sections": _PROCUREMENT_COST_MODEL_CONDITIONS,
    },
}
