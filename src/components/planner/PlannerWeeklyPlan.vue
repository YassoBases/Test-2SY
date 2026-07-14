<template>
  <v-card class="glass-card glass-card--solid pa-4" variant="flat">
    <div v-if="weeklyPlan.length" class="weekly-plan">
      <div v-for="day in weeklyPlan" :key="day.day_name" class="weekly-plan__day mb-4">
        <div class="d-flex align-center gap-2 mb-2">
          <v-icon size="18" color="secondary">mdi-calendar-today</v-icon>
          <span class="text-subtitle-2 font-weight-bold">{{ day.day_name }}</span>
        </div>
        <ul class="weekly-plan__tasks mb-0">
          <li
            v-for="task in day.tasks"
            :key="task.id"
            class="weekly-plan__task d-flex align-center gap-2 py-2"
          >
            <span class="weekly-plan__priority">{{ task.priority_icon || '•' }}</span>
            <span class="text-body-2 flex-grow-1">{{ task.task_label || taskLabel(task) }}</span>
            <v-chip v-if="!readOnly && task.status === 'planned'" size="x-small" variant="tonal" color="primary">
              {{ t('common.planner.minutesShort', { n: task.duration_minutes }) }}
            </v-chip>
            <v-btn
              v-if="!readOnly && task.status === 'planned'"
              icon="mdi-check"
              size="x-small"
              variant="tonal"
              color="success"
              @click="$emit('complete', task.id)"
            />
          </li>
        </ul>
      </div>
    </div>
    <p v-else class="text-body-2 text-medium-emphasis mb-0 text-center py-4">
      {{ t('common.planner.weeklyPlanEmpty') }}
    </p>
  </v-card>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

defineProps({
  weeklyPlan: { type: Array, default: () => [] },
  readOnly: { type: Boolean, default: false },
})

defineEmits(['complete'])

const { t } = useI18n()

function taskLabel(task) {
  return t('common.planner.taskMinutes', {
    subject: task.subject,
    minutes: task.duration_minutes || 45,
  })
}
</script>

<style scoped>
.weekly-plan__tasks {
  list-style: none;
  padding: 0 1rem 0 0;
  margin: 0;
}

.weekly-plan__task {
  border-bottom: 1px solid rgba(124, 108, 240, 0.1);
}

.weekly-plan__task:last-child {
  border-bottom: none;
}

.weekly-plan__priority {
  min-width: 1.25rem;
  text-align: center;
}
</style>
