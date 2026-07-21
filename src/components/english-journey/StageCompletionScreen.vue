<template>
  <section class="stage-complete">
    <div class="stage-complete__badge" aria-hidden="true">
      <v-icon icon="mdi-party-popper" size="40" />
    </div>
    <h1 class="stage-complete__title">{{ t('student.englishJourney.complete.title') }}</h1>
    <p class="stage-complete__encourage">
      {{ wrapUp?.encouragement || t('student.englishJourney.complete.encouragement') }}
    </p>

    <ul v-if="wrapUp?.achievements?.length" class="stage-complete__list eng-island" dir="ltr">
      <li v-for="(item, i) in wrapUp.achievements" :key="i">{{ item }}</li>
    </ul>

    <AppCard v-if="nextLabel" class="stage-complete__next" solid padding="md">
      <p class="stage-complete__next-label">{{ t('student.englishJourney.complete.next') }}</p>
      <p class="stage-complete__next-name eng-island" dir="ltr">{{ nextLabel }}</p>
    </AppCard>

    <div class="stage-complete__actions">
      <AppButton variant="primary" :to="homeTo">
        {{ t('student.englishJourney.complete.backJourney') }}
      </AppButton>
    </div>
  </section>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import AppCard from '../ui/AppCard.vue'
import AppButton from '../ui/AppButton.vue'
import { ROUTES } from '../../constants/app.js'

defineProps({
  wrapUp: { type: Object, default: null },
  nextLabel: { type: String, default: '' },
})

const { t } = useI18n()
const homeTo = ROUTES.STUDENT_ENGLISH_JOURNEY
</script>

<style scoped>
.stage-complete {
  max-width: 560px;
  margin-inline: auto;
  padding: 40px 16px;
  text-align: center;
}

.stage-complete__badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 72px;
  height: 72px;
  margin-block-end: 16px;
  border-radius: 20px;
  background: color-mix(in srgb, var(--color-primary, #6366f1) 16%, transparent);
  color: var(--color-primary-deep, #4f46e5);
}

.stage-complete__title {
  margin: 0 0 12px;
  font-family: var(--font-display, Tajawal, sans-serif);
  font-size: clamp(1.5rem, 3vw, 2rem);
}

.stage-complete__encourage {
  margin: 0 0 20px;
  color: var(--text-muted, #3f4f63);
}

.stage-complete__list {
  text-align: start;
  margin: 0 auto 24px;
  max-width: 420px;
}

.stage-complete__next {
  margin-block-end: 24px;
  text-align: start;
}

.stage-complete__next-label {
  margin: 0 0 4px;
  font-size: 0.75rem;
  color: var(--text-muted, #3f4f63);
}

.stage-complete__next-name {
  margin: 0;
  font-weight: 700;
  font-size: 1.125rem;
}

.eng-island {
  unicode-bidi: isolate;
}
</style>
