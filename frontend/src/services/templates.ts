import api from './api';
import type {
  DocumentTemplate,
  GeneratedDocument,
  TemplateCategory,
  TemplatePreviewResponse,
} from '../types';

// --- Template CRUD ---

export async function seedTemplates(): Promise<{ seeded: number }> {
  const { data } = await api.post('/templates/seed');
  return data;
}

export async function listTemplates(
  category?: TemplateCategory,
): Promise<DocumentTemplate[]> {
  const params: Record<string, string> = {};
  if (category) params.category = category;
  const { data } = await api.get('/templates', { params });
  return data;
}

export async function getTemplate(
  templateId: string,
): Promise<DocumentTemplate> {
  const { data } = await api.get(`/templates/${templateId}`);
  return data;
}

// --- Preview and Generation ---

export async function previewTemplate(
  templateId: string,
  projectId?: string,
  researcherId?: string,
): Promise<TemplatePreviewResponse> {
  const { data } = await api.post(`/templates/${templateId}/preview`, {
    project_id: projectId,
    researcher_id: researcherId,
  });
  return data;
}

export async function generateDocument(
  templateId: string,
  projectId?: string,
  researcherId?: string,
  manualFields?: Record<string, string>,
  generatedBy?: string,
): Promise<GeneratedDocument> {
  const { data } = await api.post('/templates/generate', {
    template_id: templateId,
    project_id: projectId,
    researcher_id: researcherId,
    manual_fields: manualFields,
    generated_by: generatedBy,
  });
  return data;
}

export async function downloadDocument(
  templateId: string,
  projectId?: string,
  researcherId?: string,
  manualFields?: Record<string, string>,
): Promise<Blob> {
  const { data } = await api.post(
    `/templates/${templateId}/download`,
    {
      project_id: projectId,
      researcher_id: researcherId,
      manual_fields: manualFields,
    },
    { responseType: 'blob' },
  );
  return data;
}

// --- Generated Documents ---

export async function listGeneratedDocuments(
  projectId?: string,
  templateId?: string,
): Promise<{ items: GeneratedDocument[]; total: number }> {
  const params: Record<string, string> = {};
  if (projectId) params.project_id = projectId;
  if (templateId) params.template_id = templateId;
  const { data } = await api.get('/templates/documents/list', { params });
  return data;
}

export async function getGeneratedDocument(
  docId: string,
): Promise<GeneratedDocument> {
  const { data } = await api.get(`/templates/documents/${docId}`);
  return data;
}

export async function updateDocumentStatus(
  docId: string,
  status: string,
): Promise<GeneratedDocument> {
  const { data } = await api.put(`/templates/documents/${docId}/status`, {
    status,
  });
  return data;
}
