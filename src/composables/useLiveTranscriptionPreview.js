import { ref } from 'vue'

/**
 * Speaking's live transcript preview (MVP, display-only). Connects directly from the browser to
 * OpenAI's Realtime API over WebRTC using a short-lived ephemeral client secret minted by our own
 * backend (see api/language.js -> createSpeakingLiveTranscriptionSession). The backend's real
 * OPENAI_API_KEY never reaches this code.
 *
 * This is UX only: nothing here is ever submitted for grading. The official transcript remains
 * whatever the backend's own post-submit STT pipeline returns after Submit. Every failure path is
 * silent -- a missing/broken live preview must never block recording, submission, grading, or
 * section progression.
 *
 * start() must be called only after the student taps the recording button. Starting it earlier
 * opens the browser microphone and can capture room audio before the learner intentionally records.
 * Repeated calls are cheap: if a connection is active/unavailable they resolve immediately, and if
 * a connection is still in flight they return the same promise.
 */
export function useLiveTranscriptionPreview() {
  const transcript = ref('')
  const connecting = ref(false)
  const active = ref(false)
  // Sticky once true for this composable instance's lifetime segment between reset() calls --
  // avoids repeatedly retrying a clearly-unavailable/misconfigured feature within one turn.
  const unavailable = ref(false)

  let peerConnection = null
  let dataChannel = null
  let localStream = null
  // Keyed by "item_id:content_index" -- input_audio_transcription.delta events carry an
  // incremental text FRAGMENT for one segment of speech, never the full transcript so far, so
  // fragments must be accumulated per-segment and then joined across segments, not replaced.
  let itemText = new Map()
  // Segments whose .completed event has already arrived -- their text is now final. Realtime
  // can legitimately split one continuous utterance into multiple segments (e.g. across a brief
  // pause), each with its own item_id, so a segment being "completed" must not stop OTHER,
  // still-open segments from continuing to accumulate; it only freezes that one segment against
  // further (out-of-order/duplicate) deltas corrupting or duplicating its already-final text.
  let completedKeys = new Set()
  let currentAttempt = 0
  let inFlightPromise = null

  function updateTranscriptFromItems() {
    transcript.value = Array.from(itemText.values()).join(' ').trim()
  }

  function segmentKey(event) {
    const itemId = typeof event.item_id === 'string' && event.item_id ? event.item_id : 'default'
    const contentIndex = typeof event.content_index === 'number' ? event.content_index : 0
    return `${itemId}:${contentIndex}`
  }

  function handleServerEvent(raw) {
    let event
    try {
      event = JSON.parse(raw)
    } catch {
      return
    }
    if (!event || typeof event !== 'object') return
    if (event.type === 'conversation.item.input_audio_transcription.delta' && typeof event.delta === 'string') {
      const key = segmentKey(event)
      if (completedKeys.has(key)) return // this segment's completed transcript is already final
      itemText.set(key, (itemText.get(key) || '') + event.delta)
      updateTranscriptFromItems()
    } else if (
      event.type === 'conversation.item.input_audio_transcription.completed'
      && typeof event.transcript === 'string'
    ) {
      // The completed transcript is authoritative for this segment: it REPLACES whatever
      // partial deltas were accumulated (never appended alongside them), so the final text is
      // never duplicated.
      const key = segmentKey(event)
      itemText.set(key, event.transcript)
      completedKeys.add(key)
      updateTranscriptFromItems()
    }
  }

  async function stop() {
    currentAttempt += 1 // invalidate any in-flight start() so it discards its own late setup
    active.value = false
    connecting.value = false
    inFlightPromise = null
    try {
      dataChannel?.close()
    } catch { /* best-effort cleanup only */ }
    try {
      peerConnection?.close()
    } catch { /* best-effort cleanup only */ }
    try {
      localStream?.getTracks().forEach((track) => track.stop())
    } catch { /* best-effort cleanup only */ }
    dataChannel = null
    peerConnection = null
    localStream = null
  }

  function reset() {
    transcript.value = ''
    itemText = new Map()
    completedKeys = new Set()
    unavailable.value = false
  }

  function start(fetchSessionToken) {
    if (active.value || unavailable.value) return Promise.resolve()
    if (connecting.value && inFlightPromise) return inFlightPromise

    const myAttempt = ++currentAttempt
    connecting.value = true
    inFlightPromise = (async () => {
      try {
        if (typeof RTCPeerConnection === 'undefined' || !navigator.mediaDevices?.getUserMedia) {
          unavailable.value = true
          return
        }

        const session = await fetchSessionToken()
        if (myAttempt !== currentAttempt) return // superseded by a stop()/newer start() meanwhile
        if (!session?.available || !session?.client_secret) {
          unavailable.value = true
          return
        }

        const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
        if (myAttempt !== currentAttempt) {
          stream.getTracks().forEach((track) => track.stop())
          return
        }
        localStream = stream

        const pc = new RTCPeerConnection()
        localStream.getTracks().forEach((track) => pc.addTrack(track, localStream))
        const dc = pc.createDataChannel('oai-events')
        // The data channel is the exact path transcript deltas travel over, and it opens in
        // lockstep with the underlying ICE/DTLS transport that also carries the audio track --
        // waiting for it here (rather than declaring "active" the instant the SDP answer is
        // merely accepted) is what actually confirms audio can start being transcribed.
        const dataChannelReady = new Promise((resolve, reject) => {
          const cleanup = () => {
            dc.removeEventListener('open', onOpen)
            dc.removeEventListener('error', onError)
            pc.removeEventListener('connectionstatechange', onStateChange)
          }
          const onOpen = () => { cleanup(); resolve() }
          const onError = () => { cleanup(); reject(new Error('live transcription data channel error')) }
          const onStateChange = () => {
            if (pc.connectionState === 'failed' || pc.connectionState === 'closed') {
              cleanup()
              reject(new Error(`live transcription connection ${pc.connectionState}`))
            }
          }
          dc.addEventListener('open', onOpen)
          dc.addEventListener('error', onError)
          pc.addEventListener('connectionstatechange', onStateChange)
        })
        dc.addEventListener('message', (e) => {
          if (myAttempt === currentAttempt) handleServerEvent(e.data)
        })
        peerConnection = pc
        dataChannel = dc

        const offer = await pc.createOffer()
        await pc.setLocalDescription(offer)

        const response = await fetch('https://api.openai.com/v1/realtime/calls', {
          method: 'POST',
          body: offer.sdp,
          headers: {
            Authorization: `Bearer ${session.client_secret}`,
            'Content-Type': 'application/sdp',
          },
        })
        if (myAttempt !== currentAttempt) return
        if (!response.ok) {
          unavailable.value = true
          await stop()
          return
        }
        const answerSdp = await response.text()
        await pc.setRemoteDescription({ type: 'answer', sdp: answerSdp })
        if (myAttempt !== currentAttempt) return
        await dataChannelReady
        if (myAttempt !== currentAttempt) return
        active.value = true
      } catch {
        // Best-effort UX only -- never surface a live-caption failure as a user-facing error.
        unavailable.value = true
        await stop()
      } finally {
        if (myAttempt === currentAttempt) {
          connecting.value = false
          inFlightPromise = null
        }
      }
    })()

    return inFlightPromise
  }

  return { transcript, active, connecting, unavailable, start, stop, reset }
}
