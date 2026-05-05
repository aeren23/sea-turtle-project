// Turtle domain types — mirrors backend DTOs

/** Paginated list item from GET /api/Turtles */
export interface TurtleDto {
  id:                 string;   // UUID
  turtleCode:         string;   // e.g. "t042"
  species:            string | null;
  nickname:           string | null;
  firstSeenAt:        string;   // ISO date
  firstSeenLocation:  string | null;
  lastSeenAt:         string | null;
  encounterCount:     number;
  profilePhotoUrl:    string | null;
}

/** Request body for PUT /api/Turtles/{id} */
export interface UpdateTurtleRequest {
  nickname:          string | null;
  species:           string | null;
  firstSeenLocation: string | null;
}
