import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // 加载环境变量
  const env = loadEnv(mode, process.cwd())
  // 默认API端口，如果环境变量中设置了则使用环境变量
  const apiPort = env.VITE_API_PORT || '8080'

  return {
    plugins: [vue(), tailwindcss()],
    server: {
      proxy: {
        // 代理API请求到后端FastAPI服务
        '/api': {
          target: `http://127.0.0.1:${apiPort}`,
          changeOrigin: true,
          secure: false
        },
        // 代理静态资源请求
        '/static': {
          target: `http://127.0.0.1:${apiPort}`,
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
  }
})

