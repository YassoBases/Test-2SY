<template>
  <aside class="teacher-quiz-class-context" :aria-label="$t('teacher.quizzes.currentClass')">
    <p class="teacher-quiz-class-context__eyebrow">{{ $t('teacher.quizzes.currentClass') }}</p>
    <div class="teacher-quiz-class-context__items">
      <div class="teacher-quiz-class-context__item">
        <v-icon size="18" class="teacher-quiz-class-context__icon">mdi-book-open-variant</v-icon>
        <div>
          <span class="teacher-quiz-class-context__label">{{ $t('teacher.labels.subject') }}</span>
          <span class="teacher-quiz-class-context__value">{{ subject }}</span>
        </div>
      </div>
      <div class="teacher-quiz-class-context__item">
        <v-icon size="18" class="teacher-quiz-class-context__icon">mdi-school-outline</v-icon>
        <div>
          <span class="teacher-quiz-class-context__label">{{ $t('teacher.labels.grade') }}</span>
          <span class="teacher-quiz-class-context__value">{{ gradeLabel }}</span>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()


const props = defineProps({
  subject: { type: String, default: '—' },
  grade: { type: [Number, String], default: '' },
})

const gradeLabel = computed(() => {
  if (props.grade === '' || props.grade == null) return '—'
  return t('teacher.labels.gradeNumber', { grade: props.grade })
})
</script>
