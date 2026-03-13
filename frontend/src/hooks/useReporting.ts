import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  autoGenerateReportingPeriods,
  createReportShell,
  advanceReportWorkflow,
  getReportingCalendar,
  getReportWorkflow,
  getTechnicalReport,
  listReportingPeriods,
  listTechnicalReports,
  updateReportSection,
  updateTechnicalReport,
  getPartB2Data,
  getPartB3Data,
  getPartB4Data,
  listRisks,
  createRisk,
  updateRisk,
  deleteRisk,
} from '../services/reporting';
import type { RiskCreate } from '../types';

// --- Reporting Periods ---

export function useReportingPeriods(projectId: string) {
  return useQuery({
    queryKey: ['reporting-periods', projectId],
    queryFn: () => listReportingPeriods(projectId),
    enabled: !!projectId,
  });
}

export function useAutoGeneratePeriods() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (projectId: string) =>
      autoGenerateReportingPeriods(projectId),
    onSuccess: (_data, projectId) => {
      queryClient.invalidateQueries({
        queryKey: ['reporting-periods', projectId],
      });
      queryClient.invalidateQueries({ queryKey: ['reporting-calendar'] });
    },
  });
}

// --- Reporting Calendar ---

export function useReportingCalendar(projectId?: string) {
  return useQuery({
    queryKey: ['reporting-calendar', projectId],
    queryFn: () => getReportingCalendar(projectId),
  });
}

// --- Risks ---

export function useRisks(projectId: string, status?: string) {
  return useQuery({
    queryKey: ['risks', projectId, status],
    queryFn: () => listRisks(projectId, status),
    enabled: !!projectId,
  });
}

export function useCreateRisk(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: RiskCreate) => createRisk(projectId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['risks', projectId] });
    },
  });
}

export function useUpdateRisk(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      riskId,
      data,
    }: {
      riskId: string;
      data: Partial<RiskCreate>;
    }) => updateRisk(riskId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['risks', projectId] });
    },
  });
}

export function useDeleteRisk(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (riskId: string) => deleteRisk(riskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['risks', projectId] });
    },
  });
}

// --- Technical Reports ---

export function useTechnicalReports(projectId: string) {
  return useQuery({
    queryKey: ['technical-reports', projectId],
    queryFn: () => listTechnicalReports(projectId),
    enabled: !!projectId,
  });
}

export function useTechnicalReport(reportId: string) {
  return useQuery({
    queryKey: ['technical-report', reportId],
    queryFn: () => getTechnicalReport(reportId),
    enabled: !!reportId,
  });
}

export function useCreateReportShell() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (periodId: string) => createReportShell(periodId),
    onSuccess: (data) => {
      queryClient.invalidateQueries({
        queryKey: ['technical-reports', data.project_id],
      });
    },
  });
}

export function useAdvanceWorkflow() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (reportId: string) => advanceReportWorkflow(reportId),
    onSuccess: (data) => {
      queryClient.invalidateQueries({
        queryKey: ['technical-report', data.id],
      });
      queryClient.invalidateQueries({
        queryKey: ['technical-reports', data.project_id],
      });
      queryClient.invalidateQueries({
        queryKey: ['report-workflow', data.id],
      });
    },
  });
}

export function useUpdateTechnicalReport() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      reportId,
      data,
    }: {
      reportId: string;
      data: { part_a_summary?: string; status?: string; ec_feedback?: string };
    }) => updateTechnicalReport(reportId, data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({
        queryKey: ['technical-report', data.id],
      });
    },
  });
}

export function useReportWorkflow(reportId: string) {
  return useQuery({
    queryKey: ['report-workflow', reportId],
    queryFn: () => getReportWorkflow(reportId),
    enabled: !!reportId,
  });
}

export function useUpdateReportSection() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      sectionId,
      data,
    }: {
      sectionId: string;
      data: {
        content?: Record<string, unknown>;
        narrative?: string;
        status?: string;
        assigned_to?: string;
      };
    }) => updateReportSection(sectionId, data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({
        queryKey: ['technical-report', data.technical_report_id],
      });
    },
  });
}

// --- Auto-Generated Data ---

export function usePartB2Data(reportId: string) {
  return useQuery({
    queryKey: ['part-b2', reportId],
    queryFn: () => getPartB2Data(reportId),
    enabled: !!reportId,
  });
}

export function usePartB3Data(reportId: string) {
  return useQuery({
    queryKey: ['part-b3', reportId],
    queryFn: () => getPartB3Data(reportId),
    enabled: !!reportId,
  });
}

export function usePartB4Data(reportId: string) {
  return useQuery({
    queryKey: ['part-b4', reportId],
    queryFn: () => getPartB4Data(reportId),
    enabled: !!reportId,
  });
}
