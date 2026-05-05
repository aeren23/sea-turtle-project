import { useState, useCallback } from 'react';
import { identifyTurtle, registerUnknownTurtle } from '../api/identification.api';
import type { IdentificationResponse, RegisterUnknownRequest } from '../types/identification.types';
import { useUiStore } from '../stores/uiStore';

export type IdentificationStep = 'upload' | 'result' | 'register';

/**
 * Hook managing the 3-step identification wizard state machine.
 * Responsibility: wizard step transitions, API calls, and result state.
 */
export const useIdentification = () => {
  const [step, setStep]           = useState<IdentificationStep>('upload');
  const [result, setResult]       = useState<IdentificationResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const { addToast, setGlobalLoading } = useUiStore();

  /** Step 1 → Step 2: Upload photo and get identification result */
  const identify = useCallback(async (photoFile: File) => {
    setIsLoading(true);
    setGlobalLoading(true);
    try {
      const response = await identifyTurtle(photoFile);
      setResult(response);
      setStep('result');
    } catch {
      addToast('Identification failed. Please try again.', 'error');
    } finally {
      setIsLoading(false);
      setGlobalLoading(false);
    }
  }, [addToast, setGlobalLoading]);

  /** Step 2 (Unknown) → Step 3: Show register form */
  const proceedToRegister = useCallback(() => {
    setStep('register');
  }, []);

  /** Step 3 → Complete: Register unknown turtle as new individual */
  const registerUnknown = useCallback(async (
    data: RegisterUnknownRequest,
  ): Promise<IdentificationResponse | null> => {
    setIsLoading(true);
    try {
      const response = await registerUnknownTurtle(data);
      setResult(response);
      addToast(`New turtle registered: ${response.turtleId}`, 'success');
      return response;
    } catch {
      addToast('Registration failed. Session may have expired.', 'error');
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [addToast]);

  /** Reset wizard to initial state */
  const reset = useCallback(() => {
    setStep('upload');
    setResult(null);
  }, []);

  return { step, result, isLoading, identify, proceedToRegister, registerUnknown, reset };
};
