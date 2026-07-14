<template>
  <v-card class="glass-card pa-6 text-center" variant="flat">
    <v-icon size="56" color="success" class="mb-3">mdi-party-popper</v-icon>
    <div class="text-h5 font-weight-bold mb-2">{{ t('student.languages.coach.success.title') }}</div>
    <p class="text-body-2 text-medium-emphasis mb-4">{{ result.summary }}</p>

    <div class="level-shift d-flex align-center justify-center gap-3 mb-4">
      <v-chip size="large" variant="tonal">{{ result.old_cefr }}</v-chip>
      <v-icon color="success">mdi-arrow-right</v-icon>
      <v-chip size="large" color="success" variant="flat">{{ result.new_cefr }}</v-chip>
    </div>

    <LearningCoachCard
      v-if="result.level_benefits?.length || stageSummary"
      :eyebrow="t('student.languages.coach.success.eyebrow')"
      :headline="t('student.languages.coach.success.changesTitle')"
      :bullets="result.level_benefits || []"
      :summary="stageSummary"
      :next-step="nextLessonLine"
      class="text-start coach-embedded mb-4"
    />

    <v-btn color="secondary" variant="flat" size="large" @click="$emit('continue')">
      {{ t('student.languages.listeningPromotion.actions.continueListening') }}
    </v-btn>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import LearningCoachCard from './LearningCoachCard.vue'

const props = defineProps({
  result: { type: Object, required: true },
})

defineEmits(['continue'])

const { t } = useI18n()

const stageSummary = computed(() =>
  props.result.journey_reset?.learning_stage_name
    ? t('student.languages.coach.success.stageReset', {
        stage: props.result.journey_reset.learning_stage_name,
      })
    : '',
)

const nextLessonLine = computed(() => {
  if (props.result.recommended_next_lesson) {
    return t('student.languages.coach.success.nextLesson', { lesson: props.result.recommended_next_lesson })
  }
  return t('student.languages.coach.success.nextPractice')
})
</script>

<style scoped>
.success-panel {
  padding: 0.85rem;
}
.level-shift {
  flex-wrap: wrap;
}
</style>
