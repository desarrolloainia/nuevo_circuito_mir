import { fileURLToPath } from 'node:url'

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  modules: [
    '@nuxt/eslint',
    '@nuxt/ui',
    '@formkit/auto-animate/nuxt'
  ],

  devtools: {
    enabled: true
  },

  app: { head: { htmlAttrs: { lang: 'es' } } },

  css: ['@/app/assets/css/main.css'],

  colorMode: { preference: 'light' },

  runtimeConfig: {
    public: {
      apiBase: 'http://localhost:8000'
    }
  },

  dir: { pages: 'routes', layouts: 'layouts' },

  srcDir: 'src/app',

  alias: {
    '@': fileURLToPath(new URL('./src', import.meta.url))
  },

  routeRules: {
    '/': { redirect: '/login' }
  },

  compatibilityDate: '2026-06-30',

  eslint: {
    config: {
      stylistic: {
        commaDangle: 'never',
        braceStyle: '1tbs'
      }
    }
  }
})
