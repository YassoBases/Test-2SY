<template>
  <v-card class="glass-card pa-4 pa-md-5 mb-6" variant="flat">
    <div class="d-flex align-center gap-2 mb-4">
      <v-icon color="primary">mdi-compare</v-icon>
      <h3 class="text-h6 font-weight-bold mb-0">
        {{ comparison?.period_label || t('parent.insights.periodComparison.title') }}
      </h3>
    </div>

    <v-row v-if="comparison" dense>
      <v-col v-for="metric in metrics" :key="metric.key" cols="12" sm="6" md="3">
        <div class="compare-card pa-4 rounded-lg h-100">
          <p class="text-caption text-medium-emphasis mb-1">{{ metric.label }}</p>
          <div class="d-flex align-center gap-2 mb-2">
            <span class="text-h5 font-weight-bold">{{ formatValue(metric) }}</span>
            <v-chip
              v-if="metric.change_percent != null"
              size="small"
              variant="tonal"
              :color="metric.change_percent >= 0 ? 'success' : 'error'"
              :prepend-icon="metric.change_percent >= 0 ? 'mdi-arrow-up' : 'mdi-arrow-down'"
            >
              {{ formatChange(metric.change_percent) }}
            </v-chip>
          </div>
          <p class="text-caption mb-0 text-medium-emphasis">
            {{ t('parent.insights.periodComparison.previous', { value: formatPrevious(metric) }) }}
          </p>
        </div>
      </v-col>
    </v-row>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  comparison: { type: Object, default: null },
})

const { t } = useI18n()

const metrics = computed(() => {
  const c = props.comparison
  if (!c) return []
  return [
    { key: 'study_time', ...c.study_time },
    { key: 'lesson_completion', ...c.lesson_completion },
    { key: 'quiz_performance', ...c.quiz_performance },
    { key: 'planner_adherence', ...c.planner_adherence },
  ].filter((m) => m.label)
})

function formatValue(metric) {
  if (metric.unit === '%') return `${metric.current_value}%`
  return `${metric.current_value} ${metric.unit || ''}`.trim()
}

function formatPrevious(metric) {
  if (metric.unit === '%') return `${metric.previous_value}%`
  return `${metric.previous_value} ${metric.unit || ''}`.trim()
}

function formatChange(pct) {
  const sign = pct >= 0 ? '+' : ''
  return `${sign}${pct}%`
}
</script>

<style scoped>
.compare-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
}
</style>
