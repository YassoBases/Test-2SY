<template>
  <SessionStageContainer
    stage-id="mission"
    :eyebrow="t('student.grammarSession.stages.mission')"
    :title="t('student.grammarTeacher.mission.title')"
    :subtitle="t('student.grammarTeacher.mission.subtitle')"
  >
    <TeacherMessage :name="teacherName" :voice-state="voiceState">
      <p>{{ missionLine }}</p>
    </TeacherMessage>

    <SessionContentCard :title="t('student.grammarTeacher.mission.whereUsed')" :eng-island="false">
      <p>{{ t('student.grammarTeacher.mission.whereUsedBody') }}</p>
    </SessionContentCard>

    <SessionContentCard :title="t('student.grammarTeacher.mission.whyUseful')" :eng-island="false">
      <p>{{ t('student.grammarTeacher.mission.whyUsefulBody') }}</p>
    </SessionContentCard>

    <SessionContentCard
      v-if="lesson.expected_patterns?.length"
      :title="t('student.grammarSession.mission.successCriteria')"
    >
      <ul class="mission__list eng-island" dir="ltr">
        <li v-for="(p, i) in lesson.expected_patterns" :key="i">{{ p }}</li>
      </ul>
    </SessionContentCard>

    <SessionContentCard :title="t('student.grammarSession.mission.outcome')" :eng-island="false">
      <p>{{ t('student.grammarSession.mission.outcomeBody') }}</p>
    </SessionContentCard>

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

const missionLine = computed(() => {
  if (props.teacherMessage) return props.teacherMessage
  const goal = props.lesson.lesson_goal
  if (goal) return t('student.grammarTeacher.mission.lead', { goal })
  return t('student.grammarTeacher.mission.leadFallback', {
    topic: props.lesson.grammar_target || 'today’s grammar',
  })
})
</script>

<style scoped>
.mission__list {
  margin: 0;
  padding-inline-start: 1.25rem;
}

.eng-island {
  unicode-bidi: isolate;
}

p {
  margin: 0;
}
</style>
