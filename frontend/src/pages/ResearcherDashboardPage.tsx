import { useParams, Link } from 'react-router-dom';
import { useResearcherDashboard } from '../hooks/useDashboards';
import type {
  ResearcherAllocationSummary,
  TimesheetStatusItem,
  ResearcherDeadline,
} from '../types';

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

function AllocationsTable({
  allocations,
}: {
  allocations: ResearcherAllocationSummary[];
}) {
  if (allocations.length === 0) {
    return <p className="text-gray-400 text-sm py-4">No allocations found</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200 text-left text-gray-500">
            <th className="py-3 px-3 font-medium">Project</th>
            <th className="py-3 px-3 font-medium">Work Package</th>
            <th className="py-3 px-3 font-medium text-right">Planned PM</th>
            <th className="py-3 px-3 font-medium text-right">Actual PM</th>
            <th className="py-3 px-3 font-medium">Period</th>
            <th className="py-3 px-3 font-medium">Progress</th>
          </tr>
        </thead>
        <tbody>
          {allocations.map((a, i) => {
            const pct =
              Number(a.planned_pm) > 0
                ? (Number(a.actual_pm) / Number(a.planned_pm)) * 100
                : 0;
            return (
              <tr key={i} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="py-3 px-3">
                  <Link
                    to={`/projects/${a.project_id}`}
                    className="text-blue-600 hover:underline font-medium"
                  >
                    {a.project_acronym}
                  </Link>
                </td>
                <td className="py-3 px-3 text-gray-600">
                  {a.wp_title || <span className="text-gray-300">—</span>}
                </td>
                <td className="py-3 px-3 text-right text-gray-600">
                  {fmt(a.planned_pm)}
                </td>
                <td className="py-3 px-3 text-right text-gray-600">
                  {fmt(a.actual_pm)}
                </td>
                <td className="py-3 px-3 text-gray-500 text-xs">
                  {a.period_start && a.period_end
                    ? `${new Date(a.period_start).toLocaleDateString()} – ${new Date(a.period_end).toLocaleDateString()}`
                    : '—'}
                </td>
                <td className="py-3 px-3 w-32">
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-gray-100 rounded-full h-2 overflow-hidden">
                      <div
                        className="h-2 rounded-full bg-blue-500"
                        style={{ width: `${Math.min(pct, 100)}%` }}
                      />
                    </div>
                    <span className="text-xs text-gray-500 w-10 text-right">
                      {pct.toFixed(0)}%
                    </span>
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function TimesheetGrid({ items }: { items: TimesheetStatusItem[] }) {
  if (items.length === 0) {
    return <p className="text-gray-400 text-sm py-4">No timesheet data</p>;
  }

  // Group by project, columns = months
  const projects = [...new Set(items.map((i) => i.project_acronym))];
  const months = [...new Set(items.map((i) => i.month))].sort();

  const statusColor = (status: string) => {
    switch (status) {
      case 'complete':
        return 'bg-green-500';
      case 'incomplete':
        return 'bg-yellow-400';
      default:
        return 'bg-gray-200';
    }
  };

  return (
    <div className="overflow-x-auto">
      <table className="text-sm">
        <thead>
          <tr className="text-gray-500">
            <th className="py-2 px-3 text-left font-medium">Project</th>
            {months.map((m) => (
              <th key={m} className="py-2 px-3 text-center font-medium">
                {m}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {projects.map((proj) => (
            <tr key={proj} className="border-t border-gray-100">
              <td className="py-2 px-3 font-medium text-gray-700">{proj}</td>
              {months.map((month) => {
                const item = items.find(
                  (i) => i.project_acronym === proj && i.month === month,
                );
                return (
                  <td key={month} className="py-2 px-3 text-center">
                    {item ? (
                      <div className="flex flex-col items-center gap-1">
                        <span
                          className={`inline-block w-4 h-4 rounded-sm ${statusColor(item.status)}`}
                          title={`${fmt(item.hours_logged)}h / ${fmt(item.hours_expected)}h`}
                        />
                        <span className="text-xs text-gray-400">
                          {fmt(item.hours_logged)}h
                        </span>
                      </div>
                    ) : (
                      <span className="text-gray-300">—</span>
                    )}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function DeadlinesList({ deadlines }: { deadlines: ResearcherDeadline[] }) {
  if (deadlines.length === 0) {
    return <p className="text-gray-400 text-sm py-4">No upcoming deadlines</p>;
  }

  return (
    <ul className="divide-y divide-gray-100">
      {deadlines.map((d, i) => {
        const urgent = d.days_until <= 14;
        return (
          <li key={i} className="py-3 flex items-center justify-between">
            <div>
              <Link
                to={`/projects/${d.project_id}`}
                className="text-blue-600 hover:underline text-sm font-medium"
              >
                {d.project_acronym}
              </Link>
              <span className="text-gray-500 text-sm ml-2">{d.title}</span>
              <span className="block text-xs text-gray-400">
                {d.deadline_type} · {new Date(d.due_date).toLocaleDateString()}
              </span>
            </div>
            <span
              className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${
                urgent
                  ? 'bg-red-100 text-red-700'
                  : 'bg-gray-100 text-gray-600'
              }`}
            >
              {d.days_until}d
            </span>
          </li>
        );
      })}
    </ul>
  );
}

export default function ResearcherDashboardPage() {
  const { researcherId } = useParams<{ researcherId: string }>();
  const { data, isLoading, error } = useResearcherDashboard(researcherId);

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
        Failed to load researcher dashboard
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome, {data.researcher_name}
        </h1>
        <p className="text-sm text-gray-500 mt-1">
          Your project allocations and upcoming tasks
        </p>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <SummaryCard
          label="Total Planned PM"
          value={fmt(data.total_planned_pm)}
        />
        <SummaryCard
          label="Total Actual PM"
          value={fmt(data.total_actual_pm)}
        />
        <SummaryCard
          label="Active Projects"
          value={String(data.allocations.length)}
          sub="allocations"
        />
      </div>

      {/* PM Allocations */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          PM Allocations
        </h2>
        <AllocationsTable allocations={data.allocations} />
      </div>

      {/* Timesheet status + Deadlines side by side */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Timesheet Status
          </h2>
          <div className="flex items-center gap-4 mb-3 text-xs text-gray-500">
            <span className="flex items-center gap-1">
              <span className="inline-block w-3 h-3 rounded-sm bg-green-500" /> Complete
            </span>
            <span className="flex items-center gap-1">
              <span className="inline-block w-3 h-3 rounded-sm bg-yellow-400" /> Incomplete
            </span>
            <span className="flex items-center gap-1">
              <span className="inline-block w-3 h-3 rounded-sm bg-gray-200" /> Not Started
            </span>
          </div>
          <TimesheetGrid items={data.timesheet_status} />
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Upcoming Deadlines
          </h2>
          <DeadlinesList deadlines={data.upcoming_deadlines} />
        </div>
      </div>
    </div>
  );
}
