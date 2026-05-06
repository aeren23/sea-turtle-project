// API base — in Docker: proxied by nginx to seaturtle-api:8080
// In local dev: Vite proxy forwards to localhost:5000
export const API_BASE_URL = '/api';
export const PHOTOS_BASE_URL = '/photos';

// Identification thresholds (mirrors backend IDENTIFICATION_THRESHOLD = 0.6)
export const CONFIDENCE_HIGH_THRESHOLD = 0.80;
export const CONFIDENCE_MID_THRESHOLD  = 0.60;

// Pagination defaults
export const DEFAULT_PAGE_SIZE = 12;
export const ENCOUNTER_PAGE_SIZE = 15;

// Species list (from project spec)
export const TURTLE_SPECIES = [
  { value: 'Chelonia mydas',    label: 'Green Turtle (Chelonia mydas)' },
  { value: 'Caretta caretta',   label: 'Loggerhead (Caretta caretta)' },
  { value: 'Unknown',           label: 'Unknown Species' },
] as const;

// Biological sides
export const BIOLOGICAL_SIDES = ['left', 'right', 'top'] as const;

// JWT token storage key
export const AUTH_TOKEN_KEY = 'st_jwt_token';
export const AUTH_USER_KEY  = 'st_user';

// Max photo upload size: 10 MB
export const MAX_PHOTO_BYTES = 10 * 1024 * 1024;

// Accepted image MIME types
export const ACCEPTED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp'];

// Recent encounters count on dashboard
export const DASHBOARD_RECENT_COUNT = 5;
