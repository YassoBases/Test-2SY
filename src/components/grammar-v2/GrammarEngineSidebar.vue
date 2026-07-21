<template>
  <AppCard class="engine-sidebar" solid padding="md">
    <h2 class="engine-sidebar__title">{{ t('student.grammarV2.sidebar.title') }}</h2>

    <div class="engine-sidebar__block">
      <p class="engine-sidebar__label">{{ t('student.grammarV2.sidebar.currentGrammar') }}</p>
      <p class="engine-sidebar__value eng-island" dir="ltr">{{ currentName || '—' }}</p>
    </div>
    <div class="engine-sidebar__block">
      <p class="engine-sidebar__label">{{ t('student.grammarV2.sidebar.currentCefr') }}</p>
      <p class="engine-sidebar__value eng-island" dir="ltr">{{ cefr || '—' }}</p>
    </div>
    <div class="engine-sidebar__block">
      <p class="engine-sidebar__label">{{ t('student.grammarV2.sidebar.confidence') }}</p>
      <p class="engine-sidebar__value">{{ Math.round(confidence) }}%</p>
    </div>
    <div class="engine-sidebar__block">
      <p class="engine-sidebar__label">{{ t('student.grammarV2.sidebar.mastery') }}</p>
      <p class="engine-sidebar__value">{{ Math.round(mastery) }}%</p>
    </div>
    <div class="engine-sidebar__block">
      <p class="engine-sidebar__label">{{ t('student.grammarV2.sidebar.nextGrammar') }}</p>
      <p class="engine-sidebar__value eng-island" dir="ltr">{{ nextName || '—' }}</p>
    </div>
    <div class="engine-sidebar__block">
      <p class="engine-sidebar__label">{{ t('student.grammarV2.sidebar.eta') }}</p>
      <p class="engine-sidebar__value">
        {{ t('student.grammarV2.common.minutes', { n: minutes }) }}
      </p>
    </div>
    <div v-if="recommendation" class="engine-sidebar__block">
      <p class="engine-sidebar__label">{{ t('student.grammarV2.sidebar.recommendation') }}</p>
      <p class="engine-sidebar__value eng-island" dir="ltr">{{ recommendation }}</p>
    </div>
  </AppCard>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import AppCard from '../ui/AppCard.vue'

defineProps({
  currentName: { type: String, default: '' },
  cefr: { type: String, default: '' },
  confidence: { type: Number, default: 0 },
  mastery: { type: Number, default: 0 },
  nextName: { type: String, default: '' },
  minutes: { type: Number, default: 18 },
  recommendation: { type: String, default: '' },
})

const { t } = useI18n()
</script>

<style scoped>
.engine-sidebar__title {
  margin: 0 0 16px;
  font-size: 1.0625rem;
}

.engine-sidebar__block {
  margin-block-start: 14px;
}

.engine-sidebar__label {
  margin: 0 0 4px;
  font-size: 0.75rem;
  color: var(--text-muted, #3f4f63);
}

.engine-sidebar__value {
  margin: 0;
  font-weight: 600;
  font-size: 0.9375rem;
}

.eng-island {
  unicode-bidi: isolate;
}
</style>
