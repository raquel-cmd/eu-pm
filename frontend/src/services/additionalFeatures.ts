import api from './api';
import type {
  IPAsset,
  IPAssetListResponse,
  DisseminationActivity,
  DisseminationActivityListResponse,
  KPIDefinition,
  KPIDefinitionListResponse,
  KPIValue,
  KPIValueListResponse,
  EthicsRequirement,
  EthicsRequirementListResponse,
  DataManagementRecord,
  DataManagementRecordListResponse,
  CollaborationRecord,
  CollaborationRecordListResponse,
  Amendment,
  AmendmentListResponse,
  Notification,
  NotificationListResponse,
} from '../types';

// 9.1 IP Assets
export const listIPAssets = async (projectId: string, status?: string) => {
  const params: Record<string, string> = {};
  if (status) params.status = status;
  const { data } = await api.get<IPAssetListResponse>(
    `/projects/${projectId}/ip-assets`,
    { params },
  );
  return data;
};

export const getIPAsset = async (assetId: string) => {
  const { data } = await api.get<IPAsset>(`/ip-assets/${assetId}`);
  return data;
};

export const createIPAsset = async (
  projectId: string,
  body: Partial<IPAsset>,
) => {
  const { data } = await api.post<IPAsset>(
    `/projects/${projectId}/ip-assets`,
    body,
  );
  return data;
};

export const updateIPAsset = async (
  assetId: string,
  body: Partial<IPAsset>,
) => {
  const { data } = await api.put<IPAsset>(`/ip-assets/${assetId}`, body);
  return data;
};

export const deleteIPAsset = async (assetId: string) => {
  await api.delete(`/ip-assets/${assetId}`);
};

// 9.3 Dissemination Activities
export const listDisseminationActivities = async (
  projectId: string,
  activityType?: string,
) => {
  const params: Record<string, string> = {};
  if (activityType) params.activity_type = activityType;
  const { data } = await api.get<DisseminationActivityListResponse>(
    `/projects/${projectId}/dissemination-activities`,
    { params },
  );
  return data;
};

export const getDisseminationActivity = async (activityId: string) => {
  const { data } = await api.get<DisseminationActivity>(
    `/dissemination-activities/${activityId}`,
  );
  return data;
};

export const createDisseminationActivity = async (
  projectId: string,
  body: Partial<DisseminationActivity>,
) => {
  const { data } = await api.post<DisseminationActivity>(
    `/projects/${projectId}/dissemination-activities`,
    body,
  );
  return data;
};

export const updateDisseminationActivity = async (
  activityId: string,
  body: Partial<DisseminationActivity>,
) => {
  const { data } = await api.put<DisseminationActivity>(
    `/dissemination-activities/${activityId}`,
    body,
  );
  return data;
};

export const deleteDisseminationActivity = async (activityId: string) => {
  await api.delete(`/dissemination-activities/${activityId}`);
};

// 9.4 KPI Definitions
export const listKPIDefinitions = async (programme?: string) => {
  const params: Record<string, string> = {};
  if (programme) params.programme = programme;
  const { data } = await api.get<KPIDefinitionListResponse>(
    '/kpi-definitions',
    { params },
  );
  return data;
};

export const getKPIDefinition = async (defnId: string) => {
  const { data } = await api.get<KPIDefinition>(
    `/kpi-definitions/${defnId}`,
  );
  return data;
};

export const createKPIDefinition = async (body: Partial<KPIDefinition>) => {
  const { data } = await api.post<KPIDefinition>('/kpi-definitions', body);
  return data;
};

export const updateKPIDefinition = async (
  defnId: string,
  body: Partial<KPIDefinition>,
) => {
  const { data } = await api.put<KPIDefinition>(
    `/kpi-definitions/${defnId}`,
    body,
  );
  return data;
};

export const deleteKPIDefinition = async (defnId: string) => {
  await api.delete(`/kpi-definitions/${defnId}`);
};

// 9.4 KPI Values
export const listKPIValues = async (
  projectId: string,
  kpiDefinitionId?: string,
) => {
  const params: Record<string, string> = {};
  if (kpiDefinitionId) params.kpi_definition_id = kpiDefinitionId;
  const { data } = await api.get<KPIValueListResponse>(
    `/projects/${projectId}/kpi-values`,
    { params },
  );
  return data;
};

export const createKPIValue = async (
  projectId: string,
  body: Partial<KPIValue>,
) => {
  const { data } = await api.post<KPIValue>(
    `/projects/${projectId}/kpi-values`,
    body,
  );
  return data;
};

export const updateKPIValue = async (
  valueId: string,
  body: Partial<KPIValue>,
) => {
  const { data } = await api.put<KPIValue>(`/kpi-values/${valueId}`, body);
  return data;
};

export const deleteKPIValue = async (valueId: string) => {
  await api.delete(`/kpi-values/${valueId}`);
};

// 9.5 Ethics Requirements
export const listEthicsRequirements = async (projectId: string) => {
  const { data } = await api.get<EthicsRequirementListResponse>(
    `/projects/${projectId}/ethics-requirements`,
  );
  return data;
};

export const createEthicsRequirement = async (
  projectId: string,
  body: Partial<EthicsRequirement>,
) => {
  const { data } = await api.post<EthicsRequirement>(
    `/projects/${projectId}/ethics-requirements`,
    body,
  );
  return data;
};

export const updateEthicsRequirement = async (
  reqId: string,
  body: Partial<EthicsRequirement>,
) => {
  const { data } = await api.put<EthicsRequirement>(
    `/ethics-requirements/${reqId}`,
    body,
  );
  return data;
};

export const deleteEthicsRequirement = async (reqId: string) => {
  await api.delete(`/ethics-requirements/${reqId}`);
};

// 9.5 Data Management Records
export const listDataManagementRecords = async (projectId: string) => {
  const { data } = await api.get<DataManagementRecordListResponse>(
    `/projects/${projectId}/data-management-records`,
  );
  return data;
};

export const createDataManagementRecord = async (
  projectId: string,
  body: Partial<DataManagementRecord>,
) => {
  const { data } = await api.post<DataManagementRecord>(
    `/projects/${projectId}/data-management-records`,
    body,
  );
  return data;
};

export const updateDataManagementRecord = async (
  recordId: string,
  body: Partial<DataManagementRecord>,
) => {
  const { data } = await api.put<DataManagementRecord>(
    `/data-management-records/${recordId}`,
    body,
  );
  return data;
};

export const deleteDataManagementRecord = async (recordId: string) => {
  await api.delete(`/data-management-records/${recordId}`);
};

// 9.6 Collaboration Records
export const listCollaborationRecords = async (
  partnerId?: string,
  projectId?: string,
) => {
  const params: Record<string, string> = {};
  if (partnerId) params.partner_id = partnerId;
  if (projectId) params.project_id = projectId;
  const { data } = await api.get<CollaborationRecordListResponse>(
    '/collaboration-records',
    { params },
  );
  return data;
};

export const createCollaborationRecord = async (
  body: Partial<CollaborationRecord>,
) => {
  const { data } = await api.post<CollaborationRecord>(
    '/collaboration-records',
    body,
  );
  return data;
};

export const updateCollaborationRecord = async (
  recordId: string,
  body: Partial<CollaborationRecord>,
) => {
  const { data } = await api.put<CollaborationRecord>(
    `/collaboration-records/${recordId}`,
    body,
  );
  return data;
};

export const deleteCollaborationRecord = async (recordId: string) => {
  await api.delete(`/collaboration-records/${recordId}`);
};

// 9.7 Amendments
export const listAmendments = async (projectId: string) => {
  const { data } = await api.get<AmendmentListResponse>(
    `/projects/${projectId}/amendments`,
  );
  return data;
};

export const getAmendment = async (amendmentId: string) => {
  const { data } = await api.get<Amendment>(
    `/amendments/${amendmentId}`,
  );
  return data;
};

export const createAmendment = async (
  projectId: string,
  body: Partial<Amendment>,
) => {
  const { data } = await api.post<Amendment>(
    `/projects/${projectId}/amendments`,
    body,
  );
  return data;
};

export const updateAmendment = async (
  amendmentId: string,
  body: Partial<Amendment>,
) => {
  const { data } = await api.put<Amendment>(
    `/amendments/${amendmentId}`,
    body,
  );
  return data;
};

export const deleteAmendment = async (amendmentId: string) => {
  await api.delete(`/amendments/${amendmentId}`);
};

// 9.8 Notifications
export const listNotifications = async (
  projectId?: string,
  status?: string,
  recipientEmail?: string,
) => {
  const params: Record<string, string> = {};
  if (projectId) params.project_id = projectId;
  if (status) params.status = status;
  if (recipientEmail) params.recipient_email = recipientEmail;
  const { data } = await api.get<NotificationListResponse>(
    '/notifications',
    { params },
  );
  return data;
};

export const createNotification = async (body: Partial<Notification>) => {
  const { data } = await api.post<Notification>('/notifications', body);
  return data;
};

export const updateNotification = async (
  notificationId: string,
  body: Partial<Notification>,
) => {
  const { data } = await api.put<Notification>(
    `/notifications/${notificationId}`,
    body,
  );
  return data;
};

export const markNotificationRead = async (notificationId: string) => {
  const { data } = await api.post<Notification>(
    `/notifications/${notificationId}/read`,
  );
  return data;
};

export const markNotificationSent = async (notificationId: string) => {
  const { data } = await api.post<Notification>(
    `/notifications/${notificationId}/send`,
  );
  return data;
};

export const dismissNotification = async (notificationId: string) => {
  const { data } = await api.post<Notification>(
    `/notifications/${notificationId}/dismiss`,
  );
  return data;
};

export const deleteNotification = async (notificationId: string) => {
  await api.delete(`/notifications/${notificationId}`);
};
