import React from 'react';
import './ConfidenceGauge.css';
import { formatConfidence, getConfidenceLevel } from '../../utils/formatters';

interface ConfidenceGaugeProps {
  /** Score between 0.0 and 1.0 */
  score: number;
  size?: number;
}

const STROKE_CIRCUMFERENCE = 2 * Math.PI * 38; // radius = 38

/**
 * Animated SVG radial gauge for confidence score display.
 * Responsibility: visual representation of a single 0–1 score value.
 */
const ConfidenceGauge: React.FC<ConfidenceGaugeProps> = ({ score, size = 120 }) => {
  const level = getConfidenceLevel(score);
  const fillLength = STROKE_CIRCUMFERENCE * score;
  const offset = STROKE_CIRCUMFERENCE - fillLength;

  const colorMap: Record<string, string> = {
    high: 'var(--color-biolum-green)',
    mid:  'var(--color-amber)',
    low:  'var(--color-coral-warn)',
  };
  const strokeColor = colorMap[level];

  return (
    <div
      className="confidence-gauge"
      style={{ width: size, height: size }}
      role="meter"
      aria-valuenow={Math.round(score * 100)}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={`Confidence: ${formatConfidence(score)}`}
    >
      <svg width={size} height={size} viewBox="0 0 100 100">
        {/* Background track */}
        <circle
          cx="50" cy="50" r="38"
          fill="none"
          stroke="var(--color-ocean-border)"
          strokeWidth="6"
        />
        {/* Animated fill arc */}
        <circle
          cx="50" cy="50" r="38"
          fill="none"
          stroke={strokeColor}
          strokeWidth="6"
          strokeLinecap="round"
          strokeDasharray={STROKE_CIRCUMFERENCE}
          strokeDashoffset={offset}
          transform="rotate(-90 50 50)"
          className="confidence-gauge__arc"
          style={{ filter: `drop-shadow(0 0 4px ${strokeColor})` }}
        />
        {/* Center text */}
        <text
          x="50" y="50"
          textAnchor="middle"
          dominantBaseline="central"
          className="confidence-gauge__text"
        >
          {Math.round(score * 100)}
        </text>
        <text
          x="50" y="64"
          textAnchor="middle"
          className="confidence-gauge__sub"
        >
          %
        </text>
      </svg>
    </div>
  );
};

export default ConfidenceGauge;
