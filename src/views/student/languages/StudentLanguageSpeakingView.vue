<template>
  <div class="page-container slide-up-enter-active speaking-runtime">
    <LanguageModuleTabs />
    <PageHeader
      compact
      :eyebrow="t('student.languages.speakingJourney.page.eyebrow')"
      eyebrow-icon="mdi-microphone"
      :title="t('student.languages.speakingJourney.page.title')"
      :subtitle="t('student.languages.speakingJourney.page.subtitle')"
    />

    <v-alert v-if="pageError" type="error" variant="tonal" class="mb-4 rounded-lg" role="alert">
      <div class="d-flex flex-wrap align-center justify-space-between gap-3">
        <div>
          <div class="text-body-2 font-weight-medium mb-1">{{ friendlyErrorTitle }}</div>
          <span>{{ pageErrorDisplay }}</span>
        </div>
        <div class="d-flex flex-wrap gap-2">
          <v-btn
            size="small"
            variant="text"
            class="spk-pressable"
            :loading="journeyLoading"
            :aria-label="t('student.languages.speakingJourney.runtime.retry')"
            @click="retryJourneyLoad"
          >
            {{ t('student.languages.speakingJourney.runtime.retry') }}
          </v-btn>
          <v-btn
            size="small"
            variant="tonal"
            class="spk-pressable"
            :loading="lessonLoading || learningStarting"
            :aria-label="t('student.languages.speakingJourney.runtime.continueLearning')"
            @click="onContinueLearning"
          >
            {{ t('student.languages.speakingJourney.runtime.continueLearning') }}
          </v-btn>
        </div>
      </div>
    </v-alert>

    <LoadingState
      v-if="pageLoading"
      variant="cards"
      :count="3"
      :label="t('student.languages.speakingJourney.runtime.loading')"
      class="mb-6 spk-skeleton-block"
    />

    <template v-else>
      <v-tabs
        v-model="tab"
        color="secondary"
        dir="rtl"
        class="mb-4 speaking-tabs"
        show-arrows
        density="comfortable"
      >
        <v-tab value="journey">{{ t('student.languages.speakingJourney.tabs.journey') }}</v-tab>
        <v-tab value="lesson">{{ t('student.languages.speakingJourney.tabs.lesson') }}</v-tab>
        <v-tab value="discussion">{{ t('student.languages.speakingJourney.tabs.discussion') }}</v-tab>
        <v-tab value="alex">{{ t('student.languages.speakingJourney.tabs.alex') }}</v-tab>
        <v-tab value="assessment">{{ t('student.languages.speakingJourney.tabs.assessment') }}</v-tab>
      </v-tabs>

      <v-window v-model="tab">
        <v-window-item value="journey">
          <SpeakingJourneyPanel
            :focus-label="focusLabel"
            :focus-reason="focusReason"
            :plan-summary="planSummary"
            :lesson-title="lessonTitle"
            :official-cefr="officialCefr"
            :internal-stage="internalStage"
            :alex-remaining-seconds="alexRemainingSeconds"
            :promotion-readiness="promotionReadiness"
            :spa-unlocked="spaUnlocked"
            :expected-outcome="expectedOutcome"
            :objectives="objectives"
            :current-mission="currentMission"
            :current-task="currentTask"
            :attempt="attempt"
            :teaching-blocks="teachingBlocks"
            :support="support"
            :today-steps="todaySteps"
            :learning-path="learningPath"
            :next-mission="nextMission"
            :weak-skills="weakSkills"
            :improving-skills="improvingSkills"
            :retention-needed="retentionNeeded"
            :transfer-needed="transferNeeded"
            :improving-skills-available="improvingSkillsAvailable"
            :retention-signal-present="retentionSignalPresent"
            :transfer-signal-present="transferSignalPresent"
            :today-missions="todayMissions"
            :has-active-session="hasActiveSession"
            :has-plan="hasPlan"
            :has-blueprint="hasBlueprint"
            :practice-with-alex-available="practiceWithAlexAvailable"
            :starting="starting || learningStarting"
            :advancing="advancing"
            :preparing-live="preparingLive"
            :session-outcome="sessionOutcome"
            :live-task-prompt="liveTaskPrompt"
            :today-session-phase="todaySessionPhase"
            :next-recommendation="nextRecommendation"
            :returning-from-alex="returningFromAlex"
            :continuity-override="tab === 'alex' ? 'alex' : ''"
            :current-activity-title="currentActivityTitle"
            :current-activity-instructions="currentActivityInstructions"
            :current-activity-kind="currentActivityKind"
            :activities-total="activitiesTotal"
            :activities-completed="activitiesCompleted"
            :activities-remaining="activitiesRemaining"
            :live-execution-ready="liveExecutionReady"
            :can-continue-activity="canContinueActivity"
            @start-session="onStartJourneySession"
            @continue-activity="onContinueActivity"
            @practice-alex="goLivePrepared"
            @talk-alex="goLivePrepared"
            @go-assessment="tab = 'assessment'"
            @dismiss-return="clearReturningFromAlex"
            @dismiss-reflection="clearSessionOutcome"
          />
        </v-window-item>

        <v-window-item value="lesson">
          <SpeakingPackageLesson
            :loading="lessonLoading"
            :advancing="lessonAdvancing"
            :error="lessonError"
            :package-data="lessonPackage"
            :constraints-summary="lessonConstraints"
            :state="lessonState"
            :section-progress="lessonProgress"
            :current-section="lessonSection"
            :ready-for-discussion="lessonReadyForDiscussion"
            @advance="onLessonAdvance"
            @mark-vocab="onLessonMarkVocab"
            @mark-block="onLessonMarkBlock"
            @mini-prep="onLessonMiniPrep"
            @open-latest="onLessonOpenLatest"
            @restart="onLessonRestart"
            @retry="onLessonRetry"
            @start-discussion="onStartDiscussionFromLesson"
          />
        </v-window-item>

        <v-window-item value="discussion">
          <SpeakingGuidedDiscussion
            :loading="discussionLoading"
            :submitting="discussionSubmitting"
            :advancing="discussionAdvancing"
            :error="discussionError"
            :draft="discussionDraft"
            :state="discussionState"
            :package-title="discussionPackageTitle"
            :current-step="discussionCurrentStep"
            :turns="discussionTurns"
            :phase="discussionPhase"
            :completed="discussionCompleted"
            :ready-for-alex="discussionReadyForAlex"
            :can-advance="discussionCanAdvance"
            :steps-total="discussionStepsTotal"
            :step-index="discussionStepIndex"
            :progress-percent="discussionProgressPercent"
            :case-title="discussionCaseTitle"
            :setting="discussionCaseSetting"
            :character-hooks="discussionCharacterHooks"
            :voice-mode="sceneVoiceMode"
            :voice-active="sceneVoiceActive"
            :last-heard="sceneVoiceLastHeard"
            :needs-lesson="discussionNeedsLesson"
            :has-tutor-audio="Boolean(discussionLastAudio?.b64)"
            @open="onDiscussionOpen"
            @submit="onDiscussionSubmit"
            @advance="onDiscussionAdvance"
            @restart="onDiscussionRestart"
            @retry="onDiscussionRetry"
            @go-lesson="enterLessonTab"
            @start-alex="goLivePrepared"
            @start-recording="onDiscussionStartRecording"
            @stop-recording="onDiscussionStopRecording"
            @replay-audio="onDiscussionReplayAudio"
            @update:draft="discussionDraft = $event"
          />
        </v-window-item>

        <v-window-item value="alex">
          <div class="speaking-runtime">
            <SpeakingCaseContinuityStrip
              v-if="aliveCaseTitle"
              :story-title="aliveCaseTitle"
              :student-role="aliveStudentRole"
              :characters="aliveCharacters"
              :decision="aliveDecision"
              :vocabulary="aliveVocabulary"
              :grammar="aliveGrammar"
              mode="live"
            />
            <SpeakingContinuityStrip active="alex" />
            <v-alert
              v-if="hasActiveSession || lessonTitle"
              type="info"
              variant="tonal"
              class="mb-4 rounded-lg alex-continuity"
              role="status"
            >
              <div class="text-subtitle-2 font-weight-bold mb-1">
                {{ t('student.languages.speakingJourney.alex.inLessonTitle') }}
              </div>
              <p class="text-body-2 mb-2">
                {{
                  t('student.languages.speakingJourney.alex.inLessonBody', {
                    lesson: lessonTitle || focusLabel || currentMission?.title || '—',
                  })
                }}
              </p>
              <v-btn
                size="small"
                variant="text"
                class="spk-pressable"
                prepend-icon="mdi-arrow-left"
                :aria-label="t('student.languages.speakingJourney.alex.backToLesson')"
                @click="returnToLesson"
              >
                {{ t('student.languages.speakingJourney.alex.backToLesson') }}
              </v-btn>
            </v-alert>
            <v-alert
              v-if="!liveExecutionReady && !journeyLiveSessionId"
              type="info"
              variant="tonal"
              class="mb-4 rounded-lg"
              role="status"
            >
              {{ t('student.languages.speakingJourney.alex.needSession') }}
              <template #append>
                <v-btn
                  variant="text"
                  size="small"
                  class="spk-pressable"
                  :loading="preparingLive"
                  :aria-label="t('student.languages.speakingJourney.actions.talkAlex')"
                  @click="goLivePrepared"
                >
                  {{ t('student.languages.speakingJourney.actions.talkAlex') }}
                </v-btn>
              </template>
            </v-alert>
            <LanguageSpeakingLiveShell
              v-if="alexShellMounted"
              :key="alexShellKey"
              require-prepared-session
              :initial-task-prompt="liveTaskPrompt"
              :journey-live-session-id="journeyLiveSessionId"
              @session-ended="onLiveEnded"
              @back-to-lesson="returnToLesson"
            />
          </div>
        </v-window-item>

        <v-window-item value="assessment">
          <div class="speaking-runtime mb-4">
            <v-btn
              variant="text"
              class="spk-pressable mb-2"
              prepend-icon="mdi-arrow-left"
              :aria-label="t('student.languages.speakingJourney.runtime.backToJourney')"
              @click="tab = 'journey'"
            >
              {{ t('student.languages.speakingJourney.runtime.backToJourney') }}
            </v-btn>
          </div>
          <SpeakingPromotionPanel
            :phase="promoPhase"
            :home-state="promoHomeState"
            :status="promoStatus"
            :status-loading="promoStatusLoading"
            :status-error="promoStatusError"
            :assessment-error="promoAssessmentError"
            :assessment-loading="promoAssessmentLoading"
            :available="promoAvailable"
            :spa-unlocked="promoSpaUnlocked"
            :message="promoMessage"
            :source-cefr="promoSourceCefr"
            :target-cefr="promoTargetCefr"
            :estimated-duration-seconds="promoEstimatedDuration"
            :task-count="promoTaskCount"
            :has-interaction-gaps="promoHasInteractionGaps"
            :current-task="promoCurrentTask"
            :completed-task-count="promoCompletedCount"
            :remaining-task-count="promoRemainingCount"
            :session-loading="promoSessionLoading"
            :session-error="promoSessionError"
            :submit-loading="promoSubmitLoading"
            :submit-error="promoSubmitError"
            :last-submit="promoLastSubmit"
            :action-loading="promoActionLoading"
            :result="promoResult"
            :result-loading="promoResultLoading"
            :result-error="promoResultError"
            :can-retry="promoCanRetry"
            :can-promote="promoCanPromote"
            :promote-loading="promoPromoteLoading"
            :promote-error="promoPromoteError"
            :promotion-result="promoPromotionResult"
            :official-promoted="promoOfficialPromoted"
            @open-intro="onPromoOpenIntro"
            @begin-tasks="onPromoBeginTasks"
            @resume="onPromoResume"
            @submit-task="onPromoSubmitTask"
            @abandon="onPromoAbandon"
            @retry="onPromoRetry"
            @view-result="onPromoViewResult"
            @retry-status="loadPromoStatus"
            @back-to-journey="onPromoBackToJourney"
            @back-home="onPromoBackHome"
            @promote="onPromoOfficial"
          />
        </v-window-item>
      </v-window>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import PageHeader from '../../../components/common/PageHeader.vue'
import LoadingState from '../../../components/common/LoadingState.vue'
import LanguageModuleTabs from '../../../components/language/LanguageModuleTabs.vue'
import LanguageSpeakingLiveShell from '../../../components/language/LanguageSpeakingLiveShell.vue'
import SpeakingJourneyPanel from '../../../components/language/SpeakingJourneyPanel.vue'
import SpeakingPackageLesson from '../../../components/language/SpeakingPackageLesson.vue'
import SpeakingGuidedDiscussion from '../../../components/language/SpeakingGuidedDiscussion.vue'
import SpeakingPromotionPanel from '../../../components/language/SpeakingPromotionPanel.vue'
import SpeakingContinuityStrip from '../../../components/language/SpeakingContinuityStrip.vue'
import SpeakingCaseContinuityStrip from '../../../components/language/SpeakingCaseContinuityStrip.vue'
import { useLanguageGate } from '../../../composables/useLanguageGate.js'
import { useLanguageAccess } from '../../../composables/useLanguageAccess.js'
import { useSpeakingJourney } from '../../../composables/useSpeakingJourney.js'
import { useSpeakingLearningPackage } from '../../../composables/useSpeakingLearningPackage.js'
import { useSpeakingLessonRuntime } from '../../../composables/useSpeakingLessonRuntime.js'
import { useSpeakingDiscussion } from '../../../composables/useSpeakingDiscussion.js'
import { useScenePracticeVoice } from '../../../composables/useScenePracticeVoice.js'
import { useSpeakingPromotion } from '../../../composables/useSpeakingPromotion.js'

const { t } = useI18n()
const router = useRouter()
const route = useRoute()
const { access, loadAccess } = useLanguageAccess()
const { handleLanguageApiError, getErrorMessage } = useLanguageGate()

const {
  loading: journeyLoading,
  error: journeyError,
  errorKind: journeyErrorKind,
  starting,
  advancing,
  preparingLive,
  sessionOutcome,
  liveTaskPrompt,
  journeyLiveSessionId,
  focusLabel,
  focusReason,
  officialCefr,
  internalStage,
  alexRemainingSeconds,
  promotionReadiness,
  spaUnlocked,
  currentMission,
  currentTask,
  attempt,
  learningPath,
  support,
  teachingBlocks,
  weakSkills,
  improvingSkills,
  retentionNeeded,
  transferNeeded,
  improvingSkillsAvailable,
  retentionSignalPresent,
  transferSignalPresent,
  nextMission,
  hasActiveSession,
  hasPlan,
  hasBlueprint,
  practiceWithAlexAvailable,
  todayMissions,
  todaySteps,
  todaySessionPhase,
  nextRecommendation,
  returningFromAlex,
  expectedOutcome,
  objectives,
  planSummary,
  lessonTitle,
  currentActivityTitle,
  currentActivityInstructions,
  currentActivityKind,
  activitiesTotal,
  activitiesCompleted,
  activitiesRemaining,
  liveExecutionReady,
  canContinueActivity,
  loadJourney,
  startSession,
  continueActivity,
  prepareForLiveAlex,
  onLiveSessionEnded,
  clearReturningFromAlex,
  clearSessionOutcome,
  clearError,
} = useSpeakingJourney()

const {
  phase: promoPhase,
  homeState: promoHomeState,
  status: promoStatus,
  statusLoading: promoStatusLoading,
  statusError: promoStatusError,
  assessmentLoading: promoAssessmentLoading,
  assessmentError: promoAssessmentError,
  available: promoAvailable,
  spaUnlocked: promoSpaUnlocked,
  message: promoMessage,
  targetCefr: promoTargetCefr,
  sourceCefr: promoSourceCefr,
  estimatedDurationSeconds: promoEstimatedDuration,
  taskCount: promoTaskCount,
  hasInteractionGaps: promoHasInteractionGaps,
  currentTask: promoCurrentTask,
  completedTaskCount: promoCompletedCount,
  remainingTaskCount: promoRemainingCount,
  sessionLoading: promoSessionLoading,
  sessionError: promoSessionError,
  submitLoading: promoSubmitLoading,
  submitError: promoSubmitError,
  lastSubmit: promoLastSubmit,
  actionLoading: promoActionLoading,
  result: promoResult,
  resultLoading: promoResultLoading,
  resultError: promoResultError,
  canRetryProjection: promoCanRetry,
  canPromoteOfficial: promoCanPromote,
  officialPromoted: promoOfficialPromoted,
  promotionResult: promoPromotionResult,
  promoteLoading: promoPromoteLoading,
  promoteError: promoPromoteError,
  loadStatus: loadPromoStatus,
  openIntro: promoOpenIntro,
  beginTasks: promoBeginTasks,
  resumeAssessment: promoResume,
  submitCurrentTask: promoSubmitTask,
  abandonAssessment: promoAbandon,
  retryAssessment: promoRetry,
  viewResult: promoViewResult,
  promoteOfficial: promoPromoteOfficial,
  backToHome: promoBackHome,
} = useSpeakingPromotion()

const {
  starting: learningStarting,
  error: learningPackageError,
  startLearning,
  packageId: ensuredPackageId,
  clear: clearLearningPackage,
} = useSpeakingLearningPackage()

const {
  loading: lessonLoading,
  advancing: lessonAdvancing,
  error: lessonError,
  packageData: lessonPackage,
  constraintsSummary: lessonConstraints,
  state: lessonState,
  sectionProgress: lessonProgress,
  currentSection: lessonSection,
  readyForDiscussion: lessonReadyForDiscussion,
  openLesson,
  loadActive: loadActiveLesson,
  advance: advanceLesson,
  markVocab: markLessonVocab,
  markBlock: markLessonBlock,
  completeMiniPrep: completeLessonMiniPrep,
  hydrate: hydrateLesson,
  clear: clearLessonRuntime,
} = useSpeakingLessonRuntime()

const {
  loading: discussionLoading,
  submitting: discussionSubmitting,
  advancing: discussionAdvancing,
  error: discussionError,
  draft: discussionDraft,
  lastAudio: discussionLastAudio,
  state: discussionState,
  packageTitle: discussionPackageTitle,
  packageSnippet: discussionPackageSnippet,
  currentStep: discussionCurrentStep,
  turns: discussionTurns,
  phase: discussionPhase,
  completed: discussionCompleted,
  readyForAlex: discussionReadyForAlex,
  canAdvance: discussionCanAdvance,
  stepsTotal: discussionStepsTotal,
  stepIndex: discussionStepIndex,
  progressPercent: discussionProgressPercent,
  openDiscussion,
  loadActive: loadActiveDiscussion,
  submit: submitDiscussion,
  submitVoice: submitDiscussionVoice,
  advance: advanceDiscussion,
  clear: clearDiscussion,
} = useSpeakingDiscussion()

const {
  mode: sceneVoiceMode,
  lastHeard: sceneVoiceLastHeard,
  prime: primeSceneVoice,
  startRecording: startSceneRecording,
  stopRecordingAndRespond: stopSceneRecordingAndRespond,
  playTutorAudio,
  stop: stopSceneVoice,
  isVoiceActive: isSceneVoiceActive,
  clearEphemeral: clearSceneVoiceEphemeral,
} = useScenePracticeVoice()

const sceneVoiceActive = computed(() => isSceneVoiceActive())

const TAB_VALUES = ['journey', 'lesson', 'discussion', 'alex', 'assessment']
const LEGACY_PRACTICE_MODES = ['conversation', 'shadowing', 'scenarios', 'exercises', 'practice']
const LEGACY_SCENE_MODES = ['bridge', 'prep', 'rehearsal', 'scene']

function tabFromQuery() {
  const mode = route.query.mode
  if (mode === 'live') return 'alex'
  if (mode === 'lesson' || mode === 'package') return 'lesson'
  if (mode === 'discussion') return 'discussion'
  // Retired Scene Practice modes land on Live Voice Discussion.
  if (LEGACY_SCENE_MODES.includes(mode)) return 'discussion'
  // Retired Additional Exercises modes land on the journey home.
  if (LEGACY_PRACTICE_MODES.includes(mode)) return 'journey'
  if (mode === 'assessment' || mode === 'promotion') return 'assessment'
  if (TAB_VALUES.includes(mode)) return mode
  return 'journey'
}

const tab = ref(tabFromQuery())

// Prime mic while Live Voice Discussion is active and not completed.
const sceneVoiceShouldRun = computed(
  () => tab.value === 'discussion' && Boolean(discussionState.value) && !discussionCompleted.value,
)

watch(sceneVoiceShouldRun, (shouldRun, wasRunning) => {
  if (shouldRun && !wasRunning) {
    clearSceneVoiceEphemeral()
    void primeSceneVoice()
  } else if (!shouldRun && wasRunning) {
    stopSceneVoice()
  }
})

watch(discussionLastAudio, (audio) => {
  if (audio?.b64 && tab.value === 'discussion') {
    void playTutorAudio(audio.b64, audio.mime)
  }
})

const pageLoading = ref(true)
const alexShellMounted = ref(tab.value === 'alex')
const ensuringLessonTab = ref(false)

const pageError = computed(() => journeyError.value || '')

const pageErrorDisplay = computed(() => {
  const kind = journeyErrorKind.value
  if (kind && kind !== 'message' && kind !== 'generic') {
    const key = `student.languages.speakingJourney.runtime.errors.${kind}`
    const translated = t(key)
    if (translated !== key) return translated
  }
  if (kind === 'generic' || !pageError.value) {
    return t('student.languages.speakingJourney.runtime.errors.generic')
  }
  return pageError.value
})

const friendlyErrorTitle = computed(() => {
  const kind = journeyErrorKind.value
  const key = `student.languages.speakingJourney.runtime.errorTitles.${kind || 'generic'}`
  const translated = t(key)
  return translated === key
    ? t('student.languages.speakingJourney.runtime.errorTitles.generic')
    : translated
})

function focusSpeakingTarget(selector) {
  requestAnimationFrame(() => {
    const el = document.querySelector(selector)
    if (el && typeof el.focus === 'function') el.focus({ preventScroll: false })
  })
}

function returnToLesson() {
  tab.value = 'journey'
  focusSpeakingTarget('[data-spk-focus="lesson"], [data-spk-focus="home"]')
}

const alexShellKey = computed(
  () => journeyLiveSessionId.value || `alex-idle-${tab.value}`,
)

function excludeStudentRole(characters, role) {
  const list = Array.isArray(characters) ? characters.filter(Boolean) : []
  const roleLower = String(role || '').toLowerCase()
  return list.filter((name) => String(name || '').toLowerCase() !== roleLower)
}

const discussionNeedsLesson = computed(
  () => !discussionState.value && !lessonReadyForDiscussion.value,
)
const discussionSpine = computed(() => discussionPackageSnippet.value?.story_spine || {})
const discussionCaseTitle = computed(
  () => discussionSpine.value?.title || discussionPackageTitle.value || lessonTitle.value || '',
)
const discussionCaseSetting = computed(() => discussionSpine.value?.setting || '')
const discussionCharacterHooks = computed(() =>
  excludeStudentRole(discussionSpine.value?.characters, ''),
)

// Live tab continuity — from discussion Educational Case (no Scene Practice brief).
const aliveStudentRole = computed(() => '')
const aliveCaseTitle = computed(() => discussionCaseTitle.value)
const aliveCharacters = computed(() => discussionCharacterHooks.value)
const aliveDecision = computed(() => discussionSpine.value?.decision_point || '')
const aliveVocabulary = computed(() => [])
const aliveGrammar = computed(() => [])

watch(tab, (value) => {
  if (value === 'alex') alexShellMounted.value = true
  const queryMode =
    value === 'alex'
      ? 'live'
      : value === 'assessment'
        ? 'assessment'
        : value === 'lesson'
          ? 'lesson'
          : value === 'discussion'
            ? 'discussion'
            : 'journey'
  if (route.query.mode !== queryMode) {
    router.replace({ query: { ...route.query, mode: queryMode } })
  }
  if (value === 'assessment') {
    loadPromoStatus().catch(() => {})
  }
  // Hydrated/opened lesson is authoritative until an explicit refresh
  // (open latest, restart, retry). Do not overwrite it on tab enter.
  if (value === 'lesson' && !lessonPackage.value) {
    ensureLessonTabContent().catch(() => {})
  }
  if (value === 'discussion') {
    ensureDiscussionSession().catch(() => {})
  }
})

onMounted(async () => {
  try {
    await loadAccess(true)
    if (access.value?.redirect) {
      router.push(access.value.redirect)
      return
    }
    await loadJourney({ force: true })
    if (tab.value === 'assessment') {
      await loadPromoStatus().catch(() => {})
    }
    if (tab.value === 'lesson') {
      await ensureLessonTabContent().catch(() => {})
    }
    // Dev skip-placement lands here with ?autostart=1 — start today's case without blocking the skip modal.
    if (String(route.query.autostart || '') === '1') {
      const { autostart: _drop, ...rest } = route.query
      router.replace({ query: rest }).catch(() => {})
      await onContinueLearning()
    }
  } catch (e) {
    if (!handleLanguageApiError(e, access.value)) {
      // journeyError already set by composable
    }
  } finally {
    pageLoading.value = false
  }
})

function enterLessonTab() {
  tab.value = 'lesson'
  focusSpeakingTarget('[data-spk-focus="lesson"], [data-spk-focus="home"]')
}

async function ensureLessonTabContent() {
  if (
    ensuringLessonTab.value ||
    lessonPackage.value ||
    lessonLoading.value ||
    learningStarting.value
  ) {
    return null
  }

  ensuringLessonTab.value = true
  try {
    const active = await loadActiveLesson()
    if (active?.package && active?.state?.package_id) {
      return active
    }
    return await startLessonPipeline()
  } catch (e) {
    if (learningPackageError.value || lessonError.value) {
      journeyError.value = learningPackageError.value || lessonError.value
    } else if (!handleLanguageApiError(e, access.value)) {
      journeyError.value = getErrorMessage(e, t('student.languages.speakingJourney.runtime.errors.generic'))
    }
    return null
  } finally {
    ensuringLessonTab.value = false
  }
}

function isNoLearningPackageError(err) {
  const detail = err?.response?.data?.detail
  const msg =
    typeof detail === 'string'
      ? detail
      : typeof detail?.message === 'string'
        ? detail.message
        : err?.message || ''
  return (
    /No Learning Package available to open/i.test(msg) ||
    /Learning package not found/i.test(msg) ||
    /no_package/i.test(String(detail || ''))
  )
}

async function onStartJourneySession() {
  clearSessionOutcome()
  try {
    // Integration: Start Learning → ensure package (E1) → open lesson (E2)
    await startLessonPipeline()
  } catch (e) {
    if (learningPackageError.value) {
      journeyError.value = learningPackageError.value
    } else if (!handleLanguageApiError(e, access.value)) {
      journeyError.value = getErrorMessage(e, t('student.languages.speakingJourney.runtime.errors.generic'))
    }
  }
}

/** Resume active lesson → open indexed package → else start-learning pipeline. */
async function startLessonPipeline({ forceRestartLesson = false } = {}) {
  clearLessonRuntime()
  clearLearningPackage()
  handleMissingDiscussionPackage()
  const started = await startLearning({
    authorMode: 'auto',
    useCache: true,
    forceRestartLesson,
  })
  if (started?.lesson) {
    hydrateLesson(started.lesson)
  } else {
    await openLesson({
      packageId: started?.package?.package_id || ensuredPackageId.value,
      forceRestart: forceRestartLesson,
    })
  }
  try {
    await loadJourney({ force: true })
  } catch {
    /* journey refresh best-effort */
  }
  enterLessonTab()
  return started
}

function handleMissingDiscussionPackage() {
  clearDiscussion()
  discussionError.value = ''
}

async function onContinueLearning() {
  clearError?.()
  clearSessionOutcome()
  try {
    const active = await loadActiveLesson()
    if (active?.package && active?.state?.package_id) {
      enterLessonTab()
      return
    }
    clearLearningPackage()

    const knownPackageId = ensuredPackageId.value || null
    if (knownPackageId) {
      try {
        await openLesson({ packageId: knownPackageId })
        enterLessonTab()
        return
      } catch (openErr) {
        if (!isNoLearningPackageError(openErr)) {
          throw openErr
        }
      }
    }

    await onStartJourneySession()
  } catch (e) {
    if (learningPackageError.value) {
      journeyError.value = learningPackageError.value
    } else if (lessonError.value) {
      journeyError.value =
        typeof lessonError.value === 'string'
          ? lessonError.value
          : getErrorMessage(e, t('student.languages.speakingJourney.runtime.errors.generic'))
    } else if (!handleLanguageApiError(e, access.value)) {
      journeyError.value = getErrorMessage(e, t('student.languages.speakingJourney.runtime.errors.generic'))
    }
  }
}

async function enterDiscussionFromLesson() {
  tab.value = 'discussion'
  await ensureDiscussionSession({ forceOpen: true })
}

/**
 * Resume active Live Voice Discussion, or open one once the lesson is ready.
 * Never maps "finish the lesson first" into a fake error banner.
 */
async function ensureDiscussionSession({ forceOpen = false, forceRestart = false } = {}) {
  discussionError.value = ''

  try {
    await loadActiveLesson()
  } catch {
    /* lesson may not be open yet */
  }
  const currentPackageId = lessonState.value?.package_id || ensuredPackageId.value || null

  if (!forceRestart) {
    try {
      const active = await loadActiveDiscussion()
      const activePackageId = active?.state?.package_id || null
      const samePackage = !currentPackageId || !activePackageId || activePackageId === currentPackageId
      if (active?.state && samePackage && (!active.state.completed || !forceOpen)) {
        // /active is text-only; re-open (no restart) once to attach Supertonic audio.
        if (!active.audio_b64 && !discussionLastAudio.value?.b64) {
          try {
            return await openDiscussion({
              packageId: activePackageId || undefined,
              forceRestart: false,
            })
          } catch (openErr) {
            if (isNoLearningPackageError(openErr)) {
              handleMissingDiscussionPackage()
              return null
            }
            return active
          }
        }
        return active
      }
      if (active?.state && !samePackage) {
        handleMissingDiscussionPackage()
      }
    } catch {
      /* no active discussion yet */
    }
  }

  if (!lessonReadyForDiscussion.value) {
    return null
  }

  const packageId = lessonState.value?.package_id || ensuredPackageId.value || null
  if (!packageId) {
    discussionError.value = ''
    return null
  }
  try {
    return await openDiscussion({
      packageId: packageId || undefined,
      forceRestart,
    })
  } catch (openErr) {
    if (isNoLearningPackageError(openErr)) {
      handleMissingDiscussionPackage()
    }
    return null
  }
}

function onDiscussionReplayAudio() {
  const audio = discussionLastAudio.value
  if (!audio?.b64) return
  void playTutorAudio(audio.b64, audio.mime)
}

async function onDiscussionStartRecording() {
  try {
    await startSceneRecording()
  } catch {
    /* voice composable falls back */
  }
}

async function onDiscussionStopRecording() {
  try {
    await stopSceneRecordingAndRespond((blob, opts) => submitDiscussionVoice(blob, opts))
  } catch {
    /* error on discussion composable */
  }
}

async function onContinueActivity() {
  try {
    await continueActivity()
  } catch {
    /* error set on composable */
  }
}

async function goLivePrepared() {
  try {
    alexShellMounted.value = true
    await prepareForLiveAlex()
    tab.value = 'alex'
    focusSpeakingTarget('.speaking-live-shell, .speaking-live-hero, .alex-continuity')
  } catch {
    /* error set on composable */
  }
}

async function onLiveEnded() {
  await onLiveSessionEnded()
  tab.value = 'journey'
  focusSpeakingTarget('[data-spk-focus="reflection"], [data-spk-focus="lesson"], [data-spk-focus="home"]')
}

async function retryJourneyLoad() {
  clearError?.()
  try {
    await loadJourney({ force: true })
  } catch {
    /* error set on composable */
  }
}

async function onPromoOpenIntro() {
  try {
    await promoOpenIntro()
  } catch {
    /* error set on composable */
  }
}

async function onPromoBeginTasks() {
  try {
    await promoBeginTasks()
  } catch {
    /* error set on composable */
  }
}

async function onPromoResume() {
  try {
    await promoResume()
  } catch {
    /* error set on composable */
  }
}

async function onPromoSubmitTask(payload) {
  try {
    await promoSubmitTask(payload || {})
  } catch {
    /* error set on composable */
  }
}

async function onPromoAbandon() {
  try {
    await promoAbandon()
  } catch {
    /* error set on composable */
  }
}

async function onPromoRetry() {
  try {
    await promoRetry()
  } catch {
    /* error set on composable */
  }
}

async function onPromoViewResult() {
  try {
    await promoViewResult()
  } catch {
    /* error set on composable */
  }
}

async function onPromoOfficial() {
  try {
    await promoPromoteOfficial()
    try {
      await loadJourney({ force: true })
    } catch {
      /* journey error set on composable */
    }
  } catch {
    /* error set on composable */
  }
}

function onPromoBackHome() {
  promoBackHome()
}

async function onPromoBackToJourney() {
  promoBackHome()
  tab.value = 'journey'
  focusSpeakingTarget('[data-spk-focus="home"]')
}

async function onLessonAdvance() {
  try {
    await advanceLesson()
    if (lessonReadyForDiscussion.value) {
      await enterDiscussionFromLesson()
    }
  } catch {
    /* error on composable */
  }
}

async function onLessonMarkVocab(id) {
  try {
    await markLessonVocab(id)
  } catch {
    /* error on composable */
  }
}

async function onLessonMarkBlock(id) {
  try {
    await markLessonBlock(id)
  } catch {
    /* error on composable */
  }
}

async function onLessonMiniPrep() {
  try {
    await completeLessonMiniPrep()
  } catch {
    /* error on composable */
  }
}

async function onLessonOpenLatest() {
  try {
    clearLessonRuntime()
    clearLearningPackage()
    await startLessonPipeline()
  } catch (e) {
    journeyError.value =
      learningPackageError.value ||
      lessonError.value ||
      getErrorMessage(e, t('student.languages.speakingJourney.runtime.errors.generic'))
  }
}

async function onLessonRestart() {
  try {
    clearLessonRuntime()
    clearLearningPackage()
    await startLessonPipeline({ forceRestartLesson: true })
  } catch (e) {
    journeyError.value =
      learningPackageError.value ||
      lessonError.value ||
      getErrorMessage(e, t('student.languages.speakingJourney.runtime.errors.generic'))
  }
}

async function onLessonRetry() {
  try {
    await loadActiveLesson()
  } catch {
    try {
      await startLessonPipeline()
    } catch (e) {
      journeyError.value =
        learningPackageError.value ||
        lessonError.value ||
        getErrorMessage(e, t('student.languages.speakingJourney.runtime.errors.generic'))
    }
  }
}

async function onStartDiscussionFromLesson() {
  if (!lessonReadyForDiscussion.value) {
    enterLessonTab()
    return
  }
  await enterDiscussionFromLesson()
}

async function onDiscussionOpen() {
  await ensureDiscussionSession({ forceOpen: true })
}

async function onDiscussionSubmit() {
  try {
    await submitDiscussion()
  } catch {
    /* error on composable */
  }
}

async function onDiscussionAdvance() {
  try {
    await advanceDiscussion()
  } catch {
    /* error on composable */
  }
}

async function onDiscussionRestart() {
  await ensureDiscussionSession({ forceOpen: true, forceRestart: true })
}

async function onDiscussionRetry() {
  await ensureDiscussionSession({ forceOpen: true })
}

</script>

<style scoped>
.page-container {
  max-width: 1100px;
  margin: 0 auto;
}
.english-island {
  unicode-bidi: isolate;
}
.speaking-tabs {
  direction: rtl;
}
.speaking-tabs :deep(.v-btn),
.speaking-tabs :deep(.v-tab) {
  text-transform: none;
  letter-spacing: 0;
}
</style>
