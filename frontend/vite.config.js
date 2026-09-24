import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'apple-touch-icon.png'],
      manifest: {
        name: '积分奖励平台',
        short_name: '积分奖励',
        description: '家长管理积分、孩子完成任务奖励积分的积分奖励平台',
        theme_color: '#6366f1',
        background_color: '#f8fafc',
        display: 'standalone',
        orientation: 'any',
        icons: [
          {
            src: 'apple-touch-icon.png',
            sizes: '192x192',
            type: 'image/png',
          },
          {
            src: 'apple-touch-icon-512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'any maskable',
          },
        ],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
      },
    }),
  ],
  server: {
    host: '0.0.0.0',
    port: 7888,
    proxy: {
      '/api': {
        target: process.env.VITE_PROXY_TARGET || 'http://localhost:8000',
        changeOrigin: true,
      },
      '/uploads': {
        target: process.env.VITE_PROXY_TARGET || 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
