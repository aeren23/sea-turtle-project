using SeaTurtle.API.Models.DTOs.Turtles;

namespace SeaTurtle.API.Services;

public interface ITurtleService
{
    Task<IEnumerable<TurtleDto>> GetAllTurtlesAsync(int skip = 0, int take = 50);
    Task<TurtleDto?> GetTurtleByIdAsync(string identifier);
    Task<TurtleDto?> UpdateTurtleAsync(Guid id, UpdateTurtleRequest request);
    Task<bool> DeleteTurtleAsync(Guid id);
}
