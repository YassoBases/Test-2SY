import { onMounted, onUnmounted, ref } from 'vue'
import {
  fetchNotifications,
  fetchUnreadCount,
  markAllNotificationsRead,
  markNotificationRead,
} from '../api/notifications.js'
import { isApiMode } from '../utils/session.js'

export function useNotifications() {
  const items = ref([])
  const unreadCount = ref(0)
  const loading = ref(false)
  let pollTimer = null

  async function refresh() {
    if (!isApiMode()) {
      items.value = []
      unreadCount.value = 0
      return
    }
    loading.value = true
    try {
      const [list, count] = await Promise.all([
        fetchNotifications({ limit: 30 }),
        fetchUnreadCount(),
      ])
      items.value = list.items ?? []
      unreadCount.value = count ?? list.unread_count ?? 0
    } catch {
      /* keep last known count */
    } finally {
      loading.value = false
    }
  }

  async function markRead(id) {
    if (!isApiMode()) return
    await markNotificationRead(id)
    const row = items.value.find((n) => n.id === id)
    if (row && !row.is_read) {
      row.is_read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    }
  }

  async function markAllRead() {
    if (!isApiMode()) return
    await markAllNotificationsRead()
    items.value.forEach((n) => {
      n.is_read = true
    })
    unreadCount.value = 0
  }

  function startPolling(intervalMs = 60000) {
    stopPolling()
    pollTimer = setInterval(refresh, intervalMs)
  }

  function stopPolling() {
    if (pollTimer) {
      clearInterval(pollTimer)
      pollTimer = null
    }
  }

  onMounted(() => {
    refresh()
    startPolling()
  })

  onUnmounted(stopPolling)

  return { items, unreadCount, loading, refresh, markRead, markAllRead }
}
