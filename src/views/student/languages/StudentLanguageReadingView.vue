<template>
  <div class="page-container slide-up-enter-active">
    <PageHeader
      eyebrow="Learn languages"
      eyebrow-icon="mdi-book-open-page-variant"
      title="Reading"
      subtitle="Adaptive passages that get harder as you improve — tap any word for its meaning"
    />
    <LanguageModuleTabs />

    <v-alert v-if="loadError" type="error" variant="tonal" class="mb-4 rounded-lg">{{ loadError }}</v-alert>

    <LoadingState v-if="loading" variant="article" class="mb-6" />

    <!-- GENERATING (fresh, level-tuned passage is being created) -->
    <v-card v-else-if="generating" class="glass-card pa-8" variant="flat">
      <LearningLoader title="Writing a passage at your level…" icon="mdi-feather" />
    </v-card>

    <!-- INTRO -->
    <v-card v-else-if="!lesson" class="glass-card pa-6" variant="flat">
      <div class="text-center mb-5">
        <v-icon size="48" color="secondary" class="mb-3">mdi-book-open-page-variant</v-icon>
        <h3 class="text-h6 font-weight-bold mb-1">Adaptive reading practice</h3>
        <p class="text-body-2 text-medium-emphasis mb-4">
          Read a short passage and answer 5 questions. We adapt the difficulty to you and explain every answer.
        </p>
        <div class="mb-3">
          <v-chip
            size="small"
            :color="dailyGoalDone ? 'success' : 'secondary'"
            variant="tonal"
            :prepend-icon="dailyGoalDone ? 'mdi-check-circle' : 'mdi-fire'"
          >Today: {{ readToday }} / {{ DAILY_GOAL }} passages{{ dailyGoalDone ? ' — done!' : '' }}</v-chip>
        </div>
        <div class="d-flex align-center justify-center gap-1 mb-4">
          <span class="text-caption text-medium-emphasis me-1">Length:</span>
          <v-chip
            v-for="opt in LENGTH_OPTIONS"
            :key="opt.value"
            size="small"
            :color="readingLength === opt.value ? 'secondary' : undefined"
            :variant="readingLength === opt.value ? 'flat' : 'outlined'"
            @click="readingLength = opt.value"
          >{{ opt.label }}</v-chip>
        </div>
        <v-btn color="secondary" variant="flat" size="large" :loading="busy" prepend-icon="mdi-play" @click="loadNext">
          Start reading
        </v-btn>
      </div>

      <!-- reading insights -->
      <div v-if="insights && insights.lessons_completed" class="insights-box pa-3 rounded-lg mb-4" dir="ltr">
        <div class="text-caption font-weight-bold text-medium-emphasis mb-2">Your reading</div>
        <div class="d-flex flex-wrap gap-4 mb-2">
          <div v-if="insights.avg_wpm" class="text-center">
            <div class="text-h6 font-weight-bold">{{ insights.avg_wpm }}</div>
            <div class="text-caption text-medium-emphasis">avg wpm</div>
          </div>
          <div v-if="insights.best_wpm" class="text-center">
            <div class="text-h6 font-weight-bold">{{ insights.best_wpm }}</div>
            <div class="text-caption text-medium-emphasis">best wpm</div>
          </div>
          <div v-if="insights.avg_comprehension != null" class="text-center">
            <div class="text-h6 font-weight-bold">{{ Math.round(insights.avg_comprehension) }}%</div>
            <div class="text-caption text-medium-emphasis">comprehension</div>
          </div>
          <div class="text-center">
            <div class="text-h6 font-weight-bold">{{ insights.lessons_completed }}</div>
            <div class="text-caption text-medium-emphasis">passages</div>
          </div>
        </div>
        <div v-if="insights.wpm_recent?.length > 1" class="d-flex align-end gap-1 mb-2" style="height: 34px">
          <div v-for="(w, i) in insights.wpm_recent" :key="i" class="wpm-bar" :style="{ height: barHeight(w) }" :title="`${w} wpm`" />
        </div>
        <div v-if="insights.weak_skills?.length" class="d-flex flex-wrap gap-1 align-center">
          <span class="text-caption text-medium-emphasis me-1">Work on:</span>
          <v-chip v-for="s in insights.weak_skills" :key="s.code" size="x-small" variant="tonal" color="warning">
            {{ prettySkill(s.code) }} · {{ s.mastery }}%
          </v-chip>
        </div>
      </div>

      <!-- interests -->
      <div v-if="topicOptions.length" class="mb-4">
        <div class="text-caption font-weight-bold text-medium-emphasis mb-1">
          Your interests <span class="font-weight-regular">— we'll lean new passages this way</span>
        </div>
        <div class="d-flex flex-wrap gap-1">
          <v-chip
            v-for="t in topicOptions"
            :key="t"
            size="small"
            :color="selectedTopics.includes(t) ? 'secondary' : undefined"
            :variant="selectedTopics.includes(t) ? 'flat' : 'outlined'"
            @click="toggleTopic(t)"
          >{{ t }}</v-chip>
        </div>
      </div>

      <!-- library -->
      <div v-if="history.length">
        <div class="text-caption font-weight-bold text-medium-emphasis mb-1">Your library</div>
        <v-list density="compact" class="rounded-lg" bg-color="transparent">
          <v-list-item v-for="h in history" :key="h.id" class="px-2 lib-item" @click="reread(h.id)">
            <v-list-item-title dir="ltr">{{ h.title }}</v-list-item-title>
            <template #append>
              <v-chip size="x-small" variant="tonal" class="me-2">{{ h.level }}</v-chip>
              <span v-if="h.score_percent != null" class="text-caption">{{ Math.round(h.score_percent) }}%</span>
            </template>
          </v-list-item>
        </v-list>
      </div>
    </v-card>

    <!-- PRACTICE -->
    <template v-else>
      <div class="d-flex align-center justify-space-between flex-wrap gap-2 mb-3">
        <div class="d-flex align-center gap-2">
          <v-btn size="x-small" variant="text" prepend-icon="mdi-bookshelf" @click="backToLibrary">Library</v-btn>
          <v-chip
            size="small"
            :color="difficultyUp ? 'success' : 'secondary'"
            :variant="difficultyUp ? 'flat' : 'tonal'"
            :prepend-icon="difficultyUp ? 'mdi-trending-up' : 'mdi-stairs-up'"
          >Level {{ lesson.level }}<span v-if="difficultyUp" class="ml-1 font-weight-bold">· harder</span></v-chip>
        </div>
        <span class="text-caption text-medium-emphasis">{{ answeredCount }} / {{ lesson.questions.length }} answered</span>
      </div>

      <v-row>
        <!-- PASSAGE -->
        <v-col cols="12" md="7">
          <v-card class="glass-card pa-5 passage-card" variant="flat">
            <div class="d-flex align-center justify-space-between gap-2 mb-1">
              <div class="text-subtitle-1 font-weight-bold">{{ lesson.title }}</div>
              <div class="d-flex gap-1">
                <v-btn
                  size="x-small" variant="tonal" color="secondary"
                  prepend-icon="mdi-fullscreen" @click="zen = true"
                >Focus</v-btn>
                <v-btn
                  size="x-small" variant="tonal" color="secondary"
                  prepend-icon="mdi-marker" @click="saveSelection"
                >Highlight</v-btn>
                <v-btn
                  size="x-small" variant="tonal" color="secondary"
                  prepend-icon="mdi-form-textbox" @click="openCloze"
                >Cloze</v-btn>
                <v-btn
                  size="x-small" variant="tonal" color="secondary"
                  prepend-icon="mdi-speedometer" @click="openPacer"
                >Speed</v-btn>
                <v-btn
                  size="x-small" variant="tonal" color="secondary" :loading="audioBusy"
                  :prepend-icon="audioUrl ? 'mdi-volume-high' : 'mdi-headphones'"
                  @click="toggleAudio"
                >{{ audioUrl ? 'Listen' : 'Narrate' }}</v-btn>
              </div>
            </div>
            <audio
              v-if="audioUrl" ref="audioEl" :src="audioUrl" controls class="w-100 mb-2"
              @timeupdate="onAudioTime" @ended="clearKaraoke" @pause="clearKaraoke"
            />

            <!-- pre-teach glossary -->
            <div v-if="lesson.glossary?.length" class="glossary-box pa-3 rounded-lg mb-3" dir="ltr">
              <div class="text-caption font-weight-bold text-medium-emphasis mb-1">Key words before you read</div>
              <div v-for="(g, i) in lesson.glossary" :key="i" class="text-body-2">
                <strong>{{ g.word }}</strong><span v-if="g.definition"> — {{ g.definition }}</span>
              </div>
            </div>

            <div class="d-flex align-center justify-space-between flex-wrap gap-2 mb-2">
              <p class="text-caption text-medium-emphasis mb-0">
                {{ tapMode === 'word' ? 'Tap a word to see its meaning.' : 'Tap a sentence to have it explained.' }}
              </p>
              <v-btn-toggle v-model="tapMode" density="compact" mandatory variant="outlined" divided>
                <v-btn size="x-small" value="word">Words</v-btn>
                <v-btn size="x-small" value="sentence">Sentences</v-btn>
              </v-btn-toggle>
            </div>

            <p v-if="tapMode === 'word'" class="reading-passage" dir="ltr">
              <template v-for="(tok, i) in tokens" :key="i"><span
                  v-if="tok.word"
                  class="rw"
                  :class="{ 'rw--hl': isHighlighted(tok), 'rw--karaoke': tok.wordIndex === karaokeWordIndex }"
                  @click="lookup(tok.text)"
                >{{ tok.text }}</span><span v-else :class="{ 'rw--hl': isHighlighted(tok) }">{{ tok.text }}</span></template>
            </p>
            <p v-else class="reading-passage" dir="ltr">
              <span
                v-for="(s, i) in sentences"
                :key="i"
                class="rs"
                @click="explainSentence(s)"
              >{{ s }} </span>
            </p>
          </v-card>

          <!-- highlights + notes (saved per passage) -->
          <v-card v-if="highlights.length" class="glass-card pa-4 mt-3" variant="flat" dir="ltr">
            <div class="text-caption font-weight-bold text-medium-emphasis mb-2">
              <v-icon size="14" icon="mdi-marker" /> Your highlights
            </div>
            <div v-for="(h, i) in highlights" :key="i" class="hl-item pa-2 rounded-lg mb-2">
              <div class="d-flex align-start justify-space-between gap-2">
                <span class="text-body-2 hl-text">“{{ h.text }}”</span>
                <v-btn icon="mdi-close" size="x-small" variant="text" @click="removeHighlight(i)" />
              </div>
              <v-text-field
                v-model="h.note" placeholder="Add a note…" density="compact" variant="plain" hide-details
                class="hl-note" @blur="persistHighlights"
              />
            </div>
          </v-card>
        </v-col>

        <!-- QUESTIONS -->
        <v-col cols="12" md="5">
          <v-card class="glass-card pa-5" variant="flat">
            <div
              v-for="(q, qi) in lesson.questions"
              :key="q.id"
              class="q-block mb-4"
              :class="{ 'q-block--active': activeQid === q.id }"
            >
              <div class="text-caption text-medium-emphasis mb-1">
                {{ qi + 1 }}. <span>{{ typeLabel(q.type) }}</span>
              </div>
              <p class="text-body-2 font-weight-medium mb-2" dir="ltr">{{ q.stem }}</p>
              <v-radio-group v-model="answers[q.id]" hide-details density="compact" :disabled="submitted" class="mb-1">
                <v-radio
                  v-for="(opt, oi) in q.choices" :key="oi" :value="oi" :label="opt" dir="ltr"
                  :color="optionColor(q, oi)"
                />
              </v-radio-group>

              <!-- per-question result -->
              <div v-if="resultFor(q.id)" class="q-result pa-2 rounded-lg mt-1" :class="resultFor(q.id).is_correct ? 'ok' : 'bad'">
                <div class="text-caption font-weight-bold mb-1">
                  <v-icon size="14" :icon="resultFor(q.id).is_correct ? 'mdi-check-circle' : 'mdi-close-circle'" />
                  {{ resultFor(q.id).is_correct ? 'Correct' : 'Not quite' }}
                </div>
                <div v-if="resultFor(q.id).explanation" class="text-caption mb-1" dir="ltr">{{ resultFor(q.id).explanation }}</div>
                <v-btn
                  v-if="resultFor(q.id).evidence_quote"
                  size="x-small" variant="text" color="secondary" prepend-icon="mdi-text-search"
                  @click="showEvidence(q.id, resultFor(q.id).evidence_quote)"
                >Show in text</v-btn>
              </div>
            </div>

            <v-btn
              v-if="!submitted"
              color="secondary" variant="flat" block :loading="busy" :disabled="answeredCount < lesson.questions.length"
              @click="submit"
            >Submit</v-btn>

            <template v-else>
              <v-alert :type="result.passed ? 'success' : 'warning'" variant="tonal" density="comfortable" class="mb-2">
                {{ result.score_percent }}% — {{ result.correct_count }}/{{ result.total_questions }}
                <span v-if="result.passed"> · passed 🎉</span>
              </v-alert>

              <div class="d-flex flex-wrap gap-2 mb-3">
                <v-chip v-if="result.reading_wpm" size="small" variant="tonal" color="info" prepend-icon="mdi-speedometer">
                  {{ result.reading_wpm }} words/min
                </v-chip>
                <v-chip v-for="t in weakTypes" :key="t" size="small" variant="tonal" color="warning" prepend-icon="mdi-target">
                  practice: {{ typeLabel(t) }}
                </v-chip>
              </div>

              <!-- Summary-writing comprehension -->
              <div class="summary-box pa-3 rounded-lg mb-3">
                <div class="text-caption font-weight-bold mb-1">
                  <v-icon size="14" icon="mdi-text-box-edit-outline" /> Summarise it in your own words
                </div>
                <v-textarea
                  v-model="summaryText" rows="3" density="compact" variant="outlined" hide-details
                  placeholder="Write 1-2 sentences about the main idea…" dir="ltr" :disabled="summaryBusy || !!summaryResult"
                />
                <v-btn
                  v-if="!summaryResult"
                  class="mt-2" size="small" color="secondary" variant="flat"
                  :loading="summaryBusy" :disabled="summaryText.trim().length < 3" @click="checkSummary"
                >Check my summary</v-btn>
                <div v-else class="mt-2">
                  <v-chip size="small" :color="summaryResult.score_percent >= 60 ? 'success' : 'warning'" variant="tonal" class="mb-1">
                    Comprehension {{ Math.round(summaryResult.score_percent) }}%
                  </v-chip>
                  <p v-if="summaryResult.feedback" class="text-body-2 mb-1" dir="ltr">{{ summaryResult.feedback }}</p>
                  <div v-if="summaryResult.missed_points?.length" class="text-caption" dir="ltr">
                    <span class="text-medium-emphasis">You missed:</span> {{ summaryResult.missed_points.join('; ') }}
                  </div>
                </div>
              </div>

              <v-btn color="secondary" variant="flat" block :loading="busy" prepend-icon="mdi-arrow-right" @click="loadNext">
                Next passage
              </v-btn>
            </template>
          </v-card>
        </v-col>
      </v-row>
    </template>

    <!-- word meaning -->
    <v-dialog v-model="wordOpen" max-width="420">
      <v-card class="glass-card pa-4" variant="flat" dir="ltr">
        <div class="d-flex align-center justify-space-between mb-1">
          <span class="text-h6 font-weight-bold">{{ wordData?.word || wordQuery }}</span>
          <v-btn icon="mdi-close" size="x-small" variant="text" @click="wordOpen = false" />
        </div>
        <div v-if="wordLoading" class="py-2"><LearningLoader compact :title="''" icon="mdi-book-search" /></div>
        <template v-else-if="wordData">
          <div class="d-flex gap-2 mb-2 flex-wrap">
            <v-chip v-if="wordData.part_of_speech" size="x-small" variant="tonal">{{ wordData.part_of_speech }}</v-chip>
            <v-chip v-if="wordData.cefr_level" size="x-small" color="secondary" variant="tonal">{{ wordData.cefr_level }}</v-chip>
          </div>
          <p class="text-body-2 mb-1">{{ wordData.definition }}</p>
          <p v-if="wordData.example_sentence" class="text-body-2 text-medium-emphasis mb-1"><em>{{ wordData.example_sentence }}</em></p>
          <div v-if="wordData.pronunciation_tip" class="text-caption text-medium-emphasis">🔊 {{ wordData.pronunciation_tip }}</div>
          <div v-if="wordData.synonyms?.length" class="d-flex flex-wrap gap-1 mt-2">
            <v-chip v-for="(s, i) in wordData.synonyms" :key="i" size="x-small" variant="outlined">{{ s }}</v-chip>
          </div>
          <v-btn
            class="mt-3"
            size="small"
            block
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

    <!-- Zen / focus reading mode -->
    <Teleport to="body">
      <Transition name="zen-fade">
        <div v-if="zen && lesson" class="zen-overlay">
          <div class="zen-top">
            <v-chip size="small" variant="tonal" color="secondary">{{ lesson.level }}</v-chip>
            <v-btn icon="mdi-close" variant="text" @click="zen = false" />
          </div>
          <div class="zen-body">
            <h2 class="zen-title" dir="ltr">{{ lesson.title }}</h2>
            <p class="zen-text" dir="ltr">
              <template v-for="(tok, i) in tokens" :key="i"><span
                  v-if="tok.word" class="rw" @click="lookup(tok.text)">{{ tok.text }}</span><span v-else>{{ tok.text }}</span></template>
            </p>
          </div>
        </div>
      </Transition>
    </Teleport>

    <v-snackbar v-model="diffSnack" color="success" location="top" :timeout="4500">
      <v-icon start icon="mdi-trending-up" /> Difficulty increased — passages are now <strong class="mx-1">Level {{ diffLevel }}</strong> 🎯
    </v-snackbar>

    <!-- sentence explanation -->
    <v-dialog v-model="sentenceOpen" max-width="480">
      <v-card class="glass-card pa-4" variant="flat" dir="ltr">
        <div class="d-flex align-center justify-space-between mb-2">
          <span class="text-subtitle-2 font-weight-bold">Sentence explained</span>
          <v-btn icon="mdi-close" size="x-small" variant="text" @click="sentenceOpen = false" />
        </div>
        <p class="text-body-2 font-italic text-medium-emphasis mb-3">"{{ sentenceQuery }}"</p>
        <div v-if="sentenceLoading" class="text-center py-4"><v-progress-circular indeterminate color="secondary" size="28" /></div>
        <p v-else class="text-body-2" style="white-space: pre-line">{{ sentenceExplanation }}</p>
      </v-card>
    </v-dialog>

    <!-- speed trainer (RSVP) -->
    <v-dialog v-model="pacerOpen" max-width="560">
      <v-card class="glass-card pa-6 text-center" variant="flat" dir="ltr">
        <div class="d-flex align-center justify-space-between mb-2">
          <span class="text-subtitle-2 font-weight-bold">Speed trainer</span>
          <v-btn icon="mdi-close" size="x-small" variant="text" @click="pacerOpen = false" />
        </div>
        <div class="pacer-word">{{ pacerWords[pacerIndex] || (pacerIndex >= pacerWords.length ? 'Done ✓' : '—') }}</div>
        <v-progress-linear :model-value="pacerProgress" color="secondary" height="6" rounded class="my-3" />
        <div class="d-flex align-center justify-center gap-1 mb-3">
          <span class="text-caption text-medium-emphasis me-1">Speed:</span>
          <v-chip
            v-for="w in [150, 250, 350, 450]"
            :key="w"
            size="x-small"
            :color="pacerWpm === w ? 'secondary' : undefined"
            :variant="pacerWpm === w ? 'flat' : 'outlined'"
            @click="setPacerWpm(w)"
          >{{ w }}</v-chip>
          <span class="text-caption text-medium-emphasis ms-1">wpm</span>
        </div>
        <div class="d-flex justify-center gap-2">
          <v-btn size="small" color="secondary" variant="flat" :prepend-icon="pacerRunning ? 'mdi-pause' : 'mdi-play'" @click="togglePacer">
            {{ pacerRunning ? 'Pause' : (pacerIndex >= pacerWords.length ? 'Restart' : 'Play') }}
          </v-btn>
          <v-btn size="small" variant="tonal" prepend-icon="mdi-restart" @click="restartPacer">Restart</v-btn>
        </div>
      </v-card>
    </v-dialog>

    <!-- cloze (fill the gaps) -->
    <v-dialog v-model="clozeOpen" max-width="640" scrollable>
      <v-card class="glass-card pa-5" variant="flat" dir="ltr">
        <div class="d-flex align-center justify-space-between mb-2">
          <span class="text-subtitle-2 font-weight-bold">Fill the gaps</span>
          <v-btn icon="mdi-close" size="x-small" variant="text" @click="clozeOpen = false" />
        </div>
        <p v-if="!clozeHasBlanks" class="text-body-2 text-medium-emphasis">This passage is too short for a gap exercise.</p>
        <template v-else>
          <p class="reading-passage" style="line-height: 2.4">
            <template v-for="(tok, i) in tokens" :key="i"><select
                v-if="clozeBlanks[i] !== undefined"
                v-model="clozeAnswers[i]"
                class="blank-select"
                :class="clozeChecked ? (clozeAnswers[i] === clozeBlanks[i] ? 'ok' : 'bad') : ''"
              ><option value="">— ? —</option><option v-for="(o, oi) in clozeOptions" :key="oi" :value="o">{{ o }}</option></select><span v-else>{{ tok.text }}</span></template>
          </p>
          <div class="d-flex align-center gap-3 mt-3">
            <v-btn size="small" color="secondary" variant="flat" @click="checkCloze">Check</v-btn>
            <span v-if="clozeChecked" class="text-body-2 font-weight-bold" :class="clozeScore === clozeTotal ? 'text-success' : 'text-warning'">
              {{ clozeScore }} / {{ clozeTotal }} correct
            </span>
          </div>
        </template>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import PageHeader from '../../../components/common/PageHeader.vue'
import LoadingState from '../../../components/common/LoadingState.vue'
import LanguageModuleTabs from '../../../components/language/LanguageModuleTabs.vue'
import LearningLoader from '../../../components/language/LearningLoader.vue'
import {
  fetchNextReading,
  fetchReadingGlossary,
  fetchReadingLesson,
  submitReadingLesson,
  analyzeWord,
  fetchReadingAudio,
  submitReadingSummary,
  saveVocabularyWord,
  fetchReadingTopics,
  saveReadingTopics,
  fetchReadingHistory,
  fetchReadingInsights,
  explainReadingSentence,
} from '../../../api/language.js'
import { celebrate, celebrateBig } from '../../../composables/useCelebrate.js'
import { useLanguageGate } from '../../../composables/useLanguageGate.js'
import { useLanguageAccess } from '../../../composables/useLanguageAccess.js'

const { access, loadAccess } = useLanguageAccess()
const { handleLanguageApiError, getErrorMessage } = useLanguageGate()

const loading = ref(true)
const busy = ref(false)
const generating = ref(false)
const loadError = ref('')
const lesson = ref(null)
const answers = reactive({})
const submitted = ref(false)
const result = ref(null)
const activeQid = ref(null)
const activeEvidence = ref('')

// word lookup + save
const wordOpen = ref(false)
const wordLoading = ref(false)
const wordData = ref(null)
const wordMap = ref({})  // pre-fetched passage glossary -> instant taps
const wordQuery = ref('')
const savingWord = ref(false)
const savedWords = ref(new Set())

// passage narration
const audioUrl = ref('')
const audioBusy = ref(false)
const audioEl = ref(null)

// reading speed + summary
const startedAt = ref(0)
const summaryText = ref('')
const summaryBusy = ref(false)
const summaryResult = ref(null)

// interests + library + insights
const topicOptions = ref([])
const selectedTopics = ref([])
const history = ref([])
const insights = ref(null)

function prettySkill(code) {
  const tail = String(code || '').split('.').pop() || ''
  return tail.replace(/_/g, ' ').replace(/\b\w/g, (m) => m.toUpperCase())
}
function barHeight(w) {
  const max = Math.max(...(insights.value?.wpm_recent || [1]), 1)
  return `${Math.max(12, Math.round((w / max) * 100))}%`
}

// length control
const LENGTH_OPTIONS = [
  { value: 'short', label: 'Short' },
  { value: 'medium', label: 'Medium' },
  { value: 'long', label: 'Long' },
]
const readingLength = ref('medium')

// zen / focus reading
const zen = ref(false)

// tap mode + sentence explanation
const tapMode = ref('word')
const sentenceOpen = ref(false)
const sentenceLoading = ref(false)
const sentenceQuery = ref('')
const sentenceExplanation = ref('')

const sentences = computed(() => {
  const p = lesson.value?.passage || ''
  return (p.match(/[^.!?]+[.!?]*/g) || []).map((s) => s.trim()).filter(Boolean)
})

// highlights + notes (saved per passage in localStorage)
const highlights = ref([])
function _hlKey() {
  return lesson.value?.id ? `reading_highlights_${lesson.value.id}` : ''
}
function loadHighlights() {
  highlights.value = []
  const key = _hlKey()
  if (!key) return
  try {
    highlights.value = JSON.parse(localStorage.getItem(key) || '[]')
  } catch {
    highlights.value = []
  }
}
function persistHighlights() {
  const key = _hlKey()
  if (key) {
    try {
      localStorage.setItem(key, JSON.stringify(highlights.value))
    } catch {
      /* storage full / unavailable — non-fatal */
    }
  }
}
function saveSelection() {
  const text = (window.getSelection?.()?.toString() || '').trim()
  if (!text || text.length > 400) return
  if (highlights.value.some((h) => h.text === text)) return
  highlights.value.push({ text, note: '' })
  persistHighlights()
  window.getSelection?.()?.removeAllRanges?.()
}
function removeHighlight(i) {
  highlights.value.splice(i, 1)
  persistHighlights()
}

// cloze (fill-the-gaps) — built locally from the current passage, self-study
const clozeOpen = ref(false)
const clozeChecked = ref(false)
const clozeBlanks = ref({}) // tokenIndex -> correct word
const clozeAnswers = ref({}) // tokenIndex -> chosen word
const clozeOptions = ref([])
const clozeHasBlanks = computed(() => Object.keys(clozeBlanks.value).length > 0)
const clozeTotal = computed(() => Object.keys(clozeBlanks.value).length)
const clozeScore = computed(
  () => Object.entries(clozeBlanks.value).filter(([i, w]) => clozeAnswers.value[i] === w).length,
)

function openCloze() {
  const toks = tokens.value
  const blanks = {}
  let wordCount = 0
  let made = 0
  toks.forEach((t, i) => {
    if (!t.word) return
    wordCount += 1
    const clean = t.text.replace(/[^A-Za-z']/g, '')
    if (clean.length >= 4 && wordCount % 5 === 0 && made < 8) {
      blanks[i] = clean
      made += 1
    }
  })
  clozeBlanks.value = blanks
  clozeAnswers.value = {}
  clozeChecked.value = false
  clozeOptions.value = [...new Set(Object.values(blanks))].sort(() => Math.random() - 0.5)
  clozeOpen.value = true
}

function checkCloze() {
  clozeChecked.value = true
}

// daily reading goal (counted from completed-today in the library)
const DAILY_GOAL = 3
const readToday = computed(() => {
  const today = new Date().toDateString()
  return (history.value || []).filter((h) => {
    if (!h.completed_at) return false
    try {
      return new Date(h.completed_at).toDateString() === today
    } catch {
      return false
    }
  }).length
})
const dailyGoalDone = computed(() => readToday.value >= DAILY_GOAL)

// speed trainer (RSVP — flash one word at a time at a target WPM)
const pacerOpen = ref(false)
const pacerWpm = ref(250)
const pacerIndex = ref(0)
const pacerRunning = ref(false)
let pacerTimer = null
const pacerWords = computed(() => (lesson.value?.passage || '').split(/\s+/).filter(Boolean))
const pacerProgress = computed(() => {
  const n = pacerWords.value.length
  return n ? Math.min(100, Math.round((pacerIndex.value / n) * 100)) : 0
})
function _clearPacer() {
  if (pacerTimer) {
    clearInterval(pacerTimer)
    pacerTimer = null
  }
}
function _runPacer() {
  _clearPacer()
  pacerRunning.value = true
  pacerTimer = setInterval(() => {
    if (pacerIndex.value >= pacerWords.value.length) {
      stopPacer()
      return
    }
    pacerIndex.value += 1
  }, Math.max(60, Math.round(60000 / pacerWpm.value)))
}
function openPacer() {
  if (!pacerWords.value.length) return
  pacerIndex.value = 0
  pacerOpen.value = true
  _runPacer()
}
function togglePacer() {
  if (pacerRunning.value) {
    _clearPacer()
    pacerRunning.value = false
  } else {
    if (pacerIndex.value >= pacerWords.value.length) pacerIndex.value = 0
    _runPacer()
  }
}
function restartPacer() {
  pacerIndex.value = 0
  _runPacer()
}
function stopPacer() {
  _clearPacer()
  pacerRunning.value = false
}
function setPacerWpm(w) {
  pacerWpm.value = w
  if (pacerRunning.value) _runPacer()
}
// Stop the interval on ANY close path (X button, backdrop, Esc) — not just update:model-value.
watch(pacerOpen, (open) => {
  if (!open) stopPacer()
})
onUnmounted(_clearPacer)

async function explainSentence(sentence) {
  if (!sentence) return
  sentenceQuery.value = sentence
  sentenceExplanation.value = ''
  sentenceOpen.value = true
  sentenceLoading.value = true
  try {
    const res = await explainReadingSentence(sentence, lesson.value?.level || 'A2')
    sentenceExplanation.value = res?.explanation || 'No explanation available.'
  } catch {
    sentenceExplanation.value = 'Could not load the explanation right now.'
  } finally {
    sentenceLoading.value = false
  }
}

const answeredCount = computed(() => lesson.value ? lesson.value.questions.filter((q) => answers[q.id] != null).length : 0)

// Question types the student got wrong — surfaced as "practice these" chips.
const weakTypes = computed(() => {
  const out = []
  for (const r of result.value?.question_results || []) {
    if (!r.is_correct && r.type && !out.includes(r.type)) out.push(r.type)
  }
  return out.slice(0, 3)
})

function isSaved(word) {
  return savedWords.value.has((word || '').toLowerCase())
}

const TYPE_LABELS = {
  main_idea: 'Main idea',
  detail: 'Detail',
  inference: 'Inference',
  vocab_in_context: 'Vocabulary',
  tone: 'Tone',
  true_false_notgiven: 'True / False / Not Given',
  sentence_completion: 'Sentence completion',
  heading_match: 'Matching headings',
}
function typeLabel(t) {
  return TYPE_LABELS[t] || (t || 'Question').replace(/_/g, ' ')
}

const tokens = computed(() => {
  const p = lesson.value?.passage || ''
  const re = /([A-Za-z]+(?:'[A-Za-z]+)?)|([^A-Za-z]+)/g
  const out = []
  let m
  let wi = -1
  while ((m = re.exec(p))) {
    const isWord = !!m[1]
    if (isWord) wi += 1
    out.push({ text: m[0], start: m.index, end: m.index + m[0].length, word: isWord, wordIndex: isWord ? wi : -1 })
  }
  return out
})
const totalWords = computed(() => tokens.value.filter((t) => t.word).length)

// read-along: highlight the word in step with the narration's playback position (estimated from
// progress, so it works with the existing audio without per-word TTS timings).
const karaokeWordIndex = ref(-1)
function onAudioTime(e) {
  const a = e?.target
  if (!a || !a.duration || !totalWords.value) return
  karaokeWordIndex.value = Math.min(totalWords.value - 1, Math.floor((a.currentTime / a.duration) * totalWords.value))
}
function clearKaraoke() {
  karaokeWordIndex.value = -1
}

const evidenceRange = computed(() => {
  const ev = (activeEvidence.value || '').trim()
  const p = lesson.value?.passage || ''
  if (!ev) return null
  const i = p.indexOf(ev)
  return i < 0 ? null : [i, i + ev.length]
})

function isHighlighted(tok) {
  const r = evidenceRange.value
  return !!r && tok.start < r[1] && tok.end > r[0]
}

function resultFor(qid) {
  return result.value?.question_results?.find((r) => r.id === qid) || null
}

function optionColor(q, oi) {
  const r = resultFor(q.id)
  if (!r) return undefined
  if (oi === r.correct_index) return 'success'
  if (oi === r.selected_index && !r.is_correct) return 'error'
  return undefined
}

function showEvidence(qid, quote) {
  activeQid.value = qid
  activeEvidence.value = quote
}

// Tell the learner when the difficulty actually stepped up (served level higher than last time).
const CEFR = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
const diffSnack = ref(false)
const diffLevel = ref('')
const difficultyUp = ref(false)
function _flagDifficulty(level) {
  if (!level) return
  let prev = null
  try {
    prev = localStorage.getItem('reading_seen_level')
  } catch {
    /* storage unavailable */
  }
  difficultyUp.value = !!prev && CEFR.indexOf(level) > CEFR.indexOf(prev)
  if (difficultyUp.value) {
    diffLevel.value = level
    diffSnack.value = true
  }
  try {
    localStorage.setItem('reading_seen_level', level)
  } catch {
    /* storage unavailable */
  }
}

async function loadNext() {
  if (busy.value) return
  busy.value = true
  generating.value = true
  loadError.value = ''
  try {
    const data = await fetchNextReading(readingLength.value)
    lesson.value = data
    _flagDifficulty(data.level)
    _resetPassageState()
    prefetchGlossary(data?.id)
  } catch (e) {
    if (!handleLanguageApiError(e, access.value)) loadError.value = getErrorMessage(e, 'Could not load a passage')
  } finally {
    busy.value = false
    generating.value = false
    loading.value = false
  }
}

async function submit() {
  if (busy.value || !lesson.value) return
  busy.value = true
  loadError.value = ''
  try {
    const payload = {}
    for (const q of lesson.value.questions) {
      payload[q.id] = { selected_index: answers[q.id] }
    }
    const duration = startedAt.value ? Math.round((Date.now() - startedAt.value) / 1000) : null
    result.value = await submitReadingLesson(lesson.value.id, payload, duration)
    submitted.value = true
    if (result.value?.score_percent >= 100) celebrateBig()
    else if (result.value?.passed) celebrate()
  } catch (e) {
    loadError.value = getErrorMessage(e, 'Could not submit your answers')
  } finally {
    busy.value = false
  }
}

// Pre-fetch the whole passage's glossary in one call so taps are instant.
async function prefetchGlossary(contentId) {
  if (!contentId) return
  wordMap.value = {}
  try {
    const { glossary } = await fetchReadingGlossary(contentId)
    wordMap.value = glossary || {}
  } catch {
    /* best-effort — lookup falls back to on-demand analysis */
  }
}

async function lookup(word) {
  const clean = (word || '').replace(/[^A-Za-z']/g, '')
  if (!clean) return
  wordQuery.value = clean
  wordOpen.value = true
  // Instant if the word is in the pre-fetched passage glossary.
  const hit = wordMap.value[clean.toLowerCase()]
  if (hit) {
    wordData.value = hit
    wordLoading.value = false
    return
  }
  wordData.value = null
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
    /* non-fatal — the word just isn't saved */
  } finally {
    savingWord.value = false
  }
}

async function toggleAudio() {
  if (audioUrl.value) {
    audioEl.value?.paused ? audioEl.value?.play() : audioEl.value?.pause()
    return
  }
  if (audioBusy.value || !lesson.value) return
  audioBusy.value = true
  try {
    const res = await fetchReadingAudio(lesson.value.id)
    if (res?.available && res.public_url) {
      audioUrl.value = res.public_url
      await nextTick()
      audioEl.value?.play?.()
    } else {
      loadError.value = 'Narration is not available for this passage right now.'
    }
  } catch (e) {
    loadError.value = getErrorMessage(e, 'Could not load the narration')
  } finally {
    audioBusy.value = false
  }
}

async function checkSummary() {
  if (summaryBusy.value || !lesson.value || summaryText.value.trim().length < 3) return
  summaryBusy.value = true
  try {
    summaryResult.value = await submitReadingSummary(lesson.value.id, summaryText.value.trim())
  } catch (e) {
    loadError.value = getErrorMessage(e, 'Could not check your summary')
  } finally {
    summaryBusy.value = false
  }
}

function _resetPassageState() {
  Object.keys(answers).forEach((k) => delete answers[k])
  submitted.value = false
  result.value = null
  activeQid.value = null
  activeEvidence.value = ''
  audioUrl.value = ''
  summaryText.value = ''
  summaryResult.value = null
  karaokeWordIndex.value = -1
  startedAt.value = Date.now()
  loadHighlights()
}

async function reread(id) {
  if (busy.value) return
  busy.value = true
  loadError.value = ''
  try {
    lesson.value = await fetchReadingLesson(id)
    _resetPassageState()
  } catch (e) {
    loadError.value = getErrorMessage(e, 'Could not open that passage')
  } finally {
    busy.value = false
  }
}

async function backToLibrary() {
  lesson.value = null
  await loadIntroExtras()
}

async function toggleTopic(t) {
  const next = selectedTopics.value.includes(t)
    ? selectedTopics.value.filter((x) => x !== t)
    : [...selectedTopics.value, t]
  selectedTopics.value = next
  try {
    const res = await saveReadingTopics(next)
    if (res?.selected) selectedTopics.value = res.selected // server caps/validates
  } catch {
    /* non-fatal — preference just isn't saved */
  }
}

async function loadIntroExtras() {
  try {
    const [topics, hist, ins] = await Promise.all([
      fetchReadingTopics(),
      fetchReadingHistory(),
      fetchReadingInsights(),
    ])
    topicOptions.value = topics?.options || []
    selectedTopics.value = topics?.selected || []
    history.value = hist || []
    insights.value = ins || null
  } catch {
    /* best-effort — intro extras are optional */
  }
}

onMounted(async () => {
  try {
    await loadAccess(true)
    await loadIntroExtras() // show interests + library first; the learner starts when ready
  } catch (e) {
    if (!handleLanguageApiError(e, access.value)) loadError.value = getErrorMessage(e, 'Unable to load reading')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.page-container { max-width: 1040px; margin: 0 auto; }
.passage-card { position: sticky; top: 16px; }
.reading-passage { line-height: 2; font-size: 1.05rem; }
.rw { cursor: pointer; border-radius: 4px; transition: background 0.1s; }
.rw:hover { background: rgba(var(--v-theme-secondary), 0.18); }
.rw--hl { background: rgba(var(--v-theme-warning), 0.32); border-radius: 3px; }
.rw--karaoke { background: rgba(var(--v-theme-secondary), 0.45); border-radius: 3px; }
.q-block { padding: 8px; border-radius: 12px; transition: background 0.15s; }
.q-block--active { background: rgba(var(--v-theme-secondary), 0.06); }
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
.summary-box { background: rgba(var(--v-theme-secondary), 0.06); border: 1px solid rgba(var(--v-theme-secondary), 0.18); }
.lib-item { cursor: pointer; border-radius: 8px; }
.lib-item:hover { background: rgba(var(--v-theme-secondary), 0.08); }
.glossary-box { background: rgba(var(--v-theme-info), 0.07); border: 1px solid rgba(var(--v-theme-info), 0.2); }
.pacer-word { font-size: 2.4rem; font-weight: 700; min-height: 3.2rem; display: flex; align-items: center; justify-content: center; letter-spacing: 0.5px; }
.insights-box { background: rgba(var(--v-theme-secondary), 0.06); border: 1px solid rgba(var(--v-theme-secondary), 0.18); }
.wpm-bar { flex: 1 1 0; min-width: 4px; background: rgb(var(--v-theme-secondary)); border-radius: 2px 2px 0 0; opacity: 0.7; }
.blank-select { border: 1px solid rgba(var(--v-theme-secondary), 0.5); border-radius: 6px; padding: 0 4px; margin: 0 2px; background: rgba(var(--v-theme-secondary), 0.08); color: inherit; font: inherit; }
.blank-select.ok { border-color: rgb(var(--v-theme-success)); color: rgb(var(--v-theme-success)); }
.blank-select.bad { border-color: rgb(var(--v-theme-error)); color: rgb(var(--v-theme-error)); }
.hl-item { background: rgba(var(--v-theme-warning), 0.1); border: 1px solid rgba(var(--v-theme-warning), 0.25); }
.hl-text { font-style: italic; }
.hl-note { font-size: 0.85rem; }
</style>

<style>
/* Zen mode lives at <body> via Teleport, so it is intentionally not scoped. */
.zen-overlay {
  position: fixed;
  inset: 0;
  z-index: 2000; /* below Vuetify dialogs (~2400) so the word lookup still shows on top */
  background:
    radial-gradient(1200px 600px at 70% -10%, rgba(34, 211, 238, 0.12), transparent 60%),
    radial-gradient(1000px 600px at 0% 110%, rgba(167, 139, 250, 0.12), transparent 60%),
    #0b1020;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}
.zen-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  position: sticky;
  top: 0;
}
.zen-body { max-width: 720px; margin: 0 auto; padding: 8px 28px 80px; }
.zen-title { font-size: 1.6rem; font-weight: 800; margin-bottom: 20px; color: #e8ecf6; }
.zen-text { font-size: 1.5rem; line-height: 2.1; color: #d6dcec; letter-spacing: 0.2px; }
.zen-text .rw { cursor: pointer; border-radius: 5px; transition: background 0.12s; }
.zen-text .rw:hover { background: rgba(34, 211, 238, 0.2); }
.zen-fade-enter-active, .zen-fade-leave-active { transition: opacity 0.35s ease; }
.zen-fade-enter-from, .zen-fade-leave-to { opacity: 0; }
.rs { cursor: pointer; border-radius: 4px; transition: background 0.1s; }
.rs:hover { background: rgba(var(--v-theme-secondary), 0.14); }
</style>
