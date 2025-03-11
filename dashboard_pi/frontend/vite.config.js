import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
    server: {
    host: true, // Allow access from any network
    strictPort: true, // Ensure Vite doesn't pick random ports
    port: 5173, // Default Vite port, change if needed
    allowedHosts: ["waafiadam-pi.local"], // Allow this hostname
  },
});
