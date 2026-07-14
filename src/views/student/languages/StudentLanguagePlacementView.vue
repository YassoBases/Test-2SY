<template>
  <div class="page-container slide-up-enter-active">
    <PageHeader
      eyebrow="Learn languages"
      eyebrow-icon="mdi-translate"
      title="Placement test"
      subtitle="Answer the four skill questions to determine your level"
    />

    <v-alert v-if="loadError" type="error" variant="tonal" class="mb-4 rounded-lg">{{ loadError }}</v-alert>

    <LoadingState v-if="loading" variant="cards" :count="3" class="mb-6" />

    <template v-else-if="state && !showResults">
      <v-card class="glass-card pa-5 mb-4" variant="flat">
        <div class="d-flex align-center justify-space-between flex-wrap gap-3">
          <div class="text-body-2 text-medium-emphasis">
            {{ stepLabel }} — a question {{ currentIndexInStep + 1 }} / {{ currentStepQuestions.length }}
          </div>
          <v-chip color="secondary" variant="tonal" size="small">
            {{ totalAnswered }} / {{ totalQuestions }} Answered
          </v-chip>
        </div>

        <v-progress-linear
          class="mt-4"
          :model-value="overallProgress"
          color="secondary"
          height="10"
          rounded
        />

        <div class="d-flex gap-2 flex-wrap mt-4">
          <v-chip
            v-for="s in steps"
            :key="s.key"
            :color="s.key === activeStep ? 'secondary' : 'default'"
            :variant="s.key === activeStep ? 'flat' : 'tonal'" size="small"
          >
            {{ s.label }}
            <span v-if="stepAnsweredCount[s.key]"> ({{ stepAnsweredCount[s.key] }})</span>
          </v-chip>
        </div>
      </v-card>

      <v-card v-if="!currentQuestion" class="glass-card pa-6" variant="flat">
        <v-alert type="warning" variant="tonal" density="comfortable">
          No questions are available for this section yet.
        </v-alert>
      </v-card>

      <v-card v-else class="glass-card pa-6" variant="flat">
        <div class="text-subtitle-1 font-weight-bold mb-2">{{ questionTitle }}</div>

        <div v-if="currentQuestion?.media_url" class="mb-4">
          <audio :src="currentQuestion.media_url" controls class="w-100" />
        </div>

        <div class="text-body-1 mb-4">
          {{ currentStem }}
        </div>

        <!-- MCQ -->
        <div v-if="isMcq">
          <v-radio-group v-model="mcqValue" @update:model-value="autosaveMcq">
            <v-radio
              v-for="(c, idx) in currentChoices"
              :key="idx"
              :label="String(c)"
              :value="idx"
            />
          </v-radio-group>
        </div>

        <!-- Writing -->
        <div v-else-if="isWriting">
          <v-textarea
            v-model="textValue"
            :rows="6"
            auto-grow
            counter
            :hint="writingHint"
            persistent-hint
            @update:model-value="autosaveText"
          />
        </div>

        <!-- Speaking -->
        <div v-else-if="isSpeaking">
          <v-alert type="info" variant="tonal" class="mb-4">
            Record your answer audio. It will be done Save Register automatically.
          </v-alert>

          <div class="d-flex gap-2 flex-wrap align-center">
            <v-btn
              color="secondary"
              variant="flat"
              :disabled="recording || uploadingAudio"
              @click="startRecording"
            >
              Start recording
            </v-btn>
            <v-btn
              color="warning"
              variant="tonal"
              :disabled="!recording"
              @click="stopRecording"
            >
              Off
            </v-btn>
            <v-btn
              color="secondary"
              variant="tonal"
              prepend-icon="mdi-upload"
              :disabled="recording || uploadingAudio"
              @click="triggerSpeakingUpload"
            >
              Upload audio
            </v-btn>
            <input
              ref="speakingFileInput"
              type="file"
              accept="audio/*"
              class="d-none"
              @change="onSpeakingFilePicked"
            />
            <v-progress-circular v-if="uploadingAudio" indeterminate color="secondary" size="22" />
          </div>

          <div v-if="speakingMediaUrl" class="mt-4">
            <div class="text-caption text-medium-emphasis mb-1">Last saved recording</div>
            <audio :src="speakingMediaUrl" controls class="w-100" />
          </div>
          <v-alert
            v-else-if="speakingSaved"
            type="success"
            variant="tonal"
            density="comfortable"
            class="mt-4"
            icon="mdi-check-circle"
          >
            You already recorded an answer for this question. Record again to replace it.
          </v-alert>
        </div>

        <div class="d-flex align-center justify-space-between flex-wrap gap-2 mt-6">
          <v-btn variant="tonal" :disabled="isFirst" @click="prev">the previous</v-btn>
          <div class="d-flex gap-2">
            <v-btn v-if="!isLast" color="secondary" variant="flat" @click="next">the next</v-btn>
            <v-btn v-else color="success" variant="flat" :loading="submitting" @click="submit">
              Finish and show results
            </v-btn>
          </div>
        </div>
      </v-card>
    </template>

    <template v-else-if="showResults && results">
      <v-card class="glass-card pa-6" variant="flat">
        <div class="d-flex align-center justify-space-between flex-wrap gap-2 mb-4">
          <div>
            <div class="text-h6 font-weight-bold">Placement result</div>
            <div class="text-caption text-medium-emphasis">methodology: {{ results.overall_calculation_method || 'bottleneck' }}</div>
          </div>
          <v-chip color="secondary" variant="flat">
            General level: {{ results.overall_level || '—' }}
          </v-chip>
        </div>

        <v-row class='mb-2'>
          <v-col v-for="s in skillResults" :key="s.skill" cols="6" sm="3">
            <div class="skill-level-box text-center pa-3 rounded-lg">
              <div class="text-caption text-medium-emphasis">{{ s.label }}</div>
              <div class="text-h6 font-weight-bold text-secondary">{{ s.level || '—' }}</div>
            </div>
          </v-col>
        </v-row>

        <v-row class='mb-2'>
          <v-col cols="12" sm="6" v-if="access?.levels?.strength_label_ar">
            <v-alert type="success" variant="tonal" density="comfortable">
              <strong>Power point:</strong> {{ access.levels.strength_label_ar }}
            </v-alert>
          </v-col>
          <v-col cols="12" sm="6" v-if="access?.levels?.primary_focus_label_ar">
            <v-alert type="info" variant="tonal" density="comfortable">
              <strong>Focus axis:</strong> {{ access.levels.primary_focus_label_ar }}
            </v-alert>
          </v-col>
        </v-row>

        <v-alert type="info" variant="tonal" class="mb-4">
          <div class="text-body-2">
            <strong>Estimated duration of the route:</strong> {{ estimatedPathDurationLabel }}
          </div>
          <div class="text-caption text-medium-emphasis mt-1">
            (Initial estimate — It will be optimized in the learning panel)
          </div>
        </v-alert>

        <div class="d-flex gap-2 flex-wrap">
          <v-btn color="secondary" variant="flat" @click="startJourney">Start your learning journey</v-btn>
          <v-btn variant="tonal" @click="backToHub">Return</v-btn>
        </div>
      </v-card>
    </template>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import PageHeader from '../../../components/common/PageHeader.vue'
import LoadingState from '../../../components/common/LoadingState.vue'
import { getErrorMessage } from '../../../api/client.js'
import {
  placementStartApi,
  placementSaveResponseApi,
  placementSubmitApi,
  placementUploadSpeakingApi,
  fetchLanguageAccess,
  fetchLanguageHub,
} from '../../../api/language.js'
import { ROUTES } from '../../../constants/app.js'
import {
  countWritingSentences,
  countWritingWords,
  validateWritingText,
} from '../../../utils/languageValidation.js'

const router = useRouter()

const loading = ref(true)
const loadError = ref('')
const state = ref(null)
const submitting = ref(false)
const showResults = ref(false)
const results = ref(null)
const access = ref(null)

const steps = [
  { key: 'reading', label: 'Reading' },
  { key: 'listening', label: 'Listen' },
  { key: 'writing', label: 'Writing' },
  { key: 'speaking', label: 'Speaking' },
]

const activeStep = ref('reading')
const stepIndex = computed(() => steps.findIndex((s) => s.key === activeStep.value))
const cursorByStep = ref({ reading: 0, listening: 0, writing: 0, speaking: 0 })

const totalQuestions = computed(() => state.value?.questions?.length || 0)
const responses = computed(() => state.value?.responses_by_question_id || {})

const questionsByStep = computed(() => {
  const out = { reading: [], listening: [], writing: [], speaking: [] }
  for (const q of state.value?.questions || []) {
    const sec = (state.value?.sections || []).find((s) => s.id === q.section_id)
    const skill = sec?.skill
    if (skill && out[skill]) out[skill].push(q)
  }
  return out
})

const currentStepQuestions = computed(() => questionsByStep.value[activeStep.value] || [])
const currentIndexInStep = computed(() => cursorByStep.value[activeStep.value] || 0)
const currentQuestion = computed(() => currentStepQuestions.value[currentIndexInStep.value] || null)

const stepLabel = computed(() => steps.find((s) => s.key === activeStep.value)?.label || '')
const questionTitle = computed(() => stepLabel.value)

const currentStem = computed(() => currentQuestion.value?.prompt?.stem || currentQuestion.value?.prompt?.prompt || '')
const currentChoices = computed(() => currentQuestion.value?.prompt?.choices || [])

const isMcq = computed(() => ['mcq', 'mcq_listening'].includes(currentQuestion.value?.question_type))
const isWriting = computed(() => currentQuestion.value?.question_type === 'writing')
const isSpeaking = computed(() => currentQuestion.value?.question_type === 'speaking')

const writingHint = computed(() => {
  const minWords = currentQuestion.value?.prompt?.min_words
  const minSentences = currentQuestion.value?.prompt?.min_sentences
  if (!minWords) return ''
  const parts = [`Minimum ${minWords} words required.`]
  if (minSentences) parts.push(`${minSentences} sentences minimum`)
  return parts.join(' · ')
})

const writingWordCount = computed(() => countWritingWords(textValue.value))
const writingSentenceCount = computed(() => countWritingSentences(textValue.value))

const mcqValue = ref(null)
const textValue = ref('')
const speakingMediaUrl = ref(null)
const speakingSaved = ref(false)

const stepAnsweredCount = computed(() => {
  const out = { reading: 0, listening: 0, writing: 0, speaking: 0 }
  for (const q of state.value?.questions || []) {
    const sec = (state.value?.sections || []).find((s) => s.id === q.section_id)
    const skill = sec?.skill
    const r = responses.value?.[q.id]
    if (!skill || !r) continue
    if (r.selected_index != null || r.text || r.media_object_id) out[skill] += 1
  }
  return out
})

const totalAnswered = computed(() => Object.values(stepAnsweredCount.value).reduce((a, b) => a + b, 0))
const overallProgress = computed(() => (totalQuestions.value ? Math.round((totalAnswered.value / totalQuestions.value) * 100) : 0))

const isFirst = computed(() => stepIndex.value === 0 && currentIndexInStep.value === 0)
const isLast = computed(() => stepIndex.value === steps.length - 1 && currentIndexInStep.value >= currentStepQuestions.value.length - 1)

function syncInputsFromSaved() {
  const q = currentQuestion.value
  if (!q) return
  const saved = responses.value?.[q.id] || {}
  mcqValue.value = saved.selected_index ?? saved.answer ?? null
  textValue.value = saved.text ?? saved.answer ?? ''
  // Fresh in-session playback URL isn't persisted, but flag that a recording already exists
  // so revisiting a speaking question shows it was answered instead of looking blank.
  speakingMediaUrl.value = null
  speakingSaved.value = !!saved.media_object_id
}

watch(currentQuestion, syncInputsFromSaved, { immediate: true })

let dirty = false
function markDirty() {
  dirty = true
}

async function autosaveMcq() {
  markDirty()
  const q = currentQuestion.value
  if (!q) return
  await safeSave({ selected_index: mcqValue.value })
}

async function autosaveText() {
  markDirty()
  const q = currentQuestion.value
  if (!q) return
  await safeSave({ text: textValue.value })
}

async function safeSave(payload) {
  const q = currentQuestion.value
  const attemptId = state.value?.attempt?.id
  if (!q || !attemptId) return
  try {
    await placementSaveResponseApi({
      attempt_id: attemptId,
      question_id: q.id,
      response_json: payload,
    })
    state.value.responses_by_question_id[q.id] = payload
    dirty = false
  } catch (e) {
    // do not block flow; show only lightweight message
    loadError.value = getErrorMessage(e, 'Unable to Save Answer')
  }
}

function validateCurrentWriting() {
  if (!isWriting.value || !currentQuestion.value) return true
  // Empty writing is an allowed skip (the backend scores a skipped task 0 and never blocks
  // submission). Only validate when the learner actually typed an answer — otherwise a learner
  // who cannot meet the minimum would be trapped and could never finish the test.
  if (!textValue.value.trim()) {
    loadError.value = ''
    return true
  }
  const minWords = Number(currentQuestion.value?.prompt?.min_words || 20)
  const minSentences = Number(currentQuestion.value?.prompt?.min_sentences || 0)
  const check = validateWritingText(textValue.value, { minWords, minSentences })
  if (!check.ok) {
    loadError.value = check.message
    return false
  }
  loadError.value = ''
  return true
}

async function next() {
  if (isWriting.value) {
    await autosaveText()
    if (!validateCurrentWriting()) return
  }
  const idx = currentIndexInStep.value
  if (idx < currentStepQuestions.value.length - 1) {
    cursorByStep.value[activeStep.value] = idx + 1
    return
  }
  if (stepIndex.value < steps.length - 1) {
    activeStep.value = steps[stepIndex.value + 1].key
  }
}

function prev() {
  const idx = currentIndexInStep.value
  if (idx > 0) {
    cursorByStep.value[activeStep.value] = idx - 1
    return
  }
  if (stepIndex.value > 0) {
    activeStep.value = steps[stepIndex.value - 1].key
  }
}

async function submit() {
  if (isWriting.value && !validateCurrentWriting()) return
  submitting.value = true
  loadError.value = ''
  try {
    const res = await placementSubmitApi(state.value.attempt.id)
    results.value = res
    showResults.value = true
    try {
      access.value = await fetchLanguageAccess()
    } catch {
      access.value = null
    }
  } catch (e) {
    loadError.value = getErrorMessage(e, 'The placement test could not be completed')
  } finally {
    submitting.value = false
  }
}

// Speaking recording (MediaRecorder) + upload
const recording = ref(false)
const uploadingAudio = ref(false)
const speakingFileInput = ref(null)
let mediaRecorder = null
let chunks = []
let recordStartedAt = 0

function triggerSpeakingUpload() {
  speakingFileInput.value?.click()
}

function getAudioDuration(file) {
  return new Promise((resolve) => {
    try {
      const url = URL.createObjectURL(file)
      const a = new Audio()
      a.preload = 'metadata'
      a.onloadedmetadata = () => {
        URL.revokeObjectURL(url)
        const d = Number.isFinite(a.duration) ? Math.max(1, Math.round(a.duration)) : null
        resolve(d)
      }
      a.onerror = () => {
        URL.revokeObjectURL(url)
        resolve(null)
      }
      a.src = url
    } catch {
      resolve(null)
    }
  })
}

async function onSpeakingFilePicked(e) {
  const file = e.target.files?.[0]
  e.target.value = '' // allow re-picking the same file
  if (!file) return
  if (!String(file.type || '').startsWith('audio/')) {
    loadError.value = 'Please choose an audio file.'
    return
  }
  const minSeconds = Number(currentQuestion.value?.prompt?.min_seconds || 20)
  const dur = await getAudioDuration(file)
  if (dur != null && dur < minSeconds) {
    loadError.value = `Minimum ${minSeconds} seconds required. Your file is ${dur}s — please choose a longer recording.`
    return
  }
  loadError.value = ''
  // Unknown duration falls back to the minimum so it passes validation and scores fairly.
  await uploadSpeaking(file, dur ?? minSeconds)
}

function pickAudioMime() {
  const candidates = ['audio/webm', 'audio/mp4', 'audio/ogg']
  for (const t of candidates) {
    if (typeof MediaRecorder !== 'undefined' && MediaRecorder.isTypeSupported?.(t)) return t
  }
  return ''
}

async function startRecording() {
  const q = currentQuestion.value
  if (!q) return
  let stream = null
  try {
    stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    chunks = []
    const mime = pickAudioMime()
    mediaRecorder = new MediaRecorder(stream, mime ? { mimeType: mime } : undefined)
    mediaRecorder.ondataavailable = (e) => {
      if (e.data && e.data.size) chunks.push(e.data)
    }
    mediaRecorder.onstop = async () => {
      const durationSeconds = Math.max(1, Math.round((Date.now() - recordStartedAt) / 1000))
      stream.getTracks().forEach((t) => t.stop())
      const blob = new Blob(chunks, { type: mediaRecorder?.mimeType || mime || 'audio/webm' })
      const minSeconds = Number(currentQuestion.value?.prompt?.min_seconds || 20)
      if (durationSeconds < minSeconds) {
        loadError.value = `Minimum ${minSeconds} seconds required. Your recording was ${durationSeconds}s — please record again.`
        return
      }
      await uploadSpeaking(blob, durationSeconds)
    }
    recordStartedAt = Date.now()
    mediaRecorder.start()
    recording.value = true
  } catch (e) {
    stream?.getTracks().forEach((t) => t.stop())
    loadError.value = getErrorMessage(e, 'Unable to start recording')
  }
}

function stopRecording() {
  if (mediaRecorder && recording.value) {
    mediaRecorder.stop()
    recording.value = false
  }
}

async function uploadSpeaking(blob, durationSeconds) {
  const attemptId = state.value?.attempt?.id
  const q = currentQuestion.value
  if (!attemptId || !q) return
  uploadingAudio.value = true
  try {
    const res = await placementUploadSpeakingApi({ attemptId, questionId: q.id, blob, durationSeconds })
    speakingMediaUrl.value = res.public_url || null
    speakingSaved.value = true
    state.value.responses_by_question_id[q.id] = {
      media_object_id: res.media_object_id,
      duration_seconds: durationSeconds,
    }
    dirty = false
  } catch (e) {
    loadError.value = getErrorMessage(e, 'The recording could not be uploaded')
  } finally {
    uploadingAudio.value = false
  }
}

function beforeUnloadHandler(e) {
  if (!dirty) return
  e.preventDefault()
  e.returnValue = ''
}

onMounted(async () => {
  window.addEventListener('beforeunload', beforeUnloadHandler)
  const wantsResults = router.currentRoute.value?.query?.results === '1'
  try {
    if (wantsResults) {
      access.value = await fetchLanguageAccess()
      if (access.value?.placement_completed) {
        const hub = await fetchLanguageHub()
        const lv = access.value.levels || {}
        results.value = {
          overall_level: hub?.placement?.overall_level || hub?.levels?.overall,
          overall_calculation_method: 'bottleneck',
          skills: ['reading', 'listening', 'writing', 'speaking'].map((skill) => ({
            skill,
            level: lv[skill] || null,
          })),
        }
        showResults.value = true
        return
      }
    }
    const data = await placementStartApi()
    state.value = data
  } catch (e) {
    const msg = getErrorMessage(e, 'The placement test could not be started')
    loadError.value = msg
    if (wantsResults) {
      try {
        access.value = await fetchLanguageAccess()
        if (access.value?.placement_completed) {
          const hub = await fetchLanguageHub()
          const lv = access.value.levels || {}
          results.value = {
            overall_level: hub?.placement?.overall_level || hub?.levels?.overall,
            overall_calculation_method: 'bottleneck',
            skills: ['reading', 'listening', 'writing', 'speaking'].map((skill) => ({
              skill,
              level: lv[skill] || null,
            })),
          }
          showResults.value = true
          return
        }
      } catch {
        /* fall through to hub redirect */
      }
    }
    router.push(ROUTES.STUDENT_LANGUAGES)
  } finally {
    loading.value = false
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('beforeunload', beforeUnloadHandler)
})

// Also guard route-leave.
const removeGuard = router.beforeEach((to, from, nextFn) => {
  if (from.path.includes('/student/languages/placement') && dirty) {
    const ok = window.confirm('You have unsaved answers. Do you want to leave?')
    if (!ok) return nextFn(false)
  }
  nextFn()
})

onBeforeUnmount(() => {
  try { removeGuard() } catch {}
})

const skillResults = computed(() => {
  const map = {
    reading: 'Reading',
    listening: 'Listen',
    writing: 'Writing',
    speaking: 'Speaking',
  }
  const rows = results.value?.skills || []
  return ['reading', 'listening', 'writing', 'speaking'].map((k) => ({
    skill: k,
    label: map[k],
    level: rows.find((r) => r.skill === k)?.level || null,
  }))
})

const estimatedPathDurationLabel = computed(() => {
  // Phase B estimate: 4 items/week, 20 items default => ~5 weeks
  const items = 20
  const perWeek = 4
  const weeks = Math.max(1, Math.ceil(items / perWeek))
  if (weeks === 1) return 'About one week'
  if (weeks === 2) return 'About two weeks'
  return `about ${weeks} Weeks`
})

function startJourney() {
  router.push(ROUTES.STUDENT_LANGUAGES)
}

function backToHub() {
  router.push(ROUTES.STUDENT_LANGUAGES)
}
</script>

<style scoped>
.page-container {
  max-width: 960px;
  margin: 0 auto;
}
.skill-level-box {
  background: rgba(var(--v-theme-on-surface), 0.04);
  border: 1px solid rgba(var(--v-theme-on-surface), 0.08);
}
</style>

