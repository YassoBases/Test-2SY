<template>
  <SessionStageContainer
    stage-id="writing"
    :eyebrow="t('student.grammarSession.stages.writing')"
    :title="t('student.grammarSession.writing.title')"
    :subtitle="t('student.grammarSession.writing.subtitle')"
  >
    <SessionContentCard :title="t('student.grammarSession.writing.readyTitle')" :eng-island="false">
      <p>{{ t('student.grammarSession.writing.readyBody') }}</p>
    </SessionContentCard>
    <p class="write-ready__hint">{{ t('student.grammarSession.writing.hint') }}</p>
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
.write-ready__hint {
  margin: 0;
  font-size: 0.875rem;
  color: var(--text-muted, #3f4f63);
}

p {
  margin: 0;
}
</style>
