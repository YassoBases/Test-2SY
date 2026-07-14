import { api } from './client.js'

export async function fetchActivitySummary() {
  const { data } = await api.get('/student/activity/summary')
  return data
}

export async function fetchActivitySessions(limit = 30) {
  const { data } = await api.get('/student/activity/sessions', { params: { limit } })
  return data
}

export async function fetchActivityEvents(limit = 50, eventType = null) {
  const params = { limit }
  if (eventType) params.event_type = eventType
  const { data } = await api.get('/student/activity/events', { params })
  return data
}

/** Record a client-side engagement event (navigation, lesson viewed, quiz started, …). */
export async function recordActivityEvent(payload) {
  const { data } = await api.post('/student/activity/events', payload)
  return data
}

export async function fetchParentActivitySummary(studentId = null) {
  const params = studentId ? { student_id: studentId } : {}
  const { data } = await api.get('/parent/activity-tracking/summary', { params })
  return data
}

export async function fetchParentAttendanceAnalytics(studentId = null, { weekOffset = 0, monthOffset = 0, sessionLimit = 30 } = {}) {
  const params = { week_offset: weekOffset, month_offset: monthOffset, session_limit: sessionLimit }
  if (studentId) params.student_id = studentId
  const { data } = await api.get('/parent/activity-tracking/analytics', { params })
  return data
}
