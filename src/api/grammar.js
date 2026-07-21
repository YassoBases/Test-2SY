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

/** Wave D - server-attested completion. Client must not send grammar_id/score. */
export async function completeGrammarActivity(payload = {}) {
  const { data } = await api.post('/student/grammar/activity/complete', payload)
  return data
}
