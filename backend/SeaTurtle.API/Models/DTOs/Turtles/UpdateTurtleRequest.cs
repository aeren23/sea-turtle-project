using System.ComponentModel.DataAnnotations;

namespace SeaTurtle.API.Models.DTOs.Turtles;

public class UpdateTurtleRequest
{
    [MaxLength(100)]
    public string? Species { get; set; }

    [MaxLength(100)]
    public string? Nickname { get; set; }

    [MaxLength(500)]
    public string? FirstSeenLocation { get; set; }
}
