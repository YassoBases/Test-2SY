<template>
  <div>
    <template v-if="phase === 'dashboard'">
      <ListeningPromotionStatusCard
        :journey="journey"
        :loading="statusLoading"
        :can-start="canStartTest"
        :has-active-session="hasActiveSession"
        :session-loading="sessionLoading"
        @start="$emit('start')"
        @resume="$emit('resume')"
      />
      <ListeningPromotionHistoryCard :history-events="historyEvents" class="mt-4" />
    </template>

    <template v-else-if="phase === 'session' && session">
      <ListeningPromotionSessionCard
        :session="session"
        :questions="mcqQuestions"
        :answers="answers"
        @update:answers="answers = $event"
        :expires-at-ms="expiresAtMs"
        :submitting="submitLoading"
        @submit="$emit('submit', answers)"
        @cancel="$emit('cancel')"
      />
    </template>

    <template v-else-if="phase === 'result' && submitResult">
      <ListeningPromotionResultCard
        :result="submitResult"
        :promoting="promoteLoading"
        @promote="$emit('promote')"
        @back="$emit('back')"
      />
    </template>

    <template v-else-if="phase === 'success' && promotionResult">
      <ListeningPromotionSuccessCard :result="promotionResult" @continue="$emit('continue')" />
    </template>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import ListeningPromotionStatusCard from './ListeningPromotionStatusCard.vue'
import ListeningPromotionHistoryCard from './ListeningPromotionHistoryCard.vue'
import ListeningPromotionSessionCard from './ListeningPromotionSessionCard.vue'
import ListeningPromotionResultCard from './ListeningPromotionResultCard.vue'
import ListeningPromotionSuccessCard from './ListeningPromotionSuccessCard.vue'

defineProps({
  phase: { type: String, default: 'dashboard' },
  journey: { type: Object, default: null },
  historyEvents: { type: Array, default: () => [] },
  statusLoading: { type: Boolean, default: false },
  canStartTest: { type: Boolean, default: false },
  hasActiveSession: { type: Boolean, default: false },
  sessionLoading: { type: Boolean, default: false },
  session: { type: Object, default: null },
  mcqQuestions: { type: Array, default: () => [] },
  expiresAtMs: { type: Number, default: null },
  submitLoading: { type: Boolean, default: false },
  submitResult: { type: Object, default: null },
  promoteLoading: { type: Boolean, default: false },
  promotionResult: { type: Object, default: null },
})

defineEmits(['start', 'resume', 'submit', 'cancel', 'promote', 'back', 'continue'])

const answers = ref({})
</script>
