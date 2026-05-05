import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useEncounters } from '../hooks/useEncounters';
import { useAuthStore } from '../stores/authStore';
import EncounterRow from '../components/ui/EncounterRow';
import Pagination from '../components/ui/Pagination';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import Modal from '../components/ui/Modal';
import type { EncounterDto, UpdateEncounterRequest } from '../types/encounter.types';
import './EncountersPage.css';

const editSchema = z.object({
  locationName: z.string().optional(),
  latitude:     z.number().nullable().optional(),
  longitude:    z.number().nullable().optional(),
  notes:        z.string().optional(),
});
type EditFormData = z.infer<typeof editSchema>;

/**
 * Encounters list page.
 * Displays all encounters in a sortable table with edit/delete actions.
 * Responsibility: encounter list display and CRUD interaction.
 */
const EncountersPage: React.FC = () => {
  const { encounters, isLoading, page, hasMore, fetchPage, remove, update } = useEncounters();
  const { user, isAdmin } = useAuthStore();

  const [editingEncounter, setEditingEncounter] = useState<EncounterDto | null>(null);

  const { register, handleSubmit, reset: resetForm } = useForm<EditFormData>({
    resolver: zodResolver(editSchema),
  });

  const openEdit = (encounter: EncounterDto) => {
    setEditingEncounter(encounter);
    resetForm({
      locationName: encounter.locationName ?? '',
      latitude:     encounter.latitude ?? undefined,
      longitude:    encounter.longitude ?? undefined,
      notes:        encounter.notes ?? '',
    });
  };

  const handleSave = async (data: EditFormData) => {
    if (!editingEncounter) return;
    const payload: UpdateEncounterRequest = {
      locationName: data.locationName || null,
      latitude:     data.latitude ?? null,
      longitude:    data.longitude ?? null,
      notes:        data.notes || null,
    };
    await update(editingEncounter.id, payload);
    setEditingEncounter(null);
  };

  /** User can edit own encounters; admin can edit any */
  const canEditEncounter = (enc: EncounterDto): boolean =>
    isAdmin() || enc.researcherName === user?.fullName;

  return (
    <div className="encounters-page">
      {/* Header */}
      <header className="encounters-page__header fade-up-1">
        <div>
          <h1 className="encounters-page__title">Encounters</h1>
          <p className="encounters-page__subtitle">
            {encounters.length} records loaded · sorted by date descending
          </p>
        </div>
      </header>

      {/* Table */}
      {isLoading ? (
        <div className="encounters-page__loading">
          <LoadingSpinner label="Loading encounters..." size="lg" />
        </div>
      ) : encounters.length === 0 ? (
        <p className="encounters-page__empty">No encounters found.</p>
      ) : (
        <div className="encounters-page__table-wrap fade-up-2">
          <table className="encounters-page__table" aria-label="Encounter records">
            <thead>
              <tr className="encounters-page__thead-row">
                <th scope="col">Date</th>
                <th scope="col">Turtle</th>
                <th scope="col">Location</th>
                <th scope="col">Researcher</th>
                <th scope="col">Side</th>
                <th scope="col">Confidence</th>
                <th scope="col" aria-label="Actions" />
              </tr>
            </thead>
            <tbody>
              {encounters.map((enc) => (
                <EncounterRow
                  key={enc.id}
                  encounter={enc}
                  canEdit={canEditEncounter(enc)}
                  onEdit={openEdit}
                  onDelete={(id) => {
                    if (window.confirm('Delete this encounter?')) remove(id);
                  }}
                />
              ))}
            </tbody>
          </table>
        </div>
      )}

      {!isLoading && (
        <Pagination
          currentPage={page}
          hasMore={hasMore}
          onPrev={() => fetchPage(page - 1)}
          onNext={() => fetchPage(page + 1)}
          isLoading={isLoading}
        />
      )}

      {/* Edit Modal */}
      <Modal
        isOpen={editingEncounter !== null}
        onClose={() => setEditingEncounter(null)}
        title="Edit Encounter"
        width={500}
      >
        <form
          onSubmit={handleSubmit(handleSave)}
          className="encounters-page__edit-form"
          noValidate
        >
          <div className="field">
            <label className="field__label" htmlFor="enc-location">Location Name</label>
            <input
              id="enc-location"
              type="text"
              className="field__input"
              placeholder="e.g. Dalyan Beach"
              {...register('locationName')}
            />
          </div>

          <div className="encounters-page__coord-row">
            <div className="field">
              <label className="field__label" htmlFor="enc-lat">Latitude</label>
              <input
                id="enc-lat"
                type="number"
                step="0.0001"
                className="field__input"
                placeholder="36.8505"
                {...register('latitude', { valueAsNumber: true })}
              />
            </div>
            <div className="field">
              <label className="field__label" htmlFor="enc-lng">Longitude</label>
              <input
                id="enc-lng"
                type="number"
                step="0.0001"
                className="field__input"
                placeholder="28.1234"
                {...register('longitude', { valueAsNumber: true })}
              />
            </div>
          </div>

          <div className="field">
            <label className="field__label" htmlFor="enc-notes">Notes</label>
            <textarea
              id="enc-notes"
              className="field__input encounters-page__textarea"
              placeholder="Observation notes..."
              rows={4}
              {...register('notes')}
            />
          </div>

          <div className="encounters-page__modal-actions">
            <button type="submit" className="btn btn--primary">Save Changes</button>
            <button
              type="button"
              className="btn btn--ghost"
              onClick={() => setEditingEncounter(null)}
            >
              Cancel
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default EncountersPage;
