<template>
  <div class="page-container slide-up-enter-active">
    <PageHeader eyebrow="Learn languages" eyebrow-icon="mdi-microphone" title="Speaking" subtitle="Practice speaking and get instant feedback" />
    <LanguageModuleTabs />

    <LanguageSpeakingModeToggle v-model="speakingMode" class="mb-2" />

    <v-alert v-if="loadError" type="error" variant="tonal" class="mb-4">{{ loadError }}</v-alert>
    <LoadingState v-if="loading && speakingMode === 'exercises'" variant="cards" :count="3" class="mb-6" />

    <!-- AI Conversation Mode -->
    <LanguageSpeakingConversationPanel v-if="speakingMode === 'conversation'" />

    <!-- Shadowing Mode (repeat after me) -->
    <LanguageShadowingPanel v-else-if="speakingMode === 'shadowing'" />

    <!-- Role-play Scenarios (text conversation) -->
    <LanguageScenariosPanel v-else-if="speakingMode === 'scenarios'" />

    <!-- Speaking Exercises (unchanged) -->
    <v-row v-else-if="!loading">
      <v-col cols="12" md="4">
        <v-list density="comfortable">
          <v-list-item
            v-for="p in prompts"
            :key="p.id"
            :active="selectedId === p.id"
            rounded="lg"
            @click="selectPrompt(p.id)"
          >
            <v-list-item-title>{{ p.title }}</v-list-item-title>
          </v-list-item>
        </v-list>
        <EmptyState v-if="!prompts.length" compact preset="languageExercise" />
      </v-col>
      <v-col cols="12" md="8">
        <EmptyState
          v-if="!selectedId && prompts.length"
          compact
          icon="mdi-cursor-default-click-outline"
          title="Choose an exercise"
          description="Select an exercise from the list to begin."
        />
        <v-card v-else-if="prompt" class="glass-card pa-6" variant="flat">
          <div class="text-h6 mb-2" dir="ltr">{{ prompt.prompt }}</div>
          <div class="text-caption mb-3">minimum: {{ prompt.min_seconds }} second</div>

          <div class="d-flex gap-2 mb-4 flex-wrap">
            <v-btn color="error" variant="tonal" :disabled="recording" @click="startRec">Start recording</v-btn>
            <v-btn color="secondary" variant="flat" :disabled="!recording" @click="stopRec">Stop</v-btn>
            <v-btn
              color="secondary"
              variant="tonal"
              :loading="submitting"
              :disabled="!canSubmit"
              @click="submit"
            >
              Submit
            </v-btn>
          </div>

          <v-alert
            v-if="durationSeconds > 0 && prompt && durationSeconds < prompt.min_seconds"
            type="warning"
            variant="tonal"
            density="comfortable"
            class="mb-3 rounded-lg"
            dir="ltr"
          >
            {{ minSecondsRequiredMessage(prompt.min_seconds) }}
          </v-alert>

          <audio v-if="playbackUrl" :src="playbackUrl" controls class="w-100 mb-4" />

          <v-alert v-if="result" :type="result.passed ? 'success' : 'warning'" variant="tonal">
            {{ result.passed ? 'Exercise completed' : 'Submitted — try to record longer next time' }}
          </v-alert>

          <v-card
            v-if="result && (result.transcript || result.reply || result.correction_text)"
            variant="tonal"
            color="secondary"
            class="mt-4 pa-4 rounded-lg"
            dir="ltr"
          >
            <div class="text-subtitle-2 mb-2">AI feedback</div>

            <div v-if="result.transcript" class="mb-3">
              <div class="text-caption text-medium-emphasis">What we heard</div>
              <div class="text-body-2">{{ result.transcript }}</div>
            </div>

            <div v-if="result.reply" class="mb-3">
              <div class="text-caption text-medium-emphasis">Tutor reply</div>
              <div class="text-body-2">{{ result.reply }}</div>
              <audio v-if="result.reply_audio_url" :src="result.reply_audio_url" controls class="w-100 mt-2" />
            </div>

            <LanguageSpeakingCorrectionBlock
              v-if="speakingCorrection"
              :display="speakingCorrection"
              :weak-words="speakingWeakWords"
              class="mt-2"
            />
          </v-card>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import PageHeader from '../../../components/common/PageHeader.vue'
import LoadingState from '../../../components/common/LoadingState.vue'
import EmptyState from '../../../components/common/EmptyState.vue'
import LanguageModuleTabs from '../../../components/language/LanguageModuleTabs.vue'
import LanguageSpeakingModeToggle from '../../../components/language/LanguageSpeakingModeToggle.vue'
import LanguageSpeakingConversationPanel from '../../../components/language/LanguageSpeakingConversationPanel.vue'
import LanguageShadowingPanel from '../../../components/language/LanguageShadowingPanel.vue'
import LanguageScenariosPanel from '../../../components/language/LanguageScenariosPanel.vue'
import LanguageSpeakingCorrectionBlock from '../../../components/language/LanguageSpeakingCorrectionBlock.vue'
import {
  fetchSpeakingPrompt,
  fetchSpeakingPrompts,
  submitSpeakingPractice,
  uploadSpeakingPractice,
} from '../../../api/language.js'
import { useLanguageGate } from '../../../composables/useLanguageGate.js'
import { useLanguageAccess } from '../../../composables/useLanguageAccess.js'
import { minSecondsRequiredMessage } from '../../../utils/languageValidation.js'

const { access, loadAccess } = useLanguageAccess()
const { handleLanguageApiError, getErrorMessage } = useLanguageGate()

const router = useRouter()
const route = useRoute()

const validModes = ['exercises', 'conversation', 'shadowing', 'scenarios']
const speakingMode = ref(validModes.includes(route.query.mode) ? route.query.mode : 'exercises')
const prompts = ref([])
const loading = ref(true)
const loadError = ref('')
const selectedId = ref(null)
const prompt = ref(null)
const recording = ref(false)
const submitting = ref(false)
const result = ref(null)

// Colour-coded correction (grammar red / pronunciation yellow / fix green) for the last attempt.
const speakingWeakWords = computed(() =>
  (result.value?.weak_words || result.value?.pronunciation?.words || [])
    .filter((w) => (typeof w === 'string' ? w : w?.weak))
    .map((w) => (typeof w === 'string' ? w : w?.word)),
)
const speakingCorrection = computed(() => {
  const r = result.value
  if (!r || !r.correction_text || r.correction_text === r.transcript) return null
  const explanation = (r.grammar_errors || [])
    .map((e) => e.message)
    .filter(Boolean)
    .slice(0, 3)
    .join(' ')
  return {
    has_errors: true,
    your_sentence: r.transcript || '',
    corrected_sentence: r.correction_text || '',
    explanation,
  }
})

const mediaObjectId = ref(null)
const playbackUrl = ref(null)
const durationSeconds = ref(0)

let mediaRecorder = null
let chunks = []
let startedAt = 0

const canSubmit = computed(() => {
  if (!mediaObjectId.value || !prompt.value) return false
  return durationSeconds.value >= prompt.value.min_seconds
})

onMounted(async () => {
  try {
    await loadAccess(true)
    if (access.value?.redirect) {
      router.push(access.value.redirect)
      return
    }
    const res = await fetchSpeakingPrompts()
    prompts.value = res.prompts || []
  } catch (e) {
    if (!handleLanguageApiError(e, access.value)) {
      loadError.value = getErrorMessage(e, 'Unable to download')
    }
  } finally {
    loading.value = false
  }
})

async function selectPrompt(id) {
  selectedId.value = id
  result.value = null
  mediaObjectId.value = null
  playbackUrl.value = null
  try {
    prompt.value = await fetchSpeakingPrompt(id)
    if (prompt.value.progress?.public_url) {
      playbackUrl.value = prompt.value.progress.public_url
      mediaObjectId.value = prompt.value.progress.media_object_id
    }
  } catch (e) {
    if (!handleLanguageApiError(e, access.value)) {
      loadError.value = getErrorMessage(e, 'Unable to load the exercise')
    }
  }
}

async function startRec() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    chunks = []
    mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' })
    mediaRecorder.ondataavailable = (e) => chunks.push(e.data)
    mediaRecorder.onstop = async () => {
      stream.getTracks().forEach((t) => t.stop())
      const blob = new Blob(chunks, { type: 'audio/webm' })
      durationSeconds.value = Math.max(1, Math.round((Date.now() - startedAt) / 1000))
      playbackUrl.value = URL.createObjectURL(blob)
      const up = await uploadSpeakingPractice(selectedId.value, blob)
      mediaObjectId.value = up.media_object_id
      if (up.public_url) playbackUrl.value = up.public_url
    }
    startedAt = Date.now()
    mediaRecorder.start()
    recording.value = true
  } catch (e) {
    loadError.value = getErrorMessage(e, 'Unable to access microphone')
  }
}

function stopRec() {
  if (mediaRecorder && recording.value) {
    mediaRecorder.stop()
    recording.value = false
  }
}

async function submit() {
  if (!selectedId.value || !mediaObjectId.value || !prompt.value) return
  if (durationSeconds.value < prompt.value.min_seconds) {
    loadError.value = minSecondsRequiredMessage(prompt.value.min_seconds)
    return
  }
  submitting.value = true
  try {
    result.value = await submitSpeakingPractice(selectedId.value, {
      media_object_id: mediaObjectId.value,
      duration_seconds: durationSeconds.value,
    })
    const res = await fetchSpeakingPrompts()
    prompts.value = res.prompts || []
  } catch (e) {
    loadError.value = getErrorMessage(e, 'Unable to send')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.page-container { max-width: 1100px; margin: 0 auto; }
</style>
