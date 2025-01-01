import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    exclude: ['lucide-react'],
  },
  build: {
    minify: 'esbuild', // Use esbuild for faster minification
    target: 'esnext', // Target modern browsers
    sourcemap: false, // Disable sourcemaps in production
  },
});
