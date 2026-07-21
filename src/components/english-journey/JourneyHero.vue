<template>
  <section class="journey-hero" aria-labelledby="journey-hero-title">
    <div class="journey-hero__glow" aria-hidden="true" />
    <p class="journey-hero__kicker">
      <v-icon icon="mdi-robot-happy-outline" size="18" aria-hidden="true" />
      {{ t('student.englishJourney.hero.kicker') }}
    </p>
    <p class="journey-hero__greeting">
      {{ t('student.englishJourney.hero.greeting', { name: name || '—' }) }}
    </p>
    <h1 id="journey-hero-title" class="journey-hero__title">
      {{ headline }}
    </h1>
    <p class="journey-hero__lead">
      {{ t('student.englishJourney.hero.lead') }}
    </p>

    <div v-if="currentLabel || goal" class="journey-hero__focus">
      <div v-if="currentLabel" class="journey-hero__focus-item">
        <span class="journey-hero__label">{{ t('student.englishJourney.hero.currentStage') }}</span>
        <span class="journey-hero__focus-value eng-island" dir="ltr">{{ currentLabel }}</span>
      </div>
      <div v-if="goal" class="journey-hero__focus-item">
        <span class="journey-hero__label">{{ t('student.englishJourney.hero.goal') }}</span>
        <span class="journey-hero__focus-value eng-island" dir="ltr">{{ goal }}</span>
      </div>
    </div>

    <div class="journey-hero__meta">
      <span v-if="cefr" class="journey-hero__chip eng-island" dir="ltr">
        <v-icon icon="mdi-school-outline" size="16" aria-hidden="true" />
        {{ cefr }}
      </span>
      <span v-if="streak > 0" class="journey-hero__chip">
        <v-icon icon="mdi-fire" size="16" aria-hidden="true" />
        {{ t('student.englishJourney.hero.streak', { days: streak }) }}
      </span>
      <span class="journey-hero__chip">
        <v-icon icon="mdi-clock-outline" size="16" aria-hidden="true" />
        {{ t('student.englishJourney.hero.eta', { minutes }) }}
      </span>
    </div>

    <div class="journey-hero__cta">
      <AppButton
        variant="primary"
        size="large"
        :loading="loading"
        :disabled="disabled"
        prepend-icon="mdi-play"
        @click="$emit('start')"
      >
        {{ disabled ? t('student.englishJourney.hero.ctaDisabled') : t('student.englishJourney.hero.cta') }}
      </AppButton>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import AppButton from '../ui/AppButton.vue'

const props = defineProps({
  name: { type: String, default: '' },
  currentLabel: { type: String, default: '' },
  goal: { type: String, default: '' },
  cefr: { type: String, default: '' },
  streak: { type: Number, default: 0 },
  minutes: { type: Number, default: 18 },
  loading: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
})

defineEmits(['start'])
const { t } = useI18n()

const headline = computed(() => {
  if (props.currentLabel) {
    return t('student.englishJourney.hero.headlineWithStage', { stage: props.currentLabel })
  }
  return t('student.englishJourney.hero.headline')
})
</script>

<style scoped>
.journey-hero {
  position: relative;
  padding: 36px 28px;
  border-radius: 20px;
  overflow: hidden;
  margin-block-end: 24px;
  background:
    radial-gradient(120% 90% at 100% 0%, rgba(99, 102, 241, 0.22), transparent 55%),
    radial-gradient(90% 70% at 0% 100%, rgba(56, 189, 248, 0.1), transparent 50%),
    linear-gradient(165deg, #eef2ff 0%, #ffffff 55%);
}

.journey-hero__kicker {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin: 0 0 10px;
  font-size: 0.8125rem;
  font-weight: 700;
  color: var(--color-primary-deep, #4f46e5);
}

.journey-hero__greeting {
  margin: 0 0 8px;
  font-size: 0.9375rem;
  color: var(--text-muted, #3f4f63);
}

.journey-hero__title {
  margin: 0 0 10px;
  font-family: var(--font-display, Tajawal, sans-serif);
  font-size: clamp(1.65rem, 3vw, 2.15rem);
  line-height: 1.25;
  max-width: 28ch;
}

.journey-hero__lead {
  margin: 0 0 18px;
  max-width: 42ch;
  color: var(--text-muted, #3f4f63);
  font-size: 0.975rem;
}

.journey-hero__focus {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
  margin-block-end: 16px;
}

.journey-hero__focus-item {
  padding: 12px 14px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.72);
}

.journey-hero__label {
  display: block;
  margin-block-end: 4px;
  font-size: 0.75rem;
  color: var(--text-muted, #3f4f63);
}

.journey-hero__focus-value {
  font-weight: 700;
  font-size: 1rem;
}

.eng-island {
  unicode-bidi: isolate;
}

.journey-hero__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-block-end: 22px;
}

.journey-hero__chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 12px;
  background: color-mix(in srgb, var(--color-primary, #6366f1) 12%, #fff);
  font-size: 0.8125rem;
}

@media (max-width: 600px) {
  .journey-hero {
    padding: 24px 16px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .journey-hero {
    transition: none;
  }
}
</style>
