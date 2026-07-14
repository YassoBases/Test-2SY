<template>
  <div class="scenarios-panel">
    <v-alert v-if="error" type="error" variant="tonal" class="mb-3 rounded-lg">{{ error }}</v-alert>

    <!-- Scenario picker -->
    <template v-if="view === 'list'">
      <div v-if="loading" class="py-8"><v-progress-linear indeterminate color="secondary" rounded /></div>
      <v-row v-else dense>
        <v-col v-for="sc in scenarios" :key="sc.id" cols="12" md="6">
          <v-card class="glass-card pa-4 h-100" variant="flat">
            <div class="d-flex align-center justify-space-between gap-2 mb-1">
              <span class="text-subtitle-2 font-weight-bold">{{ sc.title_ar }}</span>
              <v-chip size="x-small" :color="sc.locked ? 'medium-emphasis' : 'secondary'" variant="tonal">
                {{ sc.level_min }}+
              </v-chip>
            </div>
            <div class="text-caption text-medium-emphasis mb-1" dir="ltr">{{ sc.title_en }}</div>
            <p class="text-body-2 mb-3">{{ sc.description_ar }}</p>
            <v-btn
              size="small"
              :color="sc.locked ? 'medium-emphasis' : 'secondary'"
              :variant="sc.locked ? 'text' : 'flat'"
              :disabled="sc.locked || starting"
              :prepend-icon="sc.locked ? 'mdi-lock' : 'mdi-play'"
              @click="start(sc)"
            >
              {{ sc.locked ? `Locked — needs ${sc.level_min}` : 'Start' }}
            </v-btn>
          </v-card>
        </v-col>
      </v-row>
      <v-card v-if="!loading && !scenarios.length" class="glass-card pa-6" variant="flat">
        <div class="text-body-2 text-medium-emphasis">No scenarios available yet.</div>
      </v-card>
    </template>

    <!-- Chat -->
    <template v-else>
      <div class="d-flex align-center gap-2 mb-3 flex-wrap">
        <v-btn size="small" variant="text" prepend-icon="mdi-arrow-left" @click="backToList">Scenarios</v-btn>
        <div class="text-subtitle-2 font-weight-bold">{{ active?.title_ar }}</div>
        <v-spacer />
        <v-btn size="small" color="warning" variant="tonal" :loading="ending" :disabled="!messages.length" @click="finish">
          End &amp; get feedback
        </v-btn>
      </div>

      <v-card class="chat-card glass-card mb-3" variant="flat">
        <div ref="scrollEl" class="chat-messages pa-4" dir="ltr">
          <div v-for="(m, i) in messages" :key="i" class="msg-row mb-3" :class="m.role === 'user' ? 'msg-row--user' : 'msg-row--ai'">
            <div class="msg-bubble" :class="m.role === 'user' ? 'msg-bubble--user' : 'msg-bubble--ai'">
              <p class="text-body-2 mb-0">{{ m.text }}</p>
            </div>
          </div>
          <div v-if="sending" class="d-flex align-center gap-2 text-medium-emphasis py-2">
            <v-progress-circular indeterminate size="18" width="2" color="secondary" />
            <span class="text-caption">…</span>
          </div>
        </div>
        <div v-if="recording" class="px-3 pt-2 d-flex align-center gap-2 text-error">
          <v-icon size="16" class="rec-dot">mdi-circle</v-icon>
          <span class="text-caption">Recording… tap the mic to stop</span>
        </div>
        <div class="pa-3 border-t d-flex gap-2 align-center">
          <v-btn
            :color="recording ? 'error' : 'secondary'"
            :variant="recording ? 'flat' : 'tonal'"
            icon
            size="small"
            :disabled="sending"
            @click="recording ? stopRecording() : startRecording()"
          >
            <v-icon>{{ recording ? 'mdi-stop' : 'mdi-microphone' }}</v-icon>
          </v-btn>
          <v-text-field
            v-model="draft"
            density="compact"
            variant="outlined"
            hide-details
            placeholder="Type your reply in English…"
            dir="ltr"
            :disabled="sending || recording"
            @keyup.enter="send"
          />
          <v-btn color="secondary" variant="flat" :loading="sending" :disabled="!draft.trim() || recording" @click="send">Send</v-btn>
        </div>
      </v-card>
    </template>

    <!-- Feedback -->
    <v-dialog v-model="feedbackOpen" max-width="600">
      <v-card class="pa-4" dir="ltr">
        <div class="d-flex align-center justify-space-between mb-3">
          <span class="text-h6">Conversation feedback</span>
          <v-btn icon="mdi-close" variant="text" size="small" @click="feedbackOpen = false" />
        </div>
        <template v-if="feedback">
          <div class="d-flex align-center gap-2 flex-wrap mb-3">
            <v-chip v-if="feedback.estimated_cefr" color="secondary" variant="flat" size="small">
              Estimated level: {{ feedback.estimated_cefr }}
            </v-chip>
            <v-chip
              v-if="feedback.goal_achieved !== undefined"
              :color="feedback.goal_achieved ? 'success' : 'warning'"
              variant="flat"
              size="small"
              :prepend-icon="feedback.goal_achieved ? 'mdi-check-circle' : 'mdi-progress-check'"
            >
              {{ feedback.goal_achieved ? 'Goal achieved' : 'Goal not yet met' }}
            </v-chip>
          </div>

          <div v-if="feedback.scores" class="scores-grid mb-3">
            <div v-for="s in scoreRows" :key="s.key" class="score-pill text-center pa-2 rounded-lg">
              <div class="text-caption text-medium-emphasis">{{ s.label }}</div>
              <div class="text-body-1 font-weight-bold">{{ s.value }}</div>
            </div>
          </div>

          <p v-if="feedback.overall_impression" class="text-body-2 mb-3">{{ feedback.overall_impression }}</p>
          <p v-if="feedback.goal_note" class="text-caption text-medium-emphasis mb-3">{{ feedback.goal_note }}</p>

          <div v-if="feedback.strengths?.length" class="mb-3">
            <div class="text-caption font-weight-bold mb-1">Your strengths</div>
            <ul class="text-body-2 ps-4 mb-0">
              <li v-for="(s, i) in feedback.strengths" :key="i">{{ s }}</li>
            </ul>
          </div>

          <div v-if="feedback.errors?.length" class="mb-3">
            <div class="text-caption font-weight-bold mb-1">Corrections</div>
            <LanguageCorrectionList :errors="scenarioCorrections" />
          </div>

          <div v-if="feedback.vocabulary_suggestions?.length" class="mb-3">
            <div class="text-caption font-weight-bold mb-1">Suggested words</div>
            <div class="d-flex flex-wrap gap-1">
              <v-chip v-for="(w, i) in feedback.vocabulary_suggestions" :key="i" size="x-small" variant="tonal">{{ w }}</v-chip>
            </div>
          </div>

          <div v-if="feedback.cefr_note || feedback.next_focus" class="next-box pa-3 rounded-lg mb-3">
            <p v-if="feedback.cefr_note" class="text-body-2 mb-1"><strong>Level note:</strong> {{ feedback.cefr_note }}</p>
            <p v-if="feedback.next_focus" class="text-body-2 mb-0"><strong>Focus next:</strong> {{ feedback.next_focus }}</p>
          </div>

          <p v-if="feedback.encouragement" class="text-body-2 text-success mb-3">{{ feedback.encouragement }}</p>
          <v-btn color="secondary" variant="flat" @click="closeFeedback">New scenario</v-btn>
        </template>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'
import { endScenario, fetchScenarios, scenarioTurn, scenarioTurnVoice, startScenario } from '../../api/language.js'
import { getErrorMessage } from '../../api/client.js'
import LanguageCorrectionList from './LanguageCorrectionList.vue'

const scenarios = ref([])
const loading = ref(true)
const error = ref('')
const view = ref('list')
const active = ref(null)
const sessionId = ref(null)
const messages = ref([])
const draft = ref('')
const starting = ref(false)
const sending = ref(false)
const ending = ref(false)
const feedbackOpen = ref(false)
const feedback = ref(null)
const scenarioCorrections = computed(() =>
  (feedback.value?.errors || []).map((e) => ({
    original: e.original,
    corrected: e.corrected,
    type: e.type === 'pronunciation' ? 'pronunciation' : 'grammar',
    explanation: e.explanation_ar || e.explanation || '',
  })),
)
const scrollEl = ref(null)
const recording = ref(false)
let mediaRecorder = null
let chunks = []
let micStream = null

const scoreRows = computed(() => {
  const s = feedback.value?.scores || {}
  return [
    { key: 'task_completion', label: 'Task', value: s.task_completion ?? 0 },
    { key: 'fluency', label: 'Fluency', value: s.fluency ?? 0 },
    { key: 'grammar', label: 'Grammar', value: s.grammar ?? 0 },
    { key: 'vocabulary', label: 'Vocabulary', value: s.vocabulary ?? 0 },
    { key: 'interaction', label: 'Interaction', value: s.interaction ?? 0 },
  ]
})

async function loadList() {
  loading.value = true
  try {
    const res = await fetchScenarios()
    scenarios.value = res.scenarios || []
  } catch (e) {
    error.value = e?.response?.data?.detail || 'Could not load scenarios'
  } finally {
    loading.value = false
  }
}

async function start(sc) {
  if (sc.locked) return
  starting.value = true
  error.value = ''
  try {
    const res = await startScenario(sc.id)
    active.value = sc
    sessionId.value = res.session_id
    messages.value = res.opening_line ? [{ role: 'assistant', text: res.opening_line }] : []
    view.value = 'chat'
    scrollDown()
  } catch (e) {
    error.value = e?.response?.data?.detail || 'Could not start the scenario'
  } finally {
    starting.value = false
  }
}

async function send() {
  const text = draft.value.trim()
  if (!text || sending.value) return
  messages.value.push({ role: 'user', text })
  draft.value = ''
  sending.value = true
  scrollDown()
  try {
    const res = await scenarioTurn(sessionId.value, text)
    messages.value.push({ role: 'assistant', text: res.assistant_reply })
    scrollDown()
  } catch (e) {
    error.value = e?.response?.data?.detail || 'Could not send your message'
  } finally {
    sending.value = false
  }
}

async function startRecording() {
  if (sending.value) return
  error.value = ''
  try {
    micStream = await navigator.mediaDevices.getUserMedia({ audio: true })
    chunks = []
    mediaRecorder = new MediaRecorder(micStream, { mimeType: 'audio/webm' })
    mediaRecorder.ondataavailable = (e) => chunks.push(e.data)
    mediaRecorder.onstop = () => sendVoice()
    mediaRecorder.start()
    recording.value = true
  } catch (e) {
    error.value = getErrorMessage(e, 'Unable to access microphone')
  }
}

function stopRecording() {
  if (mediaRecorder && recording.value) {
    mediaRecorder.stop()
    recording.value = false
    micStream?.getTracks().forEach((t) => t.stop())
  }
}

async function sendVoice() {
  const blob = new Blob(chunks, { type: 'audio/webm' })
  if (!blob.size || sending.value) return
  sending.value = true
  try {
    const res = await scenarioTurnVoice(sessionId.value, blob)
    if (res.transcript) messages.value.push({ role: 'user', text: res.transcript })
    messages.value.push({ role: 'assistant', text: res.assistant_reply })
    scrollDown()
  } catch (e) {
    error.value = getErrorMessage(e, 'Could not send your recording')
  } finally {
    sending.value = false
  }
}

async function finish() {
  ending.value = true
  try {
    feedback.value = await endScenario(sessionId.value)
    feedbackOpen.value = true
  } catch (e) {
    error.value = e?.response?.data?.detail || 'Could not end the session'
  } finally {
    ending.value = false
  }
}

function backToList() {
  view.value = 'list'
  sessionId.value = null
  messages.value = []
  loadList()
}

function closeFeedback() {
  feedbackOpen.value = false
  backToList()
}

function scrollDown() {
  nextTick(() => {
    if (scrollEl.value) scrollEl.value.scrollTop = scrollEl.value.scrollHeight
  })
}

onMounted(loadList)
</script>

<style scoped>
.chat-card {
  display: flex;
  flex-direction: column;
}
.chat-messages {
  flex: 1;
  overflow-y: auto;
  min-height: 280px;
  max-height: 460px;
}
.msg-row--user {
  display: flex;
  justify-content: flex-end;
}
.msg-row--ai {
  display: flex;
  justify-content: flex-start;
}
.msg-bubble {
  max-width: 88%;
  padding: 10px 14px;
  border-radius: 14px;
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
.err-box {
  background: rgba(var(--v-theme-warning), 0.06);
  border: 1px solid rgba(var(--v-theme-warning), 0.18);
}
.scores-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
}
.score-pill {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
}
.next-box {
  background: rgba(var(--v-theme-info), 0.06);
  border: 1px solid rgba(var(--v-theme-info), 0.18);
}
@media (max-width: 480px) {
  .scores-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
.rec-dot {
  animation: rec-pulse 1s ease-in-out infinite;
}
@keyframes rec-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}
</style>
