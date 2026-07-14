import { api } from './client.js'



const EVI_WS_BASE = 'wss://api.hume.ai/v0/evi/chat'



/**

 * Budget-gated live authorization (S13).

 * Optional leaseId resumes the same authoritative lease on reconnect.

 * Server returns remaining_seconds / session_allowed_seconds — never trust client duration.

 */

export async function fetchSpeakingLiveToken({ leaseId } = {}) {

  const body = leaseId ? { lease_id: leaseId } : {}

  const { data } = await api.post('/student/languages/speaking/live/token', body)

  return data

}



/** Liveness ping — server derives elapsed time; do NOT send duration. */

export async function submitLiveHeartbeat(leaseId) {

  const { data } = await api.post('/student/languages/speaking/live/heartbeat', {

    lease_id: leaseId,

  })

  return data

}



/** Intentional end — reconciles remaining server-elapsed time under the lease. */

export async function submitLiveEnd(leaseId) {

  const { data } = await api.post('/student/languages/speaking/live/end', {

    lease_id: leaseId,

  })

  return data

}



export async function submitSpeakingLiveTool({ toolName, toolCallId, parameters, speakingGoal }) {

  const { data } = await api.post('/student/languages/speaking/live/tool', {

    tool_name: toolName,

    tool_call_id: toolCallId,

    parameters: parameters || '{}',

    speaking_goal: speakingGoal || 'general_english',

  })

  return data

}



export async function submitSpeakingLiveTurn({

  blob,

  leaseId,

  liveSessionId,

  liveTurnId,

  eviEventsJson,

  providerTranscript,

}) {

  const form = new FormData()

  form.append('file', new File([blob], 'live-turn.wav', { type: blob.type || 'audio/wav' }))

  // S14: backend-authoritative identity — lease_id + backend-issued live_session_id.
  // The task prompt is NOT client-authoritative; the backend resolves it.

  form.append('lease_id', leaseId || '')

  form.append('live_session_id', liveSessionId)

  form.append('live_turn_id', liveTurnId)

  form.append('evi_events_json', eviEventsJson || '[]')

  if (providerTranscript) form.append('provider_transcript', providerTranscript)

  const { data } = await api.post('/student/languages/speaking/live/turn', form, {

    headers: { 'Content-Type': 'multipart/form-data' },

    timeout: 5 * 60 * 1000,

  })

  return data

}



export function buildEviWebSocketUrl({ accessToken, configId, verboseTranscription = false }) {

  const params = new URLSearchParams({ access_token: accessToken, config_id: configId })

  // Enables interim user_message events for progressive live student speech UI.

  if (verboseTranscription) params.set('verbose_transcription', 'true')

  return `${EVI_WS_BASE}?${params.toString()}`

}


