import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useProjects, useDeleteProject } from '../hooks/useProjects';
import { StatusBadge } from '../components/StatusBadge';
import { ConfirmDialog } from '../components/ConfirmDialog';
import {
  Programme,
  CostModel,
  ProjectStatus,
  ProjectRole,
  PROGRAMME_LABELS,
  COST_MODEL_LABELS,
  STATUS_LABELS,
  ROLE_LABELS,
} from '../types';
import type { Project } from '../types';

function formatCurrency(value: string | null): string {
  if (!value) return '-';
  return new Intl.NumberFormat('en-EU', {
    style: 'currency',
    currency: 'EUR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(Number(value));
}

function formatDate(value: string | null): string {
  if (!value) return '-';
  return new Date(value).toLocaleDateString('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });
}

export default function ProjectListPage() {
  const navigate = useNavigate();
  const [statusFilter, setStatusFilter] = useState<ProjectStatus | ''>('');
  const [programmeFilter, setProgrammeFilter] = useState<Programme | ''>('');
  const [costModelFilter, setCostModelFilter] = useState<CostModel | ''>('');

  const filters = {
    ...(statusFilter && { status: statusFilter }),
    ...(programmeFilter && { programme: programmeFilter }),
    ...(costModelFilter && { cost_model: costModelFilter }),
  };

  const { data, isLoading, error } = useProjects(filters);
  const deleteProject = useDeleteProject();

  const [deleteTarget, setDeleteTarget] = useState<Project | null>(null);

  function handleDelete() {
    if (!deleteTarget) return;
    deleteProject.mutate(deleteTarget.id, {
      onSuccess: () => setDeleteTarget(null),
    });
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Projects</h1>
        <Link
          to="/projects/new"
          className="bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-800"
        >
          New Project
        </Link>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-6">
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as ProjectStatus | '')}
          className="border border-gray-300 rounded-md px-3 py-1.5 text-sm bg-white"
        >
          <option value="">All Statuses</option>
          {Object.values(ProjectStatus).map((s) => (
            <option key={s} value={s}>
              {STATUS_LABELS[s]}
            </option>
          ))}
        </select>
        <select
          value={programmeFilter}
          onChange={(e) => setProgrammeFilter(e.target.value as Programme | '')}
          className="border border-gray-300 rounded-md px-3 py-1.5 text-sm bg-white"
        >
          <option value="">All Programmes</option>
          {Object.values(Programme).map((p) => (
            <option key={p} value={p}>
              {PROGRAMME_LABELS[p]}
            </option>
          ))}
        </select>
        <select
          value={costModelFilter}
          onChange={(e) => setCostModelFilter(e.target.value as CostModel | '')}
          className="border border-gray-300 rounded-md px-3 py-1.5 text-sm bg-white"
        >
          <option value="">All Cost Models</option>
          {Object.values(CostModel).map((c) => (
            <option key={c} value={c}>
              {COST_MODEL_LABELS[c]}
            </option>
          ))}
        </select>
        {(statusFilter || programmeFilter || costModelFilter) && (
          <button
            onClick={() => {
              setStatusFilter('');
              setProgrammeFilter('');
              setCostModelFilter('');
            }}
            className="text-sm text-gray-500 hover:text-gray-700 underline"
          >
            Clear filters
          </button>
        )}
      </div>

      {/* Table */}
      {isLoading ? (
        <div className="text-center py-12 text-gray-500">Loading projects...</div>
      ) : error ? (
        <div className="text-center py-12 text-red-600">
          Failed to load projects. Is the backend running?
        </div>
      ) : !data?.items.length ? (
        <div className="text-center py-12">
          <p className="text-gray-500 mb-4">No projects found.</p>
          <Link
            to="/projects/new"
            className="text-blue-700 hover:text-blue-800 font-medium"
          >
            Create your first project
          </Link>
        </div>
      ) : (
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Acronym
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Programme
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Cost Model
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Role
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Start
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    End
                  </th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Budget
                  </th>
                  <th className="px-4 py-3" />
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {data.items.map((project) => (
                  <tr
                    key={project.id}
                    className="hover:bg-gray-50 cursor-pointer"
                    onClick={() => navigate(`/projects/${project.id}`)}
                  >
                    <td className="px-4 py-3 text-sm font-medium text-blue-700">
                      {project.acronym}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {PROGRAMME_LABELS[project.programme]}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {COST_MODEL_LABELS[project.cost_model]}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {ROLE_LABELS[project.role]}
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge status={project.status} />
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {formatDate(project.start_date)}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {formatDate(project.end_date)}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600 text-right">
                      {formatCurrency(project.total_budget)}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setDeleteTarget(project);
                        }}
                        className="text-gray-400 hover:text-red-600 text-sm"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="px-4 py-3 bg-gray-50 border-t border-gray-200 text-sm text-gray-500">
            {data.total} project{data.total !== 1 ? 's' : ''}
          </div>
        </div>
      )}

      <ConfirmDialog
        open={!!deleteTarget}
        title="Delete Project"
        message={`Are you sure you want to delete "${deleteTarget?.acronym}"? This action cannot be undone.`}
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  );
}
