<template>
  <AppCard id="daily-focus" class="daily-focus" solid padding="lg">
    <div class="daily-focus__head">
      <div>
        <p class="daily-focus__eyebrow">{{ t('student.home.dailyFocus.eyebrow') }}</p>
        <h2 class="daily-focus__title">{{ focus.mission }}</h2>
      </div>
      <v-chip size="small" color="primary" variant="tonal">{{ focus.target }}</v-chip>
    </div>
    <p class="daily-focus__detail">{{ focus.detail }}</p>
    <div class="daily-focus__progress">
      <div class="daily-focus__progress-labels">
        <span>{{ t('student.home.dailyFocus.progress') }}</span>
        <span>{{ focus.progress }}%</span>
      </div>
      <v-progress-linear
        :model-value="focus.progress"
        color="secondary"
        height="8"
        rounded
        class="daily-focus__bar"
      />
    </div>
  </AppCard>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import { AppCard } from '../../ui/index.js'

const { t } = useI18n()

defineProps({
  focus: {
    type: Object,
    default: () => ({
      mission: '',
      target: '',
      progress: 0,
      detail: '',
    }),
  },
})
</script>

<style scoped>
.daily-focus {
  margin-bottom: var(--em-space-xl);
  border-inline-start: 3px solid var(--em-primary);
}

.daily-focus__eyebrow {
  margin: 0 0 4px;
  font-size: var(--em-text-caption);
  font-weight: 600;
  color: var(--em-primary);
}

.daily-focus__title {
  margin: 0;
  font-family: var(--font-display);
  font-size: 1.125rem;
  font-weight: 700;
}

.daily-focus__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
}

.daily-focus__detail {
  margin: 0 0 16px;
  font-size: var(--em-text-sm);
  color: var(--em-text-muted);
}

.daily-focus__progress-labels {
  display: flex;
  justify-content: space-between;
  font-size: var(--em-text-caption);
  color: var(--em-text-muted);
  margin-bottom: 6px;
}

.daily-focus__bar :deep(.v-progress-linear__determinate) {
  transition: width 1s var(--em-ease-spring);
}
</style>
