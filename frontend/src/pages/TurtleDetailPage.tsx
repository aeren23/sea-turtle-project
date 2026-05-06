import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTurtleDetail } from '../hooks/useTurtles';
import { useTurtleEncounters } from '../hooks/useEncounters';
import { updateTurtle, deleteTurtle } from '../api/turtles.api';
import { useAuthStore } from '../stores/authStore';
import { useUiStore } from '../stores/uiStore';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import Modal from '../components/ui/Modal';
import { formatDate, formatDateTime, formatConfidence, getConfidenceLevel, capitalise } from '../utils/formatters';
import { TURTLE_SPECIES } from '../utils/constants';
import './TurtleDetailPage.css';

/**
 * Single turtle profile page.
 * Shows: hero photo, metadata, encounter timeline.
 * Admin: edit and delete turtle actions.
 */
const TurtleDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { turtle, isLoading } = useTurtleDetail(id ?? '');
  const { encounters, isLoading: encLoading } = useTurtleEncounters(id ?? '');
  const { isAdmin } = useAuthStore();
  const { addToast } = useUiStore();

  const [isEditOpen, setEditOpen]     = useState(false);
  const [isDeleteOpen, setDeleteOpen] = useState(false);
  const [editNickname, setEditNickname]   = useState('');
  const [editSpecies, setEditSpecies]     = useState('');
  const [editLocation, setEditLocation]   = useState('');
  const [isSaving, setIsSaving]           = useState(false);

  const openEdit = () => {
    if (!turtle) return;
    setEditNickname(turtle.nickname ?? '');
    setEditSpecies(turtle.species ?? '');
    setEditLocation(turtle.firstSeenLocation ?? '');
    setEditOpen(true);
  };

  const handleSaveEdit = async () => {
    if (!turtle) return;
    setIsSaving(true);
    try {
      await updateTurtle(turtle.id, {
        nickname:          editNickname || null,
        species:           editSpecies || null,
        firstSeenLocation: editLocation || null,
      });
      addToast('Turtle profile updated.', 'success');
      setEditOpen(false);
      window.location.reload(); // refresh to show updated data
    } catch {
      addToast('Failed to update turtle.', 'error');
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!turtle) return;
    setIsSaving(true);
    try {
      await deleteTurtle(turtle.id);
      addToast(`Turtle ${turtle.turtleCode} deleted.`, 'success');
      navigate('/turtles');
    } catch {
      addToast('Failed to delete turtle. Admin role required.', 'error');
    } finally {
      setIsSaving(false);
      setDeleteOpen(false);
    }
  };

  if (isLoading) {
    return (
      <div className="turtle-detail-loading">
        <LoadingSpinner label="Loading profile..." size="lg" />
      </div>
    );
  }

  if (!turtle) return <p className="turtle-detail-error">Turtle not found.</p>;

  return (
    <div className="turtle-detail">
      {/* Hero section */}
      <section className="turtle-detail__hero fade-up-1">
        <div className="turtle-detail__hero-photo">
          {turtle.profilePhotoUrl ? (
            <img src={turtle.profilePhotoUrl} alt={`Turtle ${turtle.turtleCode}`} />
          ) : (
            <div className="turtle-detail__hero-placeholder" aria-hidden="true">◉</div>
          )}
        </div>

        <div className="turtle-detail__hero-info">
          {/* Breadcrumb */}
          <p className="turtle-detail__breadcrumb">
            <a href="/turtles">Catalog</a> / {turtle.turtleCode.toUpperCase()}
          </p>

          <h1 className="turtle-detail__code">{turtle.turtleCode.toUpperCase()}</h1>

          {turtle.nickname && (
            <p className="turtle-detail__nickname">"{turtle.nickname}"</p>
          )}

          <p className="turtle-detail__species">
            {turtle.species ?? 'Species Unknown'}
          </p>

          {/* Bio stats */}
          <div className="turtle-detail__bio-grid">
            <div className="turtle-detail__bio-item">
              <span className="turtle-detail__bio-label">First Seen</span>
              <span className="turtle-detail__bio-value">{formatDate(turtle.firstSeenAt)}</span>
            </div>
            {turtle.lastSeenAt && (
              <div className="turtle-detail__bio-item">
                <span className="turtle-detail__bio-label">Last Seen</span>
                <span className="turtle-detail__bio-value">{formatDate(turtle.lastSeenAt)}</span>
              </div>
            )}
            <div className="turtle-detail__bio-item">
              <span className="turtle-detail__bio-label">Encounters</span>
              <span className="turtle-detail__bio-value">{turtle.encounterCount}</span>
            </div>
            {turtle.firstSeenLocation && (
              <div className="turtle-detail__bio-item">
                <span className="turtle-detail__bio-label">Location</span>
                <span className="turtle-detail__bio-value">{turtle.firstSeenLocation}</span>
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="turtle-detail__admin-actions">
            <button className="btn btn--ghost" onClick={openEdit}>✎ Edit Profile</button>
            {isAdmin() && (
              <button className="btn btn--danger" onClick={() => setDeleteOpen(true)}>✕ Delete</button>
            )}
          </div>
        </div>
      </section>

      {/* Encounter timeline */}
      <section className="turtle-detail__encounters fade-up-3" aria-labelledby="encounters-title">
        <h2 id="encounters-title" className="turtle-detail__section-title">
          Encounter History
          <span className="turtle-detail__encounter-count">{encounters.length}</span>
        </h2>

        {encLoading ? (
          <LoadingSpinner label="Loading encounters..." />
        ) : encounters.length === 0 ? (
          <p className="turtle-detail__empty">No encounters recorded for this turtle.</p>
        ) : (
          <div className="turtle-detail__timeline">
            {encounters.map((enc) => {
              const level = getConfidenceLevel(enc.confidenceScore);
              return (
                <div key={enc.id} className="turtle-detail__timeline-item">
                  {/* Dot */}
                  <div className="turtle-detail__timeline-dot" />

                  {/* Content */}
                  <div className="turtle-detail__timeline-content">
                    <div className="turtle-detail__timeline-header">
                      <span className="turtle-detail__timeline-date">
                        {formatDateTime(enc.encounterDate)}
                      </span>
                      <span className="tag">{capitalise(enc.biologicalSide)}</span>
                      <span className={`turtle-detail__tl-confidence turtle-detail__tl-confidence--${level}`}>
                        {formatConfidence(enc.confidenceScore)}
                      </span>
                    </div>

                    {enc.locationName && (
                      <p className="turtle-detail__timeline-location">
                        ◎ {enc.locationName}
                      </p>
                    )}

                    {enc.notes && (
                      <p className="turtle-detail__timeline-notes">{enc.notes}</p>
                    )}

                    {/* Photos */}
                    {enc.photoUrls.length > 0 && (
                      <div className="turtle-detail__timeline-photos">
                        {enc.photoUrls.map((url) => (
                          <img
                            key={url}
                            src={url}
                            alt={`Encounter photo`}
                            className="turtle-detail__timeline-photo"
                            loading="lazy"
                          />
                        ))}
                      </div>
                    )}

                    <p className="turtle-detail__timeline-researcher">
                      by {enc.researcherName}
                      {enc.galleryUpdated && (
                        <span className="tag" style={{ marginLeft: '8px' }}>Gallery Updated</span>
                      )}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>

      {/* Edit Modal */}
      <Modal isOpen={isEditOpen} onClose={() => setEditOpen(false)} title="Edit Turtle Profile">
        <div className="turtle-detail__edit-form">
          <div className="field">
            <label className="field__label" htmlFor="edit-species">Species</label>
            <input
              id="edit-species"
              className="field__input"
              list="edit-species-list"
              value={editSpecies}
              onChange={(e) => setEditSpecies(e.target.value)}
              placeholder="e.g. Caretta caretta"
            />
            <datalist id="edit-species-list">
              {TURTLE_SPECIES.map((s) => (
                <option key={s.value} value={s.value}>{s.label}</option>
              ))}
            </datalist>
          </div>
          <div className="field">
            <label className="field__label" htmlFor="edit-nickname">Nickname</label>
            <input
              id="edit-nickname"
              type="text"
              className="field__input"
              value={editNickname}
              onChange={(e) => setEditNickname(e.target.value)}
            />
          </div>
          <div className="field">
            <label className="field__label" htmlFor="edit-location">First Seen Location</label>
            <input
              id="edit-location"
              type="text"
              className="field__input"
              value={editLocation}
              onChange={(e) => setEditLocation(e.target.value)}
            />
          </div>
          <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', marginTop: '8px' }}>
            <button className="btn btn--primary" onClick={handleSaveEdit} disabled={isSaving}>
              {isSaving ? 'Saving...' : 'Save Changes'}
            </button>
            <button className="btn btn--ghost" onClick={() => setEditOpen(false)}>Cancel</button>
          </div>
        </div>
      </Modal>

      {/* Delete Confirm Modal */}
      <Modal isOpen={isDeleteOpen} onClose={() => setDeleteOpen(false)} title="Confirm Deletion" width={400}>
        <div className="turtle-detail__delete-confirm">
          <p>Are you sure you want to delete <strong>{turtle.turtleCode.toUpperCase()}</strong>? This action cannot be undone.</p>
          <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', marginTop: '20px' }}>
            <button className="btn btn--danger" onClick={handleDelete} disabled={isSaving}>
              {isSaving ? 'Deleting...' : 'Delete'}
            </button>
            <button className="btn btn--ghost" onClick={() => setDeleteOpen(false)}>Cancel</button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default TurtleDetailPage;
