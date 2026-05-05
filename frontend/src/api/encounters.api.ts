import apiClient from './apiClient';
import type { EncounterDto, UpdateEncounterRequest } from '../types/encounter.types';
import { ENCOUNTER_PAGE_SIZE } from '../utils/constants';

/** GET /api/Encounters — paginated full encounter list */
export const getEncounters = async (skip = 0, take = ENCOUNTER_PAGE_SIZE): Promise<EncounterDto[]> => {
  const response = await apiClient.get<EncounterDto[]>('/api/Encounters', {
    params: { skip, take },
  });
  return response.data;
};

/** GET /api/Encounters/{id} — single encounter details */
export const getEncounterById = async (id: string): Promise<EncounterDto> => {
  const response = await apiClient.get<EncounterDto>(`/api/Encounters/${id}`);
  return response.data;
};

/** GET /api/Encounters/turtle/{turtleId} — all encounters for a specific turtle */
export const getEncountersByTurtleId = async (turtleId: string): Promise<EncounterDto[]> => {
  const response = await apiClient.get<EncounterDto[]>(`/api/Encounters/turtle/${turtleId}`);
  return response.data;
};

/** PUT /api/Encounters/{id} — update location, notes on an encounter */
export const updateEncounter = async (
  id: string,
  data: UpdateEncounterRequest,
): Promise<EncounterDto> => {
  const response = await apiClient.put<EncounterDto>(`/api/Encounters/${id}`, data);
  return response.data;
};

/** DELETE /api/Encounters/{id} — delete an encounter (own records or Admin) */
export const deleteEncounter = async (id: string): Promise<void> => {
  await apiClient.delete(`/api/Encounters/${id}`);
};
