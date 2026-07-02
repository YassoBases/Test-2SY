<template>
  <v-card class="glass-card glass-card--elevated pa-4 pa-md-5 section-card mb-6" variant="flat">
    <div class="d-flex align-center justify-space-between mb-4 flex-wrap gap-2">
      <div class="d-flex align-center gap-2">
        <v-icon color="secondary">mdi-clock-check-outline</v-icon>
        <h3 class="text-h6 font-weight-bold mb-0">{{ t('parent.attendance.studyTime.title') }}</h3>
      </div>
      <v-chip size="small" variant="tonal" color="success" prepend-icon="mdi-database-check">
        {{ t('parent.attendance.studyTime.realActivity') }}
      </v-chip>
    </div>

    <v-alert v-if="error" type="error" variant="tonal" density="compact" class="mb-4 rounded-lg">
      {{ error }}
    </v-alert>

    <v-skeleton-loader v-if="loading" type="article, table" />

    <template v-else-if="analytics">
      <v-row dense class="mb-5">
        <v-col cols="6" md="3">
          <div class="metric-card pa-4 rounded-lg text-center h-100">
            <v-icon color="primary" size="22" class="mb-2">mdi-calendar-today</v-icon>
            <div class="text-h5 font-weight-bold eduspark-gradient-text">
              {{ analytics.overview.today_minutes }}
            </div>
            <p class="text-caption text-medium-emphasis mb-0">{{ t('parent.attendance.studyTime.todayMinutes') }}</p>
          </div>
        </v-col>
        <v-col cols="6" md="3">
          <div class="metric-card pa-4 rounded-lg text-center h-100">
            <v-icon color="secondary" size="22" class="mb-2">mdi-calendar-week</v-icon>
            <div class="text-h5 font-weight-bold">{{ analytics.overview.week_minutes }}</div>
            <p class="text-caption text-medium-emphasis mb-1">{{ t('parent.attendance.studyTime.weekMinutes') }}</p>
            <v-chip
              v-if="analytics.overview.week_comparison_percent != null"
              size="x-small"
              variant="tonal"
              :color="analytics.overview.week_comparison_percent >= 0 ? 'success' : 'error'"
            >
              {{ formatComparison(analytics.overview.week_comparison_percent) }}
            </v-chip>
          </div>
        </v-col>
        <v-col cols="6" md="3">
          <div class="metric-card pa-4 rounded-lg text-center h-100">
            <v-icon color="info" size="22" class="mb-2">mdi-calendar-month</v-icon>
            <div class="text-h5 font-weight-bold">{{ analytics.overview.month_minutes }}</div>
            <p class="text-caption text-medium-emphasis mb-1">{{ t('parent.attendance.studyTime.monthMinutes') }}</p>
            <v-chip
              v-if="analytics.overview.month_comparison_percent != null"
              size="x-small"
              variant="tonal"
              :color="analytics.overview.month_comparison_percent >= 0 ? 'success' : 'error'"
            >
              {{ formatComparison(analytics.overview.month_comparison_percent) }}
            </v-chip>
          </div>
        </v-col>
        <v-col cols="6" md="3">
          <div class="metric-card pa-4 rounded-lg text-center h-100">
            <v-icon color="warning" size="22" class="mb-2">mdi-history</v-icon>
            <div class="text-body-1 font-weight-bold text-truncate">
              {{ formatLastActivity(analytics.overview.last_activity_at) }}
            </div>
            <p class="text-caption text-medium-emphasis mb-0">{{ t('parent.attendance.studyTime.lastActivity') }}</p>
          </div>
        </v-col>
      </v-row>

      <div class="d-flex align-center justify-space-between flex-wrap gap-2 mb-3">
        <p class="text-subtitle-2 font-weight-bold mb-0">
          {{ t('parent.attendance.studyTime.dailyDistribution', { period: analytics.weekly_analytics.period_label }) }}
        </p>
        <v-btn-toggle
          :model-value="weekOffset"
          mandatory
          density="compact"
          variant="outlined"
          divided
          @update:model-value="$emit('week-offset', $event)"
        >
          <v-btn :value="0" size="small">{{ t('parent.attendance.studyTime.thisWeek') }}</v-btn>
          <v-btn :value="1" size="small">{{ t('parent.attendance.studyTime.lastWeek') }}</v-btn>
        </v-btn-toggle>
      </div>

      <div class="daily-chart mb-5">
        <div
          v-for="day in analytics.daily_breakdown"
          :key="day.date"
          class="daily-bar-col text-center"
        >
          <div class="bar-track">
            <div
              class="bar-fill"
              :style="{ height: barHeight(day.study_minutes) }"
              :class="{ 'bar-fill--zero': !day.study_minutes }"
            />
          </div>
          <p class="text-caption font-weight-bold mb-0 mt-2">{{ day.day_label }}</p>
          <p class="text-caption text-medium-emphasis mb-0">{{ day.study_minutes }} {{ t('parent.units.minutesShort') }}</p>
        </div>
      </div>

      <v-row dense class="mb-6">
        <v-col cols="6" sm="3">
          <div class="stat-mini pa-3 rounded-lg h-100">
            <p class="text-caption text-medium-emphasis mb-1">{{ t('parent.attendance.studyTime.weeklyTotal') }}</p>
            <p class="text-body-2 font-weight-bold mb-0">{{ analytics.weekly_analytics.total_minutes }} {{ t('parent.units.minutesShort') }}</p>
          </div>
        </v-col>
        <v-col cols="6" sm="3">
          <div class="stat-mini pa-3 rounded-lg h-100">
            <p class="text-caption text-medium-emphasis mb-1">{{ t('parent.attendance.studyTime.dailyAverage') }}</p>
            <p class="text-body-2 font-weight-bold mb-0">{{ analytics.weekly_analytics.daily_average_minutes }} {{ t('parent.units.minutesShort') }}</p>
          </div>
        </v-col>
        <v-col cols="6" sm="3">
          <div class="stat-mini pa-3 rounded-lg h-100">
            <p class="text-caption text-medium-emphasis mb-1">{{ t('parent.attendance.studyTime.mostActiveDay') }}</p>
            <p class="text-body-2 font-weight-bold mb-0">{{ daySummary(analytics.weekly_analytics.most_active_day) }}</p>
          </div>
        </v-col>
        <v-col cols="6" sm="3">
          <div class="stat-mini pa-3 rounded-lg h-100">
            <p class="text-caption text-medium-emphasis mb-1">{{ t('parent.attendance.studyTime.leastActiveDay') }}</p>
            <p class="text-body-2 font-weight-bold mb-0">{{ daySummary(analytics.weekly_analytics.least_active_day) }}</p>
          </div>
        </v-col>
      </v-row>

      <div class="d-flex align-center justify-space-between flex-wrap gap-2 mb-3">
        <div class="d-flex align-center gap-1">
          <p class="text-subtitle-2 font-weight-bold mb-0">
            {{ t('parent.attendance.studyTime.monthlyAnalysis', { period: analytics.monthly_analytics.period_label }) }}
          </p>
          <v-icon v-if="analytics.monthly_analytics.trend === 'up'" color="success" size="18">mdi-trending-up</v-icon>
          <v-icon v-else-if="analytics.monthly_analytics.trend === 'down'" color="error" size="18">mdi-trending-down</v-icon>
          <v-icon v-else color="grey" size="18">mdi-minus</v-icon>
        </div>
        <div class="d-flex align-center gap-2 flex-wrap">
          <v-chip
            v-if="analytics.monthly_analytics.comparison_percent != null"
            size="small"
            variant="tonal"
            :color="analytics.monthly_analytics.comparison_percent >= 0 ? 'success' : 'error'"
          >
            {{ formatComparison(analytics.monthly_analytics.comparison_percent) }} {{ t('parent.attendance.studyTime.vsPreviousMonth') }}
          </v-chip>
          <v-btn-toggle
            :model-value="monthOffset"
            mandatory
            density="compact"
            variant="outlined"
            divided
            @update:model-value="$emit('month-offset', $event)"
          >
            <v-btn :value="0" size="small">{{ t('parent.attendance.studyTime.thisMonth') }}</v-btn>
            <v-btn :value="1" size="small">{{ t('parent.attendance.studyTime.lastMonth') }}</v-btn>
          </v-btn-toggle>
        </div>
      </div>

      <v-row dense class="mb-4">
        <v-col cols="6" sm="4">
          <div class="stat-mini pa-3 rounded-lg h-100">
            <p class="text-caption text-medium-emphasis mb-1">{{ t('parent.attendance.studyTime.monthlyTotal') }}</p>
            <p class="text-body-2 font-weight-bold mb-0">{{ analytics.monthly_analytics.total_minutes }} {{ t('parent.units.minutesShort') }}</p>
          </div>
        </v-col>
        <v-col cols="6" sm="4">
          <div class="stat-mini pa-3 rounded-lg h-100">
            <p class="text-caption text-medium-emphasis mb-1">{{ t('parent.attendance.studyTime.weeklyAverage') }}</p>
            <p class="text-body-2 font-weight-bold mb-0">{{ analytics.monthly_analytics.weekly_average_minutes }} {{ t('parent.units.minutesShort') }}</p>
          </div>
        </v-col>
        <v-col cols="12" sm="4">
          <div class="stat-mini pa-3 rounded-lg h-100">
            <p class="text-caption text-medium-emphasis mb-1">{{ t('parent.attendance.studyTime.activeDaysThisWeek') }}</p>
            <p class="text-body-2 font-weight-bold mb-0">{{ analytics.weekly_analytics.active_days_count }}</p>
          </div>
        </v-col>
      </v-row>

      <div v-if="analytics.monthly_analytics.weeks?.length" class="month-weeks mb-6">
        <p class="text-caption text-medium-emphasis mb-2">{{ t('parent.attendance.studyTime.monthWeekDistribution') }}</p>
        <div class="d-flex gap-2 flex-wrap">
          <div
            v-for="w in analytics.monthly_analytics.weeks"
            :key="w.week_index"
            class="week-bucket pa-3 rounded-lg flex-grow-1 text-center"
          >
            <p class="text-caption mb-1">{{ t('parent.attendance.studyTime.weekWithIndex', { n: w.week_index }) }}</p>
            <p class="text-h6 font-weight-bold mb-0">
              {{ w.study_minutes }}<span class="text-caption"> {{ t('parent.units.minutesShort') }}</span>
            </p>
            <div class="week-bar mt-2">
              <div class="week-bar-fill" :style="{ width: monthWeekWidth(w.study_minutes) }" />
            </div>
          </div>
        </div>
      </div>

      <div class="d-flex align-center gap-2 mb-3">
        <v-icon color="primary" size="20">mdi-login</v-icon>
        <p class="text-subtitle-2 font-weight-bold mb-0">{{ t('parent.attendance.studyTime.loginLogoutLog') }}</p>
      </div>

      <v-table v-if="analytics.login_history?.length" density="comfortable" class="session-table rounded-lg">
        <thead>
          <tr>
            <th>{{ t('parent.attendance.studyTime.date') }}</th>
            <th>{{ t('parent.attendance.studyTime.loginTime') }}</th>
            <th>{{ t('parent.attendance.studyTime.logoutTime') }}</th>
            <th>{{ t('parent.attendance.studyTime.studyDuration') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in analytics.login_history" :key="row.id">
            <td>{{ row.date }}</td>
            <td>{{ formatTime(row.login_at) }}</td>
            <td>
              <span v-if="row.is_open" class="text-success">{{ t('parent.attendance.studyTime.openSession') }}</span>
              <span v-else>{{ formatTime(row.logout_at) }}</span>
            </td>
            <td class="font-weight-bold">{{ row.active_minutes }} {{ t('parent.units.minutesShort') }}</td>
          </tr>
        </tbody>
      </v-table>

      <v-alert v-else type="info" variant="tonal" density="compact" class="rounded-lg">
        {{ t('parent.attendance.studyTime.noSessionsInPeriod') }}
      </v-alert>
    </template>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  analytics: { type: Object, default: null },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
  weekOffset: { type: Number, default: 0 },
  monthOffset: { type: Number, default: 0 },
})

defineEmits(['week-offset', 'month-offset'])

const { t, locale } = useI18n()

function dateLocale() {
  return locale.value === 'ar' ? 'ar-SY' : 'en-US'
}

const maxDailyMinutes = computed(() => {
  const days = props.analytics?.daily_breakdown || []
  return Math.max(...days.map((d) => d.study_minutes), 1)
})

const maxMonthWeekMinutes = computed(() => {
  const weeks = props.analytics?.monthly_analytics?.weeks || []
  return Math.max(...weeks.map((w) => w.study_minutes), 1)
})

function barHeight(minutes) {
  const pct = Math.round((minutes / maxDailyMinutes.value) * 100)
  return `${Math.max(pct, minutes > 0 ? 8 : 2)}%`
}

function monthWeekWidth(minutes) {
  const pct = Math.round((minutes / maxMonthWeekMinutes.value) * 100)
  return `${Math.max(pct, minutes > 0 ? 12 : 4)}%`
}

function formatTime(iso) {
  if (!iso) return t('parent.common.emDash')
  return new Date(iso).toLocaleTimeString(dateLocale(), { hour: '2-digit', minute: '2-digit' })
}

function formatLastActivity(iso) {
  if (!iso) return t('parent.attendance.studyTime.noActivityYet')
  const d = new Date(iso)
  return d.toLocaleString(dateLocale(), {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function daySummary(day) {
  if (!day || !day.study_minutes) return t('parent.common.emDash')
  return t('parent.attendance.studyTime.daySummary', { label: day.day_label, minutes: day.study_minutes })
}

function formatComparison(pct) {
  if (pct == null) return t('parent.common.emDash')
  const sign = pct >= 0 ? '+' : ''
  return `${sign}${pct}%`
}
</script>

<style scoped>
.section-card {
  border-inline-start: 3px solid rgba(34, 211, 238, 0.45);
}

.metric-card {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.06);
  transition: border-color 0.2s ease;
}

.metric-card:hover {
  border-color: rgba(34, 211, 238, 0.25);
}

.daily-chart {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 10px;
  align-items: end;
  min-height: 160px;
}

@media (max-width: 600px) {
  .daily-chart {
    grid-template-columns: repeat(4, 1fr);
  }
}

.bar-track {
  height: 100px;
  background: rgba(0, 0, 0, 0.25);
  border-radius: 8px;
  display: flex;
  align-items: flex-end;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.bar-fill {
  width: 100%;
  background: linear-gradient(180deg, rgba(34, 211, 238, 0.85), rgba(124, 108, 240, 0.65));
  border-radius: 6px 6px 0 0;
  transition: height 0.35s ease;
}

.bar-fill--zero {
  background: rgba(255, 255, 255, 0.08);
}

.stat-mini {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.week-bucket {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  min-width: 100px;
}

.week-bar {
  height: 6px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 4px;
  overflow: hidden;
}

.week-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, rgba(124, 108, 240, 0.8), rgba(34, 211, 238, 0.8));
  border-radius: 4px;
  transition: width 0.35s ease;
}

.session-table {
  background: rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.06);
}
</style>
