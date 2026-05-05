import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { login as loginApi, register as registerApi } from '../api/auth.api';
import type { LoginRequest, RegisterRequest } from '../types/auth.types';
import { useAuthStore } from '../stores/authStore';
import { useUiStore } from '../stores/uiStore';

/**
 * Hook encapsulating authentication actions.
 * Responsibility: orchestrate API calls, store updates, and navigation on auth events.
 */
export const useAuth = () => {
  const [isLoading, setIsLoading] = useState(false);
  const { setAuth, clearAuth, isAdmin } = useAuthStore();
  const { addToast } = useUiStore();
  const navigate = useNavigate();

  const login = useCallback(async (data: LoginRequest) => {
    setIsLoading(true);
    try {
      const response = await loginApi(data);
      setAuth(response.token, {
        id:       '',           // not returned from login — fetched via /me on demand
        email:    response.email,
        fullName: response.fullName,
        role:     response.role,
      });
      navigate('/dashboard');
    } catch {
      addToast('Invalid email or password.', 'error');
    } finally {
      setIsLoading(false);
    }
  }, [setAuth, addToast, navigate]);

  const register = useCallback(async (data: RegisterRequest) => {
    setIsLoading(true);
    try {
      const response = await registerApi(data);
      setAuth(response.token, {
        id:       '',
        email:    response.email,
        fullName: response.fullName,
        role:     response.role,
      });
      navigate('/dashboard');
    } catch {
      addToast('Registration failed. This email may already be in use.', 'error');
    } finally {
      setIsLoading(false);
    }
  }, [setAuth, addToast, navigate]);

  const logout = useCallback(() => {
    clearAuth();
    navigate('/login');
  }, [clearAuth, navigate]);

  return { login, register, logout, isLoading, isAdmin };
};
