import api from './api';
import type {
  WorkPackage,
  WorkPackageCreate,
  WorkPackageUpdate,
  Deliverable,
  DeliverableCreate,
  DeliverableUpdate,
  Milestone,
  MilestoneCreate,
  MilestoneUpdate,
  PaginatedResponse,
} from '../types';

// --- Work Packages ---

export async function listWorkPackages(
  projectId: string,
): Promise<PaginatedResponse<WorkPackage>> {
  const { data } = await api.get(`/projects/${projectId}/work-packages`);
  return data;
}

export async function getWorkPackage(
  projectId: string,
  wpId: string,
): Promise<WorkPackage> {
  const { data } = await api.get(
    `/projects/${projectId}/work-packages/${wpId}`,
  );
  return data;
}

export async function createWorkPackage(
  projectId: string,
  wp: WorkPackageCreate,
): Promise<WorkPackage> {
  const { data } = await api.post(
    `/projects/${projectId}/work-packages`,
    wp,
  );
  return data;
}

export async function updateWorkPackage(
  projectId: string,
  wpId: string,
  wp: WorkPackageUpdate,
): Promise<WorkPackage> {
  const { data } = await api.put(
    `/projects/${projectId}/work-packages/${wpId}`,
    wp,
  );
  return data;
}

export async function deleteWorkPackage(
  projectId: string,
  wpId: string,
): Promise<void> {
  await api.delete(`/projects/${projectId}/work-packages/${wpId}`);
}

// --- Deliverables ---

export async function listDeliverables(
  projectId: string,
  wpId: string,
): Promise<PaginatedResponse<Deliverable>> {
  const { data } = await api.get(
    `/projects/${projectId}/work-packages/${wpId}/deliverables`,
  );
  return data;
}

export async function createDeliverable(
  projectId: string,
  wpId: string,
  deliverable: DeliverableCreate,
): Promise<Deliverable> {
  const { data } = await api.post(
    `/projects/${projectId}/work-packages/${wpId}/deliverables`,
    deliverable,
  );
  return data;
}

export async function updateDeliverable(
  projectId: string,
  wpId: string,
  deliverableId: string,
  deliverable: DeliverableUpdate,
): Promise<Deliverable> {
  const { data } = await api.put(
    `/projects/${projectId}/work-packages/${wpId}/deliverables/${deliverableId}`,
    deliverable,
  );
  return data;
}

export async function deleteDeliverable(
  projectId: string,
  wpId: string,
  deliverableId: string,
): Promise<void> {
  await api.delete(
    `/projects/${projectId}/work-packages/${wpId}/deliverables/${deliverableId}`,
  );
}

// --- Milestones ---

export async function listMilestones(
  projectId: string,
  wpId: string,
): Promise<PaginatedResponse<Milestone>> {
  const { data } = await api.get(
    `/projects/${projectId}/work-packages/${wpId}/milestones`,
  );
  return data;
}

export async function createMilestone(
  projectId: string,
  wpId: string,
  milestone: MilestoneCreate,
): Promise<Milestone> {
  const { data } = await api.post(
    `/projects/${projectId}/work-packages/${wpId}/milestones`,
    milestone,
  );
  return data;
}

export async function updateMilestone(
  projectId: string,
  wpId: string,
  milestoneId: string,
  milestone: MilestoneUpdate,
): Promise<Milestone> {
  const { data } = await api.put(
    `/projects/${projectId}/work-packages/${wpId}/milestones/${milestoneId}`,
    milestone,
  );
  return data;
}

export async function deleteMilestone(
  projectId: string,
  wpId: string,
  milestoneId: string,
): Promise<void> {
  await api.delete(
    `/projects/${projectId}/work-packages/${wpId}/milestones/${milestoneId}`,
  );
}
