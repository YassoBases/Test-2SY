<template>
  <v-expansion-panels v-model="openPanel" variant="accordion" class="week-panels">
    <v-expansion-panel
      v-for="i in orderedDayIndices" :key="i"
      :value="i"
      class="week-day-panel" :class="{ 'is-today': i === todayIndex }"
    >
      <v-expansion-panel-title>
        <span class="week-day-name">{{ dayLabels[i] }}</span>
        <span v-if="i === todayIndex" class="week-day-today-badge">{{ t('common.routine.today') }}</span>
        <v-spacer />
        <span v-if="slotsForDay(i).length === 0" class="week-day-count text-disabled">{{ t('common.routine.emptyDay') }}</span>
        <span v-else class="week-day-count">{{ t('common.routine.activities', { count: slotsForDay(i).length }) }}</span>
      </v-expansion-panel-title>

      <v-expansion-panel-text>
        <div v-if="slotsForDay(i).length === 0" class="week-day-empty">
          <v-icon size="22" color="grey">mdi-weather-sunny</v-icon>
          <span>{{ t('common.routine.emptyDay') }}</span>
        </div>

        <v-table v-else density="comfortable" class="week-table">
          <thead>
            <tr>
              <th class="text-start">{{ t('common.routine.time') }}</th>
              <th class="text-start">{{ t('common.routine.activity') }}</th>
              <th class="text-start">{{ t('common.routine.subject') }}</th>
              <th class="text-start">{{ t('common.routine.status') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="slot in slotsForDay(i)" :key="slot.id || slot.start"
              :class="slotRowClass(slot)"
            >
              <td class="week-table-time">{{ slot.start }} – {{ slot.end }}</td>
              <td>
                <div class="d-flex align-center ga-2">
                  <v-icon :color="typeColor(slot.type)" size="16">{{ typeIcon(slot.type) }}</v-icon>
                  <span :class="{ 'text-decoration-line-through text-disabled': slot.status === 'missed' }">
                    {{ displayTitle(slot) }}
                  </span>
                </div>
              </td>
              <td>
                <v-chip v-if="slot.subject" size="x-small" variant="tonal" color="primary">
                  {{ slot.subject }}
                </v-chip>
                <span v-else>—</span>
              </td>
              <td>
                <div class="d-flex align-center ga-1">
                  <v-chip v-if="slot.status === 'completed'" size="x-small" color="success" variant="flat">
                    <v-icon size="11" start>mdi-check</v-icon>{{ t('common.planner.slotStatus.completed') }}
                  </v-chip>
                  <v-chip v-else-if="slot.status === 'missed'" size="x-small" color="error" variant="flat">
                    <v-icon size="11" start>mdi-close</v-icon>{{ t('common.planner.slotStatus.missed') }}
                  </v-chip>
                  <template v-else-if="interactive && slot.id">
                    <v-btn
                      size="x-small" color="success" variant="tonal" icon="mdi-check"
                      :loading="loadingSlot === slot.id + '_complete'"
                      @click.stop="emit('complete', slot.id)"
                    />
                    <v-btn
                      size="x-small" color="error" variant="tonal" icon="mdi-close"
                      :loading="loadingSlot === slot.id + '_miss'"
                      @click.stop="emit('miss', slot.id)"
                    />
                  </template>
                  <v-chip v-else size="x-small" variant="tonal" color="grey">{{ t('common.planner.slotStatus.planned') }}</v-chip>
                  <v-btn
                    v-if="interactive && slot.id && slot.status !== 'planned'"
                    size="x-small" variant="text" icon="mdi-refresh"
                    :loading="loadingSlot === slot.id + '_undo'"
                    @click.stop="emit('undo', slot.id)"
                  />
                </div>
              </td>
            </tr>
          </tbody>
        </v-table>

        <div v-if="interactive && slotsForDay(i).length > 0" class="week-day-summary">
          <span><v-icon size="12" color="success">mdi-check-circle</v-icon>{{ daySummary(i).completed }}</span>
          <span><v-icon size="12" color="error">mdi-close-circle</v-icon>{{ daySummary(i).missed }}</span>
          <span><v-icon size="12" color="grey">mdi-clock-outline</v-icon>{{ daySummary(i).planned }}</span>
        </div>
      </v-expansion-panel-text>
    </v-expansion-panel>
  </v-expansion-panels>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  days: { type: Object, default: () => ({}) },
  interactive: { type: Boolean, default: false },
  loadingSlot: { type: String, default: null },
})

const emit = defineEmits(['complete', 'miss', 'undo'])

const { t, locale } = useI18n()

const jsDay = new Date().getDay()
const todayIndex = jsDay === 0 ? 6 : jsDay - 1

const dayLabels = computed(() => [
  t('common.days.monday'),
  t('common.days.tuesday'),
  t('common.days.wednesday'),
  t('common.days.thursday'),
  t('common.days.friday'),
  t('common.days.saturday'),
  t('common.days.sunday'),
])

const orderedDayIndices = Array.from({ length: 7 }, (_, n) => (todayIndex + n) % 7)

const openPanel = ref(todayIndex)

const sortedSlotsByDay = computed(() => {
  const days = props.days || {}
  const out = {}
  for (let i = 0; i < 7; i++) {
    const slots = days[String(i)]
    out[i] = Array.isArray(slots) && slots.length
      ? [...slots].sort((a, b) => a.start.localeCompare(b.start))
      : []
  }
  return out
})

function slotsForDay(i) {
  return sortedSlotsByDay.value[i] || []
}

function daySummary(i) {
  const slots = slotsForDay(i)
  return {
    completed: slots.filter((s) => s.status === 'completed').length,
    missed: slots.filter((s) => s.status === 'missed').length,
    planned: slots.filter((s) => s.status === 'planned').length,
  }
}

function typeColor(type) {
  const map = { school:'blue', study:'purple', sport:'green', meal:'orange', sleep:'indigo', prayer:'teal', family:'pink', private_lesson:'deep-purple', free:'grey', other:'grey' }
  return map[type] || 'grey'
}

function typeIcon(type) {
  const map = { school:'mdi-school', study:'mdi-book-open', sport:'mdi-run', meal:'mdi-food', sleep:'mdi-sleep', prayer:'mdi-hands-pray', family:'mdi-home-heart', private_lesson:'mdi-account-school', free:'mdi-coffee', other:'mdi-calendar' }
  return map[type] || 'mdi-calendar'
}

function slotRowClass(slot) {
  if (slot.status === 'completed') return 'week-row-completed'
  if (slot.status === 'missed') return 'week-row-missed'
  return ''
}

function displayTitle(slot) {
  const title = String(slot?.title || '').trim()
  const subject = String(slot?.subject || '').trim()
  if (!title || locale.value !== 'en') return title

  const exactMap = {
    'فطور': 'Breakfast',
    'المدرسة': 'School',
    'غداء وراحة قصيرة': 'Lunch & short break',
    'غداء': 'Lunch',
    'راحة أو مشي خفيف': 'Rest or light walk',
    'عشاء': 'Dinner',
    'وقت العائلة وتجهيز الغد': 'Family time & prep for tomorrow',
    'نوم': 'Sleep',
    'مراجعة عامة': 'General review',
    'موعد': 'Appointment',
    'بعد وصول الطالب إلى البيت': 'After getting home',
  }
  if (exactMap[title]) return exactMap[title]

  if (title.startsWith('مراجعة مركزة ')) return `Focused review ${subject || title.slice('مراجعة مركزة '.length)}`
  if (title.startsWith('مراجعة ')) return `Review ${subject || title.slice('مراجعة '.length)}`
  if (title.startsWith('حل واجبات ')) return `Homework ${subject || title.slice('حل واجبات '.length)}`
  if (title.startsWith('تدريب ')) return `Practice ${subject || title.slice('تدريب '.length)}`

  return title
}
</script>

<style scoped>
.week-panels {
  background: transparent;
}
.week-day-panel {
  border: 1px solid rgba(255,255,255,0.06) !important;
  border-radius: 14px !important;
  overflow: hidden;
  margin-bottom: 10px;
  background: rgba(255,255,255,0.02) !important;
}
.week-day-panel.is-today {
  border-color: rgba(34,211,238,0.35) !important;
}
.week-day-name { font-size: 16px; font-weight: 700; }
.week-day-today-badge {
  font-size: 11px;
  font-weight: 700;
  padding: 3px 10px;
  margin-inline-start: 10px;
  border-radius: 999px;
  background: rgba(34,211,238,0.18);
  color: rgb(34,211,238);
  letter-spacing: 0.2px;
}
.week-day-count {
  font-size: 12px;
  color: rgba(255,255,255,0.5);
}
.week-day-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 28px 0;
  color: rgba(255,255,255,0.28);
  font-size: 12px;
}
.week-table {
  background: transparent;
}
.week-table :deep(th) {
  font-size: 12px;
  font-weight: 700;
  color: rgba(255,255,255,0.5);
}
.week-table :deep(td) {
  font-size: 13px;
}
.week-table-time {
  font-weight: 700;
  white-space: nowrap;
}
.week-row-completed { background: rgba(76,175,80,0.06); }
.week-row-missed { background: rgba(244,67,54,0.04); opacity: 0.75; }
.week-day-summary {
  display: flex;
  gap: 16px;
  padding: 10px 4px 0;
  font-size: 12px;
  color: rgba(255,255,255,0.5);
}
.week-day-summary span { display: flex; align-items: center; gap: 4px; }
</style>
