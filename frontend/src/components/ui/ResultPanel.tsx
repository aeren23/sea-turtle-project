import React from 'react';
import { Link } from 'react-router-dom';
import type { IdentificationResponse } from '../../types/identification.types';
import ConfidenceGauge from './ConfidenceGauge';
import { capitalise } from '../../utils/formatters';
import './ResultPanel.css';

interface ResultPanelProps {
  result:           IdentificationResponse;
  onRegister:            () => void;
  onIdentifyAgain:       () => void;
  onAddEncounterDetails: (encounterId: string) => void;
}

/**
 * Displays the AI identification result: known turtle profile or unknown alert.
 * Responsibility: render result state and offer next-action buttons.
 */
const ResultPanel: React.FC<ResultPanelProps> = ({ result, onRegister, onIdentifyAgain, onAddEncounterDetails }) => {
  const isKnown = result.isKnown;

  return (
    <div className={`result-panel ${isKnown ? 'result-panel--known' : 'result-panel--unknown'} fade-up`}>
      {/* Top status bar */}
      <div className="result-panel__status-bar">
        <div className="result-panel__status-indicator" />
        <span className="result-panel__status-text">
          {isKnown ? 'Identity Confirmed' : 'Unknown Individual'}
        </span>
        <span className={`tag ${isKnown ? '' : 'tag--warn'}`}>
          {capitalise(result.biologicalSide)} profile
        </span>
      </div>

      {/* Main content */}
      <div className="result-panel__body">
        {/* Gauge */}
        <div className="result-panel__gauge">
          <ConfidenceGauge score={result.score} size={140} />
          <span className="result-panel__gauge-label">AI Confidence</span>
        </div>

        {/* Identity info */}
        <div className="result-panel__info">
          {isKnown ? (
            <>
              <div className="result-panel__id">{result.turtleId?.toUpperCase()}</div>
              {result.nickname && (
                <div className="result-panel__nickname">"{result.nickname}"</div>
              )}
              {result.species && (
                <div className="result-panel__species">{result.species}</div>
              )}

              {/* Profile photo thumbnail */}
              {result.photoUrl && (
                <img
                  src={result.photoUrl}
                  alt={`Turtle ${result.turtleId}`}
                  className="result-panel__photo"
                />
              )}

              {/* Actions */}
              <div className="result-panel__actions">
                {result.encounterId && (
                  <button
                    className="btn btn--secondary"
                    onClick={() => onAddEncounterDetails(result.encounterId as string)}
                  >
                    Add Encounter Details
                  </button>
                )}
                <Link
                  to={`/turtles/${result.turtleId}`}
                  className="btn btn--primary"
                >
                  View Full Profile
                </Link>
                <button
                  className="btn btn--ghost"
                  onClick={onIdentifyAgain}
                >
                  Identify Another
                </button>
              </div>
            </>
          ) : (
            <>
              <div className="result-panel__unknown-icon" aria-hidden="true">◈</div>
              <p className="result-panel__unknown-text">
                No match found in the database. This may be a new individual
                not yet registered in the system.
              </p>

              <div className="result-panel__actions">
                <button
                  className="btn btn--primary"
                  onClick={onRegister}
                >
                  Register as New Turtle
                </button>
                <button
                  className="btn btn--ghost"
                  onClick={onIdentifyAgain}
                >
                  Try Again
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default ResultPanel;
