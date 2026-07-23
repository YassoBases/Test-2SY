import { api } from './client.js'

export async function fetchTeacherStatus() {
  const { data } = await api.get('/student/teacher/status')
  return data
}

/** Start today's AI Teacher session (orchestration only — no random lesson). */
export async function startTeacherSession(params = {}) {
  const { data } = await api.post('/student/teacher/session/start', null, {
    params: {
      session_length_minutes: params.sessionLengthMinutes ?? 0,
      response_slow: params.responseSlow ?? false,
    },
  })
  return data
}
