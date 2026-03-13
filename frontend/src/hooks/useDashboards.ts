/**
 * React Query hooks for role-based dashboards (Section 10).
 */
import { useQuery } from '@tanstack/react-query';
import {
  fetchPIDashboard,
  fetchProjectDashboard,
  fetchResearcherDashboard,
} from '../services/dashboards';

export function usePIDashboard() {
  return useQuery({
    queryKey: ['dashboards', 'pi'],
    queryFn: fetchPIDashboard,
  });
}

export function useResearcherDashboard(researcherId: string | undefined) {
  return useQuery({
    queryKey: ['dashboards', 'researcher', researcherId],
    queryFn: () => fetchResearcherDashboard(researcherId!),
    enabled: !!researcherId,
  });
}

export function useProjectDashboard(projectId: string | undefined) {
  return useQuery({
    queryKey: ['dashboards', 'project', projectId],
    queryFn: () => fetchProjectDashboard(projectId!),
    enabled: !!projectId,
  });
}
