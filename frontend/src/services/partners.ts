import api from './api';
import type {
  Partner,
  PartnerCreate,
  PartnerUpdate,
  PaginatedResponse,
  ProjectPartner,
  ProjectPartnerCreate,
  ProjectPartnerUpdate,
} from '../types';

export async function listPartners(
  skip = 0,
  limit = 50,
): Promise<PaginatedResponse<Partner>> {
  const { data } = await api.get('/partners', { params: { skip, limit } });
  return data;
}

export async function getPartner(id: string): Promise<Partner> {
  const { data } = await api.get(`/partners/${id}`);
  return data;
}

export async function createPartner(partner: PartnerCreate): Promise<Partner> {
  const { data } = await api.post('/partners', partner);
  return data;
}

export async function updatePartner(
  id: string,
  partner: PartnerUpdate,
): Promise<Partner> {
  const { data } = await api.put(`/partners/${id}`, partner);
  return data;
}

export async function deletePartner(id: string): Promise<void> {
  await api.delete(`/partners/${id}`);
}

// Project-Partner links

export async function listProjectPartners(
  projectId: string,
): Promise<ProjectPartner[]> {
  const { data } = await api.get(`/projects/${projectId}/partners`);
  return data;
}

export async function addPartnerToProject(
  projectId: string,
  link: ProjectPartnerCreate,
): Promise<ProjectPartner> {
  const { data } = await api.post(`/projects/${projectId}/partners`, link);
  return data;
}

export async function updateProjectPartner(
  projectId: string,
  linkId: string,
  update: ProjectPartnerUpdate,
): Promise<ProjectPartner> {
  const { data } = await api.put(
    `/projects/${projectId}/partners/${linkId}`,
    update,
  );
  return data;
}

export async function removePartnerFromProject(
  projectId: string,
  linkId: string,
): Promise<void> {
  await api.delete(`/projects/${projectId}/partners/${linkId}`);
}
