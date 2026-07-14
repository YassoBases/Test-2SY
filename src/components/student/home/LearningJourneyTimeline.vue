<template>
  <AppSection
    id="journey"
    :title="t('student.home.journey.title')"
    :subtitle="t('student.home.journey.subtitle')"
    spacing="md"
    class="home-hub-section home-hub-section--timeline"
  >
    <div v-if="nodes.length" class="journey-timeline">
      <div
        v-for="(node, index) in nodes"
        :key="node.id"
        class="journey-node"
        :class="`journey-node--${node.status}`"
      >
        <div class="journey-node__track">
          <div class="journey-node__dot" :aria-label="statusLabel(node.status)">
            <v-icon v-if="node.status === 'done'" size="14" color="white">mdi-check</v-icon>
            <v-icon v-else-if="node.status === 'locked'" size="14">mdi-lock</v-icon>
            <span v-else class="journey-node__pulse" />
          </div>
          <div v-if="index < nodes.length - 1" class="journey-node__line" />
        </div>

        <AppCard
          class="journey-node__card"
          :class="{ 'journey-node__card--clickable': node.unlocked }"
          :interactive="node.unlocked"
          padding="md"
          :to="node.unlocked ? ROUTES.STUDENT_COURSE(node.id) : undefined"
        >
          <div class="journey-node__head">
            <div>
              <div class="journey-node__subject">{{ node.subject_name }}</div>
              <div class="journey-node__teacher text-caption text-medium-emphasis">
                {{ node.teacher_name }}
              </div>
            </div>
            <v-chip size="x-small" :color="statusColor(node.status)" variant="tonal">
              {{ statusLabel(node.status) }}
            </v-chip>
          </div>
          <div v-if="node.unlocked" class="journey-node__progress">
            <v-progress-linear
              :model-value="node.progress_percent || 0"
              height="6"
              rounded
              color="primary"
              class="journey-node__bar"
            />
            <span class="text-caption text-medium-emphasis">
              {{ t('student.home.journey.progressLine', {
                percent: node.progress_percent || 0,
                done: node.completed_lesson_count || 0,
                total: node.lesson_count,
              }) }}
            </span>
          </div>
          <p v-else class="journey-node__lock-msg text-caption mb-0">
            {{ node.lock_reason || t('student.home.journey.lockReason') }}
          </p>
        </AppCard>
      </div>
    </div>

    <AppEmptyState
      v-else
      preset="courses"
      :description="grade ? t('student.home.journey.empty.noCourses') : t('student.home.journey.empty.noGrade')"
      :action-label="grade ? t('student.home.subjects.empty.subscriptions') : t('student.home.subjects.empty.setGrade')"
      :action-to="grade ? ROUTES.STUDENT_SUBSCRIPTIONS : ROUTES.ONBOARDING_GRADE"
      :action-icon="grade ? 'mdi-credit-card' : 'mdi-school'"
    />
  </AppSection>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import { AppCard, AppEmptyState, AppSection } from '../../ui/index.js'
import { ROUTES } from '../../../constants/app.js'

const { t } = useI18n()

defineProps({
  nodes: { type: Array, default: () => [] },
  grade: { type: [Number, String], default: null },
})

function statusLabel(status) {
  const map = {
    done: t('student.home.journey.status.done'),
    active: t('student.home.journey.status.active'),
    ready: t('student.home.journey.status.ready'),
    locked: t('student.home.journey.status.locked'),
  }
  return map[status] || status
}

function statusColor(status) {
  const map = {
    done: 'success',
    active: 'primary',
    ready: 'info',
    locked: 'warning',
  }
  return map[status] || 'default'
}
</script>

<style scoped>
.journey-timeline {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.journey-node {
  display: grid;
  grid-template-columns: 36px 1fr;
  gap: 12px;
}

.journey-node__track {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 18px;
}

.journey-node__dot {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--em-surface-raised);
  border: 2px solid var(--em-border);
  flex-shrink: 0;
}

.journey-node--done .journey-node__dot {
  background: var(--em-success);
  border-color: var(--em-success);
}

.journey-node--active .journey-node__dot {
  background: var(--em-primary);
  border-color: var(--em-primary);
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.2);
}

.journey-node--locked .journey-node__dot {
  opacity: 0.7;
}

.journey-node__pulse {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #fff;
}

.journey-node--active .journey-node__pulse {
  animation: journey-pulse 1.6s ease-in-out infinite;
}

@keyframes journey-pulse {
  0%,
  100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.35);
    opacity: 0.65;
  }
}

.journey-node__bar :deep(.v-progress-linear__determinate) {
  transition: width 0.9s var(--em-ease-spring);
}

.journey-node__line {
  flex: 1;
  width: 2px;
  min-height: 24px;
  margin: 4px 0;
  background: linear-gradient(180deg, var(--em-border), transparent);
}

.journey-node__card {
  margin-bottom: 16px;
}

.journey-node--locked .journey-node__card {
  opacity: 0.82;
}

.journey-node__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 10px;
}

.journey-node__subject {
  font-weight: 700;
  font-size: var(--em-text-sm);
}

.journey-node__progress {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.journey-node__lock-msg {
  color: var(--em-text-muted);
}
</style>
