<template>
  <v-card class="glass-card pa-4 pa-md-5 planner-calendar" variant="flat">
    <div class="d-flex align-center justify-space-between mb-4 flex-wrap gap-2">
      <h3 class="text-h6 font-weight-bold mb-0">{{ t('common.planner.studyCalendarTitle') }}</h3>
      <v-chip size="small" variant="tonal" color="secondary" prepend-icon="mdi-calendar-week">
        {{ t('common.planner.sessionsCount', { count: schedule.length }) }}
      </v-chip>
    </div>

    <div v-if="loading">
      <v-skeleton-loader v-for="i in 4" :key="i" type="list-item-two-line" class="mb-2" />
    </div>

    <div v-else-if="groupedDays.length" class="calendar-days">
      <div v-for="day in groupedDays" :key="day.label" class="day-group mb-4">
        <p class="text-caption font-weight-bold text-medium-emphasis mb-2 day-label">{{ day.label }}</p>
        <div
          v-for="slot in day.slots"
          :key="slot.id"
          class="slot-row d-flex align-center gap-3 pa-3 rounded-lg mb-2"
          :class="{ 'slot-row--done': slot.status === 'completed' }"
        >
          <div class="slot-time text-caption font-weight-bold">{{ formatTime(slot.scheduled_at) }}</div>
          <div class="flex-grow-1">
            <p class="text-body-2 font-weight-medium mb-0">{{ slot.subject }}</p>
            <p v-if="slot.reasoning" class="text-caption text-medium-emphasis mb-0">{{ slot.reasoning }}</p>
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
    </div>

    <v-card v-else class="pa-8 text-center bg-transparent" variant="flat">
      <v-icon size="48" color="grey" class="mb-2">mdi-calendar-blank</v-icon>
      <p class="text-body-2 text-medium-emphasis mb-0">
        {{ t('common.planner.studyCalendarEmpty') }}
      </p>
    </v-card>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  schedule: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
})

defineEmits(['complete'])

const { t, locale } = useI18n()

const groupedDays = computed(() => {
  const map = new Map()
  const dateLocale = locale.value === 'ar' ? 'ar-SY' : 'en'
  for (const slot of props.schedule) {
    const d = new Date(slot.scheduled_at)
    const label = d.toLocaleDateString(dateLocale, { weekday: 'long', day: 'numeric', month: 'short' })
    if (!map.has(label)) map.set(label, { label, slots: [] })
    map.get(label).slots.push(slot)
  }
  return [...map.values()]
})

function formatTime(iso) {
  const timeLocale = locale.value === 'ar' ? 'ar-SY' : 'en'
  return new Date(iso).toLocaleTimeString(timeLocale, { hour: '2-digit', minute: '2-digit' })
}

function statusColor(status) {
  return { planned: 'primary', completed: 'success', missed: 'error' }[status] || 'grey'
}

function statusLabel(status) {
  return t(`common.planner.slotStatus.${status}`, status)
}
</script>

<style scoped>
.slot-row {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.slot-row--done {
  opacity: 0.65;
}

.slot-time {
  min-width: 52px;
  color: rgb(var(--v-theme-secondary));
}

.day-label {
  letter-spacing: 0.02em;
}
</style>
