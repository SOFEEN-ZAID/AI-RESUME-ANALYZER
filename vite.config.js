import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/analyze-text': 'http://localhost:8000',
      '/analyze-file': 'http://localhost:8000',
    },
  },
})
