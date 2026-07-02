import { computed, ref } from 'vue'

const STORAGE_KEY = 'eduspark-ui-theme'
const PREFERENCE_KEY = 'eduspark-theme-preference'

const preference = ref('dark')
const mode = ref('night')

let vuetifyThemeRef = null
let systemListenerBound = false

function getSystemMode() {
  if (typeof window === 'undefined') return 'night'
  return window.matchMedia('(prefers-color-scheme: light)').matches ? 'morning' : 'night'
}

function preferenceToMode(pref) {
  if (pref === 'light') return 'morning'
  if (pref === 'dark') return 'night'
  return getSystemMode()
}

function readPreference() {
  try {
    const saved = localStorage.getItem(PREFERENCE_KEY)
    if (saved === 'light' || saved === 'dark' || saved === 'system') return saved
    const legacy = localStorage.getItem(STORAGE_KEY)
    if (legacy === 'morning') return 'light'
    if (legacy === 'night') return 'dark'
  } catch {
    /* ignore */
  }
  return 'dark'
}

function bindSystemListener() {
  if (systemListenerBound || typeof window === 'undefined') return
  systemListenerBound = true
  window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', () => {
    if (preference.value === 'system') {
      applyThemeMode(getSystemMode())
    }
  })
}

export function applyThemeMode(next) {
  const value = next === 'morning' ? 'morning' : 'night'
  mode.value = value
  document.documentElement.setAttribute('data-theme', value)
  try {
    localStorage.setItem(STORAGE_KEY, value)
  } catch {
    /* ignore */
  }
  if (vuetifyThemeRef) {
    vuetifyThemeRef.global.name.value = value === 'morning' ? 'edusparkMorning' : 'edusparkNight'
  }
}

export function setThemePreference(next) {
  const value = next === 'light' || next === 'dark' || next === 'system' ? next : 'dark'
  preference.value = value
  try {
    localStorage.setItem(PREFERENCE_KEY, value)
  } catch {
    /* ignore */
  }
  applyThemeMode(preferenceToMode(value))
}

/** Call before Vue mount to avoid theme flash. */
export function initThemeMode() {
  preference.value = readPreference()
  applyThemeMode(preferenceToMode(preference.value))
  bindSystemListener()
}

export function bindVuetifyTheme(themeApi) {
  vuetifyThemeRef = themeApi
  applyThemeMode(mode.value)
}

export function readInitialVuetifyTheme() {
  return preferenceToMode(readPreference()) === 'morning' ? 'edusparkMorning' : 'edusparkNight'
}

export function useThemeMode() {
  const isMorning = computed(() => mode.value === 'morning')
  const isNight = computed(() => mode.value === 'night')

  function setMode(next) {
    setThemePreference(next === 'morning' ? 'light' : 'dark')
  }

  function toggle() {
    setThemePreference(isMorning.value ? 'dark' : 'light')
  }

  return {
    mode,
    preference,
    isMorning,
    isNight,
    setMode,
    setPreference: setThemePreference,
    toggle,
  }
}
