<template>
  <v-card class="glass-card pa-6" variant="flat">
    <div class="text-h6 mb-2">{{ t('student.languages.speaking.live.title') }}</div>
    <div class="text-body-2 mb-4">{{ t('student.languages.speaking.live.subtitle') }}</div>

    <v-alert v-if="errorMessage" type="error" variant="tonal" class="mb-4">
      {{ errorMessage }}
    </v-alert>

    <div class="d-flex align-center gap-3 mb-4 flex-wrap">
      <v-chip :color="stateColor" variant="tonal" size="small">
        {{ t(`student.languages.speaking.live.states.${state}`) }}
      </v-chip>
      <v-chip v-if="assistantSpeaking" color="info" variant="tonal" size="small">
        {{ t('student.languages.speaking.live.assistantSpeaking') }}
      </v-chip>
    </div>

    <div class="d-flex gap-2 mb-4 flex-wrap">
      <v-btn color="secondary" :disabled="!canStart" :loading="state === 'connecting'" @click="onStart">
        {{ t('student.languages.speaking.live.start') }}
      </v-btn>
      <v-btn color="primary" variant="tonal" :disabled="!isListening" @click="onFinalize">
        {{ t('student.languages.speaking.live.finishTurn') }}
      </v-btn>
      <v-btn color="error" variant="tonal" :disabled="state === 'idle'" @click="onStop">
        {{ t('student.languages.speaking.live.stop') }}
      </v-btn>
    </div>

    <v-alert v-if="evaluationResult?.success" type="success" variant="tonal" class="mb-2">
      {{ t('student.languages.speaking.live.evalReady', { version: evaluationResult.engine_version || '7.0.0' }) }}
    </v-alert>
    <v-alert v-else-if="evaluationResult && !evaluationResult.success" type="warning" variant="tonal" class="mb-2">
      {{ evaluationResult.error || t('student.languages.speaking.live.evalFailed') }}
    </v-alert>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useLiveConversation } from '../../composables/useLiveConversation.js'

const { t } = useI18n()
const {
  state,
  errorMessage,
  evaluationResult,
  assistantSpeaking,
  canStart,
  isListening,
  startLiveSession,
  finalizeTurnAndEvaluate,
  stopLiveSession,
} = useLiveConversation()

const stateColor = computed(() => {
  if (state.value === 'assistant_speaking') return 'info'
  if (state.value === 'user_speaking' || state.value === 'listening') return 'success'
  if (state.value === 'failed' || state.value === 'interrupted') return 'warning'
  return 'default'
})

async function onStart() {
  try {
    await startLiveSession()
  } catch (err) {
    errorMessage.value = err?.message || t('student.languages.speaking.live.errors.connect')
  }
}

async function onFinalize() {
  try {
    await finalizeTurnAndEvaluate({ taskPrompt: t('student.languages.speaking.live.defaultPrompt') })
  } catch (err) {
    errorMessage.value = err?.message || t('student.languages.speaking.live.errors.evaluate')
  }
}

async function onStop() {
  await stopLiveSession()
}
</script>
