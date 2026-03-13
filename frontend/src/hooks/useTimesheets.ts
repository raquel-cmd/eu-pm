import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as timesheetsApi from '../services/timesheets';
import type { EffortAllocationCreate, TimesheetEntryCreate } from '../types';

// --- Effort Allocations ---

export function useEffortAllocations(projectId: string) {
  return useQuery({
    queryKey: ['effort-allocations', projectId],
    queryFn: () => timesheetsApi.listEffortAllocations(projectId),
  });
}

export function useCreateEffortAllocation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      projectId,
      data,
    }: {
      projectId: string;
      data: EffortAllocationCreate;
    }) => timesheetsApi.createEffortAllocation(projectId, data),
    onSuccess: (_, { projectId }) => {
      queryClient.invalidateQueries({ queryKey: ['effort-allocations', projectId] });
      queryClient.invalidateQueries({ queryKey: ['effort-summary', projectId] });
    },
  });
}

export function useDeleteEffortAllocation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      projectId,
      allocationId,
    }: {
      projectId: string;
      allocationId: string;
    }) => timesheetsApi.deleteEffortAllocation(projectId, allocationId),
    onSuccess: (_, { projectId }) => {
      queryClient.invalidateQueries({ queryKey: ['effort-allocations', projectId] });
      queryClient.invalidateQueries({ queryKey: ['effort-summary', projectId] });
    },
  });
}

// --- Timesheet Entries ---

export function useTimesheetEntries(
  projectId: string,
  params?: { researcher_id?: string; date_from?: string; date_to?: string },
) {
  return useQuery({
    queryKey: ['timesheets', projectId, params],
    queryFn: () => timesheetsApi.listTimesheetEntries(projectId, params),
  });
}

export function useCreateTimesheetEntry() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      projectId,
      data,
    }: {
      projectId: string;
      data: TimesheetEntryCreate;
    }) => timesheetsApi.createTimesheetEntry(projectId, data),
    onSuccess: (_, { projectId }) => {
      queryClient.invalidateQueries({ queryKey: ['timesheets', projectId] });
      queryClient.invalidateQueries({ queryKey: ['effort-summary', projectId] });
    },
  });
}

export function useSubmitTimesheets() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      projectId,
      entryIds,
    }: {
      projectId: string;
      entryIds: string[];
    }) => timesheetsApi.submitTimesheets(projectId, entryIds),
    onSuccess: (_, { projectId }) => {
      queryClient.invalidateQueries({ queryKey: ['timesheets', projectId] });
    },
  });
}

export function useApproveTimesheets() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      projectId,
      entryIds,
    }: {
      projectId: string;
      entryIds: string[];
    }) => timesheetsApi.approveTimesheets(projectId, entryIds),
    onSuccess: (_, { projectId }) => {
      queryClient.invalidateQueries({ queryKey: ['timesheets', projectId] });
    },
  });
}

// --- Project Effort Summary ---

export function useProjectEffortSummary(projectId: string) {
  return useQuery({
    queryKey: ['effort-summary', projectId],
    queryFn: () => timesheetsApi.getProjectEffortSummary(projectId),
  });
}

// --- Compliance ---

export function useComplianceReport(
  projectId: string,
  periodStart: string,
  periodEnd: string,
) {
  return useQuery({
    queryKey: ['compliance', projectId, periodStart, periodEnd],
    queryFn: () => timesheetsApi.getComplianceReport(projectId, periodStart, periodEnd),
    enabled: !!periodStart && !!periodEnd,
  });
}
