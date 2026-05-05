namespace SeaTurtle.API.Models.Entities;

/// <summary>
/// Represents a single observation event where a turtle was identified.
/// Each encounter is linked to one turtle and one user (researcher).
/// </summary>
public class Encounter
{
    public Guid Id { get; set; }

    /// <summary>The identified turtle.</summary>
    public Guid TurtleId { get; set; }

    /// <summary>The user who performed the identification.</summary>
    public Guid UserId { get; set; }

    /// <summary>Date and time of the encounter.</summary>
    public DateTime EncounterDate { get; set; } = DateTime.UtcNow;

    /// <summary>Human-readable location name (e.g. "Dalyan Beach").</summary>
    public string? LocationName { get; set; }

    /// <summary>GPS latitude of the encounter location.</summary>
    public double? Latitude { get; set; }

    /// <summary>GPS longitude of the encounter location.</summary>
    public double? Longitude { get; set; }

    /// <summary>Optional researcher notes about this encounter.</summary>
    public string? Notes { get; set; }

    /// <summary>AI confidence score from identification (0.0 - 1.0).</summary>
    public float ConfidenceScore { get; set; }

    /// <summary>YOLO-detected biological side (left/right/top).</summary>
    public string BiologicalSide { get; set; } = string.Empty;

    /// <summary>
    /// Whether the AI auto-added this photo's embedding to the FAISS gallery.
    /// True only when confidence score >= AUTO_ADD_GALLERY_THRESHOLD (0.9).
    /// </summary>
    public bool GalleryUpdated { get; set; } = false;

    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    // Navigation properties
    public Turtle Turtle { get; set; } = null!;
    public User User { get; set; } = null!;
    public ICollection<Photo> Photos { get; set; } = new List<Photo>();
}
