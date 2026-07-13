<template>
  <div class="page-container slide-up-enter-active">
    <PageHeader
      eyebrow="Learn languages"
      eyebrow-icon="mdi-clipboard-text-clock"
      title="AI Placement Exam"
      subtitle="Speaking, listening, reading, grammar/vocab and writing — then a full level report"
    />
    <LanguageModuleTabs />

    <v-alert v-if="loadError" type="error" variant="tonal" class="mb-4 rounded-lg">{{ loadError }}</v-alert>

    <!-- INTRO -->
    <v-card v-if="view === 'intro'" class="glass-card pa-6 exam-intro text-center" variant="flat">
      <v-icon size="52" color="secondary" class="mb-2">mdi-medal-outline</v-icon>
      <h3 class="text-h6 font-weight-bold mb-1">Full level test — skills plus language systems</h3>
      <p class="text-body-2 text-medium-emphasis mb-4">
        ~10 minutes. You'll speak, listen, read, answer grammar/vocab checks and write. Each skill is graded separately, then
        we map you to a CEFR level and unlock your learning path.
      </p>
      <v-row dense class="mb-2 text-start">
        <v-col v-for="k in INTRO_SKILLS" :key="k" cols="6" sm="4">
          <div class="skill-pill glass-card pa-3 h-100">
            <v-icon :icon="SECTION_META[k].icon" color="secondary" class="mb-1" />
            <div class="font-weight-bold text-body-2">{{ SECTION_META[k].label }}</div>
            <div class="text-caption text-medium-emphasis">{{ SECTION_META[k].hint }}</div>
          </div>
        </v-col>
      </v-row>
      <p class="text-caption text-medium-emphasis mb-0">
        Includes a short speaking task, then a full CEFR level report.
      </p>
      <v-btn color="secondary" variant="flat" size="large" :loading="busy" :disabled="rateLimitBlocked" prepend-icon="mdi-play" class="mt-3" @click="start">
        Start the exam
      </v-btn>
      <v-btn
        v-if="evaluationFailed && sessionId"
        color="warning"
        variant="tonal"
        size="large"
        :loading="busy"
        :disabled="rateLimitBlocked"
        prepend-icon="mdi-refresh"
        class="mt-3 ml-2"
        @click="retryEvaluation"
      >
        Retry report evaluation
      </v-btn>
    </v-card>

    <!-- EXAM -->
    <template v-else-if="view === 'exam' && state">
      <!-- section stepper -->
      <v-card class="glass-card pa-3 mb-3" variant="flat">
        <div class="d-flex align-center justify-space-between flex-wrap gap-2">
          <div class="d-flex align-center gap-2 flex-wrap">
            <v-chip
              v-for="(sec, i) in state.sections"
              :key="sec"
              size="small"
              :color="i === state.section_index ? 'secondary' : undefined"
              :variant="i < state.section_index ? 'flat' : i === state.section_index ? 'flat' : 'tonal'"
              :prepend-icon="i < state.section_index ? 'mdi-check' : skillIcon(sec)"
            >
              {{ skillLabel(sec) }}
            </v-chip>
          </div>
          <v-btn
            size="small"
            color="warning"
            variant="tonal"
            prepend-icon="mdi-restart"
            :loading="busy"
            :disabled="rateLimitBlocked"
            @click="startFresh"
          >
            Start fresh
          </v-btn>
        </div>
        <v-progress-linear
          :model-value="(100 * state.section_index) / state.section_total"
          color="secondary" height="6" rounded class="mt-2"
        />
      </v-card>

      <!-- preparing next section (content generated in the background) -->
      <v-card v-if="state.phase === 'preparing'" class="glass-card pa-8 text-center" variant="flat">
        <v-progress-circular indeterminate color="secondary" size="40" class="mb-3" />
        <h3 class="text-subtitle-1 font-weight-bold mb-1">Preparing your next section…</h3>
        <p class="text-caption text-medium-emphasis mb-0">Generating fresh questions just for you.</p>
      </v-card>

      <!-- SPEAKING / INTERVIEW (chat — scoring is shown only at the end, in the report) -->
      <v-card v-if="isSpeakingPhase" class="glass-card pa-4 mb-3" variant="flat">
        <v-chip v-if="state.speaking?.scenario_title" size="small" color="secondary" variant="tonal" :prepend-icon="state.phase === 'interview' ? 'mdi-account-voice' : 'mdi-drama-masks'" class="mb-2">
          {{ state.speaking.scenario_title }}
        </v-chip>
        <v-alert v-if="state.phase === 'interview'" type="info" variant="tonal" density="compact" class="mb-2">
          Phase 2 — a quick spoken interview to pinpoint your exact level.
        </v-alert>
        <div class="text-caption text-medium-emphasis mb-2">{{ skillLabel(state.phase) }} — answer {{ state.speaking?.turn }} / {{ state.speaking?.total_turns }}</div>

        <div class="exam-chat mb-3">
          <div
            v-for="(m, i) in speakingChat" :key="i"
            class="exam-msg-row" :class="m.role === 'student' ? 'is-user' : 'is-ai'"
          >
            <div class="exam-msg" :class="m.role === 'student' ? 'exam-msg--user' : 'exam-msg--ai'" dir="ltr">
              <span v-if="m.role !== 'student'" class="text-caption text-medium-emphasis d-block mb-1">Examiner</span>
              {{ m.text }}
            </div>
          </div>
          <div v-if="busy" class="d-flex align-center gap-2 text-medium-emphasis py-1">
            <v-progress-circular indeterminate size="16" width="2" color="secondary" />
            <span class="text-caption">Listening to your answer…</span>
          </div>
        </div>

        <div class="recorder-box pa-4 text-center">
          <v-btn
            :color="recorder.recording.value ? 'error' : 'secondary'"
            :variant="recorder.recording.value ? 'flat' : 'tonal'"
            size="large" :icon="recorder.recording.value ? 'mdi-stop' : 'mdi-microphone'"
            :disabled="busy" @click="recorder.toggleRecording()"
          />
          <div class="text-caption text-medium-emphasis mt-2">
            <span v-if="recorder.recording.value">Recording… {{ recorder.formattedTime.value }} — tap to stop</span>
            <span v-else-if="recorder.audioBlob.value">Audio ready — submit once for secure transcription</span>
            <span v-else>Tap to record your spoken answer</span>
          </div>
          <div class="text-caption text-medium-emphasis mt-3">— or —</div>
          <v-file-input
            v-model="uploadFile"
            accept="audio/*"
            density="compact"
            variant="outlined"
            hide-details
            prepend-icon="mdi-upload"
            label="Upload an audio file"
            class="mt-2 upload-input"
            :disabled="busy || recorder.recording.value"
            @update:model-value="onUpload"
          />
        </div>

        <div class="d-flex justify-end mt-3">
          <v-btn
            color="secondary" variant="flat" :loading="busy"
            :disabled="!recorder.audioBlob.value || recorder.recording.value || rateLimitBlocked"
            prepend-icon="mdi-send" @click="sendSpeaking"
          >
            Submit answer
          </v-btn>
        </div>
      </v-card>

      <!-- LISTENING / READING / GRAMMAR-VOCAB (MCQ) -->
      <v-card v-else-if="isMcqPhase && state.mcq" class="glass-card pa-4 mb-3" variant="flat">
        <div class="text-caption text-medium-emphasis mb-2">
          {{ skillLabel(state.phase) }} — question {{ state.mcq.item_index + 1 }}
        </div>

        <template v-if="state.phase === 'listening'">
          <p v-if="state.mcq.situation" class="text-body-2 text-medium-emphasis mb-2">{{ state.mcq.situation }}</p>
          <template v-if="state.mcq.audio_url && !audioFailed">
            <audio
              :src="audioSrc(state.mcq.audio_url)"
              :controls="listenCount < MAX_LISTENS"
              class="w-100 mb-2"
              @play="onListenPlay"
              @error="onAudioUnavailable"
              @loadedmetadata="onAudioMetadata"
            />
            <div class="text-caption mb-3" :class="listensLeft ? 'text-medium-emphasis' : 'text-warning'">
              <template v-if="listenCount === 0">Press play to listen (max {{ MAX_LISTENS }} times)</template>
              <template v-else>Replays remaining: {{ listensLeft }}</template>
            </div>
          </template>
          <v-alert v-else type="warning" variant="tonal" density="compact" class="mb-3">
            Audio playback is unavailable for this clip.
          </v-alert>
        </template>
        <template v-else-if="state.phase === 'reading'">
          <div class="passage-box pa-3 mb-3" dir="ltr">{{ state.mcq.passage }}</div>
        </template>
        <p v-else class="text-body-2 text-medium-emphasis mb-3" dir="ltr">{{ state.mcq.instructions }}</p>

        <!-- Listening questions remain hidden until a real audio playback begins. -->
        <template v-if="showMcqQuestion">
          <p class="text-body-1 font-weight-medium mb-2" dir="ltr">{{ state.mcq.question }}</p>
          <v-radio-group v-model="choice" hide-details class="mb-3">
            <v-radio v-for="(opt, i) in state.mcq.options" :key="i" :value="i" :label="opt" dir="ltr" />
          </v-radio-group>

          <div class="d-flex justify-end">
            <v-btn color="secondary" variant="flat" :loading="busy" :disabled="choice === null || rateLimitBlocked" prepend-icon="mdi-arrow-right" @click="sendMcq">
              Next
            </v-btn>
          </div>
        </template>
        <p v-else-if="listeningRequiresPlayback" class="text-caption text-medium-emphasis mb-0">Listen first — the question appears after you play the clip.</p>
      </v-card>

      <v-card v-else-if="state.phase === 'content_unavailable'" class="glass-card pa-8 text-center" variant="flat">
        <v-icon icon="mdi-cloud-alert" color="warning" size="42" class="mb-3" />
        <h3 class="text-subtitle-1 font-weight-bold mb-1">This section is temporarily unavailable</h3>
        <p class="text-caption text-medium-emphasis mb-3">
          This is a technical content problem, not a missing answer. Your completed work is preserved.
        </p>
        <v-btn color="warning" variant="tonal" prepend-icon="mdi-refresh" :loading="busy" :disabled="rateLimitBlocked" @click="retryContent">
          Retry section preparation
        </v-btn>
      </v-card>

      <!-- WRITING -->
      <v-card v-else-if="state.phase === 'writing' && state.writing" class="glass-card pa-4 mb-3" variant="flat">
        <div class="text-caption text-medium-emphasis mb-1">Writing</div>
        <p class="text-body-1 font-weight-medium mb-3" dir="ltr">{{ state.writing.prompt }}</p>
        <v-textarea
          v-model="writingText"
          variant="outlined"
          rows="6"
          dir="ltr"
          :disabled="busy"
          placeholder="Write your answer in English…"
          counter
          hide-details="auto"
        />
        <div class="d-flex align-center justify-space-between mt-2 flex-wrap gap-2">
          <span class="text-caption" :class="wordCount >= state.writing.min_words ? 'text-success' : 'text-medium-emphasis'">
            {{ wordCount }} words (min {{ state.writing.min_words }})
          </span>
          <v-btn color="secondary" variant="flat" :loading="busy" :disabled="wordCount < state.writing.min_words || rateLimitBlocked" prepend-icon="mdi-check" @click="sendWriting">
            Finish exam
          </v-btn>
        </div>
      </v-card>
    </template>

    <!-- SMART LOADER -->
    <v-card v-else-if="view === 'evaluating'" class="glass-card pa-8 text-center exam-loader" variant="flat">
      <div class="loader-orb mb-4">
        <v-progress-circular indeterminate :size="76" :width="5" color="secondary" />
        <v-icon size="30" color="secondary" class="loader-orb__icon">mdi-brain</v-icon>
      </div>
      <h3 class="text-h6 font-weight-bold mb-2">Grading all four skills</h3>
      <p class="text-body-2 text-medium-emphasis loader-msg">{{ loaderMsg }}</p>
    </v-card>

    <!-- REPORT -->
    <template v-else-if="view === 'report' && report">
      <v-card class="glass-card report-hero pa-6 mb-4 text-center" variant="flat">
        <div class="text-caption text-medium-emphasis mb-1">Your overall level</div>
        <div class="cefr-badge">{{ report.overall_level }}</div>
        <div v-if="report.confidence" class="d-flex align-center justify-center gap-2 mt-3 flex-wrap">
          <v-chip size="small" :color="confidenceColor" variant="tonal" prepend-icon="mdi-shield-check">
            Confidence {{ Math.round(report.confidence * 100) }}%
          </v-chip>
        </div>
        <p v-if="consistencyNote" class="text-caption text-medium-emphasis mt-2 mb-0">{{ consistencyNote }}</p>
        <p v-if="report.summary" class="text-body-2 mt-3 mb-0 report-summary">{{ report.summary }}</p>
      </v-card>

      <v-row class="mb-2">
        <v-col v-for="s in skillRows" :key="s.key" cols="6" sm="3">
          <v-card class="glass-card kpi-card pa-4 text-center" variant="flat">
            <v-icon :icon="s.icon" color="secondary" class="mb-1" />
            <div class="text-caption text-medium-emphasis">{{ s.label }}</div>
            <div class="text-h6 font-weight-bold">{{ s.level }}</div>
            <v-progress-linear :model-value="s.pct" :color="barColor(s.pct)" height="6" rounded class="mt-1" />
            <div class="text-caption text-medium-emphasis mt-1">{{ s.detail }}</div>
          </v-card>
        </v-col>
      </v-row>

      <!-- strongest / weakest + time to next level -->
      <v-row class="mb-2" dense>
        <v-col v-if="report.strongest_skill" cols="6" sm="4">
          <v-card class="glass-card kpi-card kpi-card--success pa-3" variant="flat">
            <div class="text-caption text-medium-emphasis">Strongest skill</div>
            <div class="font-weight-bold text-capitalize">{{ report.strongest_skill }}</div>
          </v-card>
        </v-col>
        <v-col v-if="report.weakest_skill" cols="6" sm="4">
          <v-card class="glass-card kpi-card kpi-card--warning pa-3" variant="flat">
            <div class="text-caption text-medium-emphasis">Focus skill</div>
            <div class="font-weight-bold text-capitalize">{{ report.weakest_skill }}</div>
          </v-card>
        </v-col>
        <v-col v-if="report.weeks_to_next_level" cols="12" sm="4">
          <v-card class="glass-card kpi-card pa-3" variant="flat">
            <div class="text-caption text-medium-emphasis">Est. to next level</div>
            <div class="font-weight-bold">~{{ report.weeks_to_next_level }} weeks</div>
          </v-card>
        </v-col>
      </v-row>

      <!-- speaking breakdown (transcript-assessable criteria) -->
      <section v-if="speakingCriteria.length" class="section-block">
        <div class="section-block__head">
          <h3 class="section-block__title">Speaking breakdown</h3>
          <p class="section-block__subtitle mb-0">Transcript-based criteria; pronunciation is unassessed</p>
        </div>
        <v-card class="glass-card pa-3" variant="flat">
          <div v-for="c in speakingCriteria" :key="c.key" class="mb-2">
            <div class="d-flex justify-space-between text-body-2">
              <span>{{ c.label }}</span><span class="font-weight-bold">{{ c.value.toFixed(1) }}/10</span>
            </div>
            <v-progress-linear :model-value="c.value * 10" :color="barColor(c.value * 10)" height="6" rounded />
          </div>
        </v-card>
      </section>

      <!-- speaking, turn by turn (the detailed per-answer feedback, kept for the end) -->
      <section v-if="report.speaking_turns?.length" class="section-block">
        <div class="section-block__head">
          <h3 class="section-block__title">Speaking — turn by turn</h3>
          <p class="section-block__subtitle mb-0">What you said and how to improve each answer</p>
        </div>
        <v-card v-for="(t, i) in report.speaking_turns" :key="i" class="glass-card pa-3 mb-2" variant="flat" dir="ltr">
          <div v-if="t.question" class="text-caption text-medium-emphasis mb-1">Q: {{ t.question }}</div>
          <p v-if="t.transcription" class="text-body-2 mb-2">“{{ t.transcription }}”</p>
          <div v-if="t.grammar_vocab_feedback" class="text-caption mb-1"><strong>Language:</strong> {{ t.grammar_vocab_feedback }}</div>
          <div v-if="t.pronunciation_feedback" class="text-caption mb-1"><strong>Pronunciation:</strong> {{ t.pronunciation_feedback }}</div>
          <div v-if="t.fluency_note" class="text-caption"><strong>Fluency:</strong> {{ t.fluency_note }}</div>
        </v-card>
      </section>

      <!-- writing breakdown (IELTS 4 criteria) -->
      <section v-if="writingCriteria.length" class="section-block">
        <div class="section-block__head">
          <h3 class="section-block__title">Writing breakdown</h3>
          <p class="section-block__subtitle mb-0">The four IELTS writing criteria</p>
        </div>
        <v-card class="glass-card pa-3" variant="flat">
          <div v-for="c in writingCriteria" :key="c.key" class="mb-2">
            <div class="d-flex justify-space-between text-body-2">
              <span>{{ c.label }}</span><span class="font-weight-bold">{{ c.value.toFixed(1) }}/10</span>
            </div>
            <v-progress-linear :model-value="c.value * 10" :color="barColor(c.value * 10)" height="6" rounded />
          </div>
        </v-card>
      </section>

      <v-row class="mb-2">
        <v-col v-if="report.strengths?.length" cols="12" sm="6">
          <section class="section-block">
            <div class="section-block__head"><h3 class="section-block__title">Strengths</h3></div>
            <v-card class="glass-card pa-3" variant="flat">
              <div v-for="(x, i) in report.strengths" :key="i" class="text-body-2 mb-1"><v-icon size="16" color="success" icon="mdi-check-circle" /> {{ x }}</div>
            </v-card>
          </section>
        </v-col>
        <v-col v-if="report.weaknesses?.length" cols="12" sm="6">
          <section class="section-block">
            <div class="section-block__head"><h3 class="section-block__title">To work on</h3></div>
            <v-card class="glass-card pa-3" variant="flat">
              <div v-for="(x, i) in report.weaknesses" :key="i" class="text-body-2 mb-1"><v-icon size="16" color="warning" icon="mdi-alert-circle" /> {{ x }}</div>
            </v-card>
          </section>
        </v-col>
      </v-row>

      <section v-if="report.detected_errors?.length" class="section-block">
        <div class="section-block__head">
          <h3 class="section-block__title">Corrections</h3>
          <p class="section-block__subtitle mb-0">Real mistakes from your answers, explained</p>
        </div>
        <v-card class="glass-card pa-3 mb-2" variant="flat">
          <LanguageCorrectionList :errors="examCorrections" />
        </v-card>
      </section>

      <section v-if="report.recommendations?.length" class="section-block">
        <div class="section-block__head"><h3 class="section-block__title">Your study plan</h3></div>
        <v-card class="glass-card pa-3" variant="flat">
          <div v-for="(x, i) in report.recommendations" :key="i" class="text-body-2 mb-1 d-flex gap-2">
            <v-icon size="16" color="secondary" icon="mdi-arrow-right-circle" />
            <span><strong>{{ i + 1 }}.</strong> {{ x }}</span>
          </div>
        </v-card>
      </section>

      <v-alert v-if="report.recommended_starting_lesson_topic" type="info" variant="tonal" class="mb-4 rounded-lg" icon="mdi-lightbulb-on-outline">
        <strong>Start here:</strong> {{ report.recommended_starting_lesson_topic }}
      </v-alert>

      <div class="d-flex gap-2 flex-wrap">
        <v-btn color="secondary" variant="flat" :to="ROUTES.STUDENT_LANGUAGES" prepend-icon="mdi-view-dashboard-outline">
          Go to my learning home
        </v-btn>
        <v-btn variant="tonal" :to="ROUTES.STUDENT_LANGUAGES_CURRICULUM" prepend-icon="mdi-map-marker-path">
          My learning path
        </v-btn>
        <v-btn variant="text" :loading="busy" prepend-icon="mdi-restart" @click="restart">Take it again</v-btn>
      </div>
    </template>

    <LoadingState v-else-if="view === 'loading'" variant="cards" :count="2" class="mb-6" />
  </div>
</template>

<script setup>
import { computed, onUnmounted, ref } from 'vue'
import PageHeader from '../../../components/common/PageHeader.vue'
import LoadingState from '../../../components/common/LoadingState.vue'
import LanguageModuleTabs from '../../../components/language/LanguageModuleTabs.vue'
import LanguageCorrectionList from '../../../components/language/LanguageCorrectionList.vue'
import { useVoiceRecorder } from '../../../composables/useVoiceRecorder.js'
import {
  initiateExam,
  fetchExamState,
  submitSpeakingTurn,
  answerExamMcq,
  submitExamWriting,
  fetchExamReport,
  retryExamEvaluation,
  abandonExam,
} from '../../../api/language.js'
import { getErrorMessage } from '../../../api/client.js'
import { mediaUrl } from '../../../utils/media.js'
import { ROUTES } from '../../../constants/app.js'

const SECTION_META = {
  speaking: { label: 'Speaking', icon: 'mdi-microphone', hint: 'Talk to the AI' },
  listening: { label: 'Listening', icon: 'mdi-headphones', hint: 'Listen & answer' },
  reading: { label: 'Reading', icon: 'mdi-book-open-page-variant', hint: 'Read & answer' },
  grammar_vocab: { label: 'Grammar/Vocab', icon: 'mdi-format-letter-case', hint: 'Use English accurately' },
  writing: { label: 'Writing', icon: 'mdi-pencil', hint: 'Write a reply' },
  interview: { label: 'Interview', icon: 'mdi-account-voice', hint: 'Guided follow-up' },
}
// Core skills shown on the intro screen (the interview is a Phase-2 deep-dive).
const INTRO_SKILLS = ['speaking', 'listening', 'reading', 'grammar_vocab', 'writing']
const CONSISTENCY_LABEL = {
  consistent: 'Spoken and written performance matched — high-confidence result',
  speaking_stronger: 'You performed noticeably stronger speaking than in writing',
  writing_stronger: 'You performed noticeably stronger in writing than speaking',
  live_phase_unavailable: 'Based on the written phase only',
}

const view = ref('intro') // intro | exam | evaluating | report | loading
const loadError = ref('')
const busy = ref(false)
const rateLimitBlocked = ref(false)

const sessionId = ref(null)
const state = ref(null)
const lastFeedback = ref(null)
const report = ref(null)
const evaluationFailed = ref(false)
const submissionRequestId = ref('')

const examCorrections = computed(() =>
  (report.value?.detected_errors || []).map((e) => ({
    original: e.original_text,
    corrected: e.corrected_text,
    type: e.type === 'pronunciation' ? 'pronunciation' : 'grammar',
    explanation: e.rule_explanation || '',
  })),
)

const recorder = useVoiceRecorder({ minSeconds: 1 })
const uploadFile = ref(null)
const choice = ref(null)
const writingText = ref('')

function ensureSubmissionRequestId() {
  if (!submissionRequestId.value) {
    submissionRequestId.value = globalThis.crypto?.randomUUID?.()
      || `placement-${Date.now()}-${Math.random().toString(36).slice(2)}`
  }
  return submissionRequestId.value
}

// Listening integrity: questions hidden until first listen; max 2 replays.
const MAX_LISTENS = 2
const listenCount = ref(0)
const audioFailed = ref(false)
const listeningRequiresPlayback = computed(() =>
  state.value?.phase === 'listening'
  && listenCount.value === 0
)
const showMcqQuestion = computed(() => state.value?.phase !== 'listening' || !listeningRequiresPlayback.value)
let prepAttempts = 0

const wordCount = computed(() => writingText.value.trim().split(/\s+/).filter(Boolean).length)

const LOADER_MESSAGES = [
  'Reviewing your spoken answers…',
  'Scoring listening comprehension…',
  'Scoring reading comprehension…',
  'Checking grammar and vocabulary…',
  'Grading your writing…',
  'Mapping each skill to a CEFR level…',
  'Writing your placement report…',
]
const loaderMsg = ref(LOADER_MESSAGES[0])
let loaderTimer = null
let pollTimer = null
let prepTimer = null
let pollRunId = 0
let rateLimitTimer = null

const isSpeakingPhase = computed(() => state.value?.phase === 'speaking' || state.value?.phase === 'interview')
const isMcqPhase = computed(() => ['listening', 'reading', 'grammar_vocab'].includes(state.value?.phase))

// Running chat log for the spoken sections (examiner questions + your transcribed answers).
// No scoring is shown during the exam — all evaluation comes at the end in the report.
const speakingChat = ref([])
function pushExaminer(text) {
  const t = (text || '').trim()
  if (!t) return
  const last = speakingChat.value[speakingChat.value.length - 1]
  if (last && last.role === 'examiner' && last.text === t) return
  speakingChat.value.push({ role: 'examiner', text: t })
}
function pushStudent(text) {
  const t = (text || '').trim()
  if (t) speakingChat.value.push({ role: 'student', text: t })
}

function skillLabel(k) {
  return SECTION_META[k]?.label || k
}
function skillIcon(k) {
  return SECTION_META[k]?.icon || 'mdi-circle-small'
}
function audioSrc(url) {
  return mediaUrl(url)
}

const skillRows = computed(() => {
  const r = report.value
  if (!r) return []
  const rows = [
    { key: 'speaking', label: 'Speaking', icon: 'mdi-microphone', level: r.speaking_level, pct: (r.speaking_score || 0) * 10, detail: `${(r.speaking_score || 0).toFixed(1)}/10` },
    { key: 'listening', label: 'Listening', icon: 'mdi-headphones', level: r.listening_level, pct: r.listening_score_percent || 0, detail: `${Math.round(r.listening_score_percent || 0)}%` },
    { key: 'reading', label: 'Reading', icon: 'mdi-book-open-page-variant', level: r.reading_level, pct: r.reading_score_percent || 0, detail: `${Math.round(r.reading_score_percent || 0)}%` },
    { key: 'writing', label: 'Writing', icon: 'mdi-pencil', level: r.writing_level, pct: (r.writing_score || 0) * 10, detail: `${(r.writing_score || 0).toFixed(1)}/10` },
  ]
  if (r.grammar_vocab_level) {
    rows.splice(3, 0, {
      key: 'grammar_vocab',
      label: 'Grammar/Vocab',
      icon: 'mdi-format-letter-case',
      level: r.grammar_vocab_level,
      pct: r.grammar_vocab_score_percent || 0,
      detail: `${Math.round(r.grammar_vocab_score_percent || 0)}%`,
    })
  }
  return rows
})

const confidenceColor = computed(() => {
  const c = report.value?.confidence || 0
  if (c >= 0.85) return 'success'
  if (c >= 0.7) return 'secondary'
  return 'warning'
})
const consistencyNote = computed(() => CONSISTENCY_LABEL[report.value?.cross_phase_consistency] || '')

const writingCriteria = computed(() => {
  const b = report.value?.writing_breakdown
  if (!b || !Object.keys(b).length) return []
  return [
    { key: 'task_achievement', label: 'Task achievement', value: b.task_achievement || 0 },
    { key: 'coherence', label: 'Coherence & cohesion', value: b.coherence || 0 },
    { key: 'lexical', label: 'Lexical resource', value: b.lexical || 0 },
    { key: 'grammar', label: 'Grammar', value: b.grammar || 0 },
  ]
})

const speakingCriteria = computed(() => {
  const b = report.value?.speaking_breakdown
  if (!b || !Object.keys(b).length) return []
  const criteria = [
    { key: 'fluency', label: 'Fluency & coherence', value: b.fluency || 0 },
    { key: 'lexical', label: 'Lexical resource', value: b.lexical || 0 },
    { key: 'grammar', label: 'Grammar', value: b.grammar || 0 },
  ]
  if (Object.prototype.hasOwnProperty.call(b, 'pronunciation')) {
    criteria.push({ key: 'pronunciation', label: 'Pronunciation', value: b.pronunciation || 0 })
  }
  return criteria
})

function barColor(pct) {
  if (pct >= 75) return 'success'
  if (pct >= 50) return 'secondary'
  if (pct >= 35) return 'warning'
  return 'error'
}

function onUpload(file) {
  const f = Array.isArray(file) ? file[0] : file
  if (f) recorder.setBlob(f)
}

function onListenPlay() {
  listenCount.value += 1
}

const listensLeft = computed(() => Math.max(0, MAX_LISTENS - listenCount.value))

function onAudioUnavailable() {
  audioFailed.value = true
}

function onAudioMetadata(event) {
  const duration = Number(event?.target?.duration || 0)
  if (!Number.isFinite(duration) || duration <= 0.2) {
    audioFailed.value = true
  }
}

function applyState(data) {
  if (prepTimer) { clearTimeout(prepTimer); prepTimer = null }
  state.value = data
  submissionRequestId.value = ''
  if (data.last_feedback) lastFeedback.value = data.last_feedback
  // reset per-section inputs
  choice.value = null
  recorder.reset()
  uploadFile.value = null
  listenCount.value = 0
  audioFailed.value = false
  if (data.phase === 'evaluating') {
    startEvaluating()
  } else if (data.phase === 'completed') {
    loadReport()
  } else {
    if (data.phase !== 'preparing') prepAttempts = 0
    view.value = 'exam'
    if (data.phase === 'preparing') schedulePrepPoll()
    // Append the examiner's current question to the spoken chat log.
    if (isSpeakingPhase.value) pushExaminer(data.speaking?.examiner_message)
  }
}

function retryAfterMs(error, fallbackMs) {
  const headers = error?.response?.headers
  const raw = headers?.['retry-after'] ?? headers?.get?.('retry-after')
  if (raw == null || raw === '') return fallbackMs
  const seconds = Number(raw)
  if (Number.isFinite(seconds) && seconds >= 0) {
    return Math.min(5 * 60 * 1000, Math.max(1000, Math.ceil(seconds * 1000)))
  }
  const retryAt = Date.parse(raw)
  if (Number.isFinite(retryAt)) {
    return Math.min(5 * 60 * 1000, Math.max(1000, retryAt - Date.now()))
  }
  return fallbackMs
}

function handleRequestError(error, fallbackMessage) {
  if (error?.response?.status !== 429) {
    loadError.value = getErrorMessage(error, fallbackMessage)
    return
  }
  const delayMs = retryAfterMs(error, 30_000)
  const seconds = Math.max(1, Math.ceil(delayMs / 1000))
  rateLimitBlocked.value = true
  if (rateLimitTimer) clearTimeout(rateLimitTimer)
  rateLimitTimer = setTimeout(() => {
    rateLimitTimer = null
    rateLimitBlocked.value = false
  }, delayMs)
  loadError.value = `Too many requests. Please retry in ${seconds} seconds.`
}

async function recoverStaleState(error) {
  const detail = error?.response?.data?.detail
  if (detail?.code !== 'stale_exam_state' || !sessionId.value) return false
  try {
    applyState(await fetchExamState(sessionId.value))
    loadError.value = 'The exam advanced before this answer arrived. Review the current question and answer again.'
  } catch (refreshError) {
    handleRequestError(refreshError, 'The exam state changed and could not be refreshed')
  }
  return true
}

function schedulePrepPoll(delayMs = 2500) {
  prepAttempts += 1
  if (prepAttempts > 30) {
    loadError.value = 'Required exam content is temporarily unavailable. Your answers were preserved.'
    state.value = { ...state.value, phase: 'content_unavailable', evidence_status: 'content_unavailable' }
    return
  }
  prepTimer = setTimeout(async () => {
    prepTimer = null
    try {
      applyState(await fetchExamState(sessionId.value))
    } catch (e) {
      schedulePrepPoll(retryAfterMs(e, 2500))
    }
  }, delayMs)
}

async function start() {
  if (busy.value || rateLimitBlocked.value) return
  busy.value = true
  loadError.value = ''
  try {
    const data = await initiateExam()
    sessionId.value = data.session_id
    lastFeedback.value = null
    speakingChat.value = []
    applyState(data)
  } catch (e) {
    handleRequestError(e, 'Could not start the exam')
  } finally {
    busy.value = false
  }
}

async function retryContent() {
  if (!sessionId.value || busy.value || rateLimitBlocked.value) return
  busy.value = true
  loadError.value = ''
  try {
    applyState(await fetchExamState(sessionId.value))
  } catch (e) {
    handleRequestError(e, 'Could not retry section preparation')
  } finally {
    busy.value = false
  }
}

async function startFresh() {
  if (busy.value || rateLimitBlocked.value) return
  busy.value = true
  loadError.value = ''
  try {
    if (sessionId.value) await abandonExam(sessionId.value)
  } catch {
    /* continue with a fresh initiate attempt */
  } finally {
    sessionId.value = null
    report.value = null
    state.value = null
    lastFeedback.value = null
    speakingChat.value = []
    writingText.value = ''
    choice.value = null
    listenCount.value = 0
    audioFailed.value = false
    uploadFile.value = null
    recorder.reset()
    prepAttempts = 0
    busy.value = false
  }
  await start()
}

async function sendSpeaking() {
  if (!recorder.audioBlob.value || busy.value || rateLimitBlocked.value) return
  busy.value = true
  loadError.value = ''
  try {
    const data = await submitSpeakingTurn(
      sessionId.value,
      recorder.audioBlob.value,
      recorder.elapsed.value,
      ensureSubmissionRequestId(),
      state.value.state_revision,
      state.value.turn_token || state.value.speaking?.turn_token,
    )
    // Show what the student said as a chat bubble (no scoring shown until the final report).
    pushStudent(data.last_feedback?.transcription)
    applyState(data)
  } catch (e) {
    if (!(await recoverStaleState(e))) handleRequestError(e, 'Could not submit your answer')
  } finally {
    busy.value = false
  }
}

async function sendMcq() {
  if (choice.value === null || busy.value || rateLimitBlocked.value) return
  busy.value = true
  loadError.value = ''
  try {
    const data = await answerExamMcq(
      sessionId.value,
      choice.value,
      ensureSubmissionRequestId(),
      state.value.state_revision,
      state.value.question_token || state.value.mcq?.question_token,
    )
    applyState(data)
  } catch (e) {
    if (!(await recoverStaleState(e))) handleRequestError(e, 'Could not save your answer')
  } finally {
    busy.value = false
  }
}

async function sendWriting() {
  if (wordCount.value < (state.value?.writing?.min_words || 0) || busy.value || rateLimitBlocked.value) return
  busy.value = true
  loadError.value = ''
  try {
    const data = await submitExamWriting(
      sessionId.value,
      writingText.value.trim(),
      ensureSubmissionRequestId(),
      state.value.state_revision,
      state.value.prompt_token || state.value.writing?.prompt_token,
    )
    if (data.status === 'processing') {
      startEvaluating()
    } else {
      applyState(data)
    }
  } catch (e) {
    if (!(await recoverStaleState(e))) handleRequestError(e, 'Could not submit your writing')
  } finally {
    busy.value = false
  }
}

async function retryEvaluation() {
  if (!sessionId.value || busy.value || rateLimitBlocked.value) return
  busy.value = true
  loadError.value = ''
  try {
    await retryExamEvaluation(sessionId.value)
    evaluationFailed.value = false
    startEvaluating()
  } catch (e) {
    handleRequestError(e, 'Could not retry the placement evaluation')
  } finally {
    busy.value = false
  }
}

function startEvaluating() {
  finishLoading()
  const runId = pollRunId
  evaluationFailed.value = false
  view.value = 'evaluating'
  let i = 0
  loaderMsg.value = LOADER_MESSAGES[0]
  loaderTimer = setInterval(() => {
    i = (i + 1) % LOADER_MESSAGES.length
    loaderMsg.value = LOADER_MESSAGES[i]
  }, 1500)
  const startedAt = Date.now()
  let attempts = 0
  const pollReport = async () => {
    pollTimer = null
    attempts += 1
    let nextDelay = 2000
    try {
      const r = await fetchExamReport(sessionId.value)
      if (runId !== pollRunId) return
      const elapsed = Date.now() - startedAt
      if (r.status === 'completed' && r.report && elapsed >= 4000) {
        report.value = r.report
        finishLoading()
        view.value = 'report'
        return
      } else if (r.status === 'failed') {
        finishLoading()
        evaluationFailed.value = true
        loadError.value = r.error_message || 'The report could not be generated. Please retry the evaluation.'
        view.value = 'intro'
        return
      }
    } catch (e) {
      if (runId !== pollRunId) return
      nextDelay = retryAfterMs(e, 2000)
    }
    if (attempts > 45) {
      finishLoading()
      loadError.value = 'Report is taking too long. Please try again later.'
      view.value = 'intro'
      return
    }
    if (runId === pollRunId) pollTimer = setTimeout(pollReport, nextDelay)
  }
  pollTimer = setTimeout(pollReport, 0)
}

async function loadReport() {
  try {
    const r = await fetchExamReport(sessionId.value)
    if (r.report) {
      report.value = r.report
      view.value = 'report'
    }
  } catch (e) {
    if (e?.response?.status === 429) {
      pollTimer = setTimeout(loadReport, retryAfterMs(e, 30_000))
    } else {
      loadError.value = getErrorMessage(e, 'Could not load your report')
    }
  }
}

function finishLoading() {
  pollRunId += 1
  if (loaderTimer) clearInterval(loaderTimer)
  if (pollTimer) clearTimeout(pollTimer)
  if (prepTimer) clearTimeout(prepTimer)
  loaderTimer = null
  pollTimer = null
  prepTimer = null
}

async function restart() {
  // Best-effort: drop any unfinished attempt so the next start is guaranteed fresh.
  if (sessionId.value) {
    try { await abandonExam(sessionId.value) } catch { /* ignore */ }
  }
  sessionId.value = null
  report.value = null
  state.value = null
  lastFeedback.value = null
  speakingChat.value = []
  writingText.value = ''
  prepAttempts = 0
  audioFailed.value = false
  loadError.value = ''
  view.value = 'intro'
}

onUnmounted(() => {
  finishLoading()
  if (rateLimitTimer) clearTimeout(rateLimitTimer)
})
</script>

<style scoped>
.page-container { max-width: 820px; margin: 0 auto; }
.exam-intro { border: 1px solid rgba(var(--v-theme-secondary), 0.25); }
.skill-pill { border: 1px solid rgba(255, 255, 255, 0.08); }
.examiner-q { line-height: 1.5; }
.exam-chat { max-height: 320px; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; }
.exam-msg-row { display: flex; }
.exam-msg-row.is-user { justify-content: flex-end; }
.exam-msg-row.is-ai { justify-content: flex-start; }
.exam-msg { max-width: 86%; padding: 9px 13px; border-radius: 14px; line-height: 1.45; }
.exam-msg--user { background: rgba(var(--v-theme-secondary), 0.16); border: 1px solid rgba(var(--v-theme-secondary), 0.3); }
.exam-msg--ai { background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.08); }
.recorder-box { border: 1px dashed rgba(var(--v-theme-secondary), 0.4); border-radius: 14px; }
.upload-input { max-width: 360px; margin-inline: auto; }
.passage-box {
  background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px; line-height: 1.6; max-height: 320px; overflow-y: auto;
}
.feedback-card { border: 1px solid rgba(var(--v-theme-secondary), 0.3); }

.exam-loader { border: 1px solid rgba(var(--v-theme-secondary), 0.25); }
.loader-orb { position: relative; display: inline-grid; place-items: center; }
.loader-orb__icon { position: absolute; }
.loader-msg { min-height: 1.4em; transition: opacity 0.3s; }

.report-hero { border: 1px solid rgba(var(--v-theme-secondary), 0.3); }
.cefr-badge {
  display: inline-block; font-size: 2.6rem; font-weight: 800; letter-spacing: 0.04em;
  padding: 6px 26px; border-radius: 16px; color: #fff;
  background: linear-gradient(135deg, var(--em-purple, #7c6cf0), var(--em-cyan, #22d3ee));
  box-shadow: 0 14px 36px -10px rgba(124, 108, 240, 0.6);
}
.report-summary { max-width: 60ch; margin-inline: auto; color: rgba(var(--v-theme-on-surface), 0.78); }
</style>
