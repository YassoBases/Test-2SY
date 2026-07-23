<template>
  <SessionStageContainer
    stage-id="learn"
    :eyebrow="t('student.grammarSession.stages.learn')"
    :title="t('student.grammarTeacher.learn.title')"
    :subtitle="t('student.grammarTeacher.learn.subtitle')"
  >
    <TeachingMicroCard
      v-if="currentTeachCard"
      :card="currentTeachCard"
      :index="teachCardIndex"
      :total="teachingCards.length"
      :is-last="allTeachCardsSeen"
      :teacher-name="teacherName"
      :voice-state="voiceState"
      @ask="$emit('ask')"
      @next-card="$emit('next-card')"
    />

    <p v-else class="learn__empty">
      {{ t('student.grammarSession.learn.empty') }}
    </p>
  </SessionStageContainer>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import SessionStageContainer from '../../ai-session/SessionStageContainer.vue'
import TeachingMicroCard from '../teacher/TeachingMicroCard.vue'

defineProps({
  lesson: { type: Object, required: true },
  teacherName: { type: String, default: 'Alex' },
  voiceState: { type: String, default: 'idle' },
  teachingCards: { type: Array, default: () => [] },
  teachCardIndex: { type: Number, default: 0 },
  currentTeachCard: { type: Object, default: null },
  allTeachCardsSeen: { type: Boolean, default: true },
})

defineEmits(['ask', 'next-card'])
const { t } = useI18n()
</script>

<style scoped>
.learn__empty {
  margin: 0;
  color: var(--text-muted, #3f4f63);
}
</style>
