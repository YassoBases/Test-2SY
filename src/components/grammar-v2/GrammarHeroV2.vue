<template>
  <section class="grammar-hero" aria-labelledby="grammar-hero-title">
    <p class="grammar-hero__kicker">{{ t('student.grammarV2.hero.kicker') }}</p>
    <h1 id="grammar-hero-title" class="grammar-hero__title">
      {{ t('student.grammarV2.hero.title') }}
    </h1>

    <div class="grammar-hero__grid">
      <div class="grammar-hero__cell">
        <span class="grammar-hero__label">{{ t('student.grammarV2.hero.currentGrammar') }}</span>
        <span class="grammar-hero__value eng-island" dir="ltr">{{ currentName || '—' }}</span>
      </div>
      <div class="grammar-hero__cell">
        <span class="grammar-hero__label">{{ t('student.grammarV2.hero.currentCefr') }}</span>
        <span class="grammar-hero__value eng-island" dir="ltr">{{ cefr || '—' }}</span>
      </div>
      <div class="grammar-hero__cell">
        <span class="grammar-hero__label">{{ t('student.grammarV2.hero.currentStage') }}</span>
        <span class="grammar-hero__value">
          {{ stageIndex }}/{{ stageTotal || '—' }}
        </span>
      </div>
      <div class="grammar-hero__cell">
        <span class="grammar-hero__label">{{ t('student.grammarV2.hero.overallProgress') }}</span>
        <span class="grammar-hero__value">{{ completed }}/{{ total }} ({{ percent }}%)</span>
      </div>
      <div class="grammar-hero__cell">
        <span class="grammar-hero__label">{{ t('student.grammarV2.hero.eta') }}</span>
        <span class="grammar-hero__value">
          {{ t('student.grammarV2.common.minutes', { n: minutes }) }}
        </span>
      </div>
    </div>

    <div class="grammar-hero__actions">
      <AppButton
        type="button"
        variant="primary"
        size="large"
        :loading="loading"
        :disabled="!canStart || loading"
        prepend-icon="mdi-play"
        @click.prevent="$emit('start')"
      >
        {{ t('student.grammarV2.hero.startLesson') }}
      </AppButton>
      <AppButton variant="secondary" :to="reviewTo">
        {{ t('student.grammarV2.hero.reviewCompleted') }}
      </AppButton>
    </div>
  </section>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import AppButton from '../ui/AppButton.vue'
import { ROUTES } from '../../constants/app.js'

defineProps({
  currentName: { type: String, default: '' },
  cefr: { type: String, default: '' },
  stageIndex: { type: Number, default: 0 },
  stageTotal: { type: Number, default: 0 },
  completed: { type: Number, default: 0 },
  total: { type: Number, default: 0 },
  percent: { type: Number, default: 0 },
  minutes: { type: Number, default: 18 },
  loading: { type: Boolean, default: false },
  canStart: { type: Boolean, default: false },
})

defineEmits(['start'])
const { t } = useI18n()
const reviewTo = ROUTES.STUDENT_GRAMMAR_REVIEW
</script>

<style scoped>
.grammar-hero {
  padding: 32px 28px;
  border-radius: 20px;
  margin-block-end: 24px;
  background:
    radial-gradient(120% 80% at 100% 0%, rgba(99, 102, 241, 0.16), transparent 55%),
    linear-gradient(165deg, #eef2ff 0%, #fff 60%);
}

.grammar-hero__kicker {
  margin: 0 0 6px;
  font-size: 0.8125rem;
  font-weight: 700;
  color: var(--color-primary-deep, #4f46e5);
}

.grammar-hero__title {
  margin: 0 0 20px;
  font-family: var(--font-display, Tajawal, sans-serif);
  font-size: clamp(1.75rem, 3vw, 2.25rem);
}

.grammar-hero__grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
  margin-block-end: 22px;
}

.grammar-hero__cell {
  padding: 12px 14px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.78);
}

.grammar-hero__label {
  display: block;
  margin-block-end: 4px;
  font-size: 0.75rem;
  color: var(--text-muted, #3f4f63);
}

.grammar-hero__value {
  font-weight: 700;
  font-size: 0.975rem;
}

.grammar-hero__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.eng-island {
  unicode-bidi: isolate;
}

@media (max-width: 600px) {
  .grammar-hero {
    padding: 24px 16px;
  }
}
</style>
