import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getDashboardStats, getRecentEncounters } from '../api/dashboard.api';
import type { DashboardStatsDto } from '../types/identification.types';
import type { EncounterDto } from '../types/encounter.types';
import StatCard from '../components/ui/StatCard';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import { formatDateTime, formatConfidence, getConfidenceLevel, capitalise } from '../utils/formatters';
import { useAuthStore } from '../stores/authStore';
import './DashboardPage.css';

/**
 * Main dashboard — system overview with stats and recent activity feed.
 * Responsibility: compose dashboard widgets from stats and recent encounters data.
 */
const DashboardPage: React.FC = () => {
  const [stats, setStats]           = useState<DashboardStatsDto | null>(null);
  const [encounters, setEncounters] = useState<EncounterDto[]>([]);
  const [isLoading, setIsLoading]   = useState(true);
  const { user } = useAuthStore();

  useEffect(() => {
    const fetchDashboardData = async () => {
      setIsLoading(true);
      try {
        const [statsData, encountersData] = await Promise.all([
          getDashboardStats(),
          getRecentEncounters(5),
        ]);
        setStats(statsData);
        setEncounters(encountersData);
      } finally {
        setIsLoading(false);
      }
    };
    fetchDashboardData();
  }, []);

  if (isLoading) {
    return (
      <div className="dashboard-loading">
        <LoadingSpinner label="Loading dashboard..." size="lg" />
      </div>
    );
  }

  return (
    <div className="dashboard">
      {/* Page header */}
      <header className="dashboard__header fade-up-1">
        <div>
          <h1 className="dashboard__title">Mission Control</h1>
          <p className="dashboard__subtitle">
            Welcome back, <strong>{user?.fullName ?? 'Researcher'}</strong>
          </p>
        </div>
        <Link to="/identify" className="btn btn--primary dashboard__cta" id="identify-cta">
          ⬡ Identify Turtle
        </Link>
      </header>

      {/* Stat cards */}
      {stats && (
        <div className="dashboard__stats" role="region" aria-label="System statistics">
          <StatCard label="Turtles Tracked"   value={stats.totalTurtles}     icon="◉" delayIndex={0} />
          <StatCard label="Total Encounters"  value={stats.totalEncounters}  icon="◎" delayIndex={1} />
          <StatCard label="Photos Archived"   value={stats.totalPhotos}      icon="◈" delayIndex={2} />
          <StatCard label="Active Researchers" value={stats.totalResearchers} icon="⬡" delayIndex={3} />
        </div>
      )}

      {/* Recent activity */}
      <section className="dashboard__recent fade-up-4" aria-labelledby="recent-label">
        <header className="dashboard__section-header">
          <h2 id="recent-label" className="dashboard__section-title">Recent Encounters</h2>
          <Link to="/encounters" className="btn btn--ghost dashboard__see-all">
            View All →
          </Link>
        </header>

        {encounters.length === 0 ? (
          <p className="dashboard__empty">No encounters recorded yet.</p>
        ) : (
          <div className="dashboard__encounter-list">
            {encounters.map((enc) => {
              const level = getConfidenceLevel(enc.confidenceScore);
              return (
                <div key={enc.id} className="dashboard__encounter-item">
                  <div className="dashboard__encounter-turtle">
                    <Link
                      to={`/turtles/${enc.turtleId}`}
                      className="dashboard__encounter-code"
                    >
                      {enc.turtleCode.toUpperCase()}
                    </Link>
                    <span className="tag">{capitalise(enc.biologicalSide)}</span>
                  </div>

                  <div className="dashboard__encounter-meta">
                    <span>{enc.locationName ?? 'Unknown location'}</span>
                    <span>{enc.researcherName}</span>
                  </div>

                  <div className="dashboard__encounter-score">
                    <span className={`dashboard__confidence dashboard__confidence--${level}`}>
                      {formatConfidence(enc.confidenceScore)}
                    </span>
                    <span className="dashboard__encounter-date">
                      {formatDateTime(enc.encounterDate)}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
};

export default DashboardPage;
