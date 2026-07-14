<template>
  <v-card class="how-card pa-6 mb-4" variant="flat">
    <div class="d-flex align-center gap-2 mb-4">
      <v-icon color="secondary" size="28">mdi-map-marker-path</v-icon>
      <h3 class="text-h6 font-weight-bold mb-0">{{ t('student.languages.coach.ux.howItWorks.title') }}</h3>
    </div>
    <div class="how-steps">
      <div v-for="(step, idx) in steps" :key="step.key" class="how-step">
        <div class="how-step-marker">
          <div class="how-step-number">{{ idx + 1 }}</div>
          <div v-if="idx < steps.length - 1" class="how-step-line" />
        </div>
        <div class="how-step-body pb-4">
          <div class="text-subtitle-1 font-weight-bold">{{ step.title }}</div>
          <p class="text-body-2 text-medium-emphasis mb-0">{{ step.body }}</p>
        </div>
      </div>
    </div>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const steps = computed(() => [
  {
    key: 'practice',
    title: t('student.languages.coach.ux.howItWorks.steps.practice.title'),
    body: t('student.languages.coach.ux.howItWorks.steps.practice.body'),
  },
  {
    key: 'improve',
    title: t('student.languages.coach.ux.howItWorks.steps.improve.title'),
    body: t('student.languages.coach.ux.howItWorks.steps.improve.body'),
  },
  {
    key: 'unlock',
    title: t('student.languages.coach.ux.howItWorks.steps.unlock.title'),
    body: t('student.languages.coach.ux.howItWorks.steps.unlock.body'),
  },
  {
    key: 'pass',
    title: t('student.languages.coach.ux.howItWorks.steps.pass.title'),
    body: t('student.languages.coach.ux.howItWorks.steps.pass.body'),
  },
  {
    key: 'promote',
    title: t('student.languages.coach.ux.howItWorks.steps.promote.title'),
    body: t('student.languages.coach.ux.howItWorks.steps.promote.body'),
  },
])
</script>

<style scoped>
.how-card {
  border-radius: 20px;
}
.how-steps {
  display: flex;
  flex-direction: column;
}
.how-step {
  display: flex;
  gap: 1rem;
}
.how-step-marker {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 2rem;
  flex-shrink: 0;
}
.how-step-number {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.875rem;
  background: rgba(var(--v-theme-secondary), 0.18);
  color: rgb(var(--v-theme-secondary));
}
.how-step-line {
  flex: 1;
  width: 2px;
  min-height: 1.5rem;
  margin: 0.25rem 0;
  background: rgba(var(--v-theme-on-surface), 0.12);
}
.how-step-body {
  flex: 1;
  min-width: 0;
}
</style>
