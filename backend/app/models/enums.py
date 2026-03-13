"""Domain enums used across the application."""

import enum


class Programme(str, enum.Enum):
    """EU funding programme."""

    HORIZON_EUROPE = "HORIZON_EUROPE"
    DIGITAL_EUROPE = "DIGITAL_EUROPE"
    ERASMUS_PLUS = "ERASMUS_PLUS"
    CEF = "CEF"
    FCT = "FCT"


class CostModel(str, enum.Enum):
    """Project cost model determining financial tracking behavior."""

    ACTUAL_COSTS = "ACTUAL_COSTS"
    LUMP_SUM = "LUMP_SUM"
    UNIT_COSTS = "UNIT_COSTS"
    MIXED = "MIXED"


class ProjectRole(str, enum.Enum):
    """Institution's role in the project."""

    COORDINATOR = "COORDINATOR"
    PARTNER = "PARTNER"
    ASSOCIATED_PARTNER = "ASSOCIATED_PARTNER"


class ProjectStatus(str, enum.Enum):
    """Project lifecycle status."""

    PROPOSAL = "PROPOSAL"
    NEGOTIATION = "NEGOTIATION"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    CLOSED = "CLOSED"


class OrgType(str, enum.Enum):
    """Organization type per EC classification."""

    HES = "HES"
    REC = "REC"
    PRC = "PRC"
    PUB = "PUB"
    OTH = "OTH"


class WPStatus(str, enum.Enum):
    """Work package status."""

    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    DELAYED = "DELAYED"


class DeliverableType(str, enum.Enum):
    """Type of deliverable."""

    REPORT = "REPORT"
    DEMONSTRATOR = "DEMONSTRATOR"
    DATA = "DATA"
    SOFTWARE = "SOFTWARE"
    OTHER = "OTHER"


class DisseminationLevel(str, enum.Enum):
    """Deliverable dissemination level."""

    PU = "PU"
    SEN = "SEN"
    CO = "CO"


class ECReviewStatus(str, enum.Enum):
    """EC review status for deliverables."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REVISION_REQUESTED = "REVISION_REQUESTED"
    REJECTED = "REJECTED"


class TrafficLight(str, enum.Enum):
    """Traffic light status indicator."""

    GREEN = "GREEN"
    AMBER = "AMBER"
    RED = "RED"


class ECBudgetCategory(str, enum.Enum):
    """EC budget categories (Horizon Europe standard A-E)."""

    A_PERSONNEL = "A_PERSONNEL"
    B_SUBCONTRACTING = "B_SUBCONTRACTING"
    C1_TRAVEL = "C1_TRAVEL"
    C2_EQUIPMENT = "C2_EQUIPMENT"
    C3_OTHER_GOODS = "C3_OTHER_GOODS"
    D_OTHER_COSTS = "D_OTHER_COSTS"
    E_INDIRECT = "E_INDIRECT"


class ExpenseStatus(str, enum.Enum):
    """Expense lifecycle status."""

    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REPORTED = "REPORTED"
    AUDITED = "AUDITED"


class MissionPurpose(str, enum.Enum):
    """Purpose of a mission/travel."""

    CONSORTIUM_MEETING = "CONSORTIUM_MEETING"
    CONFERENCE = "CONFERENCE"
    SECONDMENT = "SECONDMENT"
    FIELDWORK = "FIELDWORK"
    TRAINING = "TRAINING"
    OTHER = "OTHER"


class ApprovalStatus(str, enum.Enum):
    """Approval workflow status for missions and procurements."""

    REQUESTED = "REQUESTED"
    PI_APPROVED = "PI_APPROVED"
    CENTRALLY_APPROVED = "CENTRALLY_APPROVED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class ProcurementMethod(str, enum.Enum):
    """Procurement method."""

    DIRECT_PURCHASE = "DIRECT_PURCHASE"
    THREE_QUOTES = "THREE_QUOTES"
    PUBLIC_TENDER = "PUBLIC_TENDER"
    FRAMEWORK_AGREEMENT = "FRAMEWORK_AGREEMENT"


class UniversityThreshold(str, enum.Enum):
    """University procurement threshold classification."""

    BELOW_THRESHOLD = "BELOW_THRESHOLD"
    SIMPLIFIED = "SIMPLIFIED"
    FULL_PROCEDURE = "FULL_PROCEDURE"


class ProcurementApprovalStatus(str, enum.Enum):
    """Procurement approval workflow status."""

    REQUESTED = "REQUESTED"
    PI_APPROVED = "PI_APPROVED"
    PROCUREMENT_APPROVED = "PROCUREMENT_APPROVED"
    COMPLETED = "COMPLETED"


class ResearcherPosition(str, enum.Enum):
    """Researcher position/role within the institution."""

    PI = "PI"
    CO_PI = "CO_PI"
    POSTDOC = "POSTDOC"
    PHD_STUDENT = "PHD_STUDENT"
    RESEARCH_ENGINEER = "RESEARCH_ENGINEER"
    TECHNICIAN = "TECHNICIAN"
    ADMIN = "ADMIN"


class ContractType(str, enum.Enum):
    """Employment contract type (Portuguese/EU context)."""

    DL57 = "DL57"
    CEEC = "CEEC"
    BOLSA_BI = "BOLSA_BI"
    BOLSA_BD = "BOLSA_BD"
    BOLSA_BPD = "BOLSA_BPD"
    CLT = "CLT"
    OTHER = "OTHER"


class UserRole(str, enum.Enum):
    """User role for role-based access control."""

    PI = "PI"
    RESEARCHER = "RESEARCHER"
    CENTRAL_FINANCE_PM = "CENTRAL_FINANCE_PM"
    EXTERNAL_PARTNER = "EXTERNAL_PARTNER"


class ReportingPeriodType(str, enum.Enum):
    """Type of reporting period."""

    PERIODIC = "PERIODIC"
    FINAL = "FINAL"


class ReportStatus(str, enum.Enum):
    """Technical report workflow status."""

    DRAFT = "DRAFT"
    WP_INPUT = "WP_INPUT"
    PARTNER_REVIEW = "PARTNER_REVIEW"
    CONSOLIDATION = "CONSOLIDATION"
    INTERNAL_REVIEW = "INTERNAL_REVIEW"
    FINAL_REVIEW = "FINAL_REVIEW"
    SUBMITTED = "SUBMITTED"
    EC_APPROVED = "EC_APPROVED"


class ReportSectionType(str, enum.Enum):
    """Section type within a technical report."""

    PART_A_SUMMARY = "PART_A_SUMMARY"
    PART_B1_WP_NARRATIVE = "PART_B1_WP_NARRATIVE"
    PART_B2_DELIVERABLES = "PART_B2_DELIVERABLES"
    PART_B3_RISKS = "PART_B3_RISKS"
    PART_B4_RESOURCES = "PART_B4_RESOURCES"


class ReportSectionStatus(str, enum.Enum):
    """Status of a report section draft."""

    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"


class RiskCategory(str, enum.Enum):
    """Risk category classification."""

    TECHNICAL = "TECHNICAL"
    FINANCIAL = "FINANCIAL"
    ORGANIZATIONAL = "ORGANIZATIONAL"
    EXTERNAL = "EXTERNAL"


class RiskLevel(str, enum.Enum):
    """Probability or impact level for a risk."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class RiskStatus(str, enum.Enum):
    """Current status of a risk."""

    OPEN = "OPEN"
    MITIGATED = "MITIGATED"
    CLOSED = "CLOSED"


class ReminderType(str, enum.Enum):
    """Automated reporting reminder milestones."""

    T_90 = "T_90"
    T_60 = "T_60"
    T_45 = "T_45"
    T_30 = "T_30"
    T_20 = "T_20"
    T_15 = "T_15"
    T_7 = "T_7"


class FinancialStatementStatus(str, enum.Enum):
    """Workflow status for Form C financial statements."""

    DRAFT = "DRAFT"
    PARTNER_SUBMITTED = "PARTNER_SUBMITTED"
    COORDINATOR_REVIEW = "COORDINATOR_REVIEW"
    COORDINATOR_APPROVED = "COORDINATOR_APPROVED"
    REPORTED_TO_EC = "REPORTED_TO_EC"
    EC_APPROVED = "EC_APPROVED"


class CFSStatus(str, enum.Enum):
    """Certificate on Financial Statements status (required when cumulative > EUR 430k)."""

    NOT_REQUIRED = "NOT_REQUIRED"
    PENDING = "PENDING"
    OBTAINED = "OBTAINED"
    SUBMITTED = "SUBMITTED"


class UnitType(str, enum.Enum):
    """Types of deliverable units for unit-cost projects."""

    PERSON_DAY = "PERSON_DAY"
    PERSON_MONTH = "PERSON_MONTH"
    TRAINING_HOUR = "TRAINING_HOUR"
    PUBLICATION = "PUBLICATION"
    DATASET = "DATASET"
    PROTOTYPE = "PROTOTYPE"
    EVENT = "EVENT"
    LICENCE = "LICENCE"
    OTHER = "OTHER"


class UnitCostStatus(str, enum.Enum):
    """Status of a unit delivery record."""

    PLANNED = "PLANNED"
    REPORTED = "REPORTED"
    APPROVED = "APPROVED"


class CompletionStatus(str, enum.Enum):
    """WP completion status for lump-sum projects."""

    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    PARTIALLY_COMPLETED = "PARTIALLY_COMPLETED"


class TemplateCategory(str, enum.Enum):
    """Category of document template."""

    PERSONNEL = "PERSONNEL"
    EC_CONSORTIUM = "EC_CONSORTIUM"
    REPORTING = "REPORTING"
    MISSION_TRAVEL = "MISSION_TRAVEL"
    PROCUREMENT = "PROCUREMENT"


class PersonnelTemplateType(str, enum.Enum):
    """Personnel contract template types."""

    BOLSA_BI = "BOLSA_BI"
    BOLSA_BD = "BOLSA_BD"
    BOLSA_BPD = "BOLSA_BPD"
    DL57 = "DL57"
    CEEC = "CEEC"
    CLT = "CLT"
    CONTRACT_RENEWAL = "CONTRACT_RENEWAL"


class GeneratedDocumentStatus(str, enum.Enum):
    """Status of a generated document."""

    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    SIGNED = "SIGNED"
    ARCHIVED = "ARCHIVED"


# --- Section 9: Additional Features ---


class IPType(str, enum.Enum):
    """Type of intellectual property asset."""

    BACKGROUND = "BACKGROUND"
    FOREGROUND = "FOREGROUND"


class IPStatus(str, enum.Enum):
    """Status of an IP asset."""

    IDENTIFIED = "IDENTIFIED"
    DISCLOSED = "DISCLOSED"
    PATENT_FILED = "PATENT_FILED"
    PATENT_GRANTED = "PATENT_GRANTED"
    LICENSED = "LICENSED"
    EXPLOITED = "EXPLOITED"


class DisseminationActivityType(str, enum.Enum):
    """Type of communication/dissemination activity."""

    PUBLICATION = "PUBLICATION"
    CONFERENCE = "CONFERENCE"
    PRESS_RELEASE = "PRESS_RELEASE"
    SOCIAL_MEDIA = "SOCIAL_MEDIA"
    WORKSHOP = "WORKSHOP"
    POLICY_BRIEF = "POLICY_BRIEF"
    OTHER = "OTHER"


class OpenAccessStatus(str, enum.Enum):
    """Open access compliance status."""

    NOT_APPLICABLE = "NOT_APPLICABLE"
    GREEN = "GREEN"
    GOLD = "GOLD"
    DIAMOND = "DIAMOND"
    EMBARGO = "EMBARGO"
    NON_COMPLIANT = "NON_COMPLIANT"


class KPIDataType(str, enum.Enum):
    """Data type for a KPI indicator value."""

    INTEGER = "INTEGER"
    DECIMAL = "DECIMAL"
    PERCENTAGE = "PERCENTAGE"
    BOOLEAN = "BOOLEAN"
    TEXT = "TEXT"


class EthicsStatus(str, enum.Enum):
    """Status of an ethics requirement."""

    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class DMPStatus(str, enum.Enum):
    """Data Management Plan compliance status."""

    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    COMPLIANT = "COMPLIANT"
    NON_COMPLIANT = "NON_COMPLIANT"


class AmendmentStatus(str, enum.Enum):
    """Grant agreement amendment status."""

    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"


class AmendmentType(str, enum.Enum):
    """Type of grant agreement amendment."""

    BUDGET_TRANSFER = "BUDGET_TRANSFER"
    TIMELINE_CHANGE = "TIMELINE_CHANGE"
    PARTNER_CHANGE = "PARTNER_CHANGE"
    SCOPE_CHANGE = "SCOPE_CHANGE"
    OTHER = "OTHER"


class NotificationType(str, enum.Enum):
    """Type of system notification."""

    REPORTING_DEADLINE = "REPORTING_DEADLINE"
    TIMESHEET_REMINDER = "TIMESHEET_REMINDER"
    DELIVERABLE_DUE = "DELIVERABLE_DUE"
    BUDGET_THRESHOLD = "BUDGET_THRESHOLD"
    CONTRACT_EXPIRY = "CONTRACT_EXPIRY"
    AMENDMENT_STATUS = "AMENDMENT_STATUS"
    EC_FEEDBACK = "EC_FEEDBACK"
    PARTNER_PAYMENT = "PARTNER_PAYMENT"
    RISK_ESCALATION = "RISK_ESCALATION"


class NotificationPriority(str, enum.Enum):
    """Notification priority level."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class NotificationStatus(str, enum.Enum):
    """Notification delivery status."""

    PENDING = "PENDING"
    SENT = "SENT"
    READ = "READ"
    DISMISSED = "DISMISSED"
