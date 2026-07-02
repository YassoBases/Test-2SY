import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import vuetify from 'vite-plugin-vuetify'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const apiTarget = (env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')

  return {
    plugins: [vue(), vuetify({ autoImport: true })],
    optimizeDeps: {
      include: ['vue', 'vue-router', 'vuetify'],
      // Avoid 504 Outdated Optimize Dep aborting lazy route imports during dev navigation.
      ignoreOutdatedRequests: true,
    },
    server: {
      host: true,
      port: 5173,
      warmup: {
        clientFiles: [
          './src/layouts/StudentLayout.vue',
          './src/views/student/StudentDashboardView.vue',
          './src/views/student/StudentCourseView.vue',
          './src/components/ui/AppCard.vue',
          './src/components/student/home/SubjectCatalogCard.vue',
        ],
      },
      proxy: {
        '/api': {
          target: apiTarget,
          changeOrigin: true,
          timeout: 300000,
          proxyTimeout: 300000,
        },
        '/uploads': {
          target: apiTarget,
          changeOrigin: true,
        },
      },
    },
  }
})
