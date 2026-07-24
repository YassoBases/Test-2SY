<template>
  <v-card class="skill-path-card pa-5" variant="flat">
    <div class="skill-path-head">
      <div>
        <h3 class="text-subtitle-1 font-weight-bold mb-1">{{ skillLabel }} path</h3>
        <p class="text-body-2 text-medium-emphasis mb-0">
          CEFR levels split into Beginner, Intermediate, and Advanced stages.
        </p>
      </div>
      <v-chip size="small" variant="tonal" color="secondary">{{ stages.length }} stages</v-chip>
    </div>

    <div class="path-map">
      <div v-for="level in CEFR_LEVELS" :key="level" class="path-row">
        <div class="path-row__level">{{ level }}</div>
        <div class="path-row__stages">
          <div
            v-for="stage in stagesFor(level)"
            :key="`${skillKey}-${stage.cefr_level}-${stage.internal_stage}`"
            class="stage-pill"
            :class="`stage-pill--${stage.status}`"
          >
            <div class="stage-pill__top">
              <span>{{ stage.internal_stage }}</span>
              <v-icon :icon="stageIcon(stage.status)" :color="stageColor(stage.status)" size="18" />
            </div>
            <small>{{ statusLabel(stage.status) }}</small>
            <p class="stage-pill__reason">{{ stage.reason }}</p>
          </div>
        </div>
      </div>
    </div>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'

const CEFR_LEVELS = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
const INTERNAL_STAGES = ['Beginner', 'Intermediate', 'Advanced']

const props = defineProps({
  skillLabel: { type: String, default: 'Skill' },
  skillKey: { type: String, default: 'skill' },
  currentCefr: { type: String, default: 'A1' },
  currentStage: { type: [String, Number], default: 'Beginner' },
  currentReason: { type: String, default: 'Complete more practice attempts.' },
  nextLevelReason: { type: String, default: 'Pass the readiness test to unlock this level.' },
})

const normalizedCefr = computed(() => {
  const raw = String(props.currentCefr || '').trim().toUpperCase()
  return CEFR_LEVELS.includes(raw) ? raw : 'A1'
})

const normalizedStage = computed(() => normalizeStage(props.currentStage))

const currentRank = computed(() => stageRank(normalizedCefr.value, normalizedStage.value))

const stages = computed(() =>
  CEFR_LEVELS.flatMap((cefr) =>
    INTERNAL_STAGES.map((stage) => {
      const rank = stageRank(cefr, stage)
      const status = rank === currentRank.value ? 'current' : rank < currentRank.value ? 'unlocked' : 'locked'
      return {
        cefr_level: cefr,
        internal_stage: stage,
        rank,
        status,
        reason: stageReason({ cefr, stage, rank, status }),
      }
    }),
  ),
)

function normalizeStage(value) {
  if (typeof value === 'number') return INTERNAL_STAGES[Math.max(1, Math.min(3, value)) - 1]
  const clean = String(value || '').trim().toLowerCase()
  if (clean.includes('advanced') || clean === '3' || clean.includes('3/3')) return 'Advanced'
  if (clean.includes('intermediate') || clean === '2' || clean.includes('2/3')) return 'Intermediate'
  return 'Beginner'
}

function stageRank(cefr, stage) {
  return CEFR_LEVELS.indexOf(cefr) * INTERNAL_STAGES.length + INTERNAL_STAGES.indexOf(stage)
}

function stagesFor(level) {
  return stages.value.filter((stage) => stage.cefr_level === level)
}

function statusLabel(status) {
  const map = {
    current: 'Current',
    unlocked: 'Unlocked',
    locked: 'Locked',
  }
  return map[status] || status
}

function stageIcon(status) {
  const map = {
    current: 'mdi-map-marker-circle',
    unlocked: 'mdi-lock-open-variant-outline',
    locked: 'mdi-lock-outline',
  }
  return map[status] || 'mdi-circle-outline'
}

function stageColor(status) {
  const map = {
    current: 'secondary',
    unlocked: 'primary',
    locked: 'grey',
  }
  return map[status] || 'grey'
}

function stageReason(stage) {
  if (stage.status === 'current') return props.currentReason
  if (stage.status === 'unlocked') return 'Ready when you reach this step.'
  if (stage.cefr !== normalizedCefr.value) return props.nextLevelReason
  return 'Complete the previous stage first.'
}
</script>

<style scoped>
.skill-path-card {
  border-radius: 20px;
  background: rgba(var(--v-theme-surface), 0.92);
  border: 1px solid rgba(var(--v-theme-on-surface), 0.08);
}

.skill-path-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}

.path-map {
  display: grid;
  gap: 0.8rem;
}

.path-row {
  display: grid;
  grid-template-columns: 4rem 1fr;
  gap: 0.75rem;
  align-items: center;
}

.path-row__level {
  font-size: 1.25rem;
  font-weight: 900;
  color: rgb(var(--v-theme-secondary));
}

.path-row__stages {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.7rem;
}

.stage-pill {
  min-height: 7rem;
  border-radius: 10px;
  padding: 0.9rem;
  border: 1px solid rgba(var(--v-theme-on-surface), 0.1);
  background: rgba(var(--v-theme-surface), 0.96);
  transition: border-color 0.15s ease, background 0.15s ease, color 0.15s ease;
}

.stage-pill__top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  margin-bottom: 0.45rem;
}

.stage-pill span {
  font-weight: 800;
  color: rgb(var(--v-theme-on-surface));
}

.stage-pill small {
  display: block;
  color: rgba(var(--v-theme-on-surface), 0.66);
  margin-bottom: 0.45rem;
}

.stage-pill__reason {
  margin: 0;
  font-size: 0.82rem;
  line-height: 1.45;
  color: rgba(var(--v-theme-on-surface), 0.62);
}

.stage-pill--current {
  background: rgba(var(--v-theme-secondary), 0.13);
  border-color: rgba(var(--v-theme-secondary), 0.9);
}

.stage-pill--unlocked {
  background: rgba(var(--v-theme-primary), 0.05);
  border-color: rgba(var(--v-theme-primary), 0.5);
}

.stage-pill--locked {
  background: rgba(var(--v-theme-surface), 0.72);
  border-color: rgba(var(--v-theme-on-surface), 0.08);
  opacity: 0.68;
}

@media (max-width: 760px) {
  .path-row {
    grid-template-columns: 1fr;
    gap: 0.45rem;
  }

  .path-row__stages {
    grid-template-columns: 1fr;
  }

  .stage-pill {
    min-height: auto;
  }
}
</style>
