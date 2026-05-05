import React from 'react';
import './LoadingSpinner.css';

interface LoadingSpinnerProps {
  /** Label shown below the spinner */
  label?: string;
  size?:  'sm' | 'md' | 'lg';
}

/**
 * Animated loading spinner with optional label.
 * Used during API calls and page loading states.
 */
const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  label = 'Processing...',
  size  = 'md',
}) => (
  <div className={`spinner spinner--${size}`} role="status" aria-label={label}>
    <svg className="spinner__ring" viewBox="0 0 50 50" aria-hidden="true">
      <circle className="spinner__track" cx="25" cy="25" r="20" fill="none" strokeWidth="3" />
      <circle className="spinner__arc"   cx="25" cy="25" r="20" fill="none" strokeWidth="3" />
    </svg>
    {label && <span className="spinner__label">{label}</span>}
  </div>
);

export default LoadingSpinner;
