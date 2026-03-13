import { Link } from 'react-router-dom';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { usePIDashboard } from '../hooks/useDashboards';
import { PROGRAMME_LABELS, STATUS_LABELS } from '../types';
import type { PIProjectSummary, CrossProjectDeadline } from '../types';

function fmt(value: number | string): string {
  const n = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(n)) return String(value);
  return n.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

function SummaryCard({
  label,
  value,
  sub,
}: {
  label: string;
  value: string;
  sub?: string;
}) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-5">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
      {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
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

function BurnBar({ pct }: { pct: number }) {
  const width = Math.min(pct, 100);
  const bg =
    pct >= 95 ? 'bg-red-500' : pct >= 80 ? 'bg-yellow-500' : 'bg-blue-500';
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 bg-gray-100 rounded-full h-2 overflow-hidden">
        <div className={`h-2 rounded-full ${bg}`} style={{ width: `${width}%` }} />
      </div>
      <span className="text-xs text-gray-500 w-12 text-right">{fmt(pct)}%</span>
    </div>
  );
}

function ProjectsGrid({ projects }: { projects: PIProjectSummary[] }) {
  if (projects.length === 0) {
    return (
      <div className="text-center py-12 text-gray-400">
        No projects found
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200 text-left text-gray-500">
            <th className="py-3 px-3 font-medium">Status</th>
            <th className="py-3 px-3 font-medium">Project</th>
            <th className="py-3 px-3 font-medium">Programme</th>
            <th className="py-3 px-3 font-medium">Next Deadline</th>
            <th className="py-3 px-3 font-medium">Budget</th>
            <th className="py-3 px-3 font-medium">Burn Rate</th>
            <th className="py-3 px-3 font-medium text-center">Team</th>
            <th className="py-3 px-3 font-medium text-center">Risks</th>
            <th className="py-3 px-3 font-medium text-center">Amendments</th>
          </tr>
        </thead>
        <tbody>
          {projects.map((p) => (
            <tr key={p.project_id} className="border-b border-gray-100 hover:bg-gray-50">
              <td className="py-3 px-3">
                <TrafficDot color={p.traffic_light} />
              </td>
              <td className="py-3 px-3">
                <Link
                  to={`/projects/${p.project_id}/dashboard`}
                  className="text-blue-600 hover:underline font-medium"
                >
                  {p.acronym}
                </Link>
                <span className="block text-xs text-gray-400">
                  {STATUS_LABELS[p.status] || p.status}
                </span>
              </td>
              <td className="py-3 px-3 text-gray-600">
                {PROGRAMME_LABELS[p.programme] || p.programme}
              </td>
              <td className="py-3 px-3 text-gray-600">
                {p.next_deadline ? (
                  <>
                    <span>{new Date(p.next_deadline).toLocaleDateString()}</span>
                    <span className="block text-xs text-gray-400">
                      {p.next_deadline_type}
                    </span>
                  </>
                ) : (
                  <span className="text-gray-300">—</span>
                )}
              </td>
              <td className="py-3 px-3 text-gray-600">
                <span className="block">€{fmt(p.budget_spent)}</span>
                <span className="text-xs text-gray-400">
                  of €{fmt(p.budget_total)}
                </span>
              </td>
              <td className="py-3 px-3 w-40">
                <BurnBar pct={Number(p.burn_rate_pct)} />
              </td>
              <td className="py-3 px-3 text-center text-gray-600">{p.team_size}</td>
              <td className="py-3 px-3 text-center">
                {p.open_risks > 0 ? (
                  <span className="inline-block px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-700">
                    {p.open_risks}
                  </span>
                ) : (
                  <span className="text-gray-300">0</span>
                )}
              </td>
              <td className="py-3 px-3 text-center">
                {p.active_amendments > 0 ? (
                  <span className="inline-block px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-700">
                    {p.active_amendments}
                  </span>
                ) : (
                  <span className="text-gray-300">0</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function DeadlinesTable({ deadlines }: { deadlines: CrossProjectDeadline[] }) {
  if (deadlines.length === 0) {
    return <p className="text-gray-400 text-sm py-4">No upcoming deadlines</p>;
  }

  return (
    <table className="min-w-full text-sm">
      <thead>
        <tr className="border-b border-gray-200 text-left text-gray-500">
          <th className="py-2 px-3 font-medium">Project</th>
          <th className="py-2 px-3 font-medium">Type</th>
          <th className="py-2 px-3 font-medium">Date</th>
          <th className="py-2 px-3 font-medium text-right">Days Until</th>
        </tr>
      </thead>
      <tbody>
        {deadlines.map((d, i) => {
          const urgent = d.days_until <= 14;
          return (
            <tr key={i} className="border-b border-gray-100">
              <td className="py-2 px-3">
                <Link
                  to={`/projects/${d.project_id}`}
                  className="text-blue-600 hover:underline"
                >
                  {d.project_acronym}
                </Link>
              </td>
              <td className="py-2 px-3 text-gray-600">{d.deadline_type}</td>
              <td className="py-2 px-3 text-gray-600">
                {new Date(d.date).toLocaleDateString()}
              </td>
              <td className="py-2 px-3 text-right">
                <span
                  className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${
                    urgent
                      ? 'bg-red-100 text-red-700'
                      : 'bg-gray-100 text-gray-600'
                  }`}
                >
                  {d.days_until}d
                </span>
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}

function BudgetChart({ projects }: { projects: PIProjectSummary[] }) {
  if (projects.length === 0) return null;

  const data = projects.map((p) => ({
    name: p.acronym,
    budget: Number(p.budget_total),
    spent: Number(p.budget_spent),
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} margin={{ top: 5, right: 20, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" />
        <YAxis tickFormatter={(v: number) => `€${(v / 1000).toFixed(0)}k`} />
        <Tooltip
          formatter={(value: number) => `€${fmt(value)}`}
          labelStyle={{ fontWeight: 600 }}
        />
        <Legend />
        <Bar dataKey="budget" name="Budget" fill="#93c5fd" radius={[4, 4, 0, 0]} />
        <Bar dataKey="spent" name="Spent" fill="#3b82f6" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

export default function PIDashboardPage() {
  const { data, isLoading, error } = usePIDashboard();

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
        Failed to load dashboard data
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">PI Dashboard</h1>
        <p className="text-sm text-gray-500 mt-1">Portfolio overview across all projects</p>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <SummaryCard
          label="Total Budget"
          value={`€${fmt(data.total_budget)}`}
        />
        <SummaryCard
          label="Total Spent"
          value={`€${fmt(data.total_spent)}`}
        />
        <SummaryCard
          label="Overall Burn Rate"
          value={`${fmt(data.overall_burn_rate)}%`}
        />
        <SummaryCard
          label="Active Projects"
          value={String(data.active_project_count)}
          sub={`${data.projects.length} total`}
        />
      </div>

      {/* Projects grid */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Projects</h2>
        <ProjectsGrid projects={data.projects} />
      </div>

      {/* Budget chart + Deadlines side by side */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Budget vs Spent
          </h2>
          <BudgetChart projects={data.projects} />
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Upcoming Deadlines
          </h2>
          <DeadlinesTable deadlines={data.cross_project_deadlines} />
        </div>
      </div>
    </div>
  );
}
