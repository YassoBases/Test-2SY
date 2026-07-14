import { ref } from 'vue'
import {
  fetchListeningLesson,
  fetchListeningNextSession,
  pollListeningAcquisition,
} from '../api/language.js'

const MAX_POLL_ATTEMPTS = 40

/**
 * Learning Session acquisition — explicit backend state, no HTTP error surfacing.
 * Reusable pattern for Reading / Speaking / Writing later.
 */
export function useListeningAcquisition() {
  const bundle = ref(null)
  const acquisition = ref(null)
  const phase = ref('idle') // idle | loading | ready | pending | unavailable
  const pollAttempt = ref(0)

  let pollTimer = null
  let pollGeneration = 0

  function stopPolling() {
    pollGeneration += 1
    if (pollTimer) {
      clearTimeout(pollTimer)
      pollTimer = null
    }
  }

  function reset() {
    stopPolling()
    bundle.value = null
    acquisition.value = null
    phase.value = 'idle'
    pollAttempt.value = 0
  }

  async function _handleResponse(data) {
    if (data?.outcome === 'lesson_ready' && data.bundle) {
      stopPolling()
      bundle.value = data.bundle
      acquisition.value = null
      phase.value = 'ready'
      return data.bundle
    }

    if (data?.outcome === 'acquisition_pending' && data.acquisition) {
      acquisition.value = data.acquisition
      const status = data.acquisition.status
      if (status === 'temporary_failure' || status === 'no_content') {
        phase.value = 'unavailable'
      } else {
        phase.value = 'pending'
      }
      return null
    }

    phase.value = 'unavailable'
    acquisition.value = {
      status: 'temporary_failure',
      message_key: 'student.languages.listeningJourney.acquisition.unavailable',
      temporary_failure: true,
      retry_after: 60,
      poll_after: 60,
    }
    return null
  }

  function schedulePoll(acq, attempt) {
    stopPolling()
    const generation = pollGeneration
    const delayMs = Math.max(2, (acq?.poll_after || 3)) * 1000

    pollTimer = setTimeout(async () => {
      if (generation !== pollGeneration) return
      if (pollAttempt.value >= MAX_POLL_ATTEMPTS) {
        phase.value = 'unavailable'
        acquisition.value = {
          ...acquisition.value,
          status: 'temporary_failure',
          temporary_failure: true,
          message_key: 'student.languages.listeningJourney.acquisition.unavailable',
          retry_after: 60,
        }
        return
      }
      pollAttempt.value += 1
      try {
        const data = await pollListeningAcquisition(attempt + pollAttempt.value)
        const result = await _handleResponse(data)
        if (result) return
        if (phase.value === 'pending' && acquisition.value) {
          schedulePoll(acquisition.value, attempt)
        }
      } catch {
        phase.value = 'unavailable'
        acquisition.value = {
          status: 'temporary_failure',
          temporary_failure: true,
          message_key: 'student.languages.listeningJourney.acquisition.offline',
          retry_after: 15,
          poll_after: 15,
        }
      }
    }, delayMs)
  }

  async function start({ resumeLessonId = null, attempt = 1 } = {}) {
    stopPolling()
    phase.value = 'loading'
    bundle.value = null
    acquisition.value = null
    pollAttempt.value = 0

    try {
      if (resumeLessonId) {
        const lesson = await fetchListeningLesson(resumeLessonId)
        bundle.value = lesson
        phase.value = 'ready'
        return lesson
      }

      const data = await fetchListeningNextSession(attempt)
      const result = await _handleResponse(data)
      if (result) return result

      if (phase.value === 'pending' && acquisition.value) {
        schedulePoll(acquisition.value, attempt)
      }
      return null
    } catch {
      phase.value = 'unavailable'
      acquisition.value = {
        status: 'temporary_failure',
        temporary_failure: true,
        message_key: 'student.languages.listeningJourney.acquisition.offline',
        retry_after: 15,
        poll_after: 15,
      }
      return null
    }
  }

  async function retry() {
    const wait = acquisition.value?.retry_after || 0
    if (wait > 0) {
      await new Promise((r) => setTimeout(r, Math.min(wait, 3) * 1000))
    }
    return start({ attempt: (acquisition.value?.attempt || 1) + pollAttempt.value + 1 })
  }

  return {
    bundle,
    acquisition,
    phase,
    pollAttempt,
    start,
    retry,
    reset,
    stopPolling,
  }
}
