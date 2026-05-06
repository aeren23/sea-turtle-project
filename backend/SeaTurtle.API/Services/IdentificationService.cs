using Microsoft.EntityFrameworkCore;
using SeaTurtle.API.Data;
using SeaTurtle.API.Models.DTOs.Identification;
using SeaTurtle.API.Models.Entities;

namespace SeaTurtle.API.Services;

public class IdentificationService : IIdentificationService
{
    private readonly IAiServiceClient _aiClient;
    private readonly AppDbContext _context;
    private readonly ILogger<IdentificationService> _logger;

    public IdentificationService(IAiServiceClient aiClient, AppDbContext context, ILogger<IdentificationService> logger)
    {
        _aiClient = aiClient;
        _context = context;
        _logger = logger;
    }

    public async Task<IdentificationResponse> IdentifyAsync(Stream photoStream, string fileName, string contentType, long fileSizeBytes, Guid userId)
    {
        // 1. Forward to ai-service
        var aiResult = await _aiClient.IdentifyAsync(photoStream, fileName);

        if (!aiResult.Success)
        {
            throw new Exception($"AI Identification failed: {aiResult.Error}");
        }

        // 2. Handle Known Turtle
        if (aiResult.IsKnown && !string.IsNullOrEmpty(aiResult.TurtleId))
        {
            var turtle = await _context.Turtles.FirstOrDefaultAsync(t => t.TurtleCode == aiResult.TurtleId);
            
            // If turtle exists in FAISS but not in our DB (edge case before seed), create a stub
            if (turtle == null)
            {
                turtle = new Turtle
                {
                    TurtleCode = aiResult.TurtleId,
                    FirstSeenAt = DateTime.UtcNow
                };
                _context.Turtles.Add(turtle);
            }

            turtle.LastSeenAt = DateTime.UtcNow;

            var encounter = new Encounter
            {
                Turtle = turtle,
                UserId = userId,
                ConfidenceScore = aiResult.BestScore,
                BiologicalSide = aiResult.BiologicalSide,
                GalleryUpdated = aiResult.GalleryUpdated
            };
            _context.Encounters.Add(encounter);

            if (!string.IsNullOrEmpty(aiResult.SavedPhotoPath))
            {
                var photo = new Photo
                {
                    Turtle = turtle,
                    Encounter = encounter,
                    FilePath = aiResult.SavedPhotoPath,
                    OriginalFileName = fileName,
                    FileSizeBytes = fileSizeBytes,
                    ContentType = contentType,
                    BiologicalSide = aiResult.BiologicalSide
                };
                _context.Photos.Add(photo);
            }

            await _context.SaveChangesAsync();

            return new IdentificationResponse
            {
                IsKnown = true,
                TurtleId = turtle.TurtleCode,
                Score = aiResult.BestScore,
                BiologicalSide = aiResult.BiologicalSide,
                Species = turtle.Species,
                Nickname = turtle.Nickname,
                PhotoUrl = $"/photos/{turtle.TurtleCode}/{Path.GetFileName(aiResult.SavedPhotoPath?.Replace('\\', '/'))}",
                EncounterId = encounter.Id,
                BoundingBox = aiResult.BoundingBox,
                DetectionConfidence = aiResult.DetectionConfidence
            };
        }

        // 3. Handle Unknown Turtle
        return new IdentificationResponse
        {
            IsKnown = false,
            Score = aiResult.BestScore,
            BiologicalSide = aiResult.BiologicalSide,
            SessionId = aiResult.SessionId,
            BoundingBox = aiResult.BoundingBox,
            DetectionConfidence = aiResult.DetectionConfidence
        };
    }

    public async Task<IdentificationResponse> RegisterUnknownAsync(RegisterUnknownRequest request, Guid userId)
    {
        // 1. Confirm registration with ai-service
        var aiResult = await _aiClient.RegisterAsync(request.SessionId);

        if (!aiResult.Success || string.IsNullOrEmpty(aiResult.TurtleId))
        {
            throw new Exception($"AI Registration failed: {aiResult.Error}");
        }

        // 2. Create new Turtle in DB
        var turtle = new Turtle
        {
            TurtleCode = aiResult.TurtleId,
            Species = request.Species,
            Nickname = request.Nickname,
            FirstSeenLocation = request.LocationName,
            FirstSeenAt = DateTime.UtcNow,
            LastSeenAt = DateTime.UtcNow
        };
        _context.Turtles.Add(turtle);

        // 3. Create Encounter
        var encounter = new Encounter
        {
            Turtle = turtle,
            UserId = userId,
            LocationName = request.LocationName,
            Latitude = request.Latitude,
            Longitude = request.Longitude,
            Notes = request.Notes,
            ConfidenceScore = request.Score,
            BiologicalSide = string.IsNullOrEmpty(request.BiologicalSide) ? "unknown" : request.BiologicalSide,
            GalleryUpdated = true // Always true for a new registration
        };
        _context.Encounters.Add(encounter);

        // Note: For registrations, ai-service moves the photo to the new folder.
        // We now fetch the final path from ai-service to insert a Photo record.
        if (!string.IsNullOrEmpty(aiResult.SavedPhotoPath))
        {
            var photo = new Photo
            {
                Encounter = encounter,
                Turtle = turtle,
                FilePath = aiResult.SavedPhotoPath,
                UploadedAt = DateTime.UtcNow
            };
            _context.Photos.Add(photo);
        }

        await _context.SaveChangesAsync();

        return new IdentificationResponse
        {
            IsKnown = true,
            TurtleId = turtle.TurtleCode,
            Species = turtle.Species,
            Nickname = turtle.Nickname
        };
    }
}
