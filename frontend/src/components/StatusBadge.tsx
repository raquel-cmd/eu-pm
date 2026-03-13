import { ProjectStatus, STATUS_LABELS } from '../types';

const STATUS_COLORS: Record<ProjectStatus, string> = {
  [ProjectStatus.PROPOSAL]: 'bg-gray-100 text-gray-700',
  [ProjectStatus.NEGOTIATION]: 'bg-yellow-100 text-yellow-800',
  [ProjectStatus.ACTIVE]: 'bg-green-100 text-green-800',
  [ProjectStatus.SUSPENDED]: 'bg-red-100 text-red-800',
  [ProjectStatus.CLOSED]: 'bg-blue-100 text-blue-800',
};

const STATUS_DOTS: Record<ProjectStatus, string> = {
  [ProjectStatus.PROPOSAL]: 'bg-gray-400',
  [ProjectStatus.NEGOTIATION]: 'bg-yellow-400',
  [ProjectStatus.ACTIVE]: 'bg-green-500',
  [ProjectStatus.SUSPENDED]: 'bg-red-500',
  [ProjectStatus.CLOSED]: 'bg-blue-400',
};

export function StatusBadge({ status }: { status: ProjectStatus }) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium ${STATUS_COLORS[status]}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${STATUS_DOTS[status]}`} />
      {STATUS_LABELS[status]}
    </span>
  );
}

export function TrafficLightDot({
  color,
}: {
  color: 'GREEN' | 'AMBER' | 'RED';
}) {
  const colors = {
    GREEN: 'bg-green-500',
    AMBER: 'bg-amber-400',
    RED: 'bg-red-500',
  };
  return <span className={`inline-block w-3 h-3 rounded-full ${colors[color]}`} />;
}
