import React from 'react';
import { Link } from 'react-router-dom';
import type { EncounterDto } from '../../types/encounter.types';
import { formatDate, formatConfidence, getConfidenceLevel, capitalise } from '../../utils/formatters';
import './EncounterRow.css';

interface EncounterRowProps {
  encounter: EncounterDto;
  onDelete?: (id: string) => void;
  onEdit?:   (encounter: EncounterDto) => void;
  canEdit:   boolean;
}

/**
 * Single row in the encounters table.
 * Responsibility: display encounter data and provide contextual action buttons.
 */
const EncounterRow: React.FC<EncounterRowProps> = ({ encounter, onDelete, onEdit, canEdit }) => {
  const confidenceLevel = getConfidenceLevel(encounter.confidenceScore);

  return (
    <tr className="encounter-row">
      <td className="encounter-row__cell encounter-row__cell--date">
        {formatDate(encounter.encounterDate)}
      </td>
      <td className="encounter-row__cell">
        <Link
          to={`/turtles/${encounter.turtleId}`}
          className="encounter-row__turtle-link"
        >
          {encounter.turtleCode.toUpperCase()}
        </Link>
      </td>
      <td className="encounter-row__cell encounter-row__cell--secondary">
        {encounter.locationName ?? '—'}
      </td>
      <td className="encounter-row__cell encounter-row__cell--secondary">
        {encounter.researcherName}
      </td>
      <td className="encounter-row__cell">
        <span className={`encounter-row__side tag`}>
          {capitalise(encounter.biologicalSide)}
        </span>
      </td>
      <td className="encounter-row__cell">
        <span className={`encounter-row__confidence encounter-row__confidence--${confidenceLevel}`}>
          {formatConfidence(encounter.confidenceScore)}
        </span>
      </td>
      <td className="encounter-row__cell encounter-row__cell--actions">
        {canEdit && (
          <>
            <button
              className="encounter-row__action-btn"
              onClick={() => onEdit?.(encounter)}
              aria-label={`Edit encounter ${encounter.id}`}
            >
              ✎
            </button>
            <button
              className="encounter-row__action-btn encounter-row__action-btn--danger"
              onClick={() => onDelete?.(encounter.id)}
              aria-label={`Delete encounter ${encounter.id}`}
            >
              ✕
            </button>
          </>
        )}
      </td>
    </tr>
  );
};

export default EncounterRow;
