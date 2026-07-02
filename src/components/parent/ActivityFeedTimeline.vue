<template>
  <div class="activity-feed">
    <div v-if="loading" class="py-2">
      <v-skeleton-loader
        v-for="i in 5"
        :key="i"
        type="list-item-avatar-two-line"
        class="mb-3 rounded-lg"
      />
    </div>

    <v-timeline v-else side="end" align="start" truncate-line="both" density="compact" class="feed-timeline">
      <v-timeline-item
        v-for="item in items"
        :key="item.id"
        :dot-color="iconMeta(item.event_type).color"
        size="small"
        fill-dot
      >
        <template #icon>
          <v-icon size="16" color="white">{{ iconMeta(item.event_type).icon }}</v-icon>
        </template>

        <v-card class="feed-card glass-card pa-3" variant="flat">
          <div class="d-flex align-start justify-space-between gap-2 flex-wrap">
            <p class="text-body-2 font-weight-medium mb-1 feed-title">{{ item.title }}</p>
            <span class="text-caption text-medium-emphasis feed-time">{{ item.relative_time }}</span>
          </div>
          <p v-if="item.description" class="text-caption text-medium-emphasis mb-0">
            {{ item.description }}
          </p>
        </v-card>
      </v-timeline-item>
    </v-timeline>

    <v-card v-if="!loading && !items.length" class="glass-card pa-8 text-center" variant="flat">
      <v-icon size="48" color="grey" class="mb-2">mdi-timeline-clock-outline</v-icon>
      <p class="text-body-2 text-medium-emphasis mb-0">{{ t('parent.activity.empty') }}</p>
    </v-card>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

defineProps({
  items: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
})

const { t } = useI18n()

const EVENT_ICONS = {
  quiz_submitted: { icon: 'mdi-clipboard-check', color: 'primary' },
  study_session_completed: { icon: 'mdi-book-check', color: 'success' },
  study_streak: { icon: 'mdi-fire', color: 'orange' },
  no_study_today: { icon: 'mdi-calendar-remove', color: 'warning' },
  planner_generated: { icon: 'mdi-calendar-star', color: 'secondary' },
  weak_subject_alert: { icon: 'mdi-alert', color: 'error' },
  lesson_activity: { icon: 'mdi-school', color: 'info' },
  performance_improved: { icon: 'mdi-trending-up', color: 'success' },
  weekly_summary: { icon: 'mdi-chart-bar', color: 'primary' },
}

function iconMeta(type) {
  return EVENT_ICONS[type] || { icon: 'mdi-circle-small', color: 'grey' }
}
</script>

<style scoped>
.feed-timeline {
  direction: rtl;
}

.feed-card {
  border-inline-start: 3px solid rgba(var(--v-theme-primary), 0.35);
}

.feed-title {
  line-height: 1.5;
}

.feed-time {
  white-space: nowrap;
}

@media (max-width: 600px) {
  .feed-timeline :deep(.v-timeline-item__body) {
    padding-inline-start: 8px;
  }
}
</style>
