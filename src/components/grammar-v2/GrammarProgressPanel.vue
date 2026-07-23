<template>
  <AppCard class="grammar-progress" solid padding="md">
    <h2 class="grammar-progress__title">{{ t('student.grammarV2.progress.title') }}</h2>
    <div
      class="grammar-progress__track"
      role="progressbar"
      :aria-valuenow="percent"
      aria-valuemin="0"
      aria-valuemax="100"
      :aria-label="t('student.grammarV2.progress.title')"
    >
      <div class="grammar-progress__fill" :style="{ width: `${percent}%` }" />
    </div>
    <dl class="grammar-progress__stats">
      <div>
        <dt>{{ t('student.grammarV2.progress.completed') }}</dt>
        <dd>{{ completed }}/{{ total }}</dd>
      </div>
      <div>
        <dt>{{ t('student.grammarV2.progress.cefr') }}</dt>
        <dd class="eng-island" dir="ltr">{{ cefr || '—' }}</dd>
      </div>
      <div>
        <dt>{{ t('student.grammarV2.progress.stage') }}</dt>
        <dd>{{ stageIndex }}/{{ stageTotal || '—' }}</dd>
      </div>
      <div>
        <dt>{{ t('student.grammarV2.progress.remaining') }}</dt>
        <dd>{{ remaining }}</dd>
      </div>
      <div>
        <dt>{{ t('student.grammarV2.progress.percent') }}</dt>
        <dd>{{ percent }}%</dd>
      </div>
    </dl>
  </AppCard>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import AppCard from '../ui/AppCard.vue'

defineProps({
  completed: { type: Number, default: 0 },
  total: { type: Number, default: 0 },
  cefr: { type: String, default: '' },
  stageIndex: { type: Number, default: 0 },
  stageTotal: { type: Number, default: 0 },
  remaining: { type: Number, default: 0 },
  percent: { type: Number, default: 0 },
})

const { t } = useI18n()
</script>

<style scoped>
.grammar-progress {
  margin-block-end: 24px;
}

.grammar-progress__title {
  margin: 0 0 12px;
  font-size: 1.0625rem;
}

.grammar-progress__track {
  height: 10px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--color-primary, #6366f1) 12%, transparent);
  overflow: hidden;
  margin-block-end: 16px;
}

.grammar-progress__fill {
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #6366f1, #4f46e5);
  transition: width 280ms ease-out;
}

.grammar-progress__stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 12px;
  margin: 0;
}

.grammar-progress__stats dt {
  font-size: 0.75rem;
  color: var(--text-muted, #3f4f63);
}

.grammar-progress__stats dd {
  margin: 4px 0 0;
  font-weight: 700;
  font-size: 1.05rem;
}

.eng-island {
  unicode-bidi: isolate;
}

@media (prefers-reduced-motion: reduce) {
  .grammar-progress__fill {
    transition: none;
  }
}
</style>
