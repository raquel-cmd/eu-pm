import { useState, useEffect } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import {
  useProject,
  useCreateProject,
  useUpdateProject,
} from '../hooks/useProjects';
import {
  Programme,
  CostModel,
  ProjectRole,
  ProjectStatus,
  PROGRAMME_LABELS,
  COST_MODEL_LABELS,
  ROLE_LABELS,
  STATUS_LABELS,
} from '../types';
import type { ProjectCreate } from '../types';

const PROGRAMME_COST_MODELS: Record<Programme, CostModel[]> = {
  [Programme.HORIZON_EUROPE]: [
    CostModel.ACTUAL_COSTS,
    CostModel.LUMP_SUM,
    CostModel.UNIT_COSTS,
    CostModel.MIXED,
  ],
  [Programme.DIGITAL_EUROPE]: [CostModel.ACTUAL_COSTS, CostModel.LUMP_SUM],
  [Programme.ERASMUS_PLUS]: [CostModel.LUMP_SUM, CostModel.UNIT_COSTS],
  [Programme.CEF]: [CostModel.ACTUAL_COSTS],
  [Programme.FCT]: [CostModel.ACTUAL_COSTS],
};

const EMPTY_FORM: ProjectCreate = {
  acronym: '',
  full_title: '',
  programme: Programme.HORIZON_EUROPE,
  cost_model: CostModel.ACTUAL_COSTS,
  role: ProjectRole.COORDINATOR,
  status: ProjectStatus.PROPOSAL,
};

function FormField({
  label,
  required,
  children,
}: {
  label: string;
  required?: boolean;
  children: React.ReactNode;
}) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {label}
        {required && <span className="text-red-500 ml-0.5">*</span>}
      </label>
      {children}
    </div>
  );
}

const inputClass =
  'w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500';

export default function ProjectFormPage() {
  const { id } = useParams<{ id: string }>();
  const isEditing = !!id;
  const navigate = useNavigate();
  const { data: existing, isLoading } = useProject(id);
  const createProject = useCreateProject();
  const updateProject = useUpdateProject();

  const [form, setForm] = useState<ProjectCreate>({ ...EMPTY_FORM });
  const [errors, setErrors] = useState<string[]>([]);

  useEffect(() => {
    if (existing) {
      setForm({
        acronym: existing.acronym,
        full_title: existing.full_title,
        grant_agreement_number: existing.grant_agreement_number,
        programme: existing.programme,
        call_identifier: existing.call_identifier,
        cost_model: existing.cost_model,
        role: existing.role,
        start_date: existing.start_date,
        end_date: existing.end_date,
        duration_months: existing.duration_months,
        total_budget: existing.total_budget,
        eu_contribution: existing.eu_contribution,
        funding_rate: existing.funding_rate,
        status: existing.status,
        ec_project_officer: existing.ec_project_officer,
        internal_cost_center: existing.internal_cost_center,
      });
    }
  }, [existing]);

  const availableCostModels = PROGRAMME_COST_MODELS[form.programme];

  function handleProgrammeChange(programme: Programme) {
    const models = PROGRAMME_COST_MODELS[programme];
    const costModel = models.includes(form.cost_model) ? form.cost_model : models[0];
    setForm({ ...form, programme, cost_model: costModel });
  }

  function set<K extends keyof ProjectCreate>(key: K, value: ProjectCreate[K]) {
    setForm({ ...form, [key]: value });
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErrors([]);

    const validationErrors: string[] = [];
    if (!form.acronym.trim()) validationErrors.push('Acronym is required');
    if (!form.full_title.trim()) validationErrors.push('Full title is required');
    if (validationErrors.length) {
      setErrors(validationErrors);
      return;
    }

    const payload = { ...form };
    // Clean empty strings to null for optional fields
    for (const key of [
      'grant_agreement_number',
      'call_identifier',
      'ec_project_officer',
      'internal_cost_center',
    ] as const) {
      if (payload[key] === '') payload[key] = null;
    }

    if (isEditing) {
      updateProject.mutate(
        { id, data: payload },
        { onSuccess: () => navigate(`/projects/${id}`) },
      );
    } else {
      createProject.mutate(payload, {
        onSuccess: (project) => navigate(`/projects/${project.id}`),
      });
    }
  }

  if (isEditing && isLoading) {
    return <div className="text-center py-12 text-gray-500">Loading...</div>;
  }

  const isPending = createProject.isPending || updateProject.isPending;

  return (
    <div className="max-w-3xl">
      <Link
        to={isEditing ? `/projects/${id}` : '/projects'}
        className="text-sm text-gray-500 hover:text-gray-700 mb-2 inline-block"
      >
        &larr; {isEditing ? 'Back to project' : 'Back to projects'}
      </Link>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">
        {isEditing ? 'Edit Project' : 'New Project'}
      </h1>

      {errors.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <ul className="list-disc list-inside text-sm text-red-700">
            {errors.map((err, i) => (
              <li key={i}>{err}</li>
            ))}
          </ul>
        </div>
      )}

      {(createProject.error || updateProject.error) && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 text-sm text-red-700">
          Failed to save project. Please check your input and try again.
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Basic Information */}
        <section>
          <h2 className="text-lg font-medium text-gray-900 mb-4 border-b pb-2">
            Basic Information
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <FormField label="Acronym" required>
              <input
                className={inputClass}
                value={form.acronym}
                onChange={(e) => set('acronym', e.target.value)}
                maxLength={50}
              />
            </FormField>
            <FormField label="Status">
              <select
                className={inputClass}
                value={form.status}
                onChange={(e) => set('status', e.target.value as ProjectStatus)}
              >
                {Object.values(ProjectStatus).map((s) => (
                  <option key={s} value={s}>
                    {STATUS_LABELS[s]}
                  </option>
                ))}
              </select>
            </FormField>
            <div className="sm:col-span-2">
              <FormField label="Full Title" required>
                <input
                  className={inputClass}
                  value={form.full_title}
                  onChange={(e) => set('full_title', e.target.value)}
                  maxLength={500}
                />
              </FormField>
            </div>
            <FormField label="Grant Agreement Number">
              <input
                className={inputClass}
                value={form.grant_agreement_number ?? ''}
                onChange={(e) => set('grant_agreement_number', e.target.value)}
                maxLength={50}
              />
            </FormField>
            <FormField label="Call Identifier">
              <input
                className={inputClass}
                value={form.call_identifier ?? ''}
                onChange={(e) => set('call_identifier', e.target.value)}
                maxLength={100}
              />
            </FormField>
          </div>
        </section>

        {/* Programme & Cost Model */}
        <section>
          <h2 className="text-lg font-medium text-gray-900 mb-4 border-b pb-2">
            Programme & Cost Model
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <FormField label="Programme" required>
              <select
                className={inputClass}
                value={form.programme}
                onChange={(e) =>
                  handleProgrammeChange(e.target.value as Programme)
                }
              >
                {Object.values(Programme).map((p) => (
                  <option key={p} value={p}>
                    {PROGRAMME_LABELS[p]}
                  </option>
                ))}
              </select>
            </FormField>
            <FormField label="Cost Model" required>
              <select
                className={inputClass}
                value={form.cost_model}
                onChange={(e) => set('cost_model', e.target.value as CostModel)}
              >
                {availableCostModels.map((c) => (
                  <option key={c} value={c}>
                    {COST_MODEL_LABELS[c]}
                  </option>
                ))}
              </select>
            </FormField>
            <FormField label="Role" required>
              <select
                className={inputClass}
                value={form.role}
                onChange={(e) => set('role', e.target.value as ProjectRole)}
              >
                {Object.values(ProjectRole).map((r) => (
                  <option key={r} value={r}>
                    {ROLE_LABELS[r]}
                  </option>
                ))}
              </select>
            </FormField>
          </div>

          {/* Dynamic cost model info */}
          <div className="mt-4 p-3 bg-blue-50 rounded-lg text-sm text-blue-800">
            {form.cost_model === CostModel.ACTUAL_COSTS && (
              <p>
                <strong>Actual Costs:</strong> Full expense tracking with mandatory
                timesheets, Form C financial reporting, and EC eligibility checks.
              </p>
            )}
            {form.cost_model === CostModel.LUMP_SUM && (
              <p>
                <strong>Lump Sum:</strong> WP-level budget monitoring with optional
                timesheets. WP completion declarations instead of Form C.
              </p>
            )}
            {form.cost_model === CostModel.UNIT_COSTS && (
              <p>
                <strong>Unit Costs:</strong> Unit delivery tracking with rate-based
                calculations. Evidence of units delivered required.
              </p>
            )}
            {form.cost_model === CostModel.MIXED && (
              <p>
                <strong>Mixed:</strong> Per-WP or per-category cost model overrides
                with project-level default.
              </p>
            )}
          </div>
        </section>

        {/* Timeline */}
        <section>
          <h2 className="text-lg font-medium text-gray-900 mb-4 border-b pb-2">
            Timeline
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <FormField label="Start Date">
              <input
                type="date"
                className={inputClass}
                value={form.start_date ?? ''}
                onChange={(e) => set('start_date', e.target.value || null)}
              />
            </FormField>
            <FormField label="End Date">
              <input
                type="date"
                className={inputClass}
                value={form.end_date ?? ''}
                onChange={(e) => set('end_date', e.target.value || null)}
              />
            </FormField>
            <FormField label="Duration (months)">
              <input
                type="number"
                min={1}
                className={inputClass}
                value={form.duration_months ?? ''}
                onChange={(e) =>
                  set(
                    'duration_months',
                    e.target.value ? parseInt(e.target.value) : null,
                  )
                }
              />
            </FormField>
          </div>
        </section>

        {/* Financial */}
        <section>
          <h2 className="text-lg font-medium text-gray-900 mb-4 border-b pb-2">
            Financial
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <FormField label="Total Budget (EUR)">
              <input
                type="number"
                step="0.01"
                min={0}
                className={inputClass}
                value={form.total_budget ?? ''}
                onChange={(e) =>
                  set('total_budget', e.target.value || null)
                }
              />
            </FormField>
            <FormField label="EU Contribution (EUR)">
              <input
                type="number"
                step="0.01"
                min={0}
                className={inputClass}
                value={form.eu_contribution ?? ''}
                onChange={(e) =>
                  set('eu_contribution', e.target.value || null)
                }
              />
            </FormField>
            <FormField label="Funding Rate (%)">
              <input
                type="number"
                step="0.01"
                min={0}
                max={100}
                className={inputClass}
                value={form.funding_rate ?? ''}
                onChange={(e) =>
                  set('funding_rate', e.target.value || null)
                }
              />
            </FormField>
          </div>

          {/* Cost model specific sections */}
          {form.cost_model === CostModel.ACTUAL_COSTS && (
            <div className="mt-4 p-4 border border-gray-200 rounded-lg">
              <h3 className="text-sm font-medium text-gray-700 mb-2">
                Actual Costs Configuration
              </h3>
              <p className="text-xs text-gray-500">
                This project will require detailed expense tracking in EC budget
                categories A-E. Timesheets will be mandatory for all personnel
                costs.
              </p>
            </div>
          )}

          {form.cost_model === CostModel.LUMP_SUM && (
            <div className="mt-4 p-4 border border-gray-200 rounded-lg">
              <h3 className="text-sm font-medium text-gray-700 mb-2">
                Lump Sum Configuration
              </h3>
              <p className="text-xs text-gray-500">
                Budget will be monitored at work package level. WP completion
                declarations will be used instead of Form C reporting.
              </p>
            </div>
          )}

          {form.cost_model === CostModel.UNIT_COSTS && (
            <div className="mt-4 p-4 border border-gray-200 rounded-lg">
              <h3 className="text-sm font-medium text-gray-700 mb-2">
                Unit Costs Configuration
              </h3>
              <p className="text-xs text-gray-500">
                Costs will be tracked via unit delivery with rate-based
                calculations. Evidence of units delivered will be required.
              </p>
            </div>
          )}
        </section>

        {/* Administrative */}
        <section>
          <h2 className="text-lg font-medium text-gray-900 mb-4 border-b pb-2">
            Administrative
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <FormField label="EC Project Officer">
              <input
                className={inputClass}
                value={form.ec_project_officer ?? ''}
                onChange={(e) => set('ec_project_officer', e.target.value)}
                maxLength={200}
              />
            </FormField>
            <FormField label="Internal Cost Center">
              <input
                className={inputClass}
                value={form.internal_cost_center ?? ''}
                onChange={(e) => set('internal_cost_center', e.target.value)}
                maxLength={50}
              />
            </FormField>
          </div>
        </section>

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-4 border-t">
          <Link
            to={isEditing ? `/projects/${id}` : '/projects'}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Cancel
          </Link>
          <button
            type="submit"
            disabled={isPending}
            className="px-6 py-2 text-sm font-medium text-white bg-blue-700 rounded-md hover:bg-blue-800 disabled:opacity-50"
          >
            {isPending
              ? 'Saving...'
              : isEditing
                ? 'Save Changes'
                : 'Create Project'}
          </button>
        </div>
      </form>
    </div>
  );
}
