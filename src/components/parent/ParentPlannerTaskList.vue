<template>
  <v-list density="compact" class="bg-transparent pa-0">
    <v-list-item
      v-for="task in tasks"
      :key="task.id"
      rounded="lg"
      class="task-row mb-1"
      :class="{ 'task-row--compact': compact }"
    >
      <template #prepend>
        <span class="status-symbol">{{ statusSymbol(task.status) }}</span>
      </template>
      <v-list-item-title class="text-body-2">
        {{ task.task_name || task.subject }}
      </v-list-item-title>
      <v-list-item-subtitle v-if="!compact" class="text-caption">
        {{ task.status_label }}
        <span v-if="task.planned_at"> — {{ formatWhen(task.planned_at) }}</span>
      </v-list-item-subtitle>
      <template v-if="compact" #append>
        <v-chip size="x-small" variant="tonal" :color="statusColor(task.status)">
          {{ task.status_label }}
        </v-chip>
      </template>
    </v-list-item>
  </v-list>
</template>

<script setup>
import { useLocalizedLabels } from '../../composables/useLocalizedLabels.js'

defineProps({
  tasks: { type: Array, default: () => [] },
  compact: { type: Boolean, default: false },
})

const { dateLocale } = useLocalizedLabels()

function statusSymbol(status) {
  if (status === 'completed') return '✓'
  if (status === 'missed' || status === 'overdue') return '⚠️'
  return '⏳'
}

function statusColor(status) {
  if (status === 'completed') return 'success'
  if (status === 'missed' || status === 'overdue') return 'error'
  return 'warning'
}

function formatWhen(iso) {
  try {
    return new Date(iso).toLocaleString(dateLocale(), {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return iso
  }
}
</script>

<style scoped>
.task-row {
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.task-row--compact {
  padding-top: 4px;
  padding-bottom: 4px;
}

.status-symbol {
  width: 1.25rem;
  text-align: center;
  font-size: 0.95rem;
}
</style>
