import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  useTemplate,
  useTemplatePreview,
  useGenerateDocument,
  useDownloadDocument,
} from '../hooks/useTemplates';
import { useProjects } from '../hooks/useProjects';
import { useResearchers } from '../hooks/useResearchers';
import {
  TEMPLATE_CATEGORY_LABELS,
  PERSONNEL_TEMPLATE_TYPE_LABELS,
  GeneratedDocumentStatus,
} from '../types';
import type { TemplateFieldPreview } from '../types';

function FieldInput({
  field,
  value,
  onChange,
}: {
  field: TemplateFieldPreview;
  value: string;
  onChange: (val: string) => void;
}) {
  const isAuto = field.field_type === 'auto';

  if (field.input_type === 'textarea') {
    return (
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {field.label}
          {field.required && <span className="text-red-500 ml-1">*</span>}
          {isAuto && (
            <span className="ml-2 text-xs text-green-600 font-normal">
              Auto-populated
            </span>
          )}
        </label>
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={isAuto}
          rows={3}
          className={`w-full rounded-md border px-3 py-2 text-sm ${
            isAuto
              ? 'bg-gray-50 border-gray-200 text-gray-600'
              : 'border-gray-300 focus:border-blue-500 focus:ring-1 focus:ring-blue-500'
          }`}
        />
        {field.help_text && (
          <p className="mt-1 text-xs text-gray-500">{field.help_text}</p>
        )}
      </div>
    );
  }

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {field.label}
        {field.required && <span className="text-red-500 ml-1">*</span>}
        {isAuto && (
          <span className="ml-2 text-xs text-green-600 font-normal">
            Auto-populated
          </span>
        )}
      </label>
      <input
        type={field.input_type === 'number' ? 'number' : 'text'}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={isAuto}
        className={`w-full rounded-md border px-3 py-2 text-sm ${
          isAuto
            ? 'bg-gray-50 border-gray-200 text-gray-600'
            : 'border-gray-300 focus:border-blue-500 focus:ring-1 focus:ring-blue-500'
        }`}
      />
      {field.help_text && (
        <p className="mt-1 text-xs text-gray-500">{field.help_text}</p>
      )}
    </div>
  );
}

export default function TemplateFillPage() {
  const { templateId } = useParams<{ templateId: string }>();
  const navigate = useNavigate();

  const [selectedProjectId, setSelectedProjectId] = useState<string>('');
  const [selectedResearcherId, setSelectedResearcherId] = useState<string>('');
  const [manualValues, setManualValues] = useState<Record<string, string>>({});
  const [successMsg, setSuccessMsg] = useState('');

  const { data: template, isLoading: templateLoading } = useTemplate(templateId!);
  const { data: projects } = useProjects();
  const { data: researchers } = useResearchers();

  const { data: preview, isLoading: previewLoading } = useTemplatePreview(
    templateId!,
    selectedProjectId || undefined,
    selectedResearcherId || undefined,
  );

  const generateMutation = useGenerateDocument();
  const downloadMutation = useDownloadDocument();

  // Sync auto-populated values from preview into manual values for display
  useEffect(() => {
    if (!preview) return;
    const newValues: Record<string, string> = {};
    for (const field of preview.fields) {
      if (field.field_type === 'auto' && field.value) {
        newValues[field.name] = field.value;
      }
    }
    setManualValues((prev) => ({ ...newValues, ...prev }));
  }, [preview]);

  function handleManualChange(name: string, value: string) {
    setManualValues((prev) => ({ ...prev, [name]: value }));
  }

  function getManualFieldValues(): Record<string, string> {
    if (!preview) return {};
    const manual: Record<string, string> = {};
    for (const field of preview.fields) {
      if (field.field_type === 'manual' && manualValues[field.name]) {
        manual[field.name] = manualValues[field.name];
      }
    }
    return manual;
  }

  function handleGenerate() {
    generateMutation.mutate(
      {
        templateId: templateId!,
        projectId: selectedProjectId || undefined,
        researcherId: selectedResearcherId || undefined,
        manualFields: getManualFieldValues(),
        generatedBy: 'Web UI',
      },
      {
        onSuccess: () => {
          setSuccessMsg('Document generated and saved successfully.');
        },
      },
    );
  }

  function handleDownload() {
    downloadMutation.mutate(
      {
        templateId: templateId!,
        projectId: selectedProjectId || undefined,
        researcherId: selectedResearcherId || undefined,
        manualFields: getManualFieldValues(),
      },
      {
        onSuccess: (blob) => {
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `${template?.slug || 'document'}.docx`;
          a.click();
          URL.revokeObjectURL(url);
        },
      },
    );
  }

  if (templateLoading) {
    return <div className="text-center py-12 text-gray-500">Loading template...</div>;
  }

  if (!template) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 mb-4">Template not found.</p>
        <Link to="/templates" className="text-blue-700 hover:underline">
          Back to library
        </Link>
      </div>
    );
  }

  const autoFields = preview?.fields.filter((f) => f.field_type === 'auto') || [];
  const manualFields = preview?.fields.filter((f) => f.field_type === 'manual') || [];

  return (
    <div className="max-w-3xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <Link
          to="/templates"
          className="text-sm text-blue-700 hover:underline mb-2 inline-block"
        >
          &larr; Back to library
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">{template.name}</h1>
        <div className="flex items-center gap-3 mt-1">
          <span className="text-sm text-gray-500">
            {TEMPLATE_CATEGORY_LABELS[template.category]}
          </span>
          {template.personnel_type && (
            <span className="text-sm text-gray-500">
              &middot; {PERSONNEL_TEMPLATE_TYPE_LABELS[template.personnel_type]}
            </span>
          )}
          <span className="text-sm text-gray-500">&middot; v{template.version}</span>
        </div>
        {template.description && (
          <p className="text-sm text-gray-600 mt-2">{template.description}</p>
        )}
      </div>

      {/* Context selectors */}
      <div className="bg-white border border-gray-200 rounded-lg p-5 mb-6">
        <h2 className="text-sm font-semibold text-gray-900 mb-4">
          Select Context
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Project
            </label>
            <select
              value={selectedProjectId}
              onChange={(e) => setSelectedProjectId(e.target.value)}
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm
                focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            >
              <option value="">-- Select project --</option>
              {projects?.items?.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.acronym} — {p.full_title}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Researcher
            </label>
            <select
              value={selectedResearcherId}
              onChange={(e) => setSelectedResearcherId(e.target.value)}
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm
                focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            >
              <option value="">-- Select researcher --</option>
              {researchers?.items?.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name} ({r.position})
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {previewLoading && (
        <div className="text-center py-6 text-gray-500">Loading preview...</div>
      )}

      {preview && (
        <>
          {/* Auto-populated fields */}
          {autoFields.length > 0 && (
            <div className="bg-white border border-gray-200 rounded-lg p-5 mb-6">
              <h2 className="text-sm font-semibold text-gray-900 mb-4">
                Auto-Populated Fields
                <span className="text-xs font-normal text-gray-500 ml-2">
                  (from project / researcher data)
                </span>
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {autoFields.map((field) => (
                  <FieldInput
                    key={field.name}
                    field={field}
                    value={manualValues[field.name] || field.value || ''}
                    onChange={(val) => handleManualChange(field.name, val)}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Manual fields */}
          {manualFields.length > 0 && (
            <div className="bg-white border border-gray-200 rounded-lg p-5 mb-6">
              <h2 className="text-sm font-semibold text-gray-900 mb-4">
                Required Information
              </h2>
              <div className="grid grid-cols-1 gap-4">
                {manualFields.map((field) => (
                  <FieldInput
                    key={field.name}
                    field={field}
                    value={manualValues[field.name] || ''}
                    onChange={(val) => handleManualChange(field.name, val)}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Conditional sections */}
          {preview.conditional_sections_active.length > 0 && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <h3 className="text-sm font-semibold text-blue-900 mb-2">
                Active Conditional Sections
              </h3>
              <ul className="text-sm text-blue-800 space-y-1">
                {preview.conditional_sections_active.map((section) => (
                  <li key={section} className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-500" />
                    {section.replace(/_/g, ' ')}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Success message */}
          {successMsg && (
            <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-md text-sm text-green-800">
              {successMsg}{' '}
              <Link
                to="/templates/documents"
                className="text-green-700 underline"
              >
                View generated documents
              </Link>
            </div>
          )}

          {/* Error message */}
          {(generateMutation.isError || downloadMutation.isError) && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md text-sm text-red-800">
              Failed to generate document. Please check all required fields.
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3">
            <button
              onClick={handleGenerate}
              disabled={generateMutation.isPending}
              className="inline-flex items-center px-5 py-2.5 bg-blue-700 text-white
                rounded-md text-sm font-medium hover:bg-blue-800
                disabled:opacity-50"
            >
              {generateMutation.isPending ? 'Generating...' : 'Generate & Save'}
            </button>
            <button
              onClick={handleDownload}
              disabled={downloadMutation.isPending}
              className="inline-flex items-center px-5 py-2.5 border border-gray-300
                rounded-md text-sm font-medium text-gray-700 bg-white
                hover:bg-gray-50 disabled:opacity-50"
            >
              {downloadMutation.isPending ? 'Downloading...' : 'Download DOCX'}
            </button>
          </div>
        </>
      )}
    </div>
  );
}
