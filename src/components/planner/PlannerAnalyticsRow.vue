<template>
  <v-row class="mb-4">
    <v-col v-for="card in cards" :key="card.label" cols="6" md="3">
      <v-card class="analytics-card pa-4" variant="flat">
        <v-icon :color="card.color" class="mb-2">{{ card.icon }}</v-icon>
        <div class="text-h5 font-weight-bold neon-value">{{ card.value }}</div>
        <p class="text-caption text-medium-emphasis mb-0">{{ card.label }}</p>
      </v-card>
    </v-col>
  </v-row>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  schedule: { type: Array, default: () => [] },
  profile: { type: Object, default: () => ({}) },
  planStats: { type: Object, default: () => ({}) },
  streak: { type: Object, default: () => ({}) },
  subjectAnalytics: { type: Array, default: () => [] },
})

const { t } = useI18n()

const cards = computed(() => {
  const planned = props.planStats.planned_count ?? props.schedule.filter((s) => s.status === 'planned').length
  const done = props.planStats.completed_count ?? props.schedule.filter((s) => s.status === 'completed').length
  const weak = props.subjectAnalytics.filter((s) => s.strength_level === 'weak').length
    || props.profile.weak_subjects?.length
    || 0
  const streakDays = props.streak.current_streak_days ?? 0
  return [
    { label: t('common.planner.analytics.plannedTasks'), value: planned, icon: 'mdi-calendar-week', color: 'secondary' },
    { label: t('common.planner.analytics.completed'), value: done, icon: 'mdi-check-decagram', color: 'success' },
    { label: t('common.planner.analytics.weakSubjects'), value: weak, icon: 'mdi-alert-circle-outline', color: 'warning' },
    {
      label: t('common.planner.analytics.learningStreak'),
      value: t('common.planner.streakDays', { days: streakDays }),
      icon: 'mdi-fire',
      color: 'error',
    },
  ]
})
</script>

<style scoped>
.analytics-card {
  background: rgba(15, 22, 45, 0.7) !important;
  border: 1px solid rgba(124, 108, 240, 0.2) !important;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.analytics-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 32px rgba(34, 211, 238, 0.12) !important;
}

.neon-value {
  color: var(--em-cyan);
  text-shadow: 0 0 20px rgba(34, 211, 238, 0.35);
}
</style>
