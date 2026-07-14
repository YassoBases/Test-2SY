<template>
  <section v-if="blocks.length" class="teaching-blocks mb-5" aria-label="teaching blocks">
    <div class="text-subtitle-1 font-weight-bold mb-3">
      {{ t('student.languages.speakingJourney.teaching.title') }}
    </div>
    <div class="blocks-grid">
      <article
        v-for="(block, idx) in blocks"
        :key="`${block.kind}-${idx}`"
        class="teaching-card glass-card pa-4"
      >
        <div class="d-flex align-start gap-3">
          <div class="icon-wrap" aria-hidden="true">
            <v-icon :color="meta(block.kind).color" size="22">{{ meta(block.kind).icon }}</v-icon>
          </div>
          <div class="min-width-0 flex-grow-1">
            <div class="text-caption text-medium-emphasis mb-1">
              {{ meta(block.kind).label }}
            </div>
            <div class="text-body-1 font-weight-medium mb-1">{{ block.title }}</div>
            <p class="text-body-2 mb-0" dir="auto">{{ block.body }}</p>
          </div>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

defineProps({
  blocks: { type: Array, default: () => [] },
})

const { t } = useI18n()

/** Presentational mapping only — content always comes from backend `kind`. */
function meta(kind) {
  const k = String(kind || '').toLowerCase()
  const map = {
    explanation: {
      icon: 'mdi-school-outline',
      color: 'primary',
      label: t('student.languages.speakingJourney.teaching.kinds.explanation'),
    },
    example: {
      icon: 'mdi-lightbulb-on-outline',
      color: 'secondary',
      label: t('student.languages.speakingJourney.teaching.kinds.example'),
    },
    noticing_cue: {
      icon: 'mdi-eye-outline',
      color: 'info',
      label: t('student.languages.speakingJourney.teaching.kinds.tip'),
    },
    contrast: {
      icon: 'mdi-compare',
      color: 'warning',
      label: t('student.languages.speakingJourney.teaching.kinds.reminder'),
    },
    scaffold: {
      icon: 'mdi-strategy',
      color: 'primary',
      label: t('student.languages.speakingJourney.teaching.kinds.strategy'),
    },
    guided_prompt: {
      icon: 'mdi-comment-quote-outline',
      color: 'secondary',
      label: t('student.languages.speakingJourney.teaching.kinds.prompt'),
    },
    misconception_correction: {
      icon: 'mdi-alert-circle-outline',
      color: 'warning',
      label: t('student.languages.speakingJourney.teaching.kinds.reminder'),
    },
  }
  return (
    map[k] || {
      icon: 'mdi-book-open-page-variant',
      color: 'primary',
      label: t('student.languages.speakingJourney.teaching.kinds.general'),
    }
  )
}
</script>

<style scoped>
.blocks-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: 1fr;
}
@media (min-width: 960px) {
  .blocks-grid {
    grid-template-columns: 1fr 1fr;
  }
}
.teaching-card {
  border-radius: var(--em-radius-md, 16px);
  border: 1px solid rgba(var(--v-theme-on-surface), 0.06);
  transition: transform 160ms ease, border-color 160ms ease;
}
@media (prefers-reduced-motion: no-preference) {
  .teaching-card:hover {
    transform: translateY(-1px);
    border-color: rgba(var(--v-theme-primary), 0.22);
  }
}
.icon-wrap {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  background: rgba(var(--v-theme-primary), 0.1);
  flex-shrink: 0;
}
.min-width-0 {
  min-width: 0;
}
</style>
