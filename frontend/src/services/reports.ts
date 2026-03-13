import api from './api';
import type {
  FinanceDashboard,
  PMDeclarationsResponse,
  CostStatementResponse,
  OverheadCalculationResponse,
  AnnualSummaryResponse,
} from '../types';

const REPORTS_HEADERS = { 'X-User-Role': 'CENTRAL_FINANCE_PM' };

export async function getFinanceDashboard(): Promise<FinanceDashboard> {
  const { data } = await api.get('/reports/finance-dashboard', {
    headers: REPORTS_HEADERS,
  });
  return data;
}

export async function getPMDeclarations(params: {
  project_id: string;
  period_start: string;
  period_end: string;
}): Promise<PMDeclarationsResponse> {
  const { data } = await api.get('/reports/pm-declarations', {
    params,
    headers: REPORTS_HEADERS,
  });
  return data;
}

export async function getCostStatement(params: {
  project_id: string;
  period_start?: string;
  period_end?: string;
}): Promise<CostStatementResponse> {
  const { data } = await api.get('/reports/cost-statements', {
    params,
    headers: REPORTS_HEADERS,
  });
  return data;
}

export async function getOverheadCalculations(params: {
  project_id: string;
}): Promise<OverheadCalculationResponse> {
  const { data } = await api.get('/reports/overhead-calculations', {
    params,
    headers: REPORTS_HEADERS,
  });
  return data;
}

export async function getAnnualSummary(params: {
  year: number;
  project_id?: string;
}): Promise<AnnualSummaryResponse> {
  const { data } = await api.get('/reports/annual-summary', {
    params,
    headers: REPORTS_HEADERS,
  });
  return data;
}
