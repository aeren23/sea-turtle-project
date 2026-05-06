using SeaTurtle.API.Models.DTOs.Encounters;

namespace SeaTurtle.API.Services;

public interface IEncounterService
{
    Task<IEnumerable<EncounterDto>> GetAllEncountersAsync(int skip = 0, int take = 50);
    Task<IEnumerable<EncounterDto>> GetEncountersByTurtleIdAsync(string turtleIdentifier);
    Task<EncounterDto?> GetEncounterByIdAsync(Guid id);
    Task<EncounterDto?> UpdateEncounterAsync(Guid id, UpdateEncounterRequest request, Guid currentUserId, string currentUserRole);
    Task<bool> DeleteEncounterAsync(Guid id, Guid currentUserId, string currentUserRole);
}
