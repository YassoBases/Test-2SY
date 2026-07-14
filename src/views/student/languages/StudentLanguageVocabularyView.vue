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

      <!-- Infinite offline vocabulary generator -->
      <VocabularyGenerator />

      <!-- Word lookup (AI, English-only) -->
      <v-card class="glass-card pa-4 mb-4" variant="flat">
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

      <!-- Daily fill-in-the-blanks challenge -->
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

      <EmptyState v-if="!cards.length" preset="languageVocabulary" />

      <template v-else>
        <v-card class="glass-card pa-6 mb-4 flashcard" variant="flat">
          <div class="d-flex justify-space-between align-center mb-3">
            <v-chip size="small">{{ currentCard?.level || '—' }}</v-chip>
            <div class="d-flex align-center gap-2">
              <v-chip v-if="currentCard?.due" size="x-small" color="warning" variant="tonal">due</v-chip>
              <v-chip size="small" variant="tonal" color="secondary">
                {{ vocabularyStatusLabel(currentCard?.status) }}
              </v-chip>
            </div>
          </div>

          <div class="text-h4 font-weight-bold mb-2" dir="ltr">{{ currentCard?.word }}</div>
          <WordPronunciation v-if="currentCard?.word" :word="currentCard.word" class="mb-2" />
          <div v-if="revealed" class="mt-4">
            <div class="text-h6 mb-2">{{ currentCard?.translation_ar }}</div>
            <p v-if="currentCard?.example" class="text-body-2 mb-1" dir="ltr">{{ currentCard.example }}</p>
          </div>
          <div v-else class="text-body-2 text-medium-emphasis mt-4">Press "Show meaning" to see the translation.</div>

          <div v-if="!revealed" class="mt-6">
            <v-btn variant="tonal" block :loading="enriching" @click="reveal">Show meaning</v-btn>
          </div>
          <div v-else class="mt-6">
            <div class="text-caption text-medium-emphasis text-center mb-2">How well did you recall this word?</div>
            <div class="d-flex gap-2 flex-wrap justify-center">
              <v-btn size="small" color="error" variant="tonal" :loading="reviewing" @click="grade(1)">Again</v-btn>
              <v-btn size="small" color="warning" variant="tonal" :loading="reviewing" @click="grade(3)">Hard</v-btn>
              <v-btn size="small" color="secondary" variant="tonal" :loading="reviewing" @click="grade(4)">Good</v-btn>
              <v-btn size="small" color="success" variant="flat" :loading="reviewing" @click="grade(5)">Easy</v-btn>
            </div>
          </div>
        </v-card>

        <div class="d-flex align-center justify-space-between flex-wrap gap-2">
          <v-btn variant="text" :disabled="index <= 0" @click="prev">Previous</v-btn>
          <span class="text-body-2">{{ index + 1 }} / {{ cards.length }}</span>
          <v-btn variant="text" :disabled="index >= cards.length - 1" @click="next">Next</v-btn>
        </div>

        <v-list v-if="cards.length > 1" density="compact" class="mt-4 glass-card rounded-lg">
          <v-list-item
            v-for="(card, i) in cards"
            :key="card.id"
            :active="i === index"
            rounded="lg"
            @click="goTo(i)"
          >
            <template #prepend>
              <v-icon size="10" :color="card.due ? 'warning' : 'success'" class="me-2">mdi-circle</v-icon>
            </template>
            <v-list-item-title dir="ltr">{{ card.word }}</v-list-item-title>
            <template #append>
              <span class="text-caption">{{ vocabularyStatusLabel(card.status) }}</span>
            </template>
          </v-list-item>
        </v-list>
      </template>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import PageHeader from '../../../components/common/PageHeader.vue'
import LoadingState from '../../../components/common/LoadingState.vue'
import EmptyState from '../../../components/common/EmptyState.vue'
import LanguageModuleTabs from '../../../components/language/LanguageModuleTabs.vue'
import WordPronunciation from '../../../components/language/WordPronunciation.vue'
import VocabularyGenerator from '../../../components/language/VocabularyGenerator.vue'
import {
  fetchVocabulary,
  fetchVocabularyCard,
  fetchVocabularyStats,
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
const cards = ref([])
const metrics = ref(null)
const stats = ref(null)
const listMeta = ref(null)
const index = ref(0)
const revealed = ref(false)
const reviewing = ref(false)
const enriching = ref(false)

const currentCard = computed(() => cards.value[index.value] || null)
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

watch(index, () => {
  revealed.value = false
})

onMounted(async () => {
  try {
    await loadAccess(true)
    await loadCards()
    await loadStats()
  } catch (e) {
    if (!handleLanguageApiError(e, access.value)) {
      loadError.value = getErrorMessage(e, 'Unable to load vocabulary')
    }
  } finally {
    loading.value = false
  }
})

async function loadCards() {
  const res = await fetchVocabulary()
  listMeta.value = { student_level: res.student_level, lesson_level: res.lesson_level }
  metrics.value = res.metrics
  cards.value = res.cards || []
  if (index.value >= cards.value.length) index.value = 0
}

async function loadStats() {
  try {
    stats.value = await fetchVocabularyStats()
  } catch {
    /* the due-today stat is best-effort */
  }
}

async function reveal() {
  const card = currentCard.value
  // Stub word (no definition yet) -> fetch detail, which lazily AI-enriches + caches it server-side.
  if (card && card.enriched === false && !enriching.value) {
    enriching.value = true
    try {
      const fresh = await fetchVocabularyCard(card.id)
      cards.value[index.value] = fresh
    } catch (e) {
      loadError.value = getErrorMessage(e, 'Could not load the meaning')
    } finally {
      enriching.value = false
    }
  }
  revealed.value = true
}

async function grade(quality) {
  if (!currentCard.value) return
  reviewing.value = true
  try {
    const updated = await reviewVocabularyCard(currentCard.value.id, quality)
    cards.value[index.value] = updated
    metrics.value = (await fetchVocabulary()).metrics
    await loadStats()
    if (index.value < cards.value.length - 1) {
      index.value += 1
    } else {
      revealed.value = false
    }
  } catch (e) {
    loadError.value = getErrorMessage(e, 'Unable to save review')
  } finally {
    reviewing.value = false
  }
}

function prev() {
  if (index.value > 0) index.value -= 1
}

function next() {
  if (index.value < cards.value.length - 1) index.value += 1
}

function goTo(i) {
  index.value = i
}
</script>

<style scoped>
.page-container {
  max-width: 720px;
  margin: 0 auto;
}
.flashcard {
  min-height: 280px;
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
