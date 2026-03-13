import { useQuery } from '@tanstack/react-query';
import * as reportsApi from '../services/reports';

export function useFinanceDashboard() {
  return useQuery({
    queryKey: ['finance-dashboard'],
    queryFn: reportsApi.getFinanceDashboard,
  });
}

export function usePMDeclarations(params: {
  project_id: string;
  period_start: string;
  period_end: string;
}) {
  return useQuery({
    queryKey: ['pm-declarations', params],
    queryFn: () => reportsApi.getPMDeclarations(params),
    enabled: !!params.project_id && !!params.period_start && !!params.period_end,
  });
}

export function useCostStatement(params: {
  project_id: string;
  period_start?: string;
  period_end?: string;
}) {
  return useQuery({
    queryKey: ['cost-statement', params],
    queryFn: () => reportsApi.getCostStatement(params),
    enabled: !!params.project_id,
  });
}

export function useOverheadCalculations(params: { project_id: string }) {
  return useQuery({
    queryKey: ['overhead-calculations', params],
    queryFn: () => reportsApi.getOverheadCalculations(params),
    enabled: !!params.project_id,
  });
}

export function useAnnualSummary(params: {
  year: number;
  project_id?: string;
}) {
  return useQuery({
    queryKey: ['annual-summary', params],
    queryFn: () => reportsApi.getAnnualSummary(params),
    enabled: !!params.year,
  });
}
