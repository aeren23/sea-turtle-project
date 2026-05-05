using System.Security.Claims;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using SeaTurtle.API.Models.DTOs.Identification;
using SeaTurtle.API.Services;

namespace SeaTurtle.API.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public class IdentificationController : ControllerBase
{
    private readonly IIdentificationService _identificationService;
    private readonly ILogger<IdentificationController> _logger;

    public IdentificationController(IIdentificationService identificationService, ILogger<IdentificationController> logger)
    {
        _identificationService = identificationService;
        _logger = logger;
    }

    [HttpPost("identify")]
    [Consumes("multipart/form-data")]
    public async Task<ActionResult<IdentificationResponse>> Identify(IFormFile photo)
    {
        if (photo == null || photo.Length == 0)
        {
            return BadRequest(new { message = "Valid photo file is required." });
        }

        var userIdStr = User.FindFirstValue(ClaimTypes.NameIdentifier);
        if (!Guid.TryParse(userIdStr, out var userId))
        {
            return Unauthorized();
        }

        try
        {
            using var stream = photo.OpenReadStream();
            var response = await _identificationService.IdentifyAsync(
                stream, 
                photo.FileName, 
                photo.ContentType, 
                photo.Length, 
                userId);

            return Ok(response);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Identification error");
            return StatusCode(500, new { message = "An error occurred during identification." });
        }
    }

    [HttpPost("register")]
    public async Task<ActionResult<IdentificationResponse>> RegisterUnknown([FromBody] RegisterUnknownRequest request)
    {
        var userIdStr = User.FindFirstValue(ClaimTypes.NameIdentifier);
        if (!Guid.TryParse(userIdStr, out var userId))
        {
            return Unauthorized();
        }

        try
        {
            var response = await _identificationService.RegisterUnknownAsync(request, userId);
            return Ok(response);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Registration error");
            return StatusCode(500, new { message = "An error occurred during registration." });
        }
    }
}
