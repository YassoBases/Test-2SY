<template>
  <v-card class="goals-card pa-6 mb-4" variant="flat">
    <div class="d-flex align-center justify-space-between flex-wrap gap-2 mb-2">
      <div>
        <div class="text-overline text-medium-emphasis">{{ t('student.languages.listeningJourney.goals.eyebrow') }}</div>
        <h3 class="text-h6 font-weight-bold mb-0">{{ t('student.languages.coach.ux.goals.title') }}</h3>
      </div>
      <v-fade-transition>
        <span v-if="goalSaved" class="text-success text-caption">{{ t('student.languages.listeningJourney.goals.saved') }}</span>
      </v-fade-transition>
    </div>
    <p class="text-body-2 text-medium-emphasis mb-5">{{ t('student.languages.coach.ux.goals.subtitle') }}</p>

    <v-row dense>
      <v-col v-for="goal in goals" :key="goal.id" cols="12" sm="6" md="4">
        <button
          type="button"
          class="goal-card"
          :class="{ 'goal-card--active': activeGoalId === goal.id }"
          :disabled="saving"
          @click="$emit('select', goal.id)"
        >
          <v-icon :icon="goal.icon" size="28" class="goal-card-icon mb-2" />
          <div class="goal-card-title">{{ t(goal.labelKey) }}</div>
          <div class="goal-card-desc">{{ t(goal.descKey) }}</div>
        </button>
      </v-col>
    </v-row>
  </v-card>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import { LISTENING_LEARNING_GOALS } from '../../constants/listeningGoals.js'

defineProps({
  activeGoalId: { type: String, default: 'general_english' },
  saving: { type: Boolean, default: false },
  goalSaved: { type: Boolean, default: false },
})

defineEmits(['select'])

const { t } = useI18n()
const goals = LISTENING_LEARNING_GOALS
</script>

<style scoped>
.goals-card {
  border-radius: 20px;
}
.goal-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  width: 100%;
  text-align: start;
  padding: 1.25rem;
  border-radius: 16px;
  border: 2px solid rgba(var(--v-theme-on-surface), 0.08);
  background: rgba(var(--v-theme-on-surface), 0.02);
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s, transform 0.15s;
}
.goal-card:hover:not(:disabled) {
  border-color: rgba(var(--v-theme-secondary), 0.35);
  transform: translateY(-2px);
}
.goal-card--active {
  border-color: rgb(var(--v-theme-secondary));
  background: rgba(var(--v-theme-secondary), 0.1);
}
.goal-card:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.goal-card-icon {
  color: rgb(var(--v-theme-secondary));
}
.goal-card-title {
  font-size: 1rem;
  font-weight: 700;
  margin-bottom: 0.35rem;
}
.goal-card-desc {
  font-size: 0.8125rem;
  line-height: 1.45;
  color: rgba(var(--v-theme-on-surface), 0.68);
}
</style>
