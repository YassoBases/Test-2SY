<template>
  <section class="section-block mb-4">
    <div class="section-block__head">
      <h3 class="section-block__title">Vocabulary generator</h3>
      <div class="section-block__subtitle">A personalized AI batch based on your level and interests.</div>
    </div>
    <v-card class="glass-card pa-6" variant="flat">
      <div class="d-flex flex-wrap gap-3 align-center">
        <v-btn color="secondary" variant="flat" :loading="aiLoading" prepend-icon="mdi-auto-fix" @click="generateAi">
          Generate my words
        </v-btn>
        <span v-if="aiRemainingToday !== null" class="text-caption text-medium-emphasis">
          {{ aiRemainingToday }} of 10 AI words left today
        </span>
      </div>

      <div v-if="aiLoading" class="mt-4"><LearningLoader compact :title="''" icon="mdi-cards" /></div>
      <v-alert v-else-if="aiLimitReached" type="info" variant="tonal" class="mt-3 mb-0">
        You've used today's AI words — come back tomorrow for more!
      </v-alert>
      <v-alert v-else-if="aiError" type="error" variant="tonal" class="mt-3 mb-0">{{ aiError }}</v-alert>
      <template v-else-if="aiWords.length && currentAiWord">
        <div class="d-flex align-center justify-space-between mt-4 mb-3">
          <v-btn
            variant="text" size="default" prepend-icon="mdi-chevron-left"
            :disabled="aiIndex <= 0" @click="prevAiWord"
          >Previous</v-btn>
          <span class="text-body-1 font-weight-bold" dir="ltr">{{ aiIndex + 1 }} / {{ aiWords.length }} today</span>
          <v-btn
            variant="text" size="default" append-icon="mdi-chevron-right"
            :disabled="aiIndex >= aiWords.length - 1" @click="nextAiWord"
          >Next</v-btn>
        </div>
        <v-row justify="center">
          <v-col cols="12" sm="10" md="8" lg="7">
            <VocabularyWordCard
              :key="currentAiWord.content_id ?? currentAiWord.word"
              large
              :word="{
                word: currentAiWord.word,
                translation_ar: currentAiWord.translation_ar,
                example: currentAiWord.example_sentence,
                example_ar: currentAiWord.example_sentence_ar,
                part_of_speech: currentAiWord.part_of_speech,
                cefr_level: currentAiWord.cefr_level,
              }"
              :image-url="aiImages[currentAiWord.content_id] || ''"
              :image-loading="!!aiImagesLoading[currentAiWord.content_id]"
              show-grading
              :grading-quality="aiGradingQuality"
              @grade="gradeAiWord"
            />
          </v-col>
        </v-row>
      </template>
      <p v-else class="text-caption text-medium-emphasis mt-3 mb-0">
        Press “Generate my words” for a personalized batch based on your level and interests.
      </p>
    </v-card>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import LearningLoader from './LearningLoader.vue'
import VocabularyWordCard from './VocabularyWordCard.vue'
import { generateAiVocabBatch, fetchVocabularyWordImage, reviewVocabularyCard } from '../../api/language.js'
import { getErrorMessage } from '../../api/client.js'

const emit = defineEmits(['graded'])

const aiWords = ref([])
const aiLoading = ref(false)
const aiError = ref('')
const aiLimitReached = ref(false)
const aiRemainingToday = ref(null)
const aiImages = ref({})
const aiImagesLoading = ref({})
const aiIndex = ref(0)
const aiGradingQuality = ref(null)

const currentAiWord = computed(() => aiWords.value[aiIndex.value] || null)

// Cap concurrent image requests (mirrors the review bank's throttle) — firing all 10 at once
// starved other in-flight requests (including the next grade/generate call) behind them.
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

async function generateAi() {
  aiLoading.value = true
  aiError.value = ''
  aiLimitReached.value = false
  try {
    const res = await generateAiVocabBatch()
    aiWords.value = res.words || []
    aiIndex.value = 0
    aiRemainingToday.value = res.remaining_today
    const withImages = aiWords.value.filter((w) => w.content_id)
    runLimited(withImages, 2, loadWordImage)
  } catch (e) {
    if (e?.response?.status === 429) {
      aiLimitReached.value = true
    } else {
      aiError.value = getErrorMessage(e, 'Could not generate your words')
    }
  } finally {
    aiLoading.value = false
  }
}

async function loadWordImage(w) {
  aiImagesLoading.value = { ...aiImagesLoading.value, [w.content_id]: true }
  try {
    const { image_url } = await fetchVocabularyWordImage(w.content_id)
    aiImages.value = { ...aiImages.value, [w.content_id]: image_url }
  } catch {
    aiImages.value = { ...aiImages.value, [w.content_id]: null }
  } finally {
    aiImagesLoading.value = { ...aiImagesLoading.value, [w.content_id]: false }
  }
}

function prevAiWord() {
  if (aiIndex.value > 0) aiIndex.value -= 1
}

function nextAiWord() {
  if (aiIndex.value < aiWords.value.length - 1) aiIndex.value += 1
}

// Grade today's word right from the single-card view, then move on — same SM-2 review
// path the review bank uses (a progress row already exists from generation time).
async function gradeAiWord(quality) {
  const w = currentAiWord.value
  if (!w?.content_id) {
    nextAiWord()
    return
  }
  aiGradingQuality.value = quality
  try {
    await reviewVocabularyCard(w.content_id, quality)
    // Let the page know a real review was recorded — this component is fully self-contained
    // (its own aiWords/aiIndex state), so nothing else refreshes the "X/10 today" tracker
    // that lives in the Review Bank tab unless we say so.
    emit('graded')
  } catch {
    /* best-effort — still advance so the student isn't stuck on a failed save */
  } finally {
    aiGradingQuality.value = null
    nextAiWord()
  }
}
</script>
