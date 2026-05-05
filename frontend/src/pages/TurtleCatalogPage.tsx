import React, { useState } from 'react';
import { useTurtles } from '../hooks/useTurtles';
import TurtleCard from '../components/ui/TurtleCard';
import Pagination from '../components/ui/Pagination';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import { TURTLE_SPECIES } from '../utils/constants';
import './TurtleCatalogPage.css';

/**
 * Turtle catalog — paginated grid of turtle cards with species filter.
 * Responsibility: list display, pagination, and client-side species filter.
 */
const TurtleCatalogPage: React.FC = () => {
  const { turtles, isLoading, page, hasMore, fetchPage } = useTurtles();
  const [speciesFilter, setSpeciesFilter] = useState<string>('all');

  const filteredTurtles = speciesFilter === 'all'
    ? turtles
    : turtles.filter((t) => t.species === speciesFilter);

  return (
    <div className="catalog-page">
      {/* Header */}
      <header className="catalog-page__header fade-up-1">
        <div>
          <h1 className="catalog-page__title">Turtle Catalog</h1>
          <p className="catalog-page__subtitle">
            {turtles.length} individuals loaded · FAISS-seeded database
          </p>
        </div>

        {/* Species filter */}
        <div className="catalog-page__filters">
          <label className="field__label" htmlFor="species-filter">Filter by species</label>
          <select
            id="species-filter"
            className="field__input catalog-page__select"
            value={speciesFilter}
            onChange={(e) => setSpeciesFilter(e.target.value)}
          >
            <option value="all">All Species</option>
            {TURTLE_SPECIES.map((s) => (
              <option key={s.value} value={s.value}>{s.label}</option>
            ))}
          </select>
        </div>
      </header>

      {/* Turtle grid */}
      {isLoading ? (
        <div className="catalog-page__loading">
          <LoadingSpinner label="Loading catalog..." size="lg" />
        </div>
      ) : filteredTurtles.length === 0 ? (
        <p className="catalog-page__empty">No turtles found for this filter.</p>
      ) : (
        <div
          className="catalog-page__grid fade-up-2"
          role="list"
          aria-label="Turtle catalog"
        >
          {filteredTurtles.map((turtle, index) => (
            <div key={turtle.id} role="listitem">
              <TurtleCard turtle={turtle} index={index} />
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {!isLoading && (
        <Pagination
          currentPage={page}
          hasMore={hasMore}
          onPrev={() => fetchPage(page - 1)}
          onNext={() => fetchPage(page + 1)}
          isLoading={isLoading}
        />
      )}
    </div>
  );
};

export default TurtleCatalogPage;
