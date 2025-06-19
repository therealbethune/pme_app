import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    watch: {
      usePolling: true,
      interval: 100,
    },
    hmr: {
      overlay: true,
    },
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
  build: {
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          charts: ['recharts', 'plotly.js-dist'],
          ui: ['@mui/material', '@emotion/react', '@emotion/styled'],
        },
      },
    },
  },
  optimizeDeps: {
    include: ['react', 'react-dom', 'recharts', '@mui/material'],
  },
})
