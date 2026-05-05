import React from 'react';
import './Pagination.css';

interface PaginationProps {
  currentPage: number;
  hasMore:     boolean;
  onPrev:      () => void;
  onNext:      () => void;
  isLoading?:  boolean;
}

/**
 * Simple prev/next pagination control.
 * Responsibility: page navigation UI only — no data fetching.
 */
const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  hasMore,
  onPrev,
  onNext,
  isLoading = false,
}) => (
  <div className="pagination" role="navigation" aria-label="Page navigation">
    <button
      className="btn btn--ghost pagination__btn"
      onClick={onPrev}
      disabled={currentPage === 0 || isLoading}
      aria-label="Previous page"
    >
      ← Prev
    </button>

    <span className="pagination__info">
      Page <strong>{currentPage + 1}</strong>
    </span>

    <button
      className="btn btn--ghost pagination__btn"
      onClick={onNext}
      disabled={!hasMore || isLoading}
      aria-label="Next page"
    >
      Next →
    </button>
  </div>
);

export default Pagination;
