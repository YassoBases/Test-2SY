<template>
  <section
    v-if="visible"
    class="reflection glass-card pa-5 pa-md-6 mb-5"
    :class="`reflection--${outcomeTone}`"
    role="region"
    tabindex="-1"
    data-spk-focus="reflection"
    :aria-labelledby="headingId"
  >
    <div class="d-flex align-center gap-2 mb-3">
      <v-icon :color="outcomeTone === 'retry' ? 'warning' : 'success'" aria-hidden="true">
        {{ outcomeTone === 'retry' ? 'mdi-reload' : 'mdi-check-decagram-outline' }}
      </v-icon>
      <h2 :id="headingId" class="text-h6 font-weight-bold mb-0">
        {{ title }}
      </h2>
    </div>

    <p v-if="summary" class="text-body-1 mb-4">{{ summary }}</p>

    <v-row dense>
      <v-col v-if="improvingSkills.length" cols="12" md="6">
        <div class="text-caption text-medium-emphasis mb-2">
          {{ t('student.languages.speakingJourney.reflection.improved') }}
        </div>
        <ul class="ref-list">
          <li v-for="(s, i) in improvingSkills.slice(0, 4)" :key="`imp-${i}`">
            <strong>{{ s.label }}</strong>
            <span v-if="s.improvement_focus" class="text-medium-emphasis"> — {{ s.improvement_focus }}</span>
          </li>
        </ul>
      </v-col>
      <v-col v-if="practiceSkills.length" cols="12" md="6">
        <div class="text-caption text-medium-emphasis mb-2">
          {{ t('student.languages.speakingJourney.reflection.needsPractice') }}
        </div>
        <ul class="ref-list">
          <li v-for="(s, i) in practiceSkills.slice(0, 4)" :key="`prac-${i}`">
            <strong>{{ s.label }}</strong>
            <span v-if="s.improvement_focus" class="text-medium-emphasis"> — {{ s.improvement_focus }}</span>
          </li>
        </ul>
      </v-col>
      <v-col v-if="transferNeeded.length" cols="12" md="6">
        <div class="text-caption text-medium-emphasis mb-2">
          {{ t('student.languages.speakingJourney.reflection.transfer') }}
        </div>
        <ul class="ref-list">
          <li v-for="(s, i) in transferNeeded.slice(0, 3)" :key="`tr-${i}`">
            <strong>{{ s.label }}</strong>
          </li>
        </ul>
      </v-col>
    </v-row>

    <div v-if="alexSummary" class="alex-summary rounded-lg pa-4 mt-4">
      <div class="text-caption text-medium-emphasis mb-1">
        {{ t('student.languages.speakingJourney.reflection.alexUsage') }}
      </div>
      <div class="text-body-2">{{ alexSummary }}</div>
    </div>

    <div v-if="nextMission" class="next-box rounded-lg pa-4 mt-4">
      <div class="text-caption text-medium-emphasis mb-1">
        {{ t('student.languages.speakingJourney.reflection.nextLesson') }}
      </div>
      <div class="text-body-1 font-weight-medium">{{ nextMission.title }}</div>
      <div class="text-body-2 text-medium-emphasis">{{ nextMission.purpose }}</div>
      <v-chip
        v-if="nextMission.is_task_bearing"
        size="x-small"
        class="mt-2"
        variant="tonal"
        color="secondary"
      >
        {{ t('student.languages.speakingJourney.path.taskBearing') }}
      </v-chip>
    </div>

    <v-alert
      v-if="nextActionCopy || promotionReminder"
      class="mt-4"
      type="info"
      variant="tonal"
      density="comfortable"
    >
      {{ nextActionCopy || promotionReminder }}
    </v-alert>

    <v-chip
      v-if="sessionOutcome?.retry_same_target"
      class="mt-4"
      size="small"
      color="warning"
      variant="tonal"
    >
      {{ t('student.languages.speakingJourney.reflection.retryHint') }}
    </v-chip>

    <div class="d-flex flex-wrap gap-2 mt-5">
      <v-btn
        color="primary"
        class="em-btn em-btn--primary spk-pressable"
        :loading="starting"
        prepend-icon="mdi-play"
        :aria-label="t('student.languages.speakingJourney.actions.startSession')"
        @click="$emit('start-session')"
      >
        {{ t('student.languages.speakingJourney.actions.startSession') }}
      </v-btn>
      <v-btn
        v-if="spaUnlocked"
        variant="tonal"
        class="spk-pressable"
        prepend-icon="mdi-trophy-outline"
        :aria-label="t('student.languages.speakingJourney.actions.viewAssessment')"
        @click="$emit('go-assessment')"
      >
        {{ t('student.languages.speakingJourney.actions.viewAssessment') }}
      </v-btn>
      <v-btn
        variant="text"
        class="spk-pressable"
        prepend-icon="mdi-close"
        :aria-label="t('student.languages.speakingJourney.reflection.dismiss')"
        @click="$emit('dismiss')"
      >
        {{ t('student.languages.speakingJourney.reflection.dismiss') }}
      </v-btn>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  sessionOutcome: { type: Object, default: null },
  improvingSkills: { type: Array, default: () => [] },
  weakSkills: { type: Array, default: () => [] },
  retentionNeeded: { type: Array, default: () => [] },
  transferNeeded: { type: Array, default: () => [] },
  nextMission: { type: Object, default: null },
  alexRemainingSeconds: { type: Number, default: null },
  spaUnlocked: { type: Boolean, default: false },
  promotionReadiness: { type: Object, default: null },
  starting: { type: Boolean, default: false },
})

defineEmits(['start-session', 'go-assessment', 'dismiss'])

const { t } = useI18n()
const headingId = 'speaking-reflection-heading'

const visible = computed(
  () => Boolean(props.sessionOutcome?.student_summary) || Boolean(props.sessionOutcome?.outcome_kind),
)
const summary = computed(() => props.sessionOutcome?.student_summary || '')
const practiceSkills = computed(() => {
  if (props.weakSkills?.length) return props.weakSkills
  return props.retentionNeeded || []
})

const outcomeKind = computed(() => String(props.sessionOutcome?.outcome_kind || '').toLowerCase())
const outcomeTone = computed(() =>
  outcomeKind.value.includes('retry') || props.sessionOutcome?.retry_same_target ? 'retry' : 'complete',
)

const title = computed(() => {
  if (outcomeTone.value === 'retry') {
    return t('student.languages.speakingJourney.reflection.titleRetry')
  }
  return t('student.languages.speakingJourney.reflection.titleComplete')
})

const alexSummary = computed(() => {
  const remaining = props.alexRemainingSeconds
  if (remaining == null || typeof remaining !== 'number') {
    return t('student.languages.speakingJourney.reflection.alexUnknown')
  }
  const mins = Math.floor(remaining / 60)
  const secs = remaining % 60
  return t('student.languages.speakingJourney.reflection.alexRemaining', {
    minutes: mins,
    seconds: secs,
  })
})

const nextActionCopy = computed(() => {
  const action = props.promotionReadiness?.next_action
  return typeof action === 'string' && action.trim() ? action.trim() : ''
})

const promotionReminder = computed(() => {
  if (nextActionCopy.value) return ''
  if (props.spaUnlocked) {
    return t('student.languages.speakingJourney.reflection.promoUnlocked')
  }
  const msg = props.promotionReadiness?.message
  if (msg) return msg
  return ''
})
</script>

<style scoped>
.reflection {
  border-radius: var(--em-radius-md, 16px);
  border-inline-start: 4px solid rgb(var(--v-theme-success));
}
.reflection--retry {
  border-inline-start-color: rgb(var(--v-theme-warning));
}
.ref-list {
  margin: 0;
  padding-inline-start: 1.1rem;
}
.next-box,
.alex-summary {
  background: rgba(var(--v-theme-on-surface), 0.04);
  border: 1px solid rgba(var(--v-theme-on-surface), 0.06);
}
</style>
