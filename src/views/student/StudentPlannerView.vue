<template>
  <div class="planner-page slide-up-enter-active">
    <PageHeader
      :eyebrow="t('student.planner.header.eyebrow')"
      eyebrow-icon="mdi-calendar-star"
      :title="t('student.planner.header.title')"
      :subtitle="t('student.planner.header.subtitle')"
      gradient-title
    >
      <template #actions>
        <v-btn
          color="secondary"
          variant="tonal"
          rounded="lg"
          :loading="generating"
          @click="onGenerate"
        >
          <v-icon start>mdi-auto-fix</v-icon>
          {{ t('student.planner.generateCta') }}
        </v-btn>
      </template>
    </PageHeader>

    <PlannerAiBanner :message="bannerMessage" />

    <PlannerAnalyticsRow
      :schedule="schedule"
      :profile="profile"
      :plan-stats="planStats"
      :streak="streak"
      :subject-analytics="subjectAnalytics"
    />

    <v-alert
      v-if="loadError"
      type="error"
      variant="tonal"
      class="mb-5 rounded-lg"
      closable
      @click:close="loadError = ''"
    >
      {{ loadError }}
    </v-alert>

    <section class="section-block mb-6">
      <div class="section-block__head">
        <h3 class="section-block__title">{{ t('student.planner.sections.weeklyPlan') }}</h3>
        <p class="section-block__subtitle mb-0">{{ t('student.planner.sections.weeklyPlanSubtitle') }}</p>
      </div>
      <PlannerWeeklyPlan :weekly-plan="weeklyPlan" @complete="onComplete" />
    </section>

    <v-row class="mb-6">
      <v-col cols="12" md="6">
        <section class="section-block">
          <div class="section-block__head">
            <h3 class="section-block__title">{{ t('student.planner.sections.subjectAnalysis') }}</h3>
            <p class="section-block__subtitle mb-0">{{ t('student.planner.sections.subjectAnalysisSubtitle') }}</p>
          </div>
          <PlannerSubjectStrength :subjects="subjectAnalytics" />
        </section>
      </v-col>
      <v-col cols="12" md="6">
        <section class="section-block">
          <div class="section-block__head">
            <h3 class="section-block__title">{{ t('student.planner.sections.recommendations') }}</h3>
            <p class="section-block__subtitle mb-0">{{ t('student.planner.sections.recommendationsSubtitle') }}</p>
          </div>
          <PlannerRecommendations :items="recommendations" />
        </section>
      </v-col>
    </v-row>

    <PlannerStudySections
      class="mb-6"
      :schedule="schedule"
      :reasoning="reasoning"
      :insights="insights"
      :recommendations="recommendations"
      :profile="profile"
      :life-events="lifeEvents"
      :courses="courses"
      @complete="onComplete"
    />

    <v-row>
      <v-col cols="12" lg="4" class="chat-col">
        <PlannerChatPanel
          :messages="chatHistory"
          :loading="chatting"
          @send="onChat"
        />
        <PlannerReasoningPanel :reasoning="reasoning" class="mt-4" />
        <PlannerEventCards :events="lifeEvents" class="mt-4" />
      </v-col>
      <v-col cols="12" lg="8">
        <PlannerWeeklyGrid
          :schedule="schedule"
          class="mb-4"
          @reorder="onReorder"
        />
        <PlannerCalendar
          :schedule="schedule"
          :loading="loading"
          @complete="onComplete"
        />
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import PageHeader from '../../components/common/PageHeader.vue'
import PlannerChatPanel from '../../components/planner/PlannerChatPanel.vue'
import PlannerCalendar from '../../components/planner/PlannerCalendar.vue'
import PlannerEventCards from '../../components/planner/PlannerEventCards.vue'
import PlannerReasoningPanel from '../../components/planner/PlannerReasoningPanel.vue'
import PlannerWeeklyGrid from '../../components/planner/PlannerWeeklyGrid.vue'
import PlannerAnalyticsRow from '../../components/planner/PlannerAnalyticsRow.vue'
import PlannerAiBanner from '../../components/planner/PlannerAiBanner.vue'
import PlannerStudySections from '../../components/planner/PlannerStudySections.vue'
import PlannerWeeklyPlan from '../../components/planner/PlannerWeeklyPlan.vue'
import PlannerSubjectStrength from '../../components/planner/PlannerSubjectStrength.vue'
import PlannerRecommendations from '../../components/planner/PlannerRecommendations.vue'
import { usePlanner } from '../../composables/usePlanner.js'
import { fetchStudentDashboard } from '../../api/studentCourses.js'
import { isApiMode } from '../../utils/session.js'

const { t } = useI18n()
const {
  loading,
  generating,
  chatting,
  loadError,
  profile,
  lifeEvents,
  schedule,
  chatHistory,
  reasoning,
  insights,
  weeklyPlan,
  subjectAnalytics,
  recommendations,
  streak,
  planStats,
  load,
  generatePlan,
  sendMessage,
  completeSession,
} = usePlanner()

const bannerMessage = ref(t('student.planner.banner.default'))
const courses = ref([])

onMounted(async () => {
  await load()
  if (recommendations.value[0]?.text) {
    bannerMessage.value = recommendations.value[0].text
  }
  if (isApiMode()) {
    try {
      const dash = await fetchStudentDashboard()
      courses.value = dash.courses || []
    } catch {
      courses.value = []
    }
  }
})

async function onGenerate() {
  await generatePlan()
  if (recommendations.value[0]?.text) {
    bannerMessage.value = recommendations.value[0].text
  }
}

async function onChat(message) {
  const data = await sendMessage(message)
  if (data?.reasoning?.length) {
    bannerMessage.value = data.reasoning[0]
  }
  await load()
}

async function onComplete(slotId) {
  await completeSession(slotId)
}

async function onReorder() {
  await generatePlan()
  bannerMessage.value = t('student.planner.banner.reordered')
}
</script>

<style scoped>
.planner-page {
  max-width: 1400px;
  margin-inline: auto;
}

.chat-col {
  position: sticky;
  top: 88px;
  align-self: flex-start;
}

@media (max-width: 1280px) {
  .chat-col {
    position: static;
  }
}
</style>
