namespace SeaTurtle.API.Models.DTOs.Identification;

public class IdentificationResponse
{
    public bool IsKnown { get; set; }
    public string? TurtleId { get; set; }
    public float Score { get; set; }
    public string BiologicalSide { get; set; } = string.Empty;
    public string? SessionId { get; set; }
    
    // Detailed profile included if IsKnown = true
    public string? Species { get; set; }
    public string? Nickname { get; set; }
    public string? PhotoUrl { get; set; }
}
