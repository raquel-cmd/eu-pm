import api from './api';
import type {
  Project,
  ProjectCreate,
  ProjectUpdate,
  PaginatedResponse,
  ProjectStatus,
  Programme,
  CostModel,
  ProjectRole,
} from '../types';

interface ListProjectsParams {
  status?: ProjectStatus;
  programme?: Programme;
  cost_model?: CostModel;
  role?: ProjectRole;
  skip?: number;
  limit?: number;
}

export async function listProjects(
  params: ListProjectsParams = {},
): Promise<PaginatedResponse<Project>> {
  const { data } = await api.get('/projects', { params });
  return data;
}

export async function getProject(id: string): Promise<Project> {
  const { data } = await api.get(`/projects/${id}`);
  return data;
}

export async function createProject(project: ProjectCreate): Promise<Project> {
  const { data } = await api.post('/projects', project);
  return data;
}

export async function updateProject(
  id: string,
  project: ProjectUpdate,
): Promise<Project> {
  const { data } = await api.put(`/projects/${id}`, project);
  return data;
}

export async function deleteProject(id: string): Promise<void> {
  await api.delete(`/projects/${id}`);
}
