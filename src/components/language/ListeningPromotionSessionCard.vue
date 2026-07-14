<template>
  <v-card class="glass-card pa-5" variant="flat">
    <div class="d-flex align-center justify-space-between flex-wrap gap-2 mb-3">
      <div>
        <div class="text-overline text-medium-emphasis">{{ t('student.languages.listeningPromotion.session.eyebrow') }}</div>
        <div class="text-h6 font-weight-bold">
          {{ t('student.languages.listeningPromotion.session.title', { from: session.official_cefr, to: session.target_cefr }) }}
        </div>
      </div>
      <v-chip color="warning" variant="tonal" size="small" prepend-icon="mdi-timer-outline">
        {{ timerLabel }}
      </v-chip>
    </div>

    <div class="d-flex align-center justify-space-between text-caption text-medium-emphasis mb-3">
      <span>{{ t('student.languages.listeningPromotion.session.progress', { current: answeredCount, total: questions.length }) }}</span>
      <span>{{ t('student.languages.listeningPromotion.session.attempt', { n: session.attempt_number }) }}</span>
    </div>
    <v-progress-linear
      :model-value="questions.length ? (100 * answeredCount) / questions.length : 0"
      color="secondary"
      height="8"
      rounded
      class="mb-4"
    />

    <v-card
      v-for="(question, index) in questions"
      :key="question.id"
      class="assessment-card pa-4 mb-3"
      variant="flat"
    >
      <div class="d-flex align-center gap-2 mb-2">
        <v-chip size="x-small" color="secondary" variant="tonal">
          {{ t('student.languages.listeningPromotion.session.question', { n: index + 1 }) }}
        </v-chip>
        <span v-if="question.objectiveLabel" class="text-caption text-medium-emphasis">{{ question.objectiveLabel }}</span>
      </div>
      <p v-if="question.situation" class="text-body-2 text-medium-emphasis mb-2" dir="ltr">{{ question.situation }}</p>
      <LanguageMcqForm
        :questions="[{ id: question.id, stem: question.stem, choices: question.choices }]"
        :answers="answers"
        @update:answers="$emit('update:answers', $event)"
      />
    </v-card>

    <div class="d-flex flex-wrap gap-2 mt-2">
      <v-btn
        color="secondary"
        variant="flat"
        size="large"
        block
        :loading="submitting"
        :disabled="!canSubmit || expired"
        @click="$emit('submit')"
      >
        {{ t('student.languages.listeningPromotion.actions.submitTest') }}
      </v-btn>
      <v-btn variant="text" @click="$emit('cancel')">{{ t('student.languages.common.back') }}</v-btn>
    </div>

    <v-alert v-if="expired" type="warning" variant="tonal" class="mt-3">
      {{ t('student.languages.listeningPromotion.session.expired') }}
    </v-alert>
  </v-card>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import LanguageMcqForm from './LanguageMcqForm.vue'

const props = defineProps({
  session: { type: Object, required: true },
  questions: { type: Array, default: () => [] },
  answers: { type: Object, default: () => ({}) },
  expiresAtMs: { type: Number, default: null },
  submitting: { type: Boolean, default: false },
})

defineEmits(['update:answers', 'submit', 'cancel'])

const { t } = useI18n()
const now = ref(Date.now())
let timerId = null

const answeredCount = computed(
  () => props.questions.filter((q) => props.answers[q.id] != null).length,
)

const canSubmit = computed(
  () => props.questions.length > 0 && answeredCount.value === props.questions.length,
)

const expired = computed(() => props.expiresAtMs != null && now.value >= props.expiresAtMs)

const timerLabel = computed(() => {
  if (!props.expiresAtMs) return t('student.languages.listeningPromotion.session.noTimer')
  const remainingMs = Math.max(0, props.expiresAtMs - now.value)
  const totalSec = Math.ceil(remainingMs / 1000)
  const min = Math.floor(totalSec / 60)
  const sec = totalSec % 60
  return `${min}:${String(sec).padStart(2, '0')}`
})

onMounted(() => {
  timerId = window.setInterval(() => {
    now.value = Date.now()
  }, 1000)
})

onUnmounted(() => {
  if (timerId) window.clearInterval(timerId)
})
</script>

<style scoped>
.assessment-card {
  border: 1px solid rgba(var(--v-theme-on-surface), 0.08);
  border-radius: 14px;
}
</style>
