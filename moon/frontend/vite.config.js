import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    allowedHosts: ['bbangjik.kakaolab.cloud'],  // ✅ 외부 도메인 허용
    port: 5173,
  },
})
