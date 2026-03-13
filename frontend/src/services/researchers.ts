import api from './api';
import type {
  Researcher,
  ResearcherCreate,
  ResearcherAllocation,
  PaginatedResponse,
} from '../types';

export async function listResearchers(
  params: { project_id?: string; skip?: number; limit?: number } = {},
): Promise<PaginatedResponse<Researcher>> {
  const { data } = await api.get('/researchers', { params });
  return data;
}

export async function getResearcher(id: string): Promise<Researcher> {
  const { data } = await api.get(`/researchers/${id}`);
  return data;
}

export async function createResearcher(
  researcher: ResearcherCreate,
): Promise<Researcher> {
  const { data } = await api.post('/researchers', researcher);
  return data;
}

export async function updateResearcher(
  id: string,
  researcher: Partial<ResearcherCreate>,
): Promise<Researcher> {
  const { data } = await api.put(`/researchers/${id}`, researcher);
  return data;
}

export async function deleteResearcher(id: string): Promise<void> {
  await api.delete(`/researchers/${id}`);
}

export async function getResearcherAllocation(
  id: string,
): Promise<ResearcherAllocation> {
  const { data } = await api.get(`/researchers/${id}/allocation`);
  return data;
}
