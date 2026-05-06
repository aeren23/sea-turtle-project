namespace SeaTurtle.API.Models.Settings;

/// <summary>
/// Strongly-typed configuration for file upload limits.
/// Eliminates the magic number 52428800 (50 MB) from Program.cs.
/// </summary>
public static class UploadSettings
{
    /// <summary>Maximum allowed photo upload size in bytes (50 MB).</summary>
    public const long MaxPhotoUploadBytes = 50 * 1024 * 1024;
}
