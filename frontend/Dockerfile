# SeaTurtle Photo-ID — Frontend Docker Build
# Multi-stage: Node build → Nginx serve

# ---- Stage 1: Build ----
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies (cached layer — only re-runs when package*.json changes)
COPY package.json package-lock.json ./
RUN npm ci --silent

# Copy source and build
COPY . .

# VITE_API_TARGET is set to the internal Docker service name at build time.
# Vite proxy routes /api and /photos to this target.
ENV VITE_API_TARGET=http://seaturtle-api:8080

RUN npm run build

# ---- Stage 2: Serve ----
FROM nginx:1.27-alpine AS runtime

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Custom nginx config for SPA routing
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
