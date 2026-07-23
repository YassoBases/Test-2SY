<template>
  <SessionStageContainer
    stage-id="reflection"
    :eyebrow="t('student.grammarSession.stages.reflection')"
    :title="t('student.grammarSession.reflection.title')"
    :subtitle="t('student.grammarSession.reflection.subtitle')"
  >
    <SessionContentCard
      v-if="lesson.completion_message"
      :title="t('student.grammarV2.lesson.reflection')"
    >
      <p>{{ lesson.completion_message }}</p>
    </SessionContentCard>

    <SessionContentCard :title="t('student.grammarSession.reflection.summaryTitle')" :eng-island="false">
      <p>{{ t('student.grammarSession.reflection.summaryBody') }}</p>
    </SessionContentCard>
  </SessionStageContainer>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import SessionStageContainer from '../../ai-session/SessionStageContainer.vue'
import SessionContentCard from '../../ai-session/SessionContentCard.vue'

defineProps({
  lesson: { type: Object, required: true },
})

const { t } = useI18n()
</script>

<style scoped>
p {
  margin: 0;
}
</style>
