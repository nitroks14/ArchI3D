import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// base "/ArchI3D/" pour un deploiement GitHub Pages sur https://<user>.github.io/ArchI3D/
// (voir .github/workflows/frontend-deploy.yml). Adapter si le repo est renomme.
export default defineConfig({
  plugins: [react()],
  base: process.env.VITE_BASE_PATH ?? "/ArchI3D/",
  resolve: {
    alias: {
      "@": "/src",
    },
  },
});
