<template>
  <v-card class="glass-card pa-4" variant="flat">
    <h3 class="text-subtitle-1 font-weight-bold mb-3">{{ t('common.planner.lifeEventsTitle') }}</h3>
    <v-row v-if="events.length" dense>
      <v-col v-for="ev in events" :key="ev.id" cols="12" sm="6">
        <v-card class="event-card pa-3" variant="flat">
          <div class="d-flex align-center gap-2 mb-1">
            <v-icon size="18" :color="typeColor(ev.event_type)">{{ typeIcon(ev.event_type) }}</v-icon>
            <span class="text-body-2 font-weight-medium">{{ ev.title }}</span>
          </div>
          <p class="text-caption text-medium-emphasis mb-0">
            {{ eventMeta(ev) }}
          </p>
        </v-card>
      </v-col>
    </v-row>
    <p v-else class="text-caption text-medium-emphasis mb-0">
      {{ t('common.planner.lifeEventsEmpty') }}
    </p>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

defineProps({
  events: { type: Array, default: () => [] },
})

const { t, locale } = useI18n()

const TYPE_META = {
  school: { icon: 'mdi-school', color: 'info' },
  private_lesson: { icon: 'mdi-account-tie', color: 'primary' },
  exam: { icon: 'mdi-file-document-alert', color: 'error' },
  sport: { icon: 'mdi-soccer', color: 'success' },
  family: { icon: 'mdi-home-heart', color: 'warning' },
  social: { icon: 'mdi-account-group', color: 'secondary' },
  religious: { icon: 'mdi-mosque', color: 'info' },
  other: { icon: 'mdi-calendar', color: 'grey' },
}

const dayNames = computed(() => [
  t('common.days.monday'),
  t('common.days.tuesday'),
  t('common.days.wednesday'),
  t('common.days.thursday'),
  t('common.days.friday'),
  t('common.days.saturday'),
  t('common.days.sunday'),
])

function typeIcon(type) {
  return TYPE_META[type]?.icon || 'mdi-calendar'
}

function typeColor(type) {
  return TYPE_META[type]?.color || 'grey'
}

function eventMeta(ev) {
  const parts = []
  if (ev.event_date) {
    parts.push(formatEventDate(ev.event_date))
  } else if (ev.day_of_week != null) {
    parts.push(dayNames.value[ev.day_of_week] || '')
  }
  if (ev.start_time) parts.push(ev.start_time)
  if (ev.subject) parts.push(ev.subject)
  return parts.filter(Boolean).join(' · ') || t('common.planner.reservedSlot')
}
function formatEventDate(value) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  const dateLocale = locale.value === 'ar' ? 'ar-SY' : 'en'
  return date.toLocaleDateString(dateLocale, { weekday: 'short', day: 'numeric', month: 'short' })
}
</script>

<style scoped>
.event-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
}
</style>
