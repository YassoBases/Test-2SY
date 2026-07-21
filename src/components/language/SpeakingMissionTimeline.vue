<template>
  <section
    v-if="items.length"
    class="mission-timeline glass-card"
    :class="compact ? 'mission-timeline--compact pa-4' : 'pa-5 mb-5'"
    :aria-label="t('student.languages.speakingJourney.timeline.title')"
  >
    <div class="text-subtitle-2 font-weight-bold mb-3">
      {{
        compact
          ? t('student.languages.speakingJourney.timeline.railTitle')
          : t('student.languages.speakingJourney.timeline.title')
      }}
    </div>
    <ol class="timeline">
      <li
        v-for="(item, idx) in items"
        :key="itemKey(item, idx)"
        class="timeline-item"
        :class="[
          `timeline-item--${normalizeStatus(item.status)}`,
          { 'timeline-item--compact': compact },
        ]"
      >
        <div class="timeline-rail" aria-hidden="true">
          <span class="timeline-dot">
            <v-icon size="16">{{ iconFor(item) }}</v-icon>
          </span>
          <span v-if="idx < items.length - 1" class="timeline-line" />
        </div>
        <div class="timeline-body">
          <div class="d-flex flex-wrap align-center gap-2 mb-1">
            <div class="text-body-2 font-weight-medium">{{ displayTitle(item) }}</div>
            <v-chip
              v-if="normalizeStatus(item.status) === 'active'"
              size="x-small"
              color="primary"
              variant="flat"
            >
              {{ t('student.languages.speakingJourney.timeline.now') }}
            </v-chip>
            <v-chip
              v-else-if="normalizeStatus(item.status) === 'done'"
              size="x-small"
              color="success"
              variant="tonal"
            >
              {{ t('student.languages.speakingJourney.timeline.done') }}
            </v-chip>
            <v-chip v-else size="x-small" variant="outlined">
              {{ t('student.languages.speakingJourney.timeline.upcoming') }}
            </v-chip>
          </div>
          <div v-if="!compact || normalizeStatus(item.status) === 'active'" class="text-caption text-medium-emphasis">
            {{ item.purpose }}
          </div>
          <v-chip
            v-if="(item.is_task_bearing || item.is_live) && (!compact || normalizeStatus(item.status) === 'active')"
            size="x-small"
            class="mt-2"
            variant="tonal"
            color="secondary"
          >
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
import { missionKindMeta } from '../../utils/speakingRuntimeMeta.js'
import { educationalMissionTitle } from '../../utils/speakingFraming.js'

const props = defineProps({
  learningPath: { type: Array, default: () => [] },
  todayMissions: { type: Array, default: () => [] },
  lessonTitle: { type: String, default: '' },
  compact: { type: Boolean, default: false },
})

const { t } = useI18n()

function displayTitle(item) {
  return educationalMissionTitle(item?.title, props.lessonTitle, t)
}

function normalizeStatus(status) {
  const s = String(status || '').toLowerCase()
  if (s === 'done' || s === 'completed') return 'done'
  if (s === 'active' || s === 'current') return 'active'
  return 'upcoming'
}

/** Prefer S12 learning_path; fall back to today_missions with order-aware statuses. */
const items = computed(() => {
  if (props.learningPath?.length) return props.learningPath
  const missions = props.todayMissions || []
  const activeIdx = missions.findIndex((m) => m.is_executable || m.is_live)
  return missions.map((m, idx) => {
    let status = 'upcoming'
    if (activeIdx >= 0) {
      if (idx < activeIdx) status = 'done'
      else if (idx === activeIdx) status = 'active'
    } else if (idx === 0) {
      status = 'upcoming'
    }
    return {
      title: m.title,
      purpose: m.execution_mode || m.kind || '',
      status,
      kind: m.kind,
      is_task_bearing: m.is_executable,
      is_live: m.is_live,
    }
  })
})

function iconFor(item) {
  const status = normalizeStatus(item.status)
  if (status === 'done') return 'mdi-check'
  if (status === 'active') return 'mdi-play'
  if (item.is_live) return 'mdi-account-voice'
  return missionKindMeta(item.kind).icon
}

function itemKey(item, idx) {
  return item.mission_id || item.step_id || `${item.title || 'm'}-${item.status || ''}-${idx}`
}
</script>

<style scoped>
.mission-timeline {
  border-radius: var(--em-radius-md, 16px);
}
.mission-timeline--compact {
  max-height: min(70vh, 560px);
  overflow: auto;
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
  transition: opacity 180ms ease, transform 180ms ease;
}
.timeline-item--compact {
  min-height: 52px;
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
.timeline-item--active .timeline-dot {
  background: rgba(var(--v-theme-primary), 0.18);
  color: rgb(var(--v-theme-primary));
}
.timeline-item--done .timeline-dot {
  background: rgba(var(--v-theme-success), 0.18);
  color: rgb(var(--v-theme-success));
}
.timeline-line {
  flex: 1;
  width: 2px;
  margin: 4px 0;
  background: rgba(var(--v-theme-on-surface), 0.12);
}
.timeline-item--active .timeline-body {
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
