<template>
  <div class="speaking-promotion-result speaking-runtime">
    <LoadingState v-if="resultLoading && !result" variant="cards" :count="1" class="spk-skeleton-block" />

    <v-alert v-else-if="resultError" type="error" variant="tonal" class="mb-4 rounded-lg" role="alert">
      <div class="d-flex flex-wrap align-center justify-space-between gap-2">
        <span>{{ resultError }}</span>
        <v-btn size="small" variant="text" class="spk-pressable" @click="$emit('retry-load')">
          {{ t('student.languages.speakingJourney.runtime.retry') }}
        </v-btn>
      </div>
    </v-alert>

    <v-card v-else-if="result" class="glass-card pa-6 mb-4" variant="flat" :class="outcomeClass">
      <div class="text-overline text-medium-emphasis mb-1">
        {{ t('student.languages.speakingJourney.assessment.eyebrow') }}
      </div>
      <h2 class="text-h5 font-weight-bold mb-2">{{ title }}</h2>
      <p class="text-body-1 mb-4">{{ result.message || fallbackMessage }}</p>

      <!-- PASS -->
      <template v-if="isPass">
        <v-alert
          type="success"
          variant="tonal"
          class="mb-4 rounded-lg spk-pop"
          prepend-icon="mdi-party-popper"
        >
          {{ t('student.languages.speakingJourney.assessment.result.passBody') }}
        </v-alert>

        <template v-if="officialPromoted && promotionResult">
          <v-alert
            type="success"
            variant="tonal"
            class="mb-4 rounded-lg"
            prepend-icon="mdi-stairs-up"
          >
            {{
              t('student.languages.speakingJourney.assessment.result.promotedSummary', {
                old: promotionResult.old_cefr,
                next: promotionResult.new_cefr,
              })
            }}
          </v-alert>
          <p class="text-body-2 text-medium-emphasis mb-4">
            {{
              promotionResult.summary ||
              t('student.languages.speakingJourney.assessment.result.promotedBody')
            }}
          </p>
        </template>
        <template v-else>
          <v-alert
            type="info"
            variant="tonal"
            class="mb-4 rounded-lg"
            prepend-icon="mdi-shield-check-outline"
          >
            {{ t('student.languages.speakingJourney.assessment.result.officialPending') }}
          </v-alert>
          <v-alert
            v-if="promoteError"
            type="error"
            variant="tonal"
            class="mb-4 rounded-lg"
            role="alert"
          >
            {{ promoteError }}
          </v-alert>
        </template>
      </template>

      <!-- FAIL + bridge projection only -->
      <template v-else-if="isFail">
        <v-alert
          v-if="result.blocked_by_required_competency"
          type="warning"
          variant="tonal"
          class="mb-4 rounded-lg"
          prepend-icon="mdi-alert-circle-outline"
        >
          {{ t('student.languages.speakingJourney.assessment.result.blockedCompetency') }}
        </v-alert>

        <div v-if="bridge" class="bridge mb-4">
          <div class="text-subtitle-2 font-weight-bold mb-2">
            {{ t('student.languages.speakingJourney.assessment.result.bridgeTitle') }}
          </div>
          <p v-if="bridge.summary" class="text-body-2 mb-3">{{ bridge.summary }}</p>

          <div v-if="bridge.focus_labels?.length || bridge.focus_skill_ids?.length" class="mb-3">
            <div class="text-caption text-medium-emphasis mb-1">
              {{ t('student.languages.speakingJourney.assessment.result.focusSkills') }}
            </div>
            <div class="d-flex flex-wrap gap-2">
              <v-chip
                v-for="(label, i) in bridge.focus_labels?.length ? bridge.focus_labels : bridge.focus_skill_ids"
                :key="`${label}-${i}`"
                size="small"
                variant="tonal"
                color="secondary"
              >
                {{ label }}
              </v-chip>
            </div>
          </div>

          <ul v-if="bridge.suggested_practice?.length" class="practice-list">
            <li v-for="(item, i) in bridge.suggested_practice" :key="i">{{ item }}</li>
          </ul>
        </div>
      </template>

      <!-- ABANDONED / TIMEOUT / INCOMPLETE -->
      <template v-else>
        <v-alert
          :type="isTimeout ? 'warning' : 'info'"
          variant="tonal"
          class="mb-4 rounded-lg"
          :prepend-icon="isTimeout ? 'mdi-timer-off-outline' : 'mdi-information-outline'"
        >
          {{ softStateBody }}
        </v-alert>
      </template>

      <v-alert v-if="sessionError" type="error" variant="tonal" class="mb-4 rounded-lg" role="alert">
        {{ sessionError }}
      </v-alert>

      <div class="d-flex flex-wrap gap-2">
        <v-btn
          v-if="isPass && canPromote && !officialPromoted"
          color="success"
          class="em-btn em-btn--primary spk-pressable"
          prepend-icon="mdi-stairs-up"
          :loading="promoteLoading"
          @click="$emit('promote')"
        >
          {{ t('student.languages.speakingJourney.assessment.result.confirmPromotion') }}
        </v-btn>
        <v-btn
          v-if="canRetry"
          color="primary"
          class="em-btn em-btn--primary spk-pressable"
          prepend-icon="mdi-refresh"
          :loading="sessionLoading"
          @click="$emit('retry')"
        >
          {{ t('student.languages.speakingJourney.assessment.result.retry') }}
        </v-btn>
        <v-btn
          variant="tonal"
          class="spk-pressable"
          prepend-icon="mdi-map-marker-path"
          @click="$emit('back-to-journey')"
        >
          {{ t('student.languages.speakingJourney.runtime.backToJourney') }}
        </v-btn>
        <v-btn variant="text" class="spk-pressable" @click="$emit('back-home')">
          {{ t('student.languages.speakingJourney.assessment.result.backHome') }}
        </v-btn>
      </div>
    </v-card>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import LoadingState from '../common/LoadingState.vue'

const props = defineProps({
  result: { type: Object, default: null },
  resultLoading: { type: Boolean, default: false },
  resultError: { type: String, default: '' },
  sessionError: { type: String, default: '' },
  sessionLoading: { type: Boolean, default: false },
  canRetry: { type: Boolean, default: false },
  canPromote: { type: Boolean, default: false },
  promoteLoading: { type: Boolean, default: false },
  promoteError: { type: String, default: '' },
  promotionResult: { type: Object, default: null },
  officialPromoted: { type: Boolean, default: false },
})

defineEmits(['retry', 'retry-load', 'back-to-journey', 'back-home', 'promote'])

const { t } = useI18n()
const outcome = computed(() => String(props.result?.outcome || '').toUpperCase())
const isPass = computed(() => outcome.value === 'PASS')
const isFail = computed(() => outcome.value === 'FAIL')
const isTimeout = computed(() => outcome.value === 'TIMEOUT')
const bridge = computed(() => props.result?.bridge_recommendation || null)

const outcomeClass = computed(() => {
  if (isPass.value) return 'result--pass'
  if (isFail.value) return 'result--fail'
  return 'result--soft'
})

const title = computed(() => {
  const map = {
    PASS: 'passTitle',
    FAIL: 'failTitle',
    ABANDONED: 'abandonedTitle',
    TIMEOUT: 'timeoutTitle',
    INCOMPLETE: 'incompleteTitle',
  }
  const key = map[outcome.value] || 'fallbackTitle'
  return t(`student.languages.speakingJourney.assessment.result.${key}`)
})

const fallbackMessage = computed(() =>
  t('student.languages.speakingJourney.assessment.result.fallbackMessage'),
)

const softStateBody = computed(() => {
  if (outcome.value === 'ABANDONED') {
    return t('student.languages.speakingJourney.assessment.result.abandonedBody')
  }
  if (outcome.value === 'TIMEOUT') {
    return t('student.languages.speakingJourney.assessment.result.timeoutBody')
  }
  return t('student.languages.speakingJourney.assessment.result.incompleteBody')
})
</script>

<style scoped>
.result--pass {
  border-inline-start: 4px solid rgb(var(--v-theme-success));
}
.result--fail {
  border-inline-start: 4px solid rgb(var(--v-theme-warning));
}
.result--soft {
  border-inline-start: 4px solid rgba(var(--v-theme-on-surface), 0.25);
}
.practice-list {
  margin: 0;
  padding-inline-start: 1.25rem;
}
.practice-list li {
  margin-bottom: 0.35rem;
}
</style>
