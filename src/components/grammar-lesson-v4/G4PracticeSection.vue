<template>
  <section class="g4-section" aria-labelledby="g4-practice-title">
    <h2 id="g4-practice-title" class="g4-section__title">
      {{ t('student.grammarV4.practice.title') }}
    </h2>
    <p class="g4-section__sub">{{ t('student.grammarV4.practice.subtitle') }}</p>

    <div v-if="done" class="done">
      {{ t('student.grammarV4.practice.done') }}
    </div>

    <div v-else-if="question" class="qcard">
      <div class="qcard__meta">
        <span>{{ t('student.grammarV4.practice.progress', { current: index + 1, total }) }}</span>
        <span class="chip">{{ question.difficulty }} · {{ question.type }}</span>
      </div>

      <p class="qcard__prompt eng-island" dir="ltr">{{ question.prompt }}</p>

      <div v-if="question.type === 'mcq'" class="options">
        <button
          v-for="opt in question.options"
          :key="opt"
          type="button"
          class="opt eng-island"
          dir="ltr"
          :class="{ 'opt--on': selected === opt }"
          :disabled="!!feedback"
          @click="$emit('update:selected', opt)"
        >
          {{ opt }}
        </button>
      </div>

      <div v-else-if="question.type === 'build'" class="build">
        <div class="build__out eng-island" dir="ltr">
          {{ build.join(' ') || '…' }}
        </div>
        <div class="build__tokens">
          <button
            v-for="(tok, i) in remaining"
            :key="`${tok}-${i}`"
            type="button"
            class="tok"
            :disabled="!!feedback"
            @click="$emit('pick-token', { token: tok, index: i })"
          >
            {{ tok }}
          </button>
        </div>
        <AppButton variant="ghost" size="small" :disabled="!!feedback" @click="$emit('reset-build')">
          {{ t('student.grammarV4.practice.reset') }}
        </AppButton>
      </div>

      <textarea
        v-else
        :value="answer"
        class="qcard__input eng-island"
        dir="ltr"
        rows="3"
        :disabled="!!feedback"
        :placeholder="t('student.grammarV4.practice.typeAnswer')"
        @input="$emit('update:answer', $event.target.value)"
      />

      <div v-if="feedback" class="feedback" :class="feedback.correct ? 'feedback--ok' : 'feedback--bad'">
        <p class="feedback__title">
          {{ feedback.correct ? t('student.grammarV4.practice.correct') : t('student.grammarV4.practice.incorrect') }}
        </p>
        <p v-if="!feedback.correct" class="eng-island" dir="ltr">
          <strong>{{ t('student.grammarV4.practice.answer') }}:</strong> {{ feedback.answer }}
        </p>
        <p>{{ feedback.explanation }}</p>
        <p v-if="!feedback.correct && feedback.mistakeWhy">{{ feedback.mistakeWhy }}</p>
        <AppButton variant="primary" @click="$emit('continue')">
          {{ feedback.correct ? t('student.grammarV4.practice.next') : t('student.grammarV4.practice.trySimilar') }}
        </AppButton>
      </div>

      <AppButton
        v-else
        variant="primary"
        class="mt-2"
        @click="$emit('check')"
      >
        {{ t('student.grammarV4.practice.check') }}
      </AppButton>
    </div>
  </section>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import AppButton from '../ui/AppButton.vue'

defineProps({
  question: { type: Object, default: null },
  index: { type: Number, default: 0 },
  total: { type: Number, default: 0 },
  answer: { type: String, default: '' },
  selected: { type: String, default: null },
  build: { type: Array, default: () => [] },
  remaining: { type: Array, default: () => [] },
  feedback: { type: Object, default: null },
  done: { type: Boolean, default: false },
})

defineEmits([
  'update:answer',
  'update:selected',
  'check',
  'continue',
  'pick-token',
  'reset-build',
])

const { t } = useI18n()
</script>

<style scoped>
.g4-section__title {
  margin: 0 0 8px;
  font-size: 1.5rem;
  font-family: var(--font-display, Tajawal, sans-serif);
}

.g4-section__sub {
  margin: 0 0 16px;
  color: var(--text-muted, #3f4f63);
}

.qcard,
.done {
  padding: 22px;
  border-radius: 16px;
  background: var(--surface-elevated, #fff);
}

.qcard__meta {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-block-end: 12px;
  font-size: 0.85rem;
  color: var(--text-muted, #3f4f63);
}

.chip {
  padding: 2px 8px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--color-primary, #6366f1) 12%, transparent);
}

.qcard__prompt {
  margin: 0 0 16px;
  font-size: 1.15rem;
  line-height: 1.55;
  white-space: pre-wrap;
}

.options {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.opt,
.tok {
  text-align: start;
  padding: 12px 14px;
  border-radius: 12px;
  border: 1px solid color-mix(in srgb, var(--text-muted, #3f4f63) 22%, transparent);
  background: transparent;
  cursor: pointer;
  font: inherit;
}

.opt--on {
  border-color: var(--color-primary, #6366f1);
  background: color-mix(in srgb, var(--color-primary, #6366f1) 10%, transparent);
}

.build__out {
  min-height: 48px;
  padding: 12px;
  border-radius: 12px;
  background: color-mix(in srgb, var(--color-primary, #6366f1) 8%, transparent);
  margin-block-end: 10px;
}

.build__tokens {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-block-end: 8px;
}

.qcard__input {
  width: 100%;
  padding: 12px 14px;
  border-radius: 12px;
  border: 1px solid color-mix(in srgb, var(--text-muted, #3f4f63) 25%, transparent);
  font: inherit;
  resize: vertical;
}

.feedback {
  margin-block-start: 16px;
  padding: 14px;
  border-radius: 12px;
}

.feedback--ok {
  background: color-mix(in srgb, #10b981 12%, transparent);
}

.feedback--bad {
  background: color-mix(in srgb, #ef4444 10%, transparent);
}

.feedback__title {
  font-weight: 800;
  margin: 0 0 8px;
}

.feedback p {
  margin: 0 0 8px;
  line-height: 1.5;
}

.eng-island {
  unicode-bidi: isolate;
}

.mt-2 {
  margin-block-start: 12px;
}
</style>
