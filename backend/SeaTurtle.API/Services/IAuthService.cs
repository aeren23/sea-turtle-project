using SeaTurtle.API.Models.DTOs.Auth;

namespace SeaTurtle.API.Services;

public interface IAuthService
{
    Task<AuthResponse?> LoginAsync(LoginRequest request);
    Task<AuthResponse> RegisterAsync(RegisterRequest request);
    Task<UserDto?> GetMeAsync(Guid userId);
}
