<template>
  <TeacherWorkspaceCard
    class="teacher-profile-onboarding tds-scope"
    :title="$t('teacher.onboarding.title')"
    :meta="$t('teacher.onboarding.meta')"
    :aria-label="$t('teacher.onboarding.aria')"
  >
    <div class="teacher-profile-onboarding__pipeline" :aria-label="$t('teacher.onboarding.pipelineAria')">
      <div
        v-for="(node, index) in pipelineNodes"
        :key="node.id"
        class="teacher-profile-onboarding__pipeline-item"
      >
        <article class="teacher-profile-onboarding__pipeline-card">
          <span class="teacher-profile-onboarding__pipeline-icon" aria-hidden="true">
            <v-icon :icon="node.icon" size="18" />
          </span>
          <span class="teacher-profile-onboarding__pipeline-label">{{ node.label }}</span>
        </article>
        <div
          v-if="index < pipelineNodes.length - 1"
          class="teacher-profile-onboarding__flow-connector"
          aria-hidden="true"
        >
          <span class="teacher-profile-onboarding__flow-line" />
          <v-icon icon="mdi-chevron-down" size="22" class="teacher-profile-onboarding__flow-arrow" />
        </div>
      </div>
    </div>

    <ol class="teacher-profile-onboarding__steps">
      <li
        v-for="(step, index) in steps"
        :key="step.id"
        class="teacher-profile-onboarding__step"
      >
        <article class="teacher-profile-onboarding__step-card">
          <div class="teacher-profile-onboarding__step-head">
            <span class="teacher-profile-onboarding__step-emoji" aria-hidden="true">{{ step.emoji }}</span>
            <h3 class="teacher-profile-onboarding__step-title">{{ step.title }}</h3>
          </div>
          <p class="teacher-profile-onboarding__step-text">{{ step.text }}</p>
        </article>

        <div
          v-if="index < steps.length - 1"
          class="teacher-profile-onboarding__flow-connector teacher-profile-onboarding__flow-connector--step"
          aria-hidden="true"
        >
          <span class="teacher-profile-onboarding__flow-line" />
          <v-icon icon="mdi-chevron-down" size="22" class="teacher-profile-onboarding__flow-arrow" />
        </div>
      </li>
    </ol>

    <TeacherFormHint variant="info" class="teacher-profile-onboarding__hint">
      {{ $t('teacher.onboarding.footerHint') }}
    </TeacherFormHint>
  </TeacherWorkspaceCard>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import { TeacherWorkspaceCard, TeacherFormHint } from '../design-system/index.js'

const pipelineNodes = [
  { id: 'teacher', label: t('teacher.onboarding.you'), icon: 'mdi-account-tie' },
  { id: 'platform', label: 'EduSpark', icon: 'mdi-school-outline' },
  { id: 'students', label: t('teacher.onboarding.yourStudents'), icon: 'mdi-account-school' },
]

const steps = [
  {
    id: 'identity',
    emoji: '👤',
    title: t('teacher.onboarding.identityTitle'),
    text: t('teacher.onboarding.identityText'),
  },
  {
    id: 'video',
    emoji: '🎥',
    title: t('teacher.onboarding.videoTitle'),
    text: t('teacher.onboarding.videoText'),
  },
  {
    id: 'pdf',
    emoji: '📄',
    title: t('teacher.onboarding.pdfTitle'),
    text: t('teacher.onboarding.pdfText'),
  },
  {
    id: 'lessons',
    emoji: '📚',
    title: t('teacher.onboarding.lessonsTitle'),
    text: t('teacher.onboarding.lessonsText'),
  },
  {
    id: 'quizzes',
    emoji: '📝',
    title: t('teacher.onboarding.quizzesTitle'),
    text: t('teacher.onboarding.quizzesText'),
  },
  {
    id: 'progress',
    emoji: '📊',
    title: t('teacher.onboarding.progressTitle'),
    text: t('teacher.onboarding.progressText'),
  },
  {
    id: 'messages',
    emoji: '💬',
    title: t('teacher.onboarding.messagesTitle'),
    text: t('teacher.onboarding.messagesText'),
  },
  {
    id: 'parents',
    emoji: '👨‍👩‍👧',
    title: t('teacher.onboarding.parentsTitle'),
    text: t('teacher.onboarding.parentsText'),
  },
  {
    id: 'assistant',
    emoji: '🤝',
    title: t('teacher.onboarding.assistantTitle'),
    text: t('teacher.onboarding.assistantText'),
  },
]
</script>

<style scoped>
.teacher-profile-onboarding {
  --teacher-onboarding-flow: #e8564a;
  --teacher-onboarding-flow-deep: #d84332;
  margin-bottom: var(--em-space-xl);
}

.teacher-profile-onboarding__pipeline {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--em-space-md);
  padding: var(--em-space-md);
  margin-bottom: var(--em-space-lg);
  border-radius: var(--em-radius-lg, 16px);
  background: rgba(var(--v-theme-on-surface), 0.02);
  border: 1px solid var(--em-border-subtle);
}

@media (min-width: 640px) {
  .teacher-profile-onboarding__pipeline {
    flex-direction: row;
    justify-content: center;
    align-items: center;
    gap: var(--em-space-sm);
  }
}

.teacher-profile-onboarding__pipeline-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

@media (min-width: 640px) {
  .teacher-profile-onboarding__pipeline-item {
    flex-direction: row;
    align-items: center;
  }
}

.teacher-profile-onboarding__pipeline-card,
.teacher-profile-onboarding__step-card {
  border-radius: var(--em-radius-sm, 10px);
  border: 1px solid color-mix(in srgb, var(--em-primary) 28%, var(--em-border-subtle));
  background: color-mix(in srgb, var(--em-primary) 4%, var(--em-surface, rgb(var(--v-theme-surface))));
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04), 0 4px 14px rgba(var(--v-theme-secondary), 0.06);
  transition:
    border-color var(--em-duration-fast, 0.15s) ease,
    box-shadow var(--em-duration-fast, 0.15s) ease,
    transform var(--em-duration-fast, 0.15s) ease;
}

.teacher-profile-onboarding__pipeline-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  min-width: 72px;
  padding: 10px 12px;
}

.teacher-profile-onboarding__step-card {
  padding: 12px 14px;
}

.teacher-profile-onboarding__step-card:hover {
  border-color: color-mix(in srgb, var(--em-primary) 42%, var(--em-border-bright));
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05), 0 8px 20px rgba(var(--v-theme-secondary), 0.1);
  transform: translateY(-1px);
}

.teacher-profile-onboarding__pipeline-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: 10px;
  background: color-mix(in srgb, var(--em-primary) 10%, transparent);
  color: var(--em-primary-deep, var(--em-primary));
}

.teacher-profile-onboarding__pipeline-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--em-text);
}

.teacher-profile-onboarding__flow-connector {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  padding: var(--em-space-md) 0;
  color: var(--teacher-onboarding-flow);
}

.teacher-profile-onboarding__flow-connector--step {
  padding: var(--em-space-lg) 0;
}

@media (min-width: 640px) {
  .teacher-profile-onboarding__flow-connector {
    flex-direction: row;
    padding: 0 var(--em-space-sm);
  }

  .teacher-profile-onboarding__flow-connector--step {
    flex-direction: column;
    padding: var(--em-space-lg) 0;
  }
}

.teacher-profile-onboarding__flow-line {
  width: 3px;
  height: 18px;
  border-radius: 2px;
  background: linear-gradient(
    180deg,
    var(--teacher-onboarding-flow),
    color-mix(in srgb, var(--teacher-onboarding-flow) 35%, transparent)
  );
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--teacher-onboarding-flow) 18%, transparent);
}

@media (min-width: 640px) {
  .teacher-profile-onboarding__pipeline-item .teacher-profile-onboarding__flow-line {
    width: 18px;
    height: 3px;
    background: linear-gradient(
      90deg,
      var(--teacher-onboarding-flow),
      color-mix(in srgb, var(--teacher-onboarding-flow) 35%, transparent)
    );
  }
}

.teacher-profile-onboarding__flow-arrow {
  color: var(--teacher-onboarding-flow-deep);
  filter: drop-shadow(0 1px 2px color-mix(in srgb, var(--teacher-onboarding-flow) 35%, transparent));
  animation: teacher-profile-onboarding-bounce 2s ease-in-out infinite;
}

@media (min-width: 640px) {
  .teacher-profile-onboarding__pipeline-item .teacher-profile-onboarding__flow-arrow {
    transform: rotate(-90deg);
  }
}

.teacher-profile-onboarding__steps {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0;
}

.teacher-profile-onboarding__step {
  display: flex;
  flex-direction: column;
}

.teacher-profile-onboarding__step-head {
  display: flex;
  align-items: center;
  gap: var(--em-space-sm);
  margin-bottom: 6px;
}

.teacher-profile-onboarding__step-emoji {
  font-size: 1.125rem;
  line-height: 1;
  flex-shrink: 0;
}

.teacher-profile-onboarding__step-title {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 700;
  line-height: 1.35;
  color: var(--em-text);
}

.teacher-profile-onboarding__step-text {
  margin: 0;
  font-size: 0.8125rem;
  line-height: 1.55;
  color: var(--em-text-muted);
}

.teacher-profile-onboarding__hint {
  margin-top: var(--em-space-lg);
}

@keyframes teacher-profile-onboarding-bounce {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(3px);
  }
}

@media (min-width: 640px) {
  @keyframes teacher-profile-onboarding-bounce {
    0%,
    100% {
      transform: rotate(-90deg) translateY(0);
    }
    50% {
      transform: rotate(-90deg) translateY(3px);
    }
  }

  .teacher-profile-onboarding__flow-connector--step .teacher-profile-onboarding__flow-arrow {
    transform: none;
    animation-name: teacher-profile-onboarding-bounce-vertical;
  }
}

@keyframes teacher-profile-onboarding-bounce-vertical {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(3px);
  }
}

@media (prefers-reduced-motion: reduce) {
  .teacher-profile-onboarding__flow-arrow {
    animation: none;
  }
}
</style>
