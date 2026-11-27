// Shourya/vite.config.ts - Vite bundler configuration bridging Shourya's ShadCN UI and Prakshat's Charts.
import path from "path"; // Node path helper for alias resolution
import { defineConfig } from "vite"; // Vite configuration factory
import react from "@vitejs/plugin-react"; // Official React Fast Refresh & JSX plugin

export default defineConfig({
  plugins: [react()], // Enable React JSX transformation
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"), // Map '@/' to Shourya/src for clean ShadCN imports
      "@prakshat": path.resolve(__dirname, "../Prakshat/charts"), // Map '@prakshat/' directly to Prakshat's chart modules
      react: path.resolve(__dirname, "./node_modules/react"), // Share single React instance with Prakshat's charts
      "react-dom": path.resolve(__dirname, "./node_modules/react-dom"), // Share ReactDOM instance
      "lightweight-charts": path.resolve(__dirname, "./node_modules/lightweight-charts"), // Resolve TradingView Lightweight Charts
      "lucide-react": path.resolve(__dirname, "./node_modules/lucide-react"), // Resolve Lucide icons for Prakshat's charts
    },
  },
  server: {
    fs: {
      allow: [path.resolve(__dirname, "..")], // Allow Vite dev server to import files from ../Prakshat/charts
    },
    proxy: {
      "/api": "http://127.0.0.1:8000", // Forward API calls to Naman's FastAPI backend during dev mode
    },
  },
  build: {
    outDir: "dist", // Emit static production bundle into Shourya/dist for FastAPI offline serving
    emptyOutDir: true, // Clean previous build artifacts before bundling
  },
});
