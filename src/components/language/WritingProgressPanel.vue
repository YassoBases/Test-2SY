<template>
  <v-card class="completion-card pa-8 mb-4" variant="flat">
    <div class="text-center mb-6">
      <v-icon color="success" size="56" class="mb-4">mdi-check-decagram</v-icon>
      <h3 class="text-h5 font-weight-bold mb-2">{{ t('student.languages.writingJourney.completion.title') }}</h3>
      <p v-if="progress?.journey_update" class="text-body-1 text-medium-emphasis mb-0">{{ progress.journey_update }}</p>
    </div>

    <div v-if="progress" class="feedback-sections mb-6">
      <div v-if="progress.what_you_did_well?.length" class="feedback-block">
        <div class="text-body-2 font-weight-bold mb-2">{{ t('student.languages.writingJourney.feedback.didWell') }}</div>
        <div v-for="(line, idx) in progress.what_you_did_well" :key="`w-${idx}`" class="d-flex gap-2 py-1">
          <v-icon color="success" size="18">mdi-check</v-icon>
          <span class="text-body-2" dir="ltr">{{ line }}</span>
        </div>
      </div>

      <div v-if="progress.mistakes_made?.length" class="feedback-block">
        <div class="text-body-2 font-weight-bold mb-2">{{ t('student.languages.writingJourney.feedback.mistakes') }}</div>
        <div v-for="(line, idx) in progress.mistakes_made" :key="`m-${idx}`" class="text-body-2 py-1" dir="ltr">{{ line }}</div>
      </div>

      <div v-if="progress.why_mistakes_happened?.length" class="feedback-block">
        <div class="text-body-2 font-weight-bold mb-2">{{ t('student.languages.writingJourney.feedback.why') }}</div>
        <div v-for="(line, idx) in progress.why_mistakes_happened" :key="`y-${idx}`" class="text-body-2 py-1" dir="ltr">{{ line }}</div>
      </div>

      <div v-if="progress.improve_next?.length" class="feedback-block">
        <div class="text-body-2 font-weight-bold mb-2">{{ t('student.languages.writingJourney.feedback.improveNext') }}</div>
        <div v-for="(line, idx) in progress.improve_next" :key="`i-${idx}`" class="text-body-2 py-1" dir="ltr">{{ line }}</div>
      </div>

      <div v-if="progress.history_comparison?.length" class="feedback-block">
        <div class="text-body-2 font-weight-bold mb-2">{{ t('student.languages.writingJourney.feedback.history') }}</div>
        <div v-for="(line, idx) in progress.history_comparison" :key="`h-${idx}`" class="text-body-2 py-1" dir="ltr">{{ line }}</div>
      </div>

      <div class="feedback-block">
        <div class="text-body-2 font-weight-bold mb-1">{{ t('student.languages.writingJourney.progress.stage') }}</div>
        <div class="text-body-1 font-weight-medium">{{ progress.writing_stage_label }}</div>
      </div>

      <div v-if="progress.progress_change" class="feedback-block">
        <div class="text-body-2 font-weight-bold mb-1">{{ t('student.languages.writingJourney.feedback.progressChange') }}</div>
        <div class="text-body-2" dir="ltr">{{ progress.progress_change }}</div>
      </div>

      <div v-if="progress.stage_proximity" class="feedback-block">
        <div class="text-body-2 font-weight-bold mb-1">{{ t('student.languages.writingJourney.feedback.stageProximity') }}</div>
        <div class="text-body-2" dir="ltr">{{ progress.stage_proximity }}</div>
      </div>

      <div v-if="progress.estimated_lessons_remaining" class="feedback-block">
        <div class="text-body-2 font-weight-bold mb-1">{{ t('student.languages.writingJourney.feedback.estimated') }}</div>
        <div class="text-body-2" dir="ltr">{{ progress.estimated_lessons_remaining }}</div>
      </div>
    </div>

    <div v-if="nextLesson" class="recommendation-block text-body-2 mb-6" dir="ltr">{{ nextLesson }}</div>

    <div class="text-center">
      <v-btn color="secondary" variant="flat" size="large" prepend-icon="mdi-pencil-plus" @click="$emit('new-lesson')">
        {{ t('student.languages.writingJourney.completion.newLesson') }}
      </v-btn>
    </div>
  </v-card>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

defineProps({
  progress: { type: Object, default: null },
  nextLesson: { type: String, default: '' },
})

defineEmits(['new-lesson'])

const { t } = useI18n()
</script>

<style scoped>
.completion-card {
  border-radius: 20px;
  background: linear-gradient(
    145deg,
    rgba(var(--v-theme-success), 0.1),
    rgba(var(--v-theme-surface), 0.95)
  );
}
.feedback-sections {
  display: grid;
  gap: 1rem;
}
.feedback-block {
  padding: 0.85rem 1rem;
  border-radius: 12px;
  background: rgba(var(--v-theme-on-surface), 0.04);
}
.recommendation-block {
  padding: 0.85rem 1rem;
  border-radius: 12px;
  background: rgba(var(--v-theme-secondary), 0.08);
  text-align: center;
}
</style>
