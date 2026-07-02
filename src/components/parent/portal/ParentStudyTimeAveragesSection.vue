<template>
  <v-card class="glass-card pa-4 pa-md-5 mb-6" variant="flat">
    <div class="d-flex align-center gap-2 mb-4">
      <v-icon color="info">mdi-clock-outline</v-icon>
      <h3 class="text-h6 font-weight-bold mb-0">{{ t('parent.attendance.averages.title') }}</h3>
    </div>

    <v-row v-if="averages" dense>
      <v-col cols="12" sm="4">
        <div class="avg-card pa-4 rounded-lg text-center h-100">
          <p class="text-caption text-medium-emphasis mb-1">{{ t('parent.attendance.averages.dailyAverage') }}</p>
          <div class="text-h4 font-weight-bold eduspark-gradient-text">
            {{ averages.daily_hours }}
            <span class="text-body-2">{{ t('parent.attendance.averages.hourPerDay') }}</span>
          </div>
          <v-chip
            v-if="averages.daily_trend_percent != null"
            size="x-small"
            variant="tonal"
            class="mt-2"
            :color="averages.daily_trend_percent >= 0 ? 'success' : 'error'"
            :prepend-icon="averages.daily_trend_percent >= 0 ? 'mdi-trending-up' : 'mdi-trending-down'"
          >
            {{ formatTrend(averages.daily_trend_percent) }} {{ t('parent.attendance.averages.comparedToPreviousWeek') }}
          </v-chip>
        </div>
      </v-col>
      <v-col cols="12" sm="4">
        <div class="avg-card pa-4 rounded-lg text-center h-100">
          <p class="text-caption text-medium-emphasis mb-1">{{ t('parent.attendance.averages.weeklyAverage') }}</p>
          <div class="text-h4 font-weight-bold">
            {{ averages.weekly_hours }}
            <span class="text-body-2">{{ t('parent.attendance.averages.hourPerWeek') }}</span>
          </div>
          <v-chip
            v-if="averages.weekly_trend_percent != null"
            size="x-small"
            variant="tonal"
            class="mt-2"
            :color="averages.weekly_trend_percent >= 0 ? 'success' : 'error'"
            :prepend-icon="averages.weekly_trend_percent >= 0 ? 'mdi-trending-up' : 'mdi-trending-down'"
          >
            {{ formatTrend(averages.weekly_trend_percent) }} {{ t('parent.attendance.averages.comparedToPreviousWeek') }}
          </v-chip>
        </div>
      </v-col>
      <v-col cols="12" sm="4">
        <div class="avg-card pa-4 rounded-lg text-center h-100">
          <p class="text-caption text-medium-emphasis mb-1">{{ t('parent.attendance.averages.monthlyTotal') }}</p>
          <div class="text-h4 font-weight-bold">
            {{ averages.monthly_hours }}
            <span class="text-body-2">{{ t('parent.attendance.averages.hourPerMonth') }}</span>
          </div>
          <v-chip
            v-if="averages.monthly_trend_percent != null"
            size="x-small"
            variant="tonal"
            class="mt-2"
            :color="averages.monthly_trend_percent >= 0 ? 'success' : 'error'"
            :prepend-icon="averages.monthly_trend_percent >= 0 ? 'mdi-trending-up' : 'mdi-trending-down'"
          >
            {{ formatTrend(averages.monthly_trend_percent) }} {{ t('parent.attendance.averages.comparedToPreviousMonth') }}
          </v-chip>
        </div>
      </v-col>
    </v-row>
  </v-card>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

defineProps({
  averages: { type: Object, default: null },
})

const { t } = useI18n()

function formatTrend(pct) {
  const sign = pct >= 0 ? '+' : ''
  return `${sign}${pct}%`
}
</script>

<style scoped>
.avg-card {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.06);
}
</style>
