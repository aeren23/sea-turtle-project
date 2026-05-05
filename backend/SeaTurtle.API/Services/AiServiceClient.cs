using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;
using SeaTurtle.API.Models.DTOs.AiService;

namespace SeaTurtle.API.Services;

public class AiServiceClient : IAiServiceClient
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<AiServiceClient> _logger;

    public AiServiceClient(HttpClient httpClient, IConfiguration config, ILogger<AiServiceClient> logger)
    {
        _httpClient = httpClient;
        _logger = logger;
        _httpClient.BaseAddress = new Uri(config["AiService:BaseUrl"] ?? "http://localhost:8000");
    }

    public async Task<AiIdentifyResult> IdentifyAsync(Stream photoStream, string fileName)
    {
        try
        {
            using var content = new MultipartFormDataContent();
            var streamContent = new StreamContent(photoStream);
            streamContent.Headers.ContentType = new MediaTypeHeaderValue("image/jpeg"); // or determine based on extension
            content.Add(streamContent, "file", fileName);

            var response = await _httpClient.PostAsync("/api/v1/identify", content);
            
            if (!response.IsSuccessStatusCode)
            {
                var errorContent = await response.Content.ReadAsStringAsync();
                _logger.LogError("Identify API failed with status {Status}: {Error}", response.StatusCode, errorContent);
                return new AiIdentifyResult { Success = false, Error = "AI service identification failed." };
            }

            var resultStr = await response.Content.ReadAsStringAsync();
            _logger.LogInformation("RAW AI RESPONSE: {Result}", resultStr);

            using var doc = JsonDocument.Parse(resultStr);
            var root = doc.RootElement;

            bool success = root.TryGetProperty("success", out var successElement) && successElement.GetBoolean();
            if (!success)
            {
                return new AiIdentifyResult { Success = false, Error = "AI returned success=false" };
            }

            var identification = root.TryGetProperty("identification", out var identObj) && identObj.ValueKind != JsonValueKind.Null ? identObj : (JsonElement?)null;
            var detection = root.TryGetProperty("detection", out var detObj) && detObj.ValueKind != JsonValueKind.Null ? detObj : (JsonElement?)null;

            bool isKnown = identification?.TryGetProperty("is_known", out var ik) == true && ik.GetBoolean();
            string? turtleId = identification?.TryGetProperty("turtle_id", out var tid) == true && tid.ValueKind != JsonValueKind.Null ? tid.GetString() : null;
            float bestScore = identification?.TryGetProperty("best_score", out var bs) == true && bs.ValueKind != JsonValueKind.Null ? (float)bs.GetDouble() : 0f;
            
            string biologicalSide = "unknown";
            if (identification?.TryGetProperty("biological_side", out var ibs) == true && ibs.ValueKind != JsonValueKind.Null)
            {
                biologicalSide = ibs.GetString() ?? "unknown";
            }
            else if (detection?.TryGetProperty("biological_side", out var dbs) == true && dbs.ValueKind != JsonValueKind.Null)
            {
                biologicalSide = dbs.GetString() ?? "unknown";
            }

            string? sessionId = root.TryGetProperty("session_id", out var sid) && sid.ValueKind != JsonValueKind.Null ? sid.GetString() : null;
            string? savedPhotoPath = root.TryGetProperty("saved_photo_path", out var spp) && spp.ValueKind != JsonValueKind.Null ? spp.GetString() : null;
            bool galleryUpdated = root.TryGetProperty("gallery_updated", out var gu) && gu.ValueKind != JsonValueKind.Null && gu.GetBoolean();

            return new AiIdentifyResult
            {
                Success = true,
                IsKnown = isKnown,
                TurtleId = turtleId,
                BestScore = bestScore,
                BiologicalSide = biologicalSide,
                SessionId = sessionId,
                SavedPhotoPath = savedPhotoPath,
                GalleryUpdated = galleryUpdated
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Exception during identify API call.");
            return new AiIdentifyResult { Success = false, Error = "Communication error with AI service." };
        }
    }

    public async Task<AiRegisterResult> RegisterAsync(string sessionId)
    {
        try
        {
            var url = $"/api/v1/register?session_id={Uri.EscapeDataString(sessionId)}";
            var response = await _httpClient.PostAsync(url, null); // Empty POST

            if (!response.IsSuccessStatusCode)
            {
                var errorContent = await response.Content.ReadAsStringAsync();
                _logger.LogError("Register API failed with status {Status}: {Error}", response.StatusCode, errorContent);
                return new AiRegisterResult { Success = false, Error = "AI service registration failed." };
            }

            var resultStr = await response.Content.ReadAsStringAsync();
            var options = new JsonSerializerOptions { PropertyNameCaseInsensitive = true };
            var result = JsonSerializer.Deserialize<AiRegisterResponse>(resultStr, options);

            if (result == null || result.status != "success")
            {
                return new AiRegisterResult { Success = false, Error = "Failed to parse AI service response." };
            }

            return new AiRegisterResult
            {
                Success = true,
                TurtleId = result.turtle_id
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Exception during register API call.");
            return new AiRegisterResult { Success = false, Error = "Communication error with AI service." };
        }
    }

    public async Task<bool> HealthCheckAsync()
    {
        try
        {
            var response = await _httpClient.GetAsync("/health");
            return response.IsSuccessStatusCode;
        }
        catch
        {
            return false;
        }
    }

    // Private classes to deserialize JSON properties with underscores
    public class AiIdentifyResponse
    {
        public bool success { get; set; }
        public IdentificationObj? identification { get; set; }
        public DetectionObj? detection { get; set; }
        public string? session_id { get; set; }
        public string? saved_photo_path { get; set; }
        public bool gallery_updated { get; set; }
        public string? error { get; set; }
        
        public class IdentificationObj
        {
            public bool is_known { get; set; }
            public string? turtle_id { get; set; }
            public float best_score { get; set; }
            public string? biological_side { get; set; }
        }

        public class DetectionObj
        {
            public string? biological_side { get; set; }
        }
    }

    public class AiRegisterResponse
    {
        public string? status { get; set; }
        public string? turtle_id { get; set; }
    }
}
