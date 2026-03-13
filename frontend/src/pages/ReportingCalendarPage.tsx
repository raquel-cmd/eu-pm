import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useReportingCalendar } from '../hooks/useReporting';
import {
  REMINDER_TYPE_LABELS,
  REPORT_STATUS_LABELS,
  type ReportingPeriod,
  type CalendarReminderItem,
} from '../types';

function DeadlineBadge({ daysUntil }: { daysUntil: number | null }) {
  if (daysUntil === null) return null;
  let color = 'bg-green-100 text-green-800';
  if (daysUntil < 0) color = 'bg-red-100 text-red-800';
  else if (daysUntil <= 30) color = 'bg-yellow-100 text-yellow-800';
  else if (daysUntil <= 60) color = 'bg-blue-100 text-blue-800';

  const label =
    daysUntil < 0
      ? `${Math.abs(daysUntil)}d overdue`
      : daysUntil === 0
        ? 'Today'
        : `${daysUntil}d remaining`;

  return (
    <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${color}`}>
      {label}
    </span>
  );
}

function UpcomingDeadlinesTable({
  deadlines,
}: {
  deadlines: ReportingPeriod[];
}) {
  if (deadlines.length === 0) {
    return (
      <p className="text-gray-500 text-sm py-4">No upcoming deadlines.</p>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200">
            <th className="text-left py-2 pr-4 font-medium text-gray-600">
              Period
            </th>
            <th className="text-left py-2 pr-4 font-medium text-gray-600">
              Type
            </th>
            <th className="text-left py-2 pr-4 font-medium text-gray-600">
              Period Dates
            </th>
            <th className="text-left py-2 pr-4 font-medium text-gray-600">
              Deadline
            </th>
            <th className="text-left py-2 font-medium text-gray-600">
              Status
            </th>
          </tr>
        </thead>
        <tbody>
          {deadlines.map((d) => (
            <tr key={d.id} className="border-b border-gray-100">
              <td className="py-2 pr-4">RP{d.period_number}</td>
              <td className="py-2 pr-4">
                <span
                  className={`px-2 py-0.5 rounded text-xs ${
                    d.period_type === 'FINAL'
                      ? 'bg-purple-100 text-purple-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {d.period_type}
                </span>
              </td>
              <td className="py-2 pr-4">
                {d.start_date} — {d.end_date}
              </td>
              <td className="py-2 pr-4">{d.technical_report_deadline}</td>
              <td className="py-2">
                <DeadlineBadge daysUntil={d.days_until_deadline} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function RemindersTable({
  reminders,
  title,
  emptyMessage,
  isOverdue,
}: {
  reminders: CalendarReminderItem[];
  title: string;
  emptyMessage: string;
  isOverdue?: boolean;
}) {
  return (
    <div>
      <h3 className="text-lg font-semibold text-gray-900 mb-3">{title}</h3>
      {reminders.length === 0 ? (
        <p className="text-gray-500 text-sm py-2">{emptyMessage}</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-2 pr-4 font-medium text-gray-600">
                  Project
                </th>
                <th className="text-left py-2 pr-4 font-medium text-gray-600">
                  Period
                </th>
                <th className="text-left py-2 pr-4 font-medium text-gray-600">
                  Milestone
                </th>
                <th className="text-left py-2 pr-4 font-medium text-gray-600">
                  Date
                </th>
                <th className="text-left py-2 font-medium text-gray-600">
                  Recipients
                </th>
              </tr>
            </thead>
            <tbody>
              {reminders.map((r, i) => (
                <tr
                  key={`${r.reporting_period_id}-${r.reminder_type}-${i}`}
                  className={`border-b border-gray-100 ${
                    isOverdue ? 'bg-red-50' : ''
                  }`}
                >
                  <td className="py-2 pr-4 font-medium">
                    {r.project_acronym}
                  </td>
                  <td className="py-2 pr-4">RP{r.period_number}</td>
                  <td className="py-2 pr-4">
                    <span className="px-2 py-0.5 rounded bg-blue-100 text-blue-800 text-xs">
                      {REMINDER_TYPE_LABELS[r.reminder_type] ?? r.reminder_type}
                    </span>
                  </td>
                  <td className="py-2 pr-4">{r.scheduled_date}</td>
                  <td className="py-2 text-gray-600">{r.description}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default function ReportingCalendarPage() {
  const [projectFilter, setProjectFilter] = useState<string>('');
  const { data: calendar, isLoading, error } = useReportingCalendar(
    projectFilter || undefined
  );

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">
          Reporting Calendar
        </h1>
        <div className="flex gap-3">
          <Link
            to="/reports"
            className="text-sm text-blue-700 hover:underline"
          >
            Finance Dashboard
          </Link>
        </div>
      </div>

      {isLoading && <p className="text-gray-500">Loading calendar...</p>}
      {error && (
        <p className="text-red-600">
          Error loading calendar: {(error as Error).message}
        </p>
      )}

      {calendar && (
        <div className="space-y-8">
          {/* Overdue Items */}
          {calendar.overdue_items.length > 0 && (
            <div className="bg-white rounded-lg border border-red-200 p-6">
              <RemindersTable
                reminders={calendar.overdue_items}
                title="Overdue Items"
                emptyMessage=""
                isOverdue
              />
            </div>
          )}

          {/* Upcoming Deadlines */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">
              Upcoming Report Deadlines
            </h3>
            <UpcomingDeadlinesTable
              deadlines={calendar.upcoming_deadlines}
            />
          </div>

          {/* Upcoming Reminders */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <RemindersTable
              reminders={calendar.reminders}
              title="Upcoming Reminders"
              emptyMessage="No upcoming reminders."
            />
          </div>
        </div>
      )}
    </div>
  );
}
