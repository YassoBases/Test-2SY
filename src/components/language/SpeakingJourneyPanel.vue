<template>
  <div class="speaking-journey speaking-runtime">
    <SpeakingContinuityStrip :active="continuityActive" />

    <Transition name="spk-enter">
      <v-alert
        v-if="returningFromAlex && !hasActiveSession"
        type="success"
        variant="tonal"
        class="mb-4 rounded-lg spk-pulse-once"
        role="status"
        closable
        @click:close="$emit('dismiss-return')"
      >
        {{ t('student.languages.speakingJourney.runtime.returnedFromAlex') }}
      </v-alert>
    </Transition>

    <template v-if="!hasActiveSession">
      <SpeakingEmptyPanel
        v-if="!hasPlan && !hasBlueprint"
        class="mb-6"
        icon="mdi-map-outline"
        :title="t('student.languages.speakingJourney.runtime.noPlanTitle')"
        :description="t('student.languages.speakingJourney.runtime.noPlanBody')"
        :action-label="t('student.languages.speakingJourney.actions.startSession')"
        action-icon="mdi-play"
        :loading="starting"
        @action="$emit('start-session')"
      />

      <v-card v-else class="journey-hero pa-6 pa-md-8 mb-6 glass-card" variant="flat">
        <div class="d-flex align-start gap-4 mb-4">
          <div class="hero-icon-wrap flex-shrink-0" aria-hidden="true">
            <v-icon color="primary" size="32">mdi-microphone</v-icon>
          </div>
          <div class="flex-grow-1 min-width-0">
            <div class="text-overline text-medium-emphasis mb-1">
              {{ t('student.languages.speakingJourney.hero.eyebrow') }}
            </div>
            <h2 class="text-h5 font-weight-bold mb-1" tabindex="-1" data-spk-focus="home">
              {{ focusLabel || t('student.languages.speakingJourney.hero.emptyFocus') }}
            </h2>
            <p class="text-body-2 text-medium-emphasis mb-0">{{ planSummary || focusReason }}</p>
          </div>
        </div>

        <v-row dense class="mb-4">
          <v-col cols="6" sm="3">
            <div class="hero-stat">
              <div class="hero-stat-label">{{ t('student.languages.speakingJourney.hero.level') }}</div>
              <div class="hero-stat-value" dir="ltr">{{ officialCefr || '—' }}</div>
            </div>
          </v-col>
          <v-col cols="6" sm="3">
            <div class="hero-stat">
              <div class="hero-stat-label">{{ t('student.languages.speakingJourney.hero.stage') }}</div>
              <div class="hero-stat-value hero-stat-value--sm" dir="ltr">{{ internalStage || '—' }}</div>
            </div>
          </v-col>
          <v-col cols="6" sm="3">
            <div class="hero-stat">
              <div class="hero-stat-label">{{ t('student.languages.speakingJourney.hero.alexTime') }}</div>
              <div class="hero-stat-value hero-stat-value--sm">{{ alexRemainingLabel }}</div>
            </div>
          </v-col>
          <v-col cols="6" sm="3">
            <div class="hero-stat">
              <div class="hero-stat-label">{{ t('student.languages.speakingJourney.hero.readiness') }}</div>
              <div class="hero-stat-value hero-stat-value--sm">
                <span class="d-inline-flex align-center gap-1">
                  <v-icon size="16" :color="spaUnlocked ? 'success' : 'warning'" aria-hidden="true">
                    {{ spaUnlocked ? 'mdi-lock-open-variant' : 'mdi-lock-outline' }}
                  </v-icon>
                  {{ readinessChip }}
                </span>
              </div>
            </div>
          </v-col>
        </v-row>

        <p v-if="nextRecommendation" class="text-body-2 mb-3">{{ nextRecommendation }}</p>
        <p v-else-if="expectedOutcome" class="text-body-2 mb-3">{{ expectedOutcome }}</p>
        <v-alert
          v-if="promotionNextAction"
          type="info"
          variant="tonal"
          density="comfortable"
          class="mb-4 rounded-lg"
          role="status"
        >
          {{ promotionNextAction }}
        </v-alert>
        <ul v-if="objectives.length" class="objectives mb-4">
          <li v-for="(obj, i) in objectives" :key="i">{{ obj }}</li>
        </ul>

        <div v-if="support.length" class="mb-4">
          <div class="text-caption text-medium-emphasis mb-2">
            {{ t('student.languages.speakingJourney.support.title') }}
          </div>
          <v-chip
            v-for="(chip, i) in support"
            :key="`hsup-${i}`"
            size="small"
            variant="tonal"
            :color="chipApplied(chip) ? 'success' : 'primary'"
            class="me-1 mb-1"
          >
            {{ supportLabel(chip) }}
          </v-chip>
        </div>

        <div class="d-flex flex-wrap gap-2">
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
            v-if="practiceWithAlexAvailable"
            variant="tonal"
            class="spk-pressable"
            :loading="preparingLive"
            prepend-icon="mdi-account-voice"
            :aria-label="t('student.languages.speakingJourney.actions.practiceAlex')"
            @click="$emit('practice-alex')"
          >
            {{ t('student.languages.speakingJourney.actions.practiceAlex') }}
          </v-btn>
          <v-btn
            v-if="spaUnlocked"
            variant="outlined"
            class="spk-pressable"
            prepend-icon="mdi-trophy-outline"
            :aria-label="t('student.languages.speakingJourney.actions.viewAssessment')"
            @click="$emit('go-assessment')"
          >
            {{ t('student.languages.speakingJourney.actions.viewAssessment') }}
          </v-btn>
        </div>
      </v-card>

      <SpeakingMissionTimeline
        :learning-path="learningPath"
        :today-missions="todayMissions"
        :lesson-title="lessonTitle || focusLabel"
      />
      <SpeakingTeachingBlocks v-if="teachingBlocks.length" :blocks="teachingBlocks" :support="support" />
    </template>

    <Transition v-else name="spk-enter" appear>
      <SpeakingLessonExperience
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
        :learning-path="learningPath"
        :today-missions="todayMissions"
        :teaching-blocks="teachingBlocks"
        :support="support"
        :today-steps="todaySteps"
        :session-phase="todaySessionPhase"
        :scenario-prompt="liveTaskPrompt"
        :alex-remaining-seconds="alexRemainingSeconds"
        :current-activity-title="currentActivityTitle"
        :current-activity-instructions="currentActivityInstructions"
        :current-activity-kind="currentActivityKind"
        :activities-total="activitiesTotal"
        :activities-completed="activitiesCompleted"
        :activities-remaining="activitiesRemaining"
        :live-execution-ready="liveExecutionReady"
        :can-continue-activity="canContinueActivity"
        :advancing="advancing"
        :preparing-live="preparingLive"
        @continue-activity="$emit('continue-activity')"
        @talk-alex="$emit('talk-alex')"
      />
    </Transition>

    <Transition name="spk-pop">
      <SpeakingReflection
        v-if="sessionOutcome"
        :session-outcome="sessionOutcome"
        :improving-skills="improvingSkills"
        :weak-skills="weakSkills"
        :retention-needed="retentionNeeded"
        :transfer-needed="transferNeeded"
        :next-mission="nextMission"
        :alex-remaining-seconds="alexRemainingSeconds"
        :spa-unlocked="spaUnlocked"
        :promotion-readiness="promotionReadiness"
        :starting="starting"
        @start-session="$emit('start-session')"
        @go-assessment="$emit('go-assessment')"
        @dismiss="$emit('dismiss-reflection')"
      />
    </Transition>

    <SpeakingSkillsPanel
      v-if="!hasActiveSession && !sessionOutcome"
      :weak-skills="weakSkills"
      :improving-skills="improvingSkills"
      :retention-needed="retentionNeeded"
      :transfer-needed="transferNeeded"
      :improving-skills-available="improvingSkillsAvailable"
      :retention-signal-present="retentionSignalPresent"
      :transfer-signal-present="transferSignalPresent"
      class="mb-6"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import SpeakingLessonExperience from './SpeakingLessonExperience.vue'
import SpeakingMissionTimeline from './SpeakingMissionTimeline.vue'
import SpeakingTeachingBlocks from './SpeakingTeachingBlocks.vue'
import SpeakingReflection from './SpeakingReflection.vue'
import SpeakingSkillsPanel from './SpeakingSkillsPanel.vue'
import SpeakingContinuityStrip from './SpeakingContinuityStrip.vue'
import SpeakingEmptyPanel from './SpeakingEmptyPanel.vue'

const props = defineProps({
  focusLabel: { type: String, default: '' },
  focusReason: { type: String, default: '' },
  planSummary: { type: String, default: '' },
  lessonTitle: { type: String, default: '' },
  officialCefr: { type: String, default: '' },
  internalStage: { type: String, default: null },
  alexRemainingSeconds: { type: Number, default: null },
  promotionReadiness: { type: Object, default: null },
  spaUnlocked: { type: Boolean, default: false },
  expectedOutcome: { type: String, default: '' },
  objectives: { type: Array, default: () => [] },
  currentMission: { type: Object, default: null },
  currentTask: { type: Object, default: null },
  attempt: { type: Object, default: null },
  learningPath: { type: Array, default: () => [] },
  nextMission: { type: Object, default: null },
  teachingBlocks: { type: Array, default: () => [] },
  support: { type: Array, default: () => [] },
  todaySteps: { type: Array, default: () => [] },
  weakSkills: { type: Array, default: () => [] },
  improvingSkills: { type: Array, default: () => [] },
  retentionNeeded: { type: Array, default: () => [] },
  transferNeeded: { type: Array, default: () => [] },
  improvingSkillsAvailable: { type: Boolean, default: false },
  retentionSignalPresent: { type: Boolean, default: false },
  transferSignalPresent: { type: Boolean, default: false },
  todayMissions: { type: Array, default: () => [] },
  hasActiveSession: { type: Boolean, default: false },
  hasPlan: { type: Boolean, default: false },
  hasBlueprint: { type: Boolean, default: false },
  practiceWithAlexAvailable: { type: Boolean, default: true },
  starting: { type: Boolean, default: false },
  advancing: { type: Boolean, default: false },
  preparingLive: { type: Boolean, default: false },
  sessionOutcome: { type: Object, default: null },
  liveTaskPrompt: { type: String, default: '' },
  todaySessionPhase: { type: String, default: '' },
  nextRecommendation: { type: String, default: '' },
  returningFromAlex: { type: Boolean, default: false },
  continuityOverride: { type: String, default: '' },
  currentActivityTitle: { type: String, default: '' },
  currentActivityInstructions: { type: String, default: '' },
  currentActivityKind: { type: String, default: '' },
  activitiesTotal: { type: Number, default: 0 },
  activitiesCompleted: { type: Number, default: 0 },
  activitiesRemaining: { type: Number, default: 0 },
  liveExecutionReady: { type: Boolean, default: false },
  canContinueActivity: { type: Boolean, default: false },
})

defineEmits([
  'start-session',
  'practice-alex',
  'talk-alex',
  'continue-activity',
  'go-assessment',
  'dismiss-return',
  'dismiss-reflection',
])

const { t } = useI18n()

const continuityActive = computed(() => {
  if (props.continuityOverride) return props.continuityOverride
  if (props.sessionOutcome) return 'reflection'
  if (props.hasActiveSession) return 'lesson'
  return 'home'
})

function supportLabel(chip) {
  if (typeof chip === 'string') return chip
  return chip?.label || chip?.title || chip?.text || String(chip?.kind || '')
}

function chipApplied(chip) {
  if (!chip || typeof chip === 'string') return false
  return Boolean(chip.applied)
}

const alexRemainingLabel = computed(() => {
  const remaining = props.alexRemainingSeconds
  if (remaining == null || typeof remaining !== 'number') {
    return t('student.languages.speakingJourney.hero.alexUnknown')
  }
  const mins = Math.floor(remaining / 60)
  const secs = remaining % 60
  if (mins <= 0) return t('student.languages.speakingJourney.hero.alexSeconds', { seconds: secs })
  return t('student.languages.speakingJourney.hero.alexMinutes', { minutes: mins, seconds: secs })
})

const readinessChip = computed(() => {
  const pr = props.promotionReadiness
  if (!pr) return t('student.languages.speakingJourney.hero.readinessUnknown')
  if (pr.spa_unlocked) return t('student.languages.speakingJourney.hero.readinessUnlocked')
  return pr.message || pr.unlock_state || t('student.languages.speakingJourney.hero.readinessBuilding')
})

const promotionNextAction = computed(() => {
  const action = props.promotionReadiness?.next_action
  return typeof action === 'string' && action.trim() ? action.trim() : ''
})
</script>

<style scoped>
.journey-hero {
  border-radius: var(--em-radius-md, 16px);
}
.hero-icon-wrap {
  width: 3.5rem;
  height: 3.5rem;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(var(--v-theme-primary), 0.12);
}
.hero-stat-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: rgba(var(--v-theme-on-surface), 0.6);
}
.hero-stat-value {
  font-size: 1.35rem;
  font-weight: 800;
}
.hero-stat-value--sm {
  font-size: 0.95rem;
  font-weight: 700;
}
.objectives {
  margin: 0;
  padding-inline-start: 1.25rem;
}
.min-width-0 {
  min-width: 0;
}
</style>
