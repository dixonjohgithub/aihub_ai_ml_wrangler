/**
 * File: vite.config.ts
 * 
 * Overview:
 * Vite configuration for the React TypeScript frontend
 * 
 * Purpose:
 * Configure build tool, dev server, and React plugin setup
 * 
 * Dependencies:
 * - @vitejs/plugin-react
 * - vite
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  },
  resolve: {
    alias: {
      '@': '/src'
    }
  }
})