<template>
  <section class="section-block mb-4">
    <div class="section-block__head">
      <h3 class="section-block__title">Vocabulary generator</h3>
      <div class="section-block__subtitle">Endless fresh words — pick a topic and level. Works offline.</div>
    </div>
    <v-card class="glass-card pa-4" variant="flat">
      <div class="d-flex flex-wrap gap-3 align-center">
        <v-select
          v-model="topic" :items="topics" label="Topic" clearable density="comfortable"
          variant="outlined" hide-details style="min-width: 180px"
        />
        <v-select
          v-model="level" :items="levels" label="CEFR level" clearable density="comfortable"
          variant="outlined" hide-details style="min-width: 150px"
        />
        <v-btn color="secondary" variant="flat" :loading="loading" prepend-icon="mdi-shuffle-variant" @click="generate">
          Generate new batch
        </v-btn>
      </div>

      <div v-if="loading" class="mt-4"><LearningLoader compact :title="''" icon="mdi-cards" /></div>
      <v-alert v-else-if="error" type="error" variant="tonal" class="mt-3 mb-0">{{ error }}</v-alert>
      <div v-else-if="mastered" class="mt-5 text-center">
        <v-icon size="40" color="success" class="mb-2">mdi-trophy-outline</v-icon>
        <p class="text-body-1 mb-0">{{ message }}</p>
      </div>
      <v-row v-else-if="words.length" class="mt-1" dir="ltr">
        <v-col v-for="w in words" :key="w.id" cols="12" sm="6" md="4">
          <v-card class="glass-card pa-3 word-card" variant="flat">
            <div class="d-flex align-center justify-space-between mb-1">
              <span class="text-subtitle-1 font-weight-bold">{{ w.word }}</span>
              <v-chip size="x-small" color="secondary" variant="tonal">{{ w.cefr_level }}</v-chip>
            </div>
            <div class="text-caption text-medium-emphasis mb-1">{{ w.part_of_speech }} · {{ w.context_theme }}</div>
            <div v-if="w.translation" class="text-body-2 mb-1" dir="auto">{{ w.translation }}</div>
            <p class="text-body-2 mb-1">{{ w.definition }}</p>
            <p v-if="w.example_sentence" class="text-caption text-medium-emphasis mb-0"><em>{{ w.example_sentence }}</em></p>
          </v-card>
        </v-col>
      </v-row>
      <p v-else class="text-caption text-medium-emphasis mt-3 mb-0">
        Choose a topic/level (optional) and press “Generate new batch”.
      </p>
    </v-card>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import LearningLoader from './LearningLoader.vue'
import { fetchVocabGeneratorOptions, generateVocabBatch } from '../../api/language.js'
import { getErrorMessage } from '../../api/client.js'

const topics = ref([])
const levels = ref([])
const topic = ref(null)
const level = ref(null)
const words = ref([])
const mastered = ref(false)
const message = ref('')
const loading = ref(false)
const error = ref('')

onMounted(async () => {
  try {
    const opts = await fetchVocabGeneratorOptions()
    topics.value = opts.topics || []
    levels.value = opts.levels || []
  } catch {
    /* options are best-effort; generate still works with no filter */
  }
})

async function generate() {
  loading.value = true
  error.value = ''
  mastered.value = false
  try {
    const res = await generateVocabBatch({ topic: topic.value, level: level.value })
    words.value = res.words || []
    mastered.value = !!res.mastered
    message.value = res.message || ''
  } catch (e) {
    error.value = getErrorMessage(e, 'Could not generate a batch')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.word-card { height: 100%; transition: transform 0.15s ease; }
.word-card:hover { transform: translateY(-3px); }
</style>
