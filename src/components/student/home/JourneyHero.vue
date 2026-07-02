<template>
  <AppCard class="journey-hero journey-hero--primary" padding="md">
    <div class="journey-hero__accent" aria-hidden="true" />

    <div class="journey-hero__row">
      <div class="journey-hero__identity" aria-hidden="true">
        <div class="journey-hero__avatar">{{ initials }}</div>
      </div>

      <div class="journey-hero__main">
        <p class="journey-hero__eyebrow">{{ greeting }}</p>
        <h1 class="journey-hero__title">{{ displayName }}</h1>

        <p class="journey-hero__mission">
          <span class="journey-hero__mission-kicker">{{ mission.headline }}</span>
          <span class="journey-hero__mission-text">{{ missionLessonLine }}</span>
        </p>

        <div class="journey-hero__actions">
          <AppButton
            variant="primary"
            size="large"
            :to="mission.to"
            prepend-icon="mdi-play-circle"
            class="journey-hero__cta em-press"
          >
            {{ mission.ctaLabel }}
          </AppButton>
        </div>

        <p v-if="progressLine" class="journey-hero__progress">{{ progressLine }}</p>
      </div>
    </div>
  </AppCard>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { AppButton, AppCard } from '../../ui/index.js'

const { t } = useI18n()

const props = defineProps({
  name: { type: String, default: '' },
  mission: {
    type: Object,
    default: () => ({
      headline: '',
      lessonTitle: '',
      ctaLabel: '',
      to: '/student/dashboard',
      lessonCount: 0,
      completedLessons: 0,
    }),
  },
})

const displayName = computed(() => props.name || t('student.common.defaultStudentName'))

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 17) return t('student.home.greeting.morning')
  return t('student.home.greeting.evening')
})

const initials = computed(() => {
  const parts = displayName.value.trim().split(/\s+/).filter(Boolean)
  if (parts.length >= 2) return `${parts[0][0]}${parts[1][0]}`
  return displayName.value.slice(0, 2) || t('student.common.defaultStudentName').slice(0, 1)
})

const missionLessonLine = computed(() => {
  const title = props.mission.lessonTitle?.trim()
  if (!title) return ''
  if (props.mission.kind === 'lesson') return t('student.home.mission.completeLesson', { title })
  return title
})

const progressLine = computed(() => {
  const total = props.mission.lessonCount || 0
  const done = props.mission.completedLessons || 0
  if (total <= 0) return ''
  return t('student.home.mission.progress', { done, total })
})
</script>

<style scoped>
.journey-hero {
  position: relative;
  overflow: hidden;
  margin-bottom: 0;
}

.journey-hero__accent {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--em-primary) 0%, var(--em-blue-soft) 100%);
}

.journey-hero__row {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 18px 22px;
  align-items: center;
  min-height: 132px;
}

.journey-hero__identity {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4px 0;
}

.journey-hero__avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  border-radius: 18px;
  font-family: var(--font-display);
  font-size: 1.15rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: var(--em-primary-deep);
  background: var(--em-surface-secondary);
  border: 1px solid var(--em-border-subtle);
}

@media (min-width: 600px) {
  .journey-hero__row {
    gap: 20px 28px;
    min-height: 148px;
  }

  .journey-hero__avatar {
    width: 68px;
    height: 68px;
    font-size: 1.2rem;
  }
}

.journey-hero__main {
  flex: 1;
  min-width: 0;
}

.journey-hero__eyebrow {
  margin: 0 0 4px;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--em-text-muted);
}

.journey-hero__title {
  margin: 0 0 10px;
  font-family: var(--font-display);
  font-size: clamp(1.5rem, 4.2vw, 1.95rem);
  font-weight: 800;
  line-height: 1.12;
  letter-spacing: -0.03em;
  color: var(--em-text);
}

.journey-hero__mission {
  margin: 0 0 14px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-width: 48ch;
}

.journey-hero__mission-kicker {
  font-size: 0.8125rem;
  font-weight: 700;
  color: var(--em-primary-deep);
  line-height: 1.35;
}

.journey-hero__mission-text {
  font-size: 1rem;
  font-weight: 700;
  line-height: 1.4;
  color: var(--em-text);
  letter-spacing: -0.015em;
}

.journey-hero__actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.journey-hero__cta {
  font-weight: 700;
}

.journey-hero__progress {
  margin: 10px 0 0;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--em-text-muted);
  line-height: 1.4;
}
</style>
