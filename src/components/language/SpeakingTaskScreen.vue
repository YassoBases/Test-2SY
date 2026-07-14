<template>
  <section v-if="show" class="task-screen glass-card pa-5 pa-md-6 mb-5" aria-labelledby="speaking-task-heading">
    <div class="text-overline text-medium-emphasis mb-1">
      {{ t('student.languages.speakingJourney.task.title') }}
    </div>
    <h3 id="speaking-task-heading" class="text-h6 font-weight-bold mb-2">
      {{ title }}
    </h3>
    <p v-if="instruction" class="text-body-1 mb-3" dir="auto">{{ instruction }}</p>
    <p v-if="context" class="text-body-2 text-medium-emphasis mb-3" dir="auto">{{ context }}</p>

    <div v-if="goal" class="goal-box rounded-lg pa-3 mb-4">
      <div class="text-caption text-medium-emphasis mb-1">
        {{ t('student.languages.speakingJourney.task.goal') }}
      </div>
      <div class="text-body-2">{{ goal }}</div>
    </div>

    <div class="d-flex flex-wrap gap-2 mb-4">
      <v-chip v-if="mode" size="small" variant="tonal">{{ mode }}</v-chip>
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
        v-if="currentTask?.uses_alex || liveExecutionReady"
        size="small"
        color="secondary"
        variant="tonal"
        prepend-icon="mdi-account-voice"
      >
        {{ t('student.languages.speakingJourney.mission.usesAlex') }}
      </v-chip>
    </div>

    <div class="d-flex flex-wrap gap-2">
      <v-btn
        v-if="liveExecutionReady"
        color="secondary"
        class="em-btn em-btn--secondary"
        :loading="preparingLive"
        prepend-icon="mdi-account-voice"
        @click="$emit('talk-alex')"
      >
        {{ t('student.languages.speakingJourney.actions.talkAlex') }}
      </v-btn>
      <v-btn
        v-else-if="canContinue"
        color="primary"
        class="em-btn em-btn--primary"
        :loading="advancing"
        prepend-icon="mdi-page-next"
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

const props = defineProps({
  currentTask: { type: Object, default: null },
  currentActivityTitle: { type: String, default: '' },
  activityInstructions: { type: String, default: '' },
  expectedOutcome: { type: String, default: '' },
  liveExecutionReady: { type: Boolean, default: false },
  canContinue: { type: Boolean, default: false },
  advancing: { type: Boolean, default: false },
  preparingLive: { type: Boolean, default: false },
})

defineEmits(['continue-activity', 'talk-alex'])

const { t } = useI18n()

const show = computed(
  () =>
    Boolean(props.currentTask) ||
    Boolean(props.currentActivityTitle) ||
    props.liveExecutionReady,
)
const title = computed(
  () => props.currentActivityTitle || t('student.languages.speakingJourney.task.title'),
)
const instruction = computed(
  () => props.currentTask?.instruction || props.activityInstructions || '',
)
const context = computed(() => props.currentTask?.context_descriptor || '')
const mode = computed(() => props.currentTask?.execution_mode || '')
const goal = computed(() => props.expectedOutcome || '')
</script>

<style scoped>
.task-screen {
  border-radius: var(--em-radius-md, 16px);
}
.goal-box {
  background: rgba(var(--v-theme-primary), 0.06);
  border: 1px solid rgba(var(--v-theme-primary), 0.12);
}
</style>
