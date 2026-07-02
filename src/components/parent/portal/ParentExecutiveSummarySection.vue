<template>
  <v-card class="glass-card glass-card--elevated pa-4 pa-md-5 mb-6" variant="flat">
    <div class="d-flex align-center gap-2 mb-4">
      <v-icon color="secondary">mdi-chart-timeline-variant</v-icon>
      <h3 class="text-h6 font-weight-bold mb-0">{{ t('parent.insights.weeklySummary.title') }}</h3>
    </div>

    <v-skeleton-loader v-if="loading" type="list-item@4" />

    <v-alert v-else-if="error" type="error" variant="tonal" density="compact" class="rounded-lg">
      {{ error }}
    </v-alert>

    <template v-else-if="summary">
      <p v-if="!summary.has_data" class="text-body-2 text-medium-emphasis mb-0">
        {{ t('parent.insights.weeklySummary.noData') }}
      </p>

      <ul v-else-if="summary.summary_lines?.length" class="summary-list mb-0">
        <li class="summary-heading">{{ t('parent.insights.weeklySummary.thisWeek') }}</li>
        <li v-for="(line, idx) in summary.summary_lines" :key="idx">{{ line }}</li>
      </ul>

      <v-row v-if="summary.weekly_snapshot" dense class="mt-4">
        <v-col cols="6" sm="4" md="2">
          <div class="metric pa-3 rounded-lg text-center">
            <div class="text-h6 font-weight-bold">{{ summary.weekly_snapshot.lessons_completed }}</div>
            <p class="text-caption mb-0">{{ t('parent.insights.weeklySummary.completedLessons') }}</p>
          </div>
        </v-col>
        <v-col cols="6" sm="4" md="2">
          <div class="metric pa-3 rounded-lg text-center">
            <div class="text-h6 font-weight-bold">{{ summary.weekly_snapshot.study_hours }}</div>
            <p class="text-caption mb-0">{{ t('parent.insights.weeklySummary.studyHours') }}</p>
          </div>
        </v-col>
        <v-col cols="6" sm="4" md="2">
          <div class="metric pa-3 rounded-lg text-center">
            <div class="text-h6 font-weight-bold">
              {{ summary.weekly_snapshot.average_quiz_score ?? t('parent.common.emDash') }}
              <span v-if="summary.weekly_snapshot.average_quiz_score != null" class="text-caption">%</span>
            </div>
            <p class="text-caption mb-0">{{ t('parent.insights.weeklySummary.quizAverage') }}</p>
          </div>
        </v-col>
        <v-col cols="6" sm="4" md="2">
          <div class="metric pa-3 rounded-lg text-center">
            <div class="text-h6 font-weight-bold">
              {{ summary.weekly_snapshot.planner_adherence_percent ?? t('parent.common.emDash') }}
              <span v-if="summary.weekly_snapshot.planner_adherence_percent != null" class="text-caption">%</span>
            </div>
            <p class="text-caption mb-0">{{ t('parent.insights.weeklySummary.planAdherence') }}</p>
          </div>
        </v-col>
        <v-col cols="6" sm="6" md="2">
          <div class="metric pa-3 rounded-lg text-center">
            <div class="text-body-2 font-weight-bold text-truncate">
              {{ summary.weekly_snapshot.most_active_subject || t('parent.common.emDash') }}
            </div>
            <p class="text-caption mb-0">{{ t('parent.insights.weeklySummary.mostActiveSubject') }}</p>
          </div>
        </v-col>
        <v-col cols="6" sm="6" md="2">
          <div class="metric pa-3 rounded-lg text-center">
            <div class="text-body-2 font-weight-bold text-truncate">
              {{ summary.weekly_snapshot.weakest_subject || t('parent.common.emDash') }}
            </div>
            <p class="text-caption mb-0">{{ t('parent.insights.weeklySummary.weakestSubject') }}</p>
          </div>
        </v-col>
      </v-row>
    </template>
  </v-card>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

defineProps({
  summary: { type: Object, default: null },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
})

const { t } = useI18n()
</script>

<style scoped>
.summary-list {
  padding-inline-start: 1.25rem;
  line-height: 1.9;
}

.summary-heading {
  list-style: none;
  margin-inline-start: -1.25rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
}

.metric {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.06);
  min-height: 72px;
}
</style>
