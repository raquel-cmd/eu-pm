import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as wpApi from '../services/workPackages';
import type {
  WorkPackageCreate,
  WorkPackageUpdate,
  DeliverableCreate,
  DeliverableUpdate,
  MilestoneCreate,
  MilestoneUpdate,
} from '../types';

// --- Work Packages ---

export function useWorkPackages(projectId: string | undefined) {
  return useQuery({
    queryKey: ['work-packages', projectId],
    queryFn: () => wpApi.listWorkPackages(projectId!),
    enabled: !!projectId,
  });
}

export function useCreateWorkPackage() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      projectId,
      data,
    }: {
      projectId: string;
      data: WorkPackageCreate;
    }) => wpApi.createWorkPackage(projectId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['work-packages'] });
    },
  });
}

export function useUpdateWorkPackage() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      projectId,
      wpId,
      data,
    }: {
      projectId: string;
      wpId: string;
      data: WorkPackageUpdate;
    }) => wpApi.updateWorkPackage(projectId, wpId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['work-packages'] });
    },
  });
}

export function useDeleteWorkPackage() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      projectId,
      wpId,
    }: {
      projectId: string;
      wpId: string;
    }) => wpApi.deleteWorkPackage(projectId, wpId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['work-packages'] });
    },
  });
}

// --- Deliverables ---

export function useDeliverables(
  projectId: string | undefined,
  wpId: string | undefined,
) {
  return useQuery({
    queryKey: ['deliverables', projectId, wpId],
    queryFn: () => wpApi.listDeliverables(projectId!, wpId!),
    enabled: !!projectId && !!wpId,
  });
}

export function useCreateDeliverable() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      projectId,
      wpId,
      data,
    }: {
      projectId: string;
      wpId: string;
      data: DeliverableCreate;
    }) => wpApi.createDeliverable(projectId, wpId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['deliverables'] });
    },
  });
}

export function useUpdateDeliverable() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      projectId,
      wpId,
      deliverableId,
      data,
    }: {
      projectId: string;
      wpId: string;
      deliverableId: string;
      data: DeliverableUpdate;
    }) => wpApi.updateDeliverable(projectId, wpId, deliverableId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['deliverables'] });
    },
  });
}

export function useDeleteDeliverable() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      projectId,
      wpId,
      deliverableId,
    }: {
      projectId: string;
      wpId: string;
      deliverableId: string;
    }) => wpApi.deleteDeliverable(projectId, wpId, deliverableId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['deliverables'] });
    },
  });
}

// --- Milestones ---

export function useMilestones(
  projectId: string | undefined,
  wpId: string | undefined,
) {
  return useQuery({
    queryKey: ['milestones', projectId, wpId],
    queryFn: () => wpApi.listMilestones(projectId!, wpId!),
    enabled: !!projectId && !!wpId,
  });
}

export function useCreateMilestone() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      projectId,
      wpId,
      data,
    }: {
      projectId: string;
      wpId: string;
      data: MilestoneCreate;
    }) => wpApi.createMilestone(projectId, wpId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['milestones'] });
    },
  });
}

export function useUpdateMilestone() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      projectId,
      wpId,
      milestoneId,
      data,
    }: {
      projectId: string;
      wpId: string;
      milestoneId: string;
      data: MilestoneUpdate;
    }) => wpApi.updateMilestone(projectId, wpId, milestoneId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['milestones'] });
    },
  });
}

export function useDeleteMilestone() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      projectId,
      wpId,
      milestoneId,
    }: {
      projectId: string;
      wpId: string;
      milestoneId: string;
    }) => wpApi.deleteMilestone(projectId, wpId, milestoneId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['milestones'] });
    },
  });
}
