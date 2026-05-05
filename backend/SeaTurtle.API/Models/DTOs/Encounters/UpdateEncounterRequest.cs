using System.ComponentModel.DataAnnotations;

namespace SeaTurtle.API.Models.DTOs.Encounters;

public class UpdateEncounterRequest
{
    [MaxLength(500)]
    public string? LocationName { get; set; }

    public double? Latitude { get; set; }
    public double? Longitude { get; set; }

    [MaxLength(2000)]
    public string? Notes { get; set; }
}
