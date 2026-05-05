import { useState, useEffect, useCallback } from 'react';
import { getTurtles, getTurtleById } from '../api/turtles.api';
import type { TurtleDto } from '../types/turtle.types';
import { DEFAULT_PAGE_SIZE } from '../utils/constants';
import { useUiStore } from '../stores/uiStore';

/**
 * Hook for paginated turtle list management.
 * Responsibility: data fetching and pagination state for the catalog page.
 */
export const useTurtles = () => {
  const [turtles, setTurtles]     = useState<TurtleDto[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [page, setPage]           = useState(0);
  const [hasMore, setHasMore]     = useState(true);
  const { addToast } = useUiStore();

  const fetchPage = useCallback(async (pageIndex: number) => {
    setIsLoading(true);
    try {
      const skip = pageIndex * DEFAULT_PAGE_SIZE;
      const data = await getTurtles(skip, DEFAULT_PAGE_SIZE);
      setTurtles(data);
      setHasMore(data.length === DEFAULT_PAGE_SIZE);
      setPage(pageIndex);
    } catch {
      addToast('Failed to load turtle list.', 'error');
    } finally {
      setIsLoading(false);
    }
  }, [addToast]);

  useEffect(() => { fetchPage(0); }, [fetchPage]);

  return { turtles, isLoading, page, hasMore, fetchPage };
};

/**
 * Hook for a single turtle's detail view.
 * Responsibility: fetch and expose a single turtle's profile.
 */
export const useTurtleDetail = (id: string) => {
  const [turtle, setTurtle]       = useState<TurtleDto | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const { addToast } = useUiStore();

  useEffect(() => {
    if (!id) return;
    setIsLoading(true);
    getTurtleById(id)
      .then(setTurtle)
      .catch(() => addToast('Failed to load turtle profile.', 'error'))
      .finally(() => setIsLoading(false));
  }, [id, addToast]);

  return { turtle, isLoading };
};
