import { useParams, Link } from 'react-router-dom';
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { useProjectDashboard } from '../hooks/useDashboards';
import {
  WP_STATUS_LABELS,
  DELIVERABLE_TYPE_LABELS,
  EC_REVIEW_LABELS,
  TRAFFIC_LIGHT_LABELS,
  RISK_CATEGORY_LABELS,
  RISK_LEVEL_LABELS,
  RISK_STATUS_LABELS,
} from '../types';
import type {
  WPProgressItem,
  DeliverableTimelineItem,
  BudgetCategoryItem,
  PartnerStatusItem,
  ProjectRiskSummary,
} from '../types';

function fmt(value: number | string): string {
  const n = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(n)) return String(value);
  return n.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

function KPICard({
  label,
  value,
  status,
}: {
  label: string;
  value: string;
  status?: 'healthy' | 'warning' | 'critical';
}) {
  const ring =
    status === 'critical'
      ? 'border-red-300'
      : status === 'warning'
        ? 'border-yellow-300'
        : 'border-green-300';
  return (
    <div className={`bg-white rounded-lg border-2 ${ring} p-5`}>
      <p className="text-sm text-gray-500">{label}</p>
      <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
    </div>
  );
}

function TrafficDot({ color }: { color: string }) {
  const bg =
    color === 'RED'
      ? 'bg-red-500'
      : color === 'AMBER'
        ? 'bg-yellow-500'
        : 'bg-green-500';
  return <span className={`inline-block w-3 h-3 rounded-full ${bg}`} />;
}

function ProgressBar({
  pct,
  color = 'bg-blue-500',
}: {
  pct: number;
  color?: string;
}) {
  const w = Math.min(pct, 100);
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 bg-gray-100 rounded-full h-2.5 overflow-hidden">
        <div className={`h-2.5 rounded-full ${color}`} style={{ width: `${w}%` }} />
      </div>
      <span className="text-xs text-gray-500 w-12 text-right">{fmt(pct)}%</span>
    </div>
  );
}

function WPProgressSection({ items }: { items: WPProgressItem[] }) {
  if (items.length === 0) {
    return <p className="text-gray-400 text-sm py-4">No work packages</p>;
  }

  return (
    <div className="space-y-4">
      {items.map((wp, i) => {
        const statusColor =
          wp.status === 'COMPLETED'
            ? 'bg-green-100 text-green-700'
            : wp.status === 'DELAYED'
              ? 'bg-red-100 text-red-700'
              : wp.status === 'IN_PROGRESS'
                ? 'bg-blue-100 text-blue-700'
                : 'bg-gray-100 text-gray-600';
        return (
          <div key={i} className="border border-gray-100 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <div>
                <span className="font-medium text-gray-900">
                  WP{wp.wp_number}
                </span>
                <span className="text-gray-500 ml-2">{wp.wp_title}</span>
              </div>
              <span
                className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${statusColor}`}
              >
                {WP_STATUS_LABELS[wp.status] || wp.status}
              </span>
            </div>
            <ProgressBar pct={Number(wp.progress_pct)} />
            <p className="text-xs text-gray-400 mt-1">
              {wp.deliverables_completed} / {wp.deliverables_total} deliverables
              completed
            </p>
          </div>
        );
      })}
    </div>
  );
}

function DeliverableTimeline({
  items,
}: {
  items: DeliverableTimelineItem[];
}) {
  if (items.length === 0) {
    return <p className="text-gray-400 text-sm py-4">No deliverables</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200 text-left text-gray-500">
            <th className="py-2 px-3 font-medium">Status</th>
            <th className="py-2 px-3 font-medium">Number</th>
            <th className="py-2 px-3 font-medium">Title</th>
            <th className="py-2 px-3 font-medium">Type</th>
            <th className="py-2 px-3 font-medium text-center">Due Month</th>
            <th className="py-2 px-3 font-medium">Submitted</th>
            <th className="py-2 px-3 font-medium">EC Review</th>
          </tr>
        </thead>
        <tbody>
          {items.map((d, i) => (
            <tr key={i} className="border-b border-gray-100 hover:bg-gray-50">
              <td className="py-2 px-3">
                <TrafficDot color={d.traffic_light} />
              </td>
              <td className="py-2 px-3 font-medium text-gray-900">
                {d.deliverable_number || '—'}
              </td>
              <td className="py-2 px-3 text-gray-600">{d.title}</td>
              <td className="py-2 px-3 text-gray-500 text-xs">
                {DELIVERABLE_TYPE_LABELS[d.deliverable_type] || d.deliverable_type}
              </td>
              <td className="py-2 px-3 text-center text-gray-600">
                {d.due_month ?? '—'}
              </td>
              <td className="py-2 px-3 text-gray-600">
                {d.submission_date
                  ? new Date(d.submission_date).toLocaleDateString()
                  : '—'}
              </td>
              <td className="py-2 px-3">
                <span
                  className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${
                    d.ec_review_status === 'APPROVED'
                      ? 'bg-green-100 text-green-700'
                      : d.ec_review_status === 'REJECTED' ||
                          d.ec_review_status === 'REVISION_REQUESTED'
                        ? 'bg-red-100 text-red-700'
                        : 'bg-gray-100 text-gray-600'
                  }`}
                >
                  {EC_REVIEW_LABELS[d.ec_review_status] || d.ec_review_status}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

const PIE_COLORS = [
  '#3b82f6',
  '#10b981',
  '#f59e0b',
  '#ef4444',
  '#8b5cf6',
  '#ec4899',
  '#06b6d4',
];

function BudgetPieChart({ items }: { items: BudgetCategoryItem[] }) {
  if (items.length === 0) {
    return <p className="text-gray-400 text-sm py-4">No expense data by category</p>;
  }

  const data = items.map((c) => ({
    name: c.category_label,
    value: Number(c.spent),
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={data}
          dataKey="value"
          nameKey="name"
          cx="50%"
          cy="50%"
          outerRadius={100}
          label={({ name, percent }: { name: string; percent: number }) =>
            `${name} (${(percent * 100).toFixed(0)}%)`
          }
          labelLine
        >
          {data.map((_, i) => (
            <Cell
              key={`cell-${i}`}
              fill={PIE_COLORS[i % PIE_COLORS.length]}
            />
          ))}
        </Pie>
        <Tooltip formatter={(value: number) => `€${fmt(value)}`} />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
}

function PartnersTable({ items }: { items: PartnerStatusItem[] }) {
  if (items.length === 0) {
    return <p className="text-gray-400 text-sm py-4">No partner data</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200 text-left text-gray-500">
            <th className="py-2 px-3 font-medium">Partner</th>
            <th className="py-2 px-3 font-medium">Country</th>
            <th className="py-2 px-3 font-medium text-right">Allocated</th>
            <th className="py-2 px-3 font-medium text-right">Spent</th>
            <th className="py-2 px-3 font-medium">Progress</th>
          </tr>
        </thead>
        <tbody>
          {items.map((p) => (
            <tr key={p.partner_id} className="border-b border-gray-100 hover:bg-gray-50">
              <td className="py-2 px-3 font-medium text-gray-900">
                {p.partner_name}
              </td>
              <td className="py-2 px-3 text-gray-600">{p.country || '—'}</td>
              <td className="py-2 px-3 text-right text-gray-600">
                €{fmt(p.allocated_budget)}
              </td>
              <td className="py-2 px-3 text-right text-gray-600">
                €{fmt(p.spent)}
              </td>
              <td className="py-2 px-3 w-36">
                <ProgressBar pct={Number(p.pct_used)} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function RiskMatrix({ risks }: { risks: ProjectRiskSummary[] }) {
  if (risks.length === 0) {
    return <p className="text-gray-400 text-sm py-4">No risks recorded</p>;
  }

  const riskColor = (prob: string, impact: string) => {
    const score =
      (['LOW', 'MEDIUM', 'HIGH'].indexOf(prob) + 1) *
      (['LOW', 'MEDIUM', 'HIGH'].indexOf(impact) + 1);
    if (score >= 6) return 'bg-red-100 text-red-800';
    if (score >= 3) return 'bg-yellow-100 text-yellow-800';
    return 'bg-green-100 text-green-800';
  };

  return (
    <div className="space-y-3">
      {risks.map((r) => {
        const color = riskColor(r.probability, r.impact);
        return (
          <div key={r.risk_id} className={`rounded-lg p-3 ${color}`}>
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-medium uppercase">
                {RISK_CATEGORY_LABELS[r.category] || r.category}
              </span>
              <span
                className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${
                  r.status === 'OPEN'
                    ? 'bg-white/50'
                    : r.status === 'MITIGATED'
                      ? 'bg-green-200 text-green-800'
                      : 'bg-gray-200 text-gray-600'
                }`}
              >
                {RISK_STATUS_LABELS[r.status] || r.status}
              </span>
            </div>
            <p className="text-sm">{r.description}</p>
            <div className="flex gap-4 mt-1 text-xs opacity-80">
              <span>
                Probability: {RISK_LEVEL_LABELS[r.probability] || r.probability}
              </span>
              <span>
                Impact: {RISK_LEVEL_LABELS[r.impact] || r.impact}
              </span>
              {r.owner && <span>Owner: {r.owner}</span>}
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default function ProjectDashboardPage() {
  const { id } = useParams<{ id: string }>();
  const { data, isLoading, error } = useProjectDashboard(id);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="text-center py-12 text-red-500">
        Failed to load project dashboard
      </div>
    );
  }

  const burnStatus =
    data.burn_rate_status === 'critical'
      ? 'critical'
      : data.burn_rate_status === 'warning'
        ? 'warning'
        : 'healthy';

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {data.acronym} — Project Dashboard
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            €{fmt(data.total_spent)} spent of €{fmt(data.total_budget)} total
            budget
          </p>
        </div>
        <Link
          to={`/projects/${data.project_id}`}
          className="text-sm text-blue-600 hover:underline"
        >
          ← Back to Project
        </Link>
      </div>

      {/* KPI cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <KPICard
          label="Burn Rate"
          value={`${fmt(data.burn_rate)}%`}
          status={burnStatus}
        />
        <KPICard
          label="PM Compliance"
          value={`${fmt(data.pm_compliance_rate)}%`}
        />
        <KPICard
          label="Deliverable Completion"
          value={`${fmt(data.deliverable_completion_rate)}%`}
        />
      </div>

      {/* WP progress */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Work Package Progress
        </h2>
        <WPProgressSection items={data.wp_progress} />
      </div>

      {/* Deliverable timeline */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Deliverable Timeline
        </h2>
        <DeliverableTimeline items={data.deliverable_timeline} />
      </div>

      {/* Budget pie + Partners side by side */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Spending by EC Category
          </h2>
          <BudgetPieChart items={data.budget_by_category} />
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Partner Status
          </h2>
          <PartnersTable items={data.partner_status} />
        </div>
      </div>

      {/* Risks */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Risk Register
        </h2>
        <RiskMatrix risks={data.risks} />
      </div>
    </div>
  );
}
