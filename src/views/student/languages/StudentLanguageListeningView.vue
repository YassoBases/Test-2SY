<template>
  <div class="page-container slide-up-enter-active">
    <PageHeader
      eyebrow="Learn languages"
      eyebrow-icon="mdi-headphones"
      title="Listen"
      subtitle="Listen and answer the questions"
    />
    <LanguageModuleTabs />

    <v-alert v-if="loadError" type="error" variant="tonal" class="mb-4 rounded-lg">{{ loadError }}</v-alert>

    <LoadingState v-if="loading" variant="article" class="mb-6" />

    <!-- GENERATING (fresh, level-tuned clip is being created) -->
    <v-card v-else-if="busy" class="glass-card pa-8" variant="flat">
      <LearningLoader title="Creating a clip at your level…" icon="mdi-headphones" />
    </v-card>

    <!-- INTRO -->
    <v-card v-else-if="!lesson" class="glass-card pa-8 text-center" variant="flat">
      <v-icon size="48" color="secondary" class="mb-3">mdi-headphones</v-icon>
      <h3 class="text-h6 font-weight-bold mb-1">Adaptive listening practice</h3>
      <p class="text-body-2 text-medium-emphasis mb-4">
        Listen to a short clip and answer the questions. The difficulty adapts to you and every answer is explained.
      </p>
      <v-btn color="secondary" variant="flat" size="large" :loading="busy" prepend-icon="mdi-play" @click="loadNext">
        Start listening
      </v-btn>
    </v-card>

    <!-- PRACTICE -->
    <template v-else>
      <div class="d-flex align-center justify-space-between flex-wrap gap-2 mb-3">
        <v-chip
          size="small"
          :color="difficultyUp ? 'success' : 'secondary'"
          :variant="difficultyUp ? 'flat' : 'tonal'"
          :prepend-icon="difficultyUp ? 'mdi-trending-up' : 'mdi-stairs-up'"
        >Level {{ lesson.level }}<span v-if="difficultyUp" class="ml-1 font-weight-bold">· harder</span></v-chip>
        <span class="text-caption text-medium-emphasis">{{ answeredCount }} / {{ lesson.questions.length }} answered</span>
      </div>

      <v-card class="glass-card pa-6 mb-4" variant="flat">
        <div class="text-subtitle-1 font-weight-bold mb-2">{{ lesson.title }}</div>
        <p v-if="lesson.instructions" class="text-body-2 text-medium-emphasis mb-3" dir="ltr">{{ lesson.instructions }}</p>
        <AudioVisualizer
          v-if="lesson.audio_available && lesson.audio_url && !audioBroken"
          :src="lesson.audio_url" @error="onAudioError"
        />
        <v-alert v-else type="info" variant="tonal" density="comfortable" class="mb-0">
          Audio isn't available for this clip right now — you can still answer the questions.
        </v-alert>
      </v-card>

      <v-card v-if="!submitResult" class="glass-card pa-6" variant="flat">
        <LanguageMcqForm v-model:answers="answers" :questions="lesson.questions" />
        <v-btn color="secondary" variant="flat" class="mt-4" block :loading="submitting" :disabled="!canSubmit" @click="submit">
          Submit
        </v-btn>
      </v-card>

      <v-card v-else class="glass-card pa-6" variant="flat">
        <v-alert :type="submitResult.passed ? 'success' : 'warning'" variant="tonal" class="mb-3">
          Result: {{ submitResult.score_percent }}% — {{ submitResult.correct_count }}/{{ submitResult.total_questions }}
        </v-alert>

        <div v-if="weakTypes.length" class="d-flex flex-wrap gap-2 mb-3">
              <v-chip v-for="t in weakTypes" :key="t" size="small" variant="tonal" color="warning" prepend-icon="mdi-target">
                practice: {{ typeLabel(t) }}
              </v-chip>
            </div>

            <!-- per-question results -->
            <div
              v-for="(r, i) in submitResult.question_results || []"
              :key="i"
              class="q-result pa-2 rounded-lg mb-2"
              :class="r.is_correct ? 'ok' : 'bad'"
              dir="ltr"
            >
              <div class="text-caption font-weight-bold mb-1">
                <v-icon size="14" :icon="r.is_correct ? 'mdi-check-circle' : 'mdi-close-circle'" />
                {{ i + 1 }}. {{ typeLabel(r.type) }} — {{ r.is_correct ? 'Correct' : 'Not quite' }}
              </div>
              <div v-if="r.explanation" class="text-caption">{{ r.explanation }}</div>
            </div>

            <!-- revealed transcript with tap-to-save -->
            <div v-if="submitResult.transcript" class="transcript-box pa-3 rounded-lg mt-3">
              <div class="text-caption font-weight-bold text-medium-emphasis mb-1">
                Transcript <span class="font-weight-regular">— tap a word to look it up or save it</span>
              </div>
              <p class="transcript-text" dir="ltr">
                <template v-for="(tok, i) in transcriptTokens" :key="i"><span
                    v-if="tok.word" class="rw" @click="lookup(tok.text)">{{ tok.text }}</span><span v-else>{{ tok.text }}</span></template>
              </p>
            </div>

        <div class="d-flex gap-2 mt-4">
          <v-btn color="secondary" variant="tonal" @click="retry">Retry</v-btn>
          <v-btn color="secondary" variant="flat" prepend-icon="mdi-arrow-right" :loading="busy" @click="loadNext">
            Next clip
          </v-btn>
        </div>
      </v-card>
    </template>

    <v-snackbar v-model="diffSnack" color="success" location="top" :timeout="4500">
      <v-icon start icon="mdi-trending-up" /> Difficulty increased — clips are now <strong class="mx-1">Level {{ diffLevel }}</strong> 🎯
    </v-snackbar>

    <!-- word meaning + save -->
    <v-dialog v-model="wordOpen" max-width="420">
      <v-card class="glass-card pa-4" variant="flat" dir="ltr">
        <div class="d-flex align-center justify-space-between mb-1">
          <span class="text-h6 font-weight-bold">{{ wordData?.word || wordQuery }}</span>
          <v-btn icon="mdi-close" size="x-small" variant="text" @click="wordOpen = false" />
        </div>
        <div v-if="wordLoading" class="text-center py-4"><v-progress-circular indeterminate color="secondary" size="28" /></div>
        <template v-else-if="wordData">
          <div class="d-flex gap-2 mb-2 flex-wrap">
            <v-chip v-if="wordData.part_of_speech" size="x-small" variant="tonal">{{ wordData.part_of_speech }}</v-chip>
            <v-chip v-if="wordData.cefr_level" size="x-small" color="secondary" variant="tonal">{{ wordData.cefr_level }}</v-chip>
          </div>
          <p class="text-body-2 mb-1">{{ wordData.definition }}</p>
          <p v-if="wordData.example_sentence" class="text-body-2 text-medium-emphasis mb-1"><em>{{ wordData.example_sentence }}</em></p>
          <v-btn
            class="mt-3" size="small" block
            :color="isSaved(wordQuery) ? 'success' : 'secondary'"
            :variant="isSaved(wordQuery) ? 'tonal' : 'flat'"
            :loading="savingWord"
            :prepend-icon="isSaved(wordQuery) ? 'mdi-check' : 'mdi-bookmark-plus-outline'"
            :disabled="isSaved(wordQuery)"
            @click="saveCurrentWord"
          >{{ isSaved(wordQuery) ? 'Saved to your words' : 'Save to my words' }}</v-btn>
        </template>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import PageHeader from '../../../components/common/PageHeader.vue'
import LoadingState from '../../../components/common/LoadingState.vue'
import LanguageModuleTabs from '../../../components/language/LanguageModuleTabs.vue'
import LearningLoader from '../../../components/language/LearningLoader.vue'
import LanguageMcqForm from '../../../components/language/LanguageMcqForm.vue'
import AudioVisualizer from '../../../components/language/AudioVisualizer.vue'
import {
  fetchNextListening,
  submitListeningLesson,
  analyzeWord,
  saveVocabularyWord,
} from '../../../api/language.js'
import { useLanguageAccess } from '../../../composables/useLanguageAccess.js'
import { buildSubmitAnswers, useLanguageGate } from '../../../composables/useLanguageGate.js'
import { celebrate, celebrateBig } from '../../../composables/useCelebrate.js'

const { access, loadAccess } = useLanguageAccess()
const { handleLanguageApiError, getErrorMessage } = useLanguageGate()

const router = useRouter()

const loading = ref(true)
const busy = ref(false)
const loadError = ref('')
const lesson = ref(null)
const answers = ref({})
const submitting = ref(false)
const submitResult = ref(null)
const audioBroken = ref(false)

const answeredCount = computed(() =>
  lesson.value ? lesson.value.questions.filter((q) => answers.value[q.id] != null).length : 0,
)

// word lookup + save
const wordOpen = ref(false)
const wordLoading = ref(false)
const wordData = ref(null)
const wordQuery = ref('')
const savingWord = ref(false)
const savedWords = ref(new Set())

const TYPE_LABELS = {
  main_idea: 'Main idea',
  detail: 'Detail',
  inference: 'Inference',
  vocab_in_context: 'Vocabulary',
  true_false_notgiven: 'True / False / Not Given',
  sentence_completion: 'Sentence completion',
}
function typeLabel(t) {
  return TYPE_LABELS[t] || (t || 'Question').replace(/_/g, ' ')
}

const weakTypes = computed(() => {
  const out = []
  for (const r of submitResult.value?.question_results || []) {
    if (!r.is_correct && r.type && !out.includes(r.type)) out.push(r.type)
  }
  return out.slice(0, 3)
})

const transcriptTokens = computed(() => {
  const p = submitResult.value?.transcript || ''
  const re = /([A-Za-z]+(?:'[A-Za-z]+)?)|([^A-Za-z]+)/g
  const out = []
  let m
  while ((m = re.exec(p))) out.push({ text: m[0], word: !!m[1] })
  return out
})

function isSaved(word) {
  return savedWords.value.has((word || '').toLowerCase())
}

async function lookup(word) {
  const clean = (word || '').replace(/[^A-Za-z']/g, '')
  if (!clean) return
  wordQuery.value = clean
  wordData.value = null
  wordOpen.value = true
  wordLoading.value = true
  try {
    wordData.value = await analyzeWord(clean, lesson.value?.level || 'A2')
  } catch {
    wordData.value = { word: clean, definition: 'Could not load the meaning right now.' }
  } finally {
    wordLoading.value = false
  }
}

async function saveCurrentWord() {
  const word = wordQuery.value
  if (!word || isSaved(word) || savingWord.value) return
  savingWord.value = true
  try {
    const res = await saveVocabularyWord(word)
    if (res?.saved) savedWords.value = new Set([...savedWords.value, (res.word || word).toLowerCase()])
  } catch {
    /* non-fatal */
  } finally {
    savingWord.value = false
  }
}

const canSubmit = computed(() => {
  if (!lesson.value?.questions?.length) return false
  return lesson.value.questions.every((q) => answers.value[q.id] !== undefined && answers.value[q.id] !== null)
})

// Cue the learner when listening difficulty stepped up.
const CEFR = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
const diffSnack = ref(false)
const diffLevel = ref('')
const difficultyUp = ref(false)
function _flagDifficulty(level) {
  if (!level) return
  let prev = null
  try {
    prev = localStorage.getItem('listening_seen_level')
  } catch {
    /* storage unavailable */
  }
  difficultyUp.value = !!prev && CEFR.indexOf(level) > CEFR.indexOf(prev)
  if (difficultyUp.value) {
    diffLevel.value = level
    diffSnack.value = true
  }
  try {
    localStorage.setItem('listening_seen_level', level)
  } catch {
    /* storage unavailable */
  }
}

async function loadNext() {
  if (busy.value) return
  busy.value = true
  loadError.value = ''
  try {
    const data = await fetchNextListening()
    lesson.value = data
    _flagDifficulty(data.level)
    answers.value = {}
    submitResult.value = null
    audioBroken.value = false
  } catch (e) {
    if (!handleLanguageApiError(e, access.value)) loadError.value = getErrorMessage(e, 'Could not load a clip')
  } finally {
    busy.value = false
    loading.value = false
  }
}

onMounted(async () => {
  try {
    await loadAccess(true)
    if (access.value?.redirect) {
      router.push(access.value.redirect)
      return
    }
  } catch (e) {
    if (!handleLanguageApiError(e, access.value)) loadError.value = getErrorMessage(e, 'Unable to load listening')
  } finally {
    loading.value = false
  }
})

function onAudioError() {
  audioBroken.value = true
}

async function submit() {
  if (!lesson.value || submitting.value) return
  submitting.value = true
  loadError.value = ''
  try {
    submitResult.value = await submitListeningLesson(lesson.value.id, buildSubmitAnswers(answers.value))
    if (submitResult.value?.score_percent >= 100) celebrateBig()
    else if (submitResult.value?.passed) celebrate()
  } catch (e) {
    if (!handleLanguageApiError(e, access.value)) loadError.value = getErrorMessage(e, 'Unable to submit your answers')
  } finally {
    submitting.value = false
  }
}

function retry() {
  submitResult.value = null
  answers.value = {}
}
</script>

<style scoped>
.page-container {
  max-width: 1100px;
  margin: 0 auto;
}
.q-result.ok { background: rgba(var(--v-theme-success), 0.12); border: 1px solid rgba(var(--v-theme-success), 0.4); animation: okPop 0.55s ease; }
.q-result.bad { background: rgba(var(--v-theme-error), 0.12); border: 1px solid rgba(var(--v-theme-error), 0.4); animation: badShake 0.42s ease; }
@keyframes okPop {
  0% { transform: scale(0.96); box-shadow: 0 0 0 rgba(var(--v-theme-success), 0); }
  55% { transform: scale(1.015); box-shadow: 0 0 22px rgba(var(--v-theme-success), 0.5); }
  100% { transform: scale(1); box-shadow: 0 0 0 rgba(var(--v-theme-success), 0); }
}
@keyframes badShake {
  0%, 100% { transform: translateX(0); }
  20% { transform: translateX(-5px); }
  40% { transform: translateX(5px); }
  60% { transform: translateX(-3px); }
  80% { transform: translateX(3px); }
}
@media (prefers-reduced-motion: reduce) {
  .q-result.ok, .q-result.bad { animation: none; }
}
.transcript-box { background: rgba(var(--v-theme-secondary), 0.06); border: 1px solid rgba(var(--v-theme-secondary), 0.18); }
.transcript-text { line-height: 1.9; }
.rw { cursor: pointer; border-radius: 4px; transition: background 0.1s; }
.rw:hover { background: rgba(var(--v-theme-secondary), 0.18); }
</style>
