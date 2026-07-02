<template>
  <TeacherWorkspaceShell mode="fullscreen">
    <template #header>
      <TeacherHero
        class="tds-workspace-shell__hero"
        variant="compact"
        :eyebrow="displayQuizTitle"
        :title="editorTitle"
      />
    </template>

    <template #header-actions>
      <TeacherButton variant="ghost" @click="$emit('close')">
        <v-icon start size="18">mdi-close</v-icon>
        {{ $t('common.close') }}
      </TeacherButton>
    </template>

    <v-alert
      v-if="questionFormError"
      type="error"
      variant="tonal"
      density="comfortable"
      class="rounded-lg"
    >
      {{ questionFormError }}
    </v-alert>

    <TeacherForm lesson>
      <TeacherFormSection variant="lesson" stack :title="$t('teacher.quizzes.questionInfo')">
        <TeacherFormField mode="plain" :label="$t('teacher.labels.questionType')">
          <div class="tds-type-grid" role="radiogroup" :aria-label="$t('teacher.labels.questionType')">
            <button
              v-for="qt in QUESTION_TYPES"
              :key="qt.value"
              type="button"
              class="tds-type-tile"
              :class="{ 'tds-type-tile--active': questionForm.question_type === qt.value }"
              :disabled="!!editingQuestionId"
              role="radio"
              :aria-checked="questionForm.question_type === qt.value"
              @click="$emit('set-question-type', qt.value)"
            >
              <v-icon :icon="questionTypeIcon(qt.value)" size="22" class="mb-2" />
              <span class="tds-type-tile__label">{{ $t(`teacher.quizzes.types.${qt.value}`) }}</span>
            </button>
          </div>
        </TeacherFormField>

        <TeacherFormField mode="plain" :label="$t('teacher.labels.questionText')">
          <v-textarea
            v-model="questionForm.question_text"
            :placeholder="$t('teacher.quizzes.questionPlaceholder')"
            rows="4"
            variant="outlined"
            density="comfortable"
            auto-grow
            hide-details
          />
        </TeacherFormField>

        <TeacherFormField mode="plain" :label="$t('teacher.labels.points')">
          <v-text-field
            v-model.number="questionForm.points"
            type="number"
            min="1"
            placeholder="1"
            variant="outlined"
            density="comfortable"
            hide-details
          />
        </TeacherFormField>
      </TeacherFormSection>

      <TeacherFormSection
        v-if="questionForm.question_type === 'multiple_choice'"
        key="multiple_choice"
        variant="lesson"
        stack
        :title="$t('teacher.quizzes.answerOptions')"
        :description="$t('teacher.quizzes.optionsHint')"
      >
        <TeacherFormField
          v-for="(opt, i) in questionForm.options"
          :key="`opt-${i}`"
          mode="plain"
          :label="$t('teacher.labels.optionNumber', { n: i + 1 })"
        >
          <v-text-field
            v-model="questionForm.options[i]"
            :placeholder="$t('teacher.labels.optionTextNumber', { n: i + 1 })"
            variant="outlined"
            density="comfortable"
            hide-details
          />
        </TeacherFormField>

        <TeacherButton variant="tonal" size="small" @click="questionForm.options.push('')">
          <v-icon start size="16">mdi-plus</v-icon>
          {{ $t('teacher.actions.addOption') }}
        </TeacherButton>

        <TeacherFormField mode="plain" :label="$t('teacher.labels.correctAnswer')">
          <v-select
            v-model="questionForm.correct_index"
            :items="correctAnswerItems"
            item-title="title"
            item-value="value"
            variant="outlined"
            density="comfortable"
            hide-details
            :menu-props="editorMenuProps"
          />
        </TeacherFormField>
      </TeacherFormSection>

      <TeacherFormSection
        v-else-if="questionForm.question_type === 'true_false'"
        key="true_false"
        variant="lesson"
        :title="$t('teacher.labels.correctAnswer')"
      >
        <v-radio-group v-model="questionForm.correct_bool" inline hide-details>
          <v-radio :label="$t('teacher.labels.trueLabel')" :value="true" />
          <v-radio :label="$t('teacher.status.error')" :value="false" />
        </v-radio-group>
      </TeacherFormSection>

      <TeacherFormSection
        v-else-if="questionForm.question_type === 'short_answer'"
        key="short_answer"
        variant="lesson"
        stack
        :title="$t('teacher.labels.modelAnswer')"
        :description="$t('teacher.quizzes.modelAnswerHint')"
      >
        <TeacherFormField mode="plain" :label="$t('teacher.labels.modelAnswer')">
          <v-text-field
            v-model="questionForm.correct_text"
            :placeholder="$t('teacher.quizzes.modelAnswerPlaceholder')"
            variant="outlined"
            density="comfortable"
            hide-details
          />
        </TeacherFormField>
      </TeacherFormSection>

      <TeacherFormSection
        v-else-if="questionForm.question_type === 'essay'"
        key="essay"
        variant="lesson"
        :title="$t('teacher.quizzes.essayQuestion')"
      >
        <TeacherFormHint variant="info">
          {{ $t('teacher.quizzes.essayHint') }}
        </TeacherFormHint>
      </TeacherFormSection>
    </TeacherForm>

    <template #footer>
      <TeacherButtonGroup align="end">
        <TeacherButton variant="secondary" @click="$emit('close')">
          {{ $t('common.cancel') }}
        </TeacherButton>
        <TeacherButton variant="primary" :loading="savingQuestion" @click="$emit('save')">
          {{ editingQuestionId ? $t('teacher.actions.saveQuestion') : $t('teacher.actions.addQuestionBtn') }}
        </TeacherButton>
      </TeacherButtonGroup>
    </template>
  </TeacherWorkspaceShell>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import { QUESTION_TYPES } from '../../../api/manualQuizzes.js'
import {
  TeacherWorkspaceShell,
  TeacherHero,
  TeacherForm,
  TeacherFormSection,
  TeacherFormField,
  TeacherFormHint,
  TeacherButton,
  TeacherButtonGroup,
} from '../design-system/index.js'

const props = defineProps({
  quizTitle: { type: String, default: '' },
  editingQuestionId: { type: [Number, String], default: null },
  questionForm: { type: Object, required: true },
  questionFormError: { type: String, default: '' },
  savingQuestion: { type: Boolean, default: false },
  correctAnswerItems: { type: Array, default: () => [] },
  editorMenuProps: { type: Object, default: () => ({}) },
})

defineEmits(['close', 'save', 'set-question-type'])

const displayQuizTitle = computed(() => props.quizTitle || t('teacher.quizzes.newQuiz'))

const editorTitle = computed(() =>
  props.editingQuestionId ? t('teacher.quizzes.editQuestion') : t('teacher.quizzes.addNewQuestion'),
)

function questionTypeIcon(type) {
  const icons = {
    multiple_choice: 'mdi-format-list-bulleted',
    true_false: 'mdi-help-circle-outline',
    short_answer: 'mdi-text-short',
    essay: 'mdi-text-long',
  }
  return icons[type] || 'mdi-help-circle-outline'
}
</script>
