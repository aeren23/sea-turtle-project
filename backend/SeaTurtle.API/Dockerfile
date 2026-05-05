FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src

# Copy csproj and restore as distinct layers
COPY ["backend/SeaTurtle.API/SeaTurtle.API.csproj", "backend/SeaTurtle.API/"]
RUN dotnet restore "backend/SeaTurtle.API/SeaTurtle.API.csproj"

# Copy everything else and build
COPY ["backend/", "backend/"]
WORKDIR "/src/backend/SeaTurtle.API"
RUN dotnet publish "SeaTurtle.API.csproj" -c Release -o /app/publish /p:UseAppHost=false

# Build runtime image
FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS final
WORKDIR /app
COPY --from=build /app/publish .

EXPOSE 8080

ENTRYPOINT ["dotnet", "SeaTurtle.API.dll"]
