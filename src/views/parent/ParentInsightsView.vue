<template>
  <ParentPortalShell
    :title="t('parent.insights.title')"
    :subtitle="t('parent.insights.subtitle')"
    :students="students"
    :selected-student-id="selectedStudentId"
    :student-context="studentContext"
    :has-students="hasStudents"
    :loading-students="loadingStudents"
    :students-error="studentsError"
    :linking="linking"
    :link-error="linkError"
    :link-success="linkSuccess"
    :loading="executiveLoading"
    :load-error="executiveError"
    @select-student="selectStudent"
    @link="linkStudent"
    @clear-students-error="studentsError = ''"
    @clear-link-error="linkError = ''"
    @clear-link-success="linkSuccess = ''"
    @clear-load-error="executiveError = ''"
  >
    <ParentExecutiveSummarySection
      :summary="executiveSummary"
      :loading="executiveLoading"
      :error="executiveError"
    />

    <ParentSubjectAnalysisSection
      v-if="executiveSummary?.has_data"
      :strength="executiveSummary.strength_analysis"
      :weakness="executiveSummary.weakness_analysis"
    />

    <ParentStudyBehaviorSection
      v-if="executiveSummary?.study_behavior"
      :behavior="executiveSummary.study_behavior"
    />

    <ParentStudyTimeAveragesSection
      v-if="executiveSummary?.study_time_averages"
      :averages="executiveSummary.study_time_averages"
    />

    <ParentPeriodComparisonSection
      v-if="executiveSummary?.period_comparison"
      :comparison="executiveSummary.period_comparison"
    />

    <ParentRiskAlertsSection
      :alerts="executiveSummary?.risk_alerts || []"
    />

    <section class="mb-6">
      <div class="d-flex align-center gap-2 mb-4">
        <v-icon color="secondary">mdi-lightbulb-on</v-icon>
        <h3 class="text-h6 font-weight-bold mb-0">{{ t('parent.insights.smartRecommendations') }}</h3>
      </div>
      <ParentInsightCards
        v-if="executiveSummary?.recommendations?.length"
        :insights="executiveSummary.recommendations"
      />
      <v-alert v-else type="info" variant="tonal" density="compact" class="rounded-lg">
        {{ t('parent.insights.recommendationsEmpty') }}
      </v-alert>
    </section>
  </ParentPortalShell>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import ParentPortalShell from '../../components/parent/portal/ParentPortalShell.vue'
import ParentExecutiveSummarySection from '../../components/parent/portal/ParentExecutiveSummarySection.vue'
import ParentSubjectAnalysisSection from '../../components/parent/portal/ParentSubjectAnalysisSection.vue'
import ParentStudyBehaviorSection from '../../components/parent/portal/ParentStudyBehaviorSection.vue'
import ParentStudyTimeAveragesSection from '../../components/parent/portal/ParentStudyTimeAveragesSection.vue'
import ParentPeriodComparisonSection from '../../components/parent/portal/ParentPeriodComparisonSection.vue'
import ParentRiskAlertsSection from '../../components/parent/portal/ParentRiskAlertsSection.vue'
import ParentInsightCards from '../../components/parent/ParentInsightCards.vue'
import { useParentShell } from '../../composables/useParentShell.js'
import { useParentExecutiveSummary } from '../../composables/useParentExecutiveSummary.js'
import { useParentPageLoad } from '../../composables/useParentPageLoad.js'

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

const executive = useParentExecutiveSummary(shell.selectedStudentId)
const {
  summary: executiveSummary,
  loading: executiveLoading,
  error: executiveError,
  load: loadExecutiveSummary,
} = executive

useParentPageLoad(shell, loadExecutiveSummary, 'insights')
</script>
