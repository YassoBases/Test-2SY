<template>
  <div id="quiz-form-workspace" class="teacher-quiz-form">
    <!-- Section 1: Quiz info -->
    <section class="teacher-quiz-form__card" aria-labelledby="quiz-form-info-title">
      <header class="teacher-quiz-form__card-head">
        <h2 id="quiz-form-info-title" class="teacher-quiz-form__card-title">{{ $t('teacher.quizzes.quizInfo') }}</h2>
        <p class="teacher-quiz-form__card-sub">{{ $t('teacher.quizzes.quizInfoHint') }}</p>
      </header>

      <div class="teacher-quiz-form__fields">
        <div class="teacher-quiz-form__field">
          <label class="teacher-quiz-form__label" for="quiz-form-title">
            {{ $t('teacher.labels.quizTitle') }}
            <span class="teacher-quiz-form__required">*</span>
          </label>
          <p class="teacher-quiz-form__helper">{{ $t('teacher.quizzes.titleHint') }}</p>
          <v-text-field
            id="quiz-form-title"
            :model-value="title"
            :placeholder="$t('teacher.quizzes.titleExample')"
            variant="outlined"
            density="comfortable"
            hide-details="auto"
            class="teacher-quiz-form__input"
            @update:model-value="$emit('update:title', $event)"
          />
        </div>

        <div class="teacher-quiz-form__field">
          <label class="teacher-quiz-form__label" for="quiz-form-description">{{ $t('teacher.labels.quizDescription') }}</label>
          <p class="teacher-quiz-form__helper">{{ $t('teacher.quizzes.descOptional') }}</p>
          <v-textarea
            id="quiz-form-description"
            :model-value="description"
            :placeholder="$t('teacher.quizzes.descPrompt')"
            rows="3"
            auto-grow
            variant="outlined"
            density="comfortable"
            hide-details
            class="teacher-quiz-form__input"
            @update:model-value="$emit('update:description', $event)"
          />
        </div>
      </div>
    </section>

    <!-- Section 2: Test settings -->
    <section class="teacher-quiz-form__card" aria-labelledby="quiz-form-exam-title">
      <header class="teacher-quiz-form__card-head">
        <h2 id="quiz-form-exam-title" class="teacher-quiz-form__card-title">{{ $t('teacher.quizzes.testSettings') }}</h2>
        <p class="teacher-quiz-form__card-sub">{{ $t('teacher.quizzes.testSettingsHint') }}</p>
      </header>

      <div class="teacher-quiz-form__fields teacher-quiz-form__fields--grid">
        <div class="teacher-quiz-form__field">
          <label class="teacher-quiz-form__label" for="quiz-form-duration">{{ $t('teacher.labels.testDuration') }}</label>
          <p class="teacher-quiz-form__helper">{{ $t('teacher.quizzes.durationOptional') }}</p>
          <v-text-field
            id="quiz-form-duration"
            :model-value="durationMinutes"
            type="number"
            min="1"
            :placeholder="$t('teacher.status.unlimited')"
            variant="outlined"
            density="comfortable"
            hide-details
            clearable
            class="teacher-quiz-form__input"
            @update:model-value="$emit('update:durationMinutes', $event)"
          />
        </div>

        <div class="teacher-quiz-form__field">
          <label class="teacher-quiz-form__label" for="quiz-form-passing">
            {{ $t('teacher.labels.passingScore') }}
            <span class="teacher-quiz-form__required">*</span>
          </label>
          <p class="teacher-quiz-form__helper">{{ $t('teacher.quizzes.passingHint') }}</p>
          <v-text-field
            id="quiz-form-passing"
            :model-value="passingScore"
            type="number"
            min="0"
            max="100"
            suffix="%"
            variant="outlined"
            density="comfortable"
            hide-details
            class="teacher-quiz-form__input"
            @update:model-value="$emit('update:passingScore', $event)"
          />
        </div>

        <div class="teacher-quiz-form__field">
          <span class="teacher-quiz-form__label">{{ $t('teacher.labels.allowedAttempts') }}</span>
          <p class="teacher-quiz-form__helper">{{ $t('teacher.quizzes.attemptsFixed') }}</p>
          <div class="teacher-quiz-form__readonly">{{ $t('teacher.quizzes.oneAttemptPerStudent') }}</div>
        </div>

        <div class="teacher-quiz-form__field">
          <label class="teacher-quiz-form__label" for="quiz-form-due">{{ $t('teacher.labels.deadline') }}</label>
          <p class="teacher-quiz-form__helper">{{ $t('teacher.quizzes.deadlineOptional') }}</p>
          <v-text-field
            id="quiz-form-due"
            :model-value="dueAtLocal"
            type="datetime-local"
            variant="outlined"
            density="comfortable"
            :min="dueAtMin"
            :error-messages="dueAtError ? [dueAtError] : []"
            clearable
            hide-details="auto"
            class="teacher-quiz-form__input"
            @update:model-value="$emit('update:dueAtLocal', $event)"
          />
        </div>
      </div>
    </section>

    <!-- Section 3: Publishing -->
    <section class="teacher-quiz-form__card" aria-labelledby="quiz-form-publish-title">
      <header class="teacher-quiz-form__card-head">
        <h2 id="quiz-form-publish-title" class="teacher-quiz-form__card-title">{{ $t('teacher.quizzes.publishSection') }}</h2>
        <p class="teacher-quiz-form__card-sub">{{ $t('teacher.quizzes.publishHint') }}</p>
      </header>

      <div class="teacher-quiz-form__publish-options" role="radiogroup" :aria-label="$t('teacher.labels.publishStatus')">
        <button
          type="button"
          class="teacher-quiz-form__publish-option"
          :class="{ 'teacher-quiz-form__publish-option--active': !isPublished }"
          role="radio"
          :aria-checked="!isPublished"
          @click="$emit('update:isPublished', false)"
        >
          <v-icon size="20" class="teacher-quiz-form__publish-icon">mdi-file-document-edit-outline</v-icon>
          <span class="teacher-quiz-form__publish-label">{{ $t('teacher.status.draft') }}</span>
          <span class="teacher-quiz-form__publish-desc">{{ $t('teacher.quizzes.draftHidden') }}</span>
        </button>
        <button
          type="button"
          class="teacher-quiz-form__publish-option"
          :class="{ 'teacher-quiz-form__publish-option--active': isPublished }"
          role="radio"
          :aria-checked="isPublished"
          @click="$emit('update:isPublished', true)"
        >
          <v-icon size="20" class="teacher-quiz-form__publish-icon">mdi-send-check-outline</v-icon>
          <span class="teacher-quiz-form__publish-label">{{ $t('teacher.status.published') }}</span>
          <span class="teacher-quiz-form__publish-desc">{{ $t('teacher.quizzes.publishedVisible') }}</span>
        </button>
      </div>
    </section>

    <div class="teacher-quiz-form__actions">
      <v-btn color="primary" class="btn-glow" size="large" rounded="lg" :loading="saving" @click="$emit('save')">
        {{ $t('teacher.actions.saveQuiz') }}
        <v-icon end>mdi-content-save-outline</v-icon>
      </v-btn>
      <p v-if="totalPoints > 0" class="teacher-quiz-form__points-note">
        {{ $t('teacher.labels.totalPoints') }} <strong dir="ltr">{{ totalPoints }}</strong>
      </p>
    </div>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

defineProps({
  title: { type: String, default: '' },
  description: { type: String, default: '' },
  durationMinutes: { type: [Number, String], default: null },
  passingScore: { type: [Number, String], default: 60 },
  dueAtLocal: { type: String, default: '' },
  dueAtMin: { type: String, default: '' },
  dueAtError: { type: String, default: '' },
  isPublished: { type: Boolean, default: false },
  totalPoints: { type: Number, default: 0 },
  saving: { type: Boolean, default: false },
})

defineEmits([
  'save',
  'update:title',
  'update:description',
  'update:durationMinutes',
  'update:passingScore',
  'update:dueAtLocal',
  'update:isPublished',
])
</script>
