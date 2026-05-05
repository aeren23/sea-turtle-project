// Encounter domain types — mirrors backend DTOs

/** Single encounter from GET /api/Encounters */
export interface EncounterDto {
  id:              string;   // UUID
  turtleId:        string;   // UUID
  turtleCode:      string;
  researcherName:  string;
  encounterDate:   string;   // ISO date
  locationName:    string | null;
  latitude:        number | null;
  longitude:       number | null;
  notes:           string | null;
  confidenceScore: number;   // 0.0 – 1.0
  biologicalSide:  string;   // "left" | "right" | "top"
  galleryUpdated:  boolean;
  photoUrls:       string[];
}

/** Request body for PUT /api/Encounters/{id} */
export interface UpdateEncounterRequest {
  locationName: string | null;
  latitude:     number | null;
  longitude:    number | null;
  notes:        string | null;
}
