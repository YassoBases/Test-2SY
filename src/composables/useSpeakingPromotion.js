import { computed, ref } from 'vue'
import {
  createSpeakingPromotionAssessment,
  fetchSpeakingPromotionAssessment,
  fetchSpeakingPromotionStatus,
} from '../api/speakingPromotion.js'
import { getErrorMessage } from '../api/client.js'

/**
 * SPA preview only — no execution, scoring, or official promotion.
 */
export function useSpeakingPromotion() {
  const status = ref(null)
  const statusLoading = ref(false)
  const statusError = ref('')
  const blueprint = ref(null)
  const blueprintLoading = ref(false)
  const blueprintError = ref('')

  const available = computed(() => Boolean(status.value?.available))
  const spaUnlocked = computed(() => Boolean(status.value?.spa_unlocked))
  const message = computed(() => status.value?.message || '')
  const targetCefr = computed(() => status.value?.target_cefr || null)
  const sourceCefr = computed(() => status.value?.source_cefr || null)
  const estimatedDurationSeconds = computed(
    () => status.value?.estimated_duration_seconds || 0,
  )
  const tasks = computed(() => blueprint.value?.tasks || [])
  const hasInteractionGaps = computed(
    () =>
      Boolean(
        blueprint.value?.has_interaction_coverage_gaps ||
          status.value?.has_interaction_coverage_gaps,
      ),
  )

  async function loadStatus({ force = false } = {}) {
    if (!force && status.value && !statusError.value) return status.value
    statusLoading.value = true
    statusError.value = ''
    try {
      status.value = await fetchSpeakingPromotionStatus()
      if (status.value?.assessment_id && !blueprint.value) {
        try {
          blueprint.value = await fetchSpeakingPromotionAssessment(status.value.assessment_id)
        } catch {
          // Status can exist before preview fetch; ignore soft failure.
        }
      }
      return status.value
    } catch (err) {
      statusError.value = getErrorMessage(err, 'Unable to load speaking assessment status')
      throw err
    } finally {
      statusLoading.value = false
    }
  }

  async function previewAssessment() {
    blueprintLoading.value = true
    blueprintError.value = ''
    try {
      if (status.value?.assessment_id) {
        blueprint.value = await fetchSpeakingPromotionAssessment(status.value.assessment_id)
      } else {
        blueprint.value = await createSpeakingPromotionAssessment()
      }
      await loadStatus({ force: true })
      return blueprint.value
    } catch (err) {
      const detail = err?.response?.data?.detail
      const msg =
        (typeof detail === 'object' && detail?.message) ||
        (typeof detail === 'string' ? detail : null) ||
        getErrorMessage(err, 'Speaking assessment is temporarily unavailable')
      blueprintError.value = msg
      throw err
    } finally {
      blueprintLoading.value = false
    }
  }

  return {
    status,
    statusLoading,
    statusError,
    blueprint,
    blueprintLoading,
    blueprintError,
    available,
    spaUnlocked,
    message,
    targetCefr,
    sourceCefr,
    estimatedDurationSeconds,
    tasks,
    hasInteractionGaps,
    loadStatus,
    previewAssessment,
  }
}
