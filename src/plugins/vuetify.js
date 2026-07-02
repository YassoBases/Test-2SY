import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'
import { createVuetify } from 'vuetify'
import { ar, en } from 'vuetify/locale'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

const fieldBgNight = 'rgba(12, 18, 38, 0.94)'
const fieldBgMorning = 'rgba(255, 255, 255, 0.98)'

import { readInitialVuetifyTheme } from '../composables/useThemeMode.js'
import { isRtlLocale, readStoredLocale } from '../i18n/index.js'

function readInitialTheme() {
  return readInitialVuetifyTheme()
}

const isMorning = readInitialTheme() === 'edusparkMorning'
const fieldBg = isMorning ? fieldBgMorning : fieldBgNight
const initialLocale = readStoredLocale()

export default createVuetify({
  components,
  directives,
  locale: {
    locale: initialLocale,
    fallback: 'en',
    messages: { ar, en },
  },
  rtl: isRtlLocale(initialLocale),
  theme: {
    defaultTheme: readInitialTheme(),
    themes: {
      edusparkNight: {
        dark: true,
        colors: {
          primary: '#6366F1',
          secondary: '#22D3EE',
          accent: '#7C6CF0',
          success: '#34D399',
          warning: '#FBBF24',
          error: '#F87171',
          info: '#38BDF8',
          background: '#080C18',
          surface: '#0F1629',
          'on-background': '#E8ECF4',
          'on-surface': '#E8ECF4',
        },
      },
      edusparkMorning: {
        dark: false,
        colors: {
          primary: '#6366F1',
          secondary: '#06B6D4',
          accent: '#7C3AED',
          success: '#10B981',
          warning: '#F59E0B',
          error: '#EF4444',
          info: '#0284C7',
          background: '#F4F7FB',
          surface: '#FFFFFF',
          'on-background': '#0F172A',
          'on-surface': '#0F172A',
        },
      },
    },
  },
  defaults: {
    VBtn: { rounded: 'lg', elevation: 0 },
    VCard: { rounded: 'xl', elevation: 0, color: 'transparent' },
    VTextField: {
      variant: 'outlined',
      density: 'comfortable',
      color: 'primary',
      bgColor: fieldBg,
    },
    VSelect: {
      variant: 'outlined',
      density: 'comfortable',
      color: 'primary',
      bgColor: fieldBg,
    },
    VTextarea: {
      variant: 'outlined',
      density: 'comfortable',
      color: 'primary',
      bgColor: fieldBg,
    },
    VNavigationDrawer: { color: 'transparent' },
    VAppBar: { color: 'transparent', elevation: 0 },
    VDialog: { scrim: 'rgba(4, 8, 18, 0.82)' },
    VDataTable: { hover: true },
  },
})
