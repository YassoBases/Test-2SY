<template>
  <div class="page-container slide-up-enter-active">
    <LanguageModuleTabs />

    <PageHeader
      compact
      eyebrow="Learn languages"
      eyebrow-icon="mdi-headphones"
      :title="t('student.languages.listeningJourney.title')"
      :subtitle="t('student.languages.listeningJourney.subtitle')"
    />

    <v-alert v-if="journeyErrorComputed" type="error" variant="tonal" class="mb-4 rounded-lg">
      {{ journeyErrorComputed }}
    </v-alert>

    <LoadingState v-if="pageLoading" variant="cards" :count="2" class="mb-6" />

    <template v-else>
      <v-tabs v-model="tab" color="secondary" dir="rtl" class="listening-subtabs mb-4">
        <v-tab value="journey">{{ t('student.languages.listeningJourney.tabs.journey') }}</v-tab>
        <v-tab value="practice">{{ t('student.languages.listeningJourney.tabs.practice') }}</v-tab>
        <v-tab value="promotion">{{ t('student.languages.listeningJourney.tabs.promotion') }}</v-tab>
      </v-tabs>

      <v-window v-model="tab">
        <v-window-item value="journey">
          <div class="listening-journey" dir="rtl">
            <ListeningJourneyHero :journey="journey" />

            <div class="listening-cta glass-card mb-4">
              <div class="listening-cta__copy">
                <h3 class="listening-cta__title">{{ t('student.languages.listeningJourney.actions.startPractice') }}</h3>
                <p class="listening-cta__sub mb-0">{{ currentStepHint }}</p>
              </div>
              <div class="listening-cta__actions">
                <v-btn
                  color="secondary"
                  variant="flat"
                  size="large"
                  rounded="lg"
                  prepend-icon="mdi-play"
                  @click="onStartPractice"
                >
                  {{ t('student.languages.listeningJourney.actions.startPractice') }}
                </v-btn>
                <v-btn
                  v-if="canStartTest || hasActiveSession"
                  color="success"
                  variant="tonal"
                  size="large"
                  rounded="lg"
                  prepend-icon="mdi-stairs-up"
                  @click="tab = 'promotion'"
                >
                  {{
                    hasActiveSession
                      ? t('student.languages.listeningPromotion.actions.resumeTest')
                      : t('student.languages.listeningJourney.actions.openPromotion')
                  }}
                </v-btn>
              </div>
            </div>

            <SkillStagePathMap
              skill-label="Listening"
              skill-key="listening"
              :current-cefr="officialCefr"
              :current-stage="learningStage"
              current-reason="Complete more listening practice attempts."
              class="mb-4"
            />

            <ListeningGoalPanel
              :active-goal-id="activeGoalId"
              :saving="savingGoal"
              :goal-saved="goalSaved"
              @select="onSelectGoal"
            />

            <div class="listening-secondary">
              <ListeningJourneyPath :timeline-steps="timelineSteps" />
              <ListeningHowItWorks />
            </div>

            <ListeningGatePanel
              v-if="!canStartTest"
              :journey="journey"
              :can-start-test="canStartTest"
            />

            <ListeningPromotionHistoryCard :history-events="historyEvents" />
          </div>
        </v-window-item>

        <v-window-item value="practice">
          <ListeningPracticePanel
            ref="practiceRef"
            :active-lesson-id="activeLessonId"
            :active-lesson-lifecycle="activeLessonLifecycle"
            @submitted="onPracticeSubmitted"
            @lesson-ready="onLessonReady"
          />
        </v-window-item>

        <v-window-item value="promotion">
          <ListeningPromotionPanel
            :phase="phase"
            :journey="journey"
            :history-events="historyEvents"
            :status-loading="statusLoading"
            :can-start-test="canStartTest"
            :has-active-session="hasActiveSession"
            :session-loading="sessionLoading"
            :session="session"
            :mcq-questions="mcqQuestions"
            :expires-at-ms="expiresAtMs"
            :submit-loading="submitLoading"
            :submit-result="submitResult"
            :promote-loading="promoteLoading"
            :promotion-result="promotionResult"
            @start="onStartTest"
            @resume="onResumeTest"
            @submit="onSubmitTest"
            @cancel="resetToDashboard"
            @promote="onPromote"
            @back="resetToDashboard"
            @continue="onPromoteContinue"
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
import ListeningJourneyHero from '../../../components/language/ListeningJourneyHero.vue'
import SkillStagePathMap from '../../../components/language/SkillStagePathMap.vue'
import ListeningJourneyPath from '../../../components/language/ListeningJourneyPath.vue'
import ListeningHowItWorks from '../../../components/language/ListeningHowItWorks.vue'
import ListeningGatePanel from '../../../components/language/ListeningGatePanel.vue'
import ListeningGoalPanel from '../../../components/language/ListeningGoalPanel.vue'
import ListeningPracticePanel from '../../../components/language/ListeningPracticePanel.vue'
import ListeningPromotionPanel from '../../../components/language/ListeningPromotionPanel.vue'
import ListeningPromotionHistoryCard from '../../../components/language/ListeningPromotionHistoryCard.vue'
import { useLanguageAccess } from '../../../composables/useLanguageAccess.js'
import { useLanguageGate } from '../../../composables/useLanguageGate.js'
import { useListeningJourney } from '../../../composables/useListeningJourney.js'
import { celebrateBig } from '../../../composables/useCelebrate.js'
import { ROUTES } from '../../../constants/app.js'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const { access, loadAccess } = useLanguageAccess()
const { handleLanguageApiError } = useLanguageGate()

const {
  journey,
  journeyError,
  statusLoading,
  session,
  sessionLoading,
  submitResult,
  submitLoading,
  promotionResult,
  promoteLoading,
  phase,
  canStartTest,
  hasActiveSession,
  mcqQuestions,
  expiresAtMs,
  officialCefr,
  learningStage,
  activeGoalId,
  timelineSteps,
  historyEvents,
  activeLessonId,
  activeLessonLifecycle,
  savingGoal,
  goalSaved,
  loadJourney,
  refreshAfterPractice,
  selectGoal,
  beginTest,
  resumeActiveSession,
  submitTest,
  promote,
  resetToDashboard,
} = useListeningJourney()

const tab = ref('journey')
const pageLoading = ref(true)
const journeyErrorLocal = ref('')
const practiceRef = ref(null)
const testAnswers = ref({})

const journeyErrorComputed = computed(() => journeyErrorLocal.value || journeyError.value)

const currentStepHint = computed(() => {
  const narrative = journey.value?.narrative || {}
  return narrative.current_step_label || narrative.journey_headline || ''
})

watch(
  () => route.query.tab,
  (value) => {
    if (value === 'practice' || value === 'promotion' || value === 'journey') tab.value = value
  },
  { immediate: true },
)

watch(tab, (value) => {
  if (route.query.tab !== value) {
    router.replace({ path: ROUTES.STUDENT_LANGUAGES_LISTENING, query: { tab: value } })
  }
})

async function onSelectGoal(goalId) {
  try {
    await selectGoal(goalId)
  } catch (e) {
    handleLanguageApiError(e, null)
  }
}

async function onPracticeSubmitted() {
  await refreshAfterPractice()
}

function onLessonReady() {
  refreshAfterPractice()
}

async function onStartPractice() {
  tab.value = 'practice'
  await nextTickPracticeStart()
}

async function nextTickPracticeStart() {
  await new Promise((r) => setTimeout(r, 100))
  practiceRef.value?.startLesson?.()
}

async function onStartTest() {
  testAnswers.value = {}
  try {
    await beginTest()
  } catch (e) {
    handleLanguageApiError(e, null)
  }
}

async function onResumeTest() {
  testAnswers.value = {}
  try {
    await resumeActiveSession()
  } catch (e) {
    handleLanguageApiError(e, null)
  }
}

async function onSubmitTest(answers) {
  try {
    await submitTest(answers || testAnswers.value)
  } catch (e) {
    handleLanguageApiError(e, null)
  }
}

async function onPromote() {
  try {
    await promote()
    celebrateBig()
  } catch (e) {
    handleLanguageApiError(e, null)
  }
}

function onPromoteContinue() {
  resetToDashboard()
  tab.value = 'practice'
}

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
      journeyErrorLocal.value = e?.message || 'Could not load listening journey'
    }
  } finally {
    pageLoading.value = false
  }
})
</script>

<style scoped>
.page-container {
  max-width: 1100px;
  margin: 0 auto;
  padding-bottom: 2rem;
}

.listening-subtabs {
  direction: rtl;
}

.listening-subtabs :deep(.v-tab) {
  text-transform: none;
  letter-spacing: 0;
}

.listening-journey {
  display: grid;
  gap: 0;
}

.listening-cta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem 1.2rem;
}

.listening-cta__title {
  font-size: 1.05rem;
  font-weight: 700;
  margin: 0 0 0.2rem;
}

.listening-cta__sub {
  font-size: 0.8125rem;
  color: rgba(var(--v-theme-on-surface), 0.55);
}

.listening-cta__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem;
}

.listening-secondary {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

@media (max-width: 900px) {
  .listening-secondary {
    grid-template-columns: 1fr;
  }
}
</style>
