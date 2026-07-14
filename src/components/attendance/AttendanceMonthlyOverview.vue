<template>
  <div class="monthly-overview">
    <p class="text-caption font-weight-bold text-medium-emphasis mb-3">{{ t('student.attendance.monthlyOverview') }}</p>
    <v-row dense>
      <v-col v-for="week in weeks" :key="week.week_index" cols="12" sm="6">
        <div class="week-card pa-3 rounded-lg">
          <div class="d-flex justify-space-between align-center mb-2">
            <span class="text-body-2 font-weight-bold">{{ week.label }}</span>
            <v-chip size="x-small" variant="tonal" color="secondary">{{ week.consistency }}%</v-chip>
          </div>
          <div class="d-flex gap-2 text-caption">
            <span class="text-success">{{ t('student.attendance.present') }} {{ week.present }}</span>
            <span class="text-warning">{{ t('student.attendance.partial') }} {{ week.partial }}</span>
            <span class="text-error">{{ t('student.attendance.absent') }} {{ week.absent }}</span>
          </div>
          <v-progress-linear
            :model-value="week.consistency"
            color="primary"
            height="6"
            rounded
            class="mt-2"
          />
        </div>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

defineProps({
  weeks: { type: Array, default: () => [] },
})

const { t } = useI18n()
</script>

<style scoped>
.week-card {
  background: rgba(124, 108, 240, 0.08);
  border: 1px solid rgba(124, 108, 240, 0.2);
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.week-card:hover {
  border-color: rgba(34, 211, 238, 0.35);
  box-shadow: 0 0 20px rgba(34, 211, 238, 0.1);
}
</style>
