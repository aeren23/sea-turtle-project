// Identification domain types — mirrors backend DTOs

/** Response from POST /api/Identification/identify */
export interface IdentificationResponse {
  isKnown:        boolean;
  turtleId:       string | null;   // e.g. "t042"
  score:          number;          // cosine similarity 0.0 – 1.0
  biologicalSide: string;          // "left" | "right" | "top"
  sessionId:      string | null;   // used if isKnown = false → register

  // Only populated when isKnown = true
  species:        string | null;
  nickname:       string | null;
  photoUrl:       string | null;
}

/** Request body for POST /api/Identification/register */
export interface RegisterUnknownRequest {
  sessionId:         string;
  species:           string | null;
  nickname:          string | null;
  firstSeenLocation: string | null;
}

/** Dashboard statistics from GET /api/Dashboard/stats */
export interface DashboardStatsDto {
  totalTurtles:     number;
  totalEncounters:  number;
  totalPhotos:      number;
  totalResearchers: number;
}
