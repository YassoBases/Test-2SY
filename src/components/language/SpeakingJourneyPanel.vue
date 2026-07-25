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

      <template v-else>
        <div class="spk-mission glass-card mb-4">
          <div class="spk-mission__glow" aria-hidden="true" />
          <div class="spk-mission__badge">
            <v-icon size="26" color="secondary">mdi-microphone</v-icon>
            <span class="spk-mission__cefr" dir="ltr">{{ officialCefr || '—' }}</span>
          </div>
          <div class="spk-mission__copy min-width-0">
            <p class="spk-mission__kicker mb-1">
              {{ t('student.languages.speakingJourney.hero.eyebrow') }}
            </p>
            <h2 class="spk-mission__title" tabindex="-1" data-spk-focus="home">
              {{ focusLabel || t('student.languages.speakingJourney.hero.emptyFocus') }}
            </h2>
            <p class="spk-mission__hint mb-0">{{ planSummary || focusReason }}</p>
            <div class="spk-mission__stats">
              <div class="spk-stat">
                <span class="spk-stat__value" dir="ltr">{{ officialCefr || '—' }}</span>
                <span class="spk-stat__label">{{ t('student.languages.speakingJourney.hero.level') }}</span>
              </div>
              <div class="spk-stat">
                <span class="spk-stat__value spk-stat__value--sm" dir="ltr">{{ internalStage || '—' }}</span>
                <span class="spk-stat__label">{{ t('student.languages.speakingJourney.hero.stage') }}</span>
              </div>
              <div class="spk-stat">
                <span class="spk-stat__value spk-stat__value--sm">{{ alexRemainingLabel }}</span>
                <span class="spk-stat__label">{{ t('student.languages.speakingJourney.hero.alexTime') }}</span>
              </div>
              <div class="spk-stat">
                <span class="spk-stat__value spk-stat__value--sm d-inline-flex align-center gap-1">
                  <v-icon size="14" :color="spaUnlocked ? 'success' : 'warning'" aria-hidden="true">
                    {{ spaUnlocked ? 'mdi-lock-open-variant' : 'mdi-lock-outline' }}
                  </v-icon>
                  {{ readinessChip }}
                </span>
                <span class="spk-stat__label">{{ t('student.languages.speakingJourney.hero.readiness') }}</span>
              </div>
            </div>
          </div>
          <div class="spk-mission__actions">
            <v-btn
              color="secondary"
              variant="flat"
              size="large"
              rounded="lg"
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
              size="large"
              rounded="lg"
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
              size="large"
              rounded="lg"
              class="spk-pressable"
              prepend-icon="mdi-trophy-outline"
              :aria-label="t('student.languages.speakingJourney.actions.viewAssessment')"
              @click="$emit('go-assessment')"
            >
              {{ t('student.languages.speakingJourney.actions.viewAssessment') }}
            </v-btn>
          </div>

          <div v-if="missionExtrasVisible" class="spk-mission__extras">
            <p v-if="nextRecommendation" class="text-body-2 mb-2">{{ nextRecommendation }}</p>
            <p v-else-if="expectedOutcome" class="text-body-2 mb-2">{{ expectedOutcome }}</p>
            <v-alert
              v-if="promotionNextAction"
              type="info"
              variant="tonal"
              density="comfortable"
              class="mb-3 rounded-lg"
              role="status"
            >
              {{ promotionNextAction }}
            </v-alert>
            <ul v-if="objectives.length" class="objectives mb-3">
              <li v-for="(obj, i) in objectives" :key="i">{{ obj }}</li>
            </ul>
            <div v-if="support.length">
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
          </div>
        </div>

        <SkillStagePathMap
          skill-label="Speaking"
          skill-key="speaking"
          :current-cefr="officialCefr"
          :current-stage="internalStage"
          current-reason="Complete more speaking practice attempts."
          class="mb-4"
        />

        <div class="spk-secondary mb-4">
          <SpeakingMissionTimeline
            compact
            :learning-path="learningPath"
            :today-missions="todayMissions"
            :lesson-title="lessonTitle || focusLabel"
          />
          <SpeakingTeachingBlocks
            v-if="teachingBlocks.length"
            :blocks="teachingBlocks"
            :support="support"
          />
        </div>
      </template>
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
import SkillStagePathMap from './SkillStagePathMap.vue'

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

const missionExtrasVisible = computed(() =>
  Boolean(
    props.nextRecommendation ||
      props.expectedOutcome ||
      promotionNextAction.value ||
      props.objectives.length ||
      props.support.length,
  ),
)
</script>

<style scoped>
.spk-mission {
  position: relative;
  overflow: hidden;
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 1rem 1.35rem;
  align-items: center;
  padding: 1.25rem 1.35rem;
}

.spk-mission__glow {
  position: absolute;
  inset: -35% auto auto -8%;
  width: 240px;
  height: 240px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(var(--v-theme-secondary), 0.2), transparent 68%);
  pointer-events: none;
}

.spk-mission__badge {
  position: relative;
  z-index: 1;
  width: 88px;
  height: 88px;
  border-radius: 26px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.2rem;
  background: linear-gradient(145deg, rgba(var(--v-theme-secondary), 0.26), rgba(var(--v-theme-primary), 0.1));
  border: 1px solid rgba(var(--v-theme-secondary), 0.32);
}

.spk-mission__cefr {
  font-size: 1.25rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  line-height: 1;
  color: rgb(var(--v-theme-secondary));
}

.spk-mission__copy {
  position: relative;
  z-index: 1;
}

.spk-mission__kicker {
  font-size: 0.72rem;
  font-weight: 650;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: rgba(var(--v-theme-on-surface), 0.5);
}

.spk-mission__title {
  font-size: 1.28rem;
  font-weight: 750;
  letter-spacing: -0.02em;
  margin: 0 0 0.35rem;
  line-height: 1.3;
}

.spk-mission__hint {
  font-size: 0.875rem;
  color: rgba(var(--v-theme-on-surface), 0.62);
}

.spk-mission__stats {
  display: flex;
  flex-wrap: wrap;
  gap: 0.85rem 1.15rem;
  margin-top: 0.85rem;
}

.spk-stat {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.spk-stat__value {
  font-size: 1.05rem;
  font-weight: 750;
  letter-spacing: -0.02em;
  line-height: 1.15;
}

.spk-stat__value--sm {
  font-size: 0.9rem;
}

.spk-stat__label {
  font-size: 0.68rem;
  color: rgba(var(--v-theme-on-surface), 0.5);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.spk-mission__actions {
  position: relative;
  z-index: 1;
  grid-column: 1 / -1;
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem;
  padding-top: 0.35rem;
  border-top: 1px solid rgba(var(--v-theme-on-surface), 0.08);
}

.spk-mission__extras {
  position: relative;
  z-index: 1;
  grid-column: 1 / -1;
  padding-top: 0.15rem;
}

.spk-secondary {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
  align-items: start;
}

.objectives {
  margin: 0;
  padding-inline-start: 1.25rem;
}

.min-width-0 {
  min-width: 0;
}

@media (max-width: 900px) {
  .spk-secondary {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .spk-mission {
    grid-template-columns: 1fr;
  }
}
</style>
