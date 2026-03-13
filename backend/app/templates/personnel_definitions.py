"""Personnel contract template definitions (Section 7.2.1).

Each definition specifies the auto-populated fields, manual input fields,
conditional sections, and DOCX structure for personnel contract types.
"""

from app.models.enums import PersonnelTemplateType, TemplateCategory

# Common auto-populated fields shared across all personnel templates
_COMMON_PROJECT_FIELDS = [
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
        "name": "funding_source",
        "label": "Funding Source",
        "field_type": "auto",
        "data_type": "text",
        "data_source": "project.programme",
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

_COMMON_RESEARCHER_FIELDS = [
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
    {
        "name": "fte",
        "label": "FTE Allocation",
        "field_type": "auto",
        "data_type": "decimal",
        "data_source": "researcher.fte",
        "required": True,
    },
    {
        "name": "contract_start",
        "label": "Contract Start Date",
        "field_type": "auto",
        "data_type": "date",
        "data_source": "researcher.start_date",
        "required": False,
    },
    {
        "name": "contract_end",
        "label": "Contract End Date",
        "field_type": "auto",
        "data_type": "date",
        "data_source": "researcher.end_date",
        "required": False,
    },
    {
        "name": "annual_gross_cost",
        "label": "Annual Gross Cost (EUR)",
        "field_type": "auto",
        "data_type": "decimal",
        "data_source": "researcher.annual_gross_cost",
        "required": False,
    },
]

# Conditional sections shared across personnel templates
_TIMESHEET_CONDITION = {
    "timesheet_obligations": {
        "section_name": "Timesheet Obligations",
        "condition_field": "project.cost_model",
        "condition_value": "ACTUAL_COSTS",
        "condition_operator": "eq",
        "content_label": (
            "The researcher is required to maintain detailed timesheets "
            "recording hours worked on this project using the institutional "
            "timesheet system. Timesheets must be submitted monthly and "
            "approved by the Principal Investigator."
        ),
    },
    "lump_sum_effort_note": {
        "section_name": "Effort Documentation (Lump Sum)",
        "condition_field": "project.cost_model",
        "condition_value": "LUMP_SUM",
        "condition_operator": "eq",
        "content_label": (
            "As this project follows the lump sum cost model, detailed "
            "timesheet tracking is not required. However, the researcher "
            "should maintain records of activities performed for project "
            "reporting purposes."
        ),
    },
    "unit_cost_delivery_note": {
        "section_name": "Unit Delivery Requirements",
        "condition_field": "project.cost_model",
        "condition_value": "UNIT_COSTS",
        "condition_operator": "eq",
        "content_label": (
            "This project uses the unit cost model. The researcher is "
            "responsible for tracking and reporting deliverable units "
            "as defined in the grant agreement."
        ),
    },
}


def _bi_manual_fields() -> list[dict]:
    """Manual input fields for Bolsa de Investigacao."""
    return [
        {
            "name": "research_plan",
            "label": "Research Plan Description",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
            "help_text": "Describe the research activities to be performed.",
        },
        {
            "name": "supervisor_name",
            "label": "Supervisor Name",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "monthly_stipend",
            "label": "Monthly Stipend (EUR)",
            "field_type": "manual",
            "data_type": "decimal",
            "required": True,
            "help_text": "Per FCT stipend tables.",
        },
        {
            "name": "scholarship_duration_months",
            "label": "Scholarship Duration (months)",
            "field_type": "manual",
            "data_type": "integer",
            "required": True,
        },
        {
            "name": "work_location",
            "label": "Work Location",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
            "default_value": "Research Lab",
        },
    ]


def _bd_manual_fields() -> list[dict]:
    """Manual input fields for Bolsa de Doutoramento."""
    return [
        {
            "name": "phd_programme",
            "label": "PhD Programme",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "supervisor_name",
            "label": "Supervisor Name",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "co_supervisor_name",
            "label": "Co-Supervisor Name",
            "field_type": "manual",
            "data_type": "text",
            "required": False,
        },
        {
            "name": "research_plan",
            "label": "Research Plan Reference",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
            "help_text": "Reference to the approved PhD research plan.",
        },
        {
            "name": "monthly_stipend",
            "label": "Monthly Stipend (EUR)",
            "field_type": "manual",
            "data_type": "decimal",
            "required": True,
        },
        {
            "name": "scholarship_duration_months",
            "label": "Scholarship Duration (months)",
            "field_type": "manual",
            "data_type": "integer",
            "required": True,
            "default_value": "48",
        },
    ]


def _bpd_manual_fields() -> list[dict]:
    """Manual input fields for Bolsa de Pos-Doutoramento."""
    return [
        {
            "name": "research_group",
            "label": "Research Group/Unit",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "supervisor_name",
            "label": "Supervisor/Host Name",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "research_plan",
            "label": "Research Plan Description",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "monthly_stipend",
            "label": "Monthly Stipend (EUR)",
            "field_type": "manual",
            "data_type": "decimal",
            "required": True,
        },
        {
            "name": "evaluation_criteria",
            "label": "Evaluation Criteria",
            "field_type": "manual",
            "data_type": "text",
            "required": False,
            "help_text": "Criteria for periodic evaluation.",
        },
        {
            "name": "scholarship_duration_months",
            "label": "Scholarship Duration (months)",
            "field_type": "manual",
            "data_type": "integer",
            "required": True,
        },
    ]


def _dl57_manual_fields() -> list[dict]:
    """Manual input fields for DL57 scientific employment contract."""
    return [
        {
            "name": "research_area",
            "label": "Research Area (FCT Classification)",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "evaluation_committee",
            "label": "Evaluation Committee Members",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
            "help_text": "Names of the evaluation committee.",
        },
        {
            "name": "salary_index",
            "label": "Salary Index/Scale",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "contract_duration_years",
            "label": "Contract Duration (years)",
            "field_type": "manual",
            "data_type": "integer",
            "required": True,
            "default_value": "3",
        },
        {
            "name": "institution_department",
            "label": "Department/Research Unit",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
    ]


def _ceec_manual_fields() -> list[dict]:
    """Manual input fields for CEEC scientific employment stimulus."""
    return [
        {
            "name": "ceec_reference",
            "label": "CEEC Application Reference",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "research_area",
            "label": "Research Area",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "institutional_commitment",
            "label": "Institutional Commitment Description",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
            "help_text": "Describe institutional support and resources.",
        },
        {
            "name": "salary_index",
            "label": "Salary Index/Scale",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "contract_duration_years",
            "label": "Contract Duration (years)",
            "field_type": "manual",
            "data_type": "integer",
            "required": True,
            "default_value": "6",
        },
    ]


def _clt_manual_fields() -> list[dict]:
    """Manual input fields for CLT employment contract."""
    return [
        {
            "name": "job_title",
            "label": "Job Title",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "salary_grade",
            "label": "Salary Grade/Level",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "monthly_salary",
            "label": "Monthly Gross Salary (EUR)",
            "field_type": "manual",
            "data_type": "decimal",
            "required": True,
        },
        {
            "name": "work_schedule",
            "label": "Work Schedule",
            "field_type": "manual",
            "data_type": "text",
            "required": False,
            "default_value": "Full-time, 40 hours/week",
        },
        {
            "name": "probation_period_months",
            "label": "Probation Period (months)",
            "field_type": "manual",
            "data_type": "integer",
            "required": False,
            "default_value": "6",
        },
    ]


def _renewal_manual_fields() -> list[dict]:
    """Manual input fields for contract renewal/extension."""
    return [
        {
            "name": "original_contract_ref",
            "label": "Original Contract Reference",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
        },
        {
            "name": "original_start_date",
            "label": "Original Contract Start Date",
            "field_type": "manual",
            "data_type": "date",
            "required": True,
        },
        {
            "name": "original_end_date",
            "label": "Original Contract End Date",
            "field_type": "manual",
            "data_type": "date",
            "required": True,
        },
        {
            "name": "new_end_date",
            "label": "New End Date",
            "field_type": "manual",
            "data_type": "date",
            "required": True,
        },
        {
            "name": "renewal_justification",
            "label": "Justification for Renewal",
            "field_type": "manual",
            "data_type": "text",
            "required": True,
            "help_text": "Explain the reason for contract extension.",
        },
        {
            "name": "budget_impact",
            "label": "Budget Impact Description",
            "field_type": "manual",
            "data_type": "text",
            "required": False,
        },
    ]


# Template definition registry
PERSONNEL_TEMPLATE_DEFINITIONS: dict[PersonnelTemplateType, dict] = {
    PersonnelTemplateType.BOLSA_BI: {
        "name": "Bolsa de Investigacao (BI)",
        "slug": "bolsa-bi",
        "description": (
            "Research scholarship contract for Bolsa de Investigacao. "
            "Auto-fills project and researcher data, adapts timesheet "
            "clauses based on cost model."
        ),
        "category": TemplateCategory.PERSONNEL,
        "personnel_type": PersonnelTemplateType.BOLSA_BI,
        "field_definitions": {
            "fields": (
                _COMMON_PROJECT_FIELDS
                + _COMMON_RESEARCHER_FIELDS
                + _bi_manual_fields()
            )
        },
        "conditional_sections": _TIMESHEET_CONDITION,
    },
    PersonnelTemplateType.BOLSA_BD: {
        "name": "Bolsa de Doutoramento (BD)",
        "slug": "bolsa-bd",
        "description": (
            "PhD scholarship contract for Bolsa de Doutoramento."
        ),
        "category": TemplateCategory.PERSONNEL,
        "personnel_type": PersonnelTemplateType.BOLSA_BD,
        "field_definitions": {
            "fields": (
                _COMMON_PROJECT_FIELDS
                + _COMMON_RESEARCHER_FIELDS
                + _bd_manual_fields()
            )
        },
        "conditional_sections": _TIMESHEET_CONDITION,
    },
    PersonnelTemplateType.BOLSA_BPD: {
        "name": "Bolsa de Pos-Doutoramento (BPD)",
        "slug": "bolsa-bpd",
        "description": (
            "Postdoctoral scholarship contract for Bolsa de "
            "Pos-Doutoramento."
        ),
        "category": TemplateCategory.PERSONNEL,
        "personnel_type": PersonnelTemplateType.BOLSA_BPD,
        "field_definitions": {
            "fields": (
                _COMMON_PROJECT_FIELDS
                + _COMMON_RESEARCHER_FIELDS
                + _bpd_manual_fields()
            )
        },
        "conditional_sections": _TIMESHEET_CONDITION,
    },
    PersonnelTemplateType.DL57: {
        "name": "DL57 Scientific Employment Contract",
        "slug": "dl57-contract",
        "description": (
            "Scientific employment contract under Decreto-Lei 57/2016."
        ),
        "category": TemplateCategory.PERSONNEL,
        "personnel_type": PersonnelTemplateType.DL57,
        "field_definitions": {
            "fields": (
                _COMMON_PROJECT_FIELDS
                + _COMMON_RESEARCHER_FIELDS
                + _dl57_manual_fields()
            )
        },
        "conditional_sections": _TIMESHEET_CONDITION,
    },
    PersonnelTemplateType.CEEC: {
        "name": "CEEC Scientific Employment Stimulus Contract",
        "slug": "ceec-contract",
        "description": (
            "Contract under the Scientific Employment Stimulus (CEEC) "
            "programme."
        ),
        "category": TemplateCategory.PERSONNEL,
        "personnel_type": PersonnelTemplateType.CEEC,
        "field_definitions": {
            "fields": (
                _COMMON_PROJECT_FIELDS
                + _COMMON_RESEARCHER_FIELDS
                + _ceec_manual_fields()
            )
        },
        "conditional_sections": _TIMESHEET_CONDITION,
    },
    PersonnelTemplateType.CLT: {
        "name": "CLT Employment Contract",
        "slug": "clt-employment",
        "description": (
            "Standard employment contract (CLT) funded by project."
        ),
        "category": TemplateCategory.PERSONNEL,
        "personnel_type": PersonnelTemplateType.CLT,
        "field_definitions": {
            "fields": (
                _COMMON_PROJECT_FIELDS
                + _COMMON_RESEARCHER_FIELDS
                + _clt_manual_fields()
            )
        },
        "conditional_sections": _TIMESHEET_CONDITION,
    },
    PersonnelTemplateType.CONTRACT_RENEWAL: {
        "name": "Contract Renewal / Extension",
        "slug": "contract-renewal",
        "description": (
            "Contract renewal or extension for any contract type. "
            "Auto-fills current contract details and project data."
        ),
        "category": TemplateCategory.PERSONNEL,
        "personnel_type": PersonnelTemplateType.CONTRACT_RENEWAL,
        "field_definitions": {
            "fields": (
                _COMMON_PROJECT_FIELDS
                + _COMMON_RESEARCHER_FIELDS
                + _renewal_manual_fields()
            )
        },
        "conditional_sections": _TIMESHEET_CONDITION,
    },
}
