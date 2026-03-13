import { useState } from 'react';
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
import { useFinanceDashboard } from '../hooks/useReports';
import {
  PROGRAMME_LABELS,
  STATUS_LABELS,
  COST_MODEL_LABELS,
  RESEARCHER_POSITION_LABELS,
  CONTRACT_TYPE_LABELS,
} from '../types';
import type {
  ProjectFinancialRow,
  FlaggedItem,
  UpcomingECPayment,
  RecruitmentPlanItem,
} from '../types';

function fmt(value: string): string {
  const n = parseFloat(value);
  if (isNaN(n)) return value;
  return n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function BurnRateBadge({ status, pct }: { status: string; pct: string }) {
  const colors =
    status === 'over_spending'
      ? 'bg-red-100 text-red-800'
      : status === 'under_spending'
        ? 'bg-yellow-100 text-yellow-800'
        : 'bg-green-100 text-green-800';
  return (
    <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${colors}`}>
      {fmt(pct)}%
    </span>
  );
}

function SeverityBadge({ severity }: { severity: string }) {
  const colors =
    severity === 'CRITICAL' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800';
  return (
    <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${colors}`}>
      {severity}
    </span>
  );
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
      {sub && <p className="text-sm text-gray-500 mt-1">{sub}</p>}
    </div>
  );
}

function ProjectsTable({ projects }: { projects: ProjectFinancialRow[] }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      <div className="px-5 py-3 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">Projects Overview</h2>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Acronym
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Programme
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Status
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                Budget
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                Spent
              </th>
              <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                Burn Rate
              </th>
              <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                PM Compliance
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Flags
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {projects.map((p) => (
              <tr key={p.project_id} className="hover:bg-gray-50">
                <td className="px-4 py-3">
                  <Link
                    to={`/projects/${p.project_id}`}
                    className="text-blue-700 hover:underline font-medium"
                  >
                    {p.acronym}
                  </Link>
                </td>
                <td className="px-4 py-3 text-sm text-gray-600">
                  {PROGRAMME_LABELS[p.programme]}
                </td>
                <td className="px-4 py-3 text-sm text-gray-600">{STATUS_LABELS[p.status]}</td>
                <td className="px-4 py-3 text-sm text-gray-900 text-right font-mono">
                  {fmt(p.total_budget)}
                </td>
                <td className="px-4 py-3 text-sm text-gray-900 text-right font-mono">
                  {fmt(p.total_spent)}
                </td>
                <td className="px-4 py-3 text-center">
                  <BurnRateBadge status={p.burn_rate_status} pct={p.burn_rate_percentage} />
                </td>
                <td className="px-4 py-3 text-center text-sm">{fmt(p.pm_compliance_rate)}%</td>
                <td className="px-4 py-3">
                  <div className="flex flex-wrap gap-1">
                    {p.flags.map((f, i) => (
                      <span
                        key={i}
                        className="inline-block px-1.5 py-0.5 rounded text-xs bg-gray-100 text-gray-700"
                      >
                        {f}
                      </span>
                    ))}
                  </div>
                </td>
              </tr>
            ))}
            {projects.length === 0 && (
              <tr>
                <td colSpan={8} className="px-4 py-8 text-center text-gray-500">
                  No projects found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function FlaggedItemsPanel({ items }: { items: FlaggedItem[] }) {
  if (items.length === 0) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-5">
        <h2 className="text-lg font-semibold text-gray-900 mb-3">Flagged Items</h2>
        <p className="text-sm text-gray-500">No flagged items.</p>
      </div>
    );
  }
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-5">
      <h2 className="text-lg font-semibold text-gray-900 mb-3">
        Flagged Items ({items.length})
      </h2>
      <div className="space-y-3">
        {items.map((item, i) => (
          <div key={i} className="flex items-start gap-3 text-sm">
            <SeverityBadge severity={item.severity} />
            <div>
              <span className="font-medium">{item.acronym}</span>
              <span className="text-gray-400 mx-1">&middot;</span>
              <span className="text-gray-600">{item.description}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function UpcomingPaymentsPanel({ payments }: { payments: UpcomingECPayment[] }) {
  if (payments.length === 0) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-5">
        <h2 className="text-lg font-semibold text-gray-900 mb-3">Upcoming EC Payments</h2>
        <p className="text-sm text-gray-500">No upcoming payments.</p>
      </div>
    );
  }
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-5">
      <h2 className="text-lg font-semibold text-gray-900 mb-3">Upcoming EC Payments</h2>
      <div className="space-y-2">
        {payments.map((p, i) => (
          <div key={i} className="flex justify-between items-center text-sm">
            <div>
              <span className="font-medium">{p.acronym}</span>
              <span className="text-gray-400 mx-1">&middot;</span>
              <span className="text-gray-500">{p.payment_type.replace('_', ' ')}</span>
            </div>
            <div className="text-right">
              <span className="font-mono font-medium">{fmt(p.expected_amount)}</span>
              <span className="text-gray-400 ml-2 text-xs">{p.expected_date}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function BudgetVsSpentChart({ projects }: { projects: ProjectFinancialRow[] }) {
  if (projects.length === 0) return null;

  const data = projects.map((p) => ({
    name: p.acronym,
    budget: parseFloat(p.total_budget),
    spent: parseFloat(p.total_spent),
  }));

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-5">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Budget vs Spent</h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} margin={{ top: 5, right: 20, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis tickFormatter={(v: number) => `€${(v / 1000).toFixed(0)}k`} />
          <Tooltip
            formatter={(value: number) =>
              `€${value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
            }
            labelStyle={{ fontWeight: 600 }}
          />
          <Legend />
          <Bar dataKey="budget" name="Budget" fill="#93c5fd" radius={[4, 4, 0, 0]} />
          <Bar dataKey="spent" name="Spent" fill="#3b82f6" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

function RecruitmentTable({ items }: { items: RecruitmentPlanItem[] }) {
  if (items.length === 0) return null;
  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      <div className="px-5 py-3 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">Recruitment Plans</h2>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Project
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Researcher
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Position
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Contract
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Contract End
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                Budget Remaining
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {items.map((r, i) => (
              <tr key={i} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-sm font-medium">{r.acronym}</td>
                <td className="px-4 py-3 text-sm text-gray-600">{r.researcher_name}</td>
                <td className="px-4 py-3 text-sm text-gray-600">
                  {RESEARCHER_POSITION_LABELS[r.position]}
                </td>
                <td className="px-4 py-3 text-sm text-gray-600">
                  {CONTRACT_TYPE_LABELS[r.contract_type]}
                </td>
                <td className="px-4 py-3 text-sm text-gray-600">{r.contract_end ?? '—'}</td>
                <td className="px-4 py-3 text-sm text-gray-900 text-right font-mono">
                  {fmt(r.funding_source_budget_remaining)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default function FinanceDashboardPage() {
  const { data, isLoading, error } = useFinanceDashboard();

  if (isLoading) {
    return <p className="text-gray-500 py-8 text-center">Loading dashboard...</p>;
  }
  if (error || !data) {
    return (
      <p className="text-red-600 py-8 text-center">
        Failed to load dashboard. Make sure you have Central Finance PM access.
      </p>
    );
  }

  const activeCount = data.projects.filter(
    (p) => p.status === 'ACTIVE' || p.status === 'NEGOTIATION',
  ).length;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Finance Dashboard</h1>
        <p className="text-sm text-gray-500">
          Generated {new Date(data.generated_at).toLocaleString()}
        </p>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <SummaryCard
          label="Total Budget"
          value={`\u20AC ${fmt(data.total_budget_all_projects)}`}
          sub={`${data.projects.length} projects`}
        />
        <SummaryCard
          label="Total Spent"
          value={`\u20AC ${fmt(data.total_spent_all_projects)}`}
        />
        <SummaryCard
          label="Overall Burn Rate"
          value={`${fmt(data.overall_burn_rate)}%`}
        />
        <SummaryCard
          label="Active Projects"
          value={String(activeCount)}
          sub={`of ${data.projects.length} total`}
        />
      </div>

      {/* Projects table */}
      <ProjectsTable projects={data.projects} />

      {/* Budget vs Spent chart */}
      <BudgetVsSpentChart projects={data.projects} />

      {/* Two-column: Payments + Flags */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <UpcomingPaymentsPanel payments={data.upcoming_ec_payments} />
        <FlaggedItemsPanel items={data.flagged_items} />
      </div>

      {/* Recruitment plans */}
      <RecruitmentTable items={data.recruitment_plans} />
    </div>
  );
}
