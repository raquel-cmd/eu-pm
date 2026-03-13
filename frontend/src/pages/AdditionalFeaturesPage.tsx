/**
 * Section 9 — Additional Features tabs for Project Detail view.
 *
 * Sub-tab components: IPAssetsTab, DisseminationTab, KPIsTab, EthicsTab,
 * AmendmentsTab, NotificationsTab
 */
import { useState } from 'react';
import {
  useIPAssets,
  useCreateIPAsset,
  useDeleteIPAsset,
  useDisseminationActivities,
  useCreateDisseminationActivity,
  useDeleteDisseminationActivity,
  useKPIDefinitions,
  useKPIValues,
  useCreateKPIValue,
  useEthicsRequirements,
  useCreateEthicsRequirement,
  useDeleteEthicsRequirement,
  useDataManagementRecords,
  useCreateDataManagementRecord,
  useDeleteDataManagementRecord,
  useAmendments,
  useCreateAmendment,
  useDeleteAmendment,
  useNotifications,
  useMarkNotificationRead,
  useDismissNotification,
} from '../hooks/useAdditionalFeatures';
import {
  IPType,
  IPStatus,
  IP_TYPE_LABELS,
  IP_STATUS_LABELS,
  DisseminationActivityType,
  DISSEMINATION_ACTIVITY_TYPE_LABELS,
  OPEN_ACCESS_STATUS_LABELS,
  OpenAccessStatus,
  EthicsStatus,
  ETHICS_STATUS_LABELS,
  DMPStatus,
  DMP_STATUS_LABELS,
  AmendmentType,
  AmendmentStatus,
  AMENDMENT_TYPE_LABELS,
  AMENDMENT_STATUS_LABELS,
  NotificationPriority,
  NotificationStatus,
  NOTIFICATION_TYPE_LABELS,
  NOTIFICATION_PRIORITY_LABELS,
  NOTIFICATION_STATUS_LABELS,
} from '../types';

type SubTabId = 'ip' | 'dissemination' | 'kpis' | 'ethics' | 'amendments' | 'notifications';

const SUB_TABS: { id: SubTabId; label: string }[] = [
  { id: 'ip', label: 'IP Assets' },
  { id: 'dissemination', label: 'Dissemination' },
  { id: 'kpis', label: 'KPIs' },
  { id: 'ethics', label: 'Ethics & DMP' },
  { id: 'amendments', label: 'Amendments' },
  { id: 'notifications', label: 'Notifications' },
];

function statusBadgeColor(status: string): string {
  const colors: Record<string, string> = {
    IDENTIFIED: 'bg-gray-100 text-gray-700',
    DISCLOSED: 'bg-blue-100 text-blue-700',
    PATENT_FILED: 'bg-yellow-100 text-yellow-700',
    PATENT_GRANTED: 'bg-green-100 text-green-700',
    LICENSED: 'bg-purple-100 text-purple-700',
    EXPLOITED: 'bg-indigo-100 text-indigo-700',
    PENDING: 'bg-yellow-100 text-yellow-700',
    SUBMITTED: 'bg-blue-100 text-blue-700',
    APPROVED: 'bg-green-100 text-green-700',
    REJECTED: 'bg-red-100 text-red-700',
    DRAFT: 'bg-gray-100 text-gray-700',
    UNDER_REVIEW: 'bg-orange-100 text-orange-700',
    WITHDRAWN: 'bg-gray-100 text-gray-500',
    COMPLIANT: 'bg-green-100 text-green-700',
    NON_COMPLIANT: 'bg-red-100 text-red-700',
    SENT: 'bg-blue-100 text-blue-700',
    READ: 'bg-green-100 text-green-700',
    DISMISSED: 'bg-gray-100 text-gray-500',
    LOW: 'bg-gray-100 text-gray-600',
    MEDIUM: 'bg-yellow-100 text-yellow-700',
    HIGH: 'bg-orange-100 text-orange-700',
    CRITICAL: 'bg-red-100 text-red-700',
  };
  return colors[status] || 'bg-gray-100 text-gray-700';
}

function Badge({ label, status }: { label: string; status: string }) {
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${statusBadgeColor(status)}`}>
      {label}
    </span>
  );
}

// ── IP Assets Tab ────────────────────────────────────

function IPAssetsTab({ projectId }: { projectId: string }) {
  const { data, isLoading } = useIPAssets(projectId);
  const createMutation = useCreateIPAsset(projectId);
  const deleteMutation = useDeleteIPAsset(projectId);
  const [showForm, setShowForm] = useState(false);
  const [title, setTitle] = useState('');
  const [ipType, setIpType] = useState<IPType>(IPType.FOREGROUND);

  if (isLoading) return <p className="text-gray-500">Loading IP assets...</p>;

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">IP and Exploitation Tracking</h3>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-blue-700 text-white px-3 py-1.5 rounded text-sm hover:bg-blue-800"
        >
          {showForm ? 'Cancel' : '+ Add IP Asset'}
        </button>
      </div>
      {showForm && (
        <div className="bg-gray-50 p-4 rounded-lg mb-4 space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
              placeholder="IP asset title"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
            <select
              value={ipType}
              onChange={(e) => setIpType(e.target.value as IPType)}
              className="border border-gray-300 rounded px-3 py-1.5 text-sm"
            >
              {Object.entries(IP_TYPE_LABELS).map(([k, v]) => (
                <option key={k} value={k}>{v}</option>
              ))}
            </select>
          </div>
          <button
            onClick={() => {
              createMutation.mutate(
                { ip_type: ipType, title, status: IPStatus.IDENTIFIED },
                { onSuccess: () => { setShowForm(false); setTitle(''); } },
              );
            }}
            disabled={!title || createMutation.isPending}
            className="bg-blue-700 text-white px-4 py-1.5 rounded text-sm hover:bg-blue-800 disabled:opacity-50"
          >
            Create
          </button>
        </div>
      )}
      {!data?.items.length ? (
        <p className="text-gray-500 text-sm">No IP assets recorded.</p>
      ) : (
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-500 border-b">
              <th className="pb-2">Title</th>
              <th className="pb-2">Type</th>
              <th className="pb-2">Status</th>
              <th className="pb-2">Owner</th>
              <th className="pb-2">Patent Ref</th>
              <th className="pb-2"></th>
            </tr>
          </thead>
          <tbody>
            {data.items.map((asset) => (
              <tr key={asset.id} className="border-b border-gray-100">
                <td className="py-2 font-medium">{asset.title}</td>
                <td className="py-2">{IP_TYPE_LABELS[asset.ip_type]}</td>
                <td className="py-2">
                  <Badge label={IP_STATUS_LABELS[asset.status]} status={asset.status} />
                </td>
                <td className="py-2 text-gray-600">{asset.owner || '—'}</td>
                <td className="py-2 text-gray-600">{asset.patent_reference || '—'}</td>
                <td className="py-2">
                  <button
                    onClick={() => deleteMutation.mutate(asset.id)}
                    className="text-red-600 hover:text-red-800 text-xs"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

// ── Dissemination Tab ────────────────────────────────

function DisseminationTab({ projectId }: { projectId: string }) {
  const { data, isLoading } = useDisseminationActivities(projectId);
  const createMutation = useCreateDisseminationActivity(projectId);
  const deleteMutation = useDeleteDisseminationActivity(projectId);
  const [showForm, setShowForm] = useState(false);
  const [title, setTitle] = useState('');
  const [activityType, setActivityType] = useState<DisseminationActivityType>(
    DisseminationActivityType.PUBLICATION,
  );

  if (isLoading) return <p className="text-gray-500">Loading...</p>;

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">Communication and Dissemination Log</h3>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-blue-700 text-white px-3 py-1.5 rounded text-sm hover:bg-blue-800"
        >
          {showForm ? 'Cancel' : '+ Add Activity'}
        </button>
      </div>
      {showForm && (
        <div className="bg-gray-50 p-4 rounded-lg mb-4 space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
            <select
              value={activityType}
              onChange={(e) => setActivityType(e.target.value as DisseminationActivityType)}
              className="border border-gray-300 rounded px-3 py-1.5 text-sm"
            >
              {Object.entries(DISSEMINATION_ACTIVITY_TYPE_LABELS).map(([k, v]) => (
                <option key={k} value={k}>{v}</option>
              ))}
            </select>
          </div>
          <button
            onClick={() => {
              createMutation.mutate(
                { activity_type: activityType, title },
                { onSuccess: () => { setShowForm(false); setTitle(''); } },
              );
            }}
            disabled={!title || createMutation.isPending}
            className="bg-blue-700 text-white px-4 py-1.5 rounded text-sm hover:bg-blue-800 disabled:opacity-50"
          >
            Create
          </button>
        </div>
      )}
      {!data?.items.length ? (
        <p className="text-gray-500 text-sm">No dissemination activities recorded.</p>
      ) : (
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-500 border-b">
              <th className="pb-2">Title</th>
              <th className="pb-2">Type</th>
              <th className="pb-2">Venue</th>
              <th className="pb-2">Date</th>
              <th className="pb-2">Open Access</th>
              <th className="pb-2"></th>
            </tr>
          </thead>
          <tbody>
            {data.items.map((a) => (
              <tr key={a.id} className="border-b border-gray-100">
                <td className="py-2 font-medium">{a.title}</td>
                <td className="py-2">{DISSEMINATION_ACTIVITY_TYPE_LABELS[a.activity_type]}</td>
                <td className="py-2 text-gray-600">{a.venue || '—'}</td>
                <td className="py-2 text-gray-600">{a.activity_date || '—'}</td>
                <td className="py-2">
                  <Badge
                    label={OPEN_ACCESS_STATUS_LABELS[a.open_access_status]}
                    status={a.open_access_status}
                  />
                </td>
                <td className="py-2">
                  <button
                    onClick={() => deleteMutation.mutate(a.id)}
                    className="text-red-600 hover:text-red-800 text-xs"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

// ── KPIs Tab ─────────────────────────────────────────

function KPIsTab({ projectId }: { projectId: string }) {
  const { data: definitions } = useKPIDefinitions();
  const { data: values, isLoading } = useKPIValues(projectId);

  if (isLoading) return <p className="text-gray-500">Loading KPIs...</p>;

  const defnMap = new Map(definitions?.items.map((d) => [d.id, d]) || []);

  return (
    <div>
      <h3 className="text-lg font-semibold mb-4">KPI and Indicator Tracking</h3>
      {definitions?.items.length ? (
        <div className="mb-4">
          <h4 className="text-sm font-medium text-gray-600 mb-2">Available Indicators</h4>
          <div className="flex flex-wrap gap-2">
            {definitions.items.map((d) => (
              <span
                key={d.id}
                className="bg-blue-50 text-blue-700 px-2 py-1 rounded text-xs"
              >
                {d.name} ({d.data_type})
              </span>
            ))}
          </div>
        </div>
      ) : null}
      {!values?.items.length ? (
        <p className="text-gray-500 text-sm">No KPI values recorded for this project.</p>
      ) : (
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-500 border-b">
              <th className="pb-2">Indicator</th>
              <th className="pb-2">Value</th>
              <th className="pb-2">Target</th>
              <th className="pb-2">Notes</th>
              <th className="pb-2">Recorded At</th>
            </tr>
          </thead>
          <tbody>
            {values.items.map((v) => {
              const defn = defnMap.get(v.kpi_definition_id);
              const displayValue =
                v.value_integer != null ? v.value_integer :
                v.value_decimal != null ? v.value_decimal :
                v.value_boolean != null ? (v.value_boolean ? 'Yes' : 'No') :
                v.value_text || '—';
              return (
                <tr key={v.id} className="border-b border-gray-100">
                  <td className="py-2 font-medium">{defn?.name || 'Unknown'}</td>
                  <td className="py-2">{String(displayValue)}</td>
                  <td className="py-2 text-gray-600">{v.target_value || '—'}</td>
                  <td className="py-2 text-gray-600">{v.notes || '—'}</td>
                  <td className="py-2 text-gray-600">
                    {v.recorded_at ? new Date(v.recorded_at).toLocaleDateString() : '—'}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
}

// ── Ethics & DMP Tab ─────────────────────────────────

function EthicsTab({ projectId }: { projectId: string }) {
  const { data: ethics, isLoading: ethLoading } = useEthicsRequirements(projectId);
  const { data: dmp, isLoading: dmpLoading } = useDataManagementRecords(projectId);
  const createEthics = useCreateEthicsRequirement(projectId);
  const deleteEthics = useDeleteEthicsRequirement(projectId);
  const createDMP = useCreateDataManagementRecord(projectId);
  const deleteDMP = useDeleteDataManagementRecord(projectId);

  if (ethLoading || dmpLoading) return <p className="text-gray-500">Loading...</p>;

  return (
    <div className="space-y-8">
      {/* Ethics Requirements */}
      <div>
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Ethics Requirements</h3>
          <button
            onClick={() =>
              createEthics.mutate({
                requirement_type: 'New Requirement',
                status: EthicsStatus.PENDING,
              })
            }
            className="bg-blue-700 text-white px-3 py-1.5 rounded text-sm hover:bg-blue-800"
          >
            + Add Requirement
          </button>
        </div>
        {!ethics?.items.length ? (
          <p className="text-gray-500 text-sm">No ethics requirements.</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b">
                <th className="pb-2">Type</th>
                <th className="pb-2">Status</th>
                <th className="pb-2">Due Date</th>
                <th className="pb-2">DPIA</th>
                <th className="pb-2">Consent</th>
                <th className="pb-2"></th>
              </tr>
            </thead>
            <tbody>
              {ethics.items.map((e) => (
                <tr key={e.id} className="border-b border-gray-100">
                  <td className="py-2 font-medium">{e.requirement_type}</td>
                  <td className="py-2">
                    <Badge label={ETHICS_STATUS_LABELS[e.status]} status={e.status} />
                  </td>
                  <td className="py-2 text-gray-600">{e.due_date || '—'}</td>
                  <td className="py-2">{e.dpia_required ? '✓' : '—'}</td>
                  <td className="py-2">{e.informed_consent_obtained ? '✓' : '—'}</td>
                  <td className="py-2">
                    <button
                      onClick={() => deleteEthics.mutate(e.id)}
                      className="text-red-600 hover:text-red-800 text-xs"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Data Management */}
      <div>
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Data Management Plan</h3>
          <button
            onClick={() =>
              createDMP.mutate({
                dataset_name: 'New Dataset',
                dmp_status: DMPStatus.DRAFT,
              })
            }
            className="bg-blue-700 text-white px-3 py-1.5 rounded text-sm hover:bg-blue-800"
          >
            + Add Dataset
          </button>
        </div>
        {!dmp?.items.length ? (
          <p className="text-gray-500 text-sm">No data management records.</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b">
                <th className="pb-2">Dataset</th>
                <th className="pb-2">Status</th>
                <th className="pb-2">Repository</th>
                <th className="pb-2">FAIR</th>
                <th className="pb-2"></th>
              </tr>
            </thead>
            <tbody>
              {dmp.items.map((d) => (
                <tr key={d.id} className="border-b border-gray-100">
                  <td className="py-2 font-medium">{d.dataset_name}</td>
                  <td className="py-2">
                    <Badge label={DMP_STATUS_LABELS[d.dmp_status]} status={d.dmp_status} />
                  </td>
                  <td className="py-2 text-gray-600">{d.repository || '—'}</td>
                  <td className="py-2">
                    <span className="text-xs space-x-1">
                      <span className={d.fair_findable ? 'text-green-600' : 'text-gray-400'}>F</span>
                      <span className={d.fair_accessible ? 'text-green-600' : 'text-gray-400'}>A</span>
                      <span className={d.fair_interoperable ? 'text-green-600' : 'text-gray-400'}>I</span>
                      <span className={d.fair_reusable ? 'text-green-600' : 'text-gray-400'}>R</span>
                    </span>
                  </td>
                  <td className="py-2">
                    <button
                      onClick={() => deleteDMP.mutate(d.id)}
                      className="text-red-600 hover:text-red-800 text-xs"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

// ── Amendments Tab ───────────────────────────────────

function AmendmentsTab({ projectId }: { projectId: string }) {
  const { data, isLoading } = useAmendments(projectId);
  const createMutation = useCreateAmendment(projectId);
  const deleteMutation = useDeleteAmendment(projectId);
  const [showForm, setShowForm] = useState(false);
  const [title, setTitle] = useState('');
  const [amendmentType, setAmendmentType] = useState<AmendmentType>(
    AmendmentType.BUDGET_TRANSFER,
  );
  const [description, setDescription] = useState('');

  if (isLoading) return <p className="text-gray-500">Loading...</p>;

  const nextNumber = (data?.items.length || 0) + 1;

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">Amendment Tracking</h3>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-blue-700 text-white px-3 py-1.5 rounded text-sm hover:bg-blue-800"
        >
          {showForm ? 'Cancel' : '+ Add Amendment'}
        </button>
      </div>
      {showForm && (
        <div className="bg-gray-50 p-4 rounded-lg mb-4 space-y-3">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
              <input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
              <select
                value={amendmentType}
                onChange={(e) => setAmendmentType(e.target.value as AmendmentType)}
                className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
              >
                {Object.entries(AMENDMENT_TYPE_LABELS).map(([k, v]) => (
                  <option key={k} value={k}>{v}</option>
                ))}
              </select>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
              rows={2}
            />
          </div>
          <button
            onClick={() => {
              createMutation.mutate(
                {
                  amendment_number: nextNumber,
                  amendment_type: amendmentType,
                  title,
                  description,
                  status: AmendmentStatus.DRAFT,
                },
                {
                  onSuccess: () => {
                    setShowForm(false);
                    setTitle('');
                    setDescription('');
                  },
                },
              );
            }}
            disabled={!title || !description || createMutation.isPending}
            className="bg-blue-700 text-white px-4 py-1.5 rounded text-sm hover:bg-blue-800 disabled:opacity-50"
          >
            Create
          </button>
        </div>
      )}
      {!data?.items.length ? (
        <p className="text-gray-500 text-sm">No amendments recorded.</p>
      ) : (
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-500 border-b">
              <th className="pb-2">#</th>
              <th className="pb-2">Title</th>
              <th className="pb-2">Type</th>
              <th className="pb-2">Status</th>
              <th className="pb-2">Request Date</th>
              <th className="pb-2">EC Decision</th>
              <th className="pb-2"></th>
            </tr>
          </thead>
          <tbody>
            {data.items.map((a) => (
              <tr key={a.id} className="border-b border-gray-100">
                <td className="py-2 text-gray-500">{a.amendment_number}</td>
                <td className="py-2 font-medium">{a.title}</td>
                <td className="py-2">{AMENDMENT_TYPE_LABELS[a.amendment_type]}</td>
                <td className="py-2">
                  <Badge label={AMENDMENT_STATUS_LABELS[a.status]} status={a.status} />
                </td>
                <td className="py-2 text-gray-600">{a.request_date || '—'}</td>
                <td className="py-2 text-gray-600">{a.ec_decision_date || '—'}</td>
                <td className="py-2">
                  <button
                    onClick={() => deleteMutation.mutate(a.id)}
                    className="text-red-600 hover:text-red-800 text-xs"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

// ── Notifications Tab ────────────────────────────────

function NotificationsTab({ projectId }: { projectId: string }) {
  const { data, isLoading } = useNotifications(projectId);
  const markRead = useMarkNotificationRead();
  const dismiss = useDismissNotification();

  if (isLoading) return <p className="text-gray-500">Loading...</p>;

  return (
    <div>
      <h3 className="text-lg font-semibold mb-4">Notifications</h3>
      {!data?.items.length ? (
        <p className="text-gray-500 text-sm">No notifications.</p>
      ) : (
        <div className="space-y-2">
          {data.items.map((n) => (
            <div
              key={n.id}
              className={`border rounded-lg p-3 ${
                n.status === NotificationStatus.PENDING
                  ? 'border-blue-200 bg-blue-50'
                  : n.status === NotificationStatus.DISMISSED
                  ? 'border-gray-200 bg-gray-50 opacity-60'
                  : 'border-gray-200 bg-white'
              }`}
            >
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <Badge
                      label={NOTIFICATION_PRIORITY_LABELS[n.priority]}
                      status={n.priority}
                    />
                    <span className="text-xs text-gray-500">
                      {NOTIFICATION_TYPE_LABELS[n.notification_type]}
                    </span>
                    <Badge
                      label={NOTIFICATION_STATUS_LABELS[n.status]}
                      status={n.status}
                    />
                  </div>
                  <h4 className="font-medium text-sm">{n.title}</h4>
                  <p className="text-xs text-gray-600 mt-0.5">{n.message}</p>
                </div>
                <div className="flex gap-2">
                  {n.status === NotificationStatus.PENDING && (
                    <button
                      onClick={() => markRead.mutate(n.id)}
                      className="text-blue-600 hover:text-blue-800 text-xs"
                    >
                      Mark Read
                    </button>
                  )}
                  {n.status !== NotificationStatus.DISMISSED && (
                    <button
                      onClick={() => dismiss.mutate(n.id)}
                      className="text-gray-500 hover:text-gray-700 text-xs"
                    >
                      Dismiss
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Main Component ───────────────────────────────────

export default function AdditionalFeaturesPanel({
  projectId,
}: {
  projectId: string;
}) {
  const [activeSubTab, setActiveSubTab] = useState<SubTabId>('ip');

  return (
    <div>
      {/* Sub-tabs */}
      <div className="flex gap-4 mb-6 border-b border-gray-100 pb-2">
        {SUB_TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveSubTab(tab.id)}
            className={`text-sm font-medium pb-1 ${
              activeSubTab === tab.id
                ? 'text-blue-700 border-b-2 border-blue-700'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {activeSubTab === 'ip' && <IPAssetsTab projectId={projectId} />}
      {activeSubTab === 'dissemination' && <DisseminationTab projectId={projectId} />}
      {activeSubTab === 'kpis' && <KPIsTab projectId={projectId} />}
      {activeSubTab === 'ethics' && <EthicsTab projectId={projectId} />}
      {activeSubTab === 'amendments' && <AmendmentsTab projectId={projectId} />}
      {activeSubTab === 'notifications' && <NotificationsTab projectId={projectId} />}
    </div>
  );
}
