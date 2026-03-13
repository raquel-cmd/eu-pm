import api from './api';
import type {
  FinancialStatement,
  WPCompletionDeclaration,
  UnitDeliveryRecord,
  CostModelFinancialReport,
  FormCReport,
  LumpSumReport,
  UnitCostReport,
  InstitutionalReport,
} from '../types';

// --- Financial Statements (Form C) ---

export async function createFinancialStatement(
  projectId: string,
  reportingPeriodId: string,
  partnerId?: string,
): Promise<FinancialStatement> {
  const { data } = await api.post(
    `/projects/${projectId}/financial-statements`,
    { reporting_period_id: reportingPeriodId, partner_id: partnerId },
  );
  return data;
}

export async function listFinancialStatements(
  projectId: string,
  reportingPeriodId?: string,
): Promise<{ items: FinancialStatement[]; total: number }> {
  const params: Record<string, string> = {};
  if (reportingPeriodId) params.reporting_period_id = reportingPeriodId;
  const { data } = await api.get(
    `/projects/${projectId}/financial-statements`,
    { params },
  );
  return data;
}

export async function getFinancialStatement(
  statementId: string,
): Promise<FinancialStatement> {
  const { data } = await api.get(`/financial-statements/${statementId}`);
  return data;
}

export async function advanceFinancialStatement(
  statementId: string,
  actor?: string,
): Promise<FinancialStatement> {
  const params: Record<string, string> = {};
  if (actor) params.actor = actor;
  const { data } = await api.post(
    `/financial-statements/${statementId}/advance`,
    null,
    { params },
  );
  return data;
}

// --- WP Completion Declarations (Lump Sum) ---

export async function createWPDeclaration(
  projectId: string,
  reportingPeriodId: string,
  workPackageId: string,
  lumpSumAmount: string,
): Promise<WPCompletionDeclaration> {
  const { data } = await api.post(
    `/projects/${projectId}/wp-declarations`,
    {
      reporting_period_id: reportingPeriodId,
      work_package_id: workPackageId,
      lump_sum_amount: lumpSumAmount,
    },
  );
  return data;
}

export async function listWPDeclarations(
  projectId: string,
  reportingPeriodId?: string,
): Promise<{ items: WPCompletionDeclaration[]; total: number }> {
  const params: Record<string, string> = {};
  if (reportingPeriodId) params.reporting_period_id = reportingPeriodId;
  const { data } = await api.get(
    `/projects/${projectId}/wp-declarations`,
    { params },
  );
  return data;
}

export async function updateWPDeclaration(
  declarationId: string,
  updates: Record<string, unknown>,
): Promise<WPCompletionDeclaration> {
  const { data } = await api.put(
    `/wp-declarations/${declarationId}`,
    updates,
  );
  return data;
}

// --- Unit Delivery Records ---

export async function createUnitRecord(
  projectId: string,
  body: {
    reporting_period_id: string;
    work_package_id?: string;
    description: string;
    unit_type: string;
    planned_units: string;
    unit_rate: string;
  },
): Promise<UnitDeliveryRecord> {
  const { data } = await api.post(
    `/projects/${projectId}/unit-records`,
    body,
  );
  return data;
}

export async function listUnitRecords(
  projectId: string,
  reportingPeriodId?: string,
): Promise<{ items: UnitDeliveryRecord[]; total: number }> {
  const params: Record<string, string> = {};
  if (reportingPeriodId) params.reporting_period_id = reportingPeriodId;
  const { data } = await api.get(
    `/projects/${projectId}/unit-records`,
    { params },
  );
  return data;
}

export async function updateUnitRecord(
  recordId: string,
  updates: Record<string, unknown>,
): Promise<UnitDeliveryRecord> {
  const { data } = await api.put(`/unit-records/${recordId}`, updates);
  return data;
}

// --- Cost-Model-Aware Reports ---

export async function getFinancialReport(
  projectId: string,
  reportingPeriodId?: string,
): Promise<CostModelFinancialReport> {
  const params: Record<string, string> = {};
  if (reportingPeriodId) params.reporting_period_id = reportingPeriodId;
  const { data } = await api.get(
    `/projects/${projectId}/financial-report`,
    { params },
  );
  return data;
}

export async function getFormCReport(
  projectId: string,
  reportingPeriodId: string,
  partnerId?: string,
): Promise<FormCReport> {
  const params: Record<string, string> = {
    reporting_period_id: reportingPeriodId,
  };
  if (partnerId) params.partner_id = partnerId;
  const { data } = await api.get(`/projects/${projectId}/form-c`, {
    params,
  });
  return data;
}

export async function getLumpSumReport(
  projectId: string,
  reportingPeriodId: string,
): Promise<LumpSumReport> {
  const { data } = await api.get(`/projects/${projectId}/lump-sum-report`, {
    params: { reporting_period_id: reportingPeriodId },
  });
  return data;
}

export async function getUnitCostReport(
  projectId: string,
  reportingPeriodId: string,
): Promise<UnitCostReport> {
  const { data } = await api.get(
    `/projects/${projectId}/unit-cost-report`,
    { params: { reporting_period_id: reportingPeriodId } },
  );
  return data;
}

export async function getInstitutionalReport(
  projectId: string,
): Promise<InstitutionalReport> {
  const { data } = await api.get(
    `/projects/${projectId}/institutional-report`,
  );
  return data;
}
