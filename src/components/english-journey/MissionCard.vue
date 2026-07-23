<template>
  <AppCard v-if="mission" class="mission-card" solid padding="md">
    <p class="mission-card__label">{{ t('student.englishJourney.sidebar.mission') }}</p>
    <h3 class="mission-card__title eng-island" dir="ltr">{{ mission.title }}</h3>
    <p v-if="mission.scenario" class="mission-card__scenario eng-island" dir="ltr">
      {{ mission.scenario }}
    </p>
  </AppCard>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import AppCard from '../ui/AppCard.vue'

defineProps({
  mission: { type: Object, default: null },
})

const { t } = useI18n()
</script>

<style scoped>
.mission-card__label {
  margin: 0 0 6px;
  font-size: 0.75rem;
  color: var(--text-muted, #3f4f63);
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.mission-card__title {
  margin: 0 0 8px;
  font-size: 1.0625rem;
}

.mission-card__scenario {
  margin: 0;
  font-size: 0.875rem;
  color: var(--text-muted, #3f4f63);
}

.eng-island {
  unicode-bidi: isolate;
}
</style>
