<template>
  <v-card class="glass-card glass-card--elevated pa-4 pa-md-5 section-card" variant="flat">
    <div class="d-flex align-center justify-space-between mb-4 flex-wrap gap-2">
      <div class="d-flex align-center gap-2">
        <v-icon color="primary">mdi-calendar-check</v-icon>
        <h3 class="text-h6 font-weight-bold mb-0">{{ t('parent.attendance.commitmentTitle') }}</h3>
      </div>
      <v-chip size="small" variant="tonal" color="secondary" prepend-icon="mdi-database">
        {{ t('parent.attendance.realData') }}
      </v-chip>
    </div>

    <v-skeleton-loader v-if="loading" type="article" />

    <template v-else>
      <v-row dense class="mb-4">
        <v-col cols="6" sm="3">
          <div class="metric-card pa-4 rounded-lg text-center">
            <div class="text-h5 font-weight-bold eduspark-gradient-text">
              {{ summary.weekly_consistency }}%
            </div>
            <p class="text-caption text-medium-emphasis mb-0">{{ t('parent.attendance.weeklyCommitment') }}</p>
          </div>
        </v-col>
        <v-col cols="6" sm="3">
          <AttendanceStreakWidget
            :streak-days="summary.streak_days"
            :attendance-percentage="summary.attendance_percentage"
          />
        </v-col>
        <v-col cols="12" sm="6">
          <div class="metric-card pa-4 rounded-lg">
            <div class="d-flex justify-space-between text-caption mb-2">
              <span>{{ t('parent.attendance.weeklyStudyMinutes') }}</span>
              <span class="font-weight-bold">{{ summary.total_study_minutes_week }} {{ t('parent.units.minutesShort') }}</span>
            </div>
            <v-progress-linear
              :model-value="summary.weekly_consistency"
              color="secondary"
              height="8"
              rounded
              class="mb-2"
            />
            <div class="d-flex justify-space-between text-caption">
              <span class="text-success">{{ t('parent.attendance.present', { n: summary.completed_sessions }) }}</span>
              <span class="text-warning">{{ t('parent.attendance.partial', { n: summary.partial_days }) }}</span>
              <span class="text-error">{{ t('parent.attendance.absent', { n: summary.missed_sessions }) }}</span>
            </div>
          </div>
        </v-col>
      </v-row>

      <AttendanceWeeklyCalendar :days="summary.weekly_calendar" class="mb-5" />

      <v-row>
        <v-col cols="12" md="6">
          <AttendanceConsistencyBars :bars="summary.consistency_bars" />
        </v-col>
        <v-col cols="12" md="6">
          <AttendanceMonthlyOverview :weeks="summary.monthly_overview" />
        </v-col>
      </v-row>

      <div v-if="summary.ai_insights?.length" class="ai-insights mt-5 pa-4 rounded-lg">
        <div class="d-flex align-center gap-2 mb-2">
          <v-icon color="secondary" size="18">mdi-creation</v-icon>
          <span class="text-subtitle-2 font-weight-bold">{{ t('parent.attendance.aiSummary') }}</span>
        </div>
        <p v-for="(line, i) in summary.ai_insights" :key="i" class="text-body-2 mb-1">{{ line }}</p>
      </div>

      <v-alert
        v-for="(alert, i) in summary.alerts"
        :key="i"
        :type="alert.type"
        variant="tonal"
        density="compact"
        class="mt-3 rounded-lg"
      >
        {{ alert.text }}
      </v-alert>
    </template>
  </v-card>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import AttendanceStreakWidget from '../attendance/AttendanceStreakWidget.vue'
import AttendanceConsistencyBars from '../attendance/AttendanceConsistencyBars.vue'
import AttendanceWeeklyCalendar from '../attendance/AttendanceWeeklyCalendar.vue'
import AttendanceMonthlyOverview from '../attendance/AttendanceMonthlyOverview.vue'

defineProps({
  summary: { type: Object, required: true },
  loading: { type: Boolean, default: false },
})

const { t } = useI18n()
</script>

<style scoped>
.section-card {
  border-inline-start: 3px solid rgba(124, 108, 240, 0.45);
}

.metric-card {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.06);
  height: 100%;
  transition: border-color 0.2s ease;
}

.metric-card:hover {
  border-color: rgba(34, 211, 238, 0.25);
}

.ai-insights {
  background: rgba(34, 211, 238, 0.06);
  border: 1px solid rgba(34, 211, 238, 0.2);
}
</style>
