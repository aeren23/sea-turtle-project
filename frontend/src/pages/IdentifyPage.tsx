import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
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
  firstSeenLocation: z.string().optional(),
});
type RegisterFormData = z.infer<typeof registerSchema>;

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

  const { register, handleSubmit, formState: { errors } } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: { species: 'Unknown' },
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
      firstSeenLocation: data.firstSeenLocation || null,
    });
    if (registered) {
      setRegisterModalOpen(false);
      navigate('/turtles');
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
        <div className="identify-page__content fade-up">
          <ResultPanel
            result={result}
            onRegister={handleProceedRegister}
            onIdentifyAgain={reset}
          />
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
            <select id="reg-species" className="field__input" {...register('species')}>
              {TURTLE_SPECIES.map((s) => (
                <option key={s.value} value={s.value}>{s.label}</option>
              ))}
            </select>
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
              {...register('firstSeenLocation')}
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
    </div>
  );
};

export default IdentifyPage;
