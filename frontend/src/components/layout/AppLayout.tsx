import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import DataStrip from './DataStrip';
import ToastContainer from '../ui/ToastContainer';
import './AppLayout.css';

/**
 * Root layout for authenticated routes.
 * Composes: DataStrip | Sidebar | Main content area
 * Responsibility: spatial composition of the application shell.
 */
const AppLayout: React.FC = () => (
  <div className="app-layout">
    <DataStrip />
    <Sidebar />

    <main className="app-layout__main" id="main-content">
      <Outlet />
    </main>

    <ToastContainer />
  </div>
);

export default AppLayout;
