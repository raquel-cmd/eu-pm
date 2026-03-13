import api from './api';
import type {
  EffortAllocation,
  EffortAllocationCreate,
  TimesheetEntry,
  TimesheetEntryCreate,
  ProjectEffortSummary,
  ComplianceReport,
  PaginatedResponse,
} from '../types';

// --- Effort Allocations ---

export async function listEffortAllocations(
  projectId: string,
  params: { researcher_id?: string; skip?: number; limit?: number } = {},
): Promise<PaginatedResponse<EffortAllocation>> {
  const { data } = await api.get(
    `/projects/${projectId}/effort-allocations`,
    { params },
  );
  return data;
}

export async function createEffortAllocation(
  projectId: string,
  allocation: EffortAllocationCreate,
): Promise<EffortAllocation> {
  const { data } = await api.post(
    `/projects/${projectId}/effort-allocations`,
    allocation,
  );
  return data;
}

export async function deleteEffortAllocation(
  projectId: string,
  allocationId: string,
): Promise<void> {
  await api.delete(
    `/projects/${projectId}/effort-allocations/${allocationId}`,
  );
}

// --- Timesheet Entries ---

export async function listTimesheetEntries(
  projectId: string,
  params: {
    researcher_id?: string;
    date_from?: string;
    date_to?: string;
    skip?: number;
    limit?: number;
  } = {},
): Promise<PaginatedResponse<TimesheetEntry>> {
  const { data } = await api.get(
    `/projects/${projectId}/timesheets`,
    { params },
  );
  return data;
}

export async function createTimesheetEntry(
  projectId: string,
  entry: TimesheetEntryCreate,
): Promise<TimesheetEntry> {
  const { data } = await api.post(
    `/projects/${projectId}/timesheets`,
    entry,
  );
  return data;
}

export async function updateTimesheetEntry(
  projectId: string,
  entryId: string,
  entry: { hours?: string; description?: string },
): Promise<TimesheetEntry> {
  const { data } = await api.put(
    `/projects/${projectId}/timesheets/${entryId}`,
    entry,
  );
  return data;
}

export async function deleteTimesheetEntry(
  projectId: string,
  entryId: string,
): Promise<void> {
  await api.delete(`/projects/${projectId}/timesheets/${entryId}`);
}

export async function submitTimesheets(
  projectId: string,
  entryIds: string[],
): Promise<TimesheetEntry[]> {
  const { data } = await api.put(
    `/projects/${projectId}/timesheets/submit`,
    { entry_ids: entryIds },
  );
  return data;
}

export async function approveTimesheets(
  projectId: string,
  entryIds: string[],
): Promise<TimesheetEntry[]> {
  const { data } = await api.put(
    `/projects/${projectId}/timesheets/approve`,
    { entry_ids: entryIds },
  );
  return data;
}

// --- Project Effort Summary ---

export async function getProjectEffortSummary(
  projectId: string,
): Promise<ProjectEffortSummary> {
  const { data } = await api.get(
    `/projects/${projectId}/effort/summary`,
  );
  return data;
}

// --- Compliance ---

export async function getComplianceReport(
  projectId: string,
  periodStart: string,
  periodEnd: string,
): Promise<ComplianceReport> {
  const { data } = await api.get(
    `/projects/${projectId}/effort/compliance`,
    { params: { period_start: periodStart, period_end: periodEnd } },
  );
  return data;
}
