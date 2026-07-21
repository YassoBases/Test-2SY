<template>
  <section class="grammar-complete">
    <div class="grammar-complete__badge" aria-hidden="true">
      <v-icon icon="mdi-check-decagram" size="40" />
    </div>
    <h1 class="grammar-complete__title">{{ t('student.grammarV2.complete.title') }}</h1>
    <p v-if="displayName" class="grammar-complete__name eng-island" dir="ltr">
      {{ displayName }}
    </p>

    <dl class="grammar-complete__stats">
      <div>
        <dt>{{ t('student.grammarV2.complete.mastery') }}</dt>
        <dd>{{ Math.round(mastery) }}%</dd>
      </div>
      <div>
        <dt>{{ t('student.grammarV2.complete.confidence') }}</dt>
        <dd>{{ Math.round(confidence) }}%</dd>
      </div>
    </dl>

    <div v-if="skills.length" class="grammar-complete__skills">
      <h2>{{ t('student.grammarV2.complete.skillsImproved') }}</h2>
      <ul>
        <li v-for="skill in skills" :key="skill" class="eng-island" dir="ltr">{{ skill }}</li>
      </ul>
    </div>

    <AppCard v-if="nextName" class="grammar-complete__next" solid padding="md">
      <p class="grammar-complete__next-label">{{ t('student.grammarV2.complete.next') }}</p>
      <p class="grammar-complete__next-name eng-island" dir="ltr">{{ nextName }}</p>
    </AppCard>

    <AppButton variant="primary" size="large" :to="homeTo">
      {{ t('student.grammarV2.complete.continue') }}
    </AppButton>
  </section>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import AppCard from '../ui/AppCard.vue'
import AppButton from '../ui/AppButton.vue'
import { ROUTES } from '../../constants/app.js'

defineProps({
  displayName: { type: String, default: '' },
  mastery: { type: Number, default: 0 },
  confidence: { type: Number, default: 0 },
  skills: { type: Array, default: () => [] },
  nextName: { type: String, default: '' },
})

const { t } = useI18n()
const homeTo = ROUTES.STUDENT_GRAMMAR
</script>

<style scoped>
.grammar-complete {
  max-width: 520px;
  margin-inline: auto;
  padding: 40px 16px;
  text-align: center;
}

.grammar-complete__badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 72px;
  height: 72px;
  margin-block-end: 16px;
  border-radius: 20px;
  background: color-mix(in srgb, #10b981 18%, transparent);
  color: #059669;
}

.grammar-complete__title {
  margin: 0 0 8px;
  font-family: var(--font-display, Tajawal, sans-serif);
  font-size: clamp(1.5rem, 3vw, 2rem);
}

.grammar-complete__name {
  margin: 0 0 20px;
  font-weight: 700;
  font-size: 1.125rem;
}

.grammar-complete__stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin: 0 0 20px;
  text-align: start;
}

.grammar-complete__stats dt {
  font-size: 0.75rem;
  color: var(--text-muted, #3f4f63);
}

.grammar-complete__stats dd {
  margin: 4px 0 0;
  font-size: 1.5rem;
  font-weight: 700;
}

.grammar-complete__skills {
  text-align: start;
  margin-block-end: 20px;
}

.grammar-complete__skills h2 {
  margin: 0 0 8px;
  font-size: 0.9375rem;
}

.grammar-complete__skills ul {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  list-style: none;
  margin: 0;
  padding: 0;
}

.grammar-complete__skills li {
  padding: 6px 12px;
  border-radius: 12px;
  background: color-mix(in srgb, var(--color-primary, #6366f1) 12%, transparent);
  font-size: 0.8125rem;
}

.grammar-complete__next {
  margin-block-end: 24px;
  text-align: start;
}

.grammar-complete__next-label {
  margin: 0 0 4px;
  font-size: 0.75rem;
  color: var(--text-muted, #3f4f63);
}

.grammar-complete__next-name {
  margin: 0;
  font-weight: 700;
}

.eng-island {
  unicode-bidi: isolate;
}
</style>
