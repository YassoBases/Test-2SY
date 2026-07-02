<template>
  <div>
    <v-card class="glass-card pa-4 pa-md-5 mb-6" variant="flat">
      <div class="d-flex align-center justify-space-between flex-wrap gap-3 mb-4">
        <div class="d-flex align-center gap-2">
          <v-icon color="primary">mdi-file-chart-outline</v-icon>
          <h3 class="text-h6 font-weight-bold mb-0">{{ t('parent.reports.historical.title') }}</h3>
        </div>
        <v-btn-toggle
          :model-value="period"
          mandatory
          density="compact"
          variant="outlined"
          divided
          @update:model-value="$emit('period-change', $event)"
        >
          <v-btn v-for="p in periods" :key="p.value" :value="p.value" size="small">
            {{ p.label }}
          </v-btn>
        </v-btn-toggle>
      </div>

      <v-row v-if="period === 'custom'" dense class="mb-4">
        <v-col cols="12" sm="5">
          <v-text-field
            :model-value="customStart"
            type="date"
            :label="t('parent.reports.historical.fromDate')"
            density="compact"
            variant="outlined"
            hide-details
            @update:model-value="$emit('update:customStart', $event)"
          />
        </v-col>
        <v-col cols="12" sm="5">
          <v-text-field
            :model-value="customEnd"
            type="date"
            :label="t('parent.reports.historical.toDate')"
            density="compact"
            variant="outlined"
            hide-details
            @update:model-value="$emit('update:customEnd', $event)"
          />
        </v-col>
        <v-col cols="12" sm="2" class="d-flex align-center">
          <v-btn color="primary" block @click="$emit('apply-custom')">{{ t('parent.reports.historical.apply') }}</v-btn>
        </v-col>
      </v-row>

      <div class="d-flex flex-wrap gap-2 mb-4">
        <v-btn size="small" variant="tonal" prepend-icon="mdi-file-delimited-outline" :loading="exporting" @click="$emit('export', 'csv')">{{ t('parent.common.exportCsv') }}</v-btn>
        <v-btn size="small" variant="tonal" prepend-icon="mdi-microsoft-excel" :loading="exporting" @click="$emit('export', 'xlsx')">{{ t('parent.common.exportExcel') }}</v-btn>
        <v-btn size="small" variant="tonal" prepend-icon="mdi-file-pdf-box" :loading="exporting" @click="$emit('export', 'pdf')">{{ t('parent.common.exportPdf') }}</v-btn>
      </div>

      <v-alert v-if="exportError" type="warning" variant="tonal" class="rounded-lg mb-4" density="compact" closable @click:close="$emit('clear-export-error')">
        <strong class="d-block mb-1">{{ t('parent.reports.historical.exportErrorTitle') }}</strong>
        {{ exportError }}
      </v-alert>

      <v-skeleton-loader v-if="loading" type="article, table" />

      <v-alert v-else-if="loadError" type="error" variant="tonal" class="rounded-lg mb-4">
        <strong class="d-block mb-1">{{ t('parent.reports.historical.loadErrorTitle') }}</strong>
        <div class="d-flex align-center justify-space-between flex-wrap gap-2">
          <span>{{ loadError }}</span>
          <v-btn size="small" variant="tonal" color="error" @click="$emit('retry')">{{ t('parent.reports.historical.retry') }}</v-btn>
        </div>
      </v-alert>

      <v-alert v-else-if="report && !report.has_data" type="info" variant="tonal" class="rounded-lg">
        {{ t('parent.reports.historical.noData') }}
      </v-alert>

      <template v-else-if="report">
        <p class="text-body-2 text-medium-emphasis mb-4">
          {{ report.student_name }} — {{ report.period_label }}
          <span class="text-caption">{{ t('parent.common.periodRange', { start: report.start_date, end: report.end_date }) }}</span>
        </p>

        <section class="mb-6">
          <h4 class="text-subtitle-1 font-weight-bold mb-3">
            {{ t('parent.reports.historical.periodComparison', { current: report.comparison.period_label, previous: report.comparison.previous_period_label }) }}
          </h4>
          <v-row dense>
            <v-col v-for="metric in comparisonMetrics" :key="metric.key" cols="12" sm="6" md="3">
              <div class="compare-card pa-4 rounded-lg h-100">
                <p class="text-caption text-medium-emphasis mb-1">{{ metric.label }}</p>
                <p class="text-h5 font-weight-bold mb-1">{{ formatMetric(metric) }}</p>
                <p class="text-caption mb-2">{{ t('parent.reports.historical.previous', { value: formatPrevious(metric) }) }}</p>
                <v-chip
                  v-if="metric.change_percent != null"
                  size="small"
                  variant="tonal"
                  :color="metric.change_percent >= 0 ? 'success' : 'error'"
                >
                  {{ formatChange(metric.change_percent) }}
                </v-chip>
              </div>
            </v-col>
          </v-row>
        </section>

        <section class="mb-6">
          <h4 class="text-subtitle-1 font-weight-bold mb-3">{{ t('parent.reports.historical.lessonCompletionWeekly') }}</h4>
          <ParentReportBarChart :points="report.lesson_history.weekly" />
          <h4 class="text-subtitle-1 font-weight-bold mb-3 mt-6">{{ t('parent.reports.historical.lessonCompletionMonthly') }}</h4>
          <ParentReportBarChart :points="report.lesson_history.monthly" />
          <p class="text-caption text-medium-emphasis mt-2 mb-0">
            {{ t('parent.reports.historical.totalInPeriod', { n: report.lesson_history.total_in_period }) }}
          </p>
        </section>

        <section class="mb-6">
          <h4 class="text-subtitle-1 font-weight-bold mb-3">{{ t('parent.reports.historical.attendanceTrend') }}</h4>
          <ParentReportBarChart :points="report.attendance_history.daily_study_trend" unit="min" />
          <h4 class="text-subtitle-1 font-weight-bold mb-3 mt-6">{{ t('parent.reports.historical.loginLogoutLog') }}</h4>
          <v-table density="comfortable" class="bg-transparent">
            <thead>
              <tr>
                <th>{{ t('parent.reports.historical.date') }}</th>
                <th>{{ t('parent.reports.historical.login') }}</th>
                <th>{{ t('parent.reports.historical.logout') }}</th>
                <th>{{ t('parent.reports.historical.minutes') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="s in report.attendance_history.login_sessions.slice(0, 20)" :key="s.id">
                <td>{{ s.day_label }} {{ s.date }}</td>
                <td class="text-caption">{{ formatTime(s.login_at) }}</td>
                <td class="text-caption">{{ s.logout_at ? formatTime(s.logout_at) : t('parent.common.emDash') }}</td>
                <td>{{ s.active_minutes }}</td>
              </tr>
              <tr v-if="!report.attendance_history.login_sessions.length">
                <td colspan="4" class="text-medium-emphasis">{{ t('parent.reports.historical.noSessions') }}</td>
              </tr>
            </tbody>
          </v-table>
        </section>

        <section>
          <h4 class="text-subtitle-1 font-weight-bold mb-3">{{ t('parent.reports.historical.plannerAdherence') }}</h4>
          <ParentReportBarChart :points="report.planner_history.adherence_trend" unit="%" />
          <h4 class="text-subtitle-1 font-weight-bold mb-3 mt-6">{{ t('parent.reports.historical.plannerMissed') }}</h4>
          <ParentReportBarChart :points="report.planner_history.missed_tasks_trend" />
        </section>
      </template>
    </v-card>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import ParentReportBarChart from './ParentReportBarChart.vue'
import { formatChangePercent } from '../../../composables/useParentHistoricalReports.js'

const props = defineProps({
  report: { type: Object, default: null },
  loading: { type: Boolean, default: false },
  exporting: { type: Boolean, default: false },
  loadError: { type: String, default: '' },
  exportError: { type: String, default: '' },
  period: { type: String, default: 'this_week' },
  customStart: { type: String, default: '' },
  customEnd: { type: String, default: '' },
})

defineEmits(['period-change', 'export', 'apply-custom', 'retry', 'clear-export-error', 'update:customStart', 'update:customEnd'])

const { t, locale } = useI18n()

const PERIOD_KEYS = ['this_week', 'last_week', 'this_month', 'last_month', 'custom']

const periods = computed(() =>
  PERIOD_KEYS.map((value) => ({
    value,
    label: t(`parent.reports.periods.${value}`),
  })),
)

const comparisonMetrics = computed(() => {
  const c = props.report?.comparison
  if (!c) return []
  return [
    { key: 'study_time', ...c.study_time },
    { key: 'grades', ...c.grades },
    { key: 'lesson_completion', ...c.lesson_completion },
    { key: 'planner_adherence', ...c.planner_adherence },
  ].filter((m) => m.label)
})

function formatChange(pct) {
  return formatChangePercent(pct)
}

function formatMetric(m) {
  if (m.unit === '%') return `${m.current_value}%`
  return `${m.current_value} ${m.unit || ''}`.trim()
}

function formatPrevious(m) {
  if (m.unit === '%') return `${m.previous_value}%`
  return `${m.previous_value} ${m.unit || ''}`.trim()
}

function dateLocale() {
  return locale.value === 'ar' ? 'ar-SY' : 'en-US'
}

function formatTime(iso) {
  if (!iso) return t('parent.common.emDash')
  try {
    return new Date(iso).toLocaleString(dateLocale(), { hour: 'numeric', minute: '2-digit', hour12: true })
  } catch {
    return iso
  }
}
</script>

<style scoped>
.compare-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
}
</style>
