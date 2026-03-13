import api from './api';
import type { Mission, MissionCreate, MissionComplete, PaginatedResponse } from '../types';

export async function listMissions(
  projectId: string,
  params: { skip?: number; limit?: number } = {},
): Promise<PaginatedResponse<Mission>> {
  const { data } = await api.get(`/projects/${projectId}/missions`, { params });
  return data;
}

export async function createMission(
  projectId: string,
  mission: MissionCreate,
): Promise<Mission> {
  const { data } = await api.post(`/projects/${projectId}/missions`, mission);
  return data;
}

export async function approveMission(
  projectId: string,
  missionId: string,
  notes?: string,
): Promise<Mission> {
  const { data } = await api.put(`/projects/${projectId}/missions/${missionId}/approve`, {
    approval_notes: notes || null,
  });
  return data;
}

export async function completeMission(
  projectId: string,
  missionId: string,
  completion: MissionComplete,
): Promise<Mission> {
  const { data } = await api.put(
    `/projects/${projectId}/missions/${missionId}/complete`,
    completion,
  );
  return data;
}

export async function cancelMission(
  projectId: string,
  missionId: string,
): Promise<Mission> {
  const { data } = await api.put(`/projects/${projectId}/missions/${missionId}/cancel`);
  return data;
}

export async function deleteMission(
  projectId: string,
  missionId: string,
): Promise<void> {
  await api.delete(`/projects/${projectId}/missions/${missionId}`);
}
