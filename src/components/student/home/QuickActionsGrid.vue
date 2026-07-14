<template>
  <AppSection :title="t('student.home.quickActions.title')" :subtitle="t('student.home.quickActions.subtitle')">
    <div class="quick-grid">
      <AppCard
        v-for="action in actions"
        :key="action.key"
        interactive
        padding="md"
        :to="action.to"
        class="quick-card"
      >
        <div class="quick-card__icon" :style="{ background: action.tint }">
          <v-icon :icon="action.icon" size="26" :color="action.color" />
        </div>
        <div class="quick-card__title">{{ action.title }}</div>
        <div class="quick-card__desc">{{ action.description }}</div>
      </AppCard>
    </div>
  </AppSection>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { AppCard, AppSection } from '../../ui/index.js'
import { ROUTES } from '../../../constants/app.js'

const { t } = useI18n()

const props = defineProps({
  continueTo: { type: [String, Object], default: undefined },
  quizTo: { type: [String, Object], default: undefined },
})

const actions = computed(() => [
  {
    key: 'chat',
    title: t('student.home.quickActions.chat.title'),
    description: t('student.home.quickActions.chat.description'),
    icon: 'mdi-message-text-outline',
    color: 'primary',
    tint: 'rgba(99, 102, 241, 0.12)',
    to: ROUTES.STUDENT_MESSAGES,
  },
  {
    key: 'lesson',
    title: t('student.home.quickActions.lesson.title'),
    description: t('student.home.quickActions.lesson.description'),
    icon: 'mdi-play-circle-outline',
    color: 'secondary',
    tint: 'rgba(56, 189, 248, 0.12)',
    to: props.continueTo || ROUTES.STUDENT_COURSES,
  },
  {
    key: 'language',
    title: t('student.home.quickActions.language.title'),
    description: t('student.home.quickActions.language.description'),
    icon: 'mdi-translate',
    color: 'primary',
    tint: 'rgba(124, 58, 237, 0.1)',
    to: ROUTES.STUDENT_LANGUAGES,
  },
  {
    key: 'planner',
    title: t('student.home.quickActions.planner.title'),
    description: t('student.home.quickActions.planner.description'),
    icon: 'mdi-calendar-star',
    color: 'warning',
    tint: 'rgba(251, 191, 36, 0.12)',
    to: ROUTES.STUDENT_PLANNER,
  },
  {
    key: 'quiz',
    title: t('student.home.quickActions.quiz.title'),
    description: t('student.home.quickActions.quiz.description'),
    icon: 'mdi-clipboard-text-outline',
    color: 'success',
    tint: 'rgba(52, 211, 153, 0.12)',
    to: props.quizTo || ROUTES.STUDENT_COURSES,
  },
  {
    key: 'achievements',
    title: t('student.home.quickActions.achievements.title'),
    description: t('student.home.quickActions.achievements.description'),
    icon: 'mdi-trophy-outline',
    color: 'warning',
    tint: 'rgba(245, 158, 11, 0.12)',
    to: ROUTES.STUDENT_ACHIEVEMENTS,
  },
])
</script>

<style scoped>
.quick-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 14px;
}

@media (min-width: 960px) {
  .quick-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.quick-card {
  min-height: 148px;
}

.quick-card__icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 14px;
}

.quick-card__title {
  font-weight: 700;
  font-size: var(--em-text-sm);
  margin-bottom: 4px;
  color: var(--em-text);
}

.quick-card__desc {
  font-size: var(--em-text-caption);
  color: var(--em-text-muted);
  line-height: 1.45;
}
</style>
