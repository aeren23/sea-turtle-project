# SeaTurtle Photo-ID: Project State & History

**Last Updated:** 2026-05-05 (Master Chronicle created)

This document tracks the high-level progress, completed milestones, and current active phase of the SeaTurtle Photo-ID project. It is intended to provide immediate context to any AI Agent joining the workspace.

## 🟡 Current Phase: Phase 4.0 — Web Platform (Frontend)
**Status:** 🚧 In Progress

All backend infrastructure is fully containerized. The React frontend is being implemented as Phase 4.0.
*   **Technology:** Vite + React 18 + TypeScript, Zustand, Axios, React Router v6, React Hook Form + Zod
*   **Design Theme:** "Bioluminescent Field Station" — Syne + JetBrains Mono fonts, ocean deep palette, animated sonar rings, confidence gauges
*   **API Coverage:** All 9 backend endpoints covered across 6 pages
*   **Docker:** `seaturtle-frontend` service (Nginx + React) on port 3000 added to docker-compose.yml
*   **Build Status:** ✅ TypeScript build passing — 0 errors, 215 modules

---

## ✅ Completed Phases

### Phase 3.5: Docker Compose Orchestration
**Status:** ✅ Completed (2026-05-05)
*   **Goal:** Single-command deployment of the entire backend stack.
*   **Services Orchestrated:**
    *   `seaturtle-db` — PostgreSQL 16 Alpine with named volume (`pgdata`) and healthcheck.
    *   `seaturtle-ai` — FastAPI AI microservice (YOLO + ResNet + FAISS) with Python 3.10-slim.
    *   `seaturtle-api` — .NET 10 Web API with JWT auth, Swagger, and EF Core.
*   **Bind Mounts:** `ai-core/` directory mounted into both AI and API containers to serve photos and seed the database without inflating Docker image sizes.
*   **Networking:** Containers communicate via Docker internal DNS (`seaturtle-ai:8000`, `seaturtle-db:5432`). Environment variables override `appsettings.json` for container-aware configuration.
*   **Dockerfiles Created:**
    *   `ai-service/Dockerfile` — Multi-step Python build with PyTorch, FAISS, OpenCV, Ultralytics.
    *   `backend/SeaTurtle.API/Dockerfile` — Multi-stage .NET 10 SDK build + ASP.NET runtime.
*   **Key Files:** `docker-compose.yml`, `.dockerignore`, `ai-service/Dockerfile`, `backend/SeaTurtle.API/Dockerfile`
*   **Healthchecks:** PostgreSQL uses `pg_isready`, AI service uses Python `urllib` (curl not available in slim image).
*   **JSON Integration Fix:** `AiServiceClient.cs` rewritten to use `JsonDocument` for direct JSON node parsing of FastAPI's nested response structure (`identification.is_known`, `identification.turtle_id`, etc.).
*   **Critical Issue Resolved:** Host-machine .NET debug process was binding `localhost:5000` and intercepting requests meant for the Docker container. Resolved by stopping the orphan process.

### Phase 3.0: Backend & Web Platform (.NET 10 API)
**Status:** ✅ Completed
*   **Infrastructure:** Docker Compose with PostgreSQL. Entity Framework Core used for ORM and migrations.
*   **Security:** JWT Authentication and Role-based authorization implemented.
*   **AI Integration:** `IAiServiceClient` added to bridge the .NET backend with the FastAPI microservice.
*   **CRUD & Business Logic:** Identification, Encounter, and Turtle services implemented.
*   **Database Seeding:** `DbSeeder` implemented to parse FAISS metadata JSONs and seed 438 turtles + photos automatically.
*   **Static Files:** `StaticFiles` middleware configured to serve photos directly from the AI dataset path.
*   **Swagger/OpenAPI:** `Swashbuckle.AspNetCore` (6.5.0) integrated with JWT Bearer authorization flow.

### Phase 2.6: Production Inference Pipeline & Microservice (FastAPI)
**Status:** ✅ Completed
*   **Microservice:** FastAPI wrapper (`ai-service/main.py`) handling `/identify` and `/register` endpoints.
*   **Photo Storage Strategy (v2):** 
    *   Known turtles saved to `images/tXXX/`.
    *   Unknown turtles stored in `images/_staging/` with a 10-minute session TTL.
*   **Autonomous Pipeline:** YOLOv8n head detector and orientation classifier integrated into an end-to-end inference flow without manual parameters.

### Phase 2.5: Embedding Gallery & FAISS Vector Store
**Status:** ✅ Completed
*   Extracted embeddings and built 3 separate FAISS `IndexFlatIP` indexes (left, right, top).
*   CLI tools built for gallery construction and query services.

### Phase 2.0: Deep Learning Implementation (Metric Learning)
**Status:** ✅ Completed
*   ResNet-50 backbone modified for metric learning with 512-d embeddings.
*   Trained using ArcFace Loss and Albumentations augmentations.
*   Best model saved to `checkpoints/best_turtle_resnet.pth`.

### Phase 1.0: Architecture Planning & Data Pipeline
**Status:** ✅ Completed
*   CrewAI agents analyzed the dataset.
*   OpenCV pipeline built for CLAHE, color correction, and resizing.
*   PyTorch Dataset implemented.

---

## 🐳 Docker Quick Start

```bash
# Boot the entire system (first run downloads ~2GB of dependencies)
docker compose up -d --build

# Verify all 3 services are healthy
docker compose ps

# Access points:
#   .NET API (Swagger): http://localhost:5000/swagger
#   FastAPI AI (Docs):   http://localhost:8000/docs
#   PostgreSQL:          localhost:5432
```

> **⚠️ Important:** Before running `docker compose up`, ensure no local .NET process is occupying port 5000. Use `netstat -ano | Select-String ":5000"` (Windows) to check.

---
**Note to AI Agents:** When undertaking new tasks, strictly adhere to the standards outlined in `docs/rules/coding_standards.md` and log your major decisions in `docs/project_log.md` using the Python `log_writer` utility.
