<template>
  <nav class="session-timeline" :aria-label="t('student.grammarSession.timeline.label')">
    <ol class="session-timeline__list">
      <li
        v-for="(stage, index) in stages"
        :key="stage"
        class="session-timeline__item"
        :class="itemClass(stage, index)"
      >
        <button
          type="button"
          class="session-timeline__btn"
          :disabled="!canSelect(stage, index)"
          :aria-current="stage === currentStage ? 'step' : undefined"
          @click="$emit('select', stage)"
        >
          <span class="session-timeline__mark" aria-hidden="true">
            <v-icon
              v-if="isCompleted(stage)"
              icon="mdi-check"
              size="14"
            />
            <span v-else-if="stage === currentStage" class="session-timeline__dot" />
            <span v-else class="session-timeline__ring" />
          </span>
          <span class="session-timeline__label">{{ labelFor(stage) }}</span>
        </button>
      </li>
    </ol>
  </nav>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import { GRAMMAR_SESSION_STAGE_META } from '../../constants/grammarSessionStages.js'

const props = defineProps({
  stages: { type: Array, required: true },
  currentStage: { type: String, required: true },
  completedStages: { type: Array, default: () => [] },
  visitedStages: { type: Array, default: () => [] },
})

defineEmits(['select'])
const { t } = useI18n()

function labelFor(stage) {
  const key = GRAMMAR_SESSION_STAGE_META[stage]?.labelKey
  return key ? t(key) : stage
}

function isCompleted(stage) {
  return props.completedStages.includes(stage)
}

function canSelect(stage, index) {
  if (stage === props.currentStage) return true
  if (isCompleted(stage) || props.visitedStages.includes(stage)) return true
  const curIdx = props.stages.indexOf(props.currentStage)
  return index === curIdx + 1 && props.completedStages.includes(props.stages[curIdx])
}

function itemClass(stage) {
  return {
    'session-timeline__item--current': stage === props.currentStage,
    'session-timeline__item--done': isCompleted(stage),
    'session-timeline__item--upcoming':
      !isCompleted(stage) && stage !== props.currentStage,
  }
}
</script>

<style scoped>
.session-timeline {
  padding: 12px 4px;
  overflow-x: auto;
}

.session-timeline__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  gap: 4px;
  min-width: max-content;
}

.session-timeline__btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border: none;
  border-radius: 12px;
  background: transparent;
  color: var(--text-muted, #3f4f63);
  cursor: pointer;
  font-size: 0.8125rem;
  white-space: nowrap;
  transition: background 200ms ease-out, color 200ms ease-out;
}

.session-timeline__btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.session-timeline__item--current .session-timeline__btn {
  background: color-mix(in srgb, var(--color-primary, #6366f1) 14%, transparent);
  color: var(--color-primary-deep, #4f46e5);
  font-weight: 700;
}

.session-timeline__item--done .session-timeline__btn {
  color: var(--text-primary, #0c1929);
}

.session-timeline__mark {
  width: 22px;
  height: 22px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: color-mix(in srgb, var(--color-primary, #6366f1) 16%, transparent);
  color: var(--color-primary-deep, #4f46e5);
  flex-shrink: 0;
}

.session-timeline__item--upcoming .session-timeline__mark {
  background: transparent;
}

.session-timeline__dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: var(--color-primary, #6366f1);
}

.session-timeline__ring {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  border: 2px solid color-mix(in srgb, var(--text-muted, #3f4f63) 50%, transparent);
}

@media (prefers-reduced-motion: reduce) {
  .session-timeline__btn {
    transition: none;
  }
}
</style>
