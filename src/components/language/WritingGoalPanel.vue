<template>
  <div class="goals-panel glass-card mb-4">
    <div class="goals-panel__head">
      <div>
        <p class="goals-panel__eyebrow mb-0">{{ t('student.languages.writingJourney.goals.eyebrow') }}</p>
        <h3 class="goals-panel__title">{{ t('student.languages.writingJourney.goals.title') }}</h3>
        <p class="goals-panel__sub mb-0">{{ t('student.languages.writingJourney.goals.subtitle') }}</p>
      </div>
      <v-fade-transition>
        <span v-if="goalSaved" class="goals-panel__saved">{{ t('student.languages.writingJourney.goals.saved') }}</span>
      </v-fade-transition>
    </div>

    <div class="goals-rail">
      <button
        v-for="(goal, idx) in goals"
        :key="goal.id"
        type="button"
        class="goal-tile"
        :class="{ 'goal-tile--active': activeGoalId === goal.id }"
        :style="{ '--i': idx }"
        :disabled="saving"
        @click="$emit('select', goal.id)"
      >
        <span class="goal-tile__orb" aria-hidden="true">
          <v-icon :icon="goal.icon" size="22" />
        </span>
        <span class="goal-tile__title">{{ t(goal.labelKey) }}</span>
        <span class="goal-tile__desc">{{ t(goal.descKey) }}</span>
        <span v-if="activeGoalId === goal.id" class="goal-tile__check" aria-hidden="true">
          <v-icon size="14">mdi-check</v-icon>
        </span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import { WRITING_LEARNING_GOALS } from '../../constants/writingGoals.js'

defineProps({
  activeGoalId: { type: String, default: 'travel' },
  saving: { type: Boolean, default: false },
  goalSaved: { type: Boolean, default: false },
})

defineEmits(['select'])

const { t } = useI18n()
const goals = WRITING_LEARNING_GOALS
</script>

<style scoped>
.goals-panel {
  position: relative;
  overflow: hidden;
  padding: 1.15rem 1.2rem 1.25rem;
}

.goals-panel::before {
  content: '';
  position: absolute;
  inset: -30% auto auto -8%;
  width: 220px;
  height: 220px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(var(--v-theme-secondary), 0.16), transparent 70%);
  pointer-events: none;
}

.goals-panel__head {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.85rem;
  margin-bottom: 0.95rem;
}

.goals-panel__eyebrow {
  font-size: 0.7rem;
  font-weight: 650;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: rgba(var(--v-theme-on-surface), 0.48);
}

.goals-panel__title {
  font-size: 1.15rem;
  font-weight: 750;
  letter-spacing: -0.02em;
  margin: 0.15rem 0 0.25rem;
  line-height: 1.25;
}

.goals-panel__sub {
  font-size: 0.84rem;
  color: rgba(var(--v-theme-on-surface), 0.58);
  line-height: 1.45;
  max-width: 36rem;
}

.goals-panel__saved {
  flex-shrink: 0;
  font-size: 0.75rem;
  font-weight: 650;
  color: rgb(var(--v-theme-success));
  padding: 0.3rem 0.7rem;
  border-radius: 999px;
  background: rgba(var(--v-theme-success), 0.12);
}

.goals-rail {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.7rem;
}

.goal-tile {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 0.45rem;
  min-height: 132px;
  padding: 0.95rem 0.7rem 0.85rem;
  border-radius: 18px;
  border: 1px solid rgba(var(--v-theme-on-surface), 0.08);
  background: linear-gradient(180deg, rgba(var(--v-theme-surface), 0.92), rgba(var(--v-theme-surface), 0.72));
  color: inherit;
  cursor: pointer;
  transition:
    border-color 0.2s ease,
    transform 0.22s cubic-bezier(0.22, 1, 0.36, 1),
    box-shadow 0.22s ease,
    background 0.2s ease;
  animation: goal-in 0.45s cubic-bezier(0.22, 1, 0.36, 1) both;
  animation-delay: calc(var(--i) * 28ms);
}

.goal-tile:hover:not(:disabled) {
  transform: translateY(-4px);
  border-color: rgba(var(--v-theme-secondary), 0.4);
  box-shadow: 0 14px 28px -18px rgba(var(--v-theme-secondary), 0.55);
}

.goal-tile--active {
  border-color: rgba(var(--v-theme-secondary), 0.85);
  background: linear-gradient(165deg, rgba(var(--v-theme-secondary), 0.18), rgba(var(--v-theme-surface), 0.9) 55%);
  box-shadow:
    0 0 0 1px rgba(var(--v-theme-secondary), 0.18),
    0 16px 30px -16px rgba(var(--v-theme-secondary), 0.55);
}

.goal-tile:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.goal-tile__orb {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  display: grid;
  place-items: center;
  color: rgb(var(--v-theme-secondary));
  background: rgba(var(--v-theme-secondary), 0.12);
  border: 1px solid rgba(var(--v-theme-secondary), 0.16);
  transition: transform 0.22s ease, background 0.2s ease;
}

.goal-tile:hover:not(:disabled) .goal-tile__orb,
.goal-tile--active .goal-tile__orb {
  transform: scale(1.06);
  background: rgba(var(--v-theme-secondary), 0.2);
}

.goal-tile__title {
  font-size: 0.88rem;
  font-weight: 750;
  line-height: 1.25;
  letter-spacing: -0.01em;
}

.goal-tile__desc {
  font-size: 0.72rem;
  line-height: 1.4;
  color: rgba(var(--v-theme-on-surface), 0.55);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.goal-tile__check {
  position: absolute;
  top: 0.55rem;
  inset-inline-start: 0.55rem;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: rgb(var(--v-theme-secondary));
  color: rgb(var(--v-theme-on-secondary));
  box-shadow: 0 4px 10px -4px rgba(var(--v-theme-secondary), 0.7);
}

@keyframes goal-in {
  from {
    opacity: 0;
    transform: translateY(8px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@media (max-width: 1100px) {
  .goals-rail {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 700px) {
  .goals-rail {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .goal-tile {
    min-height: 120px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .goal-tile {
    animation: none;
    transition: none;
  }

  .goal-tile:hover:not(:disabled),
  .goal-tile:hover:not(:disabled) .goal-tile__orb,
  .goal-tile--active .goal-tile__orb {
    transform: none;
  }
}
</style>
