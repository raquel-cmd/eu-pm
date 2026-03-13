export enum Programme {
  HORIZON_EUROPE = 'HORIZON_EUROPE',
  DIGITAL_EUROPE = 'DIGITAL_EUROPE',
  ERASMUS_PLUS = 'ERASMUS_PLUS',
  CEF = 'CEF',
  FCT = 'FCT',
}

export enum CostModel {
  ACTUAL_COSTS = 'ACTUAL_COSTS',
  LUMP_SUM = 'LUMP_SUM',
  UNIT_COSTS = 'UNIT_COSTS',
  MIXED = 'MIXED',
}

export enum ProjectRole {
  COORDINATOR = 'COORDINATOR',
  PARTNER = 'PARTNER',
  ASSOCIATED_PARTNER = 'ASSOCIATED_PARTNER',
}

export enum ProjectStatus {
  PROPOSAL = 'PROPOSAL',
  NEGOTIATION = 'NEGOTIATION',
  ACTIVE = 'ACTIVE',
  SUSPENDED = 'SUSPENDED',
  CLOSED = 'CLOSED',
}

export enum OrgType {
  HES = 'HES',
  REC = 'REC',
  PRC = 'PRC',
  PUB = 'PUB',
  OTH = 'OTH',
}

export enum WPStatus {
  NOT_STARTED = 'NOT_STARTED',
  IN_PROGRESS = 'IN_PROGRESS',
  COMPLETED = 'COMPLETED',
  DELAYED = 'DELAYED',
}

export enum DeliverableType {
  REPORT = 'REPORT',
  DEMONSTRATOR = 'DEMONSTRATOR',
  DATA = 'DATA',
  SOFTWARE = 'SOFTWARE',
  OTHER = 'OTHER',
}

export enum DisseminationLevel {
  PU = 'PU',
  SEN = 'SEN',
  CO = 'CO',
}

export enum ECReviewStatus {
  PENDING = 'PENDING',
  APPROVED = 'APPROVED',
  REVISION_REQUESTED = 'REVISION_REQUESTED',
  REJECTED = 'REJECTED',
}

export enum TrafficLight {
  GREEN = 'GREEN',
  AMBER = 'AMBER',
  RED = 'RED',
}

// --- Project ---

export interface Project {
  id: string;
  acronym: string;
  full_title: string;
  grant_agreement_number: string | null;
  programme: Programme;
  call_identifier: string | null;
  cost_model: CostModel;
  role: ProjectRole;
  start_date: string | null;
  end_date: string | null;
  duration_months: number | null;
  total_budget: string | null;
  eu_contribution: string | null;
  funding_rate: string | null;
  reporting_periods: unknown;
  status: ProjectStatus;
  ec_project_officer: string | null;
  internal_cost_center: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProjectCreate {
  acronym: string;
  full_title: string;
  grant_agreement_number?: string | null;
  programme: Programme;
  call_identifier?: string | null;
  cost_model: CostModel;
  role: ProjectRole;
  start_date?: string | null;
  end_date?: string | null;
  duration_months?: number | null;
  total_budget?: string | null;
  eu_contribution?: string | null;
  funding_rate?: string | null;
  reporting_periods?: unknown;
  status?: ProjectStatus;
  ec_project_officer?: string | null;
  internal_cost_center?: string | null;
}

export type ProjectUpdate = Partial<ProjectCreate>;

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
}

// --- Partner ---

export interface Partner {
  id: string;
  pic_number: string | null;
  legal_name: string;
  short_name: string;
  country: string | null;
  org_type: OrgType | null;
  is_sme: boolean;
  contact_person: string | null;
  bank_account_validated: boolean;
  accession_form_signed: boolean;
  created_at: string;
  updated_at: string;
}

export interface PartnerCreate {
  pic_number?: string | null;
  legal_name: string;
  short_name: string;
  country?: string | null;
  org_type?: OrgType | null;
  is_sme?: boolean;
  contact_person?: string | null;
  bank_account_validated?: boolean;
  accession_form_signed?: boolean;
}

export type PartnerUpdate = Partial<PartnerCreate>;

export interface ProjectPartner {
  id: string;
  project_id: string;
  partner_id: string;
  partner_budget: string | null;
  partner_eu_contribution: string | null;
  partner: Partner;
  created_at: string;
  updated_at: string;
}

export interface ProjectPartnerCreate {
  partner_id: string;
  partner_budget?: string | null;
  partner_eu_contribution?: string | null;
}

export interface ProjectPartnerUpdate {
  partner_budget?: string | null;
  partner_eu_contribution?: string | null;
}

// --- Work Package ---

export interface WorkPackage {
  id: string;
  project_id: string;
  wp_number: number;
  title: string;
  lead_partner_id: string | null;
  start_month: number | null;
  end_month: number | null;
  total_pm: string | null;
  objectives: string | null;
  status: WPStatus;
  created_at: string;
  updated_at: string;
}

export interface WorkPackageCreate {
  wp_number: number;
  title: string;
  lead_partner_id?: string | null;
  start_month?: number | null;
  end_month?: number | null;
  total_pm?: string | null;
  objectives?: string | null;
  status?: WPStatus;
}

export type WorkPackageUpdate = Partial<WorkPackageCreate>;

// --- Deliverable ---

export interface Deliverable {
  id: string;
  work_package_id: string;
  deliverable_number: string;
  title: string;
  type: DeliverableType;
  dissemination_level: DisseminationLevel;
  lead_partner_id: string | null;
  due_month: number | null;
  submission_date: string | null;
  ec_review_status: ECReviewStatus;
  traffic_light: TrafficLight;
  file_reference: string | null;
  created_at: string;
  updated_at: string;
}

export interface DeliverableCreate {
  deliverable_number: string;
  title: string;
  type: DeliverableType;
  dissemination_level: DisseminationLevel;
  lead_partner_id?: string | null;
  due_month?: number | null;
  submission_date?: string | null;
  ec_review_status?: ECReviewStatus;
  traffic_light?: TrafficLight;
  file_reference?: string | null;
}

export type DeliverableUpdate = Partial<DeliverableCreate>;

// --- Milestone ---

export interface Milestone {
  id: string;
  work_package_id: string;
  milestone_number: string;
  title: string;
  due_month: number | null;
  verification_means: string | null;
  achieved: boolean;
  achievement_date: string | null;
  created_at: string;
  updated_at: string;
}

export interface MilestoneCreate {
  milestone_number: string;
  title: string;
  due_month?: number | null;
  verification_means?: string | null;
  achieved?: boolean;
  achievement_date?: string | null;
}

export type MilestoneUpdate = Partial<MilestoneCreate>;

// --- Mission ---

export enum ApprovalStatus {
  REQUESTED = 'REQUESTED',
  PI_APPROVED = 'PI_APPROVED',
  CENTRALLY_APPROVED = 'CENTRALLY_APPROVED',
  COMPLETED = 'COMPLETED',
  CANCELLED = 'CANCELLED',
}

export enum MissionPurpose {
  CONFERENCE = 'CONFERENCE',
  CONSORTIUM_MEETING = 'CONSORTIUM_MEETING',
  FIELDWORK = 'FIELDWORK',
  TRAINING = 'TRAINING',
  DISSEMINATION = 'DISSEMINATION',
  OTHER = 'OTHER',
}

export interface Mission {
  id: string;
  project_id: string;
  work_package_id: string | null;
  researcher_name: string;
  purpose: MissionPurpose;
  destination: string;
  start_date: string;
  end_date: string;
  approval_status: ApprovalStatus;
  travel_costs: string | null;
  accommodation_costs: string | null;
  subsistence: string | null;
  registration_fees: string | null;
  other_costs: string | null;
  total_cost: string | null;
  currency: string;
  ec_eligible: boolean;
  supporting_docs: unknown;
  university_travel_order: string | null;
  estimated_total_cost: string | null;
  actual_total_cost: string | null;
  is_international: boolean;
  requires_central_approval: boolean;
  approved_by_pi_at: string | null;
  approved_centrally_at: string | null;
  completed_at: string | null;
  reconciliation_notes: string | null;
  actual_receipts: unknown;
  created_at: string;
  updated_at: string;
}

export interface MissionCreate {
  researcher_name: string;
  purpose: MissionPurpose;
  destination: string;
  start_date: string;
  end_date: string;
  work_package_id?: string | null;
  travel_costs?: string | null;
  accommodation_costs?: string | null;
  subsistence?: string | null;
  registration_fees?: string | null;
  other_costs?: string | null;
  total_cost?: string | null;
  is_international?: boolean;
}

export interface MissionComplete {
  actual_total_cost: string;
  actual_travel_costs?: string | null;
  actual_accommodation_costs?: string | null;
  actual_subsistence?: string | null;
  actual_registration_fees?: string | null;
  actual_other_costs?: string | null;
  actual_receipts?: unknown;
  university_travel_order?: string | null;
}

// --- Researcher ---

export enum ResearcherPosition {
  PI = 'PI',
  CO_PI = 'CO_PI',
  POSTDOC = 'POSTDOC',
  PHD_STUDENT = 'PHD_STUDENT',
  RESEARCH_ENGINEER = 'RESEARCH_ENGINEER',
  TECHNICIAN = 'TECHNICIAN',
  ADMIN = 'ADMIN',
}

export enum ContractType {
  DL57 = 'DL57',
  CEEC = 'CEEC',
  BOLSA_BI = 'BOLSA_BI',
  BOLSA_BD = 'BOLSA_BD',
  BOLSA_BPD = 'BOLSA_BPD',
  CLT = 'CLT',
  OTHER = 'OTHER',
}

export interface Researcher {
  id: string;
  name: string;
  email: string | null;
  position: ResearcherPosition;
  contract_type: ContractType;
  fte: string;
  annual_gross_cost: string | null;
  productive_hours: number;
  hourly_rate: string | null;
  start_date: string | null;
  end_date: string | null;
  created_at: string;
  updated_at: string;
}

export interface ResearcherCreate {
  name: string;
  email?: string | null;
  position: ResearcherPosition;
  contract_type: ContractType;
  fte?: string;
  annual_gross_cost?: string | null;
  productive_hours?: number;
  start_date?: string | null;
  end_date?: string | null;
}

// --- Effort Allocation ---

export interface EffortAllocation {
  id: string;
  researcher_id: string;
  project_id: string;
  work_package_id: string | null;
  period_start: string;
  period_end: string;
  planned_pm: string;
  planned_fte_percentage: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface EffortAllocationCreate {
  researcher_id: string;
  work_package_id?: string | null;
  period_start: string;
  period_end: string;
  planned_pm: string;
  planned_fte_percentage?: string | null;
  notes?: string | null;
}

// --- Timesheet Entry ---

export interface TimesheetEntry {
  id: string;
  researcher_id: string;
  project_id: string;
  work_package_id: string | null;
  date: string;
  hours: string;
  description: string | null;
  submitted_at: string | null;
  approved_at: string | null;
  person_months: string | null;
  created_at: string;
  updated_at: string;
}

export interface TimesheetEntryCreate {
  researcher_id: string;
  work_package_id?: string | null;
  date: string;
  hours: string;
  description?: string | null;
}

// --- Cross-Project Views ---

export interface ProjectAllocationDetail {
  project_id: string;
  acronym: string;
  committed_pm: string;
  actual_pm: string;
  available_capacity: string;
}

export interface ResearcherAllocation {
  researcher_id: string;
  researcher_name: string;
  fte: string;
  allocations: ProjectAllocationDetail[];
}

export interface WPEffortRow {
  wp_number: number | null;
  wp_title: string | null;
  planned_pm: string;
  actual_pm: string;
  variance: string;
}

export interface ProjectEffortSummary {
  project_id: string;
  rows: WPEffortRow[];
  total_planned_pm: string;
  total_actual_pm: string;
}

export interface ComplianceIssue {
  researcher_name: string;
  issue_type: string;
  details: string;
  period: string;
}

export interface ComplianceReport {
  issues: ComplianceIssue[];
  total_issues: number;
}

// --- Display helpers ---

export const PROGRAMME_LABELS: Record<Programme, string> = {
  [Programme.HORIZON_EUROPE]: 'Horizon Europe',
  [Programme.DIGITAL_EUROPE]: 'Digital Europe',
  [Programme.ERASMUS_PLUS]: 'Erasmus+',
  [Programme.CEF]: 'CEF',
  [Programme.FCT]: 'FCT',
};

export const COST_MODEL_LABELS: Record<CostModel, string> = {
  [CostModel.ACTUAL_COSTS]: 'Actual Costs',
  [CostModel.LUMP_SUM]: 'Lump Sum',
  [CostModel.UNIT_COSTS]: 'Unit Costs',
  [CostModel.MIXED]: 'Mixed',
};

export const ROLE_LABELS: Record<ProjectRole, string> = {
  [ProjectRole.COORDINATOR]: 'Coordinator',
  [ProjectRole.PARTNER]: 'Partner',
  [ProjectRole.ASSOCIATED_PARTNER]: 'Associated Partner',
};

export const STATUS_LABELS: Record<ProjectStatus, string> = {
  [ProjectStatus.PROPOSAL]: 'Proposal',
  [ProjectStatus.NEGOTIATION]: 'Negotiation',
  [ProjectStatus.ACTIVE]: 'Active',
  [ProjectStatus.SUSPENDED]: 'Suspended',
  [ProjectStatus.CLOSED]: 'Closed',
};

export const ORG_TYPE_LABELS: Record<OrgType, string> = {
  [OrgType.HES]: 'Higher Education',
  [OrgType.REC]: 'Research Organization',
  [OrgType.PRC]: 'Private Company',
  [OrgType.PUB]: 'Public Body',
  [OrgType.OTH]: 'Other',
};

export const WP_STATUS_LABELS: Record<WPStatus, string> = {
  [WPStatus.NOT_STARTED]: 'Not Started',
  [WPStatus.IN_PROGRESS]: 'In Progress',
  [WPStatus.COMPLETED]: 'Completed',
  [WPStatus.DELAYED]: 'Delayed',
};

export const DELIVERABLE_TYPE_LABELS: Record<DeliverableType, string> = {
  [DeliverableType.REPORT]: 'Report',
  [DeliverableType.DEMONSTRATOR]: 'Demonstrator',
  [DeliverableType.DATA]: 'Data',
  [DeliverableType.SOFTWARE]: 'Software',
  [DeliverableType.OTHER]: 'Other',
};

export const DISSEMINATION_LABELS: Record<DisseminationLevel, string> = {
  [DisseminationLevel.PU]: 'Public',
  [DisseminationLevel.SEN]: 'Sensitive',
  [DisseminationLevel.CO]: 'Confidential',
};

export const EC_REVIEW_LABELS: Record<ECReviewStatus, string> = {
  [ECReviewStatus.PENDING]: 'Pending',
  [ECReviewStatus.APPROVED]: 'Approved',
  [ECReviewStatus.REVISION_REQUESTED]: 'Revision Requested',
  [ECReviewStatus.REJECTED]: 'Rejected',
};

export const TRAFFIC_LIGHT_LABELS: Record<TrafficLight, string> = {
  [TrafficLight.GREEN]: 'Green',
  [TrafficLight.AMBER]: 'Amber',
  [TrafficLight.RED]: 'Red',
};

export const APPROVAL_STATUS_LABELS: Record<ApprovalStatus, string> = {
  [ApprovalStatus.REQUESTED]: 'Requested',
  [ApprovalStatus.PI_APPROVED]: 'PI Approved',
  [ApprovalStatus.CENTRALLY_APPROVED]: 'Centrally Approved',
  [ApprovalStatus.COMPLETED]: 'Completed',
  [ApprovalStatus.CANCELLED]: 'Cancelled',
};

export const MISSION_PURPOSE_LABELS: Record<MissionPurpose, string> = {
  [MissionPurpose.CONFERENCE]: 'Conference',
  [MissionPurpose.CONSORTIUM_MEETING]: 'Consortium Meeting',
  [MissionPurpose.FIELDWORK]: 'Fieldwork',
  [MissionPurpose.TRAINING]: 'Training',
  [MissionPurpose.DISSEMINATION]: 'Dissemination',
  [MissionPurpose.OTHER]: 'Other',
};

export const RESEARCHER_POSITION_LABELS: Record<ResearcherPosition, string> = {
  [ResearcherPosition.PI]: 'PI',
  [ResearcherPosition.CO_PI]: 'Co-PI',
  [ResearcherPosition.POSTDOC]: 'Postdoc',
  [ResearcherPosition.PHD_STUDENT]: 'PhD Student',
  [ResearcherPosition.RESEARCH_ENGINEER]: 'Research Engineer',
  [ResearcherPosition.TECHNICIAN]: 'Technician',
  [ResearcherPosition.ADMIN]: 'Admin',
};

export const CONTRACT_TYPE_LABELS: Record<ContractType, string> = {
  [ContractType.DL57]: 'DL 57',
  [ContractType.CEEC]: 'CEEC',
  [ContractType.BOLSA_BI]: 'Bolsa BI',
  [ContractType.BOLSA_BD]: 'Bolsa BD',
  [ContractType.BOLSA_BPD]: 'Bolsa BPD',
  [ContractType.CLT]: 'CLT',
  [ContractType.OTHER]: 'Other',
};

// --- Finance Dashboard (Section 6) ---

export enum ECBudgetCategory {
  A_PERSONNEL = 'A_PERSONNEL',
  B_SUBCONTRACTING = 'B_SUBCONTRACTING',
  C1_TRAVEL = 'C1_TRAVEL',
  C2_EQUIPMENT = 'C2_EQUIPMENT',
  C3_OTHER_GOODS = 'C3_OTHER_GOODS',
  D_OTHER_COSTS = 'D_OTHER_COSTS',
  E_INDIRECT = 'E_INDIRECT',
}

export const EC_BUDGET_CATEGORY_LABELS: Record<ECBudgetCategory, string> = {
  [ECBudgetCategory.A_PERSONNEL]: 'A. Personnel',
  [ECBudgetCategory.B_SUBCONTRACTING]: 'B. Subcontracting',
  [ECBudgetCategory.C1_TRAVEL]: 'C.1 Travel',
  [ECBudgetCategory.C2_EQUIPMENT]: 'C.2 Equipment',
  [ECBudgetCategory.C3_OTHER_GOODS]: 'C.3 Other Goods',
  [ECBudgetCategory.D_OTHER_COSTS]: 'D. Other Costs',
  [ECBudgetCategory.E_INDIRECT]: 'E. Indirect Costs',
};

export interface ProjectFinancialRow {
  project_id: string;
  acronym: string;
  programme: Programme;
  status: ProjectStatus;
  cost_model: CostModel;
  start_date: string | null;
  end_date: string | null;
  total_budget: string;
  eu_contribution: string;
  total_spent: string;
  burn_rate_percentage: string;
  burn_rate_status: string;
  pm_compliance_rate: string;
  flags: string[];
}

export interface UpcomingECPayment {
  project_id: string;
  acronym: string;
  payment_type: string;
  expected_amount: string;
  expected_date: string;
}

export interface RecruitmentPlanItem {
  project_id: string;
  acronym: string;
  researcher_name: string;
  position: ResearcherPosition;
  contract_type: ContractType;
  contract_end: string | null;
  funding_source_budget_remaining: string;
}

export interface FlaggedItem {
  project_id: string;
  acronym: string;
  flag_type: string;
  severity: string;
  description: string;
}

export interface FinanceDashboard {
  projects: ProjectFinancialRow[];
  total_budget_all_projects: string;
  total_spent_all_projects: string;
  overall_burn_rate: string;
  upcoming_ec_payments: UpcomingECPayment[];
  recruitment_plans: RecruitmentPlanItem[];
  flagged_items: FlaggedItem[];
  generated_at: string;
}

export interface PMDeclarationLine {
  researcher_name: string;
  researcher_position: ResearcherPosition;
  project_acronym: string;
  period_start: string;
  period_end: string;
  planned_pm: string;
  actual_hours: string;
  actual_pm: string;
  hourly_rate: string | null;
  personnel_cost: string;
  submitted: boolean;
  approved: boolean;
}

export interface PMDeclarationsResponse {
  project_id: string;
  period_start: string;
  period_end: string;
  declarations: PMDeclarationLine[];
  total_pm: string;
  total_cost: string;
}

export interface CostStatementLine {
  ec_category: ECBudgetCategory;
  university_account_code: string | null;
  university_category_name: string | null;
  budgeted: string;
  incurred: string;
  ec_eligible_amount: string;
}

export interface CostStatementResponse {
  project_id: string;
  acronym: string;
  period_start: string | null;
  period_end: string | null;
  lines: CostStatementLine[];
  total_incurred: string;
  total_eligible: string;
  indirect_costs: string;
  grand_total: string;
}

export interface OverheadCategoryBreakdown {
  category: ECBudgetCategory;
  amount: string;
}

export interface OverheadCalculationResponse {
  project_id: string;
  acronym: string;
  cost_model: CostModel;
  direct_costs_base: string;
  indirect_rate: string;
  indirect_costs: string;
  subcontracting_excluded: string;
  breakdown: OverheadCategoryBreakdown[];
}

export interface AnnualCategorySpending {
  category: ECBudgetCategory;
  amount: string;
}

export interface AnnualSummaryProject {
  project_id: string;
  acronym: string;
  year: number;
  total_budget: string;
  eu_contribution: string;
  total_spent_year: string;
  total_spent_cumulative: string;
  budget_remaining: string;
  spending_by_category: AnnualCategorySpending[];
  pm_planned: string;
  pm_actual: string;
  funds_received_cumulative: string;
  funds_received_year: string;
}

export interface AnnualSummaryResponse {
  year: number;
  projects: AnnualSummaryProject[];
  total_budget: string;
  total_spent_year: string;
  total_spent_cumulative: string;
}

// --- Reporting Engine (Section 8) ---

export enum ReportingPeriodType {
  PERIODIC = 'PERIODIC',
  FINAL = 'FINAL',
}

export enum ReportStatus {
  DRAFT = 'DRAFT',
  WP_INPUT = 'WP_INPUT',
  PARTNER_REVIEW = 'PARTNER_REVIEW',
  CONSOLIDATION = 'CONSOLIDATION',
  INTERNAL_REVIEW = 'INTERNAL_REVIEW',
  FINAL_REVIEW = 'FINAL_REVIEW',
  SUBMITTED = 'SUBMITTED',
  EC_APPROVED = 'EC_APPROVED',
}

export enum ReportSectionType {
  PART_A_SUMMARY = 'PART_A_SUMMARY',
  PART_B1_WP_NARRATIVE = 'PART_B1_WP_NARRATIVE',
  PART_B2_DELIVERABLES = 'PART_B2_DELIVERABLES',
  PART_B3_RISKS = 'PART_B3_RISKS',
  PART_B4_RESOURCES = 'PART_B4_RESOURCES',
}

export enum ReportSectionStatus {
  DRAFT = 'DRAFT',
  SUBMITTED = 'SUBMITTED',
  APPROVED = 'APPROVED',
}

export enum RiskCategory {
  TECHNICAL = 'TECHNICAL',
  FINANCIAL = 'FINANCIAL',
  ORGANIZATIONAL = 'ORGANIZATIONAL',
  EXTERNAL = 'EXTERNAL',
}

export enum RiskLevel {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
}

export enum RiskStatus {
  OPEN = 'OPEN',
  MITIGATED = 'MITIGATED',
  CLOSED = 'CLOSED',
}

export enum ReminderType {
  T_90 = 'T_90',
  T_60 = 'T_60',
  T_45 = 'T_45',
  T_30 = 'T_30',
  T_20 = 'T_20',
  T_15 = 'T_15',
  T_7 = 'T_7',
}

export const REPORT_STATUS_LABELS: Record<ReportStatus, string> = {
  [ReportStatus.DRAFT]: 'Draft',
  [ReportStatus.WP_INPUT]: 'WP Input',
  [ReportStatus.PARTNER_REVIEW]: 'Partner Review',
  [ReportStatus.CONSOLIDATION]: 'Consolidation',
  [ReportStatus.INTERNAL_REVIEW]: 'Internal Review',
  [ReportStatus.FINAL_REVIEW]: 'Final Review',
  [ReportStatus.SUBMITTED]: 'Submitted',
  [ReportStatus.EC_APPROVED]: 'EC Approved',
};

export const RISK_CATEGORY_LABELS: Record<RiskCategory, string> = {
  [RiskCategory.TECHNICAL]: 'Technical',
  [RiskCategory.FINANCIAL]: 'Financial',
  [RiskCategory.ORGANIZATIONAL]: 'Organizational',
  [RiskCategory.EXTERNAL]: 'External',
};

export const RISK_LEVEL_LABELS: Record<RiskLevel, string> = {
  [RiskLevel.LOW]: 'Low',
  [RiskLevel.MEDIUM]: 'Medium',
  [RiskLevel.HIGH]: 'High',
};

export const RISK_STATUS_LABELS: Record<RiskStatus, string> = {
  [RiskStatus.OPEN]: 'Open',
  [RiskStatus.MITIGATED]: 'Mitigated',
  [RiskStatus.CLOSED]: 'Closed',
};

export const REMINDER_TYPE_LABELS: Record<ReminderType, string> = {
  [ReminderType.T_90]: 'T-90',
  [ReminderType.T_60]: 'T-60',
  [ReminderType.T_45]: 'T-45',
  [ReminderType.T_30]: 'T-30',
  [ReminderType.T_20]: 'T-20',
  [ReminderType.T_15]: 'T-15',
  [ReminderType.T_7]: 'T-7',
};

export interface ReportingPeriod {
  id: string;
  project_id: string;
  period_number: number;
  period_type: ReportingPeriodType;
  start_date: string;
  end_date: string;
  technical_report_deadline: string;
  financial_report_deadline: string | null;
  review_meeting_date: string | null;
  days_until_deadline: number | null;
  created_at: string;
  updated_at: string;
}

export interface ReportingPeriodCreate {
  period_number: number;
  period_type?: ReportingPeriodType;
  start_date: string;
  end_date: string;
  technical_report_deadline: string;
  financial_report_deadline?: string | null;
  review_meeting_date?: string | null;
}

export interface CalendarReminderItem {
  reporting_period_id: string;
  project_id: string;
  project_acronym: string;
  period_number: number;
  reminder_type: ReminderType;
  scheduled_date: string;
  sent: boolean;
  description: string;
}

export interface ReportingCalendar {
  upcoming_deadlines: ReportingPeriod[];
  reminders: CalendarReminderItem[];
  overdue_items: CalendarReminderItem[];
}

export interface Risk {
  id: string;
  project_id: string;
  work_package_id: string | null;
  description: string;
  category: RiskCategory;
  probability: RiskLevel;
  impact: RiskLevel;
  mitigation_strategy: string | null;
  owner: string | null;
  status: RiskStatus;
  actions_taken: string | null;
  created_at: string;
  updated_at: string;
}

export interface RiskCreate {
  description: string;
  category: RiskCategory;
  probability: RiskLevel;
  impact: RiskLevel;
  mitigation_strategy?: string | null;
  owner?: string | null;
  work_package_id?: string | null;
}

export interface ReportSection {
  id: string;
  technical_report_id: string;
  section_type: ReportSectionType;
  work_package_id: string | null;
  content: Record<string, unknown> | null;
  narrative: string | null;
  status: ReportSectionStatus;
  assigned_to: string | null;
  created_at: string;
  updated_at: string;
}

export interface TechnicalReport {
  id: string;
  project_id: string;
  reporting_period_id: string;
  report_type: ReportingPeriodType;
  status: ReportStatus;
  part_a_summary: string | null;
  submitted_by: string | null;
  submitted_at: string | null;
  ec_feedback: string | null;
  sections: ReportSection[];
  created_at: string;
  updated_at: string;
}

export interface WorkflowStepInfo {
  step_number: number;
  name: string;
  actor: string;
  deadline_days_before: number;
  deadline_date: string | null;
  status: string;
}

export interface DeliverableSummaryItem {
  deliverable_number: string;
  title: string;
  type: string;
  dissemination_level: string;
  due_month: number | null;
  submission_date: string | null;
  ec_review_status: string;
  traffic_light: string;
  is_delayed: boolean;
}

export interface MilestoneSummaryItem {
  milestone_number: string;
  title: string;
  wp_number: number | null;
  due_month: number | null;
  achieved: boolean;
  achievement_date: string | null;
}

export interface PartB2Data {
  deliverables: DeliverableSummaryItem[];
  milestones: MilestoneSummaryItem[];
}

export interface WPResourceRow {
  wp_number: number | null;
  wp_title: string | null;
  planned_pm: string;
  actual_pm: string;
  variance_pm: string;
  personnel_cost: string;
}

export interface PartB4Data {
  rows: WPResourceRow[];
  total_planned_pm: string;
  total_actual_pm: string;
  total_personnel_cost: string;
}

export interface RiskSummaryItem {
  risk_id: string;
  description: string;
  category: RiskCategory;
  probability: RiskLevel;
  impact: RiskLevel;
  mitigation_strategy: string | null;
  owner: string | null;
  status: RiskStatus;
  actions_taken: string | null;
}

export interface PartB3Data {
  high_priority_risks: RiskSummaryItem[];
  other_risks: RiskSummaryItem[];
}

// --- Financial Reporting (Section 8.3) ---

export enum FinancialStatementStatus {
  DRAFT = 'DRAFT',
  PARTNER_SUBMITTED = 'PARTNER_SUBMITTED',
  COORDINATOR_REVIEW = 'COORDINATOR_REVIEW',
  COORDINATOR_APPROVED = 'COORDINATOR_APPROVED',
  REPORTED_TO_EC = 'REPORTED_TO_EC',
  EC_APPROVED = 'EC_APPROVED',
}

export const FINANCIAL_STATEMENT_STATUS_LABELS: Record<FinancialStatementStatus, string> = {
  [FinancialStatementStatus.DRAFT]: 'Draft',
  [FinancialStatementStatus.PARTNER_SUBMITTED]: 'Partner Submitted',
  [FinancialStatementStatus.COORDINATOR_REVIEW]: 'Coordinator Review',
  [FinancialStatementStatus.COORDINATOR_APPROVED]: 'Coordinator Approved',
  [FinancialStatementStatus.REPORTED_TO_EC]: 'Reported to EC',
  [FinancialStatementStatus.EC_APPROVED]: 'EC Approved',
};

export enum CFSStatus {
  NOT_REQUIRED = 'NOT_REQUIRED',
  PENDING = 'PENDING',
  OBTAINED = 'OBTAINED',
  SUBMITTED = 'SUBMITTED',
}

export enum UnitType {
  PERSON_DAY = 'PERSON_DAY',
  PERSON_MONTH = 'PERSON_MONTH',
  TRAINING_HOUR = 'TRAINING_HOUR',
  PUBLICATION = 'PUBLICATION',
  DATASET = 'DATASET',
  PROTOTYPE = 'PROTOTYPE',
  EVENT = 'EVENT',
  LICENCE = 'LICENCE',
  OTHER = 'OTHER',
}

export enum UnitCostStatus {
  PLANNED = 'PLANNED',
  REPORTED = 'REPORTED',
  APPROVED = 'APPROVED',
}

export enum CompletionStatus {
  NOT_STARTED = 'NOT_STARTED',
  IN_PROGRESS = 'IN_PROGRESS',
  COMPLETED = 'COMPLETED',
  PARTIALLY_COMPLETED = 'PARTIALLY_COMPLETED',
}

export const COMPLETION_STATUS_LABELS: Record<CompletionStatus, string> = {
  [CompletionStatus.NOT_STARTED]: 'Not Started',
  [CompletionStatus.IN_PROGRESS]: 'In Progress',
  [CompletionStatus.COMPLETED]: 'Completed',
  [CompletionStatus.PARTIALLY_COMPLETED]: 'Partially Completed',
};

export interface FinancialStatement {
  id: string;
  project_id: string;
  reporting_period_id: string;
  partner_id: string | null;
  status: FinancialStatementStatus;
  category_a_personnel: string;
  category_b_subcontracting: string;
  category_c_travel: string;
  category_d_equipment: string;
  category_e_other: string;
  total_direct_costs: string;
  indirect_costs: string;
  total_eligible_costs: string;
  ec_contribution_requested: string;
  cumulative_claimed: string;
  cfs_required: boolean;
  cfs_status: CFSStatus;
  partner_signed_by: string | null;
  partner_signed_at: string | null;
  coordinator_approved_by: string | null;
  coordinator_approved_at: string | null;
  reported_to_ec_at: string | null;
  university_report_data: Record<string, unknown> | null;
  discrepancies: Record<string, unknown> | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface WPCompletionDeclaration {
  id: string;
  project_id: string;
  reporting_period_id: string;
  work_package_id: string;
  completion_status: CompletionStatus;
  completion_percentage: number;
  lump_sum_amount: string;
  amount_claimed: string;
  evidence_documents: Record<string, unknown> | null;
  partial_completion_justification: string | null;
  deliverables_completed: Record<string, unknown> | null;
  declared_by: string | null;
  declared_at: string | null;
  approved_by: string | null;
  approved_at: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface UnitDeliveryRecord {
  id: string;
  project_id: string;
  reporting_period_id: string;
  work_package_id: string | null;
  description: string;
  unit_type: UnitType;
  planned_units: string;
  actual_units: string;
  unit_rate: string;
  total_cost: string;
  status: UnitCostStatus;
  evidence_documents: Record<string, unknown> | null;
  evidence_description: string | null;
  reported_by: string | null;
  reported_at: string | null;
  approved_by: string | null;
  approved_at: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface CategoryBreakdownRow {
  ec_category: string;
  university_account_code: string | null;
  university_category_name: string | null;
  budgeted: string;
  incurred: string;
  ec_eligible: string;
}

export interface FormCReport {
  project_id: string;
  project_acronym: string;
  reporting_period_id: string;
  partner_id: string | null;
  period_start: string;
  period_end: string;
  category_breakdown: CategoryBreakdownRow[];
  total_direct_costs: string;
  indirect_costs: string;
  indirect_rate: string;
  total_eligible_costs: string;
  ec_contribution_requested: string;
  cumulative_claimed: string;
  cfs_required: boolean;
  cfs_status: CFSStatus;
}

export interface LumpSumReport {
  project_id: string;
  project_acronym: string;
  reporting_period_id: string;
  declarations: WPCompletionDeclaration[];
  total_lump_sum: string;
  total_claimed: string;
}

export interface UnitCostReport {
  project_id: string;
  project_acronym: string;
  reporting_period_id: string;
  records: UnitDeliveryRecord[];
  total_planned_cost: string;
  total_actual_cost: string;
}

export interface InstitutionalMappingRow {
  ec_category: string;
  ec_amount: string;
  university_account_code: string | null;
  university_category_name: string | null;
  university_amount: string;
  discrepancy: string;
}

export interface InstitutionalReport {
  project_id: string;
  project_acronym: string;
  rows: InstitutionalMappingRow[];
  total_ec: string;
  total_university: string;
  total_discrepancy: string;
  has_discrepancies: boolean;
}

export interface CostModelFinancialReport {
  project_id: string;
  project_acronym: string;
  cost_model: string;
  reporting_period_id: string | null;
  form_c: FormCReport | null;
  lump_sum: LumpSumReport | null;
  unit_cost: UnitCostReport | null;
  institutional_report: InstitutionalReport | null;
}

// --- Template Library (Section 7) ---

export enum TemplateCategory {
  PERSONNEL = 'PERSONNEL',
  EC_CONSORTIUM = 'EC_CONSORTIUM',
  REPORTING = 'REPORTING',
  MISSION_TRAVEL = 'MISSION_TRAVEL',
  PROCUREMENT = 'PROCUREMENT',
}

export enum PersonnelTemplateType {
  BOLSA_BI = 'BOLSA_BI',
  BOLSA_BD = 'BOLSA_BD',
  BOLSA_BPD = 'BOLSA_BPD',
  DL57 = 'DL57',
  CEEC = 'CEEC',
  CLT = 'CLT',
  CONTRACT_RENEWAL = 'CONTRACT_RENEWAL',
}

export enum GeneratedDocumentStatus {
  DRAFT = 'DRAFT',
  PENDING_APPROVAL = 'PENDING_APPROVAL',
  APPROVED = 'APPROVED',
  SIGNED = 'SIGNED',
  ARCHIVED = 'ARCHIVED',
}

export const TEMPLATE_CATEGORY_LABELS: Record<TemplateCategory, string> = {
  [TemplateCategory.PERSONNEL]: 'Personnel',
  [TemplateCategory.EC_CONSORTIUM]: 'EC / Consortium',
  [TemplateCategory.REPORTING]: 'Reporting',
  [TemplateCategory.MISSION_TRAVEL]: 'Mission / Travel',
  [TemplateCategory.PROCUREMENT]: 'Procurement',
};

export const PERSONNEL_TEMPLATE_TYPE_LABELS: Record<PersonnelTemplateType, string> = {
  [PersonnelTemplateType.BOLSA_BI]: 'Bolsa de Investigação (BI)',
  [PersonnelTemplateType.BOLSA_BD]: 'Bolsa de Doutoramento (BD)',
  [PersonnelTemplateType.BOLSA_BPD]: 'Bolsa de Pós-Doutoramento (BPD)',
  [PersonnelTemplateType.DL57]: 'DL 57 Contract',
  [PersonnelTemplateType.CEEC]: 'CEEC Contract',
  [PersonnelTemplateType.CLT]: 'CLT Employment Contract',
  [PersonnelTemplateType.CONTRACT_RENEWAL]: 'Contract Renewal / Extension',
};

export const GENERATED_DOCUMENT_STATUS_LABELS: Record<GeneratedDocumentStatus, string> = {
  [GeneratedDocumentStatus.DRAFT]: 'Draft',
  [GeneratedDocumentStatus.PENDING_APPROVAL]: 'Pending Approval',
  [GeneratedDocumentStatus.APPROVED]: 'Approved',
  [GeneratedDocumentStatus.SIGNED]: 'Signed',
  [GeneratedDocumentStatus.ARCHIVED]: 'Archived',
};

export interface TemplateFieldDef {
  name: string;
  label: string;
  field_type: 'auto' | 'manual';
  data_source?: string;
  input_type?: string;
  required?: boolean;
  help_text?: string;
}

export interface ConditionalSectionDef {
  condition_field: string;
  condition_value: string;
  condition_operator: 'eq' | 'neq' | 'in';
  content: string;
}

export interface DocumentTemplate {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  category: TemplateCategory;
  personnel_type: PersonnelTemplateType | null;
  version: number;
  field_definitions: {
    fields: TemplateFieldDef[];
  };
  conditional_sections: Record<string, ConditionalSectionDef> | null;
  supported_cost_models: string[] | null;
  supported_programmes: string[] | null;
  created_at: string;
  updated_at: string;
}

export interface TemplateFieldPreview {
  name: string;
  label: string;
  field_type: 'auto' | 'manual';
  value: string | null;
  input_type: string;
  required: boolean;
  help_text: string | null;
}

export interface TemplatePreviewResponse {
  template_id: string;
  template_name: string;
  fields: TemplateFieldPreview[];
  conditional_sections_active: string[];
}

export interface GeneratedDocument {
  id: string;
  template_id: string;
  project_id: string | null;
  researcher_id: string | null;
  template_version: number;
  generated_by: string | null;
  generated_at: string;
  input_data: Record<string, unknown>;
  file_path: string | null;
  file_name: string;
  status: GeneratedDocumentStatus;
  created_at: string;
  updated_at: string;
}

// ──────────────────────────────────────────────────────
//  Section 9 — Additional Features
// ──────────────────────────────────────────────────────

// 9.1 IP and Exploitation Tracking

export enum IPType {
  BACKGROUND = 'BACKGROUND',
  FOREGROUND = 'FOREGROUND',
}

export enum IPStatus {
  IDENTIFIED = 'IDENTIFIED',
  DISCLOSED = 'DISCLOSED',
  PATENT_FILED = 'PATENT_FILED',
  PATENT_GRANTED = 'PATENT_GRANTED',
  LICENSED = 'LICENSED',
  EXPLOITED = 'EXPLOITED',
}

export const IP_TYPE_LABELS: Record<IPType, string> = {
  [IPType.BACKGROUND]: 'Background',
  [IPType.FOREGROUND]: 'Foreground',
};

export const IP_STATUS_LABELS: Record<IPStatus, string> = {
  [IPStatus.IDENTIFIED]: 'Identified',
  [IPStatus.DISCLOSED]: 'Disclosed',
  [IPStatus.PATENT_FILED]: 'Patent Filed',
  [IPStatus.PATENT_GRANTED]: 'Patent Granted',
  [IPStatus.LICENSED]: 'Licensed',
  [IPStatus.EXPLOITED]: 'Exploited',
};

export interface IPAsset {
  id: string;
  project_id: string;
  partner_id: string | null;
  work_package_id: string | null;
  deliverable_id: string | null;
  ip_type: IPType;
  title: string;
  description: string | null;
  status: IPStatus;
  owner: string | null;
  patent_reference: string | null;
  patent_filing_date: string | null;
  licensing_details: string | null;
  exploitation_plan: string | null;
  access_rights: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

// 9.3 Dissemination Log

export enum DisseminationActivityType {
  PUBLICATION = 'PUBLICATION',
  CONFERENCE = 'CONFERENCE',
  PRESS_RELEASE = 'PRESS_RELEASE',
  SOCIAL_MEDIA = 'SOCIAL_MEDIA',
  WORKSHOP = 'WORKSHOP',
  POLICY_BRIEF = 'POLICY_BRIEF',
  OTHER = 'OTHER',
}

export enum OpenAccessStatus {
  NOT_APPLICABLE = 'NOT_APPLICABLE',
  GREEN = 'GREEN',
  GOLD = 'GOLD',
  DIAMOND = 'DIAMOND',
  EMBARGO = 'EMBARGO',
  NON_COMPLIANT = 'NON_COMPLIANT',
}

export const DISSEMINATION_ACTIVITY_TYPE_LABELS: Record<DisseminationActivityType, string> = {
  [DisseminationActivityType.PUBLICATION]: 'Publication',
  [DisseminationActivityType.CONFERENCE]: 'Conference',
  [DisseminationActivityType.PRESS_RELEASE]: 'Press Release',
  [DisseminationActivityType.SOCIAL_MEDIA]: 'Social Media',
  [DisseminationActivityType.WORKSHOP]: 'Workshop',
  [DisseminationActivityType.POLICY_BRIEF]: 'Policy Brief',
  [DisseminationActivityType.OTHER]: 'Other',
};

export const OPEN_ACCESS_STATUS_LABELS: Record<OpenAccessStatus, string> = {
  [OpenAccessStatus.NOT_APPLICABLE]: 'N/A',
  [OpenAccessStatus.GREEN]: 'Green',
  [OpenAccessStatus.GOLD]: 'Gold',
  [OpenAccessStatus.DIAMOND]: 'Diamond',
  [OpenAccessStatus.EMBARGO]: 'Embargo',
  [OpenAccessStatus.NON_COMPLIANT]: 'Non-Compliant',
};

export interface DisseminationActivity {
  id: string;
  project_id: string;
  work_package_id: string | null;
  deliverable_id: string | null;
  activity_type: DisseminationActivityType;
  title: string;
  description: string | null;
  authors: string | null;
  venue: string | null;
  activity_date: string | null;
  doi: string | null;
  url: string | null;
  open_access_status: OpenAccessStatus;
  target_audience: string | null;
  countries_reached: string[] | null;
  evidence_documents: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

// 9.4 KPI Tracking

export enum KPIDataType {
  INTEGER = 'INTEGER',
  DECIMAL = 'DECIMAL',
  PERCENTAGE = 'PERCENTAGE',
  BOOLEAN = 'BOOLEAN',
  TEXT = 'TEXT',
}

export const KPI_DATA_TYPE_LABELS: Record<KPIDataType, string> = {
  [KPIDataType.INTEGER]: 'Integer',
  [KPIDataType.DECIMAL]: 'Decimal',
  [KPIDataType.PERCENTAGE]: 'Percentage',
  [KPIDataType.BOOLEAN]: 'Boolean',
  [KPIDataType.TEXT]: 'Text',
};

export interface KPIDefinition {
  id: string;
  name: string;
  description: string | null;
  data_type: KPIDataType;
  unit: string | null;
  programme: string | null;
  is_standard: boolean;
  created_at: string;
  updated_at: string;
}

export interface KPIValue {
  id: string;
  project_id: string;
  kpi_definition_id: string;
  reporting_period_id: string | null;
  value_integer: number | null;
  value_decimal: number | null;
  value_text: string | null;
  value_boolean: boolean | null;
  target_value: string | null;
  notes: string | null;
  recorded_at: string | null;
  created_at: string;
  updated_at: string;
}

// 9.5 Ethics and Data Management

export enum EthicsStatus {
  PENDING = 'PENDING',
  SUBMITTED = 'SUBMITTED',
  APPROVED = 'APPROVED',
  REJECTED = 'REJECTED',
  NOT_APPLICABLE = 'NOT_APPLICABLE',
}

export enum DMPStatus {
  DRAFT = 'DRAFT',
  SUBMITTED = 'SUBMITTED',
  APPROVED = 'APPROVED',
  COMPLIANT = 'COMPLIANT',
  NON_COMPLIANT = 'NON_COMPLIANT',
}

export const ETHICS_STATUS_LABELS: Record<EthicsStatus, string> = {
  [EthicsStatus.PENDING]: 'Pending',
  [EthicsStatus.SUBMITTED]: 'Submitted',
  [EthicsStatus.APPROVED]: 'Approved',
  [EthicsStatus.REJECTED]: 'Rejected',
  [EthicsStatus.NOT_APPLICABLE]: 'N/A',
};

export const DMP_STATUS_LABELS: Record<DMPStatus, string> = {
  [DMPStatus.DRAFT]: 'Draft',
  [DMPStatus.SUBMITTED]: 'Submitted',
  [DMPStatus.APPROVED]: 'Approved',
  [DMPStatus.COMPLIANT]: 'Compliant',
  [DMPStatus.NON_COMPLIANT]: 'Non-Compliant',
};

export interface EthicsRequirement {
  id: string;
  project_id: string;
  deliverable_id: string | null;
  requirement_type: string;
  description: string | null;
  status: EthicsStatus;
  due_date: string | null;
  submitted_date: string | null;
  approval_date: string | null;
  ethics_committee_ref: string | null;
  informed_consent_obtained: boolean;
  dpia_required: boolean;
  dpia_reference: string | null;
  supporting_documents: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export interface DataManagementRecord {
  id: string;
  project_id: string;
  dataset_name: string;
  description: string | null;
  repository: string | null;
  repository_url: string | null;
  dmp_status: DMPStatus;
  fair_findable: boolean;
  fair_accessible: boolean;
  fair_interoperable: boolean;
  fair_reusable: boolean;
  data_format: string | null;
  retention_period: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

// 9.6 Collaboration Network

export interface CollaborationRecord {
  id: string;
  partner_id: string;
  project_id: string | null;
  expertise_areas: string[] | null;
  reliability_rating: number | null;
  collaboration_notes: string | null;
  contact_person: string | null;
  contact_email: string | null;
  co_publications: number;
  last_collaboration_date: string | null;
  created_at: string;
  updated_at: string;
}

// 9.7 Amendment Tracking

export enum AmendmentStatus {
  DRAFT = 'DRAFT',
  SUBMITTED = 'SUBMITTED',
  UNDER_REVIEW = 'UNDER_REVIEW',
  APPROVED = 'APPROVED',
  REJECTED = 'REJECTED',
  WITHDRAWN = 'WITHDRAWN',
}

export enum AmendmentType {
  BUDGET_TRANSFER = 'BUDGET_TRANSFER',
  TIMELINE_CHANGE = 'TIMELINE_CHANGE',
  PARTNER_CHANGE = 'PARTNER_CHANGE',
  SCOPE_CHANGE = 'SCOPE_CHANGE',
  OTHER = 'OTHER',
}

export const AMENDMENT_STATUS_LABELS: Record<AmendmentStatus, string> = {
  [AmendmentStatus.DRAFT]: 'Draft',
  [AmendmentStatus.SUBMITTED]: 'Submitted',
  [AmendmentStatus.UNDER_REVIEW]: 'Under Review',
  [AmendmentStatus.APPROVED]: 'Approved',
  [AmendmentStatus.REJECTED]: 'Rejected',
  [AmendmentStatus.WITHDRAWN]: 'Withdrawn',
};

export const AMENDMENT_TYPE_LABELS: Record<AmendmentType, string> = {
  [AmendmentType.BUDGET_TRANSFER]: 'Budget Transfer',
  [AmendmentType.TIMELINE_CHANGE]: 'Timeline Change',
  [AmendmentType.PARTNER_CHANGE]: 'Partner Change',
  [AmendmentType.SCOPE_CHANGE]: 'Scope Change',
  [AmendmentType.OTHER]: 'Other',
};

export interface Amendment {
  id: string;
  project_id: string;
  amendment_number: number;
  amendment_type: AmendmentType;
  title: string;
  description: string;
  rationale: string | null;
  status: AmendmentStatus;
  request_date: string | null;
  submission_date: string | null;
  ec_decision_date: string | null;
  changes_summary: Record<string, unknown> | null;
  affected_partners: string[] | null;
  affected_work_packages: string[] | null;
  budget_impact: Record<string, unknown> | null;
  submitted_by: string | null;
  created_at: string;
  updated_at: string;
}

// 9.8 Notification System

export enum NotificationType {
  REPORTING_DEADLINE = 'REPORTING_DEADLINE',
  TIMESHEET_REMINDER = 'TIMESHEET_REMINDER',
  DELIVERABLE_DUE = 'DELIVERABLE_DUE',
  BUDGET_THRESHOLD = 'BUDGET_THRESHOLD',
  CONTRACT_EXPIRY = 'CONTRACT_EXPIRY',
  AMENDMENT_STATUS = 'AMENDMENT_STATUS',
  EC_FEEDBACK = 'EC_FEEDBACK',
  PARTNER_PAYMENT = 'PARTNER_PAYMENT',
  RISK_ESCALATION = 'RISK_ESCALATION',
}

export enum NotificationPriority {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
  CRITICAL = 'CRITICAL',
}

export enum NotificationStatus {
  PENDING = 'PENDING',
  SENT = 'SENT',
  READ = 'READ',
  DISMISSED = 'DISMISSED',
}

export const NOTIFICATION_TYPE_LABELS: Record<NotificationType, string> = {
  [NotificationType.REPORTING_DEADLINE]: 'Reporting Deadline',
  [NotificationType.TIMESHEET_REMINDER]: 'Timesheet Reminder',
  [NotificationType.DELIVERABLE_DUE]: 'Deliverable Due',
  [NotificationType.BUDGET_THRESHOLD]: 'Budget Threshold',
  [NotificationType.CONTRACT_EXPIRY]: 'Contract Expiry',
  [NotificationType.AMENDMENT_STATUS]: 'Amendment Status',
  [NotificationType.EC_FEEDBACK]: 'EC Feedback',
  [NotificationType.PARTNER_PAYMENT]: 'Partner Payment',
  [NotificationType.RISK_ESCALATION]: 'Risk Escalation',
};

export const NOTIFICATION_PRIORITY_LABELS: Record<NotificationPriority, string> = {
  [NotificationPriority.LOW]: 'Low',
  [NotificationPriority.MEDIUM]: 'Medium',
  [NotificationPriority.HIGH]: 'High',
  [NotificationPriority.CRITICAL]: 'Critical',
};

export const NOTIFICATION_STATUS_LABELS: Record<NotificationStatus, string> = {
  [NotificationStatus.PENDING]: 'Pending',
  [NotificationStatus.SENT]: 'Sent',
  [NotificationStatus.READ]: 'Read',
  [NotificationStatus.DISMISSED]: 'Dismissed',
};

export interface Notification {
  id: string;
  project_id: string | null;
  notification_type: NotificationType;
  priority: NotificationPriority;
  status: NotificationStatus;
  title: string;
  message: string;
  recipient_role: string | null;
  recipient_email: string | null;
  trigger_entity_type: string | null;
  trigger_entity_id: string | null;
  scheduled_at: string | null;
  sent_at: string | null;
  read_at: string | null;
  dismissed_at: string | null;
  extra_data: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

// List response wrappers for Section 9

export interface IPAssetListResponse {
  items: IPAsset[];
  total: number;
}

export interface DisseminationActivityListResponse {
  items: DisseminationActivity[];
  total: number;
}

export interface KPIDefinitionListResponse {
  items: KPIDefinition[];
  total: number;
}

export interface KPIValueListResponse {
  items: KPIValue[];
  total: number;
}

export interface EthicsRequirementListResponse {
  items: EthicsRequirement[];
  total: number;
}

export interface DataManagementRecordListResponse {
  items: DataManagementRecord[];
  total: number;
}

export interface CollaborationRecordListResponse {
  items: CollaborationRecord[];
  total: number;
}

export interface AmendmentListResponse {
  items: Amendment[];
  total: number;
}

export interface NotificationListResponse {
  items: Notification[];
  total: number;
}

// ── Section 10: Role-Based Dashboards ─────────────────────

// PI Dashboard
export interface PIProjectSummary {
  project_id: string;
  acronym: string;
  programme: Programme;
  status: ProjectStatus;
  traffic_light: 'GREEN' | 'AMBER' | 'RED';
  next_deadline: string | null;
  next_deadline_type: string | null;
  budget_total: number;
  budget_spent: number;
  burn_rate_pct: number;
  team_size: number;
  open_risks: number;
  active_amendments: number;
}

export interface CrossProjectDeadline {
  project_acronym: string;
  project_id: string;
  deadline_type: string;
  date: string;
  days_until: number;
}

export interface PIDashboardResponse {
  projects: PIProjectSummary[];
  cross_project_deadlines: CrossProjectDeadline[];
  total_budget: number;
  total_spent: number;
  overall_burn_rate: number;
  active_project_count: number;
}

// Researcher Dashboard
export interface ResearcherAllocationSummary {
  project_id: string;
  project_acronym: string;
  wp_title: string | null;
  planned_pm: number;
  actual_pm: number;
  period_start: string | null;
  period_end: string | null;
}

export interface TimesheetStatusItem {
  project_acronym: string;
  project_id: string;
  month: string;
  hours_logged: number;
  hours_expected: number;
  status: 'complete' | 'incomplete' | 'not_started';
}

export interface ResearcherDeadline {
  project_acronym: string;
  project_id: string;
  deadline_type: string;
  title: string;
  due_date: string;
  days_until: number;
}

export interface ResearcherDashboardResponse {
  researcher_name: string;
  researcher_id: string;
  allocations: ResearcherAllocationSummary[];
  timesheet_status: TimesheetStatusItem[];
  upcoming_deadlines: ResearcherDeadline[];
  total_planned_pm: number;
  total_actual_pm: number;
}

// Project Dashboard
export interface WPProgressItem {
  wp_number: number | null;
  wp_title: string | null;
  status: WPStatus;
  deliverables_total: number;
  deliverables_completed: number;
  progress_pct: number;
}

export interface DeliverableTimelineItem {
  deliverable_number: string | null;
  title: string;
  deliverable_type: DeliverableType;
  due_month: number | null;
  submission_date: string | null;
  ec_review_status: ECReviewStatus;
  traffic_light: TrafficLight;
}

export interface BudgetCategoryItem {
  category: string;
  category_label: string;
  budgeted: number;
  spent: number;
  remaining: number;
  pct_used: number;
}

export interface PartnerStatusItem {
  partner_name: string;
  partner_id: string;
  country: string | null;
  allocated_budget: number;
  spent: number;
  pct_used: number;
}

export interface ProjectRiskSummary {
  risk_id: string;
  description: string;
  category: RiskCategory;
  probability: RiskLevel;
  impact: RiskLevel;
  status: RiskStatus;
  owner: string | null;
}

export interface ProjectDashboardResponse {
  project_id: string;
  acronym: string;
  wp_progress: WPProgressItem[];
  deliverable_timeline: DeliverableTimelineItem[];
  budget_by_category: BudgetCategoryItem[];
  partner_status: PartnerStatusItem[];
  risks: ProjectRiskSummary[];
  burn_rate: number;
  burn_rate_status: string;
  pm_compliance_rate: number;
  deliverable_completion_rate: number;
  total_budget: number;
  total_spent: number;
}
