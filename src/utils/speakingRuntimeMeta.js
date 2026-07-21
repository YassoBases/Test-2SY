/**
 * Presentational helpers for Speaking runtime UX.
 * Maps authoritative backend kind/mode strings to icons and chrome only —
 * never invents educational state.
 */

const ACTIVITY_KIND_META = {
  warmup: { icon: 'mdi-weather-sunset', color: 'secondary', stage: 'observe' },
  target_intro: { icon: 'mdi-bullseye-arrow', color: 'primary', stage: 'observe' },
  guided_practice: { icon: 'mdi-hand-pointing-right', color: 'primary', stage: 'practice' },
  communicative_task: { icon: 'mdi-account-voice', color: 'secondary', stage: 'speak' },
  focused_retry: { icon: 'mdi-reload', color: 'warning', stage: 'practice' },
  remediation: { icon: 'mdi-lifebuoy', color: 'warning', stage: 'practice' },
  reflection: { icon: 'mdi-mirror', color: 'info', stage: 'reflect' },
}

const MISSION_KIND_META = {
  teaching: { icon: 'mdi-school-outline', color: 'primary' },
  noticing: { icon: 'mdi-eye-outline', color: 'info' },
  guided_practice: { icon: 'mdi-hand-pointing-right', color: 'primary' },
  speak: { icon: 'mdi-microphone', color: 'secondary' },
  feedback: { icon: 'mdi-comment-quote-outline', color: 'info' },
  transfer: { icon: 'mdi-swap-horizontal', color: 'secondary' },
  retention_review: { icon: 'mdi-brain', color: 'primary' },
}

const TEACHING_KIND_META = {
  explanation: { icon: 'mdi-school-outline', color: 'primary', group: 'concepts' },
  example: { icon: 'mdi-lightbulb-on-outline', color: 'secondary', group: 'examples' },
  noticing_cue: { icon: 'mdi-eye-outline', color: 'info', group: 'hints' },
  contrast: { icon: 'mdi-compare', color: 'warning', group: 'notes' },
  scaffold: { icon: 'mdi-strategy', color: 'primary', group: 'hints' },
  guided_prompt: { icon: 'mdi-comment-quote-outline', color: 'secondary', group: 'hints' },
  misconception_correction: { icon: 'mdi-alert-circle-outline', color: 'warning', group: 'notes' },
}

export function normalizeKind(kind) {
  return String(kind || '')
    .trim()
    .toLowerCase()
}

export function activityMeta(kind) {
  const k = normalizeKind(kind)
  return (
    ACTIVITY_KIND_META[k] || {
      icon: 'mdi-book-open-page-variant',
      color: 'primary',
      stage: 'observe',
    }
  )
}

export function missionKindMeta(kind) {
  const k = normalizeKind(kind)
  return MISSION_KIND_META[k] || { icon: 'mdi-flag-outline', color: 'primary' }
}

export function teachingKindMeta(kind) {
  const k = normalizeKind(kind)
  return (
    TEACHING_KIND_META[k] || {
      icon: 'mdi-book-open-page-variant',
      color: 'primary',
      group: 'notes',
    }
  )
}

/** Which primary surface the lesson focus should emphasize. */
export function primarySurfaceForActivity({
  activityKind = '',
  liveExecutionReady = false,
  hasTask = false,
  hasTeaching = false,
  controlledRequired = false,
} = {}) {
  if (liveExecutionReady) return 'speak'
  const meta = activityMeta(activityKind)
  const k = normalizeKind(activityKind)
  if (k.includes('guided') || controlledRequired || meta.stage === 'practice') return 'practice'
  if (k.includes('communicative') || meta.stage === 'speak' || hasTask) return 'speak'
  if (meta.stage === 'reflect') return 'reflect'
  if (hasTeaching || meta.stage === 'observe') return 'observe'
  return hasTask ? 'speak' : 'observe'
}

const INTERNAL_ERROR_CODES = new Set([
  'no_active_session',
  'live_budget_exhausted',
  'speaking_context_unavailable',
  'live_execution_not_ready',
  'ambiguous_active_attempt',
  'context_refresh_unavailable',
  'session_expired',
  'unauthorized',
  'forbidden',
])

/**
 * Map API/raw errors to student-safe copy.
 * Prefer explicit `kind` when callers provide one for i18n lookup.
 */
export function classifySpeakingError(raw) {
  const msg = String(raw || '').trim()
  const lower = msg.toLowerCase()
  if (!msg) return 'generic'
  if (/budget|remaining_seconds|daily.?limit/i.test(lower)) return 'alex_budget'
  if (/microphone|notallowederror|permission/i.test(lower)) return 'mic'
  if (/reconnect|connection lost|websocket|network/i.test(lower)) return 'reconnect'
  if (/expired|lease/i.test(lower)) return 'session_expired'
  if (/unavailable|not_ready|context/i.test(lower)) return 'alex_unavailable'
  if (INTERNAL_ERROR_CODES.has(lower)) return 'generic'
  if (/traceback|sqlalchemy|asyncpg|pydantic|filesystem|localhost:\d+/i.test(msg)) {
    return 'generic'
  }
  return 'message'
}

export function studentSafeJourneyError(raw, fallback) {
  const msg = String(raw || '').trim()
  if (!msg) return fallback
  const kind = classifySpeakingError(msg)
  if (kind !== 'message') return fallback
  return msg
}
