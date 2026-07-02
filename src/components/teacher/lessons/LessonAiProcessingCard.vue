<template>
  <section class="add-lesson-ai-card" aria-labelledby="add-lesson-ai-title">
    <h3 id="add-lesson-ai-title" class="add-lesson-ai-card__title">{{ $t('teacher.processing.aiCard') }}</h3>
    <ul class="add-lesson-ai-card__list">
      <li v-for="item in items" :key="item" class="add-lesson-ai-card__item">
        <v-icon size="15" class="add-lesson-ai-card__check">mdi-check</v-icon>
        <span>{{ item }}</span>
      </li>
    </ul>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

const items = computed(() => [
  t('teacher.processing.toText'),
  t('teacher.processing.summary'),
  t('teacher.processing.quiz'),
  t('teacher.processing.notes'),
  t('teacher.processing.flashcards'),
])
</script>
