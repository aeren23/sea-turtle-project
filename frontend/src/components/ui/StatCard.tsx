import React, { useEffect, useRef } from 'react';
import './StatCard.css';

interface StatCardProps {
  label:      string;
  value:      number;
  unit?:      string;
  icon?:      string;
  /** Animation delay index for staggered reveal */
  delayIndex?: number;
}

/**
 * Dashboard statistic card with animated count-up effect.
 * Responsibility: display a single numeric KPI with visual emphasis.
 */
const StatCard: React.FC<StatCardProps> = ({
  label,
  value,
  unit,
  icon,
  delayIndex = 0,
}) => {
  const valueRef = useRef<HTMLSpanElement>(null);

  // Count-up animation using requestAnimationFrame
  useEffect(() => {
    const el = valueRef.current;
    if (!el) return;

    const duration = 1200; // ms
    const start = performance.now();
    const startValue = 0;

    const animate = (now: number) => {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      // Ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.round(startValue + eased * (value - startValue)).toLocaleString();
      if (progress < 1) requestAnimationFrame(animate);
    };

    requestAnimationFrame(animate);
  }, [value]);

  return (
    <div
      className={`stat-card fade-up-${delayIndex + 1}`}
      role="figure"
      aria-label={`${label}: ${value.toLocaleString()}${unit ? ` ${unit}` : ''}`}
    >
      {icon && <span className="stat-card__icon" aria-hidden="true">{icon}</span>}
      <div className="stat-card__body">
        <div className="stat-card__value-row">
          <span ref={valueRef} className="stat-card__value">0</span>
          {unit && <span className="stat-card__unit">{unit}</span>}
        </div>
        <span className="stat-card__label">{label}</span>
      </div>
      {/* Decorative corner accent */}
      <div className="stat-card__accent" aria-hidden="true" />
    </div>
  );
};

export default StatCard;
