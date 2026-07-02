<template>
  <nav class="lesson-step-strip" :aria-label="t('student.lesson.steps.ariaLabel')">
    <ol class="lesson-step-strip__list">
      <li
        v-for="(step, index) in steps"
        :key="step.id"
        class="lesson-step-strip__item"
        :class="[
          `lesson-step-strip__item--${step.status}`,
          { 'lesson-step-strip__item--last': index === steps.length - 1 },
        ]"
      >
        <button
          type="button"
          class="lesson-step-strip__btn"
          :aria-current="step.current ? 'step' : undefined"
          :aria-label="stepAriaLabel(step)"
          @click="$emit('select', step.id)"
        >
          <span class="lesson-step-strip__marker">
            <v-icon v-if="step.completed" size="16">mdi-check</v-icon>
            <v-icon v-else :icon="step.icon" size="16" />
          </span>
          <span class="lesson-step-strip__label">{{ step.label }}</span>
        </button>
        <span
          v-if="index < steps.length - 1"
          class="lesson-step-strip__connector"
          :class="{ 'lesson-step-strip__connector--filled': step.completed }"
          aria-hidden="true"
        >
          ↓
        </span>
      </li>
    </ol>
  </nav>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

defineProps({
  steps: {
    type: Array,
    default: () => [],
  },
})

defineEmits(['select'])

function stepAriaLabel(step) {
  if (step.completed) return t('student.lesson.steps.completed', { label: step.label })
  if (step.current) return t('student.lesson.steps.current', { label: step.label })
  return t('student.lesson.steps.upcoming', { label: step.label })
}
</script>
