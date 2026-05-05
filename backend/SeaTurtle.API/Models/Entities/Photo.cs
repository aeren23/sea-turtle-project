namespace SeaTurtle.API.Models.Entities;

/// <summary>
/// Represents a turtle photo stored in the ai-core dataset directory.
/// FilePath points to the physical file managed by ai-service's PhotoStorageService.
/// </summary>
public class Photo
{
    public Guid Id { get; set; }

    /// <summary>The turtle this photo belongs to.</summary>
    public Guid TurtleId { get; set; }

    /// <summary>The encounter during which this photo was taken (nullable for seed data).</summary>
    public Guid? EncounterId { get; set; }

    /// <summary>
    /// Absolute path to the photo file on disk.
    /// Managed by ai-service's PhotoStorageService.
    /// Example: "C:\...\images\t042\20260505_a3f7b2.jpg"
    /// </summary>
    public string FilePath { get; set; } = string.Empty;

    /// <summary>Original filename as uploaded by the user.</summary>
    public string OriginalFileName { get; set; } = string.Empty;

    /// <summary>File size in bytes.</summary>
    public long FileSizeBytes { get; set; }

    /// <summary>MIME content type (e.g. "image/jpeg").</summary>
    public string ContentType { get; set; } = "image/jpeg";

    /// <summary>Biological side: left, right, or top.</summary>
    public string BiologicalSide { get; set; } = string.Empty;

    public DateTime UploadedAt { get; set; } = DateTime.UtcNow;

    // Navigation properties
    public Turtle Turtle { get; set; } = null!;
    public Encounter? Encounter { get; set; }
}
