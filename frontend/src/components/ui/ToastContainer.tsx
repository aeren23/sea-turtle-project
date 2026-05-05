import React from 'react';
import { useUiStore } from '../../stores/uiStore';
import type { ToastVariant } from '../../stores/uiStore';
import './ToastContainer.css';

const VARIANT_ICONS: Record<ToastVariant, string> = {
  success: '✓',
  error:   '✕',
  warning: '⚠',
  info:    'ℹ',
};

/**
 * Global toast notification container.
 * Reads from uiStore — no props required.
 * Responsibility: render and auto-dismiss toast queue.
 */
const ToastContainer: React.FC = () => {
  const { toasts, removeToast } = useUiStore();

  return (
    <div className="toast-container" aria-live="polite" aria-label="Notifications">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`toast toast--${toast.variant}`}
          role="alert"
        >
          <span className="toast__icon" aria-hidden="true">
            {VARIANT_ICONS[toast.variant]}
          </span>
          <span className="toast__message">{toast.message}</span>
          <button
            className="toast__close"
            onClick={() => removeToast(toast.id)}
            aria-label="Dismiss notification"
          >
            ✕
          </button>
        </div>
      ))}
    </div>
  );
};

export default ToastContainer;
