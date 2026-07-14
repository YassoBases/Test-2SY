<template>
  <article class="teacher-quiz-question-card">
    <div class="teacher-quiz-question-card__menu">
      <v-menu location="bottom end" transition="lesson-menu-transition" :close-on-content-click="true">
        <template #activator="{ props: menuProps }">
          <v-btn
            v-bind="menuProps"
            icon
            variant="text"
            size="x-small"
            class="teacher-quiz-question-card__menu-btn"
            :aria-label="$t('teacher.quizzes.questionActions')"
          >
            <v-icon size="16">mdi-dots-vertical</v-icon>
          </v-btn>
        </template>
        <v-list class="lesson-workspace-menu" density="compact" nav>
          <v-list-item prepend-icon="mdi-open-in-new" :title="$t('teacher.actions.open')" @click="$emit('open')" />
          <v-list-item prepend-icon="mdi-pencil-outline" :title="$t('common.edit')" @click="$emit('edit')" />
          <v-list-item
            prepend-icon="mdi-delete-outline"
            :title="$t('common.delete')"
            base-color="error"
            @click="$emit('delete')"
          />
        </v-list>
      </v-menu>
    </div>

    <div class="teacher-quiz-question-card__main">
      <p class="teacher-quiz-question-card__index">{{ $t('teacher.quizzes.questionIndex', { index }) }}</p>
      <h3 class="teacher-quiz-question-card__title">{{ question.question_text }}</h3>

      <div class="teacher-quiz-question-card__meta">
        <span class="teacher-quiz-question-card__meta-item">
          <v-icon size="12">mdi-format-list-bulleted-type</v-icon>
          {{ typeLabel }}
        </span>
        <span class="teacher-quiz-question-card__meta-item">
          <v-icon size="12">mdi-star-outline</v-icon>
          {{ $t('teacher.labels.pointsCount', { count: question.points }) }}
        </span>
        <span v-if="choicesCount != null" class="teacher-quiz-question-card__meta-item">
          <v-icon size="12">mdi-checkbox-multiple-marked-outline</v-icon>
          {{ $t('teacher.labels.choicesCount', { count: choicesCount }) }}
        </span>
        <span v-if="question.requires_manual_grading" class="teacher-quiz-question-card__meta-item">
          <v-icon size="12">mdi-account-edit-outline</v-icon>
          {{ $t('teacher.quizzes.manualGrading') }}
        </span>
      </div>

      <p v-if="previewSnippet" class="teacher-quiz-question-card__preview">{{ previewSnippet }}</p>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

const props = defineProps({
  question: { type: Object, required: true },
  index: { type: Number, required: true },
})

defineEmits(['open', 'edit', 'delete'])

const typeLabel = computed(() => {
  const type = props.question.question_type
  const key = `teacher.quizzes.types.${type}`
  const label = t(key)
  return label !== key ? label : type
})

const choicesCount = computed(() => {
  if (props.question.question_type === 'multiple_choice') {
    return (props.question.options || []).filter((o) => String(o || '').trim()).length
  }
  if (props.question.question_type === 'true_false') return 2
  return null
})

const previewSnippet = computed(() => {
  const text = String(props.question.question_text || '').trim()
  if (!text || text.length <= 90) return ''
  return `${text.slice(0, 90)}…`
})
</script>
