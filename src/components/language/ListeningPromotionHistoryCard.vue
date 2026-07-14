<template>
  <v-card class="story-card pa-6 mb-4" variant="flat">
    <div class="d-flex align-center gap-2 mb-5">
      <v-icon color="secondary" size="26">mdi-book-open-page-variant-outline</v-icon>
      <h3 class="text-h6 font-weight-bold mb-0">{{ t('student.languages.coach.ux.history.title') }}</h3>
    </div>
    <div class="story-timeline">
      <div v-for="(event, idx) in events" :key="idx" class="story-item">
        <div class="story-rail">
          <div class="story-dot" />
          <div v-if="idx < events.length - 1" class="story-line" />
        </div>
        <div class="story-body pb-4">
          <div class="text-caption text-medium-emphasis text-uppercase mb-1">{{ event.period }}</div>
          <div class="text-body-1">{{ event.text }}</div>
        </div>
      </div>
    </div>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  historyEvents: { type: Array, default: () => [] },
})

const { t } = useI18n()

const events = computed(() => props.historyEvents || [])
</script>

<style scoped>
.story-card {
  border-radius: 20px;
}
.story-item {
  display: flex;
  gap: 1rem;
}
.story-rail {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 1rem;
  flex-shrink: 0;
}
.story-dot {
  width: 0.65rem;
  height: 0.65rem;
  border-radius: 50%;
  background: rgb(var(--v-theme-secondary));
  margin-top: 0.35rem;
}
.story-line {
  flex: 1;
  width: 2px;
  min-height: 1.5rem;
  margin-top: 0.25rem;
  background: rgba(var(--v-theme-on-surface), 0.1);
}
.story-body {
  flex: 1;
  min-width: 0;
}
</style>
