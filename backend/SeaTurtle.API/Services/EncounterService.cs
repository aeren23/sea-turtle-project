using Microsoft.EntityFrameworkCore;
using SeaTurtle.API.Data;
using SeaTurtle.API.Models.DTOs.Encounters;
using SeaTurtle.API.Models.Entities;
using SeaTurtle.API.Models.Enums;

namespace SeaTurtle.API.Services;

public class EncounterService : IEncounterService
{
    private readonly AppDbContext _context;

    public EncounterService(AppDbContext context)
    {
        _context = context;
    }

    public async Task<IEnumerable<EncounterDto>> GetAllEncountersAsync(int skip = 0, int take = 50)
    {
        var encounters = await _context.Encounters
            .Include(e => e.Turtle)
            .Include(e => e.User)
            .Include(e => e.Photos)
            .OrderByDescending(e => e.EncounterDate)
            .Skip(skip)
            .Take(take)
            .ToListAsync();

        return encounters.Select(MapToDto);
    }

    public async Task<IEnumerable<EncounterDto>> GetEncountersByTurtleIdAsync(Guid turtleId)
    {
        var encounters = await _context.Encounters
            .Include(e => e.Turtle)
            .Include(e => e.User)
            .Include(e => e.Photos)
            .Where(e => e.TurtleId == turtleId)
            .OrderByDescending(e => e.EncounterDate)
            .ToListAsync();

        return encounters.Select(MapToDto);
    }

    public async Task<EncounterDto?> GetEncounterByIdAsync(Guid id)
    {
        var encounter = await _context.Encounters
            .Include(e => e.Turtle)
            .Include(e => e.User)
            .Include(e => e.Photos)
            .FirstOrDefaultAsync(e => e.Id == id);

        if (encounter == null) return null;

        return MapToDto(encounter);
    }

    public async Task<EncounterDto?> UpdateEncounterAsync(Guid id, UpdateEncounterRequest request, Guid currentUserId, string currentUserRole)
    {
        var encounter = await _context.Encounters.FindAsync(id);
        if (encounter == null) return null;

        // Ensure user is admin or the owner of the encounter
        if (currentUserRole != UserRole.Admin.ToString() && encounter.UserId != currentUserId)
        {
            throw new UnauthorizedAccessException("You do not have permission to modify this encounter.");
        }

        encounter.LocationName = request.LocationName;
        encounter.Latitude = request.Latitude;
        encounter.Longitude = request.Longitude;
        encounter.Notes = request.Notes;

        await _context.SaveChangesAsync();

        return await GetEncounterByIdAsync(id);
    }

    public async Task<bool> DeleteEncounterAsync(Guid id, Guid currentUserId, string currentUserRole)
    {
        var encounter = await _context.Encounters.FindAsync(id);
        if (encounter == null) return false;

        // Ensure user is admin or the owner of the encounter
        if (currentUserRole != UserRole.Admin.ToString() && encounter.UserId != currentUserId)
        {
            throw new UnauthorizedAccessException("You do not have permission to delete this encounter.");
        }

        _context.Encounters.Remove(encounter);
        await _context.SaveChangesAsync();
        return true;
    }

    private static EncounterDto MapToDto(Encounter encounter)
    {
        return new EncounterDto
        {
            Id = encounter.Id,
            TurtleId = encounter.TurtleId,
            TurtleCode = encounter.Turtle?.TurtleCode ?? "Unknown",
            ResearcherName = encounter.User?.FullName ?? "Unknown",
            EncounterDate = encounter.EncounterDate,
            LocationName = encounter.LocationName,
            Latitude = encounter.Latitude,
            Longitude = encounter.Longitude,
            Notes = encounter.Notes,
            ConfidenceScore = encounter.ConfidenceScore,
            BiologicalSide = encounter.BiologicalSide,
            GalleryUpdated = encounter.GalleryUpdated,
            PhotoUrls = encounter.Photos.Select(p => $"/photos/{encounter.Turtle?.TurtleCode}/{Path.GetFileName(p.FilePath)}").ToList()
        };
    }
}
