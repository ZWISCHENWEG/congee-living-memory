import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import path from 'path';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  build: {
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            if (id.includes('react/') || id.includes('react-dom') || id.includes('react-router')) return 'react-vendor';
            if (id.includes('@tanstack/react-query') || id.includes('zustand') || id.includes('axios')) return 'state-vendor';
            if (id.includes('lucide-react') || id.includes('framer-motion') || id.includes('clsx') || id.includes('tailwind')) return 'ui-vendor';
            return 'vendor';
          }
        },
      },
    },
  },
  server: {
    proxy: {
      // The backend mounts routes at the root, so strip the "/api" dev prefix
      // before forwarding (e.g. /api/memories -> http://127.0.0.1:8000/memories).
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
});
