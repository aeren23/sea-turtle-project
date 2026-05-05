using SeaTurtle.API.Models.DTOs.AiService;

namespace SeaTurtle.API.Services;

public interface IAiServiceClient
{
    /// <summary>Forward photo to ai-service for identification.</summary>
    Task<AiIdentifyResult> IdentifyAsync(Stream photoStream, string fileName);

    /// <summary>Confirm registration of an unknown turtle.</summary>
    Task<AiRegisterResult> RegisterAsync(string sessionId);

    /// <summary>Check ai-service health.</summary>
    Task<bool> HealthCheckAsync();
}
