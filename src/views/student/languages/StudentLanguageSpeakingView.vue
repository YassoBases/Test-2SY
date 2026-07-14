<template>
  <div class="page-container slide-up-enter-active">
    <PageHeader
      :eyebrow="t('student.languages.speakingJourney.page.eyebrow')"
      eyebrow-icon="mdi-microphone"
      :title="t('student.languages.speakingJourney.page.title')"
      :subtitle="t('student.languages.speakingJourney.page.subtitle')"
    />
    <LanguageModuleTabs />

    <v-alert v-if="pageError" type="error" variant="tonal" class="mb-4 rounded-lg" role="alert">
      {{ pageError }}
    </v-alert>

    <LoadingState v-if="pageLoading" variant="cards" :count="2" class="mb-6" />

    <template v-else>
      <v-tabs
        v-model="tab"
        color="primary"
        class="mb-4 speaking-tabs"
        show-arrows
        density="comfortable"
      >
        <v-tab value="journey">{{ t('student.languages.speakingJourney.tabs.journey') }}</v-tab>
        <v-tab value="alex">{{ t('student.languages.speakingJourney.tabs.alex') }}</v-tab>
        <v-tab value="practice">{{ t('student.languages.speakingJourney.tabs.practice') }}</v-tab>
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
            :learning-path="learningPath"
            :next-mission="nextMission"
            :weak-skills="weakSkills"
            :improving-skills="improvingSkills"
            :retention-needed="retentionNeeded"
            :transfer-needed="transferNeeded"
            :today-missions="todayMissions"
            :has-active-session="hasActiveSession"
            :practice-with-alex-available="practiceWithAlexAvailable"
            :starting="starting"
            :advancing="advancing"
            :preparing-live="preparingLive"
            :session-outcome="sessionOutcome"
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
          />
        </v-window-item>

        <v-window-item value="alex">
          <v-alert
            v-if="!liveExecutionReady && !journeyLiveSessionId"
            type="info"
            variant="tonal"
            class="mb-4 rounded-lg"
            role="status"
          >
            {{ t('student.languages.speakingJourney.alex.needSession') }}
            <template #append>
              <v-btn variant="text" size="small" :loading="preparingLive" @click="goLivePrepared">
                {{ t('student.languages.speakingJourney.actions.talkAlex') }}
              </v-btn>
            </template>
          </v-alert>
          <LanguageSpeakingLiveShell
            :initial-task-prompt="liveTaskPrompt"
            :journey-live-session-id="journeyLiveSessionId"
            @session-ended="onLiveEnded"
          />
        </v-window-item>

        <v-window-item value="practice">
          <v-btn-toggle
            v-model="practiceMode"
            mandatory
            divided
            density="comfortable"
            color="primary"
            class="mb-4 flex-wrap"
            aria-label="practice modes"
          >
            <v-btn value="conversation" size="small">
              {{ t('student.languages.speakingJourney.practice.conversation') }}
            </v-btn>
            <v-btn value="shadowing" size="small">
              {{ t('student.languages.speakingJourney.practice.shadowing') }}
            </v-btn>
            <v-btn value="scenarios" size="small">
              {{ t('student.languages.speakingJourney.practice.scenarios') }}
            </v-btn>
            <v-btn value="exercises" size="small">
              {{ t('student.languages.speakingJourney.practice.exercises') }}
            </v-btn>
          </v-btn-toggle>

          <LanguageSpeakingConversationPanel v-if="practiceMode === 'conversation'" />
          <LanguageShadowingPanel v-else-if="practiceMode === 'shadowing'" />
          <LanguageScenariosPanel v-else-if="practiceMode === 'scenarios'" />

          <template v-else>
            <LoadingState v-if="exercisesLoading" variant="cards" :count="2" />
            <v-row v-else>
              <v-col cols="12" md="4">
                <v-list density="comfortable">
                  <v-list-item
                    v-for="p in prompts"
                    :key="p.id"
                    :active="selectedId === p.id"
                    rounded="lg"
                    @click="selectPrompt(p.id)"
                  >
                    <v-list-item-title>{{ p.title }}</v-list-item-title>
                  </v-list-item>
                </v-list>
                <EmptyState
                  v-if="!prompts.length"
                  compact
                  preset="languageExercise"
                />
              </v-col>
              <v-col cols="12" md="8">
                <EmptyState
                  v-if="!selectedId && prompts.length"
                  compact
                  icon="mdi-cursor-default-click-outline"
                  :title="t('student.languages.speaking.selectPrompt')"
                  :description="t('student.languages.speakingJourney.practice.chooseExercise')"
                />
                <v-card v-else-if="prompt" class="glass-card pa-6" variant="flat">
                  <div class="text-h6 mb-2 english-island" dir="ltr">{{ prompt.prompt }}</div>
                  <div class="text-caption mb-3">
                    {{ t('student.languages.speaking.minimumSeconds', { seconds: prompt.min_seconds }) }}
                  </div>
                  <div class="d-flex gap-2 mb-4 flex-wrap">
                    <v-btn color="error" variant="tonal" :disabled="recording" @click="startRec">
                      {{ t('student.languages.speaking.startRecording') }}
                    </v-btn>
                    <v-btn color="secondary" variant="flat" :disabled="!recording" @click="stopRec">
                      {{ t('student.languages.speaking.stopRecording') }}
                    </v-btn>
                    <v-btn
                      color="primary"
                      variant="tonal"
                      :loading="submitting"
                      :disabled="!canSubmit"
                      @click="submit"
                    >
                      {{ t('student.languages.common.submit') }}
                    </v-btn>
                  </div>
                  <v-alert
                    v-if="durationSeconds > 0 && prompt && durationSeconds < prompt.min_seconds"
                    type="warning"
                    variant="tonal"
                    density="comfortable"
                    class="mb-3 rounded-lg"
                    dir="ltr"
                  >
                    {{ minSecondsRequiredMessage(prompt.min_seconds) }}
                  </v-alert>
                  <audio v-if="playbackUrl" :src="playbackUrl" controls class="w-100 mb-4" />
                  <v-alert v-if="result" :type="result.passed ? 'success' : 'warning'" variant="tonal">
                    {{
                      result.passed
                        ? t('student.languages.speakingJourney.practice.exerciseDone')
                        : t('student.languages.speakingJourney.practice.exerciseSubmitted')
                    }}
                  </v-alert>
                  <v-card
                    v-if="result && (result.transcript || result.reply || result.correction_text)"
                    variant="tonal"
                    color="secondary"
                    class="mt-4 pa-4 rounded-lg"
                    dir="ltr"
                  >
                    <div class="text-subtitle-2 mb-2">{{ t('student.languages.speakingJourney.practice.aiFeedback') }}</div>
                    <div v-if="result.transcript" class="mb-3">
                      <div class="text-caption text-medium-emphasis">{{ t('student.languages.speakingJourney.practice.heard') }}</div>
                      <div class="text-body-2">{{ result.transcript }}</div>
                    </div>
                    <div v-if="result.reply" class="mb-3">
                      <div class="text-caption text-medium-emphasis">{{ t('student.languages.speakingJourney.practice.tutorReply') }}</div>
                      <div class="text-body-2">{{ result.reply }}</div>
                      <audio v-if="result.reply_audio_url" :src="result.reply_audio_url" controls class="w-100 mt-2" />
                    </div>
                    <LanguageSpeakingCorrectionBlock
                      v-if="speakingCorrection"
                      :display="speakingCorrection"
                      :weak-words="speakingWeakWords"
                      class="mt-2"
                    />
                  </v-card>
                </v-card>
              </v-col>
            </v-row>
          </template>
        </v-window-item>

        <v-window-item value="assessment">
          <SpeakingPromotionPanel
            :status="promoStatus"
            :status-loading="promoStatusLoading"
            :status-error="promoStatusError"
            :blueprint="promoBlueprint"
            :blueprint-loading="promoBlueprintLoading"
            :blueprint-error="promoBlueprintError"
            :available="promoAvailable"
            :spa-unlocked="promoSpaUnlocked"
            :message="promoMessage"
            :source-cefr="promoSourceCefr"
            :target-cefr="promoTargetCefr"
            :estimated-duration-seconds="promoEstimatedDuration"
            :tasks="promoTasks"
            :has-interaction-gaps="promoHasInteractionGaps"
            @preview="onPreviewAssessment"
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
import EmptyState from '../../../components/common/EmptyState.vue'
import LanguageModuleTabs from '../../../components/language/LanguageModuleTabs.vue'
import LanguageSpeakingConversationPanel from '../../../components/language/LanguageSpeakingConversationPanel.vue'
import LanguageSpeakingLiveShell from '../../../components/language/LanguageSpeakingLiveShell.vue'
import LanguageShadowingPanel from '../../../components/language/LanguageShadowingPanel.vue'
import LanguageScenariosPanel from '../../../components/language/LanguageScenariosPanel.vue'
import LanguageSpeakingCorrectionBlock from '../../../components/language/LanguageSpeakingCorrectionBlock.vue'
import SpeakingJourneyPanel from '../../../components/language/SpeakingJourneyPanel.vue'
import SpeakingPromotionPanel from '../../../components/language/SpeakingPromotionPanel.vue'
import { fetchSpeakingPrompt, fetchSpeakingPrompts, submitSpeakingPractice, uploadSpeakingPractice } from '../../../api/language.js'
import { useLanguageGate } from '../../../composables/useLanguageGate.js'
import { useLanguageAccess } from '../../../composables/useLanguageAccess.js'
import { useSpeakingJourney } from '../../../composables/useSpeakingJourney.js'
import { useSpeakingPromotion } from '../../../composables/useSpeakingPromotion.js'
import { minSecondsRequiredMessage } from '../../../utils/languageValidation.js'

const { t } = useI18n()
const router = useRouter()
const route = useRoute()
const { access, loadAccess } = useLanguageAccess()
const { handleLanguageApiError, getErrorMessage } = useLanguageGate()

const {
  loading: journeyLoading,
  error: journeyError,
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
  teachingBlocks,
  weakSkills,
  improvingSkills,
  retentionNeeded,
  transferNeeded,
  nextMission,
  hasActiveSession,
  practiceWithAlexAvailable,
  todayMissions,
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
} = useSpeakingJourney()

const {
  status: promoStatus,
  statusLoading: promoStatusLoading,
  statusError: promoStatusError,
  blueprint: promoBlueprint,
  blueprintLoading: promoBlueprintLoading,
  blueprintError: promoBlueprintError,
  available: promoAvailable,
  spaUnlocked: promoSpaUnlocked,
  message: promoMessage,
  targetCefr: promoTargetCefr,
  sourceCefr: promoSourceCefr,
  estimatedDurationSeconds: promoEstimatedDuration,
  tasks: promoTasks,
  hasInteractionGaps: promoHasInteractionGaps,
  loadStatus: loadPromoStatus,
  previewAssessment,
} = useSpeakingPromotion()

const TAB_VALUES = ['journey', 'alex', 'practice', 'assessment']
const PRACTICE_VALUES = ['conversation', 'shadowing', 'scenarios', 'exercises']

function tabFromQuery() {
  const mode = route.query.mode
  if (mode === 'live') return 'alex'
  if (PRACTICE_VALUES.includes(mode)) return 'practice'
  if (mode === 'assessment' || mode === 'promotion') return 'assessment'
  if (TAB_VALUES.includes(mode)) return mode
  return 'journey'
}

function practiceFromQuery() {
  const mode = route.query.mode
  return PRACTICE_VALUES.includes(mode) ? mode : 'conversation'
}

const tab = ref(tabFromQuery())
const practiceMode = ref(practiceFromQuery())
const pageLoading = ref(true)
const prompts = ref([])
const exercisesLoading = ref(false)
const selectedId = ref(null)
const prompt = ref(null)
const recording = ref(false)
const submitting = ref(false)
const result = ref(null)
const mediaObjectId = ref(null)
const playbackUrl = ref(null)
const durationSeconds = ref(0)
let mediaRecorder = null
let chunks = []
let startedAt = 0

const pageError = computed(() => journeyError.value || '')

const speakingWeakWords = computed(() =>
  (result.value?.weak_words || result.value?.pronunciation?.words || [])
    .filter((w) => (typeof w === 'string' ? w : w?.weak))
    .map((w) => (typeof w === 'string' ? w : w?.word)),
)
const speakingCorrection = computed(() => {
  const r = result.value
  if (!r || !r.correction_text || r.correction_text === r.transcript) return null
  const explanation = (r.grammar_errors || [])
    .map((e) => e.message)
    .filter(Boolean)
    .slice(0, 3)
    .join(' ')
  return {
    has_errors: true,
    your_sentence: r.transcript || '',
    corrected_sentence: r.correction_text || '',
    explanation,
  }
})

const canSubmit = computed(() => {
  if (!mediaObjectId.value || !prompt.value) return false
  return durationSeconds.value >= prompt.value.min_seconds
})

watch(tab, (value) => {
  const queryMode =
    value === 'alex'
      ? 'live'
      : value === 'practice'
        ? practiceMode.value
        : value === 'assessment'
          ? 'assessment'
          : 'journey'
  if (route.query.mode !== queryMode) {
    router.replace({ query: { ...route.query, mode: queryMode } })
  }
  if (value === 'assessment') {
    loadPromoStatus().catch(() => {})
  }
})

watch(practiceMode, (value) => {
  if (tab.value === 'practice' && route.query.mode !== value) {
    router.replace({ query: { ...route.query, mode: value } })
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
    exercisesLoading.value = true
    try {
      const res = await fetchSpeakingPrompts()
      prompts.value = res.prompts || []
    } catch (e) {
      if (!handleLanguageApiError(e, access.value)) {
        // Non-fatal for journey/home
      }
    } finally {
      exercisesLoading.value = false
    }
    if (tab.value === 'assessment') {
      await loadPromoStatus().catch(() => {})
    }
  } catch (e) {
    if (!handleLanguageApiError(e, access.value)) {
      // journeyError already set by composable
    }
  } finally {
    pageLoading.value = false
  }
})

async function onStartJourneySession() {
  try {
    await startSession()
  } catch {
    /* error set on composable */
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
    await prepareForLiveAlex()
    tab.value = 'alex'
  } catch {
    /* error set on composable */
  }
}

async function onLiveEnded() {
  await onLiveSessionEnded()
  tab.value = 'journey'
}

async function onPreviewAssessment() {
  try {
    await previewAssessment()
  } catch {
    /* error set on composable */
  }
}

async function selectPrompt(id) {
  selectedId.value = id
  result.value = null
  mediaObjectId.value = null
  playbackUrl.value = null
  try {
    prompt.value = await fetchSpeakingPrompt(id)
    if (prompt.value.progress?.public_url) {
      playbackUrl.value = prompt.value.progress.public_url
      mediaObjectId.value = prompt.value.progress.media_object_id
    }
  } catch (e) {
    if (!handleLanguageApiError(e, access.value)) {
      journeyError.value = getErrorMessage(e, t('student.languages.speaking.errors.loadPrompt'))
    }
  }
}

async function startRec() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    chunks = []
    mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' })
    mediaRecorder.ondataavailable = (e) => chunks.push(e.data)
    mediaRecorder.onstop = async () => {
      stream.getTracks().forEach((tr) => tr.stop())
      const blob = new Blob(chunks, { type: 'audio/webm' })
      durationSeconds.value = Math.max(1, Math.round((Date.now() - startedAt) / 1000))
      playbackUrl.value = URL.createObjectURL(blob)
      const up = await uploadSpeakingPractice(selectedId.value, blob)
      mediaObjectId.value = up.media_object_id
      if (up.public_url) playbackUrl.value = up.public_url
    }
    startedAt = Date.now()
    mediaRecorder.start()
    recording.value = true
  } catch (e) {
    journeyError.value = getErrorMessage(e, t('student.languages.speaking.errors.microphone'))
  }
}

function stopRec() {
  if (mediaRecorder && recording.value) {
    mediaRecorder.stop()
    recording.value = false
  }
}

async function submit() {
  if (!selectedId.value || !mediaObjectId.value || !prompt.value) return
  if (durationSeconds.value < prompt.value.min_seconds) {
    journeyError.value = minSecondsRequiredMessage(prompt.value.min_seconds)
    return
  }
  submitting.value = true
  try {
    result.value = await submitSpeakingPractice(selectedId.value, {
      media_object_id: mediaObjectId.value,
      duration_seconds: durationSeconds.value,
    })
    const res = await fetchSpeakingPrompts()
    prompts.value = res.prompts || []
  } catch (e) {
    journeyError.value = getErrorMessage(e, t('student.languages.speaking.errors.submit'))
  } finally {
    submitting.value = false
  }
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
.speaking-tabs :deep(.v-btn) {
  text-transform: none;
  letter-spacing: 0;
}
</style>
