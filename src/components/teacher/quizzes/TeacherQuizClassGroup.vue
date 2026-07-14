<template>
  <section class="teacher-quiz-group" :aria-labelledby="headingId">
    <header class="teacher-quiz-group__head">
      <div class="teacher-quiz-group__head-text">
        <h2 :id="headingId" class="teacher-quiz-group__grade">{{ $t('teacher.labels.gradeNumber', { grade }) }}</h2>
        <p class="teacher-quiz-group__subject">{{ subject }}</p>
      </div>
      <span class="teacher-quiz-group__count">{{ countLabel }}</span>
    </header>

    <div v-if="quizzes.length" class="teacher-quiz-group__grid">
      <TeacherQuizWorkspaceCard
        v-for="item in quizzes"
        :key="item.quiz.id"
        :quiz="item.quiz"
        :course-id="courseId"
        :average-score="item.averageScore"
        @delete="$emit('delete', item)"
      />
    </div>

    <div v-else class="teacher-quiz-group__empty">
      <p class="teacher-quiz-group__empty-text">{{ $t('teacher.quizzes.noQuizzesForClass') }}</p>
      <v-btn size="small" variant="tonal" rounded="lg" @click="$emit('create')">
        <v-icon start size="16">mdi-plus</v-icon>
        {{ $t('teacher.actions.createQuiz') }}
      </v-btn>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import TeacherQuizWorkspaceCard from './TeacherQuizWorkspaceCard.vue'

const props = defineProps({
  courseId: { type: [Number, String], required: true },
  grade: { type: [Number, String], required: true },
  subject: { type: String, required: true },
  quizzes: { type: Array, default: () => [] },
  totalCount: { type: Number, default: null },
})

defineEmits(['delete', 'create'])

const headingId = computed(() => `quiz-group-${props.courseId}`)

const countLabel = computed(() => {
  const n = props.totalCount ?? props.quizzes.length
  if (n === 0) return t('teacher.quizzes.zeroQuizzes')
  if (n === 1) return t('teacher.quizzes.oneQuiz')
  if (n === 2) return t('teacher.quizzes.twoQuizzes')
  return t('teacher.quizzes.nQuizzes', { count: n })
})
</script>
