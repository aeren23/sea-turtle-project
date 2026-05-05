import React from 'react';
import { Link } from 'react-router-dom';
import type { TurtleDto } from '../../types/turtle.types';
import { formatDate } from '../../utils/formatters';
import './TurtleCard.css';

interface TurtleCardProps {
  turtle:     TurtleDto;
  /** Animation delay index for staggered catalog reveal */
  index?:     number;
}

/**
 * Turtle catalog card with hover slide-up detail panel.
 * Responsibility: display one turtle's summary in grid view.
 */
const TurtleCard: React.FC<TurtleCardProps> = ({ turtle, index = 0 }) => {
  const delayStyle = { animationDelay: `${index * 0.05}s` };

  return (
    <Link
      to={`/turtles/${turtle.id}`}
      className="turtle-card fade-up"
      style={delayStyle}
      aria-label={`View profile for ${turtle.turtleCode}`}
    >
      {/* Photo */}
      <div className="turtle-card__photo">
        {turtle.profilePhotoUrl ? (
          <img
            src={turtle.profilePhotoUrl}
            alt={`Turtle ${turtle.turtleCode}`}
            loading="lazy"
          />
        ) : (
          <div className="turtle-card__photo-placeholder" aria-hidden="true">◉</div>
        )}
        {/* Species tag overlay */}
        <span className="turtle-card__species-badge">
          {turtle.species ?? 'Unknown species'}
        </span>
      </div>

      {/* Slide-up hover panel */}
      <div className="turtle-card__panel">
        <div className="turtle-card__code">{turtle.turtleCode.toUpperCase()}</div>
        {turtle.nickname && (
          <div className="turtle-card__nickname">"{turtle.nickname}"</div>
        )}
        <div className="turtle-card__meta">
          <span className="turtle-card__meta-item">
            <span aria-hidden="true">◎</span>
            {turtle.encounterCount} encounter{turtle.encounterCount !== 1 ? 's' : ''}
          </span>
          {turtle.lastSeenAt && (
            <span className="turtle-card__meta-item">
              <span aria-hidden="true">◷</span>
              {formatDate(turtle.lastSeenAt)}
            </span>
          )}
        </div>
      </div>
    </Link>
  );
};

export default TurtleCard;
