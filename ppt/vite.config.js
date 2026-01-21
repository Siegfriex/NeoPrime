import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  root: '.',
  base: './',
  build: {
    outDir: 'dist',
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        neoprime: resolve(__dirname, 'neoprime/index.html'),
        designmate: resolve(__dirname, 'designmate/index.html'),
      },
    },
  },
  server: {
    port: 5173,
    open: true,
  },
});
