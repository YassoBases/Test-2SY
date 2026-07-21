import { api } from './client.js'

export function fetchActiveLiveBridge() {
  return api.get('/student/languages/speaking/live-bridge/active').then((r) => r.data)
}

export function prepareSpeakingLiveBridge({ packageId } = {}) {
  return api
    .post('/student/languages/speaking/live-bridge/prepare', {
      package_id: packageId || null,
    })
    .then((r) => r.data)
}

export function startSpeakingRehearsal({ packageId } = {}) {
  return api
    .post('/student/languages/speaking/live-bridge/rehearsal/start', {
      package_id: packageId || null,
    })
    .then((r) => r.data)
}

export function submitSpeakingRehearsalTurn(studentText) {
  return api
    .post('/student/languages/speaking/live-bridge/rehearsal/turn', {
      student_text: studentText,
    })
    .then((r) => r.data)
}

export function completeSpeakingRehearsal() {
  return api
    .post('/student/languages/speaking/live-bridge/rehearsal/complete')
    .then((r) => r.data)
}

/** M12 voice turn — server owns dialogue; client only sends audio. */
export function respondSpeakingRehearsal(audioBlob, { filename = 'scene_turn.webm' } = {}) {
  const form = new FormData()
  form.append('audio', audioBlob, filename)
  return api
    .post('/student/languages/speaking/live-bridge/rehearsal/respond', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 180000,
    })
    .then((r) => r.data)
}
