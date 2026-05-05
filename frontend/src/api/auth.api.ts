import apiClient from './apiClient';
import type { LoginRequest, RegisterRequest, AuthResponse, UserDto } from '../types/auth.types';

/** POST /api/Auth/login — exchange credentials for JWT */
export const login = async (data: LoginRequest): Promise<AuthResponse> => {
  const response = await apiClient.post<AuthResponse>('/api/Auth/login', data);
  return response.data;
};

/** POST /api/Auth/register — create a new researcher account (AllowAnonymous) */
export const register = async (data: RegisterRequest): Promise<AuthResponse> => {
  const response = await apiClient.post<AuthResponse>('/api/Auth/register', data);
  return response.data;
};

/** GET /api/Auth/me — fetch the currently authenticated user's profile */
export const getMe = async (): Promise<UserDto> => {
  const response = await apiClient.get<UserDto>('/api/Auth/me');
  return response.data;
};
