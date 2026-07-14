<template>
  <article class="teacher-quiz-card">
    <div class="teacher-quiz-card__menu">
      <v-menu location="bottom end" transition="lesson-menu-transition" :close-on-content-click="true">
        <template #activator="{ props: menuProps }">
          <v-btn
            v-bind="menuProps"
            icon
            variant="text"
            size="x-small"
            class="teacher-quiz-card__menu-btn"
            :aria-label="$t('teacher.quizzes.quizActions')"
          >
            <v-icon size="16">mdi-dots-vertical</v-icon>
          </v-btn>
        </template>

        <v-list class="lesson-workspace-menu" density="compact" nav>
          <v-list-item :to="builderTo" prepend-icon="mdi-open-in-new" :title="$t('teacher.actions.open')" />
          <v-list-item :to="builderTo" prepend-icon="mdi-pencil-outline" :title="$t('common.edit')" />
          <v-list-item :to="resultsTo" prepend-icon="mdi-chart-box-outline" :title="$t('teacher.quizzes.resultsTitle')" />
          <v-divider class="my-1" />
          <v-list-item
            prepend-icon="mdi-delete-outline"
            :title="$t('common.delete')"
            base-color="error"
            @click="$emit('delete')"
          />
        </v-list>
      </v-menu>
    </div>

    <div class="teacher-quiz-card__main">
      <h3 class="teacher-quiz-card__title">{{ quiz.title }}</h3>

      <div class="teacher-quiz-card__status" :class="statusClass">
        <span class="teacher-quiz-card__status-dot" aria-hidden="true" />
        <span>{{ statusLabel }}</span>
      </div>

      <p class="teacher-quiz-card__info">
        <span v-if="updatedLabel">{{ $t('teacher.labels.lastEditAt', { date: updatedLabel }) }}</span>
        <span v-if="updatedLabel" class="teacher-quiz-card__info-sep" aria-hidden="true">·</span>
        <span>{{ attemptText }}</span>
        <span class="teacher-quiz-card__info-sep" aria-hidden="true">·</span>
        <span>{{ $t('teacher.labels.averageValue', { value: averageLabel }) }}</span>
      </p>
    </div>

    <div class="teacher-quiz-card__footer">
      <v-btn
        class="teacher-quiz-card__cta btn-glow"
        color="secondary"
        variant="flat"
        rounded="lg"
        size="small"
        block
        :to="builderTo"
      >
        {{ $t('teacher.actions.openQuiz') }}
        <v-icon end size="16">mdi-arrow-left</v-icon>
      </v-btn>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import { formatLastSeen } from '../../../utils/sessionDisplay.js'

const props = defineProps({
  quiz: { type: Object, required: true },
  courseId: { type: [Number, String], required: true },
  averageScore: { type: Number, default: null },
})

defineEmits(['delete'])

const builderTo = computed(() => ({
  name: 'teacher-quiz-builder',
  params: { courseId: props.courseId, quizId: props.quiz.id },
}))

const resultsTo = computed(() => ({
  name: 'teacher-quiz-results',
  params: { courseId: props.courseId, quizId: props.quiz.id },
}))

const updatedLabel = computed(() => formatLastSeen(props.quiz.created_at))

const needsReview = computed(
  () => !props.quiz.is_published && (props.quiz.question_count || 0) > 0,
)

const statusClass = computed(() => {
  if (needsReview.value) return 'teacher-quiz-card__status--review'
  return props.quiz.is_published
    ? 'teacher-quiz-card__status--published'
    : 'teacher-quiz-card__status--draft'
})

const statusLabel = computed(() => {
  if (needsReview.value) return t('teacher.status.pendingReview')
  return props.quiz.is_published ? t('teacher.status.published') : t('teacher.status.draft')
})

const attemptText = computed(() => {
  const n = Number(props.quiz.attempt_count) || 0
  if (n === 0) return t('teacher.quizzes.noAttemptsBadge')
  if (n === 1) return t('teacher.quizzes.oneAttempt')
  return t('teacher.quizzes.nAttempts', { count: n })
})

const averageLabel = computed(() => {
  if (props.averageScore == null) return '—'
  return `${Math.round(props.averageScore)}%`
})
</script>
