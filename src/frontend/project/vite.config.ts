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
    rollupOptions: {
      // Ensure environment variables are replaced at build time
      output: {
        manualChunks: undefined
      }
    }
  },
  define: {
    // Ensure these are replaced at build time
    'import.meta.env.VITE_API_URL': JSON.stringify(process.env.VITE_API_URL),
    'import.meta.env.VITE_ENV': JSON.stringify(process.env.VITE_ENV)
  }
});
