<template>
  <AppSection
    id="my-report"
    :title="t('student.home.report.title')"
    :subtitle="t('student.home.report.subtitle')"
    spacing="md"
    class="home-hub-section home-hub-section--report"
  >
    <div class="report-grid">
      <div v-for="item in items" :key="item.key" class="report-card">
        <div class="report-card__icon" aria-hidden="true">
          <v-icon :icon="item.icon" size="20" color="primary" />
        </div>
        <div class="report-card__value">{{ item.value }}</div>
        <div class="report-card__label">{{ item.label }}</div>
      </div>
    </div>
  </AppSection>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { AppSection } from '../../ui/index.js'

const { t } = useI18n()

const props = defineProps({
  courses: { type: Array, default: () => [] },
  lessonStats: { type: Object, default: null },
  gamification: { type: Object, default: null },
  continueLesson: { type: Object, default: null },
  unlockedCount: { type: Number, default: 0 },
})

const items = computed(() => {
  const activeCount = props.unlockedCount || props.courses.filter((c) => c.unlocked).length
  const completed = props.lessonStats?.completed_lessons ?? 0

  let lastQuiz = t('student.home.report.lastQuizNone')
  const lesson = props.continueLesson
  if (lesson?.quiz_submitted && lesson.quiz_score_percent != null) {
    lastQuiz = `${Math.round(lesson.quiz_score_percent)}%`
  }

  const weekDays = studyDaysThisWeek(props.gamification)

  return [
    {
      key: 'active',
      icon: 'mdi-book-open-variant',
      value: String(activeCount),
      label: t('student.home.report.stats.activeSubjects'),
    },
    {
      key: 'completed',
      icon: 'mdi-check-circle-outline',
      value: String(completed),
      label: t('student.home.report.stats.completedLessons'),
    },
    {
      key: 'quiz',
      icon: 'mdi-clipboard-check-outline',
      value: lastQuiz,
      label: t('student.home.report.stats.lastQuiz'),
    },
    {
      key: 'week',
      icon: 'mdi-calendar-week',
      value: String(weekDays),
      label: t('student.home.report.stats.studyDays'),
    },
  ]
})

function studyDaysThisWeek(gamification) {
  if (!gamification) return 0
  const activities = gamification.recent_activity || []
  const weekAgo = Date.now() - 7 * 24 * 60 * 60 * 1000
  const days = new Set()
  for (const entry of activities) {
    if (!entry.occurred_at) continue
    const when = new Date(entry.occurred_at).getTime()
    if (Number.isNaN(when) || when < weekAgo) continue
    if (entry.kind === 'achievement') continue
    days.add(new Date(entry.occurred_at).toDateString())
  }
  if (days.size > 0) return days.size
  return Math.min(gamification.current_streak || 0, 7)
}
</script>

<style scoped>
.report-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

@media (min-width: 720px) {
  .report-grid {
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
  }
}

.report-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 6px;
  padding: 14px 14px 16px;
  border-radius: var(--em-radius-sm);
  background: var(--em-surface-secondary);
  border: 1px solid var(--em-border-subtle);
}

.report-card__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: 10px;
  background: var(--em-card-l1);
  border: 1px solid var(--em-border-subtle);
}

.report-card__value {
  font-family: var(--font-display);
  font-size: 1.35rem;
  font-weight: 800;
  line-height: 1.1;
  letter-spacing: -0.02em;
  color: var(--em-text);
}

.report-card__label {
  font-size: 0.75rem;
  font-weight: 600;
  line-height: 1.4;
  color: var(--em-text-muted);
}
</style>
