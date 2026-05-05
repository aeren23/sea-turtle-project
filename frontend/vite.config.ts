import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Docker Compose: frontend container -> seaturtle-api:8080 (internal)
// Local dev:      browser -> localhost:5173 -> proxy -> localhost:5000
const API_TARGET = process.env.VITE_API_TARGET ?? 'http://localhost:5000';

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // required for Docker container binding
    port: 5173,
    proxy: {
      // All /api/* and /photos/* requests are forwarded to the .NET API
      '/api': {
        target: API_TARGET,
        changeOrigin: true,
        secure: false,
      },
      '/photos': {
        target: API_TARGET,
        changeOrigin: true,
        secure: false,
      },
    },
  },
});
