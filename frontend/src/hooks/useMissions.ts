import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as missionsApi from '../services/missions';
import type { MissionCreate, MissionComplete } from '../types';

export function useMissions(projectId: string) {
  return useQuery({
    queryKey: ['missions', projectId],
    queryFn: () => missionsApi.listMissions(projectId),
  });
}

export function useCreateMission() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ projectId, data }: { projectId: string; data: MissionCreate }) =>
      missionsApi.createMission(projectId, data),
    onSuccess: (_, { projectId }) => {
      queryClient.invalidateQueries({ queryKey: ['missions', projectId] });
    },
  });
}

export function useApproveMission() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      projectId,
      missionId,
      notes,
    }: {
      projectId: string;
      missionId: string;
      notes?: string;
    }) => missionsApi.approveMission(projectId, missionId, notes),
    onSuccess: (_, { projectId }) => {
      queryClient.invalidateQueries({ queryKey: ['missions', projectId] });
    },
  });
}

export function useCompleteMission() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      projectId,
      missionId,
      data,
    }: {
      projectId: string;
      missionId: string;
      data: MissionComplete;
    }) => missionsApi.completeMission(projectId, missionId, data),
    onSuccess: (_, { projectId }) => {
      queryClient.invalidateQueries({ queryKey: ['missions', projectId] });
    },
  });
}

export function useCancelMission() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ projectId, missionId }: { projectId: string; missionId: string }) =>
      missionsApi.cancelMission(projectId, missionId),
    onSuccess: (_, { projectId }) => {
      queryClient.invalidateQueries({ queryKey: ['missions', projectId] });
    },
  });
}

export function useDeleteMission() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ projectId, missionId }: { projectId: string; missionId: string }) =>
      missionsApi.deleteMission(projectId, missionId),
    onSuccess: (_, { projectId }) => {
      queryClient.invalidateQueries({ queryKey: ['missions', projectId] });
    },
  });
}
