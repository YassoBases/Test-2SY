<template>
  <div>
    <div class="d-flex align-center flex-wrap gap-2">
      <v-btn
        size="small" variant="tonal" color="secondary" :loading="hearing"
        prepend-icon="mdi-volume-high" @click="hear"
      >Hear</v-btn>
      <v-btn
        size="small" variant="flat" :color="recording ? 'error' : 'secondary'" :loading="checking"
        :prepend-icon="recording ? 'mdi-stop' : 'mdi-microphone'" @click="toggleRecording"
      >{{ recording ? 'Stop' : 'Say it' }}</v-btn>
      <span v-if="recording" class="text-caption text-error">● {{ formattedTime }}</span>
      <span v-if="error" class="text-caption text-error">{{ error }}</span>
    </div>

    <div v-if="feedback && feedback.available" class="mt-2" dir="ltr">
      <v-chip size="small" :color="scoreColor" variant="tonal" class="mr-2">{{ feedback.overall_score }}%</v-chip>
      <span v-if="!feedback.said_target" class="text-caption text-warning">
        Heard “{{ feedback.transcript || '—' }}” — the word is “{{ feedback.target }}”. Try again.
      </span>
      <span v-else-if="feedback.issue" class="text-caption text-medium-emphasis">{{ feedback.issue }}</span>
      <span v-else class="text-caption text-success">Great pronunciation! 🎉</span>
      <div v-if="feedback.tip" class="text-caption text-medium-emphasis mt-1">💡 {{ feedback.tip }}</div>
    </div>
    <div v-else-if="feedback" class="mt-2 text-caption text-medium-emphasis">{{ feedback.tip }}</div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useVoiceRecorder } from '../../composables/useVoiceRecorder.js'
import { sayWord, pronounceWord } from '../../api/language.js'

const props = defineProps({ word: { type: String, required: true } })

const { recording, audioBlob, elapsed, formattedTime, toggleRecording, reset } = useVoiceRecorder({
  minSeconds: 0,
  maxSeconds: 10,
})

const hearing = ref(false)
const checking = ref(false)
const feedback = ref(null)
const error = ref('')

const scoreColor = computed(() => {
  const s = feedback.value?.overall_score ?? 0
  return s >= 80 ? 'success' : s >= 60 ? 'secondary' : 'warning'
})

// Reset feedback when the word changes (e.g. next flashcard).
watch(() => props.word, () => { feedback.value = null; error.value = '' })

async function hear() {
  if (!props.word) return
  hearing.value = true
  error.value = ''
  try {
    const { audio_url } = await sayWord(props.word)
    if (audio_url) await new Audio(audio_url).play()
    else error.value = 'Audio unavailable'
  } catch {
    error.value = 'Could not play audio'
  } finally {
    hearing.value = false
  }
}

// When a recording finishes, send it for pronunciation feedback.
watch(audioBlob, async (blob) => {
  if (!blob) return
  checking.value = true
  error.value = ''
  feedback.value = null
  try {
    feedback.value = await pronounceWord({ word: props.word, blob, durationSeconds: elapsed.value })
  } catch (e) {
    error.value = e?.response?.status === 429 ? 'Slow down a moment, then try again.' : 'Could not check pronunciation'
  } finally {
    checking.value = false
    reset(true)
  }
})
</script>
