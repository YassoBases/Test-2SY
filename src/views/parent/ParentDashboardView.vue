<template>
  <ParentPortalShell
    :title="t('parent.dashboard.title')"
    :subtitle="t('parent.dashboard.subtitle')"
    gradient-title
    :students="students"
    :selected-student-id="selectedStudentId"
    :student-context="studentContext"
    :has-students="hasStudents"
    :loading-students="loadingStudents"
    :students-error="studentsError"
    :linking="linking"
    :link-error="linkError"
    :link-success="linkSuccess"
    :loading="loading"
    :load-error="loadError"
    @select-student="selectStudent"
    @link="linkStudent"
    @clear-students-error="studentsError = ''"
    @clear-link-error="linkError = ''"
    @clear-link-success="linkSuccess = ''"
    @clear-load-error="loadError = ''"
  >
    <ChildSummaryCard :child="child" :stats="stats" class="mb-6" />

    <ParentLanguageSection v-if="languagePlacement" :data="languagePlacement" class="mb-6" />

    <ParentAiInsightSummaryCard
      :insight="latestAiInsight"
      :summary-line="aiSummaryLine"
      :loading="false"
      class="mb-6"
    />

    <ParentReportsSummaryCard class="mb-6" />

    <ParentSubjectsTeachersSummaryCard class="mb-6" />

    <ParentLessonProgressSummaryCard
      v-if="lessonProgress?.summary"
      :summary="lessonProgress.summary"
      class="mb-6"
    />

    <ParentPlannerSummaryCard
      v-if="planner?.commitment"
      :planner="planner"
      class="mb-6"
    />

    <ParentOverviewAlerts
      :alerts="overviewAlerts"
      class="mb-6"
    />

    <ParentNotesSection
      v-if="selectedStudentId"
      :student-id="selectedStudentId"
      class="mb-6"
    />

    <section class="mb-6">
      <div class="d-flex align-center gap-2 mb-4">
        <v-icon color="secondary">mdi-view-grid-outline</v-icon>
        <h3 class="text-h6 font-weight-bold mb-0">{{ t('parent.dashboard.sections') }}</h3>
      </div>
      <ParentQuickLinks />
    </section>

    <section>
      <div class="d-flex align-center justify-space-between mb-4 flex-wrap gap-2">
        <div class="d-flex align-center gap-2">
          <v-icon color="primary">mdi-timeline-text</v-icon>
          <h3 class="text-h6 font-weight-bold mb-0">{{ t('parent.dashboard.latestActivity') }}</h3>
        </div>
        <v-btn size="small" variant="tonal" :to="ROUTES.PARENT_NOTIFICATIONS">{{ t('parent.dashboard.fullLog') }}</v-btn>
      </div>
      <v-card class="glass-card pa-4 activity-panel" variant="flat">
        <ActivityFeedTimeline :items="latestActivity" :loading="false" />
      </v-card>
    </section>
  </ParentPortalShell>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import ParentPortalShell from '../../components/parent/portal/ParentPortalShell.vue'
import ParentQuickLinks from '../../components/parent/portal/ParentQuickLinks.vue'
import ParentLanguageSection from '../../components/parent/ParentLanguageSection.vue'
import ParentAiInsightSummaryCard from '../../components/parent/portal/ParentAiInsightSummaryCard.vue'
import ParentReportsSummaryCard from '../../components/parent/portal/ParentReportsSummaryCard.vue'
import ParentSubjectsTeachersSummaryCard from '../../components/parent/portal/ParentSubjectsTeachersSummaryCard.vue'
import ParentLessonProgressSummaryCard from '../../components/parent/portal/ParentLessonProgressSummaryCard.vue'
import ParentPlannerSummaryCard from '../../components/parent/portal/ParentPlannerSummaryCard.vue'
import ParentOverviewAlerts from '../../components/parent/portal/ParentOverviewAlerts.vue'
import ParentNotesSection from '../../components/parent/ParentNotesSection.vue'
import ChildSummaryCard from '../../components/parent/ChildSummaryCard.vue'
import ActivityFeedTimeline from '../../components/parent/ActivityFeedTimeline.vue'
import { useParentShell } from '../../composables/useParentShell.js'
import { useParentMonitor } from '../../composables/useParentMonitor.js'
import { useParentPageLoad } from '../../composables/useParentPageLoad.js'
import { ROUTES } from '../../constants/app.js'

const { t } = useI18n()

const shell = useParentShell()
const {
  students,
  selectedStudentId,
  studentContext,
  hasStudents,
  loadingStudents,
  studentsError,
  linking,
  linkError,
  linkSuccess,
  selectStudent,
  linkStudent,
} = shell

const {
  loading,
  loadError,
  child,
  stats,
  insights,
  activity,
  planner,
  lessonProgress,
  languagePlacement,
  load,
} = useParentMonitor(shell.selectedStudentId)

useParentPageLoad(shell, load, 'dashboard')

const latestActivity = computed(() => (activity.value || []).slice(0, 6))

const latestAiInsight = computed(() => insights.value?.[0] ?? null)

const aiSummaryLine = computed(() => {
  const lines = stats.value?.summary_lines
  if (Array.isArray(lines) && lines.length) return lines[0]
  return latestAiInsight.value?.text ?? ''
})

const overviewAlerts = computed(() =>
  (insights.value || []).slice(0, 6).map((item, index) => ({
    id: item.id ?? `insight-${index}`,
    type: item.severity === 'warning' ? 'warning' : item.severity === 'success' ? 'success' : 'info',
    title: item.text,
    subtitle: '',
    is_read: true,
  })),
)
</script>

<style scoped>
.activity-panel {
  border: 1px solid rgba(34, 211, 238, 0.12);
}
</style>
