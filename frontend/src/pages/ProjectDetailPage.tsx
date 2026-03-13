import { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useProject, useDeleteProject } from '../hooks/useProjects';
import AdditionalFeaturesPanel from './AdditionalFeaturesPage';
import {
  useWorkPackages,
  useCreateWorkPackage,
  useDeleteWorkPackage,
  useDeliverables,
  useCreateDeliverable,
  useDeleteDeliverable,
  useMilestones,
  useCreateMilestone,
  useDeleteMilestone,
} from '../hooks/useWorkPackages';
import {
  useMissions,
  useCreateMission,
  useApproveMission,
  useCompleteMission,
  useCancelMission,
  useDeleteMission,
} from '../hooks/useMissions';
import {
  useEffortAllocations,
  useCreateEffortAllocation,
  useDeleteEffortAllocation,
  useProjectEffortSummary,
  useComplianceReport,
} from '../hooks/useTimesheets';
import { useResearchers } from '../hooks/useResearchers';
import {
  useProjectPartners,
  usePartners,
  useAddPartnerToProject,
  useRemovePartnerFromProject,
} from '../hooks/usePartners';
import { StatusBadge, TrafficLightDot } from '../components/StatusBadge';
import { ConfirmDialog } from '../components/ConfirmDialog';
import {
  PROGRAMME_LABELS,
  COST_MODEL_LABELS,
  ROLE_LABELS,
  WP_STATUS_LABELS,
  DELIVERABLE_TYPE_LABELS,
  DISSEMINATION_LABELS,
  EC_REVIEW_LABELS,
  APPROVAL_STATUS_LABELS,
  MISSION_PURPOSE_LABELS,
  WPStatus,
  DeliverableType,
  DisseminationLevel,
  ApprovalStatus,
  MissionPurpose,
  CostModel,
} from '../types';
import type {
  WorkPackage,
  WorkPackageCreate,
  Deliverable,
  DeliverableCreate,
  Milestone,
  MilestoneCreate,
  ProjectPartner,
  Mission,
  MissionCreate,
  MissionComplete,
  EffortAllocationCreate,
  Researcher,
} from '../types';

type TabId = 'overview' | 'work-packages' | 'deliverables' | 'milestones' | 'partners' | 'missions' | 'effort' | 'features';

const TABS: { id: TabId; label: string }[] = [
  { id: 'overview', label: 'Overview' },
  { id: 'work-packages', label: 'Work Packages' },
  { id: 'deliverables', label: 'Deliverables' },
  { id: 'milestones', label: 'Milestones' },
  { id: 'partners', label: 'Partners' },
  { id: 'missions', label: 'Missions' },
  { id: 'effort', label: 'Effort' },
  { id: 'features', label: 'Features' },
];

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

function InfoRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="py-2 sm:grid sm:grid-cols-3 sm:gap-4">
      <dt className="text-sm font-medium text-gray-500">{label}</dt>
      <dd className="mt-1 text-sm text-gray-900 sm:col-span-2 sm:mt-0">
        {value || '-'}
      </dd>
    </div>
  );
}

// --- Work Packages Tab ---

function WorkPackagesTab({ projectId }: { projectId: string }) {
  const { data, isLoading } = useWorkPackages(projectId);
  const createWP = useCreateWorkPackage();
  const deleteWP = useDeleteWorkPackage();
  const [showForm, setShowForm] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<WorkPackage | null>(null);
  const [form, setForm] = useState<WorkPackageCreate>({
    wp_number: 1,
    title: '',
    status: WPStatus.NOT_STARTED,
  });

  function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    createWP.mutate(
      { projectId, data: form },
      {
        onSuccess: () => {
          setShowForm(false);
          setForm({ wp_number: 1, title: '', status: WPStatus.NOT_STARTED });
        },
      },
    );
  }

  if (isLoading) return <div className="py-8 text-center text-gray-500">Loading...</div>;

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-medium">Work Packages ({data?.total ?? 0})</h3>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-blue-700 text-white px-3 py-1.5 rounded text-sm font-medium hover:bg-blue-800"
        >
          {showForm ? 'Cancel' : 'Add Work Package'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="bg-gray-50 rounded-lg p-4 mb-4 space-y-3">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">WP Number</label>
              <input
                type="number"
                min={1}
                value={form.wp_number}
                onChange={(e) => setForm({ ...form, wp_number: parseInt(e.target.value) || 1 })}
                className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
                required
              />
            </div>
            <div className="sm:col-span-2">
              <label className="block text-xs font-medium text-gray-600 mb-1">Title</label>
              <input
                value={form.title}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
                className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
                required
              />
            </div>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Start Month</label>
              <input
                type="number"
                min={1}
                value={form.start_month ?? ''}
                onChange={(e) =>
                  setForm({ ...form, start_month: e.target.value ? parseInt(e.target.value) : undefined })
                }
                className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">End Month</label>
              <input
                type="number"
                min={1}
                value={form.end_month ?? ''}
                onChange={(e) =>
                  setForm({ ...form, end_month: e.target.value ? parseInt(e.target.value) : undefined })
                }
                className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Person Months</label>
              <input
                type="number"
                step="0.01"
                min={0}
                value={form.total_pm ?? ''}
                onChange={(e) =>
                  setForm({ ...form, total_pm: e.target.value || undefined })
                }
                className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
              />
            </div>
          </div>
          <button
            type="submit"
            disabled={createWP.isPending}
            className="bg-blue-700 text-white px-4 py-1.5 rounded text-sm font-medium hover:bg-blue-800 disabled:opacity-50"
          >
            {createWP.isPending ? 'Creating...' : 'Create'}
          </button>
        </form>
      )}

      {!data?.items.length ? (
        <p className="text-gray-500 text-sm py-4">No work packages yet.</p>
      ) : (
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">WP</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Title</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Months</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">PM</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-4 py-2" />
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {data.items.map((wp) => (
              <tr key={wp.id} className="hover:bg-gray-50">
                <td className="px-4 py-2 text-sm font-medium">WP{wp.wp_number}</td>
                <td className="px-4 py-2 text-sm">{wp.title}</td>
                <td className="px-4 py-2 text-sm text-gray-600">
                  {wp.start_month && wp.end_month
                    ? `M${wp.start_month}-M${wp.end_month}`
                    : '-'}
                </td>
                <td className="px-4 py-2 text-sm text-gray-600">{wp.total_pm ?? '-'}</td>
                <td className="px-4 py-2 text-sm">
                  <span
                    className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                      wp.status === WPStatus.COMPLETED
                        ? 'bg-green-100 text-green-800'
                        : wp.status === WPStatus.DELAYED
                          ? 'bg-red-100 text-red-800'
                          : wp.status === WPStatus.IN_PROGRESS
                            ? 'bg-blue-100 text-blue-800'
                            : 'bg-gray-100 text-gray-700'
                    }`}
                  >
                    {WP_STATUS_LABELS[wp.status]}
                  </span>
                </td>
                <td className="px-4 py-2 text-right">
                  <button
                    onClick={() => setDeleteTarget(wp)}
                    className="text-gray-400 hover:text-red-600 text-xs"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <ConfirmDialog
        open={!!deleteTarget}
        title="Delete Work Package"
        message={`Delete WP${deleteTarget?.wp_number} "${deleteTarget?.title}"?`}
        onConfirm={() => {
          if (deleteTarget)
            deleteWP.mutate(
              { projectId, wpId: deleteTarget.id },
              { onSuccess: () => setDeleteTarget(null) },
            );
        }}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  );
}

// --- Deliverables Tab ---

function DeliverablesTab({ projectId }: { projectId: string }) {
  const { data: wpData } = useWorkPackages(projectId);
  const [selectedWP, setSelectedWP] = useState<string>('');
  const effectiveWP = selectedWP || wpData?.items[0]?.id || '';
  const { data, isLoading } = useDeliverables(projectId, effectiveWP || undefined);
  const createDel = useCreateDeliverable();
  const deleteDel = useDeleteDeliverable();
  const [showForm, setShowForm] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<Deliverable | null>(null);
  const [form, setForm] = useState<DeliverableCreate>({
    deliverable_number: '',
    title: '',
    type: DeliverableType.REPORT,
    dissemination_level: DisseminationLevel.PU,
  });

  function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    createDel.mutate(
      { projectId, wpId: effectiveWP, data: form },
      {
        onSuccess: () => {
          setShowForm(false);
          setForm({
            deliverable_number: '',
            title: '',
            type: DeliverableType.REPORT,
            dissemination_level: DisseminationLevel.PU,
          });
        },
      },
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <div className="flex items-center gap-3">
          <h3 className="text-lg font-medium">Deliverables</h3>
          {wpData && wpData.items.length > 0 && (
            <select
              value={effectiveWP}
              onChange={(e) => setSelectedWP(e.target.value)}
              className="border border-gray-300 rounded px-2 py-1 text-sm"
            >
              {wpData.items.map((wp) => (
                <option key={wp.id} value={wp.id}>
                  WP{wp.wp_number}: {wp.title}
                </option>
              ))}
            </select>
          )}
        </div>
        {effectiveWP && (
          <button
            onClick={() => setShowForm(!showForm)}
            className="bg-blue-700 text-white px-3 py-1.5 rounded text-sm font-medium hover:bg-blue-800"
          >
            {showForm ? 'Cancel' : 'Add Deliverable'}
          </button>
        )}
      </div>

      {!wpData?.items.length ? (
        <p className="text-gray-500 text-sm py-4">
          Create work packages first to add deliverables.
        </p>
      ) : (
        <>
          {showForm && (
            <form onSubmit={handleCreate} className="bg-gray-50 rounded-lg p-4 mb-4 space-y-3">
              <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Number</label>
                  <input
                    value={form.deliverable_number}
                    onChange={(e) => setForm({ ...form, deliverable_number: e.target.value })}
                    placeholder="D1.1"
                    className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
                    required
                  />
                </div>
                <div className="sm:col-span-3">
                  <label className="block text-xs font-medium text-gray-600 mb-1">Title</label>
                  <input
                    value={form.title}
                    onChange={(e) => setForm({ ...form, title: e.target.value })}
                    className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
                    required
                  />
                </div>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Type</label>
                  <select
                    value={form.type}
                    onChange={(e) => setForm({ ...form, type: e.target.value as DeliverableType })}
                    className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
                  >
                    {Object.values(DeliverableType).map((t) => (
                      <option key={t} value={t}>{DELIVERABLE_TYPE_LABELS[t]}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Dissemination</label>
                  <select
                    value={form.dissemination_level}
                    onChange={(e) =>
                      setForm({ ...form, dissemination_level: e.target.value as DisseminationLevel })
                    }
                    className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
                  >
                    {Object.values(DisseminationLevel).map((d) => (
                      <option key={d} value={d}>{DISSEMINATION_LABELS[d]}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Due Month</label>
                  <input
                    type="number"
                    min={1}
                    value={form.due_month ?? ''}
                    onChange={(e) =>
                      setForm({ ...form, due_month: e.target.value ? parseInt(e.target.value) : undefined })
                    }
                    className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
                  />
                </div>
              </div>
              <button
                type="submit"
                disabled={createDel.isPending}
                className="bg-blue-700 text-white px-4 py-1.5 rounded text-sm font-medium hover:bg-blue-800 disabled:opacity-50"
              >
                {createDel.isPending ? 'Creating...' : 'Create'}
              </button>
            </form>
          )}

          {isLoading ? (
            <div className="text-gray-500 text-sm py-4">Loading...</div>
          ) : !data?.items.length ? (
            <p className="text-gray-500 text-sm py-4">No deliverables in this work package.</p>
          ) : (
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">No.</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Title</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Due</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Review</th>
                  <th className="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-4 py-2" />
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {data.items.map((del) => (
                  <tr key={del.id} className="hover:bg-gray-50">
                    <td className="px-4 py-2 text-sm font-medium">{del.deliverable_number}</td>
                    <td className="px-4 py-2 text-sm">{del.title}</td>
                    <td className="px-4 py-2 text-sm text-gray-600">
                      {DELIVERABLE_TYPE_LABELS[del.type]}
                    </td>
                    <td className="px-4 py-2 text-sm text-gray-600">
                      {del.due_month ? `M${del.due_month}` : '-'}
                    </td>
                    <td className="px-4 py-2 text-sm text-gray-600">
                      {EC_REVIEW_LABELS[del.ec_review_status]}
                    </td>
                    <td className="px-4 py-2 text-center">
                      <TrafficLightDot color={del.traffic_light} />
                    </td>
                    <td className="px-4 py-2 text-right">
                      <button
                        onClick={() => setDeleteTarget(del)}
                        className="text-gray-400 hover:text-red-600 text-xs"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </>
      )}

      <ConfirmDialog
        open={!!deleteTarget}
        title="Delete Deliverable"
        message={`Delete ${deleteTarget?.deliverable_number} "${deleteTarget?.title}"?`}
        onConfirm={() => {
          if (deleteTarget)
            deleteDel.mutate(
              { projectId, wpId: effectiveWP, deliverableId: deleteTarget.id },
              { onSuccess: () => setDeleteTarget(null) },
            );
        }}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  );
}

// --- Milestones Tab ---

function MilestonesTab({ projectId }: { projectId: string }) {
  const { data: wpData } = useWorkPackages(projectId);
  const [selectedWP, setSelectedWP] = useState<string>('');
  const effectiveWP = selectedWP || wpData?.items[0]?.id || '';
  const { data, isLoading } = useMilestones(projectId, effectiveWP || undefined);
  const createMs = useCreateMilestone();
  const deleteMs = useDeleteMilestone();
  const [showForm, setShowForm] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<Milestone | null>(null);
  const [form, setForm] = useState<MilestoneCreate>({
    milestone_number: '',
    title: '',
  });

  function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    createMs.mutate(
      { projectId, wpId: effectiveWP, data: form },
      {
        onSuccess: () => {
          setShowForm(false);
          setForm({ milestone_number: '', title: '' });
        },
      },
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <div className="flex items-center gap-3">
          <h3 className="text-lg font-medium">Milestones</h3>
          {wpData && wpData.items.length > 0 && (
            <select
              value={effectiveWP}
              onChange={(e) => setSelectedWP(e.target.value)}
              className="border border-gray-300 rounded px-2 py-1 text-sm"
            >
              {wpData.items.map((wp) => (
                <option key={wp.id} value={wp.id}>
                  WP{wp.wp_number}: {wp.title}
                </option>
              ))}
            </select>
          )}
        </div>
        {effectiveWP && (
          <button
            onClick={() => setShowForm(!showForm)}
            className="bg-blue-700 text-white px-3 py-1.5 rounded text-sm font-medium hover:bg-blue-800"
          >
            {showForm ? 'Cancel' : 'Add Milestone'}
          </button>
        )}
      </div>

      {!wpData?.items.length ? (
        <p className="text-gray-500 text-sm py-4">
          Create work packages first to add milestones.
        </p>
      ) : (
        <>
          {showForm && (
            <form onSubmit={handleCreate} className="bg-gray-50 rounded-lg p-4 mb-4 space-y-3">
              <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Number</label>
                  <input
                    value={form.milestone_number}
                    onChange={(e) => setForm({ ...form, milestone_number: e.target.value })}
                    placeholder="MS1"
                    className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
                    required
                  />
                </div>
                <div className="sm:col-span-2">
                  <label className="block text-xs font-medium text-gray-600 mb-1">Title</label>
                  <input
                    value={form.title}
                    onChange={(e) => setForm({ ...form, title: e.target.value })}
                    className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Due Month</label>
                  <input
                    type="number"
                    min={1}
                    value={form.due_month ?? ''}
                    onChange={(e) =>
                      setForm({ ...form, due_month: e.target.value ? parseInt(e.target.value) : undefined })
                    }
                    className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
                  />
                </div>
              </div>
              <button
                type="submit"
                disabled={createMs.isPending}
                className="bg-blue-700 text-white px-4 py-1.5 rounded text-sm font-medium hover:bg-blue-800 disabled:opacity-50"
              >
                {createMs.isPending ? 'Creating...' : 'Create'}
              </button>
            </form>
          )}

          {isLoading ? (
            <div className="text-gray-500 text-sm py-4">Loading...</div>
          ) : !data?.items.length ? (
            <p className="text-gray-500 text-sm py-4">No milestones in this work package.</p>
          ) : (
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">No.</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Title</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Due</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Achieved</th>
                  <th className="px-4 py-2" />
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {data.items.map((ms) => (
                  <tr key={ms.id} className="hover:bg-gray-50">
                    <td className="px-4 py-2 text-sm font-medium">{ms.milestone_number}</td>
                    <td className="px-4 py-2 text-sm">{ms.title}</td>
                    <td className="px-4 py-2 text-sm text-gray-600">
                      {ms.due_month ? `M${ms.due_month}` : '-'}
                    </td>
                    <td className="px-4 py-2 text-sm">
                      {ms.achieved ? (
                        <span className="text-green-600 font-medium">Yes</span>
                      ) : (
                        <span className="text-gray-400">No</span>
                      )}
                    </td>
                    <td className="px-4 py-2 text-right">
                      <button
                        onClick={() => setDeleteTarget(ms)}
                        className="text-gray-400 hover:text-red-600 text-xs"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </>
      )}

      <ConfirmDialog
        open={!!deleteTarget}
        title="Delete Milestone"
        message={`Delete ${deleteTarget?.milestone_number} "${deleteTarget?.title}"?`}
        onConfirm={() => {
          if (deleteTarget)
            deleteMs.mutate(
              { projectId, wpId: effectiveWP, milestoneId: deleteTarget.id },
              { onSuccess: () => setDeleteTarget(null) },
            );
        }}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  );
}

// --- Partners Tab ---

function PartnersTab({ projectId }: { projectId: string }) {
  const { data: projectPartners, isLoading } = useProjectPartners(projectId);
  const { data: allPartners } = usePartners();
  const addPartner = useAddPartnerToProject();
  const removePartner = useRemovePartnerFromProject();
  const [showForm, setShowForm] = useState(false);
  const [selectedPartnerId, setSelectedPartnerId] = useState('');
  const [budget, setBudget] = useState('');
  const [euContribution, setEuContribution] = useState('');
  const [deleteTarget, setDeleteTarget] = useState<ProjectPartner | null>(null);

  const linkedPartnerIds = new Set(projectPartners?.map((pp) => pp.partner_id) ?? []);
  const availablePartners =
    allPartners?.items.filter((p) => !linkedPartnerIds.has(p.id)) ?? [];

  function handleAdd(e: React.FormEvent) {
    e.preventDefault();
    addPartner.mutate(
      {
        projectId,
        data: {
          partner_id: selectedPartnerId,
          partner_budget: budget || undefined,
          partner_eu_contribution: euContribution || undefined,
        },
      },
      {
        onSuccess: () => {
          setShowForm(false);
          setSelectedPartnerId('');
          setBudget('');
          setEuContribution('');
        },
      },
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-medium">
          Partners ({projectPartners?.length ?? 0})
        </h3>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-blue-700 text-white px-3 py-1.5 rounded text-sm font-medium hover:bg-blue-800"
        >
          {showForm ? 'Cancel' : 'Add Partner'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleAdd} className="bg-gray-50 rounded-lg p-4 mb-4 space-y-3">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Partner</label>
              <select
                value={selectedPartnerId}
                onChange={(e) => setSelectedPartnerId(e.target.value)}
                className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
                required
              >
                <option value="">Select partner...</option>
                {availablePartners.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.short_name} - {p.legal_name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Budget (EUR)</label>
              <input
                type="number"
                step="0.01"
                min={0}
                value={budget}
                onChange={(e) => setBudget(e.target.value)}
                className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">EU Contribution (EUR)</label>
              <input
                type="number"
                step="0.01"
                min={0}
                value={euContribution}
                onChange={(e) => setEuContribution(e.target.value)}
                className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
              />
            </div>
          </div>
          <button
            type="submit"
            disabled={addPartner.isPending}
            className="bg-blue-700 text-white px-4 py-1.5 rounded text-sm font-medium hover:bg-blue-800 disabled:opacity-50"
          >
            {addPartner.isPending ? 'Adding...' : 'Add to Project'}
          </button>
        </form>
      )}

      {isLoading ? (
        <div className="text-gray-500 text-sm py-4">Loading...</div>
      ) : !projectPartners?.length ? (
        <p className="text-gray-500 text-sm py-4">No partners linked to this project.</p>
      ) : (
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Short Name</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Legal Name</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Country</th>
              <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Budget</th>
              <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">EU Contribution</th>
              <th className="px-4 py-2" />
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {projectPartners.map((pp) => (
              <tr key={pp.id} className="hover:bg-gray-50">
                <td className="px-4 py-2 text-sm font-medium">{pp.partner.short_name}</td>
                <td className="px-4 py-2 text-sm">{pp.partner.legal_name}</td>
                <td className="px-4 py-2 text-sm text-gray-600">{pp.partner.country ?? '-'}</td>
                <td className="px-4 py-2 text-sm text-right">
                  {formatCurrency(pp.partner_budget)}
                </td>
                <td className="px-4 py-2 text-sm text-right">
                  {formatCurrency(pp.partner_eu_contribution)}
                </td>
                <td className="px-4 py-2 text-right">
                  <button
                    onClick={() => setDeleteTarget(pp)}
                    className="text-gray-400 hover:text-red-600 text-xs"
                  >
                    Remove
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <ConfirmDialog
        open={!!deleteTarget}
        title="Remove Partner"
        message={`Remove "${deleteTarget?.partner.short_name}" from this project?`}
        onConfirm={() => {
          if (deleteTarget)
            removePartner.mutate(
              { projectId, linkId: deleteTarget.id },
              { onSuccess: () => setDeleteTarget(null) },
            );
        }}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  );
}


// --- Missions Tab ---

function ApprovalBadge({ status }: { status: ApprovalStatus }) {
  const colors: Record<ApprovalStatus, string> = {
    [ApprovalStatus.REQUESTED]: 'bg-gray-100 text-gray-700',
    [ApprovalStatus.PI_APPROVED]: 'bg-yellow-100 text-yellow-800',
    [ApprovalStatus.CENTRALLY_APPROVED]: 'bg-blue-100 text-blue-800',
    [ApprovalStatus.COMPLETED]: 'bg-green-100 text-green-800',
    [ApprovalStatus.CANCELLED]: 'bg-red-100 text-red-700',
  };
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${colors[status]}`}>
      {APPROVAL_STATUS_LABELS[status]}
    </span>
  );
}

function MissionsTab({ projectId, costModel }: { projectId: string; costModel: CostModel }) {
  const { data, isLoading } = useMissions(projectId);
  const createMission = useCreateMission();
  const approveMission = useApproveMission();
  const completeMission = useCompleteMission();
  const cancelMission = useCancelMission();
  const deleteMission = useDeleteMission();
  const [showForm, setShowForm] = useState(false);
  const [completeTarget, setCompleteTarget] = useState<Mission | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Mission | null>(null);
  const [form, setForm] = useState<MissionCreate>({
    researcher_name: '',
    purpose: MissionPurpose.CONFERENCE,
    destination: '',
    start_date: '',
    end_date: '',
  });
  const [completeForm, setCompleteForm] = useState<MissionComplete>({
    actual_total_cost: '',
  });

  function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    createMission.mutate(
      { projectId, data: form },
      {
        onSuccess: () => {
          setShowForm(false);
          setForm({
            researcher_name: '',
            purpose: MissionPurpose.CONFERENCE,
            destination: '',
            start_date: '',
            end_date: '',
          });
        },
      },
    );
  }

  function handleComplete(e: React.FormEvent) {
    e.preventDefault();
    if (!completeTarget) return;
    completeMission.mutate(
      { projectId, missionId: completeTarget.id, data: completeForm },
      {
        onSuccess: () => {
          setCompleteTarget(null);
          setCompleteForm({ actual_total_cost: '' });
        },
      },
    );
  }

  const isActualCosts = costModel === CostModel.ACTUAL_COSTS;

  if (isLoading) return <div className="py-8 text-center text-gray-500">Loading...</div>;

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-medium">Missions ({data?.total ?? 0})</h3>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-blue-700 text-white px-3 py-1.5 rounded text-sm font-medium hover:bg-blue-800"
        >
          {showForm ? 'Cancel' : 'Request Mission'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="bg-gray-50 rounded-lg p-4 mb-4 space-y-3">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Researcher</label>
              <input
                value={form.researcher_name}
                onChange={(e) => setForm({ ...form, researcher_name: e.target.value })}
                className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Purpose</label>
              <select
                value={form.purpose}
                onChange={(e) => setForm({ ...form, purpose: e.target.value as MissionPurpose })}
                className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
              >
                {Object.values(MissionPurpose).map((p) => (
                  <option key={p} value={p}>{MISSION_PURPOSE_LABELS[p]}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Destination</label>
              <input
                value={form.destination}
                onChange={(e) => setForm({ ...form, destination: e.target.value })}
                className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
                required
              />
            </div>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Start Date</label>
              <input
                type="date"
                value={form.start_date}
                onChange={(e) => setForm({ ...form, start_date: e.target.value })}
                className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">End Date</label>
              <input
                type="date"
                value={form.end_date}
                onChange={(e) => setForm({ ...form, end_date: e.target.value })}
                className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Travel Costs</label>
              <input
                type="number"
                step="0.01"
                min={0}
                value={form.travel_costs ?? ''}
                onChange={(e) => setForm({ ...form, travel_costs: e.target.value || undefined })}
                className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Total Cost</label>
              <input
                type="number"
                step="0.01"
                min={0}
                value={form.total_cost ?? ''}
                onChange={(e) => setForm({ ...form, total_cost: e.target.value || undefined })}
                className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
              />
            </div>
          </div>
          <button
            type="submit"
            disabled={createMission.isPending}
            className="bg-blue-700 text-white px-4 py-1.5 rounded text-sm font-medium hover:bg-blue-800 disabled:opacity-50"
          >
            {createMission.isPending ? 'Submitting...' : 'Submit Request'}
          </button>
        </form>
      )}

      {!data?.items.length ? (
        <p className="text-gray-500 text-sm py-4">No missions yet.</p>
      ) : (
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Researcher</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Destination</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Dates</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Purpose</th>
              <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Cost</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-4 py-2" />
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {data.items.map((m) => (
              <tr key={m.id} className="hover:bg-gray-50">
                <td className="px-4 py-2 text-sm font-medium">
                  {m.researcher_name}
                  {m.is_international && (
                    <span className="ml-1 text-xs text-orange-600" title="International">Intl</span>
                  )}
                </td>
                <td className="px-4 py-2 text-sm">{m.destination}</td>
                <td className="px-4 py-2 text-sm text-gray-600">
                  {formatDate(m.start_date)} - {formatDate(m.end_date)}
                </td>
                <td className="px-4 py-2 text-sm text-gray-600">
                  {MISSION_PURPOSE_LABELS[m.purpose]}
                </td>
                <td className="px-4 py-2 text-sm text-right">
                  {m.total_cost ? formatCurrency(m.total_cost) : '-'}
                  {m.approval_status === ApprovalStatus.COMPLETED && m.reconciliation_notes && (
                    <div className="text-xs text-gray-500 mt-0.5">{m.reconciliation_notes}</div>
                  )}
                </td>
                <td className="px-4 py-2 text-sm">
                  <ApprovalBadge status={m.approval_status} />
                </td>
                <td className="px-4 py-2 text-right space-x-2">
                  {(m.approval_status === ApprovalStatus.REQUESTED ||
                    (m.approval_status === ApprovalStatus.PI_APPROVED &&
                      m.requires_central_approval)) && (
                    <button
                      onClick={() =>
                        approveMission.mutate({ projectId, missionId: m.id })
                      }
                      className="text-blue-600 hover:text-blue-800 text-xs font-medium"
                    >
                      Approve
                    </button>
                  )}
                  {(m.approval_status === ApprovalStatus.PI_APPROVED ||
                    m.approval_status === ApprovalStatus.CENTRALLY_APPROVED) && (
                    <button
                      onClick={() => {
                        setCompleteTarget(m);
                        setCompleteForm({ actual_total_cost: m.total_cost || '' });
                      }}
                      className="text-green-600 hover:text-green-800 text-xs font-medium"
                    >
                      Complete
                    </button>
                  )}
                  {m.approval_status !== ApprovalStatus.COMPLETED &&
                    m.approval_status !== ApprovalStatus.CANCELLED && (
                    <button
                      onClick={() =>
                        cancelMission.mutate({ projectId, missionId: m.id })
                      }
                      className="text-orange-500 hover:text-orange-700 text-xs font-medium"
                    >
                      Cancel
                    </button>
                  )}
                  {m.approval_status === ApprovalStatus.CANCELLED && (
                    <button
                      onClick={() => setDeleteTarget(m)}
                      className="text-gray-400 hover:text-red-600 text-xs"
                    >
                      Delete
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {/* Complete Mission Dialog */}
      {completeTarget && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
            <h3 className="text-lg font-medium mb-4">
              Complete Mission - {completeTarget.researcher_name}
            </h3>
            <p className="text-sm text-gray-600 mb-3">
              Estimated: {completeTarget.estimated_total_cost
                ? formatCurrency(completeTarget.estimated_total_cost)
                : '-'}
            </p>
            <form onSubmit={handleComplete} className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">
                  Actual Total Cost (EUR) *
                </label>
                <input
                  type="number"
                  step="0.01"
                  min={0}
                  value={completeForm.actual_total_cost}
                  onChange={(e) =>
                    setCompleteForm({ ...completeForm, actual_total_cost: e.target.value })
                  }
                  className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
                  required
                />
              </div>
              {isActualCosts && (
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">
                    Receipts (required for actual costs)
                  </label>
                  <textarea
                    value={
                      completeForm.actual_receipts
                        ? JSON.stringify(completeForm.actual_receipts)
                        : ''
                    }
                    onChange={(e) => {
                      try {
                        setCompleteForm({
                          ...completeForm,
                          actual_receipts: e.target.value ? JSON.parse(e.target.value) : undefined,
                        });
                      } catch {
                        // Allow typing incomplete JSON
                      }
                    }}
                    placeholder='{"receipt1": "filename.pdf"}'
                    className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
                    rows={2}
                  />
                </div>
              )}
              <div className="flex gap-2 pt-2">
                <button
                  type="submit"
                  disabled={completeMission.isPending}
                  className="bg-green-600 text-white px-4 py-1.5 rounded text-sm font-medium hover:bg-green-700 disabled:opacity-50"
                >
                  {completeMission.isPending ? 'Completing...' : 'Complete Mission'}
                </button>
                <button
                  type="button"
                  onClick={() => setCompleteTarget(null)}
                  className="bg-gray-200 text-gray-700 px-4 py-1.5 rounded text-sm font-medium hover:bg-gray-300"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <ConfirmDialog
        open={!!deleteTarget}
        title="Delete Mission"
        message={`Delete mission for "${deleteTarget?.researcher_name}" to ${deleteTarget?.destination}?`}
        onConfirm={() => {
          if (deleteTarget)
            deleteMission.mutate(
              { projectId, missionId: deleteTarget.id },
              { onSuccess: () => setDeleteTarget(null) },
            );
        }}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  );
}

// --- Effort Tab ---

function EffortTab({ projectId }: { projectId: string }) {
  const { data: summary, isLoading: summaryLoading } = useProjectEffortSummary(projectId);
  const { data: allocations, isLoading: allocLoading } = useEffortAllocations(projectId);
  const { data: researchers } = useResearchers(projectId);
  const createAllocation = useCreateEffortAllocation();
  const deleteAllocation = useDeleteEffortAllocation();

  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<EffortAllocationCreate>({
    researcher_id: '',
    period_start: '',
    period_end: '',
    planned_pm: '',
  });

  // Compliance state
  const today = new Date();
  const yearStart = `${today.getFullYear()}-01-01`;
  const yearEnd = `${today.getFullYear()}-12-31`;
  const { data: compliance } = useComplianceReport(projectId, yearStart, yearEnd);

  const allResearchers = researchers?.items ?? [];

  const handleCreateAllocation = () => {
    createAllocation.mutate(
      { projectId, data: form },
      {
        onSuccess: () => {
          setShowForm(false);
          setForm({ researcher_id: '', period_start: '', period_end: '', planned_pm: '' });
        },
      },
    );
  };

  return (
    <div className="space-y-8">
      {/* Effort Summary */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Effort Summary (Planned vs Actual PM)</h3>
        {summaryLoading ? (
          <p className="text-gray-500">Loading...</p>
        ) : summary && summary.rows.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">WP</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Title</th>
                  <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Planned PM</th>
                  <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Actual PM</th>
                  <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Variance</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {summary.rows.map((row, i) => (
                  <tr key={i}>
                    <td className="px-4 py-2 text-sm">{row.wp_number ?? '-'}</td>
                    <td className="px-4 py-2 text-sm">{row.wp_title ?? 'Unassigned'}</td>
                    <td className="px-4 py-2 text-sm text-right">{row.planned_pm}</td>
                    <td className="px-4 py-2 text-sm text-right">{row.actual_pm}</td>
                    <td className={`px-4 py-2 text-sm text-right ${Number(row.variance) < 0 ? 'text-red-600' : 'text-green-600'}`}>
                      {row.variance}
                    </td>
                  </tr>
                ))}
                <tr className="bg-gray-50 font-semibold">
                  <td className="px-4 py-2 text-sm" colSpan={2}>Total</td>
                  <td className="px-4 py-2 text-sm text-right">{summary.total_planned_pm}</td>
                  <td className="px-4 py-2 text-sm text-right">{summary.total_actual_pm}</td>
                  <td className="px-4 py-2 text-sm text-right">
                    {(Number(summary.total_planned_pm) - Number(summary.total_actual_pm)).toFixed(2)}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-gray-500 text-sm">No effort data yet.</p>
        )}
      </div>

      {/* Allocations */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Researcher Allocations</h3>
          <button
            onClick={() => setShowForm(!showForm)}
            className="text-sm bg-blue-700 text-white px-3 py-1.5 rounded hover:bg-blue-800"
          >
            {showForm ? 'Cancel' : '+ Add Allocation'}
          </button>
        </div>

        {showForm && (
          <div className="bg-gray-50 p-4 rounded-lg mb-4 grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Researcher</label>
              <select
                value={form.researcher_id}
                onChange={(e) => setForm({ ...form, researcher_id: e.target.value })}
                className="w-full border rounded px-2 py-1.5 text-sm"
              >
                <option value="">Select...</option>
                {allResearchers.map((r: Researcher) => (
                  <option key={r.id} value={r.id}>{r.name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Planned PM</label>
              <input
                type="number"
                step="0.01"
                value={form.planned_pm}
                onChange={(e) => setForm({ ...form, planned_pm: e.target.value })}
                className="w-full border rounded px-2 py-1.5 text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Period Start</label>
              <input
                type="date"
                value={form.period_start}
                onChange={(e) => setForm({ ...form, period_start: e.target.value })}
                className="w-full border rounded px-2 py-1.5 text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Period End</label>
              <input
                type="date"
                value={form.period_end}
                onChange={(e) => setForm({ ...form, period_end: e.target.value })}
                className="w-full border rounded px-2 py-1.5 text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">FTE %</label>
              <input
                type="number"
                step="1"
                value={form.planned_fte_percentage ?? ''}
                onChange={(e) => setForm({ ...form, planned_fte_percentage: e.target.value || undefined })}
                className="w-full border rounded px-2 py-1.5 text-sm"
                placeholder="Optional"
              />
            </div>
            <div className="flex items-end">
              <button
                onClick={handleCreateAllocation}
                disabled={!form.researcher_id || !form.period_start || !form.period_end || !form.planned_pm}
                className="bg-green-600 text-white px-4 py-1.5 rounded text-sm hover:bg-green-700 disabled:opacity-50"
              >
                Save
              </button>
            </div>
            {createAllocation.error && (
              <p className="col-span-2 text-red-600 text-sm">
                {(createAllocation.error as { response?: { data?: { detail?: string } } }).response?.data?.detail || 'Error creating allocation'}
              </p>
            )}
          </div>
        )}

        {allocLoading ? (
          <p className="text-gray-500">Loading...</p>
        ) : allocations && allocations.items.length > 0 ? (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Researcher</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Period</th>
                <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">PM</th>
                <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">FTE %</th>
                <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {allocations.items.map((alloc) => {
                const researcher = allResearchers.find((r: Researcher) => r.id === alloc.researcher_id);
                return (
                  <tr key={alloc.id}>
                    <td className="px-4 py-2 text-sm">{researcher?.name ?? alloc.researcher_id}</td>
                    <td className="px-4 py-2 text-sm">{alloc.period_start} to {alloc.period_end}</td>
                    <td className="px-4 py-2 text-sm text-right">{alloc.planned_pm}</td>
                    <td className="px-4 py-2 text-sm text-right">{alloc.planned_fte_percentage ?? '-'}</td>
                    <td className="px-4 py-2 text-sm text-right">
                      <button
                        onClick={() => deleteAllocation.mutate({ projectId, allocationId: alloc.id })}
                        className="text-red-600 hover:text-red-800 text-xs"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        ) : (
          <p className="text-gray-500 text-sm">No allocations yet.</p>
        )}
      </div>

      {/* Compliance Overview */}
      {compliance && compliance.total_issues > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Compliance Issues ({compliance.total_issues})
          </h3>
          <div className="space-y-2">
            {compliance.issues.map((issue, i) => (
              <div
                key={i}
                className={`p-3 rounded-lg text-sm ${
                  issue.issue_type === 'over_capacity'
                    ? 'bg-red-50 text-red-800 border border-red-200'
                    : issue.issue_type === 'late_submission'
                      ? 'bg-yellow-50 text-yellow-800 border border-yellow-200'
                      : 'bg-blue-50 text-blue-800 border border-blue-200'
                }`}
              >
                <span className="font-medium">{issue.researcher_name}</span>
                {' - '}
                {issue.issue_type === 'missing_timesheet' && 'Missing Timesheet'}
                {issue.issue_type === 'late_submission' && 'Late Submission'}
                {issue.issue_type === 'over_capacity' && 'Over Capacity'}
                {': '}
                {issue.details}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// --- Main Page ---

export default function ProjectDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: project, isLoading, error } = useProject(id);
  const deleteProject = useDeleteProject();
  const [activeTab, setActiveTab] = useState<TabId>('overview');
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  if (isLoading) {
    return <div className="text-center py-12 text-gray-500">Loading project...</div>;
  }

  if (error || !project) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600 mb-4">Project not found.</p>
        <Link to="/projects" className="text-blue-700 hover:underline">
          Back to projects
        </Link>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <Link to="/projects" className="text-sm text-gray-500 hover:text-gray-700 mb-2 inline-block">
          &larr; Back to projects
        </Link>
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
              {project.acronym}
              <StatusBadge status={project.status} />
            </h1>
            <p className="text-gray-600 mt-1">{project.full_title}</p>
          </div>
          <div className="flex gap-2">
            <Link
              to={`/projects/${project.id}/edit`}
              className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-50"
            >
              Edit
            </Link>
            <button
              onClick={() => setShowDeleteConfirm(true)}
              className="bg-white border border-red-300 text-red-600 px-4 py-2 rounded-lg text-sm font-medium hover:bg-red-50"
            >
              Delete
            </button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="flex gap-6">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`pb-3 text-sm font-medium border-b-2 ${
                activeTab === tab.id
                  ? 'border-blue-700 text-blue-700'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        {activeTab === 'overview' && (
          <div className="divide-y divide-gray-100">
            <InfoRow label="Programme" value={PROGRAMME_LABELS[project.programme]} />
            <InfoRow label="Cost Model" value={COST_MODEL_LABELS[project.cost_model]} />
            <InfoRow label="Role" value={ROLE_LABELS[project.role]} />
            <InfoRow
              label="Grant Agreement"
              value={project.grant_agreement_number}
            />
            <InfoRow label="Call Identifier" value={project.call_identifier} />
            <InfoRow label="Start Date" value={formatDate(project.start_date)} />
            <InfoRow label="End Date" value={formatDate(project.end_date)} />
            <InfoRow
              label="Duration"
              value={
                project.duration_months
                  ? `${project.duration_months} months`
                  : null
              }
            />
            <InfoRow
              label="Total Budget"
              value={formatCurrency(project.total_budget)}
            />
            <InfoRow
              label="EU Contribution"
              value={formatCurrency(project.eu_contribution)}
            />
            <InfoRow
              label="Funding Rate"
              value={
                project.funding_rate ? `${project.funding_rate}%` : null
              }
            />
            <InfoRow
              label="EC Project Officer"
              value={project.ec_project_officer}
            />
            <InfoRow
              label="Internal Cost Center"
              value={project.internal_cost_center}
            />
          </div>
        )}
        {activeTab === 'work-packages' && <WorkPackagesTab projectId={project.id} />}
        {activeTab === 'deliverables' && <DeliverablesTab projectId={project.id} />}
        {activeTab === 'milestones' && <MilestonesTab projectId={project.id} />}
        {activeTab === 'partners' && <PartnersTab projectId={project.id} />}
        {activeTab === 'missions' && <MissionsTab projectId={project.id} costModel={project.cost_model} />}
        {activeTab === 'effort' && <EffortTab projectId={project.id} />}
        {activeTab === 'features' && <AdditionalFeaturesPanel projectId={project.id} />}
      </div>

      <ConfirmDialog
        open={showDeleteConfirm}
        title="Delete Project"
        message={`Are you sure you want to delete "${project.acronym}"? This action cannot be undone.`}
        onConfirm={() => {
          deleteProject.mutate(project.id, {
            onSuccess: () => navigate('/projects'),
          });
        }}
        onCancel={() => setShowDeleteConfirm(false)}
      />
    </div>
  );
}
