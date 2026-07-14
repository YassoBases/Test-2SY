<template>
  <v-card class="completion-card pa-8 text-center mb-4" variant="flat">
    <v-icon color="success" size="56" class="mb-4">mdi-check-decagram</v-icon>
    <h3 class="text-h5 font-weight-bold mb-2">{{ t('student.languages.writingJourney.completion.title') }}</h3>
    <p class="text-body-1 text-medium-emphasis mb-6">{{ t('student.languages.writingJourney.completion.body') }}</p>
    <div v-if="nextLesson" class="text-body-2 mb-6" dir="ltr">{{ nextLesson }}</div>
    <v-btn color="secondary" variant="flat" size="large" prepend-icon="mdi-pencil-plus" @click="$emit('new-lesson')">
      {{ t('student.languages.writingJourney.completion.newLesson') }}
    </v-btn>
  </v-card>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

defineProps({
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
</style>
