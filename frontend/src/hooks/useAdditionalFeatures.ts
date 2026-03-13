import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  listIPAssets,
  createIPAsset,
  updateIPAsset,
  deleteIPAsset,
  listDisseminationActivities,
  createDisseminationActivity,
  updateDisseminationActivity,
  deleteDisseminationActivity,
  listKPIDefinitions,
  createKPIDefinition,
  updateKPIDefinition,
  deleteKPIDefinition,
  listKPIValues,
  createKPIValue,
  updateKPIValue,
  deleteKPIValue,
  listEthicsRequirements,
  createEthicsRequirement,
  updateEthicsRequirement,
  deleteEthicsRequirement,
  listDataManagementRecords,
  createDataManagementRecord,
  updateDataManagementRecord,
  deleteDataManagementRecord,
  listCollaborationRecords,
  createCollaborationRecord,
  updateCollaborationRecord,
  deleteCollaborationRecord,
  listAmendments,
  createAmendment,
  updateAmendment,
  deleteAmendment,
  listNotifications,
  createNotification,
  markNotificationRead,
  dismissNotification,
  deleteNotification,
} from '../services/additionalFeatures';
import type { IPAsset, DisseminationActivity, Amendment, Notification } from '../types';

// 9.1 IP Assets
export const useIPAssets = (projectId: string, status?: string) =>
  useQuery({
    queryKey: ['ip-assets', projectId, status],
    queryFn: () => listIPAssets(projectId, status),
    enabled: !!projectId,
  });

export const useCreateIPAsset = (projectId: string) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: Partial<IPAsset>) => createIPAsset(projectId, body),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['ip-assets', projectId] }),
  });
};

export const useUpdateIPAsset = (projectId: string) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...body }: Partial<IPAsset> & { id: string }) =>
      updateIPAsset(id, body),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['ip-assets', projectId] }),
  });
};

export const useDeleteIPAsset = (projectId: string) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteIPAsset(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['ip-assets', projectId] }),
  });
};

// 9.3 Dissemination Activities
export const useDisseminationActivities = (
  projectId: string,
  activityType?: string,
) =>
  useQuery({
    queryKey: ['dissemination-activities', projectId, activityType],
    queryFn: () => listDisseminationActivities(projectId, activityType),
    enabled: !!projectId,
  });

export const useCreateDisseminationActivity = (projectId: string) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: Partial<DisseminationActivity>) =>
      createDisseminationActivity(projectId, body),
    onSuccess: () =>
      qc.invalidateQueries({
        queryKey: ['dissemination-activities', projectId],
      }),
  });
};

export const useUpdateDisseminationActivity = (projectId: string) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      ...body
    }: Partial<DisseminationActivity> & { id: string }) =>
      updateDisseminationActivity(id, body),
    onSuccess: () =>
      qc.invalidateQueries({
        queryKey: ['dissemination-activities', projectId],
      }),
  });
};

export const useDeleteDisseminationActivity = (projectId: string) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteDisseminationActivity(id),
    onSuccess: () =>
      qc.invalidateQueries({
        queryKey: ['dissemination-activities', projectId],
      }),
  });
};

// 9.4 KPI Definitions
export const useKPIDefinitions = (programme?: string) =>
  useQuery({
    queryKey: ['kpi-definitions', programme],
    queryFn: () => listKPIDefinitions(programme),
  });

export const useCreateKPIDefinition = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createKPIDefinition,
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: ['kpi-definitions'] }),
  });
};

export const useUpdateKPIDefinition = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...body }: Partial<{ id: string } & Record<string, unknown>>) =>
      updateKPIDefinition(id!, body),
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: ['kpi-definitions'] }),
  });
};

export const useDeleteKPIDefinition = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteKPIDefinition(id),
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: ['kpi-definitions'] }),
  });
};

// 9.4 KPI Values
export const useKPIValues = (projectId: string, kpiDefinitionId?: string) =>
  useQuery({
    queryKey: ['kpi-values', projectId, kpiDefinitionId],
    queryFn: () => listKPIValues(projectId, kpiDefinitionId),
    enabled: !!projectId,
  });

export const useCreateKPIValue = (projectId: string) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: Partial<Record<string, unknown>>) =>
      createKPIValue(projectId, body),
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: ['kpi-values', projectId] }),
  });
};

export const useUpdateKPIValue = (projectId: string) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...body }: { id: string } & Record<string, unknown>) =>
      updateKPIValue(id, body),
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: ['kpi-values', projectId] }),
  });
};

export const useDeleteKPIValue = (projectId: string) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteKPIValue(id),
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: ['kpi-values', projectId] }),
  });
};

// 9.5 Ethics Requirements
export const useEthicsRequirements = (projectId: string) =>
  useQuery({
    queryKey: ['ethics-requirements', projectId],
    queryFn: () => listEthicsRequirements(projectId),
    enabled: !!projectId,
  });

export const useCreateEthicsRequirement = (projectId: string) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: Partial<Record<string, unknown>>) =>
      createEthicsRequirement(projectId, body),
    onSuccess: () =>
      qc.invalidateQueries({
        queryKey: ['ethics-requirements', projectId],
      }),
  });
};

export const useUpdateEthicsRequirement = (projectId: string) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...body }: { id: string } & Record<string, unknown>) =>
      updateEthicsRequirement(id, body),
    onSuccess: () =>
      qc.invalidateQueries({
        queryKey: ['ethics-requirements', projectId],
      }),
  });
};

export const useDeleteEthicsRequirement = (projectId: string) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteEthicsRequirement(id),
    onSuccess: () =>
      qc.invalidateQueries({
        queryKey: ['ethics-requirements', projectId],
      }),
  });
};

// 9.5 Data Management Records
export const useDataManagementRecords = (projectId: string) =>
  useQuery({
    queryKey: ['data-management-records', projectId],
    queryFn: () => listDataManagementRecords(projectId),
    enabled: !!projectId,
  });

export const useCreateDataManagementRecord = (projectId: string) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: Partial<Record<string, unknown>>) =>
      createDataManagementRecord(projectId, body),
    onSuccess: () =>
      qc.invalidateQueries({
        queryKey: ['data-management-records', projectId],
      }),
  });
};

export const useUpdateDataManagementRecord = (projectId: string) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...body }: { id: string } & Record<string, unknown>) =>
      updateDataManagementRecord(id, body),
    onSuccess: () =>
      qc.invalidateQueries({
        queryKey: ['data-management-records', projectId],
      }),
  });
};

export const useDeleteDataManagementRecord = (projectId: string) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteDataManagementRecord(id),
    onSuccess: () =>
      qc.invalidateQueries({
        queryKey: ['data-management-records', projectId],
      }),
  });
};

// 9.6 Collaboration Records
export const useCollaborationRecords = (
  partnerId?: string,
  projectId?: string,
) =>
  useQuery({
    queryKey: ['collaboration-records', partnerId, projectId],
    queryFn: () => listCollaborationRecords(partnerId, projectId),
  });

export const useCreateCollaborationRecord = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createCollaborationRecord,
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: ['collaboration-records'] }),
  });
};

export const useUpdateCollaborationRecord = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...body }: { id: string } & Record<string, unknown>) =>
      updateCollaborationRecord(id, body),
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: ['collaboration-records'] }),
  });
};

export const useDeleteCollaborationRecord = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteCollaborationRecord(id),
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: ['collaboration-records'] }),
  });
};

// 9.7 Amendments
export const useAmendments = (projectId: string) =>
  useQuery({
    queryKey: ['amendments', projectId],
    queryFn: () => listAmendments(projectId),
    enabled: !!projectId,
  });

export const useCreateAmendment = (projectId: string) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: Partial<Amendment>) =>
      createAmendment(projectId, body),
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: ['amendments', projectId] }),
  });
};

export const useUpdateAmendment = (projectId: string) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...body }: Partial<Amendment> & { id: string }) =>
      updateAmendment(id, body),
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: ['amendments', projectId] }),
  });
};

export const useDeleteAmendment = (projectId: string) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteAmendment(id),
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: ['amendments', projectId] }),
  });
};

// 9.8 Notifications
export const useNotifications = (
  projectId?: string,
  status?: string,
  recipientEmail?: string,
) =>
  useQuery({
    queryKey: ['notifications', projectId, status, recipientEmail],
    queryFn: () => listNotifications(projectId, status, recipientEmail),
  });

export const useCreateNotification = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createNotification,
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: ['notifications'] }),
  });
};

export const useMarkNotificationRead = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => markNotificationRead(id),
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: ['notifications'] }),
  });
};

export const useDismissNotification = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => dismissNotification(id),
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: ['notifications'] }),
  });
};

export const useDeleteNotification = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteNotification(id),
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: ['notifications'] }),
  });
};
