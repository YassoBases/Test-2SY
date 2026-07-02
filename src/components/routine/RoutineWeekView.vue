<template>
  <v-card class="glass-card" variant="flat">
    <div class="d-flex align-center justify-space-between pa-4 pb-0">
      <h3 class="text-h6 font-weight-bold">{{ t('common.routine.weeklyProgram') }}</h3>
      <v-btn size="small" variant="tonal" color="primary" :loading="loading" prepend-icon="mdi-refresh" @click="$emit('refresh')">
        {{ t('common.refresh') }}
      </v-btn>
    </div>

    <v-tabs v-model="activeDay" density="compact" color="primary" class="mt-2">
      <v-tab v-for="day in weekDays" :key="day.key" :value="day.key">
        {{ day.label }}
      </v-tab>
    </v-tabs>

    <v-window v-model="activeDay">
      <v-window-item v-for="day in weekDays" :key="day.key" :value="day.key">
        <div class="pa-4">
          <div v-if="slotsForDay(day.key).length === 0" class="text-center py-8 text-medium-emphasis">
            <v-icon size="40" class="mb-2">mdi-calendar-blank</v-icon>
            <p>{{ t('common.routine.noProgramToday') }}</p>
          </div>
          <div v-else>
            <div v-for="slot in slotsForDay(day.key)" :key="slot.start"
              class="slot-item d-flex align-center gap-3 pa-3 rounded-lg mb-2"
              :class="`slot--${slot.type}`">
              <div class="slot-time text-caption font-weight-bold">
                {{ slot.start }}<br>{{ slot.end }}
              </div>
              <div class="flex-grow-1">
                <p class="text-body-2 font-weight-bold mb-0">{{ slot.title }}</p>
                <p v-if="slot.subject" class="text-caption text-medium-emphasis mb-0">{{ slot.subject }}</p>
              </div>
              <v-icon :color="typeColor(slot.type)" size="20">{{ typeIcon(slot.type) }}</v-icon>
            </div>
          </div>
        </div>
      </v-window-item>
    </v-window>
  </v-card>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  days: { type: Object, default: () => ({}) },
  loading: { type: Boolean, default: false },
})
defineEmits(['refresh'])

const { t } = useI18n()

const activeDay = ref(0)

const weekDays = computed(() => [
  { key: 0, label: t('common.days.monday') },
  { key: 1, label: t('common.days.tuesday') },
  { key: 2, label: t('common.days.wednesday') },
  { key: 3, label: t('common.days.thursday') },
  { key: 4, label: t('common.days.friday') },
  { key: 5, label: t('common.days.saturday') },
  { key: 6, label: t('common.days.sunday') },
])

function slotsForDay(key) {
  return (props.days[String(key)] || []).sort((a, b) => a.start.localeCompare(b.start))
}

function typeColor(type) {
  return { school: 'primary', study: 'secondary', sport: 'success', meal: 'warning',
    sleep: 'info', prayer: 'deep-orange', family: 'pink', private_lesson: 'purple', free: 'teal' }[type] || 'grey'
}

function typeIcon(type) {
  return { school: 'mdi-school', study: 'mdi-book-open', sport: 'mdi-run', meal: 'mdi-food',
    sleep: 'mdi-sleep', prayer: 'mdi-mosque', family: 'mdi-home-heart',
    private_lesson: 'mdi-account-school', free: 'mdi-gamepad-variant' }[type] || 'mdi-calendar'
}
</script>

<style scoped>
.slot-item { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); transition: 0.2s; }
.slot-item:hover { background: rgba(255,255,255,0.07); }
.slot-time { min-width: 52px; color: rgb(var(--v-theme-secondary)); font-size: 0.72rem; text-align: center; }
.slot--school { border-left: 3px solid rgb(var(--v-theme-primary)); }
.slot--study { border-left: 3px solid rgb(var(--v-theme-secondary)); }
.slot--sport { border-left: 3px solid rgb(var(--v-theme-success)); }
.slot--sleep { border-left: 3px solid rgb(var(--v-theme-info)); }
.slot--meal { border-left: 3px solid rgb(var(--v-theme-warning)); }
</style>
