import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as partnersApi from '../services/partners';
import type {
  PartnerCreate,
  PartnerUpdate,
  ProjectPartnerCreate,
  ProjectPartnerUpdate,
} from '../types';

export function usePartners() {
  return useQuery({
    queryKey: ['partners'],
    queryFn: () => partnersApi.listPartners(),
  });
}

export function useCreatePartner() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: PartnerCreate) => partnersApi.createPartner(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['partners'] });
    },
  });
}

export function useUpdatePartner() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: PartnerUpdate }) =>
      partnersApi.updatePartner(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['partners'] });
    },
  });
}

export function useDeletePartner() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => partnersApi.deletePartner(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['partners'] });
    },
  });
}

// Project-Partner links

export function useProjectPartners(projectId: string | undefined) {
  return useQuery({
    queryKey: ['project-partners', projectId],
    queryFn: () => partnersApi.listProjectPartners(projectId!),
    enabled: !!projectId,
  });
}

export function useAddPartnerToProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      projectId,
      data,
    }: {
      projectId: string;
      data: ProjectPartnerCreate;
    }) => partnersApi.addPartnerToProject(projectId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['project-partners'] });
    },
  });
}

export function useUpdateProjectPartner() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      projectId,
      linkId,
      data,
    }: {
      projectId: string;
      linkId: string;
      data: ProjectPartnerUpdate;
    }) => partnersApi.updateProjectPartner(projectId, linkId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['project-partners'] });
    },
  });
}

export function useRemovePartnerFromProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      projectId,
      linkId,
    }: {
      projectId: string;
      linkId: string;
    }) => partnersApi.removePartnerFromProject(projectId, linkId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['project-partners'] });
    },
  });
}
