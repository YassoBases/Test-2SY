<template>
  <header class="session-header" aria-label="Session header">
    <div class="session-header__teacher">
      <EmptyTeacherPlaceholder :voice-state="voiceState" size="md" />
    </div>

    <div class="session-header__meta">
      <p class="session-header__kicker">{{ kicker }}</p>
      <h1 class="session-header__topic eng-island" dir="ltr">{{ topic || '—' }}</h1>
      <div class="session-header__chips">
        <span v-if="cefr" class="chip eng-island" dir="ltr">{{ cefr }}</span>
        <span class="chip">
          {{ t('student.grammarSession.header.remaining', { n: remainingMinutes }) }}
        </span>
      </div>
    </div>

    <div class="session-header__progress">
      <LessonProgress :percent="progressPercent" />
      <AppButton
        variant="ghost"
        size="small"
        prepend-icon="mdi-close"
        :aria-label="t('student.grammarSession.header.exit')"
        @click="$emit('exit')"
      >
        {{ t('student.grammarSession.header.exit') }}
      </AppButton>
    </div>
  </header>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import AppButton from '../ui/AppButton.vue'
import EmptyTeacherPlaceholder from './EmptyTeacherPlaceholder.vue'
import LessonProgress from './LessonProgress.vue'

defineProps({
  topic: { type: String, default: '' },
  cefr: { type: String, default: '' },
  kicker: { type: String, default: '' },
  remainingMinutes: { type: Number, default: 18 },
  progressPercent: { type: Number, default: 0 },
  voiceState: { type: String, default: 'idle' },
})

defineEmits(['exit'])
const { t } = useI18n()
</script>

<style scoped>
.session-header {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 16px;
  align-items: center;
  padding: 16px 20px;
  border-radius: 20px;
  background: var(--surface-elevated, #fff);
  position: sticky;
  top: 0;
  z-index: 5;
}

.session-header__kicker {
  margin: 0 0 4px;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--text-muted, #3f4f63);
}

.session-header__topic {
  margin: 0;
  font-size: clamp(1.25rem, 2.5vw, 1.6rem);
  font-family: var(--font-display, Tajawal, sans-serif);
  line-height: 1.25;
}

.session-header__chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-block-start: 8px;
}

.chip {
  padding: 4px 10px;
  border-radius: 10px;
  background: color-mix(in srgb, var(--color-primary, #6366f1) 12%, transparent);
  font-size: 0.8125rem;
}

.session-header__progress {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
  min-width: 140px;
}

.eng-island {
  unicode-bidi: isolate;
}

@media (max-width: 720px) {
  .session-header {
    grid-template-columns: auto 1fr;
  }

  .session-header__progress {
    grid-column: 1 / -1;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    min-width: 0;
  }
}
</style>
