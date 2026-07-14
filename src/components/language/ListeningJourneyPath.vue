<template>
  <v-card class="timeline-card pa-6 mb-4" variant="flat">
    <h3 class="text-h6 font-weight-bold mb-5">{{ t('student.languages.coach.ux.timeline.title') }}</h3>
    <div class="timeline">
      <div
        v-for="(step, idx) in steps"
        :key="step.key"
        class="timeline-item"
        :class="{ 'timeline-item--done': step.done, 'timeline-item--active': step.active }"
      >
        <div class="timeline-rail">
          <div class="timeline-dot">
            <v-icon v-if="step.done" size="16" color="white">mdi-check</v-icon>
            <span v-else class="timeline-dot-inner" />
          </div>
          <div v-if="idx < steps.length - 1" class="timeline-connector" />
        </div>
        <div class="timeline-content pb-5">
          <div class="text-subtitle-1 font-weight-bold">{{ step.label }}</div>
        </div>
      </div>
    </div>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  timelineSteps: { type: Array, default: () => [] },
})

const { t } = useI18n()

const steps = computed(() => props.timelineSteps || [])
</script>

<style scoped>
.timeline-card {
  border-radius: 20px;
}
.timeline-item {
  display: flex;
  gap: 1rem;
  opacity: 0.55;
}
.timeline-item--done,
.timeline-item--active {
  opacity: 1;
}
.timeline-rail {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 2rem;
  flex-shrink: 0;
}
.timeline-dot {
  width: 1.75rem;
  height: 1.75rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(var(--v-theme-on-surface), 0.12);
  border: 2px solid rgba(var(--v-theme-on-surface), 0.15);
  flex-shrink: 0;
}
.timeline-item--active .timeline-dot {
  background: rgb(var(--v-theme-secondary));
  border-color: rgb(var(--v-theme-secondary));
  box-shadow: 0 0 0 4px rgba(var(--v-theme-secondary), 0.2);
}
.timeline-item--done .timeline-dot {
  background: rgb(var(--v-theme-success));
  border-color: rgb(var(--v-theme-success));
}
.timeline-dot-inner {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
  background: rgba(var(--v-theme-on-surface), 0.35);
}
.timeline-item--active .timeline-dot-inner {
  background: white;
}
.timeline-connector {
  flex: 1;
  width: 2px;
  min-height: 1.25rem;
  margin: 0.2rem 0;
  background: rgba(var(--v-theme-on-surface), 0.12);
}
.timeline-item--done .timeline-connector {
  background: rgba(var(--v-theme-success), 0.45);
}
.timeline-content {
  flex: 1;
  min-width: 0;
  padding-top: 0.15rem;
}
</style>
