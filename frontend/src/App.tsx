import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { useAuthStore } from './stores/authStore';

// Layout
import AppLayout from './components/layout/AppLayout';

// Pages
import LoginPage         from './pages/LoginPage';
import DashboardPage     from './pages/DashboardPage';
import IdentifyPage      from './pages/IdentifyPage';
import TurtleCatalogPage from './pages/TurtleCatalogPage';
import TurtleDetailPage  from './pages/TurtleDetailPage';
import EncountersPage    from './pages/EncountersPage';

/**
 * ProtectedRoute — redirects unauthenticated users to /login.
 * Reads token from the persistent auth store.
 */
const ProtectedRoute: React.FC = () => {
  const { token } = useAuthStore();
  return token ? <Outlet /> : <Navigate to="/login" replace />;
};

/**
 * Root application router.
 * All authenticated routes are nested under AppLayout.
 * Public routes (login) render outside the authenticated shell.
 */
const App: React.FC = () => (
  <BrowserRouter>
    <Routes>
      {/* Public */}
      <Route path="/login" element={<LoginPage />} />

      {/* Protected — all nested under AppLayout shell */}
      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard"    element={<DashboardPage />} />
          <Route path="/identify"     element={<IdentifyPage />} />
          <Route path="/turtles"      element={<TurtleCatalogPage />} />
          <Route path="/turtles/:id"  element={<TurtleDetailPage />} />
          <Route path="/encounters"   element={<EncountersPage />} />
        </Route>
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  </BrowserRouter>
);

export default App;
