<template>
  <div class="conversation-panel">
    <LanguageSpeakingLevelStrip
      :level="effectiveLevel"
      :baseline="progress?.placement_baseline_level"
      :turn-count="turnCount"
      :trend="progress?.level_trend"
      :next-level="progress?.next_level"
      :mastery-percent="progress?.mastery_progress_percent || 0"
    />

    <v-alert v-if="focus" type="success" variant="tonal" class="mb-3 rounded-lg" density="comfortable" icon="mdi-target">
      Practising: <strong>{{ focus }}</strong> — the AI will steer the chat toward this.
    </v-alert>

    <v-alert v-if="welcomeHint && !messages.length" type="info" variant="tonal" class="mb-4 rounded-lg">
      {{ welcomeHint }}
    </v-alert>

    <v-card class="chat-card glass-card mb-4" variant="flat">
      <div ref="scrollEl" class="chat-messages pa-4">
        <div v-if="!messages.length && !loading" class="text-center text-medium-emphasis py-8">
          <v-icon size="40" color="secondary" class="mb-2">mdi-microphone-message</v-icon>
          <p class="text-body-2 mb-0">Press Start recording and speak in English</p>
        </div>

        <template v-for="(msg, i) in messages" :key="i">
          <div class="msg-row mb-3" :class="msg.role === 'user' ? 'msg-row--user' : 'msg-row--ai'">
            <div class="msg-col" :class="msg.role === 'user' ? 'align-end' : 'align-start'">
              <div class="msg-bubble" :class="msg.role === 'user' ? 'msg-bubble--user' : 'msg-bubble--ai'">
                <template v-if="msg.role === 'user'">
                  <p class="text-body-2 mb-0" dir="ltr">{{ msg.content }}</p>
                </template>
                <template v-else>
                  <SpokenReply
                    :text="msg.content"
                    :audio-url="msg.reply_audio_url"
                    :autoplay="msg.autoplay === true"
                  />
                  <div
                    v-if="!msg.reply_audio_url && msg.reply_audio_pending"
                    class="d-flex align-center gap-2 text-medium-emphasis mt-2"
                  >
                    <v-progress-circular indeterminate size="16" width="2" color="secondary" />
                    <span class="text-caption">Generating voice reply…</span>
                  </div>

                  <!-- Inline correction (your sentence + corrected, colour-coded) + listen-to-correct -->
                  <template v-if="msg.correction_display && msg.correction_display.has_errors">
                    <LanguageSpeakingCorrectionBlock :display="msg.correction_display" class="mt-3" />
                    <v-btn
                      size="x-small"
                      variant="tonal"
                      color="secondary"
                      prepend-icon="mdi-volume-high"
                      class="mt-1"
                      @click="speakText(msg.correction_display.corrected_sentence)"
                    >
                      Listen to the correct sentence
                    </v-btn>
                  </template>
                </template>
              </div>

              <v-chip
                v-if="msg.role === 'user' && pillFor(msg)"
                :color="pillFor(msg).color"
                :prepend-icon="pillFor(msg).icon"
                variant="tonal"
                size="x-small"
                class="mt-1 feedback-pill"
                @click="openFeedback(msg)"
              >
                {{ pillFor(msg).text }}
              </v-chip>
            </div>
          </div>
        </template>

        <div v-if="processing" class="d-flex align-center gap-2 text-medium-emphasis py-2">
          <v-progress-circular indeterminate size="18" width="2" color="secondary" />
          <span class="text-caption">Your voice is being analyzed...</span>
        </div>
      </div>

      <div class="pa-3 border-t d-flex gap-2 flex-wrap align-center">
        <v-btn
          :color="recording ? 'error' : 'secondary'"
          :variant="recording ? 'flat' : 'tonal'"
          :disabled="processing"
          prepend-icon="mdi-microphone"
          @click="recording ? stopRecording() : startRecording()"
        >
          {{ recording ? 'Off' : 'Start recording' }}
        </v-btn>
        <v-btn
          variant="tonal"
          color="secondary"
          prepend-icon="mdi-upload"
          :disabled="processing || recording"
          @click="triggerUpload"
        >
          Upload audio
        </v-btn>
        <input
          ref="audioInput"
          type="file"
          accept="audio/*"
          class="d-none"
          @change="onAudioPicked"
        />
        <v-btn variant="text" color="medium-emphasis" :disabled="processing" @click="resetSession">
          New conversation
        </v-btn>
        <v-spacer />
        <v-menu>
          <template #activator="{ props: menuProps }">
            <v-btn icon="mdi-cog" variant="text" size="small" v-bind="menuProps" />
          </template>
          <v-list density="compact">
            <v-list-item
              v-for="opt in voiceOptions"
              :key="opt.value"
              :active="voice === opt.value"
              @click="setVoice(opt.value)"
            >
              <template #prepend>
                <v-icon size="18" :style="{ opacity: voice === opt.value ? 1 : 0 }">mdi-check</v-icon>
              </template>
              <v-list-item-title>{{ opt.title }}</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
      </div>
    </v-card>

    <v-alert v-if="error" type="error" variant="tonal" density="comfortable" class="rounded-lg">
      {{ error }}
    </v-alert>

    <v-bottom-sheet v-model="feedbackOpen" :inset="true" max-width="580">
      <v-card class="pa-4 feedback-sheet" rounded="t-xl" dir="ltr">
        <div class="d-flex align-center justify-space-between mb-3">
          <span class="text-h6">Feedback</span>
          <v-btn icon="mdi-close" variant="text" size="small" @click="feedbackOpen = false" />
        </div>

        <template v-if="selectedTurn">
          <v-btn
            v-if="sheetSentence"
            size="small"
            variant="tonal"
            color="secondary"
            prepend-icon="mdi-volume-high"
            class="mb-3"
            @click="speakText(sheetSentence)"
          >
            Listen to the correct sentence
          </v-btn>

          <LanguageSpeakingCorrectionBlock
            v-if="sheetAssistant && sheetAssistant.correction_display && sheetAssistant.correction_display.has_errors"
            :display="sheetAssistant.correction_display"
            class="mb-3"
          />

          <div
            v-if="sheetAssistant && sheetAssistant.correction_display && sheetAssistant.correction_display.has_errors"
            class="mb-3"
          >
            <v-btn
              v-if="!explanation && !explaining"
              size="small"
              variant="tonal"
              color="info"
              prepend-icon="mdi-lightbulb-on-outline"
              @click="explainCorrection"
            >
              Explain why
            </v-btn>
            <div v-else-if="explaining" class="d-flex align-center gap-2 text-medium-emphasis">
              <v-progress-circular indeterminate size="16" width="2" color="info" />
              <span class="text-caption">Writing a detailed explanation…</span>
            </div>
            <div v-else-if="explanation" class="explain-block text-body-2 pa-3 rounded-lg" dir="ltr">
              {{ explanation }}
            </div>
          </div>

          <div class="scores-grid mb-3">
            <div v-for="s in sheetScores" :key="s.key" class="score-pill text-center pa-2 rounded-lg">
              <div class="text-caption text-medium-emphasis">{{ s.label }}</div>
              <div class="text-body-1 font-weight-bold">{{ s.value }}</div>
            </div>
          </div>

          <div v-if="sheetPron" class="pron-block rounded-lg pa-3 mb-3">
            <div class="d-flex align-center justify-space-between mb-1">
              <span class="text-caption font-weight-bold">
                <v-icon size="16" :color="pronMeta.color">mdi-account-voice</v-icon>
                Your voice — {{ pronMeta.label }}
              </span>
              <v-chip size="small" :color="pronMeta.color" variant="flat">{{ sheetPron.overall_score }}/100</v-chip>
            </div>
            <v-progress-linear
              :model-value="sheetPron.overall_score"
              :color="pronMeta.color"
              height="6"
              rounded
              class="mb-1"
            />
            <p v-if="sheetPron.note" class="text-caption mb-0">{{ sheetPron.note }}</p>
          </div>

          <div
            v-if="selectedTurn.evaluation && selectedTurn.evaluation.coaching_note_ar"
            class="coach-note text-body-2 pa-3 rounded-lg mb-3"
          >
            {{ selectedTurn.evaluation.coaching_note_ar }}
          </div>

          <template
            v-if="
              sheetAssistant &&
              sheetAssistant.correction_display &&
              sheetAssistant.correction_display.has_errors &&
              sheetAssistant.correction_display.corrected_sentence
            "
          >
            <div class="text-caption font-weight-bold text-medium-emphasis mb-1">
              Practice the corrected sentence
            </div>
            <LanguageShadowingExercise :target="sheetAssistant.correction_display.corrected_sentence" />
          </template>
        </template>
      </v-card>
    </v-bottom-sheet>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import LanguageSpeakingLevelStrip from './LanguageSpeakingLevelStrip.vue'
import LanguageSpeakingCorrectionBlock from './LanguageSpeakingCorrectionBlock.vue'
import LanguageShadowingExercise from './LanguageShadowingExercise.vue'
import SpokenReply from './SpokenReply.vue'
import { useLanguageConversation } from '../../composables/useLanguageConversation.js'
import { fetchConversationTurnExplanation } from '../../api/language.js'
import { getErrorMessage } from '../../api/client.js'

const {
  messages,
  effectiveLevel,
  turnCount,
  welcomeHint,
  progress,
  loading,
  processing,
  recording,
  error,
  voice,
  setVoice,
  focus,
  setFocus,
  loadState,
  loadProgress,
  startRecording,
  stopRecording,
  uploadAudio,
  resetSession,
} = useLanguageConversation()

const route = useRoute()
const scrollEl = ref(null)
const audioInput = ref(null)

function triggerUpload() {
  audioInput.value?.click()
}

function speakText(text) {
  if (!text || !('speechSynthesis' in window)) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(text)
  u.lang = 'en-US'
  u.rate = 0.95
  window.speechSynthesis.speak(u)
}

async function onAudioPicked(e) {
  const file = e.target.files?.[0]
  if (file) await uploadAudio(file)
  e.target.value = '' // allow re-picking the same file
}

// --- Feedback bottom sheet ---
const feedbackOpen = ref(false)
const selectedTurn = ref(null)
const explanation = ref('')
const explaining = ref(false)

function getAssistantForTurn(turnIndex) {
  return messages.value.find((m) => m.role === 'assistant' && m.turn_index === turnIndex) || null
}

function pillFor(msg) {
  if (!msg || !msg.evaluation) return null
  const assistant = getAssistantForTurn(msg.turn_index)
  const hasErrors = !!(assistant && assistant.correction_display && assistant.correction_display.has_errors)
  return hasErrors
    ? { color: 'warning', icon: 'mdi-pencil-circle-outline', text: 'Tap for feedback' }
    : { color: 'success', icon: 'mdi-check-circle-outline', text: 'Good' }
}

function openFeedback(msg) {
  selectedTurn.value = msg
  explanation.value = ''
  explaining.value = false
  feedbackOpen.value = true
  // Auto-load the detailed explanation so the feedback is rich by default (no extra tap).
  const assistant = getAssistantForTurn(msg.turn_index)
  if (assistant?.correction_display?.has_errors) {
    explainCorrection()
  }
}

async function explainCorrection() {
  const turnId = sheetAssistant.value?.turn_db_id
  if (!turnId) return
  explaining.value = true
  try {
    const res = await fetchConversationTurnExplanation(turnId)
    explanation.value = res.explanation || 'No detailed explanation is available for this one.'
  } catch (e) {
    error.value = getErrorMessage(e, 'Could not load the explanation')
  } finally {
    explaining.value = false
  }
}

const sheetAssistant = computed(() =>
  selectedTurn.value ? getAssistantForTurn(selectedTurn.value.turn_index) : null,
)
// The sentence to read aloud in the feedback: the corrected version when there were
// mistakes, otherwise the learner's own (already-correct) sentence.
const sheetSentence = computed(
  () => sheetAssistant.value?.correction_display?.corrected_sentence || selectedTurn.value?.content || '',
)
const sheetScores = computed(() => {
  const s = selectedTurn.value?.evaluation?.scores || {}
  return [
    { key: 'fluency', label: 'Fluency', value: s.fluency ?? 0 },
    { key: 'grammar', label: 'Grammar', value: s.grammar ?? 0 },
    { key: 'vocabulary', label: 'Vocabulary', value: s.vocabulary ?? 0 },
    { key: 'confidence', label: 'Confidence', value: s.confidence ?? 0 },
  ]
})
// Always surface the voice (pronunciation) score as motivational feedback, at any level.
const sheetPron = computed(() => {
  const p = selectedTurn.value?.evaluation?.pronunciation
  return p && typeof p.overall_score === 'number' ? p : null
})

const pronMeta = computed(() => {
  const s = sheetPron.value?.overall_score ?? 0
  if (s >= 90) return { label: 'Excellent', color: 'success' }
  if (s >= 75) return { label: 'Very good', color: 'success' }
  if (s >= 60) return { label: 'Good — keep going', color: 'secondary' }
  if (s >= 40) return { label: 'Keep practising', color: 'warning' }
  return { label: 'Needs work', color: 'error' }
})

const voiceOptions = [
  { title: 'Aria — US, female', value: 'en-US-AriaNeural' },
  { title: 'Jenny — US, female (warm)', value: 'en-US-JennyNeural' },
  { title: 'Guy — US, male', value: 'en-US-GuyNeural' },
  { title: 'Sonia — UK, female', value: 'en-GB-SoniaNeural' },
  { title: 'Ryan — UK, male', value: 'en-GB-RyanNeural' },
]

onMounted(async () => {
  if (route.query.focus) setFocus(String(route.query.focus))
  await loadState()
  await loadProgress()
})

watch(
  () => messages.value.length,
  async () => {
    await nextTick()
    if (scrollEl.value) scrollEl.value.scrollTop = scrollEl.value.scrollHeight
  },
)
</script>

<style scoped>
.chat-card {
  min-height: 420px;
  display: flex;
  flex-direction: column;
}
.voice-select {
  max-width: 230px;
}
.chat-messages {
  flex: 1;
  overflow-y: auto;
  min-height: 280px;
  max-height: 520px;
}
.msg-row--user {
  display: flex;
  justify-content: flex-end;
}
.msg-row--ai {
  display: flex;
  justify-content: flex-start;
}
.msg-col {
  display: flex;
  flex-direction: column;
  max-width: 92%;
}
.msg-col.align-end {
  align-items: flex-end;
}
.msg-col.align-start {
  align-items: flex-start;
}
.msg-bubble {
  max-width: 100%;
  padding: 10px 14px;
  border-radius: 14px;
}
.feedback-pill {
  cursor: pointer;
}
.scores-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}
.score-pill {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
}
.pron-block {
  background: rgba(var(--v-theme-warning), 0.06);
  border: 1px solid rgba(var(--v-theme-warning), 0.18);
}
.coach-note {
  background: rgba(var(--v-theme-info), 0.08);
  border: 1px solid rgba(var(--v-theme-info), 0.2);
}
.explain-block {
  background: rgba(var(--v-theme-info), 0.06);
  border: 1px solid rgba(var(--v-theme-info), 0.18);
}
.msg-bubble--user {
  background: rgba(var(--v-theme-secondary), 0.12);
  border: 1px solid rgba(var(--v-theme-secondary), 0.25);
}
.msg-bubble--ai {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
}
.border-t {
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}
.evaluation-card {
  background: transparent !important;
  border: none !important;
  padding-left: 0 !important;
  padding-right: 0 !important;
}
</style>
