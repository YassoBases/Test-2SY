<template>
  <v-card class="skill-path-card glass-card" variant="flat">
    <div class="skill-path-head">
      <div>
        <h3 class="skill-path-title">{{ skillLabel }} journey</h3>
        <p class="skill-path-sub mb-0">{{ stages.length }} stages · follow the glow</p>
      </div>
      <div class="path-legend">
        <span><i class="path-dot path-dot--current" /> Current</span>
        <span><i class="path-dot path-dot--unlocked" /> Open</span>
        <span><i class="path-dot path-dot--locked" /> Locked</span>
      </div>
    </div>

    <div class="path-map" dir="rtl">
      <div v-for="level in CEFR_LEVELS" :key="level" class="path-row">
        <div class="path-row__level">{{ level }}</div>
        <div class="path-row__track">
          <div
            v-for="stage in stagesFor(level)"
            :key="`${skillKey}-${stage.cefr_level}-${stage.internal_stage}`"
            class="stage-node"
            :class="`stage-node--${stage.status}`"
            :title="stage.reason || statusLabel(stage.status)"
          >
            <div class="stage-node__orb">
              <v-icon :icon="stageIcon(stage.status)" size="16" />
            </div>
            <div class="stage-node__meta">
              <strong>{{ stage.internal_stage }}</strong>
              <small>{{ statusLabel(stage.status) }}</small>
            </div>
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

function stageReason({ cefr, status }) {
  if (status === 'current') return props.currentReason
  if (status === 'unlocked') return 'Ready when you reach this step.'
  if (cefr !== normalizedCefr.value) return props.nextLevelReason
  return 'Complete the previous stage first.'
}
</script>

<style scoped>
.skill-path-card {
  padding: 1.2rem 1.25rem;
  margin-bottom: 1rem;
}

.skill-path-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}

.skill-path-title {
  font-size: 1.05rem;
  font-weight: 700;
  margin: 0 0 0.15rem;
}

.skill-path-sub {
  font-size: 0.8125rem;
  color: rgba(var(--v-theme-on-surface), 0.55);
}

.path-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  font-size: 0.72rem;
  color: rgba(var(--v-theme-on-surface), 0.55);
}

.path-legend span {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.path-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.path-dot--current {
  background: rgb(var(--v-theme-secondary));
  box-shadow: 0 0 0 3px rgba(var(--v-theme-secondary), 0.25);
}

.path-dot--unlocked {
  background: rgb(var(--v-theme-primary));
}

.path-dot--locked {
  background: rgba(var(--v-theme-on-surface), 0.28);
}

.path-map {
  display: grid;
  gap: 0.85rem;
}

.path-row {
  display: grid;
  grid-template-columns: 44px 1fr;
  align-items: center;
  gap: 0.65rem;
}

.path-row__level {
  font-weight: 800;
  font-size: 0.95rem;
  color: rgb(var(--v-theme-secondary));
}

.path-row__track {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.45rem;
}

.stage-node {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  min-height: 58px;
  padding: 0.55rem 0.65rem;
  border-radius: 14px;
  border: 1px solid rgba(var(--v-theme-on-surface), 0.1);
  background: rgba(var(--v-theme-surface), 0.45);
}

.stage-node__orb {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  flex: 0 0 auto;
  background: rgba(var(--v-theme-on-surface), 0.06);
}

.stage-node__meta {
  display: flex;
  flex-direction: column;
  gap: 0.05rem;
  min-width: 0;
}

.stage-node__meta strong {
  font-size: 0.78rem;
  font-weight: 700;
  line-height: 1.2;
}

.stage-node__meta small {
  font-size: 0.65rem;
  color: rgba(var(--v-theme-on-surface), 0.55);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.stage-node--current {
  border-color: rgba(var(--v-theme-secondary), 0.7);
  background: rgba(var(--v-theme-secondary), 0.14);
  box-shadow:
    0 0 0 1px rgba(var(--v-theme-secondary), 0.2),
    0 8px 22px -14px rgba(var(--v-theme-secondary), 0.55);
}

.stage-node--current .stage-node__orb {
  background: rgba(var(--v-theme-secondary), 0.22);
  color: rgb(var(--v-theme-secondary));
  animation: stage-pulse 2.2s ease-in-out infinite;
}

.stage-node--unlocked {
  border-color: rgba(var(--v-theme-primary), 0.4);
  background: rgba(var(--v-theme-primary), 0.08);
}

.stage-node--locked {
  opacity: 0.58;
}

@keyframes stage-pulse {
  0%,
  100% {
    box-shadow: 0 0 0 0 rgba(var(--v-theme-secondary), 0.35);
  }
  50% {
    box-shadow: 0 0 0 6px rgba(var(--v-theme-secondary), 0);
  }
}

@media (max-width: 760px) {
  .path-row {
    grid-template-columns: 1fr;
  }

  .path-row__track {
    grid-template-columns: 1fr;
  }
}

@media (prefers-reduced-motion: reduce) {
  .stage-node--current .stage-node__orb {
    animation: none;
  }
}
</style>
