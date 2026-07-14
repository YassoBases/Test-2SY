<template>
  <v-card class="glass-card pa-5" variant="flat">
    <LearningCoachCard
      :eyebrow="t('student.languages.coach.promotionResult.eyebrow')"
      :headline="coachHeadline"
      :summary="coachSummary"
      :bullets="strengthBullets"
      :checklist-title="weakTitle"
      :checklist="weakChecklist"
      :next-step="nextStep"
      class="mb-0 coach-embedded"
    />

    <div class="d-flex flex-wrap gap-2 mt-5">
      <v-btn
        v-if="result.result === 'PASS'"
        color="success"
        variant="flat"
        size="large"
        :loading="promoting"
        prepend-icon="mdi-stairs-up"
        @click="$emit('promote')"
      >
        {{ t('student.languages.listeningPromotion.actions.promote') }}
      </v-btn>
      <v-btn variant="tonal" color="secondary" @click="$emit('back')">
        {{ t('student.languages.listeningPromotion.actions.backToStatus') }}
      </v-btn>
    </div>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import LearningCoachCard from './LearningCoachCard.vue'

const props = defineProps({
  result: { type: Object, required: true },
  promoting: { type: Boolean, default: false },
})

defineEmits(['promote', 'back'])

const { t } = useI18n()

const coachHeadline = computed(() =>
  props.result.result === 'PASS'
    ? t('student.languages.coach.promotionResult.passTitle')
    : props.result.result === 'BORDERLINE'
      ? t('student.languages.coach.promotionResult.borderlineTitle')
      : t('student.languages.coach.promotionResult.failTitle'),
)

const coachSummary = computed(() => props.result.recommendation || '')

const strengthBullets = computed(() =>
  (props.result.strengths || []).map((s) => (typeof s === 'string' ? s : s.label || String(s))),
)

const weakTitle = computed(() => t('student.languages.coach.promotionResult.weakTitle'))

const weakChecklist = computed(() =>
  (props.result.weaknesses || []).map((w) => ({
    text: typeof w === 'string' ? w : w.label || String(w),
    done: false,
  })),
)

const nextStep = computed(() => props.result.next_step || props.result.recommendation || '')
</script>
