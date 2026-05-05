using SeaTurtle.API.Models.DTOs.Identification;

namespace SeaTurtle.API.Services;

public interface IIdentificationService
{
    Task<IdentificationResponse> IdentifyAsync(Stream photoStream, string fileName, string contentType, long fileSizeBytes, Guid userId);
    Task<IdentificationResponse> RegisterUnknownAsync(RegisterUnknownRequest request, Guid userId);
}
