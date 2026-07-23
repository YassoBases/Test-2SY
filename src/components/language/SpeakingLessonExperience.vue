<template>
  <div
    class="speaking-lesson-experience"
    :class="[`speaking-lesson-experience--${stageKey}`, { 'is-advancing': advancing }]"
    role="region"
    :aria-label="t('student.languages.speakingJourney.runtime.lessonRegion')"
  >
    <SpeakingMissionHeader
      :lesson-title="lessonTitle"
      :focus-label="focusLabel"
      :focus-reason="focusReason"
      :plan-summary="planSummary"
      :official-cefr="officialCefr"
      :current-mission="currentMission"
      :next-mission="nextMission"
      :current-task="currentTask"
      :attempt="attempt"
      :objectives="objectives"
      :expected-outcome="expectedOutcome"
      :activity-kind="currentActivityKind"
      :live-execution-ready="liveExecutionReady"
    />

    <SpeakingLessonProgress
      :current-mission="currentMission"
      :current-activity-title="currentActivityTitle"
      :current-activity-kind="currentActivityKind"
      :activities-total="activitiesTotal"
      :activities-completed="activitiesCompleted"
      :activities-remaining="activitiesRemaining"
      :today-steps="todaySteps"
      :session-phase="sessionPhase"
    />

    <v-alert
      v-if="missionTransition"
      type="success"
      variant="tonal"
      class="mb-4 rounded-lg mission-transition"
      role="status"
      closable
      @click:close="missionTransition = null"
    >
      <div class="text-subtitle-2 font-weight-bold mb-1">
        {{ t('student.languages.speakingJourney.runtime.missionCompleteTitle') }}
      </div>
      <p class="text-body-2 mb-1">
        {{
          t('student.languages.speakingJourney.runtime.missionCompleteBody', {
            completed: missionTransition.completed,
          })
        }}
      </p>
      <p v-if="missionTransition.next" class="text-body-2 mb-0">
        {{
          t('student.languages.speakingJourney.runtime.missionNextBody', {
            next: missionTransition.next,
          })
        }}
      </p>
    </v-alert>

    <div class="lesson-layout">
      <aside class="lesson-rail" :aria-label="t('student.languages.speakingJourney.timeline.railTitle')">
        <SpeakingMissionTimeline
          :learning-path="learningPath"
          :today-missions="todayMissions"
          :lesson-title="lessonTitle || focusLabel"
          compact
        />
      </aside>

      <main class="lesson-focus">
        <section
          class="stage-banner glass-card pa-4 pa-md-5 mb-4"
          :style="{ '--stage-accent': stageAccent }"
          aria-live="polite"
        >
          <div class="d-flex align-start gap-3">
            <div class="stage-icon" aria-hidden="true">
              <v-icon :color="stageColor" size="28">{{ stageIcon }}</v-icon>
            </div>
            <div class="min-width-0 flex-grow-1">
              <div class="text-overline text-medium-emphasis mb-1">
                {{ stageLabel }}
              </div>
              <h3
                class="text-h6 font-weight-bold mb-1"
                tabindex="-1"
                data-spk-focus="lesson"
              >
                {{ focusActivityTitle }}
              </h3>
              <p class="text-body-2 text-medium-emphasis mb-0">
                {{ stageLead }}
              </p>
            </div>
          </div>
        </section>

        <Transition name="runtime-fade" mode="out-in">
          <div :key="focusKey" class="focus-surface">
            <SpeakingTeachingBlocks
              v-if="showTeaching"
              :blocks="teachingBlocks"
              :support="support"
              :layout="primarySurface === 'observe' ? 'focus' : 'secondary'"
            />

            <SpeakingGuidedPractice
              v-if="showGuided"
              :current-task="currentTask"
              :current-activity-kind="currentActivityKind"
              :activity-instructions="currentActivityInstructions"
              :can-continue="canContinueActivity"
              :advancing="advancing"
              :live-execution-ready="liveExecutionReady"
              :preparing-live="preparingLive"
              @continue-activity="$emit('continue-activity')"
              @talk-alex="$emit('talk-alex')"
            />

            <SpeakingTaskScreen
              v-if="showTask"
              :current-task="currentTask"
              :current-mission="currentMission"
              :current-activity-title="currentActivityTitle"
              :activity-instructions="currentActivityInstructions"
              :expected-outcome="expectedOutcome"
              :scenario-prompt="scenarioPrompt"
              :lesson-title="lessonTitle || focusLabel"
              :live-execution-ready="liveExecutionReady"
              :can-continue="canContinueActivity"
              :advancing="advancing"
              :preparing-live="preparingLive"
              :alex-remaining-seconds="alexRemainingSeconds"
              emphasis
              @continue-activity="$emit('continue-activity')"
              @talk-alex="$emit('talk-alex')"
            />

            <section
              v-if="showReflectSurface"
              class="reflect-surface glass-card pa-5 mb-5"
              aria-labelledby="reflect-heading"
            >
              <div class="text-overline text-medium-emphasis mb-1">
                {{ t('student.languages.speakingJourney.runtime.stages.reflect') }}
              </div>
              <h3 id="reflect-heading" class="text-h6 font-weight-bold mb-2">
                {{
                  currentActivityTitle ||
                  t('student.languages.speakingJourney.runtime.reflectTitle')
                }}
              </h3>
              <p v-if="currentActivityInstructions" class="text-body-1 mb-4" dir="auto">
                {{ currentActivityInstructions }}
              </p>
              <v-btn
                v-if="canContinueActivity"
                color="primary"
                  class="em-btn em-btn--primary spk-pressable"
                :loading="advancing"
                prepend-icon="mdi-check"
                :aria-label="t('student.languages.speakingJourney.actions.continue')"
                @click="$emit('continue-activity')"
              >
                {{ t('student.languages.speakingJourney.actions.continue') }}
              </v-btn>
            </section>

            <v-card
              v-if="showStudyContinue"
              class="glass-card pa-5 mb-5"
              variant="flat"
            >
              <div class="text-subtitle-1 font-weight-bold mb-2">
                {{
                  currentActivityTitle ||
                  t('student.languages.speakingJourney.lesson.studyStep')
                }}
              </div>
              <p v-if="currentActivityInstructions" class="text-body-2 mb-4" dir="auto">
                {{ currentActivityInstructions }}
              </p>
              <v-btn
                color="primary"
                class="em-btn em-btn--primary spk-pressable"
                :loading="advancing"
                prepend-icon="mdi-page-next"
                :aria-label="t('student.languages.speakingJourney.actions.continue')"
                @click="$emit('continue-activity')"
              >
                {{ t('student.languages.speakingJourney.actions.continue') }}
              </v-btn>
            </v-card>

            <SpeakingEmptyPanel
              v-if="showEmptyActivity"
              class="mb-5"
              compact
              icon="mdi-timeline-clock-outline"
              :title="t('student.languages.speakingJourney.runtime.emptyActivityTitle')"
              :description="t('student.languages.speakingJourney.runtime.emptyActivityBody')"
            />
          </div>
        </Transition>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import SpeakingMissionHeader from './SpeakingMissionHeader.vue'
import SpeakingLessonProgress from './SpeakingLessonProgress.vue'
import SpeakingMissionTimeline from './SpeakingMissionTimeline.vue'
import SpeakingTeachingBlocks from './SpeakingTeachingBlocks.vue'
import SpeakingGuidedPractice from './SpeakingGuidedPractice.vue'
import SpeakingTaskScreen from './SpeakingTaskScreen.vue'
import SpeakingEmptyPanel from './SpeakingEmptyPanel.vue'
import {
  activityMeta,
  primarySurfaceForActivity,
} from '../../utils/speakingRuntimeMeta.js'
import {
  educationalMissionTitle,
} from '../../utils/speakingFraming.js'

const props = defineProps({
  lessonTitle: { type: String, default: '' },
  focusLabel: { type: String, default: '' },
  focusReason: { type: String, default: '' },
  planSummary: { type: String, default: '' },
  officialCefr: { type: String, default: '' },
  currentMission: { type: Object, default: null },
  nextMission: { type: Object, default: null },
  currentTask: { type: Object, default: null },
  attempt: { type: Object, default: null },
  objectives: { type: Array, default: () => [] },
  expectedOutcome: { type: String, default: '' },
  learningPath: { type: Array, default: () => [] },
  todayMissions: { type: Array, default: () => [] },
  teachingBlocks: { type: Array, default: () => [] },
  support: { type: Array, default: () => [] },
  todaySteps: { type: Array, default: () => [] },
  sessionPhase: { type: String, default: '' },
  scenarioPrompt: { type: String, default: '' },
  alexRemainingSeconds: { type: Number, default: null },
  currentActivityTitle: { type: String, default: '' },
  currentActivityInstructions: { type: String, default: '' },
  currentActivityKind: { type: String, default: '' },
  activitiesTotal: { type: Number, default: 0 },
  activitiesCompleted: { type: Number, default: 0 },
  activitiesRemaining: { type: Number, default: 0 },
  liveExecutionReady: { type: Boolean, default: false },
  canContinueActivity: { type: Boolean, default: false },
  advancing: { type: Boolean, default: false },
  preparingLive: { type: Boolean, default: false },
})

defineEmits(['continue-activity', 'talk-alex'])

const { t } = useI18n()

const storyOrLessonTitle = computed(() => props.lessonTitle || props.focusLabel || '')
const focusActivityTitle = computed(() =>
  educationalMissionTitle(
    props.currentActivityTitle || props.currentMission?.title,
    storyOrLessonTitle.value,
    t,
  ),
)

const missionTransition = ref(null)
const lastMissionKey = ref('')
let missionTransitionTimer = 0

watch(
  () => props.currentMission?.title || props.currentMission?.purpose || '',
  (next, prev) => {
    if (!prev || !next || prev === next) {
      lastMissionKey.value = next
      return
    }
    missionTransition.value = {
      completed: educationalMissionTitle(prev, storyOrLessonTitle.value, t),
      next: educationalMissionTitle(next, storyOrLessonTitle.value, t),
    }
    lastMissionKey.value = next
    if (missionTransitionTimer) window.clearTimeout(missionTransitionTimer)
    missionTransitionTimer = window.setTimeout(() => {
      if (missionTransition.value?.next === educationalMissionTitle(next, storyOrLessonTitle.value, t)) {
        missionTransition.value = null
      }
      missionTransitionTimer = 0
    }, 8000)
  },
)

onUnmounted(() => {
  if (missionTransitionTimer) window.clearTimeout(missionTransitionTimer)
})

const meta = computed(() => activityMeta(props.currentActivityKind))
const stageKey = computed(() => meta.value.stage)
const stageIcon = computed(() => meta.value.icon)
const stageColor = computed(() => meta.value.color)
const stageAccent = computed(() => `rgb(var(--v-theme-${meta.value.color}))`)

const stageLabel = computed(() => {
  const key = `student.languages.speakingJourney.runtime.stages.${stageKey.value}`
  return t(key)
})

const stageLead = computed(() => {
  const key = `student.languages.speakingJourney.runtime.stageLeads.${stageKey.value}`
  return t(key)
})

const primarySurface = computed(() =>
  primarySurfaceForActivity({
    activityKind: props.currentActivityKind,
    liveExecutionReady: props.liveExecutionReady,
    hasTask: Boolean(props.currentTask),
    hasTeaching: Boolean(props.teachingBlocks?.length),
    controlledRequired: Boolean(props.currentTask?.controlled_required),
  }),
)

const focusKey = computed(
  () =>
    `${props.currentActivityKind}|${props.currentActivityTitle}|${primarySurface.value}|${props.liveExecutionReady}`,
)

const showTeaching = computed(() => {
  if (!props.teachingBlocks?.length) return false
  return primarySurface.value === 'observe' || primarySurface.value === 'practice'
})

const showGuided = computed(() => primarySurface.value === 'practice')

const showTask = computed(
  () =>
    primarySurface.value === 'speak' ||
    props.liveExecutionReady ||
    (Boolean(props.currentTask) && primarySurface.value !== 'practice'),
)

const showReflectSurface = computed(() => primarySurface.value === 'reflect')

const showStudyContinue = computed(() => {
  if (!props.canContinueActivity || props.liveExecutionReady) return false
  if (showGuided.value || showTask.value || showReflectSurface.value) return false
  return primarySurface.value === 'observe' && !props.teachingBlocks?.length
})

const showEmptyActivity = computed(() => {
  return (
    !showTeaching.value &&
    !showGuided.value &&
    !showTask.value &&
    !showReflectSurface.value &&
    !showStudyContinue.value &&
    !props.canContinueActivity &&
    !props.liveExecutionReady
  )
})
</script>

<style scoped>
.speaking-lesson-experience {
  position: relative;
}
.speaking-lesson-experience.is-advancing {
  opacity: 0.92;
  transition: opacity 180ms ease;
}
.lesson-layout {
  display: grid;
  gap: 1rem;
  grid-template-columns: 1fr;
}
@media (min-width: 960px) {
  .lesson-layout {
    grid-template-columns: minmax(220px, 280px) minmax(0, 1fr);
    align-items: start;
  }
  .lesson-rail {
    position: sticky;
    top: 1rem;
  }
}
.stage-banner {
  border-radius: var(--em-radius-md, 16px);
  border-inline-start: 4px solid var(--stage-accent, rgb(var(--v-theme-primary)));
}
.stage-icon {
  width: 3rem;
  height: 3rem;
  border-radius: 14px;
  display: grid;
  place-items: center;
  background: rgba(var(--v-theme-primary), 0.1);
  flex-shrink: 0;
}
.mission-transition {
  border-radius: var(--em-radius-md, 16px);
}
.min-width-0 {
  min-width: 0;
}
.runtime-fade-enter-active,
.runtime-fade-leave-active {
  transition: opacity 200ms ease, transform 200ms ease;
}
.runtime-fade-enter-from,
.runtime-fade-leave-to {
  opacity: 0;
  transform: translateY(6px);
}
@media (prefers-reduced-motion: reduce) {
  .runtime-fade-enter-active,
  .runtime-fade-leave-active {
    transition: none;
  }
}
</style>
