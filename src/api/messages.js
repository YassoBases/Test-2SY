import { api } from './client.js'

export async function fetchConversations(includeArchived = false) {
  const { data } = await api.get('/messages/conversations', {
    params: { include_archived: includeArchived },
  })
  return data
}

export async function fetchConversationsUnreadCount() {
  const { data } = await api.get('/messages/conversations/unread-count')
  return data
}

export async function fetchConversation(threadId, markRead = true) {
  const { data } = await api.get(`/messages/conversations/${threadId}`, {
    params: { mark_read: markRead },
  })
  return data
}

export async function fetchConversationContext(threadId) {
  const { data } = await api.get(`/messages/conversations/${threadId}/context`)
  return data
}

export async function searchConversationMessages(threadId, q) {
  const { data } = await api.get(`/messages/conversations/${threadId}/messages/search`, {
    params: { q },
  })
  return data
}

export async function updateConversationSettings(threadId, settings) {
  const { data } = await api.patch(`/messages/conversations/${threadId}/settings`, settings)
  return data
}

export async function markConversationUnread(threadId) {
  const { data } = await api.post(`/messages/conversations/${threadId}/mark-unread`)
  return data
}

export async function updateConversationParticipants(threadId, payload) {
  const { data } = await api.patch(`/messages/conversations/${threadId}/participants`, payload)
  return data
}

export async function createConversation(payload) {
  const { data } = await api.post('/messages/conversations', payload)
  return data
}

export async function fetchMessagingContacts() {
  const { data } = await api.get('/messages/contacts')
  return data
}

export async function sendConversationMessage(threadId, body) {
  const { data } = await api.post(`/messages/conversations/${threadId}/messages`, { body })
  return data
}

export async function sendConversationAttachment(threadId, file, { caption = '', voiceDurationMs = null } = {}) {
  const form = new FormData()
  form.append('file', file)
  form.append('caption', caption)
  if (voiceDurationMs != null) form.append('voice_duration_ms', String(voiceDurationMs))
  const { data } = await api.post(`/messages/conversations/${threadId}/messages/attachment`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export async function deleteConversationMessage(messageId) {
  const { data } = await api.delete(`/messages/messages/${messageId}`)
  return data
}

export async function markConversationRead(threadId) {
  const { data } = await api.post(`/messages/conversations/${threadId}/read`)
  return data
}

export async function markMessageRead(messageId) {
  const { data } = await api.post(`/messages/messages/${messageId}/read`)
  return data
}
