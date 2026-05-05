namespace SeaTurtle.API.Models.DTOs.Turtles;

public class TurtleDto
{
    public Guid Id { get; set; }
    public string TurtleCode { get; set; } = string.Empty;
    public string? Species { get; set; }
    public string? Nickname { get; set; }
    public DateTime FirstSeenAt { get; set; }
    public string? FirstSeenLocation { get; set; }
    public DateTime? LastSeenAt { get; set; }
    public int EncounterCount { get; set; }
    public string? ProfilePhotoUrl { get; set; }
}
