<template>
  <div class="chat-input-bar">
    <v-text-field
      ref="fieldRef"
      :model-value="modelValue"
      :placeholder="resolvedPlaceholder"
      variant="solo-filled"
      flat
      rounded="xl"
      hide-details
      class="chat-input-field"
      :disabled="disabled"
      @update:model-value="$emit('update:modelValue', $event)"
      @keyup.enter="submit"
    >
      <template #append-inner>
        <v-btn
          icon
          size="small"
          variant="text"
          :color="recording ? 'error' : 'secondary'"
          :disabled="disabled || loading || voiceLoading"
          :loading="voiceLoading"
          :aria-label="recording ? t('student.chat.voice.stopRecording') : t('student.chat.voice.recordQuestion')"
          class="voice-btn"
          @click.stop="toggleVoice"
        >
          <v-icon>{{ recording ? 'mdi-stop' : 'mdi-microphone' }}</v-icon>
        </v-btn>

        <v-btn
          icon
          size="small"
          variant="text"
          class="send-btn"
          :disabled="!modelValue?.trim() || disabled || recording"
          :loading="loading"
          color="secondary"
          :aria-label="t('student.chat.send.aria')"
          @click="submit"
        >
          <v-icon>mdi-send</v-icon>
        </v-btn>
      </template>
    </v-text-field>
  </div>
</template>

<script setup>
import { computed, nextTick, onUnmounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
  voiceLoading: { type: Boolean, default: false },
})

const resolvedPlaceholder = computed(() => props.placeholder || t('student.chat.input.defaultPlaceholder'))

const emit = defineEmits(['update:modelValue', 'send', 'voice'])

const recording = ref(false)
const fieldRef = ref(null)
let mediaRecorder = null
let mediaStream = null
let chunks = []

function submit() {
  if (!props.modelValue?.trim() || props.disabled || recording.value) return
  emit('send')
}

async function startVoice() {
  if (!navigator.mediaDevices?.getUserMedia) return
  mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true })
  chunks = []
  mediaRecorder = new MediaRecorder(mediaStream)
  mediaRecorder.ondataavailable = (event) => {
    if (event.data.size > 0) chunks.push(event.data)
  }
  mediaRecorder.onstop = () => {
    const blob = new Blob(chunks, { type: mediaRecorder?.mimeType || 'audio/webm' })
    cleanupStream()
    if (blob.size > 0) emit('voice', blob)
  }
  mediaRecorder.start()
  recording.value = true
}

function stopVoice() {
  recording.value = false
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop()
  } else {
    cleanupStream()
  }
}

function toggleVoice() {
  if (recording.value) stopVoice()
  else startVoice()
}

function cleanupStream() {
  if (mediaStream) {
    mediaStream.getTracks().forEach((track) => track.stop())
    mediaStream = null
  }
}

onUnmounted(() => {
  if (recording.value) stopVoice()
  cleanupStream()
})

async function focusInput() {
  await nextTick()
  fieldRef.value?.focus?.()
}

defineExpose({ focusInput })
</script>

<style scoped>
.chat-input-field :deep(.v-field) {
  min-height: 44px;
  border: 1px solid var(--em-border);
  background: var(--em-surface-elevated);
  box-shadow: var(--em-shadow-sm);
  transition:
    border-color var(--em-duration-fast) var(--em-ease-out),
    box-shadow var(--em-duration-fast) var(--em-ease-out),
    background var(--em-duration-fast) var(--em-ease-out);
}

.chat-input-field :deep(.v-field--focused) {
  border-color: var(--em-focus-border);
  box-shadow: var(--em-focus-ring);
}

.chat-input-field :deep(.v-field__input) {
  font-size: 0.875rem;
  padding-top: 8px;
  padding-bottom: 8px;
  color: var(--em-text);
}

.chat-input-field :deep(.v-field__input::placeholder) {
  color: var(--em-text-subtle);
  opacity: 1;
}

.send-btn {
  background: linear-gradient(135deg, var(--em-primary) 0%, var(--em-blue-soft) 100%) !important;
  color: #fff !important;
  box-shadow: var(--em-shadow-sm);
  transition: transform var(--em-duration-fast) var(--em-ease-out), filter var(--em-duration-fast) var(--em-ease-out);
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  filter: brightness(1.05);
}

.voice-btn {
  margin-inline-end: 2px;
  color: var(--em-text-muted) !important;
}
</style>
