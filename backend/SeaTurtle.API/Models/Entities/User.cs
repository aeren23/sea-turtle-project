namespace SeaTurtle.API.Models.Entities;

/// <summary>
/// Represents a registered user (researcher or admin) in the system.
/// </summary>
public class User
{
    public Guid Id { get; set; }

    /// <summary>Unique email address used for authentication.</summary>
    public string Email { get; set; } = string.Empty;

    /// <summary>BCrypt-hashed password.</summary>
    public string PasswordHash { get; set; } = string.Empty;

    /// <summary>Full display name of the user.</summary>
    public string FullName { get; set; } = string.Empty;

    /// <summary>Authorization role (Researcher or Admin).</summary>
    public Enums.UserRole Role { get; set; } = Enums.UserRole.Researcher;

    /// <summary>Soft-disable flag for deactivated accounts.</summary>
    public bool IsActive { get; set; } = true;

    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    // Navigation properties
    public ICollection<Encounter> Encounters { get; set; } = new List<Encounter>();
}
