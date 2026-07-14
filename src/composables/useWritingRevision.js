import { computed, ref } from 'vue'
import { submitWritingDraft } from '../api/language.js'
import { getErrorMessage } from '../api/client.js'

/**
 * W7 revision loop — draft submit + completion; render-only.
 */
export function useWritingRevision(getContentItemId) {
  const draftText = ref('')
  const submitting = ref(false)
  const error = ref('')
  const lastTurn = ref(null)

  const revisionNumber = computed(() => lastTurn.value?.revision_number ?? 0)
  const completed = computed(() => Boolean(lastTurn.value?.completed))
  const lifecycle = computed(() => lastTurn.value?.lifecycle || 'drafting')
  const comparison = computed(() => lastTurn.value?.comparison || null)
  const wordCount = computed(() => lastTurn.value?.word_count ?? 0)

  async function submitDraft({ completeIfReady = false } = {}) {
    const contentItemId = typeof getContentItemId === 'function' ? getContentItemId() : getContentItemId?.value
    if (!contentItemId) {
      error.value = 'No active lesson'
      return null
    }
    if (!draftText.value.trim()) {
      error.value = 'Draft text is required'
      return null
    }
    submitting.value = true
    error.value = ''
    try {
      lastTurn.value = await submitWritingDraft(contentItemId, {
        draft_text: draftText.value,
        complete_if_ready: completeIfReady,
      })
      return lastTurn.value
    } catch (err) {
      error.value = getErrorMessage(err, 'Could not submit draft')
      throw err
    } finally {
      submitting.value = false
    }
  }

  function resetRevision() {
    draftText.value = ''
    lastTurn.value = null
    error.value = ''
  }

  return {
    draftText,
    submitting,
    error,
    lastTurn,
    revisionNumber,
    completed,
    lifecycle,
    comparison,
    wordCount,
    submitDraft,
    resetRevision,
  }
}
