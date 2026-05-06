import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { updateEncounter } from '../api/encounters.api';
import { useIdentification } from '../hooks/useIdentification';
import PhotoUploadZone from '../components/ui/PhotoUploadZone';
import ResultPanel from '../components/ui/ResultPanel';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import Modal from '../components/ui/Modal';
import { TURTLE_SPECIES } from '../utils/constants';
import './IdentifyPage.css';

const registerSchema = z.object({
  species:           z.string().min(1, 'Species is required'),
  nickname:          z.string().optional(),
  locationName:      z.string().optional(),
  notes:             z.string().optional(),
});
type RegisterFormData = z.infer<typeof registerSchema>;

const updateEncounterSchema = z.object({
  locationName: z.string().optional(),
  latitude:     z.number().nullable().optional(),
  longitude:    z.number().nullable().optional(),
  notes:        z.string().optional(),
});
type UpdateEncounterFormData = z.infer<typeof updateEncounterSchema>;

/**
 * 3-step identification wizard page.
 * Step 1: Upload — Step 2: Result — Step 3: Register (if unknown)
 * Responsibility: orchestrate the wizard flow between child components.
 */
const IdentifyPage: React.FC = () => {
  const navigate = useNavigate();
  const {
    step,
    result,
    isLoading,
    identify,
    proceedToRegister,
    registerUnknown,
    reset,
  } = useIdentification();

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isRegisterModalOpen, setRegisterModalOpen] = useState(false);
  const [isUpdateEncounterOpen, setUpdateEncounterOpen] = useState(false);
  const [encounterToUpdate, setEncounterToUpdate] = useState<string | null>(null);
  const [imageScale, setImageScale] = useState({ x: 1, y: 1 });
  const [imageLoaded, setImageLoaded] = useState(false);

  const handleImageLoad = (e: React.SyntheticEvent<HTMLImageElement>) => {
    const { naturalWidth, naturalHeight, offsetWidth, offsetHeight } = e.currentTarget;
    if (naturalWidth && naturalHeight) {
      setImageScale({
        x: offsetWidth / naturalWidth,
        y: offsetHeight / naturalHeight
      });
      setImageLoaded(true);
    }
  };

  const { register, handleSubmit, formState: { errors } } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: { species: 'Unknown' },
  });

  const {
    register: registerUpdate,
    handleSubmit: handleUpdateSubmit,
    formState: { isSubmitting: isUpdatingEncounter }
  } = useForm<UpdateEncounterFormData>({
    resolver: zodResolver(updateEncounterSchema),
  });

  const handleIdentify = async () => {
    if (!selectedFile) return;
    await identify(selectedFile);
  };

  const handleProceedRegister = () => {
    proceedToRegister();
    setRegisterModalOpen(true);
  };

  const handleRegisterSubmit = async (data: RegisterFormData) => {
    if (!result?.sessionId) return;
    const registered = await registerUnknown({
      sessionId:         result.sessionId,
      species:           data.species || null,
      nickname:          data.nickname || null,
      locationName:      data.locationName || null,
      notes:             data.notes || null,
      score:             result.score,
      biologicalSide:    result.biologicalSide,
    });
    if (registered) {
      setRegisterModalOpen(false);
      navigate('/turtles');
    }
  };

  const handleEncounterUpdate = async (data: UpdateEncounterFormData) => {
    if (!encounterToUpdate) return;
    try {
      await updateEncounter(encounterToUpdate, {
        locationName: data.locationName || null,
        latitude:     data.latitude ?? null,
        longitude:    data.longitude ?? null,
        notes:        data.notes || null,
      });
      setUpdateEncounterOpen(false);
      navigate(`/turtles/${result?.turtleId}`);
    } catch (err) {
      console.error('Failed to update encounter', err);
    }
  };

  // --- Step indicators ---
  const STEPS = ['Upload', 'Result', 'Register'];
  const stepIndex = step === 'upload' ? 0 : step === 'result' ? 1 : 2;

  return (
    <div className="identify-page">
      {/* Page header */}
      <header className="identify-page__header fade-up-1">
        <div>
          <h1 className="identify-page__title">Identification Wizard</h1>
          <p className="identify-page__subtitle">
            Upload a turtle head photo · AI will match against 8,526 gallery embeddings
          </p>
        </div>

        {/* Step indicators */}
        <div className="identify-page__steps" aria-label="Wizard progress">
          {STEPS.map((label, i) => (
            <div
              key={label}
              className={`identify-page__step${i === stepIndex ? ' identify-page__step--active' : ''}${i < stepIndex ? ' identify-page__step--done' : ''}`}
              aria-current={i === stepIndex ? 'step' : undefined}
            >
              <span className="identify-page__step-num">{i < stepIndex ? '✓' : i + 1}</span>
              <span className="identify-page__step-label">{label}</span>
            </div>
          ))}
        </div>
      </header>

      {/* Step 1: Upload */}
      {step === 'upload' && (
        <div className="identify-page__content fade-up-2">
          <div className="identify-page__upload-section">
            <PhotoUploadZone onFileSelected={setSelectedFile} />

            {selectedFile && !isLoading && (
              <button
                id="run-identification-btn"
                className="btn btn--primary identify-page__identify-btn"
                onClick={handleIdentify}
                disabled={isLoading}
              >
                ⬡ Run AI Identification
              </button>
            )}
          </div>

          {isLoading && (
            <div className="identify-page__loading">
              <div className="identify-page__sonar-pulse" aria-hidden="true" />
              <LoadingSpinner label="Analyzing neural embeddings..." size="lg" />
              <p className="identify-page__loading-sub">
                Querying FAISS gallery · ResNet-50 feature extraction in progress
              </p>
            </div>
          )}
        </div>
      )}

      {/* Step 2: Result */}
      {step === 'result' && result && (
        <div className="identify-page__content fade-up" style={{ display: 'flex', gap: '2rem', alignItems: 'flex-start', flexWrap: 'wrap' }}>
          
          <div className="identify-page__preview-container">
            <img 
              src={selectedFile ? URL.createObjectURL(selectedFile) : ''} 
              alt="Uploaded turtle" 
              className="identify-page__preview-image"
              onLoad={handleImageLoad}
            />
            {imageLoaded && result.boundingBox && result.boundingBox.length === 4 && (
              <div 
                className="bbox-overlay"
                style={{
                  left: `${result.boundingBox[0] * imageScale.x}px`,
                  top: `${result.boundingBox[1] * imageScale.y}px`,
                  width: `${result.boundingBox[2] * imageScale.x}px`,
                  height: `${result.boundingBox[3] * imageScale.y}px`
                }}
              >
                <div className="bbox-overlay-label">
                  HEAD DETECTED {result.detectionConfidence ? `— ${(result.detectionConfidence * 100).toFixed(1)}%` : ''}
                </div>
              </div>
            )}
          </div>

          <div style={{ flex: '1', minWidth: '320px' }}>
            <ResultPanel
              result={result}
              onRegister={handleProceedRegister}
              onIdentifyAgain={reset}
              onAddEncounterDetails={(encounterId) => {
                setEncounterToUpdate(encounterId);
                setUpdateEncounterOpen(true);
              }}
            />
          </div>
        </div>
      )}

      {/* Registration Modal (Step 3) */}
      <Modal
        isOpen={isRegisterModalOpen}
        onClose={() => setRegisterModalOpen(false)}
        title="Register New Turtle"
        width={520}
      >
        <form
          onSubmit={handleSubmit(handleRegisterSubmit)}
          className="identify-page__register-form"
          noValidate
        >
          <p className="identify-page__register-intro">
            This turtle will be registered as a new individual in the database.
            Session ID: <code>{result?.sessionId}</code>
          </p>

          {/* Species */}
          <div className="field">
            <label className="field__label" htmlFor="reg-species">Species *</label>
            <input
              id="reg-species"
              className="field__input"
              list="species-list"
              placeholder="e.g. Caretta caretta or unknown"
              {...register('species')}
            />
            <datalist id="species-list">
              {TURTLE_SPECIES.map((s) => (
                <option key={s.value} value={s.value}>{s.label}</option>
              ))}
            </datalist>
            {errors.species && (
              <span className="field__error">{errors.species.message}</span>
            )}
          </div>

          {/* Nickname */}
          <div className="field">
            <label className="field__label" htmlFor="reg-nickname">Nickname (optional)</label>
            <input
              id="reg-nickname"
              type="text"
              className="field__input"
              placeholder="e.g. Poseidon"
              {...register('nickname')}
            />
          </div>

          {/* First seen location */}
          <div className="field">
            <label className="field__label" htmlFor="reg-location">
              First Seen Location (optional)
            </label>
            <input
              id="reg-location"
              type="text"
              className="field__input"
              placeholder="e.g. Dalyan Beach, Turkey"
              {...register('locationName')}
            />
          </div>

          {/* Notes */}
          <div className="field">
            <label className="field__label" htmlFor="reg-notes">Encounter Notes (optional)</label>
            <textarea
              id="reg-notes"
              className="field__input"
              rows={3}
              placeholder="Treatment details, distinctive marks, behaviors..."
              {...register('notes')}
            />
          </div>

          <div className="identify-page__register-actions">
            <button
              type="submit"
              className="btn btn--primary"
              disabled={isLoading}
            >
              {isLoading ? 'Registering...' : 'Confirm Registration'}
            </button>
            <button
              type="button"
              className="btn btn--ghost"
              onClick={() => setRegisterModalOpen(false)}
            >
              Cancel
            </button>
          </div>
        </form>
      </Modal>

      {/* Update Encounter Modal (for Known Turtles) */}
      <Modal
        isOpen={isUpdateEncounterOpen}
        onClose={() => setUpdateEncounterOpen(false)}
        title="Encounter Details"
        width={500}
      >
        <form
          onSubmit={handleUpdateSubmit(handleEncounterUpdate)}
          className="identify-page__register-form"
          noValidate
        >
          <p className="identify-page__register-intro">
            Add location and notes for this new sighting of <strong>{result?.turtleId?.toUpperCase()}</strong>.
          </p>

          <div className="field">
            <label className="field__label" htmlFor="enc-location">Location Name</label>
            <input
              id="enc-location"
              type="text"
              className="field__input"
              placeholder="e.g. Dalyan Beach"
              {...registerUpdate('locationName')}
            />
          </div>

          <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
            <div className="field" style={{ flex: 1, marginBottom: 0 }}>
              <label className="field__label" htmlFor="enc-lat">Latitude</label>
              <input
                id="enc-lat"
                type="number"
                step="0.0001"
                className="field__input"
                placeholder="36.8505"
                {...registerUpdate('latitude', { valueAsNumber: true })}
              />
            </div>
            <div className="field" style={{ flex: 1, marginBottom: 0 }}>
              <label className="field__label" htmlFor="enc-lng">Longitude</label>
              <input
                id="enc-lng"
                type="number"
                step="0.0001"
                className="field__input"
                placeholder="28.1234"
                {...registerUpdate('longitude', { valueAsNumber: true })}
              />
            </div>
          </div>

          <div className="field">
            <label className="field__label" htmlFor="enc-notes">Notes</label>
            <textarea
              id="enc-notes"
              className="field__input"
              rows={4}
              placeholder="Observation notes, behaviors..."
              {...registerUpdate('notes')}
            />
          </div>

          <div className="identify-page__register-actions">
            <button
              type="submit"
              className="btn btn--primary"
              disabled={isUpdatingEncounter}
            >
              {isUpdatingEncounter ? 'Saving...' : 'Save Encounter Details'}
            </button>
            <button
              type="button"
              className="btn btn--ghost"
              onClick={() => {
                setUpdateEncounterOpen(false);
                navigate(`/turtles/${result?.turtleId}`);
              }}
            >
              Skip
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default IdentifyPage;
