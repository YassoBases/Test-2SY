import { computed, onUnmounted, ref } from 'vue'
import {
  buildEviWebSocketUrl,
  fetchSpeakingLiveToken,
  submitLiveEnd,
  submitLiveHeartbeat,
  submitSpeakingLiveTool,
  submitSpeakingLiveTurn,
} from '../api/speakingLive.js'

const UI_STATES = [
  'idle',
  'requesting_microphone',
  'connecting',
  'alex_speaking',
  'student_speaking',
  'processing_turn',
  'ready',
  'reconnecting',
  'error',
  'ending',
  'ended',
]

export function useLiveConversation() {
  const state = ref('idle')
  const errorMessage = ref('')
  const errorKind = ref('')
  const liveSessionId = ref('')
  const liveTurnId = ref('')
  const eviEvents = ref([])
  const providerTranscript = ref('')
  const turnSummaries = ref([])
  const sessionEnded = ref(false)
  const processingTurn = ref(false)
  const personalizationFailed = ref(false)
  const transcriptMessages = ref([])
  /** Progressive interim student speech from EVI (verbose_transcription). Empty when none. */
  const currentStudentUtterance = ref('')
  const assistantSpeaking = ref(false)
  const micGranted = ref(false)
  const micMuted = ref(false)
  const reconnectAttempt = ref(0)
  // S13 — server-authoritative Talk with Alex daily budget (never trust client duration).
  const leaseId = ref('')
  const remainingSeconds = ref(null)
  const sessionAllowedSeconds = ref(null)
  const dailyLimitSeconds = ref(600)

  let ws = null
  let audioContext = null
  let mediaStream = null
  let processor = null
  let playbackContext = null
  let turnChunks = []
  let turnStartedAt = null
  let pendingHandoff = false
  let handoffInFlight = false
  let handoffTurnIds = new Set()
  let intentionalClose = false
  let tokenPayload = null
  let sessionTaskPrompt = 'Tell me about your day.'
  // S14 — backend-authoritative educational grounding for Alex (deterministic).
  let alexContext = null
  const contextFingerprint = ref('')
  let heartbeatTimer = null
  let deadlineTimer = null
  let heartbeatIntervalMs = 15_000
  let sessionStartedAtMs = 0
  let budgetEnding = false

  // --- Assistant (Alex) output playback ---
  // EVI streams each turn as many base64 WAV chunks, faster than realtime.
  // We keep an ordered raw-byte queue drained by a single sequential pump so
  // async decode completion order can never reorder speech chunks.
  let playbackByteQueue = []
  let scheduledSources = new Set()
  let nextPlaybackStartTime = 0
  let playbackEpoch = 0
  let isPumping = false
  let audioDiagCount = 0

  // --- Mic / input diagnostics (temporary; safe — no raw audio/secrets) ---
  let micDiagFrameCount = 0
  let micDiagSentCount = 0
  let micDiagLoggedFirstUserMessage = false
  let micDiagLastReportAt = 0
  const micDiagSeenEventTypes = new Set()
  // TEMPORARY safe signal stats (aggregate only, never raw audio/base64).
  let micDiagFramesInWindow = 0
  let micDiagSilentFramesInWindow = 0
  let micDiagLastRms = 0
  let micDiagLastPeak = 0
  let micDiagLastFrameBytes = 0

  const isActive = computed(() => !['idle', 'ended', 'error'].includes(state.value))
  const canStart = computed(() => state.value === 'idle' || state.value === 'ended' || state.value === 'error')
  const isListening = computed(() => state.value === 'ready' || state.value === 'student_speaking')
  const latestSummary = computed(() => turnSummaries.value[turnSummaries.value.length - 1] || null)
  const hasActiveSession = computed(() => isActive.value && state.value !== 'ending')
  /** Live surface should also remain visible on error (zombie/UI fix). */
  const showLiveSurface = computed(() => !['idle', 'ended'].includes(state.value))

  function _uuid(prefix) {
    return `${prefix}-${Math.random().toString(16).slice(2, 10)}`
  }

  function _mintTurnId() {
    liveTurnId.value = _uuid('turn')
    return liveTurnId.value
  }

  function _setState(next) {
    if (UI_STATES.includes(next)) state.value = next
  }

  function _micDiag(payload) {
    // eslint-disable-next-line no-console
    console.info('[Alex Mic Diagnostic]', {
      ...payload,
      state: state.value,
      sessionEnded: sessionEnded.value,
      micMuted: micMuted.value,
    })
  }

  // TEMPORARY read-only disconnect diagnostics. Ordered via `seq` so the real
  // failure sequence (hume_error -> ws_error -> ws_close -> reconnect) is
  // visible in the console. Logs only non-sensitive fields — never tokens,
  // keys, audio, base64, or raw WebSocket message bodies.
  let wsDiagSeq = 0
  function _wsDiag(payload) {
    // eslint-disable-next-line no-console
    console.info('[Alex WS Diagnostic]', {
      seq: (wsDiagSeq += 1),
      ...payload,
      uiState: state.value,
      reconnectAttempt: reconnectAttempt.value,
      sessionEnded: sessionEnded.value,
    })
  }

  // TEMPORARY safe outbound-send diagnostics. Shares wsDiagSeq so outbound
  // sends interleave with inbound/error/close logs in console order.
  // Never logs tokens, keys, config IDs, base64 audio, or raw message bodies.
  let outboundSendNum = 0
  let outboundAudioInputLogged = 0
  function _outboundDiag(payload) {
    // eslint-disable-next-line no-console
    console.info('[Alex Outbound Diagnostic]', {
      seq: (wsDiagSeq += 1),
      sendNum: (outboundSendNum += 1),
      ...payload,
      wsReadyState: ws?.readyState ?? -1,
      uiState: state.value,
    })
  }

  function _hex16(bytes) {
    return Array.from(bytes.slice(0, 16))
      .map((b) => b.toString(16).padStart(2, '0'))
      .join(' ')
  }

  function _clearCurrentStudentUtterance() {
    currentStudentUtterance.value = ''
  }

  function _assistantPlaybackIdle() {
    return playbackByteQueue.length === 0 && scheduledSources.size === 0 && !isPumping
  }

  function _maybeReturnToReady() {
    if (!_assistantPlaybackIdle()) return
    assistantSpeaking.value = false
    if (!processingTurn.value && !sessionEnded.value && state.value === 'alex_speaking') {
      _setState('ready')
    }
  }

  // Centralized cancellation: invalidates in-flight decode/pump work via the
  // epoch token, stops every scheduled source, and empties the queue so no
  // stale/late Alex audio can play after an interruption or teardown.
  function _clearAssistantPlayback() {
    playbackEpoch += 1
    playbackByteQueue = []
    nextPlaybackStartTime = 0
    scheduledSources.forEach((source) => {
      source.onended = null
      try {
        source.stop()
      } catch {
        /* already stopped */
      }
    })
    scheduledSources.clear()
    assistantSpeaking.value = false
  }

  function _closeWebSocket() {
    if (!ws) return
    try {
      ws.onclose = null
      ws.onmessage = null
      ws.onerror = null
      if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
        ws.close()
      }
    } catch {
      /* ignore */
    }
    ws = null
  }

  function _stopBudgetTimers() {
    if (heartbeatTimer) {
      clearInterval(heartbeatTimer)
      heartbeatTimer = null
    }
    if (deadlineTimer) {
      clearTimeout(deadlineTimer)
      deadlineTimer = null
    }
  }

  function _applyBudgetFields(payload) {
    if (!payload || typeof payload !== 'object') return
    if (payload.lease_id) leaseId.value = String(payload.lease_id)
    if (typeof payload.remaining_seconds === 'number') {
      remainingSeconds.value = payload.remaining_seconds
    }
    if (typeof payload.session_allowed_seconds === 'number') {
      sessionAllowedSeconds.value = payload.session_allowed_seconds
    }
    if (typeof payload.daily_limit_seconds === 'number') {
      dailyLimitSeconds.value = payload.daily_limit_seconds
    }
    if (typeof payload.heartbeat_interval_seconds === 'number' && payload.heartbeat_interval_seconds > 0) {
      heartbeatIntervalMs = Math.round(payload.heartbeat_interval_seconds * 1000)
    }
  }

  function _budgetErrorMessage(err) {
    const code = err?.response?.data?.detail?.code || err?.response?.data?.code || ''
    const serverMsg = err?.response?.data?.detail?.message || err?.response?.data?.message || ''
    if (code === 'daily_limit_reached') {
      return (
        serverMsg ||
        "You've used today's Talk with Alex time. More time will be available tomorrow."
      )
    }
    if (code === 'conversation_already_active') {
      return (
        serverMsg ||
        'You already have an active Talk with Alex conversation. Finish it in your other tab, or wait a moment and try again.'
      )
    }
    if (code === 'invalid_or_expired_live_lease' || code === 'live_lease_not_owned') {
      return serverMsg || 'This Talk with Alex session is no longer valid. Please start again.'
    }
    // S14 typed educational-context / live-identity failures — fail closed,
    // never silently continue as a generic Alex chat.
    if (code === 'speaking_context_unavailable' || code === 'live_execution_not_ready') {
      return (
        serverMsg ||
        "Your speaking lesson isn't ready yet. Start your lesson before talking with Alex."
      )
    }
    if (
      code === 'invalid_live_session' ||
      code === 'live_session_not_owned' ||
      code === 'live_task_mismatch' ||
      code === 'speaking_context_stale' ||
      code === 'ambiguous_active_attempt'
    ) {
      return serverMsg || 'Your speaking session needs to restart. Please start again.'
    }
    return ''
  }

  // Deterministic session-start grounding text injected into Hume EVI
  // session_settings.context BEFORE any audio, so Alex cannot begin as a
  // generic tutor without the current mission/task. Backend is authoritative.
  function _buildTutorContextText(ctx) {
    if (!ctx || typeof ctx !== 'object') return ''
    const lines = []
    lines.push('You are Alex, an English speaking tutor for this student.')
    if (ctx.official_cefr) lines.push(`Student official CEFR: ${ctx.official_cefr}.`)
    if (ctx.focus_title) lines.push(`Current learning focus: ${ctx.focus_title}.`)
    if (ctx.focus_reason) lines.push(ctx.focus_reason)
    if (ctx.current_mission) {
      lines.push(`Current mission: ${ctx.current_mission} — ${ctx.current_mission_purpose || ''}`.trim())
    }
    if (ctx.current_task_instruction) {
      lines.push(`Task to run now: ${ctx.current_task_instruction}`)
    }
    if (Array.isArray(ctx.learning_objectives) && ctx.learning_objectives.length) {
      lines.push(`Objectives: ${ctx.learning_objectives.join('; ')}.`)
    }
    if (Array.isArray(ctx.weak_skill_focuses) && ctx.weak_skill_focuses.length) {
      lines.push(`Gently reinforce: ${ctx.weak_skill_focuses.join(', ')}.`)
    }
    if (ctx.is_retry) lines.push('This is a retry — be encouraging and supportive.')
    const behaviors = []
    if (Array.isArray(ctx.tutor_behavior_contract)) behaviors.push(...ctx.tutor_behavior_contract)
    if (Array.isArray(ctx.mission_behavior)) behaviors.push(...ctx.mission_behavior)
    if (behaviors.length) lines.push(`How to teach now: ${behaviors.join(' ')}`)
    return lines.filter(Boolean).join('\n')
  }

  async function _sendHeartbeat() {
    if (!leaseId.value || sessionEnded.value || intentionalClose || budgetEnding) return
    try {
      const result = await submitLiveHeartbeat(leaseId.value)
      _applyBudgetFields(result)
      if (result?.deadline_reached || (typeof result?.remaining_seconds === 'number' && result.remaining_seconds <= 0)) {
        errorKind.value = 'daily_limit'
        errorMessage.value =
          "You've used today's Talk with Alex time. More time will be available tomorrow."
        await endLiveSession({ finalizePendingTurn: false, notifyServer: true, fromBudget: true })
      }
    } catch {
      /* Transient heartbeat failures are non-fatal; next tick retries. */
    }
  }

  function _startBudgetTimers() {
    _stopBudgetTimers()
    if (!leaseId.value) return
    heartbeatTimer = setInterval(() => {
      void _sendHeartbeat()
    }, heartbeatIntervalMs)

    const allowed = Number(sessionAllowedSeconds.value)
    if (Number.isFinite(allowed) && allowed > 0) {
      sessionStartedAtMs = Date.now()
      deadlineTimer = setTimeout(() => {
        if (sessionEnded.value || intentionalClose || budgetEnding) return
        errorKind.value = 'daily_limit'
        errorMessage.value =
          "You've used today's Talk with Alex time. More time will be available tomorrow."
        void endLiveSession({ finalizePendingTurn: false, notifyServer: true, fromBudget: true })
      }, Math.round(allowed * 1000))
    }
  }

  // Decode is async; a raw WAV byte queue is enqueued in EVI arrival order and
  // drained by exactly one sequential pump, so chunk order is always preserved.
  function _enqueueAssistantAudio(msg) {
    const b64 = msg?.data
    if (!b64 || sessionEnded.value) return
    const binary = atob(b64)
    const bytes = new Uint8Array(binary.length)
    for (let i = 0; i < binary.length; i += 1) bytes[i] = binary.charCodeAt(i)
    playbackByteQueue.push({ bytes, index: msg?.index })
    void _pumpAssistantPlayback()
  }

  function _scheduleAssistantBuffer(audioBuffer, item) {
    const ctx = playbackContext
    const prevNextStart = nextPlaybackStartTime
    const startAt = Math.max(ctx.currentTime, nextPlaybackStartTime)
    const source = ctx.createBufferSource()
    source.buffer = audioBuffer
    source.connect(ctx.destination)
    const epoch = playbackEpoch
    source.onended = () => {
      scheduledSources.delete(source)
      if (epoch === playbackEpoch) _maybeReturnToReady()
    }
    scheduledSources.add(source)
    source.start(startAt)
    nextPlaybackStartTime = startAt + audioBuffer.duration
    assistantSpeaking.value = true
    _setState('alex_speaking')

    if (audioDiagCount < 5) {
      audioDiagCount += 1
      const b = item.bytes
      const riff = b.length >= 4 && b[0] === 0x52 && b[1] === 0x49 && b[2] === 0x46 && b[3] === 0x46
      const wave = b.length >= 12 && b[8] === 0x57 && b[9] === 0x41 && b[10] === 0x56 && b[11] === 0x45
      // eslint-disable-next-line no-console
      console.info('[Alex Audio Diagnostic]', {
        index: item.index,
        byteLength: b.length,
        first16Hex: _hex16(b),
        riff,
        wave,
        sampleRate: audioBuffer.sampleRate,
        numberOfChannels: audioBuffer.numberOfChannels,
        duration: Number(audioBuffer.duration.toFixed(4)),
        startAt: Number(startAt.toFixed(4)),
        prevNextPlaybackStartTime: Number(prevNextStart.toFixed(4)),
      })
    }
  }

  async function _pumpAssistantPlayback() {
    if (isPumping) return
    if (!playbackContext) playbackContext = new AudioContext()
    if (playbackContext.state === 'suspended') {
      try {
        await playbackContext.resume()
      } catch {
        /* best effort */
      }
    }
    isPumping = true
    try {
      while (playbackByteQueue.length) {
        // Per-iteration epoch capture: a chunk decoded across a cancellation
        // boundary is discarded, but chunks enqueued for the new generation
        // are still drained by this same single pump (order preserved).
        const epoch = playbackEpoch
        const item = playbackByteQueue.shift()
        let audioBuffer
        try {
          audioBuffer = await playbackContext.decodeAudioData(item.bytes.buffer.slice(0))
        } catch (err) {
          // eslint-disable-next-line no-console
          console.warn('[Alex Audio Diagnostic] decodeAudioData failed; skipping chunk', {
            index: item?.index,
            error: err?.message || String(err),
          })
          continue
        }
        if (epoch !== playbackEpoch || sessionEnded.value) continue
        _scheduleAssistantBuffer(audioBuffer, item)
      }
    } finally {
      isPumping = false
      _maybeReturnToReady()
    }
  }

  function _appendTranscript(role, text) {
    const content = String(text || '').trim()
    if (!content) return
    transcriptMessages.value.push({
      id: _uuid('msg'),
      role,
      text: content,
      finalized: true,
    })
  }

  function _handleEviMessage(msg) {
    eviEvents.value.push(msg)
    const type = msg?.type
    // Log each event TYPE once (never payloads) to avoid audio_output spam.
    if (type && !micDiagSeenEventTypes.has(type)) {
      micDiagSeenEventTypes.add(type)
      _micDiag({ event: 'evi_event_type_first_seen', type: String(type) })
    }

    if (type === 'tool_call') {
      _handleToolCall(msg)
      return
    }

    // Interim student transcripts (only when verbose_transcription=true).
    if (type === 'user_message' && msg.interim) {
      const text = String(msg?.message?.content || '').trim()
      currentStudentUtterance.value = text
      // Hume: interim user messages help detect client-side interruption.
      _clearAssistantPlayback()
      if (!processingTurn.value && !sessionEnded.value) _setState('student_speaking')
      return
    }

    if (type === 'user_message' && !msg.interim) {
      // Student turn finalized: stop any late Alex audio and clear the queue
      // (EVI may not emit user_interruption if the user speaks after Alex
      // finished generating but before playback drained).
      _clearAssistantPlayback()
      const text = msg?.message?.content || providerTranscript.value
      providerTranscript.value = text
      _clearCurrentStudentUtterance()
      _appendTranscript('student', text)
      if (!micDiagLoggedFirstUserMessage) {
        micDiagLoggedFirstUserMessage = true
        _micDiag({
          event: 'first_user_message',
          hasTranscript: Boolean(String(text || '').trim()),
          transcriptLen: String(text || '').length,
          audioInputSentCount: micDiagSentCount,
          capturedFrameCount: micDiagFrameCount,
          wsReadyState: ws?.readyState ?? -1,
        })
      }
      _setState('processing_turn')
      void _handoffCompletedTurn()
      return
    }
    if (type === 'assistant_message' && !msg.interim) {
      _appendTranscript('alex', msg?.message?.content || msg?.content || '')
      return
    }
    if (type === 'audio_output') {
      _enqueueAssistantAudio(msg)
    }
    if (type === 'user_interruption') {
      _clearAssistantPlayback()
      _clearCurrentStudentUtterance()
      if (!processingTurn.value) _setState('ready')
    }
    if (type === 'assistant_end') {
      assistantSpeaking.value = false
      if (!processingTurn.value && state.value !== 'alex_speaking') _setState('ready')
    }
    if (type === 'error') {
      _wsDiag({
        event: 'hume_error',
        humeType: msg?.type,
        humeCode: msg?.code,
        humeSlug: msg?.slug,
        humeMessage: msg?.message,
      })
      errorMessage.value = 'Something went wrong with the conversation. Please try again.'
      errorKind.value = 'connection'
      _setState('error')
    }
  }

  async function _handleToolCall(msg) {
    const toolCallId = msg?.tool_call_id
    const toolName = msg?.name
    if (!toolCallId || !toolName) return
    try {
      const relay = await submitSpeakingLiveTool({
        toolName,
        toolCallId,
        parameters: typeof msg.parameters === 'string' ? msg.parameters : JSON.stringify(msg.parameters || {}),
      })
      if (ws?.readyState === WebSocket.OPEN) {
        const toolResponsePayload = {
          type: 'tool_response',
          tool_call_id: toolCallId,
          content: relay.content,
          tool_name: toolName,
          tool_type: 'function',
        }
        _outboundDiag({
          event: 'ws_send',
          type: toolResponsePayload.type,
          topLevelKeys: Object.keys(toolResponsePayload),
        })
        ws.send(JSON.stringify(toolResponsePayload))
      }
    } catch {
      if (ws?.readyState === WebSocket.OPEN) {
        // S14 fail-closed: do NOT instruct a generic conversation. Alex already
        // has deterministic session-start grounding; a failed refresh keeps the
        // existing educational context rather than degrading to generic chat.
        const toolErrorPayload = {
          type: 'tool_error',
          tool_call_id: toolCallId,
          error: 'context_refresh_unavailable',
          content: 'Keep following the current mission and task context already provided.',
          level: 'warn',
        }
        _outboundDiag({
          event: 'ws_send',
          type: toolErrorPayload.type,
          topLevelKeys: Object.keys(toolErrorPayload),
        })
        ws.send(JSON.stringify(toolErrorPayload))
      }
    }
  }

  function _startTurnCapture() {
    turnChunks = []
    turnStartedAt = Date.now()
    _setState('student_speaking')
  }

  function _appendTurnPcm(pcm) {
    turnChunks.push(new Uint8Array(pcm))
  }

  function _finalizeTurnWavBlob() {
    const pcm = new Uint8Array(turnChunks.reduce((n, c) => n + c.length, 0))
    let offset = 0
    turnChunks.forEach((c) => {
      pcm.set(c, offset)
      offset += c.length
    })
    const sampleRate = 16000
    const wavBuffer = new ArrayBuffer(44 + pcm.length)
    const view = new DataView(wavBuffer)
    const writeStr = (pos, str) => {
      for (let i = 0; i < str.length; i += 1) view.setUint8(pos + i, str.charCodeAt(i))
    }
    writeStr(0, 'RIFF')
    view.setUint32(4, 36 + pcm.length, true)
    writeStr(8, 'WAVE')
    writeStr(12, 'fmt ')
    view.setUint32(16, 16, true)
    view.setUint16(20, 1, true)
    view.setUint16(22, 1, true)
    view.setUint32(24, sampleRate, true)
    view.setUint32(28, sampleRate * 2, true)
    view.setUint16(32, 2, true)
    view.setUint16(34, 16, true)
    writeStr(36, 'data')
    view.setUint32(40, pcm.length, true)
    new Uint8Array(wavBuffer, 44).set(pcm)
    return new Blob([wavBuffer], { type: 'audio/wav' })
  }

  async function _ensureMicrophone() {
    _setState('requesting_microphone')
    _micDiag({ event: 'getUserMedia_about_to_call' })
    if (navigator.permissions?.query) {
      try {
        const status = await navigator.permissions.query({ name: 'microphone' })
        _micDiag({ event: 'permission_query', permission: status.state })
        if (status.state === 'denied') {
          errorKind.value = 'mic_denied'
          errorMessage.value = 'Microphone access is needed to talk with Alex.'
          _setState('error')
          return false
        }
      } catch {
        /* permissions API optional */
      }
    }
    try {
      mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true })
      micGranted.value = true
      micMuted.value = false
      const tracks = mediaStream.getAudioTracks()
      _micDiag({
        event: 'getUserMedia_ok',
        audioTrackCount: tracks.length,
        trackReadyState: tracks[0]?.readyState || '',
        trackEnabled: tracks[0]?.enabled ?? null,
      })
      return true
    } catch (err) {
      micGranted.value = false
      errorKind.value = err?.name === 'NotAllowedError' ? 'mic_denied' : 'mic_unavailable'
      errorMessage.value =
        errorKind.value === 'mic_denied'
          ? 'Microphone access is needed to talk with Alex.'
          : 'Your microphone is unavailable right now.'
      _micDiag({ event: 'getUserMedia_failed', errorName: err?.name || '' })
      _setState('error')
      return false
    }
  }

  async function _openWebSocket({ resumeLease = true } = {}) {
    // Reuse lease on reconnect; first start clears tokenPayload but keeps leaseId when resuming.
    if (!tokenPayload) {
      tokenPayload = await fetchSpeakingLiveToken({
        leaseId: resumeLease && leaseId.value ? leaseId.value : undefined,
      })
      _applyBudgetFields(tokenPayload)
      // S14: backend owns logical live conversation identity; frontend echoes it.
      if (tokenPayload.live_session_id) liveSessionId.value = String(tokenPayload.live_session_id)
      if (tokenPayload.alex_context) alexContext = tokenPayload.alex_context
      if (tokenPayload.context_fingerprint) contextFingerprint.value = String(tokenPayload.context_fingerprint)
    }
    outboundSendNum = 0
    outboundAudioInputLogged = 0
    const url = buildEviWebSocketUrl({
      accessToken: tokenPayload.access_token,
      configId: tokenPayload.config_id,
      // Enables interim user_message transcripts for progressive live UI.
      verboseTranscription: true,
    })
    ws = new WebSocket(url)
    _setState('connecting')
    await new Promise((resolve, reject) => {
      ws.onopen = () => {
        _micDiag({ event: 'ws_open', wsReadyState: ws.readyState })
        resolve()
      }
      ws.onerror = () => {
        _wsDiag({ event: 'ws_error' })
        reject(new Error('connect_failed'))
      }
      ws.onclose = (closeEvent) => {
        _wsDiag({
          event: 'ws_close',
          code: closeEvent?.code,
          reason: closeEvent?.reason || '',
          wasClean: closeEvent?.wasClean,
        })
        if (intentionalClose || sessionEnded.value) return
        if (state.value !== 'reconnecting' && state.value !== 'ending') {
          void _attemptReconnect()
        }
      }
    })
    ws.onmessage = (event) => {
      try {
        _handleEviMessage(JSON.parse(event.data))
      } catch {
        errorMessage.value = 'Something went wrong with the conversation. Please try again.'
        _setState('error')
      }
    }
    const sessionSettingsPayload = {
      type: 'session_settings',
      audio: { encoding: 'linear16', channels: 1, sample_rate: 16000 },
    }
    // S14 deterministic grounding: inject the authoritative educational context
    // into Hume EVI session_settings.context so Alex is grounded before speaking.
    const contextText = _buildTutorContextText(alexContext)
    if (contextText) {
      sessionSettingsPayload.context = { type: 'persistent', text: contextText }
    }
    _outboundDiag({
      event: 'ws_send',
      type: sessionSettingsPayload.type,
      topLevelKeys: Object.keys(sessionSettingsPayload),
      audioKeys: Object.keys(sessionSettingsPayload.audio),
      hasEducationalContext: Boolean(contextText),
    })
    ws.send(JSON.stringify(sessionSettingsPayload))
    // Heartbeat starts only after live authorization + WS open.
    _startBudgetTimers()
  }

  function _startAudioPipeline() {
    if (!mediaStream) {
      throw new Error('microphone_stream_missing')
    }
    try {
      audioContext = new AudioContext({ sampleRate: 16000 })
    } catch (err) {
      // Some browsers may reject an explicit sampleRate; fall back while keeping
      // the wire format declared as 16 kHz linear16 in session_settings.
      _micDiag({ event: 'audio_context_sampleRate_fallback', errorName: err?.name || '' })
      audioContext = new AudioContext()
    }
    if (audioContext.state === 'suspended') {
      void audioContext.resume()
    }
    const source = audioContext.createMediaStreamSource(mediaStream)
    processor = audioContext.createScriptProcessor(4096, 1, 1)
    micDiagFrameCount = 0
    micDiagSentCount = 0
    micDiagFramesInWindow = 0
    micDiagSilentFramesInWindow = 0
    micDiagLastRms = 0
    micDiagLastPeak = 0
    micDiagLastFrameBytes = 0
    micDiagLastReportAt = Date.now()
    _micDiag({
      event: 'audio_pipeline_started',
      micAudioContextState: audioContext.state,
      inputSampleRate: audioContext.sampleRate,
      declaredSampleRateToHume: 16000,
      sampleRateContractOk: audioContext.sampleRate === 16000,
      wsReadyState: ws?.readyState ?? -1,
    })
    processor.onaudioprocess = (e) => {
      if (sessionEnded.value || state.value === 'ending' || state.value === 'ended') return
      if (!['ready', 'student_speaking', 'alex_speaking', 'processing_turn'].includes(state.value)) return
      if (micMuted.value) return
      if (state.value === 'ready') _startTurnCapture()
      const input = e.inputBuffer.getChannelData(0)
      const pcm = new Int16Array(input.length)
      let sumSq = 0
      let peak = 0
      for (let i = 0; i < input.length; i += 1) {
        const v = input[i]
        sumSq += v * v
        const a = v < 0 ? -v : v
        if (a > peak) peak = a
        pcm[i] = Math.max(-32768, Math.min(32767, v * 32768))
      }
      _appendTurnPcm(pcm)
      micDiagFrameCount += 1
      // Aggregate signal stats only — no raw samples are ever logged/persisted.
      micDiagLastRms = input.length ? Math.sqrt(sumSq / input.length) : 0
      micDiagLastPeak = peak
      micDiagLastFrameBytes = pcm.byteLength
      micDiagFramesInWindow += 1
      if (micDiagLastRms < 0.0005) micDiagSilentFramesInWindow += 1
      if (ws?.readyState === WebSocket.OPEN) {
        const bytes = new Uint8Array(pcm.buffer)
        let binary = ''
        bytes.forEach((b) => {
          binary += String.fromCharCode(b)
        })
        // Log first 5 audio_input sends only so the session_settings → E0101
        // correlation stays visible; later frames are counted via mic heartbeat.
        if (outboundAudioInputLogged < 5) {
          outboundAudioInputLogged += 1
          _outboundDiag({
            event: 'ws_send',
            type: 'audio_input',
            topLevelKeys: ['type', 'data'],
            decodedByteLength: pcm.byteLength,
          })
        }
        ws.send(JSON.stringify({ type: 'audio_input', data: btoa(binary) }))
        micDiagSentCount += 1
      }
      const now = Date.now()
      if (now - micDiagLastReportAt >= 2000) {
        micDiagLastReportAt = now
        const tracks = mediaStream?.getAudioTracks() || []
        const windowFrames = micDiagFramesInWindow
        _micDiag({
          event: 'capture_heartbeat',
          capturedFrameCount: micDiagFrameCount,
          sentAudioInputCount: micDiagSentCount,
          micAudioContextState: audioContext?.state || '',
          inputSampleRate: audioContext?.sampleRate || 0,
          declaredSampleRateToHume: 16000,
          sampleRateContractOk: audioContext?.sampleRate === 16000,
          frameByteLength: micDiagLastFrameBytes,
          lastFrameRms: Number(micDiagLastRms.toFixed(5)),
          lastFramePeak: Number(micDiagLastPeak.toFixed(5)),
          silentFramePct: windowFrames ? Math.round((100 * micDiagSilentFramesInWindow) / windowFrames) : 0,
          trackReadyState: tracks[0]?.readyState || '',
          trackEnabled: tracks[0]?.enabled ?? null,
          trackMuted: tracks[0]?.muted ?? null,
          wsReadyState: ws?.readyState ?? -1,
        })
        micDiagFramesInWindow = 0
        micDiagSilentFramesInWindow = 0
      }
    }
    source.connect(processor)
    // Keep processor in the graph without audible mic feedback.
    const muteGain = audioContext.createGain()
    muteGain.gain.value = 0
    processor.connect(muteGain)
    muteGain.connect(audioContext.destination)
    _setState('ready')
  }

  function toggleMute() {
    if (!mediaStream) return
    micMuted.value = !micMuted.value
    mediaStream.getAudioTracks().forEach((track) => {
      track.enabled = !micMuted.value
    })
    _micDiag({
      event: 'mute_toggled',
      micMuted: micMuted.value,
      trackEnabled: mediaStream.getAudioTracks()[0]?.enabled ?? null,
    })
  }

  async function _handoffCompletedTurn() {
    if (handoffInFlight || !turnChunks.length) return null
    const turnId = _mintTurnId()
    if (handoffTurnIds.has(turnId)) return null
    handoffTurnIds.add(turnId)
    handoffInFlight = true
    processingTurn.value = true
    pendingHandoff = false
    const blob = _finalizeTurnWavBlob()
    const capturedEvents = [...eviEvents.value]
    turnChunks = []
    try {
      const payload = await submitSpeakingLiveTurn({
        blob,
        leaseId: leaseId.value,
        liveSessionId: liveSessionId.value,
        liveTurnId: turnId,
        eviEventsJson: JSON.stringify(capturedEvents),
        providerTranscript: providerTranscript.value,
      })
      if (payload?.student_session_summary) {
        turnSummaries.value.push(payload.student_session_summary)
      }
      if (payload?.success && payload?.mutation_status && payload.mutation_status !== 'applied') {
        personalizationFailed.value = true
      }
      providerTranscript.value = ''
      return payload
    } catch {
      errorKind.value = 'handoff_failed'
      errorMessage.value = 'We could not review your speaking just now. You can keep talking with Alex.'
      return null
    } finally {
      handoffInFlight = false
      processingTurn.value = false
      if (!sessionEnded.value && state.value !== 'alex_speaking') {
        _setState('ready')
      }
    }
  }

  async function _attemptReconnect() {
    if (intentionalClose || sessionEnded.value || reconnectAttempt.value >= 2) {
      _wsDiag({ event: 'reconnect_exhausted' })
      errorKind.value = 'connection'
      errorMessage.value = 'Connection lost. Please start a new conversation.'
      _setState('error')
      return
    }
    reconnectAttempt.value += 1
    _wsDiag({ event: 'reconnect_attempt' })
    _setState('reconnecting')
    // Never let audio from the dropped connection leak into the new socket.
    _clearAssistantPlayback()
    _clearCurrentStudentUtterance()
    try {
      // Reconnect must reuse the same lease (no budget reset).
      tokenPayload = null
      await _openWebSocket({ resumeLease: true })
      _setState('ready')
    } catch {
      await _attemptReconnect()
    }
  }

  async function startLiveSession({ taskPrompt, liveSessionId: externalLiveSessionId } = {}) {
    errorMessage.value = ''
    errorKind.value = ''
    sessionEnded.value = false
    intentionalClose = false
    budgetEnding = false
    reconnectAttempt.value = 0
    personalizationFailed.value = false
    handoffTurnIds = new Set()
    turnSummaries.value = []
    transcriptMessages.value = []
    eviEvents.value = []
    sessionTaskPrompt = taskPrompt || sessionTaskPrompt
    // Fresh connection: drop any prior assistant audio and reset diagnostics.
    _clearAssistantPlayback()
    _clearCurrentStudentUtterance()
    _stopBudgetTimers()
    audioDiagCount = 0
    micDiagFrameCount = 0
    micDiagSentCount = 0
    micDiagLoggedFirstUserMessage = false
    micDiagSeenEventTypes.clear()
    micMuted.value = false

    // S14: the backend issues the authoritative live_session_id at token time.
    // The frontend no longer mints logical live identity; it only echoes it.
    liveSessionId.value = ''
    void externalLiveSessionId
    _mintTurnId()
    // New conversation (not a WS reconnect): clear prior lease so authorize creates a fresh one.
    // Reconnect path keeps leaseId and reuses continuity on token mint.
    leaseId.value = ''
    remainingSeconds.value = null
    sessionAllowedSeconds.value = null
    tokenPayload = null

    const micOk = await _ensureMicrophone()
    if (!micOk) return false

    try {
      await _openWebSocket({ resumeLease: false })
      _startAudioPipeline()
      return true
    } catch (err) {
      const budgetMsg = _budgetErrorMessage(err)
      if (budgetMsg) {
        const code = err?.response?.data?.detail?.code || err?.response?.data?.code || ''
        if (code === 'daily_limit_reached') errorKind.value = 'daily_limit'
        else if (code === 'speaking_context_unavailable' || code === 'live_execution_not_ready') {
          errorKind.value = 'context_unavailable'
        } else if (
          code === 'invalid_live_session' ||
          code === 'live_session_not_owned' ||
          code === 'live_task_mismatch' ||
          code === 'speaking_context_stale' ||
          code === 'ambiguous_active_attempt'
        ) {
          errorKind.value = 'live_identity'
        } else errorKind.value = 'budget'
        errorMessage.value = budgetMsg
      } else {
        errorKind.value = 'connection'
        errorMessage.value = 'Could not connect to Alex. Please try again.'
      }
      _micDiag({ event: 'start_failed', errorName: err?.name || '', errorMessage: String(err?.message || '') })
      _setState('error')
      // Kill the zombie: close WS + stop playback + release mic.
      intentionalClose = true
      _stopBudgetTimers()
      await _cleanupMedia()
      return false
    }
  }

  async function endLiveSession({
    finalizePendingTurn = true,
    notifyServer = true,
    fromBudget = false,
  } = {}) {
    if (state.value === 'ended' || state.value === 'idle') return
    if (fromBudget) budgetEnding = true
    _setState('ending')
    sessionEnded.value = true
    intentionalClose = true
    _stopBudgetTimers()

    if (finalizePendingTurn && turnChunks.length && !handoffInFlight) {
      await _handoffCompletedTurn()
    }

    if (notifyServer && leaseId.value) {
      try {
        const ended = await submitLiveEnd(leaseId.value)
        _applyBudgetFields(ended)
      } catch {
        /* best effort — local teardown still proceeds */
      }
    }

    _clearAssistantPlayback()
    _clearCurrentStudentUtterance()
    await _cleanupMedia()
    leaseId.value = ''
    _setState('ended')
  }

  async function _cleanupMedia() {
    _stopBudgetTimers()
    _clearAssistantPlayback()
    _clearCurrentStudentUtterance()
    _closeWebSocket()
    if (processor) {
      try {
        processor.disconnect()
      } catch {
        /* ignore */
      }
      processor = null
    }
    if (audioContext) {
      try {
        await audioContext.close()
      } catch {
        /* ignore */
      }
      audioContext = null
    }
    if (mediaStream) {
      mediaStream.getTracks().forEach((t) => t.stop())
      mediaStream = null
    }
    if (playbackContext) {
      try {
        await playbackContext.close()
      } catch {
        /* ignore */
      }
      playbackContext = null
    }
    turnChunks = []
    micGranted.value = false
    micMuted.value = false
  }

  async function retryAfterError() {
    errorMessage.value = ''
    errorKind.value = ''
    _setState('idle')
    return startLiveSession({ taskPrompt: sessionTaskPrompt })
  }

  onUnmounted(() => {
    void endLiveSession({ finalizePendingTurn: false })
  })

  return {
    state,
    errorMessage,
    errorKind,
    liveSessionId,
    liveTurnId,
    leaseId,
    remainingSeconds,
    sessionAllowedSeconds,
    dailyLimitSeconds,
    contextFingerprint,
    eviEvents,
    providerTranscript,
    turnSummaries,
    latestSummary,
    sessionEnded,
    processingTurn,
    personalizationFailed,
    transcriptMessages,
    currentStudentUtterance,
    assistantSpeaking,
    micGranted,
    micMuted,
    isActive,
    canStart,
    isListening,
    hasActiveSession,
    showLiveSurface,
    startLiveSession,
    endLiveSession,
    retryAfterError,
    toggleMute,
  }
}
