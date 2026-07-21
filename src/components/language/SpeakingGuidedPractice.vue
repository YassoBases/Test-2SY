<template>
  <section
    v-if="show"
    class="guided-practice glass-card pa-5 mb-5"
    :aria-label="t('student.languages.speakingJourney.guided.title')"
  >
    <div class="text-subtitle-1 font-weight-bold mb-1">
      {{ t('student.languages.speakingJourney.guided.title') }}
    </div>
    <p class="text-body-2 text-medium-emphasis mb-4">
      {{ t('student.languages.speakingJourney.guided.lead') }}
    </p>

    <ol class="prep-flow mb-4">
      <li
        v-for="(step, idx) in flowSteps"
        :key="step.key"
        class="prep-step"
        :class="{
          'prep-step--active': idx === activeStep,
          'prep-step--done': idx < activeStep,
        }"
      >
        <button
          type="button"
          class="prep-step-btn"
          :aria-current="idx === activeStep ? 'step' : undefined"
          @click="activeStep = idx"
        >
          <span class="prep-step-index" aria-hidden="true">
            <v-icon v-if="idx < activeStep" size="16">mdi-check</v-icon>
            <template v-else>{{ idx + 1 }}</template>
          </span>
          <span class="prep-step-label">{{ step.label }}</span>
        </button>
      </li>
    </ol>

    <div class="practice-prompt rounded-lg pa-4 mb-3" dir="auto">
      <div class="text-caption text-medium-emphasis mb-1">
        {{ currentFlowHint }}
      </div>
      <div class="text-body-1">{{ instruction || currentFlowHint }}</div>
    </div>
    <p v-if="context" class="text-body-2 text-medium-emphasis mb-4" dir="auto">{{ context }}</p>

    <div class="d-flex flex-wrap gap-2">
      <v-btn
        v-if="activeStep < flowSteps.length - 1"
        variant="tonal"
        prepend-icon="mdi-arrow-right"
        @click="activeStep += 1"
      >
        {{ t('student.languages.speakingJourney.guided.nextStep') }}
      </v-btn>
      <v-btn
        v-else-if="liveExecutionReady"
        color="secondary"
        class="em-btn em-btn--secondary spk-pressable"
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
        :aria-label="t('student.languages.speakingJourney.guided.readyContinue')"
        @click="$emit('continue-activity')"
      >
        {{ t('student.languages.speakingJourney.guided.readyContinue') }}
      </v-btn>
    </div>
  </section>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { educationalMissionInstructions } from '../../utils/speakingFraming.js'

const props = defineProps({
  currentTask: { type: Object, default: null },
  currentActivityKind: { type: String, default: '' },
  activityInstructions: { type: String, default: '' },
  canContinue: { type: Boolean, default: false },
  advancing: { type: Boolean, default: false },
  liveExecutionReady: { type: Boolean, default: false },
  preparingLive: { type: Boolean, default: false },
})

defineEmits(['continue-activity', 'talk-alex'])

const { t } = useI18n()
const activeStep = ref(0)

const show = computed(() => {
  const kind = String(props.currentActivityKind || '').toLowerCase()
  const mode = String(props.currentTask?.execution_mode || '').toLowerCase()
  return (
    kind.includes('guided') ||
    kind.includes('remediation') ||
    kind.includes('retry') ||
    mode.includes('controlled') ||
    mode.includes('guided') ||
    Boolean(props.currentTask?.controlled_required)
  )
})

const instruction = computed(() =>
  educationalMissionInstructions(
    props.currentTask?.instruction || props.activityInstructions || '',
  ),
)
const context = computed(() => props.currentTask?.context_descriptor || '')

/** Local presentation flow only — does not mutate backend progress. */
const flowSteps = computed(() => [
  {
    key: 'observe',
    label: t('student.languages.speakingJourney.guided.flow.observe'),
    hint: t('student.languages.speakingJourney.guided.flow.observeHint'),
  },
  {
    key: 'practice',
    label: t('student.languages.speakingJourney.guided.flow.practice'),
    hint: t('student.languages.speakingJourney.guided.flow.practiceHint'),
  },
  {
    key: 'prepare',
    label: t('student.languages.speakingJourney.guided.flow.prepare'),
    hint: t('student.languages.speakingJourney.guided.flow.prepareHint'),
  },
  {
    key: 'ready',
    label: t('student.languages.speakingJourney.guided.flow.ready'),
    hint: t('student.languages.speakingJourney.guided.flow.readyHint'),
  },
])

const currentFlowHint = computed(
  () => flowSteps.value[activeStep.value]?.hint || '',
)

watch(
  () => [props.currentActivityKind, props.currentTask?.instruction],
  () => {
    activeStep.value = 0
  },
)
</script>

<style scoped>
.guided-practice {
  border-radius: var(--em-radius-md, 16px);
}
.prep-flow {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 8px;
  grid-template-columns: 1fr 1fr;
}
@media (min-width: 700px) {
  .prep-flow {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}
.prep-step-btn {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 8px;
  border: 1px solid rgba(var(--v-theme-on-surface), 0.1);
  background: rgba(var(--v-theme-on-surface), 0.03);
  border-radius: 12px;
  padding: 10px 12px;
  text-align: start;
  cursor: pointer;
  color: inherit;
  transition: border-color 160ms ease, background 160ms ease;
}
.prep-step--active .prep-step-btn {
  border-color: rgba(var(--v-theme-primary), 0.35);
  background: rgba(var(--v-theme-primary), 0.08);
}
.prep-step--done .prep-step-btn {
  border-color: rgba(var(--v-theme-success), 0.28);
  background: rgba(var(--v-theme-success), 0.08);
}
.prep-step-index {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-size: 0.75rem;
  font-weight: 700;
  background: rgba(var(--v-theme-on-surface), 0.08);
  flex-shrink: 0;
}
.prep-step-label {
  font-size: 0.85rem;
  font-weight: 600;
}
.practice-prompt {
  background: rgba(var(--v-theme-on-surface), 0.04);
  border: 1px solid rgba(var(--v-theme-on-surface), 0.06);
}
</style>
