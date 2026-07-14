<template>
  <div class="speaking-journey">
    <!-- Home: pre-session overview -->
    <template v-if="!hasActiveSession">
      <v-card class="journey-hero pa-6 pa-md-8 mb-6 glass-card" variant="flat">
        <div class="d-flex align-start gap-4 mb-4">
          <div class="hero-icon-wrap flex-shrink-0" aria-hidden="true">
            <v-icon color="primary" size="32">mdi-microphone</v-icon>
          </div>
          <div class="flex-grow-1 min-width-0">
            <div class="text-overline text-medium-emphasis mb-1">
              {{ t('student.languages.speakingJourney.hero.eyebrow') }}
            </div>
            <h2 class="text-h5 font-weight-bold mb-1">
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

        <p v-if="expectedOutcome" class="text-body-2 mb-3">{{ expectedOutcome }}</p>
        <ul v-if="objectives.length" class="objectives mb-4">
          <li v-for="(obj, i) in objectives" :key="i">{{ obj }}</li>
        </ul>

        <div class="d-flex flex-wrap gap-2">
          <v-btn
            color="primary"
            class="em-btn em-btn--primary"
            :loading="starting"
            prepend-icon="mdi-play"
            @click="$emit('start-session')"
          >
            {{ t('student.languages.speakingJourney.actions.startSession') }}
          </v-btn>
          <v-btn
            v-if="practiceWithAlexAvailable"
            variant="tonal"
            :loading="preparingLive"
            prepend-icon="mdi-account-voice"
            @click="$emit('practice-alex')"
          >
            {{ t('student.languages.speakingJourney.actions.practiceAlex') }}
          </v-btn>
          <v-btn
            v-if="spaUnlocked"
            variant="outlined"
            prepend-icon="mdi-trophy-outline"
            @click="$emit('go-assessment')"
          >
            {{ t('student.languages.speakingJourney.actions.viewAssessment') }}
          </v-btn>
        </div>
      </v-card>

      <SpeakingMissionTimeline :learning-path="learningPath" :today-missions="todayMissions" />
      <SpeakingTeachingBlocks :blocks="teachingBlocks" />
    </template>

    <!-- Active lesson experience -->
    <SpeakingLessonExperience
      v-else
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

    <SpeakingReflection
      :session-outcome="sessionOutcome"
      :improving-skills="improvingSkills"
      :weak-skills="weakSkills"
      :retention-needed="retentionNeeded"
      :next-mission="nextMission"
    />

    <SpeakingSkillsPanel
      :weak-skills="weakSkills"
      :improving-skills="improvingSkills"
      :retention-needed="retentionNeeded"
      :transfer-needed="transferNeeded"
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
  weakSkills: { type: Array, default: () => [] },
  improvingSkills: { type: Array, default: () => [] },
  retentionNeeded: { type: Array, default: () => [] },
  transferNeeded: { type: Array, default: () => [] },
  todayMissions: { type: Array, default: () => [] },
  hasActiveSession: { type: Boolean, default: false },
  practiceWithAlexAvailable: { type: Boolean, default: true },
  starting: { type: Boolean, default: false },
  advancing: { type: Boolean, default: false },
  preparingLive: { type: Boolean, default: false },
  sessionOutcome: { type: Object, default: null },
  currentActivityTitle: { type: String, default: '' },
  currentActivityInstructions: { type: String, default: '' },
  currentActivityKind: { type: String, default: '' },
  activitiesTotal: { type: Number, default: 0 },
  activitiesCompleted: { type: Number, default: 0 },
  activitiesRemaining: { type: Number, default: 0 },
  liveExecutionReady: { type: Boolean, default: false },
  canContinueActivity: { type: Boolean, default: false },
})

defineEmits(['start-session', 'practice-alex', 'talk-alex', 'continue-activity', 'go-assessment'])

const { t } = useI18n()

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
