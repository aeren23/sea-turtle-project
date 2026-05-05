import { create } from 'zustand';

export type ToastVariant = 'success' | 'error' | 'info' | 'warning';

export interface Toast {
  id:      string;
  message: string;
  variant: ToastVariant;
}

interface UiState {
  /** Global loading overlay (e.g. during AI identification) */
  isGlobalLoading: boolean;
  /** Toast notification queue */
  toasts: Toast[];

  /** Actions */
  setGlobalLoading: (loading: boolean) => void;
  addToast:         (message: string, variant?: ToastVariant) => void;
  removeToast:      (id: string) => void;
}

/**
 * UI store — transient state that does not need persistence.
 * Single responsibility: loading states and notification queue only.
 */
export const useUiStore = create<UiState>((set) => ({
  isGlobalLoading: false,
  toasts:          [],

  setGlobalLoading: (loading) => set({ isGlobalLoading: loading }),

  addToast: (message, variant = 'info') => {
    const id = `toast_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`;
    set((state) => ({ toasts: [...state.toasts, { id, message, variant }] }));
    // Auto-dismiss after 4 seconds
    setTimeout(() => set((state) => ({
      toasts: state.toasts.filter((t) => t.id !== id),
    })), 4000);
  },

  removeToast: (id) =>
    set((state) => ({ toasts: state.toasts.filter((t) => t.id !== id) })),
}));
