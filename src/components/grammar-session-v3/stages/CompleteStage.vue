<template>
  <SessionStageContainer
    stage-id="complete"
    :eyebrow="t('student.grammarSession.stages.complete')"
    :title="t('student.grammarSession.complete.title')"
    :subtitle="t('student.grammarSession.complete.subtitle')"
  >
    <SessionContentCard :title="t('student.grammarSession.complete.topic')" >
      <p class="eng-island" dir="ltr">{{ lesson.grammar_target || lesson.lesson_title || '—' }}</p>
    </SessionContentCard>

    <SessionContentCard :title="t('student.grammarSession.complete.nextTitle')" :eng-island="false">
      <p>{{ t('student.grammarSession.complete.nextBody') }}</p>
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
.eng-island {
  unicode-bidi: isolate;
  margin: 0;
}

p {
  margin: 0;
}
</style>
