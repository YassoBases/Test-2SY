<template>
  <v-card class="glass-card pa-4 mb-4" variant="flat" dir="ltr">
    <div class="d-flex align-center justify-space-between flex-wrap gap-2 mb-2">
      <div class="text-subtitle-2 font-weight-bold">
        <v-icon size="18" icon="mdi-school-outline" /> Daily vocabulary quiz
      </div>
      <v-btn
        v-if="!started"
        size="small" color="secondary" variant="tonal" :loading="loading"
        :disabled="quiz?.already_completed_today || quiz?.total === 0"
        @click="start"
      >
        {{ quiz?.already_completed_today ? 'Done for today' : 'Start' }}
      </v-btn>
    </div>

    <p v-if="!started && quiz?.already_completed_today" class="text-body-2 text-medium-emphasis mb-0">
      You've completed today's quiz — come back tomorrow for a new one.
    </p>
    <p v-else-if="!started && quiz && quiz.total === 0" class="text-body-2 text-medium-emphasis mb-0">
      Learn a few words first, then come back to quiz yourself on them.
    </p>
    <p v-else-if="!started" class="text-caption text-medium-emphasis mb-0">
      Spelling + pronunciation, {{ quiz?.total ?? 10 }} words you've already learned today.
    </p>

    <template v-else-if="started && !summary">
      <div class="d-flex align-center justify-space-between mb-2">
        <span class="text-caption text-medium-emphasis">Word {{ index + 1 }} / {{ items.length }}</span>
        <span class="text-caption text-medium-emphasis text-capitalize">{{ phase }}</span>
      </div>

      <template v-if="phase === 'spelling'">
        <p class="text-body-2 mb-1">{{ currentItem.definition }}</p>
        <p v-if="currentItem.example_masked" class="text-body-2 text-medium-emphasis mb-3" dir="ltr">
          <em>{{ currentItem.example_masked }}</em>
        </p>
        <div class="d-flex">
          <v-text-field
            v-model="guess" density="compact" variant="outlined" hide-details class="mr-2"
            placeholder="Type the word…" dir="ltr" :disabled="checkingSpelling"
            @keyup.enter="submitSpelling"
          />
          <v-btn color="secondary" variant="flat" :loading="checkingSpelling" :disabled="!guess.trim()" @click="submitSpelling">
            Check
          </v-btn>
        </div>
      </template>

      <template v-else-if="phase === 'pronunciation'">
        <div class="d-flex align-center flex-wrap mb-1">
          <span
            class="text-body-2 font-weight-bold mr-2"
            :class="lastSpelling?.correct ? 'text-success' : lastSpelling?.near_miss ? 'text-warning' : 'text-error'"
          >
            <template v-if="lastSpelling?.correct">✓ Correct!</template>
            <template v-else-if="lastSpelling?.near_miss">Close — it's</template>
            <template v-else>Not quite — it's</template>
          </span>
          <span class="text-h6 font-weight-bold">{{ revealedWord }}</span>
        </div>
        <p class="text-caption text-medium-emphasis mb-2">Now say it out loud.</p>
        <WordPronunciation :word="revealedWord" @scored="onScored" />
        <v-btn size="small" variant="text" class="mt-3" @click="nextWord">
          {{ isLastWord ? 'Finish quiz' : 'Next word' }}
        </v-btn>
      </template>
    </template>

    <template v-else-if="summary">
      <div class="d-flex flex-wrap">
        <div class="mr-6">
          <div class="text-caption text-medium-emphasis">Spelling</div>
          <div class="text-h6 font-weight-bold">{{ summary.spelling_correct }} / {{ summary.spelling_total }}</div>
        </div>
        <div>
          <div class="text-caption text-medium-emphasis">Pronunciation avg.</div>
          <div class="text-h6 font-weight-bold">{{ Math.round(summary.pronunciation_average) }}%</div>
        </div>
      </div>
      <p class="text-caption text-medium-emphasis mt-2 mb-0">Nice work — come back tomorrow for a new quiz.</p>
    </template>
  </v-card>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import WordPronunciation from './WordPronunciation.vue'
import { fetchDailyVocabQuiz, submitQuizSpelling, completeDailyQuiz } from '../../api/language.js'

const loading = ref(false)
const quiz = ref(null)
const started = ref(false)
const items = ref([])
const index = ref(0)
const phase = ref('spelling') // 'spelling' | 'pronunciation'
const guess = ref('')
const checkingSpelling = ref(false)
const lastSpelling = ref(null)
const revealedWord = ref('')
const results = ref([]) // [{item_id, spelling_correct, spelling_near_miss, pronunciation_score}]
const summary = ref(null)

const currentItem = computed(() => items.value[index.value] || null)
const isLastWord = computed(() => index.value >= items.value.length - 1)

onMounted(async () => {
  loading.value = true
  try {
    quiz.value = await fetchDailyVocabQuiz()
  } catch {
    quiz.value = { items: [], total: 0, already_completed_today: false }
  } finally {
    loading.value = false
  }
})

function start() {
  items.value = quiz.value?.items || []
  index.value = 0
  phase.value = 'spelling'
  guess.value = ''
  results.value = []
  summary.value = null
  started.value = true
}

async function submitSpelling() {
  if (!currentItem.value || checkingSpelling.value) return
  checkingSpelling.value = true
  try {
    const res = await submitQuizSpelling(currentItem.value.item_id, guess.value)
    lastSpelling.value = res
    revealedWord.value = res.correct_word
    results.value.push({
      item_id: currentItem.value.item_id,
      spelling_correct: res.correct,
      spelling_near_miss: res.near_miss,
      pronunciation_score: null,
    })
    phase.value = 'pronunciation'
  } catch {
    // best-effort — let the student retry the check
  } finally {
    checkingSpelling.value = false
  }
}

function onScored(feedback) {
  const entry = results.value[results.value.length - 1]
  if (entry) entry.pronunciation_score = feedback?.overall_score ?? null
}

async function nextWord() {
  if (isLastWord.value) {
    try {
      summary.value = await completeDailyQuiz(results.value)
    } catch {
      summary.value = {
        spelling_correct: results.value.filter((r) => r.spelling_correct).length,
        spelling_total: results.value.length,
        pronunciation_average: 0,
      }
    }
    return
  }
  index.value += 1
  phase.value = 'spelling'
  guess.value = ''
  lastSpelling.value = null
  revealedWord.value = ''
}
</script>
