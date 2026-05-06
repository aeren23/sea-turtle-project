namespace SeaTurtle.API.Models.DTOs.AiService;

public class AiIdentifyResult
{
    public bool Success { get; set; }
    public bool IsKnown { get; set; }
    public string? TurtleId { get; set; }
    public float BestScore { get; set; }
    public string BiologicalSide { get; set; } = string.Empty;
    public string? SessionId { get; set; }
    public string? SavedPhotoPath { get; set; }
    public bool GalleryUpdated { get; set; }
    public string? Error { get; set; }
    
    // Detection details
    public float[]? BoundingBox { get; set; }
    public float? DetectionConfidence { get; set; }
}
