import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    build: {
        outDir: "../backend/static",
        emptyOutDir: true,
        sourcemap: true
    },
    server: {
        proxy: {
            '/chatgpt': "http://localhost:8000",
            '/api': "http://localhost:8000",
            '/login': "http://localhost:8000",
            '/getAToken': "http://localhost:8000",
            '/logout': "http://localhost:8000"
        },
        host: true
    }
});
