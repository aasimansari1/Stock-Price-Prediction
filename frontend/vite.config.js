import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Vite config — dev server on 5173, proxy API calls to FastAPI on 8000
// so the frontend can call `/get-stock-data` directly with no CORS dance.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/get-stock-data": "http://localhost:8000",
      "/predict": "http://localhost:8000",
    },
  },
});
