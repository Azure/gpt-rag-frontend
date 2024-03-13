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
            '/api/get-speech-token': "http://localhost:8000",
            '/api/get-storage-account': "http://localhost:8000",            
            '/api/get-blob': "http://localhost:8000"
        },
        host: true
    }
});
