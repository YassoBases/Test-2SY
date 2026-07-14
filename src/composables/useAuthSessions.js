import { ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  fetchAuthSessions,
  revokeAllAuthSessions,
  revokeAuthSession,
} from '../api/auth.js'
import { getErrorMessage } from '../api/client.js'
import { normalizeAuthSession } from '../utils/sessionDisplay.js'
import { getSession, clearSession, isApiMode } from '../utils/session.js'
import { ROUTES } from '../constants/app.js'
import { logoutApi } from '../api/auth.js'

export function useAuthSessions() {
  const router = useRouter()
  const sessions = ref([])
  const loading = ref(false)
  const actionId = ref(null)
  const revokingAll = ref(false)
  const error = ref('')

  async function loadSessions() {
    loading.value = true
    error.value = ''
    if (!isApiMode()) {
      sessions.value = []
      error.value = 'إدارة الجلسات متاحة عند الاتصال بالخادم (VITE_USE_MOCK=false)'
      loading.value = false
      return
    }
    try {
      const rows = await fetchAuthSessions()
      sessions.value = (Array.isArray(rows) ? rows : []).map(normalizeAuthSession)
    } catch (err) {
      error.value = getErrorMessage(err, 'تعذّر تحميل الجلسات النشطة')
      sessions.value = []
    } finally {
      loading.value = false
    }
  }

  async function finishLocalLogout() {
    clearSession()
    await router.push(ROUTES.LOGIN)
  }

  async function logoutCurrentDevice() {
    actionId.value = 'current'
    error.value = ''
    try {
      const session = getSession()
      await logoutApi(session?.refreshToken)
    } catch {
      /* session may already be revoked */
    } finally {
      actionId.value = null
      await finishLocalLogout()
    }
  }

  async function revokeSession(sessionId) {
    actionId.value = sessionId
    error.value = ''
    try {
      await revokeAuthSession(sessionId)
      await loadSessions()
    } catch (err) {
      error.value = getErrorMessage(err, 'تعذّر إنهاء الجلسة')
    } finally {
      actionId.value = null
    }
  }

  async function revokeAllDevices() {
    revokingAll.value = true
    error.value = ''
    try {
      await revokeAllAuthSessions()
      await finishLocalLogout()
    } catch (err) {
      error.value = getErrorMessage(err, 'تعذّر إنهاء جميع الجلسات')
    } finally {
      revokingAll.value = false
    }
  }

  return {
    sessions,
    loading,
    actionId,
    revokingAll,
    error,
    loadSessions,
    logoutCurrentDevice,
    revokeSession,
    revokeAllDevices,
  }
}
