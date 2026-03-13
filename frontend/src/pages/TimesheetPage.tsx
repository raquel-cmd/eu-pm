import { useState, useMemo } from 'react';
import { useResearchers } from '../hooks/useResearchers';
import { useTimesheetEntries, useCreateTimesheetEntry, useSubmitTimesheets } from '../hooks/useTimesheets';
import type { Researcher, TimesheetEntry, TimesheetEntryCreate } from '../types';

function getWeekDates(baseDate: Date): Date[] {
  const day = baseDate.getDay();
  const monday = new Date(baseDate);
  monday.setDate(baseDate.getDate() - ((day + 6) % 7));
  return Array.from({ length: 7 }, (_, i) => {
    const d = new Date(monday);
    d.setDate(monday.getDate() + i);
    return d;
  });
}

function formatDateISO(d: Date): string {
  return d.toISOString().split('T')[0];
}

function formatDayLabel(d: Date): string {
  return d.toLocaleDateString('en-GB', { weekday: 'short', day: '2-digit', month: 'short' });
}

export default function TimesheetPage() {
  const { data: researchersData, isLoading: researchersLoading } = useResearchers();
  const [selectedResearcher, setSelectedResearcher] = useState('');
  const [weekOffset, setWeekOffset] = useState(0);

  const baseDate = useMemo(() => {
    const d = new Date();
    d.setDate(d.getDate() + weekOffset * 7);
    return d;
  }, [weekOffset]);

  const weekDates = useMemo(() => getWeekDates(baseDate), [baseDate]);
  const dateFrom = formatDateISO(weekDates[0]);
  const dateTo = formatDateISO(weekDates[6]);

  // We need to know which projects the researcher is on — for now, show all entries
  // across all projects for the selected researcher in the date range
  const researchers = researchersData?.items ?? [];

  if (researchersLoading) {
    return <p className="text-gray-500">Loading researchers...</p>;
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Timesheets</h1>

      <div className="flex items-center gap-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Researcher</label>
          <select
            value={selectedResearcher}
            onChange={(e) => setSelectedResearcher(e.target.value)}
            className="border rounded px-3 py-2 text-sm min-w-[200px]"
          >
            <option value="">Select a researcher...</option>
            {researchers.map((r: Researcher) => (
              <option key={r.id} value={r.id}>{r.name}</option>
            ))}
          </select>
        </div>

        <div className="flex items-center gap-2 ml-auto">
          <button
            onClick={() => setWeekOffset((w) => w - 1)}
            className="px-3 py-2 border rounded text-sm hover:bg-gray-50"
          >
            &larr; Prev
          </button>
          <button
            onClick={() => setWeekOffset(0)}
            className="px-3 py-2 border rounded text-sm hover:bg-gray-50"
          >
            Today
          </button>
          <button
            onClick={() => setWeekOffset((w) => w + 1)}
            className="px-3 py-2 border rounded text-sm hover:bg-gray-50"
          >
            Next &rarr;
          </button>
        </div>
      </div>

      <div className="text-sm text-gray-600 mb-4">
        Week of {formatDayLabel(weekDates[0])} &mdash; {formatDayLabel(weekDates[6])}
      </div>

      {selectedResearcher ? (
        <TimesheetGrid
          researcherId={selectedResearcher}
          weekDates={weekDates}
          dateFrom={dateFrom}
          dateTo={dateTo}
        />
      ) : (
        <p className="text-gray-500 text-sm">Select a researcher to view their timesheet.</p>
      )}
    </div>
  );
}

function TimesheetGrid({
  researcherId,
  weekDates,
  dateFrom,
  dateTo,
}: {
  researcherId: string;
  weekDates: Date[];
  dateFrom: string;
  dateTo: string;
}) {
  // For now, show a simple per-day entry view without project breakdown
  // A full implementation would query all projects the researcher is allocated to
  const createEntry = useCreateTimesheetEntry();
  const submitEntries = useSubmitTimesheets();

  // This is a simplified view — in a real implementation, we'd fetch entries across
  // all projects and show rows per project. For now, show a placeholder grid.

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200 border">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 w-32">Day</th>
            <th className="px-4 py-2 text-center text-xs font-medium text-gray-500">Status</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {weekDates.map((day) => {
            const isWeekend = day.getDay() === 0 || day.getDay() === 6;
            return (
              <tr key={formatDateISO(day)} className={isWeekend ? 'bg-gray-50' : ''}>
                <td className="px-4 py-3 text-sm font-medium">
                  {formatDayLabel(day)}
                </td>
                <td className="px-4 py-3 text-sm text-center text-gray-400">
                  {isWeekend ? 'Weekend' : 'Enter hours in project Effort tab'}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
      <p className="text-xs text-gray-500 mt-3">
        Timesheet entries are created per-project in each project's Effort tab. This page provides a weekly overview.
      </p>
    </div>
  );
}
