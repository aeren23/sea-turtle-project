using Microsoft.EntityFrameworkCore;
using SeaTurtle.API.Data;
using SeaTurtle.API.Models.DTOs.Turtles;
using SeaTurtle.API.Models.Entities;

namespace SeaTurtle.API.Services;

public class TurtleService : ITurtleService
{
    private readonly AppDbContext _context;

    public TurtleService(AppDbContext context)
    {
        _context = context;
    }

    public async Task<IEnumerable<TurtleDto>> GetAllTurtlesAsync(int skip = 0, int take = 50)
    {
        var turtles = await _context.Turtles
            .Include(t => t.Encounters)
            .Include(t => t.Photos)
            .OrderByDescending(t => t.LastSeenAt ?? t.FirstSeenAt)
            .Skip(skip)
            .Take(take)
            .ToListAsync();

        return turtles.Select(MapToDto);
    }

    public async Task<TurtleDto?> GetTurtleByIdAsync(Guid id)
    {
        var turtle = await _context.Turtles
            .Include(t => t.Encounters)
            .Include(t => t.Photos)
            .FirstOrDefaultAsync(t => t.Id == id);

        if (turtle == null) return null;

        return MapToDto(turtle);
    }

    public async Task<TurtleDto?> UpdateTurtleAsync(Guid id, UpdateTurtleRequest request)
    {
        var turtle = await _context.Turtles.FindAsync(id);
        if (turtle == null) return null;

        turtle.Species = request.Species;
        turtle.Nickname = request.Nickname;

        await _context.SaveChangesAsync();

        // Need includes for DTO mapping
        return await GetTurtleByIdAsync(id);
    }

    public async Task<bool> DeleteTurtleAsync(Guid id)
    {
        var turtle = await _context.Turtles.FindAsync(id);
        if (turtle == null) return false;

        turtle.IsDeleted = true; // Soft delete
        await _context.SaveChangesAsync();
        return true;
    }

    private static TurtleDto MapToDto(Turtle turtle)
    {
        // Find a profile photo (try to get a left or right side if possible, otherwise any)
        var profilePhoto = turtle.Photos.FirstOrDefault(p => p.BiologicalSide == "left" || p.BiologicalSide == "right") 
                           ?? turtle.Photos.FirstOrDefault();

        var photoUrl = profilePhoto != null 
            ? $"/photos/{turtle.TurtleCode}/{Path.GetFileName(profilePhoto.FilePath)}" 
            : null;

        return new TurtleDto
        {
            Id = turtle.Id,
            TurtleCode = turtle.TurtleCode,
            Species = turtle.Species,
            Nickname = turtle.Nickname,
            FirstSeenAt = turtle.FirstSeenAt,
            FirstSeenLocation = turtle.FirstSeenLocation,
            LastSeenAt = turtle.LastSeenAt,
            EncounterCount = turtle.Encounters.Count,
            ProfilePhotoUrl = photoUrl
        };
    }
}
