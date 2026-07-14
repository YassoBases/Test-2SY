import { api } from './client.js'

export async function fetchNotifications({ unreadOnly = false, limit = 50 } = {}) {
  const { data } = await api.get('/notifications', {
    params: { unread_only: unreadOnly, limit },
  })
  return data
}

export async function fetchUnreadCount() {
  const { data } = await api.get('/notifications/unread-count')
  return data.unread_count ?? 0
}

export async function markNotificationRead(id) {
  const { data } = await api.post(`/notifications/${id}/read`)
  return data
}

export async function markAllNotificationsRead() {
  const { data } = await api.post('/notifications/read-all')
  return data
}
