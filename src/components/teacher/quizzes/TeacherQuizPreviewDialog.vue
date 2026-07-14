<template>
  <v-dialog :model-value="open" max-width="560" @update:model-value="$emit('update:open', $event)">
    <v-card class="glass-card pa-5 rounded-lg" variant="flat">
      <div class="d-flex align-center justify-space-between gap-3 mb-4">
        <div>
          <h3 class="text-subtitle-1 font-weight-bold mb-1">{{ $t('teacher.quizzes.previewTitle') }}</h3>
          <p class="text-caption text-medium-emphasis mb-0">{{ $t('teacher.quizzes.previewSubtitle') }}</p>
        </div>
        <v-btn icon variant="text" :aria-label="$t('common.close')" @click="$emit('update:open', false)">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </div>

      <h4 class="text-body-1 font-weight-bold mb-2">{{ title }}</h4>
      <p v-if="description" class="text-body-2 text-medium-emphasis mb-3">{{ description }}</p>

      <div class="teacher-quiz-preview__meta">
        <span class="teacher-quiz-preview__chip">
          {{ durationLabel }}
        </span>
        <span class="teacher-quiz-preview__chip">{{ $t('teacher.quizzes.passingPercent', { percent: passingScore }) }}</span>
        <span class="teacher-quiz-preview__chip">{{ $t('teacher.labels.questionCount', { count: questions.length }) }}</span>
      </div>

      <div v-if="questions.length" class="teacher-quiz-preview__questions">
        <div v-for="(q, idx) in questions" :key="q.id || idx" class="teacher-quiz-preview__question">
          <p class="teacher-quiz-preview__question-head">
            {{ $t('teacher.quizzes.questionDetail', { n: idx + 1, type: typeLabel(q.question_type), points: q.points }) }}
          </p>
          <p class="teacher-quiz-preview__question-text">{{ q.question_text }}</p>
        </div>
      </div>
      <p v-else class="text-body-2 text-medium-emphasis text-center pa-6 mb-0">{{ $t('teacher.quizzes.noQuestionsPreview') }}</p>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps({
  open: { type: Boolean, default: false },
  title: { type: String, default: '' },
  description: { type: String, default: '' },
  durationMinutes: { type: [Number, String], default: null },
  passingScore: { type: [Number, String], default: 60 },
  questions: { type: Array, default: () => [] },
})

defineEmits(['update:open'])

const durationLabel = computed(() => {
  const n = Number(props.durationMinutes)
  if (Number.isFinite(n) && n >= 1) return t('teacher.labels.minutesCount', { count: n })
  return t('teacher.status.noLimit')
})

function typeLabel(questionType) {
  const key = `teacher.quizzes.types.${questionType}`
  const label = t(key)
  return label !== key ? label : questionType
}
</script>