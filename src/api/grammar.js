import { api } from './client.js'

export async function fetchGrammarStatus() {
  const { data } = await api.get('/student/grammar/status')
  return data
}

export async function fetchGrammarDashboard() {
  const { data } = await api.get('/student/grammar/dashboard')
  return data
}

export async function startGrammarLesson(payload = {}) {
  const { data } = await api.post('/student/grammar/lesson/start', payload)
  return data
}

export async function fetchGrammarLessonPreview(revisionId) {
  const { data } = await api.get('/student/grammar/lesson/preview', {
    params: { revision_id: revisionId },
  })
  return data
}

export async function evaluateGrammarLessonPreviewPractice(payload) {
  const { data } = await api.post('/student/grammar/lesson/preview/practice/evaluate', payload)
  return data
}

export async function evaluateGrammarLessonPractice(payload) {
  const { data } = await api.post('/student/grammar/lesson/practice/evaluate', payload)
  return data
}

export async function createGrammarLessonPreviewChatSession(revisionId) {
  const { data } = await api.post('/student/grammar/lesson/preview/chat/sessions', {
    revision_id: revisionId,
  })
  return data
}

export async function createGrammarLessonChatSession(revisionId) {
  const { data } = await api.post('/student/grammar/lesson/chat/sessions', {
    revision_id: revisionId,
  })
  return data
}

export async function fetchGrammarLessonPreviewChatSession(sessionId, revisionId) {
  const { data } = await api.get(`/student/grammar/lesson/preview/chat/sessions/${encodeURIComponent(sessionId)}`, {
    params: { revision_id: revisionId },
  })
  return data
}

export async function fetchGrammarLessonChatSession(sessionId, revisionId) {
  const { data } = await api.get(`/student/grammar/lesson/chat/sessions/${encodeURIComponent(sessionId)}`, {
    params: { revision_id: revisionId },
  })
  return data
}

export async function sendGrammarLessonPreviewChatMessage(sessionId, payload) {
  const { data } = await api.post(
    `/student/grammar/lesson/preview/chat/sessions/${encodeURIComponent(sessionId)}/messages`,
    payload,
  )
  return data
}

export async function sendGrammarLessonChatMessage(sessionId, payload) {
  const { data } = await api.post(
    `/student/grammar/lesson/chat/sessions/${encodeURIComponent(sessionId)}/messages`,
    payload,
  )
  return data
}

export async function synthesizeGrammarLessonPreviewChatAudio(sessionId, messageId, payload = {}) {
  const { data } = await api.post(
    `/student/grammar/lesson/preview/chat/sessions/${encodeURIComponent(sessionId)}/messages/${encodeURIComponent(messageId)}/audio`,
    payload,
  )
  return data
}

export async function synthesizeGrammarLessonChatAudio(sessionId, messageId, payload = {}) {
  const { data } = await api.post(
    `/student/grammar/lesson/chat/sessions/${encodeURIComponent(sessionId)}/messages/${encodeURIComponent(messageId)}/audio`,
    payload,
  )
  return data
}

export async function closeGrammarLessonPreviewChatSession(sessionId, revisionId) {
  const { data } = await api.post(
    `/student/grammar/lesson/preview/chat/sessions/${encodeURIComponent(sessionId)}/close`,
    null,
    { params: { revision_id: revisionId } },
  )
  return data
}

export async function closeGrammarLessonChatSession(sessionId, revisionId) {
  const { data } = await api.post(
    `/student/grammar/lesson/chat/sessions/${encodeURIComponent(sessionId)}/close`,
    null,
    { params: { revision_id: revisionId } },
  )
  return data
}

/** Wave D - server-attested completion. Client must not send grammar_id/score. */
export async function completeGrammarActivity(payload = {}) {
  const { data } = await api.post('/student/grammar/activity/complete', payload)
  return data
}
