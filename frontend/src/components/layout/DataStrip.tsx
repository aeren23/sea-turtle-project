import React from 'react';
import './DataStrip.css';

/**
 * Decorative left-edge data strip with scan-line animation.
 * Displays coordinate labels and depth indicators — purely presentational.
 * Evokes a scientific instrument readout aesthetic.
 */
const DataStrip: React.FC = () => {
  const now = new Date();
  const timeStr = now.toLocaleTimeString('en-GB', { hour12: false });

  return (
    <div className="datastrip" aria-hidden="true">
      <div className="datastrip__scan-line" />

      <div className="datastrip__content">
        {/* Top decorative tick marks */}
        <div className="datastrip__ticks">
          {Array.from({ length: 12 }, (_, i) => (
            <div
              key={i}
              className={`datastrip__tick${i % 4 === 0 ? ' datastrip__tick--major' : ''}`}
            />
          ))}
        </div>

        {/* Depth / coordinate labels */}
        <div className="datastrip__labels">
          <span className="datastrip__label">36.8°N</span>
          <span className="datastrip__label">30.4°E</span>
          <span className="datastrip__label">MEDS</span>
          <span className="datastrip__label">PWR</span>
          <span className="datastrip__label">{timeStr.slice(0, 5)}</span>
        </div>

        {/* Bottom decorative dots */}
        <div className="datastrip__dots">
          {Array.from({ length: 5 }, (_, i) => (
            <div key={i} className="datastrip__dot" />
          ))}
        </div>
      </div>
    </div>
  );
};

export default DataStrip;
