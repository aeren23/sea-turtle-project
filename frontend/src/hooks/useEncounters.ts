import { useState, useEffect, useCallback } from 'react';
import {
  getEncounters,
  getEncountersByTurtleId,
  deleteEncounter,
  updateEncounter,
} from '../api/encounters.api';
import type { EncounterDto, UpdateEncounterRequest } from '../types/encounter.types';
import { ENCOUNTER_PAGE_SIZE } from '../utils/constants';
import { useUiStore } from '../stores/uiStore';

/**
 * Hook for the global encounters page.
 * Responsibility: paginated encounter list and delete action.
 */
export const useEncounters = () => {
  const [encounters, setEncounters] = useState<EncounterDto[]>([]);
  const [isLoading, setIsLoading]   = useState(false);
  const [page, setPage]             = useState(0);
  const [hasMore, setHasMore]       = useState(true);
  const { addToast } = useUiStore();

  const fetchPage = useCallback(async (pageIndex: number) => {
    setIsLoading(true);
    try {
      const skip = pageIndex * ENCOUNTER_PAGE_SIZE;
      const data = await getEncounters(skip, ENCOUNTER_PAGE_SIZE);
      setEncounters(data);
      setHasMore(data.length === ENCOUNTER_PAGE_SIZE);
      setPage(pageIndex);
    } catch {
      addToast('Failed to load encounters.', 'error');
    } finally {
      setIsLoading(false);
    }
  }, [addToast]);

  useEffect(() => { fetchPage(0); }, [fetchPage]);

  const remove = useCallback(async (id: string) => {
    try {
      await deleteEncounter(id);
      setEncounters((prev) => prev.filter((e) => e.id !== id));
      addToast('Encounter deleted.', 'success');
    } catch {
      addToast('Failed to delete encounter.', 'error');
    }
  }, [addToast]);

  const update = useCallback(async (id: string, data: UpdateEncounterRequest) => {
    try {
      const updated = await updateEncounter(id, data);
      setEncounters((prev) => prev.map((e) => (e.id === id ? updated : e)));
      addToast('Encounter updated.', 'success');
      return updated;
    } catch {
      addToast('Failed to update encounter.', 'error');
      return null;
    }
  }, [addToast]);

  return { encounters, isLoading, page, hasMore, fetchPage, remove, update };
};

/**
 * Hook for encounter list scoped to a single turtle (used on TurtleDetailPage).
 * Responsibility: fetch encounters for one turtle only.
 */
export const useTurtleEncounters = (turtleId: string) => {
  const [encounters, setEncounters] = useState<EncounterDto[]>([]);
  const [isLoading, setIsLoading]   = useState(false);
  const { addToast } = useUiStore();

  useEffect(() => {
    if (!turtleId) return;
    setIsLoading(true);
    getEncountersByTurtleId(turtleId)
      .then(setEncounters)
      .catch(() => addToast('Failed to load encounters for this turtle.', 'error'))
      .finally(() => setIsLoading(false));
  }, [turtleId, addToast]);

  return { encounters, isLoading };
};
