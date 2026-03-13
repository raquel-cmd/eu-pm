import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as researchersApi from '../services/researchers';
import type { ResearcherCreate } from '../types';

export function useResearchers(projectId?: string) {
  return useQuery({
    queryKey: ['researchers', projectId],
    queryFn: () => researchersApi.listResearchers(projectId ? { project_id: projectId } : {}),
  });
}

export function useResearcher(id: string) {
  return useQuery({
    queryKey: ['researcher', id],
    queryFn: () => researchersApi.getResearcher(id),
    enabled: !!id,
  });
}

export function useCreateResearcher() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ResearcherCreate) => researchersApi.createResearcher(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['researchers'] });
    },
  });
}

export function useUpdateResearcher() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<ResearcherCreate> }) =>
      researchersApi.updateResearcher(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['researchers'] });
    },
  });
}

export function useDeleteResearcher() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => researchersApi.deleteResearcher(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['researchers'] });
    },
  });
}

export function useResearcherAllocation(id: string) {
  return useQuery({
    queryKey: ['researcher-allocation', id],
    queryFn: () => researchersApi.getResearcherAllocation(id),
    enabled: !!id,
  });
}
