import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'main_site/static/react',
    rollupOptions: {
      // Each key becomes its own bundle: main.js stays the homepage's,
      // indicators.js is the new one for the dashboard page.
      // Add another line here any time you want a new React-powered page.
      input: {
        main: 'src/main.jsx',
        indicators: 'src/indicators.jsx',
      },
      output: {
        // '[name].js' means the key above becomes the filename directly -
        // 'main' -> main.js (unchanged), 'indicators' -> indicators.js
        entryFileNames: '[name].js',
        chunkFileNames: 'assets/[name].js',
        assetFileNames: 'assets/[name].[ext]'
      }
    }
  }
})