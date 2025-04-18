import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      // 代理API请求到后端FastAPI服务
      '/api': {
        target: 'http://127.0.0.1:8080',
        changeOrigin: true,
        secure: false
      },
      // 代理静态资源请求
      '/static': {
        target: 'http://127.0.0.1:8080',
        changeOrigin: true,
        secure: false
      }
    }
  },
  build: {
    // 设置输出目录为dist
    outDir: 'dist',
    // 生成sourcemap以便调试
    sourcemap: true
  }
})
