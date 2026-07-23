<template>
  <SessionStageContainer
    stage-id="practice"
    :eyebrow="t('student.grammarSession.stages.practice')"
    :title="t('student.grammarSession.practice.title')"
    :subtitle="t('student.grammarSession.practice.subtitle')"
  >
    <TeacherMessage
      v-if="teacherMessage"
      :name="teacherName"
      :voice-state="voiceState"
      compact
    >
      <p>{{ teacherMessage }}</p>
    </TeacherMessage>

    <SessionContentCard
      v-if="lesson.main_activity"
      :title="t('student.grammarV2.lesson.mainActivity')"
    >
      <p>{{ lesson.main_activity }}</p>
    </SessionContentCard>

    <SessionContentCard
      v-if="lesson.follow_up_questions?.length"
      :title="t('student.grammarV2.lesson.followUp')"
    >
      <ol class="practice__list eng-island" dir="ltr">
        <li v-for="(q, i) in lesson.follow_up_questions" :key="i">{{ q }}</li>
      </ol>
    </SessionContentCard>

    <SessionContentCard
      v-if="lesson.teacher_hints?.length"
      :title="t('student.grammarV2.lesson.hints')"
    >
      <ul class="practice__list">
        <li v-for="(h, i) in lesson.teacher_hints" :key="i">{{ h }}</li>
      </ul>
    </SessionContentCard>

    <p v-if="!hasContent" class="practice__empty">
      {{ t('student.grammarSession.practice.empty') }}
    </p>

    <AppButton variant="secondary" prepend-icon="mdi-chat-question-outline" @click="$emit('ask')">
      {{ t('student.grammarTeacher.ask.cta') }}
    </AppButton>
  </SessionStageContainer>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import SessionStageContainer from '../../ai-session/SessionStageContainer.vue'
import SessionContentCard from '../../ai-session/SessionContentCard.vue'
import TeacherMessage from '../teacher/TeacherMessage.vue'
import AppButton from '../../ui/AppButton.vue'

const props = defineProps({
  lesson: { type: Object, required: true },
  teacherName: { type: String, default: 'Alex' },
  teacherMessage: { type: String, default: '' },
  voiceState: { type: String, default: 'idle' },
})

defineEmits(['ask'])
const { t } = useI18n()

const hasContent = computed(() => {
  const L = props.lesson || {}
  return !!(L.main_activity || L.follow_up_questions?.length || L.teacher_hints?.length)
})
</script>

<style scoped>
.practice__list {
  margin: 0;
  padding-inline-start: 1.25rem;
}

.practice__empty {
  margin: 0;
  color: var(--text-muted, #3f4f63);
}

.eng-island {
  unicode-bidi: isolate;
}

p {
  margin: 0;
}
</style>
