import React, { useEffect, useRef } from 'react';
import './Modal.css';

interface ModalProps {
  isOpen:    boolean;
  onClose:   () => void;
  title:     string;
  children:  React.ReactNode;
  /** Max width of the modal panel */
  width?:    number;
}

/**
 * Generic accessible modal dialog.
 * Responsibility: trap focus, handle Escape key, render overlay + panel.
 */
const Modal: React.FC<ModalProps> = ({ isOpen, onClose, title, children, width = 480 }) => {
  const dialogRef = useRef<HTMLDivElement>(null);

  // Close on Escape key
  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  // Lock body scroll while open
  useEffect(() => {
    document.body.style.overflow = isOpen ? 'hidden' : '';
    return () => { document.body.style.overflow = ''; };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div
      className="modal-overlay"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      <div
        ref={dialogRef}
        className="modal-panel"
        style={{ maxWidth: width }}
      >
        {/* Header */}
        <div className="modal-panel__header">
          <h2 id="modal-title" className="modal-panel__title">{title}</h2>
          <button
            className="modal-panel__close"
            onClick={onClose}
            aria-label="Close modal"
          >
            ✕
          </button>
        </div>

        {/* Content */}
        <div className="modal-panel__body">
          {children}
        </div>
      </div>
    </div>
  );
};

export default Modal;
