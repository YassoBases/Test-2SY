<template>
  <div class="page-container slide-up-enter-active">
    <PageHeader
      eyebrow="Learn languages"
      eyebrow-icon="mdi-pencil"
      :title="t('student.languages.writingJourney.title')"
      :subtitle="t('student.languages.writingJourney.subtitle')"
    />
    <LanguageModuleTabs />

    <v-alert v-if="pageError" type="error" variant="tonal" class="mb-4 rounded-lg">{{ pageError }}</v-alert>

    <LoadingState v-if="pageLoading" variant="cards" :count="2" class="mb-6" />

    <template v-else>
      <v-tabs v-model="tab" color="secondary" class="mb-4">
        <v-tab value="journey">{{ t('student.languages.writingJourney.tabs.journey') }}</v-tab>
        <v-tab value="practice">{{ t('student.languages.writingJourney.tabs.practice') }}</v-tab>
        <v-tab value="promotion">{{ t('student.languages.writingJourney.tabs.promotion') }}</v-tab>
      </v-tabs>

      <v-window v-model="tab">
        <v-window-item value="journey">
          <WritingJourneyHero
            :official-cefr="officialCefr"
            :active-goal-id="activeGoalId"
            :learning-stage-label="learningStageLabel"
            :learning-stage="learningStage"
            :readiness-score="readinessScore"
            :readiness-band="readinessBand"
            :estimated-lessons-remaining="estimatedLessonsRemaining"
            :primary-blockers="primaryBlockers"
            :can-start-wpa="canStartWpa"
            :progress-summary="progressSummary"
            :next-milestone="nextMilestone"
          />
          <SkillStagePathMap
            skill-label="Writing"
            skill-key="writing"
            :current-cefr="officialCefr"
            :current-stage="learningStage"
            current-reason="Complete more writing practice attempts."
            class="mb-4"
          />
          <WritingGoalPanel
            :active-goal-id="activeGoalId"
            :saving="savingGoal"
            :goal-saved="goalSaved"
            @select="onSelectGoal"
          />
          <v-card class="how-card pa-6 mb-4" variant="flat">
            <div class="d-flex align-center gap-2 mb-4">
              <v-icon color="secondary" size="28">mdi-map-marker-path</v-icon>
              <h3 class="text-h6 font-weight-bold mb-0">{{ t('student.languages.writingJourney.howItWorks.title') }}</h3>
            </div>
            <ol class="how-list">
              <li v-for="step in howSteps" :key="step">{{ step }}</li>
            </ol>
          </v-card>
          <v-card class="cta-card pa-6 mt-2 mb-6" variant="flat">
            <v-btn
              color="secondary"
              variant="flat"
              size="x-large"
              prepend-icon="mdi-pencil"
              class="px-8"
              @click="onStartPractice"
            >
              {{ t('student.languages.writingJourney.actions.startPractice') }}
            </v-btn>
          </v-card>
        </v-window-item>

        <v-window-item value="practice">
          <WritingPracticePanel
            ref="practiceRef"
            :active-goal-id="activeGoalId"
            @lesson-ready="onLessonReady"
            @completed="onLessonCompleted"
            @error="onPracticeError"
          />
        </v-window-item>

        <v-window-item value="promotion">
          <v-alert v-if="promotionStatusError" type="error" variant="tonal" class="mb-4">{{ promotionStatusError }}</v-alert>
          <v-alert v-if="promotionSessionError" type="error" variant="tonal" class="mb-4">{{ promotionSessionError }}</v-alert>
          <v-alert v-if="promotionSubmitError" type="error" variant="tonal" class="mb-4">{{ promotionSubmitError }}</v-alert>
          <v-alert v-if="promotionPromoteError" type="error" variant="tonal" class="mb-4">{{ promotionPromoteError }}</v-alert>
          <WritingPromotionPanel
            :phase="promotionPhase"
            :journey="journey"
            :status="promotionStatus"
            :can-start="canStartWpaTest"
            :has-active-session="hasActiveWpaSession"
            :session-loading="promotionSessionLoading"
            :session="promotionSession"
            :submitting="promotionSubmitLoading"
            :submit-result="promotionSubmitResult"
            :promoting="promotionPromoteLoading"
            :promotion-result="promotionApplyResult"
            @start="onStartWpa"
            @resume="onResumeWpa"
            @submit="onSubmitWpa"
            @cancel="onCancelWpa"
            @promote="onPromoteWriting"
            @back="onPromotionBack"
            @continue="onPromotionContinue"
            @practice="tab = 'practice'"
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
import WritingJourneyHero from '../../../components/language/WritingJourneyHero.vue'
import SkillStagePathMap from '../../../components/language/SkillStagePathMap.vue'
import WritingGoalPanel from '../../../components/language/WritingGoalPanel.vue'
import WritingPracticePanel from '../../../components/language/WritingPracticePanel.vue'
import WritingPromotionPanel from '../../../components/language/WritingPromotionPanel.vue'
import { useWritingJourney } from '../../../composables/useWritingJourney.js'
import { useWritingPromotion } from '../../../composables/useWritingPromotion.js'
import { useLanguageAccess } from '../../../composables/useLanguageAccess.js'
import { useLanguageGate } from '../../../composables/useLanguageGate.js'
import { getErrorMessage } from '../../../api/client.js'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const { access, loadAccess } = useLanguageAccess()
const { handleLanguageApiError } = useLanguageGate()

const {
  loading: journeyLoading,
  error: journeyError,
  journey,
  activeGoalId,
  officialCefr,
  learningStageLabel,
  learningStage,
  readinessScore,
  readinessBand,
  canStartWpa,
  primaryBlockers,
  progressSummary,
  nextMilestone,
  savingGoal,
  goalSaved,
  lastSession,
  loadJourney,
  selectGoal,
  recordSession,
  estimatedLessonsRemaining,
} = useWritingJourney()

const {
  status: promotionStatus,
  statusLoading: promotionStatusLoading,
  statusError: promotionStatusError,
  session: promotionSession,
  sessionLoading: promotionSessionLoading,
  sessionError: promotionSessionError,
  submitResult: promotionSubmitResult,
  submitLoading: promotionSubmitLoading,
  submitError: promotionSubmitError,
  promotionResult: promotionApplyResult,
  promoteLoading: promotionPromoteLoading,
  promoteError: promotionPromoteError,
  phase: promotionPhase,
  canStartTest: canStartWpaTest,
  hasActiveSession: hasActiveWpaSession,
  loadStatus: loadPromotionStatus,
  beginTest: beginWpa,
  resumeActiveSession: resumeWpa,
  submitTest: submitWpa,
  promote: promoteWriting,
  resetToDashboard: resetPromotionDashboard,
} = useWritingPromotion()

const tab = ref(route.query.tab === 'practice' ? 'practice' : route.query.tab === 'promotion' ? 'promotion' : 'journey')
const practiceRef = ref(null)
const pageError = ref('')

const pageLoading = computed(() => journeyLoading.value)

const howSteps = computed(() => [
  t('student.languages.writingJourney.howItWorks.step1'),
  t('student.languages.writingJourney.howItWorks.step2'),
  t('student.languages.writingJourney.howItWorks.step3'),
  t('student.languages.writingJourney.howItWorks.step4'),
])

watch(tab, (value) => {
  const queryTab = value === 'journey' ? undefined : value
  router.replace({ query: { ...route.query, tab: queryTab } })
  if (value === 'promotion') {
    loadPromotionStatus().catch(() => {})
  }
})

watch(
  () => route.query.tab,
  (value) => {
    tab.value = value === 'practice' ? 'practice' : value === 'promotion' ? 'promotion' : 'journey'
  },
)

onMounted(async () => {
  try {
    await loadAccess(true)
    if (access.value?.redirect) {
      router.push(access.value.redirect)
      return
    }
    await loadJourney()
  } catch (e) {
    if (!handleLanguageApiError(e, access.value)) {
      pageError.value = getErrorMessage(e, 'Unable to load writing')
    }
  }
})

async function onSelectGoal(goalId) {
  try {
    await selectGoal(goalId)
  } catch (e) {
    pageError.value = getErrorMessage(e, 'Could not save goal')
  }
}

function onStartPractice() {
  pageError.value = ''
  tab.value = 'practice'
  practiceRef.value?.startLesson?.()
}

function onLessonReady(lesson) {
  pageError.value = ''
  recordSession({
    title: lesson.mission_title || lesson.title,
    content_item_id: lesson.content_item_id,
    goal: lesson.goal,
  })
}

function onLessonCompleted(payload) {
  pageError.value = ''
  const lesson = payload?.lesson || payload
  recordSession({
    title: lesson?.mission_title || lesson?.title || 'Completed lesson',
    content_item_id: lesson?.content_item_id,
    completed: true,
  })
  loadJourney()
}

function onPracticeError(err) {
  pageError.value = getErrorMessage(err, 'Writing practice error')
}

async function onStartWpa() {
  try {
    await beginWpa()
  } catch (e) {
    pageError.value = getErrorMessage(e, 'Could not start WPA')
  }
}

async function onResumeWpa() {
  try {
    await resumeWpa()
  } catch (e) {
    pageError.value = getErrorMessage(e, 'Could not resume WPA')
  }
}

async function onSubmitWpa(submissions) {
  try {
    await submitWpa(submissions)
  } catch (e) {
    pageError.value = getErrorMessage(e, 'Could not submit WPA')
  }
}

function onCancelWpa() {
  resetPromotionDashboard()
}

async function onPromoteWriting() {
  try {
    await promoteWriting()
    await loadJourney()
  } catch (e) {
    pageError.value = getErrorMessage(e, 'Could not promote writing level')
  }
}

function onPromotionBack() {
  resetPromotionDashboard()
}

async function onPromotionContinue() {
  resetPromotionDashboard()
  await loadJourney()
  tab.value = 'journey'
}

watch(journeyError, (msg) => {
  if (msg) pageError.value = msg
})
</script>

<style scoped>
.page-container {
  max-width: 1100px;
  margin: 0 auto;
}
.how-card,
.cta-card {
  border-radius: 20px;
}
.how-list {
  margin: 0;
  padding-inline-start: 1.25rem;
}
.how-list li + li {
  margin-top: 0.5rem;
}
</style>
