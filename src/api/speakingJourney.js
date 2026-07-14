import { api } from './client.js'

export function fetchSpeakingJourney() {
  return api.get('/student/languages/speaking/journey').then((r) => r.data)
}

export function startSpeakingJourneySession({ liveSessionId } = {}) {
  return api
    .post('/student/languages/speaking/journey/session/start', {
      live_session_id: liveSessionId || '',
    })
    .then((r) => r.data)
}

export function completeSpeakingJourneyActivity(activityId) {
  return api
    .post('/student/languages/speaking/journey/session/activity/complete', {
      activity_id: activityId,
    })
    .then((r) => r.data)
}

/** Advance cursor to the first live-Alex task (backend-owned positioning). */
export function prepareSpeakingJourneyForLive() {
  return api.post('/student/languages/speaking/journey/session/prepare-live').then((r) => r.data)
}

export function recordSpeakingJourneyTurn(payload) {
  return api.post('/student/languages/speaking/journey/session/turn', payload).then((r) => r.data)
}

export function finalizeSpeakingJourneySession() {
  return api.post('/student/languages/speaking/journey/session/finalize').then((r) => r.data)
}
