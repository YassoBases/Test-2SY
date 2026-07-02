<template>
  <v-card v-if="items?.length" class="glass-card pa-4 mb-4" variant="flat">
    <div class="d-flex align-center gap-2 mb-3">
      <v-icon color="primary" size="22">mdi-chart-arc</v-icon>
      <h3 class="text-subtitle-1 font-weight-bold mb-0">{{ t('parent.performance.courseProgress.title') }}</h3>
    </div>
    <v-row dense>
      <v-col v-for="row in items" :key="row.course_id" cols="12" sm="6">
        <div class="course-row pa-3 rounded-lg">
          <div class="d-flex justify-space-between align-center mb-1">
            <span class="font-weight-bold text-body-2">{{ row.subject_name || row.course_title }}</span>
            <v-chip size="x-small" variant="tonal" :color="pctColor(row.completion_percentage)">
              {{ row.completion_percentage ?? 0 }}%
            </v-chip>
          </div>
          <v-progress-linear
            :model-value="row.completion_percentage ?? 0"
            :color="pctColor(row.completion_percentage)"
            height="6"
            rounded
            class="mb-2"
          />
          <div class="d-flex justify-space-between text-caption text-medium-emphasis">
            <span v-if="row.completed_lessons != null">
              {{ t('parent.performance.courseProgress.lessonsCount', {
                completed: row.completed_lessons,
                total: row.total_lessons ?? t('parent.common.emDash'),
              }) }}
            </span>
            <span v-if="row.average_score != null">
              {{ t('parent.performance.courseProgress.average', { value: Math.round(row.average_score) }) }}
            </span>
          </div>
        </div>
      </v-col>
    </v-row>
  </v-card>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

defineProps({
  items: { type: Array, default: () => [] },
})

const { t } = useI18n()

function pctColor(pct) {
  const n = pct ?? 0
  if (n >= 70) return 'success'
  if (n >= 30) return 'warning'
  return 'primary'
}
</script>

<style scoped>
.course-row {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.06);
}
</style>
