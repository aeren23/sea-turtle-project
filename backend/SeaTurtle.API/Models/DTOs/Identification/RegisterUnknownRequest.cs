using System.ComponentModel.DataAnnotations;

namespace SeaTurtle.API.Models.DTOs.Identification;

public class RegisterUnknownRequest
{
    [Required]
    public string SessionId { get; set; } = string.Empty;

    [MaxLength(100)]
    public string? Species { get; set; }

    [MaxLength(100)]
    public string? Nickname { get; set; }

    [MaxLength(500)]
    public string? LocationName { get; set; }

    public double? Latitude { get; set; }
    public double? Longitude { get; set; }

    [MaxLength(2000)]
    public string? Notes { get; set; }
}
