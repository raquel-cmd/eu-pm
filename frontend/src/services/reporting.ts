import api from './api';
import type {
  ReportingPeriod,
  ReportingPeriodCreate,
  ReportingCalendar,
  Risk,
  RiskCreate,
  TechnicalReport,
  WorkflowStepInfo,
  ReportSection,
  PartB2Data,
  PartB3Data,
  PartB4Data,
} from '../types';

// --- Reporting Periods ---

export async function autoGenerateReportingPeriods(
  projectId: string
): Promise<{ items: ReportingPeriod[]; total: number }> {
  const { data } = await api.post(
    `/projects/${projectId}/reporting-periods/auto-generate`
  );
  return data;
}

export async function createReportingPeriod(
  projectId: string,
  period: ReportingPeriodCreate
): Promise<ReportingPeriod> {
  const { data } = await api.post(
    `/projects/${projectId}/reporting-periods`,
    period
  );
  return data;
}

export async function listReportingPeriods(
  projectId: string
): Promise<{ items: ReportingPeriod[]; total: number }> {
  const { data } = await api.get(
    `/projects/${projectId}/reporting-periods`
  );
  return data;
}

export async function getReportingPeriod(
  periodId: string
): Promise<ReportingPeriod> {
  const { data } = await api.get(`/reporting-periods/${periodId}`);
  return data;
}

export async function deleteReportingPeriod(
  periodId: string
): Promise<void> {
  await api.delete(`/reporting-periods/${periodId}`);
}

// --- Reporting Calendar ---

export async function getReportingCalendar(
  projectId?: string
): Promise<ReportingCalendar> {
  const { data } = await api.get('/reporting-calendar', {
    params: projectId ? { project_id: projectId } : {},
  });
  return data;
}

export async function sendDueReminders(): Promise<{
  reminders_sent: number;
}> {
  const { data } = await api.post('/reporting-calendar/send-reminders');
  return data;
}

// --- Risk Register ---

export async function createRisk(
  projectId: string,
  risk: RiskCreate
): Promise<Risk> {
  const { data } = await api.post(`/projects/${projectId}/risks`, risk);
  return data;
}

export async function listRisks(
  projectId: string,
  status?: string
): Promise<{ items: Risk[]; total: number }> {
  const { data } = await api.get(`/projects/${projectId}/risks`, {
    params: status ? { status } : {},
  });
  return data;
}

export async function getRisk(riskId: string): Promise<Risk> {
  const { data } = await api.get(`/risks/${riskId}`);
  return data;
}

export async function updateRisk(
  riskId: string,
  update: Partial<Risk>
): Promise<Risk> {
  const { data } = await api.put(`/risks/${riskId}`, update);
  return data;
}

export async function deleteRisk(riskId: string): Promise<void> {
  await api.delete(`/risks/${riskId}`);
}

// --- Technical Reports ---

export async function createReportShell(
  periodId: string
): Promise<TechnicalReport> {
  const { data } = await api.post(
    `/reporting-periods/${periodId}/report`
  );
  return data;
}

export async function listTechnicalReports(
  projectId: string
): Promise<{ items: TechnicalReport[]; total: number }> {
  const { data } = await api.get(
    `/projects/${projectId}/technical-reports`
  );
  return data;
}

export async function getTechnicalReport(
  reportId: string
): Promise<TechnicalReport> {
  const { data } = await api.get(`/technical-reports/${reportId}`);
  return data;
}

export async function updateTechnicalReport(
  reportId: string,
  update: { part_a_summary?: string; status?: string; ec_feedback?: string }
): Promise<TechnicalReport> {
  const { data } = await api.put(`/technical-reports/${reportId}`, update);
  return data;
}

export async function advanceReportWorkflow(
  reportId: string
): Promise<TechnicalReport> {
  const { data } = await api.post(
    `/technical-reports/${reportId}/advance`
  );
  return data;
}

export async function getReportWorkflow(
  reportId: string
): Promise<WorkflowStepInfo[]> {
  const { data } = await api.get(
    `/technical-reports/${reportId}/workflow`
  );
  return data;
}

// --- Report Sections ---

export async function updateReportSection(
  sectionId: string,
  update: {
    content?: Record<string, unknown>;
    narrative?: string;
    status?: string;
    assigned_to?: string;
  }
): Promise<ReportSection> {
  const { data } = await api.put(`/report-sections/${sectionId}`, update);
  return data;
}

// --- Auto-Generated Data ---

export async function getPartB2Data(
  reportId: string
): Promise<PartB2Data> {
  const { data } = await api.get(
    `/technical-reports/${reportId}/part-b2`
  );
  return data;
}

export async function getPartB3Data(
  reportId: string
): Promise<PartB3Data> {
  const { data } = await api.get(
    `/technical-reports/${reportId}/part-b3`
  );
  return data;
}

export async function getPartB4Data(
  reportId: string
): Promise<PartB4Data> {
  const { data } = await api.get(
    `/technical-reports/${reportId}/part-b4`
  );
  return data;
}
