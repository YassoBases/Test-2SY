<template>
  <AppCard class="ai-sidebar" solid padding="md">
    <h2 class="ai-sidebar__title">
      <v-icon icon="mdi-robot-outline" size="22" aria-hidden="true" />
      {{ t('student.englishJourney.sidebar.title') }}
    </h2>

    <MissionCard :mission="mission" />

    <div v-if="energy" class="ai-sidebar__block">
      <p class="ai-sidebar__label">{{ t('student.englishJourney.sidebar.energy') }}</p>
      <p class="ai-sidebar__value eng-island" dir="ltr">{{ energy.level || '—' }}</p>
    </div>

    <div class="ai-sidebar__block">
      <p class="ai-sidebar__label">{{ t('student.englishJourney.sidebar.confidence') }}</p>
      <p class="ai-sidebar__value">{{ Math.round(confidence) }}%</p>
    </div>

    <div v-if="nextMilestone" class="ai-sidebar__block">
      <p class="ai-sidebar__label">{{ t('student.englishJourney.sidebar.nextMilestone') }}</p>
      <p class="ai-sidebar__value eng-island" dir="ltr">{{ nextMilestone }}</p>
    </div>
  </AppCard>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import AppCard from '../ui/AppCard.vue'
import MissionCard from './MissionCard.vue'

defineProps({
  mission: { type: Object, default: null },
  energy: { type: Object, default: null },
  confidence: { type: Number, default: 0 },
  nextMilestone: { type: String, default: '' },
})

const { t } = useI18n()
</script>

<style scoped>
.ai-sidebar__title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 16px;
  font-size: 1.0625rem;
}

.ai-sidebar__block {
  margin-block-start: 16px;
}

.ai-sidebar__label {
  margin: 0 0 4px;
  font-size: 0.75rem;
  color: var(--text-muted, #3f4f63);
}

.ai-sidebar__value {
  margin: 0;
  font-weight: 600;
}

.eng-island {
  unicode-bidi: isolate;
}
</style>
