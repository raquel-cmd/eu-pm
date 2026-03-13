/**
 * API service functions for role-based dashboards (Section 10).
 */
import api from './api';
import type {
  PIDashboardResponse,
  ProjectDashboardResponse,
  ResearcherDashboardResponse,
} from '../types';

export async function fetchPIDashboard(): Promise<PIDashboardResponse> {
  const { data } = await api.get<PIDashboardResponse>('/dashboards/pi');
  return data;
}

export async function fetchResearcherDashboard(
  researcherId: string,
): Promise<ResearcherDashboardResponse> {
  const { data } = await api.get<ResearcherDashboardResponse>(
    `/dashboards/researcher/${researcherId}`,
  );
  return data;
}

export async function fetchProjectDashboard(
  projectId: string,
): Promise<ProjectDashboardResponse> {
  const { data } = await api.get<ProjectDashboardResponse>(
    `/dashboards/project/${projectId}`,
  );
  return data;
}
