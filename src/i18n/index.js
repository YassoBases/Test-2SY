import { createI18n } from 'vue-i18n'
import { buildMessages } from './loadMessages.js'

export const LOCALE_STORAGE_KEY = 'eduspark-locale'

export const SUPPORTED_LOCALES = ['ar', 'en']

export function readStoredLocale() {
  try {
    const stored = localStorage.getItem(LOCALE_STORAGE_KEY)
    if (SUPPORTED_LOCALES.includes(stored)) return stored
  } catch {
    /* ignore */
  }
  return 'ar'
}

export function isRtlLocale(locale) {
  return locale === 'ar'
}

export function applyDocumentLocale(locale) {
  const rtl = isRtlLocale(locale)
  document.documentElement.lang = locale
  document.documentElement.dir = rtl ? 'rtl' : 'ltr'
}

const initialLocale = readStoredLocale()
applyDocumentLocale(initialLocale)

export const i18n = createI18n({
  legacy: false,
  globalInjection: true,
  locale: initialLocale,
  fallbackLocale: 'en',
  messages: buildMessages(),
})

export function setAppLocale(locale) {
  if (!SUPPORTED_LOCALES.includes(locale)) return
  i18n.global.locale.value = locale
  try {
    localStorage.setItem(LOCALE_STORAGE_KEY, locale)
  } catch {
    /* ignore */
  }
  applyDocumentLocale(locale)
}

export function t(key, ...args) {
  return i18n.global.t(key, ...args)
}
