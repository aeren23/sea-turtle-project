import React from 'react';
import './SonarRing.css';

interface SonarRingProps {
  /** Size of the ring container in px */
  size?: number;
  /** Number of concentric rings to render */
  rings?: number;
}

/**
 * Decorative SVG sonar pulse animation.
 * Renders concentric rings that animate outward like a sonar ping.
 * Purely presentational — no state or side effects.
 */
const SonarRing: React.FC<SonarRingProps> = ({ size = 120, rings = 3 }) => {
  const center = size / 2;
  const baseRadius = size / 8;

  return (
    <div className="sonar-ring" style={{ width: size, height: size }}>
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        aria-hidden="true"
      >
        {/* Static center dot */}
        <circle
          cx={center}
          cy={center}
          r={baseRadius}
          fill="var(--color-biolum-green)"
          opacity={0.9}
        />

        {/* Animated pulse rings with staggered delay */}
        {Array.from({ length: rings }, (_, index) => (
          <circle
            key={index}
            cx={center}
            cy={center}
            r={baseRadius}
            fill="none"
            stroke="var(--color-biolum-green)"
            strokeWidth={1.5}
            className="sonar-ring__pulse"
            style={{ animationDelay: `${index * 0.9}s` }}
          />
        ))}
      </svg>
    </div>
  );
};

export default SonarRing;
