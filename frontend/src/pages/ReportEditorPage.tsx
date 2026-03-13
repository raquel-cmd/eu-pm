import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  useTechnicalReport,
  useReportWorkflow,
  useAdvanceWorkflow,
  useUpdateTechnicalReport,
  useUpdateReportSection,
} from '../hooks/useReporting';
import {
  REPORT_STATUS_LABELS,
  ReportSectionType,
  ReportStatus,
  type ReportSection,
  type WorkflowStepInfo,
} from '../types';

const SECTION_TYPE_LABELS: Record<ReportSectionType, string> = {
  [ReportSectionType.PART_A_SUMMARY]: 'Part A: Publishable Summary',
  [ReportSectionType.PART_B1_WP_NARRATIVE]: 'Part B.1: WP Narrative',
  [ReportSectionType.PART_B2_DELIVERABLES]: 'Part B.2: Deliverables & Milestones',
  [ReportSectionType.PART_B3_RISKS]: 'Part B.3: Risks & Mitigation',
  [ReportSectionType.PART_B4_RESOURCES]: 'Part B.4: Resource Usage',
};

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    DRAFT: 'bg-gray-100 text-gray-800',
    WP_INPUT: 'bg-blue-100 text-blue-800',
    PARTNER_REVIEW: 'bg-indigo-100 text-indigo-800',
    CONSOLIDATION: 'bg-yellow-100 text-yellow-800',
    INTERNAL_REVIEW: 'bg-orange-100 text-orange-800',
    FINAL_REVIEW: 'bg-purple-100 text-purple-800',
    SUBMITTED: 'bg-green-100 text-green-800',
    EC_APPROVED: 'bg-emerald-100 text-emerald-800',
  };

  return (
    <span
      className={`px-2 py-1 rounded text-xs font-medium ${colors[status] ?? 'bg-gray-100 text-gray-800'}`}
    >
      {REPORT_STATUS_LABELS[status as ReportStatus] ?? status}
    </span>
  );
}

function WorkflowTracker({
  steps,
  onAdvance,
  canAdvance,
}: {
  steps: WorkflowStepInfo[];
  onAdvance: () => void;
  canAdvance: boolean;
}) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          Workflow Progress
        </h3>
        {canAdvance && (
          <button
            onClick={onAdvance}
            className="px-4 py-2 bg-blue-700 text-white text-sm rounded hover:bg-blue-800"
          >
            Advance to Next Step
          </button>
        )}
      </div>
      <div className="flex gap-1">
        {steps.map((step) => {
          let bgColor = 'bg-gray-200';
          let textColor = 'text-gray-600';
          if (step.status === 'completed') {
            bgColor = 'bg-green-500';
            textColor = 'text-white';
          } else if (step.status === 'active') {
            bgColor = 'bg-blue-500';
            textColor = 'text-white';
          } else if (step.status === 'overdue') {
            bgColor = 'bg-red-500';
            textColor = 'text-white';
          }

          return (
            <div key={step.step_number} className="flex-1 min-w-0">
              <div className={`h-2 rounded ${bgColor}`} />
              <div className="mt-1 text-xs truncate">
                <span className={textColor === 'text-white' ? 'font-semibold' : ''}>
                  {step.name}
                </span>
              </div>
              <div className="text-xs text-gray-400">
                {step.actor}
              </div>
              {step.deadline_date && (
                <div className="text-xs text-gray-400">
                  {step.deadline_date}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function SectionEditor({
  section,
  onSave,
}: {
  section: ReportSection;
  onSave: (sectionId: string, narrative: string) => void;
}) {
  const [editing, setEditing] = useState(false);
  const [text, setText] = useState(section.narrative ?? '');

  const sectionLabel =
    SECTION_TYPE_LABELS[section.section_type as ReportSectionType] ??
    section.section_type;

  const statusColors: Record<string, string> = {
    DRAFT: 'border-gray-300',
    SUBMITTED: 'border-blue-300',
    APPROVED: 'border-green-300',
  };

  return (
    <div
      className={`bg-white rounded-lg border-2 ${statusColors[section.status] ?? 'border-gray-200'} p-4`}
    >
      <div className="flex items-center justify-between mb-2">
        <h4 className="font-medium text-gray-900">{sectionLabel}</h4>
        <div className="flex items-center gap-2">
          <span
            className={`px-2 py-0.5 rounded text-xs ${
              section.status === 'APPROVED'
                ? 'bg-green-100 text-green-800'
                : section.status === 'SUBMITTED'
                  ? 'bg-blue-100 text-blue-800'
                  : 'bg-gray-100 text-gray-800'
            }`}
          >
            {section.status}
          </span>
          {section.assigned_to && (
            <span className="text-xs text-gray-500">
              Assigned: {section.assigned_to}
            </span>
          )}
        </div>
      </div>

      {section.section_type === ReportSectionType.PART_B2_DELIVERABLES ||
      section.section_type === ReportSectionType.PART_B4_RESOURCES ? (
        <p className="text-sm text-gray-500 italic">
          This section is auto-generated from project data.
        </p>
      ) : editing ? (
        <div>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={6}
            className="w-full border border-gray-300 rounded px-3 py-2 text-sm mb-2"
          />
          <div className="flex gap-2">
            <button
              onClick={() => {
                onSave(section.id, text);
                setEditing(false);
              }}
              className="px-3 py-1 bg-blue-700 text-white text-sm rounded hover:bg-blue-800"
            >
              Save
            </button>
            <button
              onClick={() => setEditing(false)}
              className="px-3 py-1 bg-gray-200 text-gray-700 text-sm rounded hover:bg-gray-300"
            >
              Cancel
            </button>
          </div>
        </div>
      ) : (
        <div>
          {section.narrative ? (
            <p className="text-sm text-gray-700 whitespace-pre-wrap">
              {section.narrative}
            </p>
          ) : (
            <p className="text-sm text-gray-400 italic">No content yet.</p>
          )}
          <button
            onClick={() => setEditing(true)}
            className="mt-2 text-sm text-blue-700 hover:underline"
          >
            Edit
          </button>
        </div>
      )}
    </div>
  );
}

export default function ReportEditorPage() {
  const { reportId } = useParams<{ reportId: string }>();
  const { data: report, isLoading, error } = useTechnicalReport(reportId ?? '');
  const { data: steps } = useReportWorkflow(reportId ?? '');
  const advanceMutation = useAdvanceWorkflow();
  const updateReportMutation = useUpdateTechnicalReport();
  const updateSectionMutation = useUpdateReportSection();

  const [partAText, setPartAText] = useState('');
  const [editingPartA, setEditingPartA] = useState(false);

  if (isLoading) return <p className="text-gray-500">Loading report...</p>;
  if (error)
    return (
      <p className="text-red-600">
        Error: {(error as Error).message}
      </p>
    );
  if (!report) return <p className="text-gray-500">Report not found.</p>;

  const canAdvance =
    report.status !== ReportStatus.EC_APPROVED &&
    report.status !== ReportStatus.SUBMITTED;

  const handleAdvance = () => {
    advanceMutation.mutate(report.id);
  };

  const handleSavePartA = () => {
    updateReportMutation.mutate({
      reportId: report.id,
      data: { part_a_summary: partAText },
    });
    setEditingPartA(false);
  };

  const handleSaveSection = (sectionId: string, narrative: string) => {
    updateSectionMutation.mutate({
      sectionId,
      data: { narrative },
    });
  };

  // Sort sections by type
  const sectionOrder = [
    ReportSectionType.PART_A_SUMMARY,
    ReportSectionType.PART_B1_WP_NARRATIVE,
    ReportSectionType.PART_B2_DELIVERABLES,
    ReportSectionType.PART_B3_RISKS,
    ReportSectionType.PART_B4_RESOURCES,
  ];
  const sortedSections = [...report.sections].sort(
    (a, b) =>
      sectionOrder.indexOf(a.section_type as ReportSectionType) -
      sectionOrder.indexOf(b.section_type as ReportSectionType)
  );

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <Link
            to="/reporting-calendar"
            className="text-sm text-blue-700 hover:underline"
          >
            Back to Calendar
          </Link>
          <h1 className="text-2xl font-bold text-gray-900 mt-1">
            Technical Report
          </h1>
          <div className="flex items-center gap-3 mt-1">
            <StatusBadge status={report.status} />
            <span className="text-sm text-gray-500">
              {report.report_type} report
            </span>
            {report.submitted_at && (
              <span className="text-sm text-gray-500">
                Submitted: {new Date(report.submitted_at).toLocaleDateString()}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Workflow Tracker */}
      {steps && (
        <WorkflowTracker
          steps={steps}
          onAdvance={handleAdvance}
          canAdvance={canAdvance}
        />
      )}

      {/* Part A: Publishable Summary */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold text-gray-900">
            Part A: Publishable Summary
          </h3>
        </div>
        {editingPartA ? (
          <div>
            <textarea
              value={partAText}
              onChange={(e) => setPartAText(e.target.value)}
              rows={8}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm mb-2"
              placeholder="Write the publishable summary..."
            />
            <div className="flex gap-2">
              <button
                onClick={handleSavePartA}
                className="px-3 py-1 bg-blue-700 text-white text-sm rounded hover:bg-blue-800"
              >
                Save
              </button>
              <button
                onClick={() => setEditingPartA(false)}
                className="px-3 py-1 bg-gray-200 text-gray-700 text-sm rounded hover:bg-gray-300"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <div>
            {report.part_a_summary ? (
              <p className="text-sm text-gray-700 whitespace-pre-wrap">
                {report.part_a_summary}
              </p>
            ) : (
              <p className="text-sm text-gray-400 italic">
                No summary written yet.
              </p>
            )}
            <button
              onClick={() => {
                setPartAText(report.part_a_summary ?? '');
                setEditingPartA(true);
              }}
              className="mt-2 text-sm text-blue-700 hover:underline"
            >
              Edit Summary
            </button>
          </div>
        )}
      </div>

      {/* Report Sections */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">
          Report Sections
        </h3>
        {sortedSections
          .filter(
            (s) => s.section_type !== ReportSectionType.PART_A_SUMMARY
          )
          .map((section) => (
            <SectionEditor
              key={section.id}
              section={section}
              onSave={handleSaveSection}
            />
          ))}
      </div>

      {/* EC Feedback */}
      {report.ec_feedback && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mt-6">
          <h3 className="text-lg font-semibold text-yellow-800 mb-2">
            EC Feedback
          </h3>
          <p className="text-sm text-yellow-700 whitespace-pre-wrap">
            {report.ec_feedback}
          </p>
        </div>
      )}
    </div>
  );
}
