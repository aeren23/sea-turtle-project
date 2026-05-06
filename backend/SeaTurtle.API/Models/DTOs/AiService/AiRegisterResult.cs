namespace SeaTurtle.API.Models.DTOs.AiService;

public class AiRegisterResult
{
    public bool Success { get; set; }
    public string? TurtleId { get; set; }
    public string? Error { get; set; }
    public string? SavedPhotoPath { get; set; }
}
