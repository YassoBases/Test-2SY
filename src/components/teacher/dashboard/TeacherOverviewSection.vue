<template>
  <AppSection
    class="teacher-home__section teacher-home__section--overview"
    :eyebrow="$t('teacher.dashboard.overview')"
    :title="$t('teacher.dashboard.teachingSummary')"
    :subtitle="$t('teacher.dashboard.overviewDesc')"
    spacing="sm"
    :divider="false"
  >
    <TeacherSummaryGrid
      v-if="metrics.length"
      :columns="metricColumns"
      :aria-label="$t('teacher.dashboard.kpiAria')"
    >
      <TeacherStatCard
        v-for="metric in metrics"
        :key="metric.id"
        compact
        :label="metric.title"
        :value="metric.value"
        :subtitle="metric.subtitle"
        :icon="metric.icon"
        tone="primary"
      />
    </TeacherSummaryGrid>

    <TeacherEmptyStateCard
      v-else
      compact
      icon="mdi-chart-line"
      :title="$t('teacher.dashboard.noMetrics')"
      :description="$t('teacher.dashboard.metricsHint')"
    />
  </AppSection>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import { AppSection } from '../../ui/index.js'
import {
  TeacherEmptyStateCard,
  TeacherStatCard,
  TeacherSummaryGrid,
} from '../design-system/index.js'

const props = defineProps({
  metrics: { type: Array, default: () => [] },
})

const metricColumns = computed(() => {
  const n = props.metrics.length
  if (n >= 4) return 4
  if (n === 3) return 3
  return 2
})
</script>
