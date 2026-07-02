<template>
  <div v-if="slots.length" class="d-flex flex-column gap-2">
    <div
      v-for="slot in slots"
      :key="slot.id"
      class="planner-slot d-flex align-center gap-3 pa-3 rounded-lg"
      :class="{ 'planner-slot--done': slot.status === 'completed' }"
    >
      <div class="text-caption font-weight-bold planner-slot__time">
        {{ formatTime(slot.scheduled_at) }}
      </div>
      <div class="flex-grow-1 min-w-0">
        <p class="text-body-2 font-weight-medium mb-0">{{ slot.subject }}</p>
        <p v-if="slot.reasoning" class="text-caption text-medium-emphasis mb-0 text-truncate">
          {{ slot.reasoning }}
        </p>
      </div>
      <v-chip size="x-small" :color="statusColor(slot.status)" variant="tonal">
        {{ statusLabel(slot.status) }}
      </v-chip>
      <v-btn
        v-if="slot.status === 'planned'"
        icon="mdi-check"
        size="small"
        variant="tonal"
        color="success"
        @click="$emit('complete', slot.id)"
      />
    </div>
  </div>
  <div v-else class="text-center py-4">
    <v-icon :icon="emptyIcon" size="40" color="grey" class="mb-2" />
    <p class="text-body-2 text-medium-emphasis mb-0">{{ emptyText }}</p>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

defineProps({
  slots: { type: Array, default: () => [] },
  emptyIcon: { type: String, default: 'mdi-calendar-blank' },
  emptyText: { type: String, default: '' },
})

defineEmits(['complete'])

const { t, locale } = useI18n()

function formatTime(iso) {
  return new Date(iso).toLocaleTimeString(locale.value === 'ar' ? 'ar-SY' : 'en-US', {
    hour: '2-digit',
    minute: '2-digit',
  })
}

function statusColor(status) {
  return { planned: 'primary', completed: 'success', missed: 'error' }[status] || 'grey'
}

function statusLabel(status) {
  const key = `common.planner.slotStatus.${status}`
  const translated = t(key)
  return translated !== key ? translated : status
}
</script>

<style scoped>
.planner-slot {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(124, 108, 240, 0.12);
}

.planner-slot--done {
  opacity: 0.72;
}

.planner-slot__time {
  min-width: 52px;
  color: var(--em-cyan);
}
</style>
