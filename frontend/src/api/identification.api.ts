import apiClient from './apiClient';
import type { IdentificationResponse } from '../types/identification.types';
import type { RegisterUnknownRequest } from '../types/identification.types';

/**
 * POST /api/Identification/identify
 * Sends a photo as multipart/form-data and returns the AI identification result.
 * The photo field name must match the .NET controller parameter: "photo"
 */
export const identifyTurtle = async (photoFile: File): Promise<IdentificationResponse> => {
  const formData = new FormData();
  formData.append('photo', photoFile);

  const response = await apiClient.post<IdentificationResponse>(
    '/api/Identification/identify',
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } },
  );
  return response.data;
};

/**
 * POST /api/Identification/register
 * Confirms an unknown turtle (identified via sessionId) and registers it as a new individual.
 */
export const registerUnknownTurtle = async (
  data: RegisterUnknownRequest,
): Promise<IdentificationResponse> => {
  const response = await apiClient.post<IdentificationResponse>(
    '/api/Identification/register',
    data,
  );
  return response.data;
};
