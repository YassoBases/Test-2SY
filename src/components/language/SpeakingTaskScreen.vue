<template>
  <section
    v-if="show"
    class="task-screen glass-card pa-5 pa-md-6 mb-5"
    :class="{ 'task-screen--emphasis': emphasis || liveExecutionReady }"
    aria-labelledby="speaking-task-heading"
  >
    <div class="text-overline text-medium-emphasis mb-1">
      {{
        liveExecutionReady
          ? t('student.languages.speakingJourney.runtime.readyForAlex')
          : t('student.languages.speakingJourney.task.title')
      }}
    </div>
    <h3 id="speaking-task-heading" class="text-h6 font-weight-bold mb-2">
      {{ title }}
    </h3>

    <p v-if="missionPurpose" class="text-body-2 text-medium-emphasis mb-3" dir="auto">
      {{ missionPurpose }}
    </p>

    <div v-if="scenario" class="scenario-box rounded-lg pa-4 mb-3">
      <div class="text-caption text-medium-emphasis mb-1">
        {{ t('student.languages.speakingJourney.task.scenario') }}
      </div>
      <div class="text-body-1" dir="auto">{{ scenario }}</div>
    </div>

    <p v-if="instruction" class="text-body-1 mb-3" dir="auto">{{ instruction }}</p>
    <p v-if="context" class="text-body-2 text-medium-emphasis mb-3" dir="auto">{{ context }}</p>

    <div v-if="goal" class="goal-box rounded-lg pa-3 mb-4">
      <div class="text-caption text-medium-emphasis mb-1">
        {{ t('student.languages.speakingJourney.task.goal') }}
      </div>
      <div class="text-body-2">{{ goal }}</div>
    </div>

    <div class="d-flex flex-wrap gap-2 mb-4">
      <v-chip v-if="modeLabel" size="small" variant="tonal">{{ modeLabel }}</v-chip>
      <v-chip
        v-if="currentTask?.recording_required"
        size="small"
        color="error"
        variant="tonal"
        prepend-icon="mdi-microphone"
      >
        {{ t('student.languages.speakingJourney.task.recording') }}
      </v-chip>
      <v-chip
        v-if="currentTask?.controlled_required"
        size="small"
        variant="tonal"
        prepend-icon="mdi-format-list-checks"
      >
        {{ t('student.languages.speakingJourney.task.controlled') }}
      </v-chip>
      <v-chip
        v-if="currentTask?.uses_alex || liveExecutionReady || currentMission?.uses_alex"
        size="small"
        color="secondary"
        variant="tonal"
        prepend-icon="mdi-account-voice"
      >
        {{ t('student.languages.speakingJourney.mission.usesAlex') }}
      </v-chip>
      <v-chip
        v-if="alexRemainingLabel"
        size="small"
        variant="outlined"
        prepend-icon="mdi-timer-outline"
      >
        {{ alexRemainingLabel }}
      </v-chip>
    </div>

    <div class="prep-state rounded-lg pa-3 mb-4">
      <div class="text-caption text-medium-emphasis mb-1">
        {{ t('student.languages.speakingJourney.task.prepState') }}
      </div>
      <div class="text-body-2 font-weight-medium">
        {{ prepStateLabel }}
      </div>
    </div>

    <div class="d-flex flex-wrap gap-2">
      <v-btn
        v-if="liveExecutionReady"
        color="secondary"
        size="large"
        class="em-btn em-btn--secondary task-cta spk-pressable"
        :class="{ 'spk-pulse-once': liveExecutionReady }"
        :loading="preparingLive"
        prepend-icon="mdi-account-voice"
        :aria-label="t('student.languages.speakingJourney.actions.startTalkAlex')"
        @click="$emit('talk-alex')"
      >
        {{ t('student.languages.speakingJourney.actions.startTalkAlex') }}
      </v-btn>
      <v-btn
        v-else-if="canContinue"
        color="primary"
        class="em-btn em-btn--primary spk-pressable"
        :loading="advancing"
        prepend-icon="mdi-page-next"
        :aria-label="t('student.languages.speakingJourney.actions.continue')"
        @click="$emit('continue-activity')"
      >
        {{ t('student.languages.speakingJourney.actions.continue') }}
      </v-btn>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  educationalMissionInstructions,
  educationalMissionTitle,
} from '../../utils/speakingFraming.js'

const props = defineProps({
  currentTask: { type: Object, default: null },
  currentMission: { type: Object, default: null },
  currentActivityTitle: { type: String, default: '' },
  activityInstructions: { type: String, default: '' },
  expectedOutcome: { type: String, default: '' },
  scenarioPrompt: { type: String, default: '' },
  lessonTitle: { type: String, default: '' },
  liveExecutionReady: { type: Boolean, default: false },
  canContinue: { type: Boolean, default: false },
  advancing: { type: Boolean, default: false },
  preparingLive: { type: Boolean, default: false },
  alexRemainingSeconds: { type: Number, default: null },
  emphasis: { type: Boolean, default: false },
})

defineEmits(['continue-activity', 'talk-alex'])

const { t } = useI18n()

const show = computed(
  () =>
    Boolean(props.currentTask) ||
    Boolean(props.currentActivityTitle) ||
    props.liveExecutionReady,
)
const title = computed(() =>
  educationalMissionTitle(
    props.currentActivityTitle || props.currentMission?.title,
    props.lessonTitle,
    t,
  ),
)
const missionPurpose = computed(() =>
  educationalMissionInstructions(props.currentMission?.purpose || ''),
)
const instruction = computed(() =>
  educationalMissionInstructions(
    props.currentTask?.instruction || props.activityInstructions || '',
  ),
)
const context = computed(() => props.currentTask?.context_descriptor || '')
const mode = computed(() => props.currentTask?.execution_mode || props.currentMission?.execution_mode || '')
const modeLabel = computed(() => {
  const m = String(mode.value || '').toLowerCase()
  if (!m) return ''
  const key = `student.languages.speakingJourney.task.modes.${m}`
  const translated = t(key)
  return translated === key ? mode.value : translated
})
const goal = computed(() => props.expectedOutcome || '')
const scenario = computed(() => props.scenarioPrompt || '')

const alexRemainingLabel = computed(() => {
  const remaining = props.alexRemainingSeconds
  if (remaining == null || typeof remaining !== 'number') return ''
  const mins = Math.floor(remaining / 60)
  const secs = remaining % 60
  if (mins <= 0) return t('student.languages.speakingJourney.hero.alexSeconds', { seconds: secs })
  return t('student.languages.speakingJourney.hero.alexMinutes', { minutes: mins, seconds: secs })
})

const prepStateLabel = computed(() => {
  if (props.liveExecutionReady) {
    return t('student.languages.speakingJourney.task.prepReady')
  }
  if (props.currentTask?.uses_alex || props.currentMission?.uses_alex) {
    return t('student.languages.speakingJourney.task.prepAlmost')
  }
  return t('student.languages.speakingJourney.task.prepLearning')
})
</script>

<style scoped>
.task-screen {
  border-radius: var(--em-radius-md, 16px);
  transition: box-shadow 200ms ease, border-color 200ms ease;
}
.task-screen--emphasis {
  border: 1px solid rgba(var(--v-theme-secondary), 0.28);
  box-shadow: 0 10px 28px rgba(var(--v-theme-secondary), 0.1);
}
.goal-box,
.scenario-box,
.prep-state {
  background: rgba(var(--v-theme-primary), 0.06);
  border: 1px solid rgba(var(--v-theme-primary), 0.12);
}
.scenario-box {
  background: rgba(var(--v-theme-secondary), 0.08);
  border-color: rgba(var(--v-theme-secondary), 0.16);
}
.task-cta {
  min-width: min(100%, 280px);
}
</style>
