<template>
  <SessionStageContainer
    stage-id="welcome"
    :eyebrow="t('student.grammarSession.stages.welcome')"
    :title="t('student.grammarTeacher.welcome.title')"
    :subtitle="t('student.grammarTeacher.welcome.subtitle')"
  >
    <TeacherMessage :name="teacherName" :voice-state="voiceState">
      <p>{{ greeting }}</p>
    </TeacherMessage>

    <SessionContentCard :title="t('student.grammarTeacher.welcome.whySelected')" :eng-island="false">
      <p>
        {{
          t('student.grammarTeacher.welcome.whySelectedBody', {
            topic: lesson.grammar_target || lesson.lesson_title || '—',
          })
        }}
      </p>
    </SessionContentCard>

    <SessionContentCard :title="t('student.grammarTeacher.welcome.achieve')" :eng-island="false">
      <p class="eng-island" dir="ltr">
        {{ lesson.lesson_goal || t('student.grammarSession.mission.fallbackGoal') }}
      </p>
    </SessionContentCard>

    <ul v-if="skills.length" class="welcome__skills">
      <li v-for="skill in skills" :key="skill" class="eng-island" dir="ltr">{{ skill }}</li>
    </ul>

    <div class="welcome__ask">
      <AppButton variant="secondary" prepend-icon="mdi-chat-question-outline" @click="$emit('ask')">
        {{ t('student.grammarTeacher.ask.cta') }}
      </AppButton>
    </div>
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
  skills: { type: Array, default: () => [] },
  teacherName: { type: String, default: 'Alex' },
  teacherMessage: { type: String, default: '' },
  voiceState: { type: String, default: 'idle' },
})

defineEmits(['ask'])
const { t } = useI18n()

const greeting = computed(
  () =>
    props.teacherMessage ||
    t('student.grammarTeacher.welcome.fallback', {
      topic: props.lesson.grammar_target || props.lesson.lesson_title || 'grammar',
    }),
)
</script>

<style scoped>
.welcome__skills {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  list-style: none;
  margin: 0;
  padding: 0;
}

.welcome__skills li {
  padding: 8px 14px;
  border-radius: 12px;
  background: rgba(59, 130, 246, 0.12);
  font-size: 0.875rem;
}

.welcome__ask {
  margin-block-start: 4px;
}

.eng-island {
  unicode-bidi: isolate;
  margin: 0;
}

p {
  margin: 0;
}
</style>
