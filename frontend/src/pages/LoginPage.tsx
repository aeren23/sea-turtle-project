import React, { useState } from 'react';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuth } from '../hooks/useAuth';
import SonarRing from '../components/SonarRing';
import './LoginPage.css';

const loginSchema = z.object({
  email: z.string().email('Enter a valid email address'),
  password: z.string().min(1, 'Password is required'),
});

const registerSchema = z.object({
  fullName: z.string().min(2, 'Full name must be at least 2 characters'),
  email: z.string().email('Enter a valid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
});

type LoginFormData = z.infer<typeof loginSchema>;
type RegisterFormData = z.infer<typeof registerSchema>;

/**
 * Login and Registration page.
 * Split layout: decorative ocean panel (left) + auth form (right).
 * Toggles between login and register mode.
 */
const LoginPage: React.FC = () => {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const { login, register, isLoading } = useAuth();

  const isRegister = mode === 'register';

  const {
    register: registerField,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<LoginFormData | RegisterFormData>({
    resolver: zodResolver(isRegister ? registerSchema : loginSchema),
  });

  const handleToggleMode = () => {
    setMode((m) => (m === 'login' ? 'register' : 'login'));
    reset();
  };

  const onSubmit = async (data: LoginFormData | RegisterFormData) => {
    if (isRegister) {
      await register(data as RegisterFormData);
    } else {
      await login(data as LoginFormData);
    }
  };

  return (
    <div className="login-page">
      {/* Left decorative panel */}
      <aside className="login-page__deco" aria-hidden="true">
        <div className="login-page__deco-content">
          <div className="login-page__sonar-wrap">
            <SonarRing size={200} rings={4} />
          </div>
          <h1 className="login-page__brand">SeaTurtle<br />Photo-ID</h1>
          <p className="login-page__tagline">
            Biometric identification system for<br />
            <em>Chelonia mydas</em> &amp; <em>Caretta caretta</em>
          </p>

          {/* Decorative data lines */}
          <div className="login-page__data-lines">
            <span>MEDS Station · Mediterranean</span>
            <span>FAISS Gallery · 8,526 vectors</span>
            <span>ResNet-50 · 512-d embeddings</span>
            <span>System nominal ●</span>
          </div>
        </div>
      </aside>

      {/* Right form panel */}
      <section className="login-page__form-panel">
        <div className="login-page__form-wrap">
          <header className="login-page__form-header">
            <h2 className="login-page__form-title">
              {isRegister ? 'Create Account' : 'Field Station Login'}
            </h2>
            <p className="login-page__form-sub">
              {isRegister
                ? 'Register as a researcher to access the identification system.'
                : 'Authenticate to access the SeaTurtle Photo-ID platform.'}
            </p>
          </header>

          <form
            className="login-page__form"
            onSubmit={handleSubmit(onSubmit)}
            noValidate
          >
            {/* Full name — register only */}
            {isRegister && (
              <div className="field fade-up-1">
                <label className="field__label" htmlFor="fullName">Full Name</label>
                <input
                  id="fullName"
                  type="text"
                  className="field__input"
                  placeholder="Dr. Jane Researcher"
                  autoComplete="name"
                  {...registerField('fullName' as keyof RegisterFormData)}
                />
                {(errors as Record<string, { message?: string }>).fullName && (
                  <span className="field__error" role="alert">
                    {(errors as Record<string, { message?: string }>).fullName?.message}
                  </span>
                )}
              </div>
            )}

            {/* Email */}
            <div className={`field ${isRegister ? 'fade-up-2' : 'fade-up-1'}`}>
              <label className="field__label" htmlFor="email">Email</label>
              <input
                id="email"
                type="email"
                className="field__input"
                placeholder="researcher@dekamer.org"
                autoComplete="email"
                {...registerField('email')}
              />
              {errors.email && (
                <span className="field__error" role="alert">{errors.email.message}</span>
              )}
            </div>

            {/* Password */}
            <div className={`field ${isRegister ? 'fade-up-3' : 'fade-up-2'}`}>
              <label className="field__label" htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                className="field__input"
                placeholder="••••••••"
                autoComplete={isRegister ? 'new-password' : 'current-password'}
                {...registerField('password')}
              />
              {errors.password && (
                <span className="field__error" role="alert">{errors.password.message}</span>
              )}
            </div>

            {/* Submit */}
            <button
              type="submit"
              className={`btn btn--primary login-page__submit ${isRegister ? 'fade-up-4' : 'fade-up-3'}`}
              disabled={isLoading}
            >
              {isLoading
                ? 'Please wait...'
                : isRegister ? 'Create Account' : 'Sign In'}
            </button>
          </form>

          {/* Mode toggle */}
          <p className="login-page__toggle-mode">
            {isRegister ? 'Already have an account?' : "Don't have an account?"}
            {' '}
            <button className="login-page__toggle-btn" onClick={handleToggleMode}>
              {isRegister ? 'Sign In' : 'Create Account'}
            </button>
          </p>

          {/* Default creds hint (dev convenience) */}
          {!isRegister && (
            <p className="login-page__hint">
              Default: <code>admin@seaturtle.org</code> / <code>Admin123!</code>
            </p>
          )}
        </div>
      </section>
    </div>
  );
};

export default LoginPage;
