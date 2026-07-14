<template>
  <section v-if="items.length" class="mission-timeline glass-card pa-5 mb-5" aria-label="mission timeline">
    <div class="text-subtitle-1 font-weight-bold mb-4">
      {{ t('student.languages.speakingJourney.timeline.title') }}
    </div>
    <ol class="timeline">
      <li
        v-for="(item, idx) in items"
        :key="idx"
        class="timeline-item"
        :class="`timeline-item--${item.status || 'upcoming'}`"
      >
        <div class="timeline-rail" aria-hidden="true">
          <span class="timeline-dot">
            <v-icon size="16">{{ iconFor(item) }}</v-icon>
          </span>
          <span v-if="idx < items.length - 1" class="timeline-line" />
        </div>
        <div class="timeline-body">
          <div class="d-flex flex-wrap align-center gap-2 mb-1">
            <div class="text-body-2 font-weight-medium">{{ item.title }}</div>
            <v-chip v-if="item.status === 'active' || item.status === 'current'" size="x-small" color="primary" variant="flat">
              {{ t('student.languages.speakingJourney.timeline.now') }}
            </v-chip>
            <v-chip v-else-if="item.status === 'done' || item.status === 'completed'" size="x-small" color="success" variant="tonal">
              {{ t('student.languages.speakingJourney.timeline.done') }}
            </v-chip>
            <v-chip v-else size="x-small" variant="outlined">
              {{ t('student.languages.speakingJourney.timeline.upcoming') }}
            </v-chip>
          </div>
          <div class="text-caption text-medium-emphasis">{{ item.purpose }}</div>
          <v-chip v-if="item.is_task_bearing || item.is_live" size="x-small" class="mt-2" variant="tonal" color="secondary">
            {{
              item.is_live
                ? t('student.languages.speakingJourney.mission.usesAlex')
                : t('student.languages.speakingJourney.path.taskBearing')
            }}
          </v-chip>
        </div>
      </li>
    </ol>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  learningPath: { type: Array, default: () => [] },
  todayMissions: { type: Array, default: () => [] },
})

const { t } = useI18n()

/** Prefer S12 learning_path; fall back to today_missions list as upcoming. */
const items = computed(() => {
  if (props.learningPath?.length) return props.learningPath
  return (props.todayMissions || []).map((m) => ({
    title: m.title,
    purpose: m.execution_mode || m.kind || '',
    status: 'upcoming',
    is_task_bearing: m.is_executable,
    is_live: m.is_live,
  }))
})

function iconFor(item) {
  if (item.status === 'done' || item.status === 'completed') return 'mdi-check'
  if (item.status === 'active' || item.status === 'current') return 'mdi-play'
  if (item.is_live) return 'mdi-account-voice'
  return 'mdi-circle-outline'
}
</script>

<style scoped>
.mission-timeline {
  border-radius: var(--em-radius-md, 16px);
}
.timeline {
  list-style: none;
  margin: 0;
  padding: 0;
}
.timeline-item {
  display: flex;
  gap: 14px;
  min-height: 64px;
}
.timeline-rail {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 28px;
  flex-shrink: 0;
}
.timeline-dot {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: rgba(var(--v-theme-on-surface), 0.06);
  color: rgba(var(--v-theme-on-surface), 0.55);
}
.timeline-item--active .timeline-dot,
.timeline-item--current .timeline-dot {
  background: rgba(var(--v-theme-primary), 0.18);
  color: rgb(var(--v-theme-primary));
}
.timeline-item--done .timeline-dot,
.timeline-item--completed .timeline-dot {
  background: rgba(var(--v-theme-success), 0.18);
  color: rgb(var(--v-theme-success));
}
.timeline-line {
  flex: 1;
  width: 2px;
  margin: 4px 0;
  background: rgba(var(--v-theme-on-surface), 0.12);
}
.timeline-item--active .timeline-body,
.timeline-item--current .timeline-body {
  background: rgba(var(--v-theme-primary), 0.06);
  border-radius: 12px;
  padding: 8px 12px;
}
.timeline-item--upcoming {
  opacity: 0.72;
}
@media (prefers-reduced-motion: no-preference) {
  .timeline-item--active .timeline-dot {
    animation: pulse-soft 1.8s ease-in-out infinite;
  }
}
@keyframes pulse-soft {
  0%,
  100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.06);
  }
}
</style>
