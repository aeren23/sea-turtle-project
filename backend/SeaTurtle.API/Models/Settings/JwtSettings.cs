namespace SeaTurtle.API.Models.Settings;

/// <summary>
/// Strongly-typed configuration for JWT authentication.
/// Bound from appsettings.json "Jwt" section via IOptions pattern.
/// Eliminates magic strings and centralises all JWT parameters.
/// </summary>
public class JwtSettings
{
    public const string SectionName = "Jwt";

    /// <summary>HMAC-SHA256 signing key. Must be ≥ 32 characters.</summary>
    public string Key { get; init; } = string.Empty;

    /// <summary>Token issuer claim (iss).</summary>
    public string Issuer { get; init; } = "SeaTurtleAPI";

    /// <summary>Token audience claim (aud).</summary>
    public string Audience { get; init; } = "SeaTurtleClient";

    /// <summary>Token lifetime in days.</summary>
    public int ExpirationDays { get; init; } = 7;
}
