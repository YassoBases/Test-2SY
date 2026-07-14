<template>
  <v-card class="weekly-grid glass-card pa-4 pa-md-5" variant="flat">
    <div class="d-flex align-center justify-space-between mb-4 flex-wrap gap-2">
      <div>
        <h3 class="text-h6 font-weight-bold mb-0">{{ t('common.planner.weeklyGrid.title') }}</h3>
        <p class="text-caption text-medium-emphasis mb-0">{{ t('common.planner.weeklyGrid.subtitle') }}</p>
      </div>
      <v-chip size="small" variant="tonal" color="secondary" prepend-icon="mdi-drag">
        {{ t('common.planner.weeklyGrid.draggable') }}
      </v-chip>
    </div>

    <div class="grid-scroll">
      <div class="week-header">
        <div class="time-gutter" />
        <div v-for="day in weekDays" :key="day.key" class="day-col-head">
          <span class="text-caption font-weight-bold">{{ day.label }}</span>
          <span class="text-caption text-medium-emphasis d-block">{{ day.date }}</span>
        </div>
      </div>

      <div class="week-body">
        <div class="time-gutter">
          <div v-for="h in hours" :key="h" class="time-label text-caption">{{ h }}:00</div>
        </div>
        <div
          v-for="day in weekDays"
          :key="day.key"
          class="day-col"
          @dragover.prevent
          @drop="onDrop(day.key, $event)"
        >
          <div v-for="h in hours" :key="h" class="hour-cell" />
          <div
            v-for="block in blocksForDay(day.key)"
            :key="block.uid"
            class="session-block"
            :class="[`session-block--${block.priority}`, { 'session-block--done': block.status === 'completed' }]"
            :style="blockStyle(block)"
            draggable="true"
            @dragstart="onDragStart(block)"
          >
            <span class="block-subject">{{ block.subject }}</span>
            <span v-if="block.reasoning" class="block-meta">{{ block.reasoning }}</span>
          </div>
        </div>
      </div>
    </div>
  </v-card>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  schedule: { type: Array, default: () => [] },
})

const emit = defineEmits(['update:schedule', 'reorder'])

const { t, locale, tm } = useI18n()

const hours = [16, 17, 18, 19, 20, 21]
const localBlocks = ref([])
let dragBlock = null

const weekDays = computed(() => {
  const labels = [
    t('common.days.sunday'),
    t('common.days.monday'),
    t('common.days.tuesday'),
    t('common.days.wednesday'),
    t('common.days.thursday'),
    t('common.days.friday'),
    t('common.days.saturday'),
  ]
  const start = new Date()
  start.setDate(start.getDate() - start.getDay())
  const dateLocale = locale.value === 'ar' ? 'ar-SY' : 'en'
  return labels.map((label, i) => {
    const d = new Date(start)
    d.setDate(start.getDate() + i)
    return {
      key: i,
      label,
      date: d.toLocaleDateString(dateLocale, { day: 'numeric', month: 'short' }),
    }
  })
})

function scheduleToBlocks(list) {
  return list.map((s, idx) => {
    const dt = new Date(s.scheduled_at)
    return {
      uid: `${s.id}-${idx}`,
      id: s.id,
      subject: s.subject,
      day: dt.getDay(),
      hour: dt.getHours(),
      duration: s.duration_minutes || 45,
      status: s.status,
      reasoning: s.reasoning,
      priority: s.priority >= 4 ? 'high' : s.priority >= 2 ? 'mid' : 'low',
    }
  })
}

watch(
  () => props.schedule,
  (v) => {
    localBlocks.value = scheduleToBlocks(v.length ? v : demoBlocks())
  },
  { immediate: true, deep: true },
)

function demoBlocks() {
  const subs = tm('common.planner.demoSubjects')
  const subjects = Array.isArray(subs) ? subs : ['Math', 'Chemistry', 'Physics', 'Arabic']
  return subjects.map((subject, i) => ({
    id: `demo-${i}`,
    subject,
    scheduled_at: new Date(Date.now() + (i + 1) * 86400000).toISOString(),
    duration_minutes: 45,
    status: 'planned',
    priority: i === 0 ? 5 : 2,
    reasoning: i === 0 ? t('common.planner.demoReasonWeak') : t('common.planner.demoReasonReview'),
  }))
}

function blocksForDay(dayKey) {
  return localBlocks.value.filter((b) => b.day === dayKey)
}

function blockStyle(block) {
  const startIdx = hours.indexOf(block.hour >= 16 ? block.hour : 17)
  const top = (startIdx >= 0 ? startIdx : 0) * 52 + 4
  const height = Math.max(44, Math.round((block.duration / 60) * 52))
  return { top: `${top}px`, height: `${height}px` }
}

function onDragStart(block) {
  dragBlock = block
}

function onDrop(dayKey, e) {
  e.preventDefault()
  if (!dragBlock) return
  const rect = e.currentTarget.getBoundingClientRect()
  const y = e.clientY - rect.top
  const slotIdx = Math.min(hours.length - 1, Math.max(0, Math.floor(y / 52)))
  dragBlock.day = dayKey
  dragBlock.hour = hours[slotIdx]
  localBlocks.value = [...localBlocks.value]
  emit('reorder', localBlocks.value)
  dragBlock = null
}
</script>

<style scoped>
.weekly-grid {
  border: 1px solid rgba(34, 211, 238, 0.2) !important;
  box-shadow: 0 0 48px rgba(124, 108, 240, 0.12) !important;
}

.grid-scroll {
  overflow-x: auto;
}

.week-header,
.week-body {
  display: grid;
  grid-template-columns: 48px repeat(7, minmax(72px, 1fr));
  min-width: 640px;
}

.time-gutter {
  border-inline-end: 1px solid rgba(255, 255, 255, 0.06);
}

.day-col-head {
  text-align: center;
  padding: 8px 4px;
  border-bottom: 1px solid rgba(34, 211, 238, 0.15);
}

.day-col {
  position: relative;
  min-height: 320px;
  border-inline-end: 1px solid rgba(255, 255, 255, 0.04);
}

.hour-cell {
  height: 52px;
  border-bottom: 1px dashed rgba(255, 255, 255, 0.04);
}

.time-label {
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--em-text-muted);
}

.session-block {
  position: absolute;
  left: 4px;
  right: 4px;
  border-radius: 10px;
  padding: 6px 8px;
  cursor: grab;
  z-index: 2;
  overflow: hidden;
  transition: box-shadow 0.2s, transform 0.15s;
  border: 1px solid rgba(255, 255, 255, 0.12);
}

.session-block:hover {
  transform: scale(1.02);
  box-shadow: 0 0 20px rgba(34, 211, 238, 0.35);
  z-index: 3;
}

.session-block--high {
  background: linear-gradient(135deg, rgba(124, 108, 240, 0.55), rgba(91, 79, 207, 0.4));
  box-shadow: 0 0 16px rgba(124, 108, 240, 0.3);
}

.session-block--mid {
  background: linear-gradient(135deg, rgba(34, 211, 238, 0.35), rgba(34, 211, 238, 0.15));
}

.session-block--low {
  background: rgba(255, 255, 255, 0.08);
}

.session-block--done {
  opacity: 0.5;
}

.block-subject {
  display: block;
  font-size: 0.75rem;
  font-weight: 700;
}

.block-meta {
  font-size: 0.65rem;
  opacity: 0.85;
}
</style>
