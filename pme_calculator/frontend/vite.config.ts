import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    emptyOutDir: true,
    rollupOptions: {
      output: {
        manualChunks: {
          // Vendor chunks
          vendor: ['react', 'react-dom'],
          charts: ['recharts'],
          icons: ['lucide-react'],
        },
      },
    },
    // Optimize chunk size
    chunkSizeWarningLimit: 300,
    // Enable source maps for production debugging
    sourcemap: true,
    // Minimize bundle size
    minify: 'esbuild',
    // Target modern browsers for smaller output
    target: 'esnext',
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: false,
    proxy: {
      '/api': {
        target: process.env.VITE_API_BASE || 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  // Optimize dependencies
  optimizeDeps: {
    include: ['react', 'react-dom', 'recharts', 'lucide-react'],
  },
  // Define environment variables that should be exposed to the client
  define: {
    'process.env.API_BASE': JSON.stringify(process.env.API_BASE || 'http://localhost:8000'),
  },
  // Environment variables configuration
  envPrefix: 'VITE_',
}) 