<template>
  <div class="teacher-quiz-kpi" :aria-label="$t('teacher.quizzes.statsStrip')">
    <div v-for="item in items" :key="item.key" class="teacher-quiz-kpi__card">
      <p class="teacher-quiz-kpi__value" dir="ltr">{{ item.value }}</p>
      <p class="teacher-quiz-kpi__label">{{ item.label }}</p>
    </div>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

defineProps({
  items: { type: Array, default: () => [] },
})
</script>
