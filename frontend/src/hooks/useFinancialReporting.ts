import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  advanceFinancialStatement,
  createFinancialStatement,
  createUnitRecord,
  createWPDeclaration,
  getFinancialReport,
  getInstitutionalReport,
  listFinancialStatements,
  listUnitRecords,
  listWPDeclarations,
  updateUnitRecord,
  updateWPDeclaration,
} from '../services/financialReporting';

// --- Financial Statements ---

export function useFinancialStatements(
  projectId: string,
  reportingPeriodId?: string,
) {
  return useQuery({
    queryKey: ['financial-statements', projectId, reportingPeriodId],
    queryFn: () => listFinancialStatements(projectId, reportingPeriodId),
    enabled: !!projectId,
  });
}

export function useCreateFinancialStatement(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      reportingPeriodId,
      partnerId,
    }: {
      reportingPeriodId: string;
      partnerId?: string;
    }) => createFinancialStatement(projectId, reportingPeriodId, partnerId),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['financial-statements', projectId],
      });
    },
  });
}

export function useAdvanceFinancialStatement(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      statementId,
      actor,
    }: {
      statementId: string;
      actor?: string;
    }) => advanceFinancialStatement(statementId, actor),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['financial-statements', projectId],
      });
    },
  });
}

// --- WP Completion Declarations ---

export function useWPDeclarations(
  projectId: string,
  reportingPeriodId?: string,
) {
  return useQuery({
    queryKey: ['wp-declarations', projectId, reportingPeriodId],
    queryFn: () => listWPDeclarations(projectId, reportingPeriodId),
    enabled: !!projectId,
  });
}

export function useCreateWPDeclaration(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      reportingPeriodId,
      workPackageId,
      lumpSumAmount,
    }: {
      reportingPeriodId: string;
      workPackageId: string;
      lumpSumAmount: string;
    }) =>
      createWPDeclaration(
        projectId,
        reportingPeriodId,
        workPackageId,
        lumpSumAmount,
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['wp-declarations', projectId],
      });
    },
  });
}

export function useUpdateWPDeclaration(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      declarationId,
      updates,
    }: {
      declarationId: string;
      updates: Record<string, unknown>;
    }) => updateWPDeclaration(declarationId, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['wp-declarations', projectId],
      });
    },
  });
}

// --- Unit Delivery Records ---

export function useUnitRecords(
  projectId: string,
  reportingPeriodId?: string,
) {
  return useQuery({
    queryKey: ['unit-records', projectId, reportingPeriodId],
    queryFn: () => listUnitRecords(projectId, reportingPeriodId),
    enabled: !!projectId,
  });
}

export function useCreateUnitRecord(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: {
      reporting_period_id: string;
      work_package_id?: string;
      description: string;
      unit_type: string;
      planned_units: string;
      unit_rate: string;
    }) => createUnitRecord(projectId, body),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['unit-records', projectId],
      });
    },
  });
}

export function useUpdateUnitRecord(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      recordId,
      updates,
    }: {
      recordId: string;
      updates: Record<string, unknown>;
    }) => updateUnitRecord(recordId, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['unit-records', projectId],
      });
    },
  });
}

// --- Cost-Model-Aware Reports ---

export function useFinancialReport(
  projectId: string,
  reportingPeriodId?: string,
) {
  return useQuery({
    queryKey: ['financial-report', projectId, reportingPeriodId],
    queryFn: () => getFinancialReport(projectId, reportingPeriodId),
    enabled: !!projectId,
  });
}

export function useInstitutionalReport(projectId: string) {
  return useQuery({
    queryKey: ['institutional-report', projectId],
    queryFn: () => getInstitutionalReport(projectId),
    enabled: !!projectId,
  });
}
