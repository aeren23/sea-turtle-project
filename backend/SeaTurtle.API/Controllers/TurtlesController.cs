using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using SeaTurtle.API.Models.DTOs.Turtles;
using SeaTurtle.API.Services;

namespace SeaTurtle.API.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public class TurtlesController : ControllerBase
{
    private readonly ITurtleService _turtleService;

    public TurtlesController(ITurtleService turtleService)
    {
        _turtleService = turtleService;
    }

    [HttpGet]
    public async Task<ActionResult<IEnumerable<TurtleDto>>> GetAll([FromQuery] int skip = 0, [FromQuery] int take = 50)
    {
        var turtles = await _turtleService.GetAllTurtlesAsync(skip, take);
        return Ok(turtles);
    }

    [HttpGet("{id:guid}")]
    public async Task<ActionResult<TurtleDto>> GetById(Guid id)
    {
        var turtle = await _turtleService.GetTurtleByIdAsync(id);
        
        if (turtle == null) return NotFound();

        return Ok(turtle);
    }

    [HttpPut("{id:guid}")]
    public async Task<ActionResult<TurtleDto>> Update(Guid id, [FromBody] UpdateTurtleRequest request)
    {
        var turtle = await _turtleService.UpdateTurtleAsync(id, request);
        
        if (turtle == null) return NotFound();

        return Ok(turtle);
    }

    [HttpDelete("{id:guid}")]
    [Authorize(Roles = "Admin")] // Only admins can soft-delete turtles
    public async Task<ActionResult> Delete(Guid id)
    {
        var success = await _turtleService.DeleteTurtleAsync(id);
        
        if (!success) return NotFound();

        return NoContent();
    }
}
