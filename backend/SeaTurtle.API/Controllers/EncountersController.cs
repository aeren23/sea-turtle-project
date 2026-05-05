using System.Security.Claims;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using SeaTurtle.API.Models.DTOs.Encounters;
using SeaTurtle.API.Services;

namespace SeaTurtle.API.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public class EncountersController : ControllerBase
{
    private readonly IEncounterService _encounterService;

    public EncountersController(IEncounterService encounterService)
    {
        _encounterService = encounterService;
    }

    [HttpGet]
    public async Task<ActionResult<IEnumerable<EncounterDto>>> GetAll([FromQuery] int skip = 0, [FromQuery] int take = 50)
    {
        var encounters = await _encounterService.GetAllEncountersAsync(skip, take);
        return Ok(encounters);
    }

    [HttpGet("turtle/{turtleId:guid}")]
    public async Task<ActionResult<IEnumerable<EncounterDto>>> GetByTurtleId(Guid turtleId)
    {
        var encounters = await _encounterService.GetEncountersByTurtleIdAsync(turtleId);
        return Ok(encounters);
    }

    [HttpGet("{id:guid}")]
    public async Task<ActionResult<EncounterDto>> GetById(Guid id)
    {
        var encounter = await _encounterService.GetEncounterByIdAsync(id);
        
        if (encounter == null) return NotFound();

        return Ok(encounter);
    }

    [HttpPut("{id:guid}")]
    public async Task<ActionResult<EncounterDto>> Update(Guid id, [FromBody] UpdateEncounterRequest request)
    {
        try
        {
            var userId = Guid.Parse(User.FindFirstValue(ClaimTypes.NameIdentifier)!);
            var role = User.FindFirstValue(ClaimTypes.Role)!;

            var encounter = await _encounterService.UpdateEncounterAsync(id, request, userId, role);
            
            if (encounter == null) return NotFound();

            return Ok(encounter);
        }
        catch (UnauthorizedAccessException ex)
        {
            return Forbid(ex.Message); // 403 Forbidden
        }
    }

    [HttpDelete("{id:guid}")]
    public async Task<ActionResult> Delete(Guid id)
    {
        try
        {
            var userId = Guid.Parse(User.FindFirstValue(ClaimTypes.NameIdentifier)!);
            var role = User.FindFirstValue(ClaimTypes.Role)!;

            var success = await _encounterService.DeleteEncounterAsync(id, userId, role);
            
            if (!success) return NotFound();

            return NoContent();
        }
        catch (UnauthorizedAccessException ex)
        {
            return Forbid(ex.Message); // 403 Forbidden
        }
    }
}
