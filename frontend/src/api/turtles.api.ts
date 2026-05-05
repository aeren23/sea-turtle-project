import apiClient from './apiClient';
import type { TurtleDto, UpdateTurtleRequest } from '../types/turtle.types';
import { DEFAULT_PAGE_SIZE } from '../utils/constants';

/** GET /api/Turtles — paginated turtle list */
export const getTurtles = async (skip = 0, take = DEFAULT_PAGE_SIZE): Promise<TurtleDto[]> => {
  const response = await apiClient.get<TurtleDto[]>('/api/Turtles', {
    params: { skip, take },
  });
  return response.data;
};

/** GET /api/Turtles/{id} — single turtle profile with encounter count */
export const getTurtleById = async (id: string): Promise<TurtleDto> => {
  const response = await apiClient.get<TurtleDto>(`/api/Turtles/${id}`);
  return response.data;
};

/** PUT /api/Turtles/{id} — update turtle metadata (species, nickname, location) */
export const updateTurtle = async (
  id: string,
  data: UpdateTurtleRequest,
): Promise<TurtleDto> => {
  const response = await apiClient.put<TurtleDto>(`/api/Turtles/${id}`, data);
  return response.data;
};

/** DELETE /api/Turtles/{id} — Admin only: soft-delete a turtle record */
export const deleteTurtle = async (id: string): Promise<void> => {
  await apiClient.delete(`/api/Turtles/${id}`);
};
