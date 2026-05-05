import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { UserDto, UserRole } from '../types/auth.types';
import { AUTH_TOKEN_KEY, AUTH_USER_KEY } from '../utils/constants';

interface AuthState {
  /** Raw JWT token string */
  token: string | null;
  /** Authenticated user profile */
  user:  UserDto | null;

  /** Actions */
  setAuth:   (token: string, user: UserDto) => void;
  clearAuth: () => void;
  isAdmin:   () => boolean;
}

/**
 * Auth store — persists token and user to localStorage.
 * Single responsibility: authentication state only.
 * Never put UI state or API calls here.
 */
export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      user:  null,

      setAuth: (token, user) => set({ token, user }),

      clearAuth: () => {
        localStorage.removeItem(AUTH_TOKEN_KEY);
        localStorage.removeItem(AUTH_USER_KEY);
        set({ token: null, user: null });
      },

      isAdmin: () => get().user?.role === ('Admin' as UserRole),
    }),
    {
      name: AUTH_TOKEN_KEY,
      // Only persist token and user, not actions
      partialize: (state) => ({ token: state.token, user: state.user }),
    },
  ),
);
