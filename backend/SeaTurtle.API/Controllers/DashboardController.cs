using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using SeaTurtle.API.Data;
using SeaTurtle.API.Models.DTOs.Dashboard;
using SeaTurtle.API.Models.DTOs.Encounters;

namespace SeaTurtle.API.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public class DashboardController : ControllerBase
{
    private readonly AppDbContext _context;

    public DashboardController(AppDbContext context)
    {
        _context = context;
    }

    [HttpGet("stats")]
    public async Task<ActionResult<DashboardStatsDto>> GetStats()
    {
        var stats = new DashboardStatsDto
        {
            TotalTurtles = await _context.Turtles.CountAsync(t => !t.IsDeleted),
            TotalEncounters = await _context.Encounters.CountAsync(),
            TotalPhotos = await _context.Photos.CountAsync(),
            TotalResearchers = await _context.Users.CountAsync(u => u.IsActive)
        };

        return Ok(stats);
    }

    [HttpGet("recent-encounters")]
    public async Task<ActionResult<IEnumerable<EncounterDto>>> GetRecentEncounters([FromQuery] int count = 5)
    {
        var encounters = await _context.Encounters
            .Include(e => e.Turtle)
            .Include(e => e.User)
            .Include(e => e.Photos)
            .OrderByDescending(e => e.EncounterDate)
            .Take(count)
            .Select(e => new EncounterDto
            {
                Id = e.Id,
                TurtleId = e.TurtleId,
                TurtleCode = e.Turtle != null ? e.Turtle.TurtleCode : "Unknown",
                ResearcherName = e.User != null ? e.User.FullName : "Unknown",
                EncounterDate = e.EncounterDate,
                LocationName = e.LocationName,
                ConfidenceScore = e.ConfidenceScore,
                BiologicalSide = e.BiologicalSide,
                GalleryUpdated = e.GalleryUpdated,
                PhotoUrls = e.Photos.Select(p => $"/photos/{e.Turtle!.TurtleCode}/{Path.GetFileName(p.FilePath)}").ToList()
            })
            .ToListAsync();

        return Ok(encounters);
    }
}
