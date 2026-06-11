import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

// window.* global mimari: dosyalar entry.jsx'te sırayla side-effect import edilir.
// Klasik JSX transform (React.createElement) — dosyalar `React` globaline bağımlı,
// her modüle otomatik import enjekte edilir (kod değişikliği gerekmez).
export default defineConfig({
  plugins: [react({ jsxRuntime: 'classic' })],
  esbuild: { jsxInject: "import React from 'react'" },
  server: { port: 5173 },
  build: { outDir: 'dist' },
});
