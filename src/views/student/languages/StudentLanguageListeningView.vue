<template>

  <div class="page-container slide-up-enter-active">

    <PageHeader

      eyebrow="Learn languages"

      eyebrow-icon="mdi-headphones"

      :title="t('student.languages.listeningJourney.title')"

      :subtitle="t('student.languages.listeningJourney.subtitle')"

    />

    <LanguageModuleTabs />



    <v-alert v-if="journeyErrorComputed" type="error" variant="tonal" class="mb-4 rounded-lg">{{ journeyErrorComputed }}</v-alert>



    <LoadingState v-if="pageLoading" variant="cards" :count="2" class="mb-6" />



    <template v-else>

      <v-tabs v-model="tab" color="secondary" class="mb-4">

        <v-tab value="journey">{{ t('student.languages.listeningJourney.tabs.journey') }}</v-tab>

        <v-tab value="practice">{{ t('student.languages.listeningJourney.tabs.practice') }}</v-tab>

        <v-tab value="promotion">{{ t('student.languages.listeningJourney.tabs.promotion') }}</v-tab>

      </v-tabs>



      <v-window v-model="tab">

        <v-window-item value="journey">

          <ListeningJourneyHero :journey="journey" />

          <ListeningJourneyPath :timeline-steps="timelineSteps" />

          <ListeningHowItWorks />

          <ListeningGatePanel

            v-if="!canStartTest"

            :journey="journey"

            :can-start-test="canStartTest"

          />

          <ListeningGoalPanel

            :active-goal-id="activeGoalId"

            :saving="savingGoal"

            :goal-saved="goalSaved"

            @select="onSelectGoal"

          />

          <ListeningPromotionHistoryCard :history-events="historyEvents" />

          <v-card class="cta-card pa-6 mt-2 mb-6" variant="flat">

            <div class="d-flex flex-wrap gap-3">

              <v-btn color="secondary" variant="flat" size="x-large" prepend-icon="mdi-play" class="px-8" @click="onStartPractice">

                {{ t('student.languages.listeningJourney.actions.startPractice') }}

              </v-btn>

              <v-btn

                v-if="canStartTest || hasActiveSession"

                color="success"

                variant="flat"

                size="x-large"

                prepend-icon="mdi-stairs-up"

                class="px-8"

                @click="tab = 'promotion'"

              >

                {{ hasActiveSession ? t('student.languages.listeningPromotion.actions.resumeTest') : t('student.languages.listeningJourney.actions.openPromotion') }}

              </v-btn>

            </div>

          </v-card>

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

.cta-card {

  border-radius: 20px;

  background: rgba(var(--v-theme-secondary), 0.06);

  border: 1px solid rgba(var(--v-theme-on-surface), 0.06);

}

</style>

