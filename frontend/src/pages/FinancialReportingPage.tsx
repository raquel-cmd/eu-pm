import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useFinancialReport } from '../hooks/useFinancialReporting';
import { useReportingPeriods } from '../hooks/useReporting';
import {
  FINANCIAL_STATEMENT_STATUS_LABELS,
  COMPLETION_STATUS_LABELS,
  type CostModelFinancialReport,
  type FormCReport,
  type LumpSumReport,
  type UnitCostReport,
  type InstitutionalReport,
  type CategoryBreakdownRow,
  type WPCompletionDeclaration,
  type UnitDeliveryRecord,
  type InstitutionalMappingRow,
  FinancialStatementStatus,
  CompletionStatus,
} from '../types';

function fmt(value: string | number): string {
  const n = typeof value === 'number' ? value : parseFloat(value);
  if (isNaN(n)) return String(value);
  return n.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

function CostModelBadge({ costModel }: { costModel: string }) {
  const colors: Record<string, string> = {
    ACTUAL_COSTS: 'bg-blue-100 text-blue-800',
    LUMP_SUM: 'bg-purple-100 text-purple-800',
    UNIT_COSTS: 'bg-green-100 text-green-800',
    MIXED: 'bg-orange-100 text-orange-800',
  };
  const labels: Record<string, string> = {
    ACTUAL_COSTS: 'Actual Costs',
    LUMP_SUM: 'Lump Sum',
    UNIT_COSTS: 'Unit Costs',
    MIXED: 'Mixed',
  };
  return (
    <span
      className={`px-2 py-1 rounded text-xs font-medium ${colors[costModel] ?? 'bg-gray-100 text-gray-800'}`}
    >
      {labels[costModel] ?? costModel}
    </span>
  );
}

function FormCSection({ report }: { report: FormCReport }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Form C Financial Statement
      </h3>
      <div className="text-sm text-gray-600 mb-4">
        Period: {report.period_start} to {report.period_end}
        {report.partner_id && (
          <span className="ml-2 text-gray-500">
            Partner: {report.partner_id}
          </span>
        )}
      </div>

      {/* Category Breakdown Table */}
      <div className="overflow-x-auto mb-4">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="text-left py-2 pr-4 font-medium text-gray-600">
                EC Category
              </th>
              <th className="text-left py-2 pr-4 font-medium text-gray-600">
                University Code
              </th>
              <th className="text-right py-2 pr-4 font-medium text-gray-600">
                Incurred
              </th>
              <th className="text-right py-2 font-medium text-gray-600">
                EC Eligible
              </th>
            </tr>
          </thead>
          <tbody>
            {report.category_breakdown
              .filter(
                (r: CategoryBreakdownRow) =>
                  parseFloat(r.incurred) > 0 ||
                  parseFloat(r.ec_eligible) > 0,
              )
              .map((row: CategoryBreakdownRow) => (
                <tr
                  key={row.ec_category}
                  className="border-b border-gray-100"
                >
                  <td className="py-2 pr-4 font-medium">
                    {row.ec_category}
                  </td>
                  <td className="py-2 pr-4 text-gray-500">
                    {row.university_account_code ?? '—'}
                  </td>
                  <td className="py-2 pr-4 text-right">
                    {fmt(row.incurred)}
                  </td>
                  <td className="py-2 text-right">
                    {fmt(row.ec_eligible)}
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>

      {/* Totals */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-gray-50 rounded p-3">
          <div className="text-xs text-gray-500">Total Direct</div>
          <div className="text-lg font-semibold">
            {fmt(report.total_direct_costs)}
          </div>
        </div>
        <div className="bg-gray-50 rounded p-3">
          <div className="text-xs text-gray-500">
            Indirect ({fmt(parseFloat(report.indirect_rate) * 100)}%)
          </div>
          <div className="text-lg font-semibold">
            {fmt(report.indirect_costs)}
          </div>
        </div>
        <div className="bg-blue-50 rounded p-3">
          <div className="text-xs text-blue-600">Total Eligible</div>
          <div className="text-lg font-bold text-blue-700">
            {fmt(report.total_eligible_costs)}
          </div>
        </div>
        <div className="bg-blue-50 rounded p-3">
          <div className="text-xs text-blue-600">EC Requested</div>
          <div className="text-lg font-bold text-blue-700">
            {fmt(report.ec_contribution_requested)}
          </div>
        </div>
      </div>

      {/* CFS Alert */}
      {report.cfs_required && (
        <div className="mt-4 bg-yellow-50 border border-yellow-200 rounded p-3">
          <div className="text-sm font-medium text-yellow-800">
            Certificate on Financial Statements Required
          </div>
          <div className="text-xs text-yellow-700">
            Cumulative claimed: EUR {fmt(report.cumulative_claimed)} (threshold:
            EUR 430,000)
          </div>
          <div className="text-xs text-yellow-700">
            Status: {report.cfs_status}
          </div>
        </div>
      )}
    </div>
  );
}

function LumpSumSection({ report }: { report: LumpSumReport }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        WP Completion Declarations
      </h3>

      {report.declarations.length === 0 ? (
        <p className="text-sm text-gray-500 italic">
          No declarations for this period.
        </p>
      ) : (
        <div className="overflow-x-auto mb-4">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-2 pr-4 font-medium text-gray-600">
                  Work Package
                </th>
                <th className="text-left py-2 pr-4 font-medium text-gray-600">
                  Status
                </th>
                <th className="text-right py-2 pr-4 font-medium text-gray-600">
                  Completion
                </th>
                <th className="text-right py-2 pr-4 font-medium text-gray-600">
                  Lump Sum
                </th>
                <th className="text-right py-2 font-medium text-gray-600">
                  Claimed
                </th>
              </tr>
            </thead>
            <tbody>
              {report.declarations.map((d: WPCompletionDeclaration) => (
                <tr
                  key={d.id}
                  className="border-b border-gray-100"
                >
                  <td className="py-2 pr-4">{d.work_package_id}</td>
                  <td className="py-2 pr-4">
                    <span
                      className={`px-2 py-0.5 rounded text-xs ${
                        d.completion_status === CompletionStatus.COMPLETED
                          ? 'bg-green-100 text-green-800'
                          : d.completion_status ===
                              CompletionStatus.PARTIALLY_COMPLETED
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {COMPLETION_STATUS_LABELS[d.completion_status] ??
                        d.completion_status}
                    </span>
                  </td>
                  <td className="py-2 pr-4 text-right">
                    {d.completion_percentage}%
                  </td>
                  <td className="py-2 pr-4 text-right">
                    {fmt(d.lump_sum_amount)}
                  </td>
                  <td className="py-2 text-right font-medium">
                    {fmt(d.amount_claimed)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-purple-50 rounded p-3">
          <div className="text-xs text-purple-600">Total Lump Sum</div>
          <div className="text-lg font-bold text-purple-700">
            {fmt(report.total_lump_sum)}
          </div>
        </div>
        <div className="bg-purple-50 rounded p-3">
          <div className="text-xs text-purple-600">Total Claimed</div>
          <div className="text-lg font-bold text-purple-700">
            {fmt(report.total_claimed)}
          </div>
        </div>
      </div>
    </div>
  );
}

function UnitCostSection({ report }: { report: UnitCostReport }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Unit Delivery Records
      </h3>

      {report.records.length === 0 ? (
        <p className="text-sm text-gray-500 italic">
          No unit records for this period.
        </p>
      ) : (
        <div className="overflow-x-auto mb-4">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-2 pr-4 font-medium text-gray-600">
                  Description
                </th>
                <th className="text-left py-2 pr-4 font-medium text-gray-600">
                  Type
                </th>
                <th className="text-right py-2 pr-4 font-medium text-gray-600">
                  Planned
                </th>
                <th className="text-right py-2 pr-4 font-medium text-gray-600">
                  Actual
                </th>
                <th className="text-right py-2 pr-4 font-medium text-gray-600">
                  Rate
                </th>
                <th className="text-right py-2 font-medium text-gray-600">
                  Cost
                </th>
              </tr>
            </thead>
            <tbody>
              {report.records.map((r: UnitDeliveryRecord) => (
                <tr key={r.id} className="border-b border-gray-100">
                  <td className="py-2 pr-4">{r.description}</td>
                  <td className="py-2 pr-4 text-gray-500">
                    {r.unit_type}
                  </td>
                  <td className="py-2 pr-4 text-right">
                    {fmt(r.planned_units)}
                  </td>
                  <td className="py-2 pr-4 text-right">
                    {fmt(r.actual_units)}
                  </td>
                  <td className="py-2 pr-4 text-right">
                    {fmt(r.unit_rate)}
                  </td>
                  <td className="py-2 text-right font-medium">
                    {fmt(r.total_cost)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-green-50 rounded p-3">
          <div className="text-xs text-green-600">Total Planned</div>
          <div className="text-lg font-bold text-green-700">
            {fmt(report.total_planned_cost)}
          </div>
        </div>
        <div className="bg-green-50 rounded p-3">
          <div className="text-xs text-green-600">Total Actual</div>
          <div className="text-lg font-bold text-green-700">
            {fmt(report.total_actual_cost)}
          </div>
        </div>
      </div>
    </div>
  );
}

function InstitutionalSection({
  report,
}: {
  report: InstitutionalReport;
}) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          Institutional Parallel Report
        </h3>
        {report.has_discrepancies && (
          <span className="px-2 py-1 rounded text-xs bg-yellow-100 text-yellow-800 font-medium">
            Discrepancies Found
          </span>
        )}
      </div>

      <div className="overflow-x-auto mb-4">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="text-left py-2 pr-4 font-medium text-gray-600">
                EC Category
              </th>
              <th className="text-left py-2 pr-4 font-medium text-gray-600">
                University Code
              </th>
              <th className="text-right py-2 pr-4 font-medium text-gray-600">
                EC Amount
              </th>
              <th className="text-right py-2 pr-4 font-medium text-gray-600">
                University Amount
              </th>
              <th className="text-right py-2 font-medium text-gray-600">
                Discrepancy
              </th>
            </tr>
          </thead>
          <tbody>
            {report.rows
              .filter(
                (r: InstitutionalMappingRow) =>
                  parseFloat(r.ec_amount) > 0 ||
                  parseFloat(r.university_amount) > 0,
              )
              .map((row: InstitutionalMappingRow) => (
                <tr
                  key={row.ec_category}
                  className={`border-b border-gray-100 ${
                    parseFloat(row.discrepancy) !== 0
                      ? 'bg-yellow-50'
                      : ''
                  }`}
                >
                  <td className="py-2 pr-4 font-medium">
                    {row.ec_category}
                  </td>
                  <td className="py-2 pr-4 text-gray-500">
                    {row.university_account_code ?? '—'}
                  </td>
                  <td className="py-2 pr-4 text-right">
                    {fmt(row.ec_amount)}
                  </td>
                  <td className="py-2 pr-4 text-right">
                    {fmt(row.university_amount)}
                  </td>
                  <td
                    className={`py-2 text-right ${
                      parseFloat(row.discrepancy) !== 0
                        ? 'text-yellow-700 font-medium'
                        : ''
                    }`}
                  >
                    {fmt(row.discrepancy)}
                  </td>
                </tr>
              ))}
          </tbody>
          <tfoot>
            <tr className="border-t-2 border-gray-300 font-semibold">
              <td className="py-2 pr-4" colSpan={2}>
                Totals
              </td>
              <td className="py-2 pr-4 text-right">
                {fmt(report.total_ec)}
              </td>
              <td className="py-2 pr-4 text-right">
                {fmt(report.total_university)}
              </td>
              <td className="py-2 text-right">
                {fmt(report.total_discrepancy)}
              </td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  );
}

export default function FinancialReportingPage() {
  const { id: projectId } = useParams<{ id: string }>();
  const [selectedPeriodId, setSelectedPeriodId] = useState<string>('');

  const { data: periods } = useReportingPeriods(projectId ?? '');
  const {
    data: report,
    isLoading,
    error,
  } = useFinancialReport(
    projectId ?? '',
    selectedPeriodId || undefined,
  );

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <Link
            to={`/projects/${projectId}`}
            className="text-sm text-blue-700 hover:underline"
          >
            Back to Project
          </Link>
          <h1 className="text-2xl font-bold text-gray-900 mt-1">
            Financial Reporting
          </h1>
          {report && (
            <div className="flex items-center gap-3 mt-1">
              <span className="text-sm text-gray-600">
                {report.project_acronym}
              </span>
              <CostModelBadge costModel={report.cost_model} />
            </div>
          )}
        </div>
      </div>

      {/* Period Selector */}
      <div className="bg-white rounded-lg border border-gray-200 p-4 mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Reporting Period
        </label>
        <select
          value={selectedPeriodId}
          onChange={(e) => setSelectedPeriodId(e.target.value)}
          className="border border-gray-300 rounded px-3 py-2 text-sm w-full max-w-md"
        >
          <option value="">All periods (overview)</option>
          {periods?.items?.map((p) => (
            <option key={p.id} value={p.id}>
              RP{p.period_number}: {p.start_date} — {p.end_date}
            </option>
          ))}
        </select>
      </div>

      {isLoading && (
        <p className="text-gray-500">Loading financial report...</p>
      )}
      {error && (
        <p className="text-red-600">
          Error: {(error as Error).message}
        </p>
      )}

      {report && (
        <div className="space-y-6">
          {/* Cost-model-specific section */}
          {report.form_c && <FormCSection report={report.form_c} />}
          {report.lump_sum && (
            <LumpSumSection report={report.lump_sum} />
          )}
          {report.unit_cost && (
            <UnitCostSection report={report.unit_cost} />
          )}

          {/* Institutional parallel report */}
          {report.institutional_report && (
            <InstitutionalSection
              report={report.institutional_report}
            />
          )}

          {/* Empty state when no period selected */}
          {!report.form_c &&
            !report.lump_sum &&
            !report.unit_cost &&
            !selectedPeriodId && (
              <div className="bg-white rounded-lg border border-gray-200 p-6 text-center">
                <p className="text-gray-500">
                  Select a reporting period to view detailed financial
                  reports.
                </p>
              </div>
            )}
        </div>
      )}
    </div>
  );
}
