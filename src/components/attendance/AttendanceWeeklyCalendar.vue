<template>
  <div class="weekly-cal">
    <p class="text-caption font-weight-bold text-medium-emphasis mb-3">{{ t('student.attendance.weeklyCalendar') }}</p>
    <div class="cal-grid">
      <div
        v-for="day in days"
        :key="day.date"
        class="cal-day pa-2 rounded-lg"
        :class="[`cal-day--${day.status}`, { 'cal-day--active': day.active }]"
      >
        <p class="text-caption font-weight-bold mb-1">{{ day.day_label }}</p>
        <v-icon size="20" :color="statusColor(day.status)">
          {{ statusIcon(day.status) }}
        </v-icon>
        <p v-if="day.study_minutes" class="text-caption mb-0 mt-1">
          {{ t('student.attendance.minutesShort', { n: day.study_minutes }) }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

defineProps({
  days: { type: Array, default: () => [] },
})

const { t } = useI18n()

function statusIcon(status) {
  return { present: 'mdi-check-circle', partial: 'mdi-circle-half-full', absent: 'mdi-close-circle' }[status] || 'mdi-help-circle'
}

function statusColor(status) {
  return { present: 'success', partial: 'warning', absent: 'grey' }[status] || 'grey'
}
</script>

<style scoped>
.cal-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 8px;
}

.cal-day {
  text-align: center;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.cal-day--present {
  border-color: rgba(52, 211, 153, 0.35);
}

.cal-day--partial {
  border-color: rgba(251, 191, 36, 0.35);
}

.cal-day--absent {
  opacity: 0.65;
}

.cal-day--active {
  box-shadow: 0 0 12px rgba(34, 211, 238, 0.15);
}
</style>
