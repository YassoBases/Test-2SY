<template>
  <div class="page-container slide-up-enter-active">
    <PageHeader
      eyebrow="Learn languages"
      eyebrow-icon="mdi-cards"
      title="Vocabulary"
      subtitle="Flashcards with spaced repetition — grade each word to schedule its next review"
    />
    <LanguageModuleTabs />

    <v-alert v-if="loadError" type="error" variant="tonal" class="mb-4 rounded-lg">{{ loadError }}</v-alert>

    <LoadingState v-if="loading" variant="cards" :count="3" class="mb-6" />

    <template v-else>
      <v-alert
        v-if="listMeta?.student_level && listMeta?.lesson_level && listMeta.student_level !== listMeta.lesson_level"
        type="info"
        variant="tonal"
        class="mb-4"
      >
        Your reading level: <strong>{{ listMeta.student_level }}</strong> —
        Cards currently available at level <strong>{{ listMeta.lesson_level }}</strong>.
      </v-alert>

      <v-tabs v-model="vocabTab" color="secondary" class="mb-4">
        <v-tab value="daily">Today's New Words</v-tab>
        <v-tab value="bank">Review Bank<template v-if="cards.length"> ({{ cards.length }})</template></v-tab>
      </v-tabs>

      <v-window v-model="vocabTab">
        <!-- Daily AI-generated batch (10/day) — a separate mode from the cumulative bank below. -->
        <v-window-item value="daily">
          <VocabularyGenerator @graded="onDailyWordGraded" />
        </v-window-item>

        <!-- Cumulative review bank — every word the student has ever met, with its own filters. -->
        <v-window-item value="bank">
          <v-row class="mb-4" v-if="metrics">
            <v-col cols="6" sm="3">
              <v-card class="glass-card kpi-card pa-3 text-center" variant="flat">
                <div class="text-caption text-medium-emphasis">Total</div>
                <div class="text-h6 font-weight-bold">{{ metrics.total_words }}</div>
              </v-card>
            </v-col>
            <v-col cols="6" sm="3">
              <v-card class="glass-card kpi-card kpi-card--success pa-3 text-center" variant="flat">
                <div class="text-caption text-medium-emphasis">Known</div>
                <div class="text-h6 font-weight-bold text-success">{{ metrics.known_words }}</div>
              </v-card>
            </v-col>
            <v-col cols="6" sm="3">
              <v-card class="glass-card kpi-card kpi-card--warning pa-3 text-center" variant="flat">
                <div class="text-caption text-medium-emphasis">Due today</div>
                <div class="text-h6 font-weight-bold text-warning">{{ stats?.due_today ?? '—' }}</div>
              </v-card>
            </v-col>
            <v-col cols="6" sm="3">
              <v-card class="glass-card kpi-card pa-3 text-center" variant="flat">
                <div class="text-caption text-medium-emphasis">Not Learned Yet</div>
                <div class="text-h6 font-weight-bold">{{ metrics.new_words }}</div>
              </v-card>
            </v-col>
          </v-row>

          <v-card v-if="metrics" class="glass-card pa-3 mb-4" variant="flat">
            <div class="d-flex justify-space-between align-center mb-1">
              <span class="text-caption text-medium-emphasis">Daily goal</span>
              <span class="text-caption font-weight-bold">
                {{ metrics.reviewed_today }}/{{ metrics.daily_review_goal }} words learned today
              </span>
            </div>
            <v-progress-linear
              :model-value="(metrics.reviewed_today / metrics.daily_review_goal) * 100"
              color="success" height="8" rounded
            />
          </v-card>

          <v-chip-group
            v-if="cards.length"
            v-model="cardFilter"
            mandatory
            selected-class="text-secondary"
            class="mb-2"
          >
            <v-chip value="all" size="small" variant="tonal">All</v-chip>
            <v-chip value="due" size="small" variant="tonal">Due</v-chip>
            <v-chip value="difficult" size="small" variant="tonal">Difficult</v-chip>
          </v-chip-group>

          <EmptyState v-if="!filteredCards.length" preset="languageVocabulary" />

          <v-row v-else class="mt-1">
            <v-col v-for="card in filteredCards" :key="card.id" cols="12" sm="6" md="4">
              <VocabularyWordCard
                :word="card"
                :image-url="card.image_url || cardImages[card.id] || ''"
                :image-loading="!!cardImagesLoading[card.id]"
                :status-label="vocabularyStatusLabel(card.status)"
                :due-badge="!!card.due"
                show-grading
                :grading-quality="gradingId === card.id ? gradingQuality : null"
                @grade="(quality) => grade(card, quality)"
              />
            </v-col>
          </v-row>
        </v-window-item>
      </v-window>

      <!-- Word lookup (AI, English-only) — a shared tool, not tied to either mode above. -->
      <v-card class="glass-card pa-4 mb-4 mt-4" variant="flat">
        <div class="text-subtitle-2 font-weight-bold mb-2">
          <v-icon size="18" icon="mdi-magnify" /> Look up a word
        </div>
        <div class="d-flex gap-2">
          <v-text-field
            v-model="lookupWord" density="compact" variant="outlined" hide-details
            placeholder="Type an English word…" dir="ltr" :disabled="lookupBusy"
            @keyup.enter="doLookup"
          />
          <v-btn color="secondary" variant="flat" :loading="lookupBusy" :disabled="!lookupWord.trim()" @click="doLookup">
            Analyze
          </v-btn>
        </div>
        <div v-if="lookup" class="mt-3" dir="ltr">
          <div class="d-flex align-center gap-2 mb-1 flex-wrap">
            <span class="text-h6 font-weight-bold">{{ lookup.word }}</span>
            <v-chip v-if="lookup.part_of_speech" size="x-small" variant="tonal">{{ lookup.part_of_speech }}</v-chip>
            <v-chip v-if="lookup.cefr_level" size="x-small" color="secondary" variant="tonal">{{ lookup.cefr_level }}</v-chip>
          </div>
          <p class="text-body-2 mb-1">{{ lookup.definition }}</p>
          <p v-if="lookup.example_sentence" class="text-body-2 text-medium-emphasis mb-1"><em>{{ lookup.example_sentence }}</em></p>
          <div v-if="lookup.pronunciation_tip" class="text-caption text-medium-emphasis mb-1">🔊 {{ lookup.pronunciation_tip }}</div>
          <WordPronunciation :word="lookup.word" class="mb-2" />
          <div v-if="lookup.synonyms?.length" class="d-flex flex-wrap gap-1">
            <v-chip v-for="(s, i) in lookup.synonyms" :key="i" size="x-small" variant="outlined">{{ s }}</v-chip>
          </div>
        </div>
      </v-card>

      <!-- Daily spelling + pronunciation quiz — tests words already learned, next to the challenge. -->
      <DailyVocabQuiz />

      <!-- Daily fill-in-the-blanks challenge — also shared, drawn from due words in the bank. -->
      <v-card class="glass-card pa-4 mb-4" variant="flat">
        <div class="d-flex align-center justify-space-between flex-wrap gap-2 mb-2">
          <div class="text-subtitle-2 font-weight-bold">
            <v-icon size="18" icon="mdi-puzzle-outline" /> Daily challenge
          </div>
          <v-btn size="small" color="secondary" variant="tonal" :loading="challengeBusy" @click="loadChallenge">
            {{ challenge ? 'New challenge' : 'Start' }}
          </v-btn>
        </div>
        <template v-if="challenge">
          <template v-if="challenge.paragraph_challenge">
            <p v-if="challenge.context_hint" class="text-caption text-medium-emphasis mb-2">{{ challenge.context_hint }}</p>
            <div class="challenge-para text-body-1" dir="ltr">
              <template v-for="(seg, i) in challengeSegments" :key="i">
                <span v-if="seg.type === 'text'">{{ seg.value }}</span>
                <select
                  v-else v-model="answers[seg.key]" class="blank-select"
                  :class="checked ? (answers[seg.key] === challenge.blanks_mapping[seg.key] ? 'ok' : 'bad') : ''"
                >
                  <option value="">— ? —</option>
                  <option v-for="(o, oi) in challenge.options_pool" :key="oi" :value="o">{{ o }}</option>
                </select>
              </template>
            </div>
            <div class="d-flex align-center gap-3 mt-3">
              <v-btn size="small" color="secondary" variant="flat" @click="checkChallenge">Check answers</v-btn>
              <span v-if="checked" class="text-body-2 font-weight-bold" :class="challengeScore === challengeTotal ? 'text-success' : 'text-warning'">
                {{ challengeScore }} / {{ challengeTotal }} correct
              </span>
            </div>
          </template>
          <p v-else class="text-body-2 text-medium-emphasis mb-0">{{ challenge.context_hint }}</p>
        </template>
      </v-card>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import PageHeader from '../../../components/common/PageHeader.vue'
import LoadingState from '../../../components/common/LoadingState.vue'
import EmptyState from '../../../components/common/EmptyState.vue'
import LanguageModuleTabs from '../../../components/language/LanguageModuleTabs.vue'
import WordPronunciation from '../../../components/language/WordPronunciation.vue'
import VocabularyGenerator from '../../../components/language/VocabularyGenerator.vue'
import VocabularyWordCard from '../../../components/language/VocabularyWordCard.vue'
import DailyVocabQuiz from '../../../components/language/DailyVocabQuiz.vue'
import {
  fetchVocabulary,
  fetchVocabularyCard,
  fetchVocabularyStats,
  fetchVocabularyWordImage,
  reviewVocabularyCard,
  vocabularyStatusLabel,
  analyzeWord,
  fetchVocabularyChallenge,
  submitVocabularyChallenge,
} from '../../../api/language.js'
import { useLanguageGate } from '../../../composables/useLanguageGate.js'
import { useLanguageAccess } from '../../../composables/useLanguageAccess.js'

const { access, loadAccess } = useLanguageAccess()
const { handleLanguageApiError, getErrorMessage } = useLanguageGate()

const loading = ref(true)
const loadError = ref('')
const vocabTab = ref('daily') // 'daily' (today's AI batch) | 'bank' (cumulative review)
const cards = ref([])
const metrics = ref(null)
const stats = ref(null)
const listMeta = ref(null)
const gradingId = ref(null) // id of the card currently being graded, or null
const gradingQuality = ref(null) // the SM-2 quality (1/3/4/5) being submitted for that card

const cardImages = ref({}) // { [cardId]: url }
const cardImagesLoading = ref({}) // { [cardId]: bool }

const cardFilter = ref('all') // 'all' | 'due' | 'difficult'
const filteredCards = computed(() => {
  if (cardFilter.value === 'due') return cards.value.filter((c) => c.due)
  if (cardFilter.value === 'difficult') return cards.value.filter((c) => c.is_difficult)
  return cards.value
})
const studentLevel = computed(() => listMeta.value?.student_level || 'A2')

// --- Word lookup ---
const lookupWord = ref('')
const lookup = ref(null)
const lookupBusy = ref(false)

async function doLookup() {
  if (!lookupWord.value.trim() || lookupBusy.value) return
  lookupBusy.value = true
  loadError.value = ''
  try {
    lookup.value = await analyzeWord(lookupWord.value.trim(), studentLevel.value)
  } catch (e) {
    loadError.value = getErrorMessage(e, 'Could not analyze that word')
  } finally {
    lookupBusy.value = false
  }
}

// --- Daily fill-in-the-blanks challenge ---
const challenge = ref(null)
const challengeBusy = ref(false)
const answers = ref({})
const checked = ref(false)
const challengeScore = ref(0)

const challengeSegments = computed(() => {
  const p = challenge.value?.paragraph_challenge || ''
  const parts = []
  const re = /(\[blank\d+\])/g
  let last = 0
  let m
  while ((m = re.exec(p))) {
    if (m.index > last) parts.push({ type: 'text', value: p.slice(last, m.index) })
    parts.push({ type: 'blank', key: m[1] })
    last = m.index + m[0].length
  }
  if (last < p.length) parts.push({ type: 'text', value: p.slice(last) })
  return parts
})
const challengeTotal = computed(() => Object.keys(challenge.value?.blanks_mapping || {}).length)

async function loadChallenge() {
  if (challengeBusy.value) return
  challengeBusy.value = true
  checked.value = false
  challengeScore.value = 0
  loadError.value = ''
  try {
    challenge.value = await fetchVocabularyChallenge()
    const fresh = {}
    for (const k of Object.keys(challenge.value?.blanks_mapping || {})) fresh[k] = ''
    answers.value = fresh
  } catch (e) {
    loadError.value = getErrorMessage(e, 'Could not load the challenge')
  } finally {
    challengeBusy.value = false
  }
}

async function checkChallenge() {
  const map = challenge.value?.blanks_mapping || {}
  let s = 0
  const results = []
  for (const k of Object.keys(map)) {
    const correct = answers.value[k] === map[k]
    if (correct) s += 1
    results.push({ word: map[k], correct })
  }
  challengeScore.value = s
  checked.value = true
  // Feed the learner model (best-effort — never block the UI on this).
  if (results.length) {
    try {
      await submitVocabularyChallenge(results)
    } catch {
      /* non-fatal: the challenge is still graded locally */
    }
  }
}

onMounted(async () => {
  try {
    await loadAccess(true)
    await refreshVocabularyData()
  } catch (e) {
    if (!handleLanguageApiError(e, access.value)) {
      loadError.value = getErrorMessage(e, 'Unable to load vocabulary')
    }
  } finally {
    loading.value = false
  }
  // Started only after the critical page data has loaded: these lazy background fetches
  // (up to 6 concurrent) would otherwise saturate the browser's per-origin connection pool
  // and starve refreshVocabularyData() of a connection, stalling the initial page load.
  enrichAndIllustrateCards()
})

// Run async jobs with bounded concurrency — cards can enrich/illustrate lazily without
// firing dozens of simultaneous AI calls at once.
async function runLimited(items, limit, worker) {
  let i = 0
  async function lane() {
    while (i < items.length) {
      const item = items[i++]
      await worker(item)
    }
  }
  await Promise.all(Array.from({ length: Math.min(limit, items.length) }, lane))
}

async function loadCardImage(card) {
  if (cardImages.value[card.id] || cardImagesLoading.value[card.id]) return
  cardImagesLoading.value = { ...cardImagesLoading.value, [card.id]: true }
  try {
    const { image_url } = await fetchVocabularyWordImage(card.id)
    if (image_url) cardImages.value = { ...cardImages.value, [card.id]: image_url }
  } catch {
    /* illustration is best-effort — the card still works without one */
  } finally {
    cardImagesLoading.value = { ...cardImagesLoading.value, [card.id]: false }
  }
}

async function enrichCard(card) {
  try {
    const fresh = await fetchVocabularyCard(card.id)
    const masterIdx = cards.value.findIndex((c) => c.id === fresh.id)
    if (masterIdx !== -1) cards.value[masterIdx] = fresh
  } catch {
    /* leave the stub as-is — it'll retry next load */
  }
}

// Every metrics/cards/stats refresh (initial load, a bank-tab grade, a daily-tab grade) goes
// through this one gate. Each call claims a ticket; if a NEWER refresh has already started by
// the time this one's response arrives, its result is discarded instead of applied — otherwise
// a fast post-grade refresh could be overwritten moments later by a slower, older refresh
// (e.g. the initial page load) resolving out of order, briefly flashing a stale count.
let vocabRefreshSeq = 0

async function refreshVocabularyData({ withStats = true } = {}) {
  const mySeq = ++vocabRefreshSeq
  const [vocabRes, statsRes] = await Promise.all([
    fetchVocabulary(),
    withStats ? fetchVocabularyStats().catch(() => null) : Promise.resolve(null),
  ])
  if (mySeq !== vocabRefreshSeq) return // superseded — a newer refresh is now the source of truth
  listMeta.value = { student_level: vocabRes.student_level, lesson_level: vocabRes.lesson_level }
  metrics.value = vocabRes.metrics
  cards.value = vocabRes.cards || []
  if (statsRes) stats.value = statsRes
}

// Everything on a card must be visible without a click now, so enrich stub words and
// fetch/generate missing illustrations in the background once the page itself has loaded.
async function enrichAndIllustrateCards() {
  const needsEnrich = cards.value.filter((c) => c.enriched === false)
  const needsImage = cards.value.filter((c) => !c.image_url)
  await Promise.all([runLimited(needsEnrich, 2, enrichCard), runLimited(needsImage, 2, loadCardImage)])
}

async function grade(card, quality) {
  gradingId.value = card.id
  gradingQuality.value = quality
  try {
    const updated = await reviewVocabularyCard(card.id, quality)
    const masterIdx = cards.value.findIndex((c) => c.id === updated.id)
    if (masterIdx !== -1) cards.value[masterIdx] = updated
    await refreshVocabularyData()
  } catch (e) {
    loadError.value = getErrorMessage(e, 'Unable to save review')
  } finally {
    gradingId.value = null
    gradingQuality.value = null
  }
}

// The daily single-card view (VocabularyGenerator) manages its own word/index state and
// grades independently — it emits 'graded' so this page's "X/10 today" tracker (and the
// bank's stale card data) stay in sync with reviews recorded from either tab.
async function onDailyWordGraded() {
  try {
    await refreshVocabularyData()
  } catch {
    /* best-effort — the tracker will catch up on next load */
  }
}
</script>

<style scoped>
.page-container {
  max-width: 1100px;
  margin: 0 auto;
}
.challenge-para {
  line-height: 2.1;
}
.blank-select {
  margin: 0 2px;
  padding: 1px 6px;
  border-radius: 8px;
  background: rgba(var(--v-theme-secondary), 0.12);
  border: 1px solid rgba(var(--v-theme-secondary), 0.4);
  color: rgb(var(--v-theme-on-surface));
  font: inherit;
}
.blank-select.ok {
  background: rgba(var(--v-theme-success), 0.18);
  border-color: rgb(var(--v-theme-success));
}
.blank-select.bad {
  background: rgba(var(--v-theme-error), 0.18);
  border-color: rgb(var(--v-theme-error));
}
</style>
