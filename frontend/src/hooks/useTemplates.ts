import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import type { TemplateCategory } from '../types';
import {
  downloadDocument,
  generateDocument,
  getGeneratedDocument,
  getTemplate,
  listGeneratedDocuments,
  listTemplates,
  previewTemplate,
  seedTemplates,
  updateDocumentStatus,
} from '../services/templates';

// --- Template CRUD ---

export function useTemplates(category?: TemplateCategory) {
  return useQuery({
    queryKey: ['templates', category],
    queryFn: () => listTemplates(category),
  });
}

export function useTemplate(templateId: string) {
  return useQuery({
    queryKey: ['templates', templateId],
    queryFn: () => getTemplate(templateId),
    enabled: !!templateId,
  });
}

export function useSeedTemplates() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => seedTemplates(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] });
    },
  });
}

// --- Preview and Generation ---

export function useTemplatePreview(
  templateId: string,
  projectId?: string,
  researcherId?: string,
) {
  return useQuery({
    queryKey: ['template-preview', templateId, projectId, researcherId],
    queryFn: () => previewTemplate(templateId, projectId, researcherId),
    enabled: !!templateId,
  });
}

export function useGenerateDocument() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      templateId,
      projectId,
      researcherId,
      manualFields,
      generatedBy,
    }: {
      templateId: string;
      projectId?: string;
      researcherId?: string;
      manualFields?: Record<string, string>;
      generatedBy?: string;
    }) =>
      generateDocument(
        templateId,
        projectId,
        researcherId,
        manualFields,
        generatedBy,
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['generated-documents'] });
    },
  });
}

export function useDownloadDocument() {
  return useMutation({
    mutationFn: ({
      templateId,
      projectId,
      researcherId,
      manualFields,
    }: {
      templateId: string;
      projectId?: string;
      researcherId?: string;
      manualFields?: Record<string, string>;
    }) => downloadDocument(templateId, projectId, researcherId, manualFields),
  });
}

// --- Generated Documents ---

export function useGeneratedDocuments(
  projectId?: string,
  templateId?: string,
) {
  return useQuery({
    queryKey: ['generated-documents', projectId, templateId],
    queryFn: () => listGeneratedDocuments(projectId, templateId),
  });
}

export function useGeneratedDocument(docId: string) {
  return useQuery({
    queryKey: ['generated-documents', docId],
    queryFn: () => getGeneratedDocument(docId),
    enabled: !!docId,
  });
}

export function useUpdateDocumentStatus() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ docId, status }: { docId: string; status: string }) =>
      updateDocumentStatus(docId, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['generated-documents'] });
    },
  });
}
