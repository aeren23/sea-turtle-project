import { PHOTOS_BASE_URL } from './constants';

/**
 * Formats an ISO date string to a human-readable "DD MMM YYYY" format.
 * Example: "2026-05-05T14:30:00Z" → "05 May 2026"
 */
export const formatDate = (isoString: string | Date): string => {
  const date = typeof isoString === 'string' ? new Date(isoString) : isoString;
  return date.toLocaleDateString('en-GB', {
    day:   '2-digit',
    month: 'short',
    year:  'numeric',
  });
};

/**
 * Formats an ISO date string to include time.
 * Example: "2026-05-05T14:30:00Z" → "05 May 2026, 14:30"
 */
export const formatDateTime = (isoString: string | Date): string => {
  const date = typeof isoString === 'string' ? new Date(isoString) : isoString;
  return date.toLocaleDateString('en-GB', {
    day:    '2-digit',
    month:  'short',
    year:   'numeric',
    hour:   '2-digit',
    minute: '2-digit',
  });
};

/**
 * Formats a confidence score (0.0 – 1.0) as a percentage string.
 * Example: 0.8763 → "87.6%"
 */
export const formatConfidence = (score: number): string => {
  return `${(score * 100).toFixed(1)}%`;
};

/**
 * Returns the color token name for a confidence score value.
 * Used to drive conditional styling without magic numbers in components.
 */
export const getConfidenceLevel = (score: number): 'high' | 'mid' | 'low' => {
  if (score >= 0.80) return 'high';
  if (score >= 0.60) return 'mid';
  return 'low';
};

/**
 * Builds the full URL for a turtle photo served by the .NET static files middleware.
 * Example: buildPhotoUrl("t042", "photo_001.jpg") → "/photos/t042/photo_001.jpg"
 */
export const buildPhotoUrl = (turtleCode: string, filename: string): string => {
  return `${PHOTOS_BASE_URL}/${turtleCode}/${filename}`;
};

/**
 * Formats decimal coordinates to a human-readable string.
 * Example: (36.8505, 30.4226) → "36.8505° N, 30.4226° E"
 */
export const formatCoordinates = (lat: number, lng: number): string => {
  const latDir = lat >= 0 ? 'N' : 'S';
  const lngDir = lng >= 0 ? 'E' : 'W';
  return `${Math.abs(lat).toFixed(4)}° ${latDir}, ${Math.abs(lng).toFixed(4)}° ${lngDir}`;
};

/**
 * Capitalises the first letter of a string.
 * Example: "left" → "Left"
 */
export const capitalise = (str: string): string =>
  str.charAt(0).toUpperCase() + str.slice(1);
