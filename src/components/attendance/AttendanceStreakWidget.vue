<template>
  <div class="streak-widget metric-card pa-4 rounded-lg text-center">
    <v-icon color="orange" size="28" class="mb-2 streak-icon">mdi-fire</v-icon>
    <div class="text-h4 font-weight-bold">{{ streakDays }}</div>
    <p class="text-caption text-medium-emphasis mb-0">{{ t('student.attendance.consecutiveDays') }}</p>
    <p class="text-caption mt-1 mb-0" style="color: var(--em-cyan)">
      {{ t('student.attendance.attendancePercent', { n: attendancePercentage }) }}
    </p>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

defineProps({
  streakDays: { type: Number, default: 0 },
  attendancePercentage: { type: Number, default: 0 },
})

const { t } = useI18n()
</script>

<style scoped>
.streak-widget {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 152, 0, 0.25);
  box-shadow: 0 0 24px rgba(255, 152, 0, 0.1);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.streak-widget:hover {
  transform: translateY(-2px);
  box-shadow: 0 0 32px rgba(255, 152, 0, 0.18);
}

.streak-icon {
  filter: drop-shadow(0 0 8px rgba(255, 152, 0, 0.5));
}
</style>
