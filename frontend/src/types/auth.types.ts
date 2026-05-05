// Auth domain types — mirrors backend DTOs

export interface LoginRequest {
  email:    string;
  password: string;
}

export interface RegisterRequest {
  fullName: string;
  email:    string;
  password: string;
}

/** JWT-based auth response from POST /api/Auth/login and /register */
export interface AuthResponse {
  token:    string;
  email:    string;
  fullName: string;
  role:     UserRole;
}

/** Current user profile from GET /api/Auth/me */
export interface UserDto {
  id:       string;
  email:    string;
  fullName: string;
  role:     UserRole;
}

export type UserRole = 'Admin' | 'Researcher';
