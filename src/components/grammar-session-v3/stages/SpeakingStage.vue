<template>
  <SessionStageContainer
    stage-id="speaking"
    :eyebrow="t('student.grammarSession.stages.speaking')"
    :title="t('student.grammarSession.speaking.title')"
    :subtitle="t('student.grammarSession.speaking.subtitle')"
  >
    <div class="speak-ready">
      <EmptyTeacherPlaceholder voice-state="idle" size="lg" show-mic />
      <SessionContentCard :title="t('student.grammarSession.speaking.readyTitle')" :eng-island="false">
        <p>{{ t('student.grammarSession.speaking.readyBody') }}</p>
      </SessionContentCard>
    </div>
    <p class="speak-ready__hint">{{ t('student.grammarSession.speaking.hint') }}</p>
  </SessionStageContainer>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import SessionStageContainer from '../../ai-session/SessionStageContainer.vue'
import SessionContentCard from '../../ai-session/SessionContentCard.vue'
import EmptyTeacherPlaceholder from '../../ai-session/EmptyTeacherPlaceholder.vue'

defineProps({
  lesson: { type: Object, required: true },
})

const { t } = useI18n()
</script>

<style scoped>
.speak-ready {
  display: flex;
  flex-direction: column;
  gap: 16px;
  align-items: flex-start;
}

.speak-ready__hint {
  margin: 0;
  font-size: 0.875rem;
  color: var(--text-muted, #3f4f63);
}

p {
  margin: 0;
}
</style>
