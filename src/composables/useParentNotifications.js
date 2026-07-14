import { ref } from 'vue'
import {
  fetchParentNotifications,
  fetchParentNotificationSettings,
  markParentNotificationRead,
  updateParentNotificationSettings,
} from '../api/parent.js'
import { getErrorMessage } from '../api/client.js'
import { resolveParentStudentId } from '../utils/parentStorage.js'
import { isApiMode } from '../utils/session.js'

export function useParentNotifications(selectedStudentId) {
  const loading = ref(false)
  const settingsLoading = ref(false)
  const loadError = ref('')
  const settingsError = ref('')
  const items = ref([])
  const unreadCount = ref(0)
  const settings = ref(null)
  const savingSettings = ref(false)
  let loadSeq = 0

  async function loadNotifications() {
    const studentId = resolveParentStudentId(selectedStudentId)
    if (studentId == null) {
      loadSeq += 1
      items.value = []
      unreadCount.value = 0
      loadError.value = ''
      loading.value = false
      return
    }
    if (!isApiMode()) return

    const seq = ++loadSeq
    loading.value = true
    loadError.value = ''
    try {
      const data = await fetchParentNotifications(studentId)
      if (seq !== loadSeq) return
      items.value = data.items || []
      unreadCount.value = data.unread_count || 0
    } catch (err) {
      if (seq !== loadSeq) return
      loadError.value = getErrorMessage(err, 'تعذر تحميل الإشعارات')
    } finally {
      if (seq === loadSeq) loading.value = false
    }
  }

  async function loadSettings() {
    const studentId = resolveParentStudentId(selectedStudentId)
    if (studentId == null) {
      settings.value = null
      settingsError.value = ''
      settingsLoading.value = false
      return
    }
    if (!isApiMode()) return

    const seq = ++loadSeq
    settingsLoading.value = true
    settingsError.value = ''
    try {
      settings.value = await fetchParentNotificationSettings(studentId)
      if (seq !== loadSeq) return
    } catch (err) {
      if (seq !== loadSeq) return
      settingsError.value = getErrorMessage(err, 'تعذر تحميل إعدادات التنبيهات')
    } finally {
      if (seq === loadSeq) settingsLoading.value = false
    }
  }

  async function markRead(notificationId) {
    const studentId = resolveParentStudentId(selectedStudentId)
    if (studentId == null) return
    const updated = await markParentNotificationRead(notificationId, studentId)
    items.value = items.value.map((n) => (n.id === updated.id ? updated : n))
    unreadCount.value = items.value.filter((n) => !n.is_read).length
  }

  async function saveSettings(payload) {
    const studentId = resolveParentStudentId(selectedStudentId)
    if (studentId == null) return
    savingSettings.value = true
    settingsError.value = ''
    try {
      settings.value = await updateParentNotificationSettings(studentId, payload)
    } catch (err) {
      settingsError.value = getErrorMessage(err, 'تعذر حفظ الإعدادات')
      throw err
    } finally {
      savingSettings.value = false
    }
  }

  async function loadAll() {
    const studentId = resolveParentStudentId(selectedStudentId)
    if (studentId == null) {
      loadSeq += 1
      items.value = []
      unreadCount.value = 0
      settings.value = null
      loadError.value = ''
      settingsError.value = ''
      loading.value = false
      settingsLoading.value = false
      return
    }
    if (!isApiMode()) return

    const seq = ++loadSeq
    loading.value = true
    settingsLoading.value = true
    loadError.value = ''
    settingsError.value = ''
    await Promise.all([
      (async () => {
        try {
          const data = await fetchParentNotifications(studentId)
          if (seq !== loadSeq) return
          items.value = data.items || []
          unreadCount.value = data.unread_count || 0
        } catch (err) {
          if (seq !== loadSeq) return
          loadError.value = getErrorMessage(err, 'تعذر تحميل الإشعارات')
        } finally {
          if (seq === loadSeq) loading.value = false
        }
      })(),
      (async () => {
        try {
          settings.value = await fetchParentNotificationSettings(studentId)
          if (seq !== loadSeq) return
        } catch (err) {
          if (seq !== loadSeq) return
          settingsError.value = getErrorMessage(err, 'تعذر تحميل إعدادات التنبيهات')
        } finally {
          if (seq === loadSeq) settingsLoading.value = false
        }
      })(),
    ])
  }

  return {
    loading,
    settingsLoading,
    loadError,
    settingsError,
    items,
    unreadCount,
    settings,
    savingSettings,
    loadNotifications,
    loadSettings,
    loadAll,
    markRead,
    saveSettings,
  }
}

export const NOTIFICATION_CATEGORY_META = {
  login: { icon: 'mdi-login', color: 'info', label: 'دخول' },
  logout: { icon: 'mdi-logout', color: 'secondary', label: 'خروج' },
  lesson: { icon: 'mdi-book-check-outline', color: 'success', label: 'درس' },
  quiz: { icon: 'mdi-clipboard-check-outline', color: 'primary', label: 'اختبار' },
  low_score: { icon: 'mdi-alert-circle-outline', color: 'error', label: 'نتيجة منخفضة' },
  inactivity: { icon: 'mdi-sleep', color: 'warning', label: 'خمول' },
  planner: { icon: 'mdi-calendar-alert', color: 'warning', label: 'المخطط' },
  general: { icon: 'mdi-bell-outline', color: 'grey', label: 'عام' },
}

export function formatNotificationTime(iso) {
  if (!iso) return '—'
  try {
    return new Date(iso).toLocaleString('ar-SY', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
      day: 'numeric',
      month: 'short',
    })
  } catch {
    return iso
  }
}

export function notificationAlertType(category) {
  if (category === 'low_score') return 'error'
  if (category === 'inactivity' || category === 'planner') return 'warning'
  if (category === 'lesson' || category === 'quiz') return 'success'
  return 'info'
}
