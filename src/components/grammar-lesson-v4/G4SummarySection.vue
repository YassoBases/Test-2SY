<template>
  <section class="g4-section" aria-labelledby="g4-summary-title">
    <h2 id="g4-summary-title" class="g4-section__title">
      {{ t('student.grammarV4.summary.title') }}
    </h2>

    <div class="card">
      <h3>{{ t('student.grammarV4.summary.learned') }}</h3>
      <p class="eng-island" dir="ltr">{{ topic }}</p>
      <p v-if="completionMessage">{{ completionMessage }}</p>
    </div>

    <div class="card">
      <h3>{{ t('student.grammarV4.summary.mistakes') }}</h3>
      <p>
        {{ t('student.grammarV4.summary.score', { correct, mistakes }) }}
      </p>
      <ul v-if="wrongItems.length" class="eng-island" dir="ltr">
        <li v-for="(w, i) in wrongItems.slice(0, 5)" :key="i">
          {{ w.given || '—' }} → {{ w.answer }}
        </li>
      </ul>
      <p v-else>{{ t('student.grammarV4.summary.noMistakes') }}</p>
    </div>

    <div class="card">
      <h3>{{ t('student.grammarV4.summary.suggestions') }}</h3>
      <p>{{ suggestion }}</p>
    </div>

    <div class="card">
      <h3>{{ t('student.grammarV4.summary.next') }}</h3>
      <p>{{ t('student.grammarV4.summary.nextBody') }}</p>
      <AppButton
        variant="primary"
        size="large"
        :loading="finishing"
        prepend-icon="mdi-check"
        @click="$emit('finish')"
      >
        {{ t('student.grammarV4.summary.finish') }}
      </AppButton>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import AppButton from '../ui/AppButton.vue'

const props = defineProps({
  topic: { type: String, default: '' },
  correct: { type: Number, default: 0 },
  mistakes: { type: Number, default: 0 },
  history: { type: Array, default: () => [] },
  completionMessage: { type: String, default: '' },
  finishing: { type: Boolean, default: false },
})

defineEmits(['finish'])
const { t } = useI18n()

const wrongItems = computed(() => props.history.filter((h) => !h.correct))

const suggestion = computed(() => {
  if (props.mistakes === 0) return t('student.grammarV4.summary.suggestGreat')
  if (props.mistakes <= 3) return t('student.grammarV4.summary.suggestReview')
  return t('student.grammarV4.summary.suggestMore')
})
</script>

<style scoped>
.g4-section__title {
  margin: 0 0 16px;
  font-size: 1.5rem;
  font-family: var(--font-display, Tajawal, sans-serif);
}

.card {
  padding: 20px 22px;
  border-radius: 16px;
  background: var(--surface-elevated, #fff);
  margin-block-end: 12px;
}

.card h3 {
  margin: 0 0 8px;
  font-size: 1rem;
}

.card p {
  margin: 0 0 10px;
  line-height: 1.6;
}

.card ul {
  margin: 0 0 8px;
  padding-inline-start: 1.2rem;
}

.eng-island {
  unicode-bidi: isolate;
}
</style>
