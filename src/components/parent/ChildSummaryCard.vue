<template>
  <v-card class="glass-card glass-card--elevated pa-5 pa-md-6 child-summary" variant="flat">
    <div class="d-flex align-center gap-4 flex-wrap">
      <v-avatar size="64" class="eduspark-gradient">
        <span class="text-h5 font-weight-bold text-white">{{ initials }}</span>
      </v-avatar>
      <div class="flex-grow-1">
        <p class="text-caption text-medium-emphasis mb-1">{{ t('parent.childSummary.tracking') }}</p>
        <h2 class="text-h5 font-weight-bold mb-1">{{ child?.name }}</h2>
        <p class="text-body-2 text-medium-emphasis mb-0">{{ child?.email }}</p>
      </div>
      <v-chip color="warning" variant="tonal" prepend-icon="mdi-eye-lock" size="small">
        {{ t('parent.childSummary.readOnly') }}
      </v-chip>
    </div>

    <v-divider class="my-5 border-opacity-25" />

    <v-row dense>
      <v-col v-for="stat in statItems" :key="stat.label" cols="6" sm="3">
        <div class="stat-pill text-center pa-3 rounded-lg">
          <div class="text-h6 font-weight-bold eduspark-gradient-text">{{ stat.value }}</div>
          <div class="text-caption text-medium-emphasis">{{ stat.label }}</div>
        </div>
      </v-col>
    </v-row>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  child: { type: Object, default: null },
  stats: { type: Object, default: () => ({}) },
})

const { t } = useI18n()

const initials = computed(() => {
  const parts = (props.child?.name || '?').split(' ')
  return parts.slice(0, 2).map((p) => p[0]).join('')
})

const statItems = computed(() => [
  { label: t('parent.childSummary.weeklySessions'), value: props.stats.weekly_sessions ?? 0 },
  { label: t('parent.childSummary.quizzes'), value: props.stats.weekly_quizzes ?? 0 },
  { label: t('parent.childSummary.averageGrades'), value: `${props.stats.average_score ?? 0}%` },
  { label: t('parent.childSummary.subjectsTracked'), value: props.stats.subjects_tracked ?? 0 },
])
</script>

<style scoped>
.stat-pill {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.06);
}
</style>
