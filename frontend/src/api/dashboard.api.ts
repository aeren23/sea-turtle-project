import apiClient from './apiClient';
import type { DashboardStatsDto } from '../types/identification.types';
import type { EncounterDto } from '../types/encounter.types';
import { DASHBOARD_RECENT_COUNT } from '../utils/constants';

/** GET /api/Dashboard/stats — system-wide statistics */
export const getDashboardStats = async (): Promise<DashboardStatsDto> => {
  const response = await apiClient.get<DashboardStatsDto>('/api/Dashboard/stats');
  return response.data;
};

/** GET /api/Dashboard/recent-encounters — last N encounters for the dashboard feed */
export const getRecentEncounters = async (
  count: number = DASHBOARD_RECENT_COUNT,
): Promise<EncounterDto[]> => {
  const response = await apiClient.get<EncounterDto[]>('/api/Dashboard/recent-encounters', {
    params: { count },
  });
  return response.data;
};
