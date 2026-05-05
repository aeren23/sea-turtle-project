namespace SeaTurtle.API.Models.DTOs.Encounters;

public class EncounterDto
{
    public Guid Id { get; set; }
    public Guid TurtleId { get; set; }
    public string TurtleCode { get; set; } = string.Empty;
    public string ResearcherName { get; set; } = string.Empty;
    public DateTime EncounterDate { get; set; }
    public string? LocationName { get; set; }
    public double? Latitude { get; set; }
    public double? Longitude { get; set; }
    public string? Notes { get; set; }
    public float ConfidenceScore { get; set; }
    public string BiologicalSide { get; set; } = string.Empty;
    public bool GalleryUpdated { get; set; }
    public List<string> PhotoUrls { get; set; } = new List<string>();
}
