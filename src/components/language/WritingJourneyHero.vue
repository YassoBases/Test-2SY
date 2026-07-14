<template>

  <v-card class="writing-hero pa-6 mb-4" variant="flat">

    <div class="text-overline text-medium-emphasis mb-1">{{ t('student.languages.writingJourney.hero.eyebrow') }}</div>

    <h2 class="text-h5 font-weight-bold mb-3">{{ t('student.languages.writingJourney.hero.title') }}</h2>

    <p v-if="progressSummary" class="text-body-2 mb-3">{{ progressSummary }}</p>

    <p v-else class="text-body-2 text-medium-emphasis mb-4">{{ t('student.languages.writingJourney.hero.subtitle') }}</p>

    <div class="writing-hero__stats">

      <div class="writing-hero__stat">

        <div class="writing-hero__stat-label">{{ t('student.languages.writingJourney.hero.officialLevel') }}</div>

        <div class="writing-hero__stat-value">{{ officialCefr }}</div>

      </div>

      <div class="writing-hero__stat">

        <div class="writing-hero__stat-label">{{ t('student.languages.writingJourney.hero.stage') }}</div>

        <div class="writing-hero__stat-value">{{ stageDisplay }}</div>

      </div>

      <div class="writing-hero__stat">

        <div class="writing-hero__stat-label">{{ t('student.languages.writingJourney.hero.readiness') }}</div>

        <div class="writing-hero__stat-value">{{ readinessScore }}/100</div>

      </div>

      <div class="writing-hero__stat">

        <div class="writing-hero__stat-label">{{ t('student.languages.writingJourney.hero.goal') }}</div>

        <div class="writing-hero__stat-value">{{ goalLabel }}</div>

      </div>

      <div v-if="estimatedLessonsRemaining != null" class="writing-hero__stat">

        <div class="writing-hero__stat-label">{{ t('student.languages.writingJourney.hero.lessonsRemaining') }}</div>

        <div class="writing-hero__stat-value">{{ estimatedLessonsRemaining }}</div>

      </div>

      <div v-if="nextMilestone" class="writing-hero__stat">

        <div class="writing-hero__stat-label">{{ t('student.languages.writingJourney.hero.nextMilestone') }}</div>

        <div class="writing-hero__stat-value text-body-2">{{ nextMilestone }}</div>

      </div>

    </div>



    <v-progress-linear

      v-if="readinessScore != null"

      :model-value="readinessScore"

      color="secondary"

      height="8"

      rounded

      class="mt-4 mb-3"

    />



    <div v-if="blockers.length" class="blockers mt-2">

      <div class="text-caption text-medium-emphasis mb-1">{{ t('student.languages.writingJourney.hero.blockers') }}</div>

      <ul class="blocker-list mb-0">

        <li v-for="item in blockers.slice(0, 3)" :key="item">{{ item }}</li>

      </ul>

    </div>



    <v-chip

      v-if="canStartWpa"

      color="success"

      variant="tonal"

      size="small"

      class="mt-3"

      prepend-icon="mdi-rocket-launch"

    >

      {{ t('student.languages.writingJourney.hero.promotionAvailable') }}

    </v-chip>

  </v-card>

</template>



<script setup>

import { computed } from 'vue'

import { useI18n } from 'vue-i18n'

import { WRITING_LEARNING_GOALS } from '../../constants/writingGoals.js'



const props = defineProps({

  officialCefr: { type: String, default: 'B1' },

  activeGoalId: { type: String, default: 'travel' },

  learningStageLabel: { type: String, default: '' },

  learningStage: { type: Number, default: null },

  progressSummary: { type: String, default: '' },

  nextMilestone: { type: String, default: '' },

  readinessScore: { type: Number, default: null },

  readinessBand: { type: String, default: '' },

  estimatedLessonsRemaining: { type: Number, default: null },

  primaryBlockers: { type: Array, default: () => [] },

  canStartWpa: { type: Boolean, default: false },

})



const { t } = useI18n()



const goalLabel = computed(() => {

  const goal = WRITING_LEARNING_GOALS.find((g) => g.id === props.activeGoalId)

  return goal ? t(goal.labelKey) : props.activeGoalId

})



const stageDisplay = computed(() => {

  if (props.learningStageLabel) return props.learningStageLabel

  if (props.learningStage) return `${props.learningStage}/3`

  return '—'

})



const blockers = computed(() => props.primaryBlockers || [])

</script>



<style scoped>

.writing-hero {

  border-radius: 20px;

  background: linear-gradient(

    145deg,

    rgba(var(--v-theme-secondary), 0.08),

    rgba(var(--v-theme-surface), 0.95)

  );

  border: 1px solid rgba(var(--v-theme-on-surface), 0.06);

}

.writing-hero__stats {

  display: grid;

  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));

  gap: 0.75rem;

}

.writing-hero__stat {

  padding: 0.75rem 1rem;

  border-radius: 12px;

  background: rgba(var(--v-theme-on-surface), 0.04);

}

.writing-hero__stat-label {

  font-size: 0.75rem;

  color: rgba(var(--v-theme-on-surface), 0.62);

  margin-bottom: 0.25rem;

}

.writing-hero__stat-value {

  font-size: 1rem;

  font-weight: 700;

}

.blocker-list {

  margin: 0;

  padding-inline-start: 1.25rem;

  font-size: 0.875rem;

}

</style>


