<template>
  <div class="page-container slide-up-enter-active">
    <PageHeader
      eyebrow="Learn languages"
      eyebrow-icon="mdi-book-alphabet"
      title="Dictionary"
      :subtitle="totalWords ? `Search ${totalWords.toLocaleString()} English words` : 'Search English words, meanings and synonyms'"
    />
    <LanguageModuleTabs />

    <v-alert v-if="loadError" type="error" variant="tonal" class="mb-4 rounded-lg">{{ loadError }}</v-alert>

    <v-card class="glass-card pa-4 mb-4" variant="flat">
      <div class="d-flex gap-2">
        <v-text-field
          v-model="query" density="compact" variant="outlined" hide-details
          placeholder="Type a word…" dir="ltr" autofocus :loading="busy"
          prepend-inner-icon="mdi-magnify" @update:model-value="onType" @keyup.enter="lookup(query)"
        />
      </div>
      <!-- suggestions -->
      <div v-if="suggestions.length && !entries.length" class="d-flex flex-wrap gap-1 mt-3">
        <v-chip
          v-for="(w, i) in suggestions" :key="i" size="small" variant="tonal"
          @click="lookup(w)"
        >{{ w }}</v-chip>
      </div>
    </v-card>

    <!-- entries -->
    <template v-if="entries.length">
      <div class="text-h5 font-weight-bold mb-2" dir="ltr">{{ activeWord }}</div>
      <v-card v-for="(e, i) in entries" :key="i" class="glass-card pa-4 mb-3" variant="flat" dir="ltr">
        <v-chip size="x-small" color="secondary" variant="tonal" class="mb-2">{{ e.part_of_speech }}</v-chip>
        <p class="text-body-1 mb-2">{{ e.definition }}</p>
        <div v-if="e.examples?.length" class="mb-2">
          <div v-for="(ex, xi) in e.examples" :key="xi" class="text-body-2 text-medium-emphasis">“{{ ex }}”</div>
        </div>
        <div v-if="e.synonyms?.length" class="d-flex flex-wrap gap-1 align-center">
          <span class="text-caption text-medium-emphasis me-1">Synonyms:</span>
          <v-chip
            v-for="(s, si) in e.synonyms" :key="si" size="x-small" variant="outlined"
            @click="lookup(s)"
          >{{ s }}</v-chip>
        </div>
      </v-card>
    </template>

    <v-card v-else-if="searched && !busy && !suggestions.length" class="glass-card pa-6 text-center" variant="flat">
      <v-icon size="40" color="medium-emphasis" class="mb-2">mdi-book-search-outline</v-icon>
      <p class="text-body-2 text-medium-emphasis mb-0">No results for “{{ query }}”. Check the spelling and try again.</p>
    </v-card>

    <v-card v-else-if="!searched" class="glass-card pa-6 text-center" variant="flat">
      <v-icon size="40" color="medium-emphasis" class="mb-2">mdi-book-open-variant</v-icon>
      <p class="text-body-2 text-medium-emphasis mb-0">Type any English word to see its meaning, examples and synonyms.</p>
    </v-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import PageHeader from '../../../components/common/PageHeader.vue'
import LanguageModuleTabs from '../../../components/language/LanguageModuleTabs.vue'
import { searchDictionary } from '../../../api/language.js'
import { getErrorMessage } from '../../../api/client.js'

const query = ref('')
const entries = ref([])
const suggestions = ref([])
const activeWord = ref('')
const totalWords = ref(0)
const busy = ref(false)
const searched = ref(false)
const loadError = ref('')

let typeTimer = null

function onType() {
  entries.value = []
  clearTimeout(typeTimer)
  const q = query.value.trim()
  if (!q) {
    suggestions.value = []
    searched.value = false
    return
  }
  typeTimer = setTimeout(() => runSearch(q, false), 250)
}

async function runSearch(q, exact) {
  busy.value = true
  loadError.value = ''
  try {
    const data = await searchDictionary(q)
    totalWords.value = data.total_words || totalWords.value
    suggestions.value = data.suggestions || []
    entries.value = exact ? data.entries || [] : []
    searched.value = true
  } catch (e) {
    loadError.value = getErrorMessage(e, 'Dictionary search failed')
  } finally {
    busy.value = false
  }
}

async function lookup(word) {
  if (!word) return
  query.value = word
  clearTimeout(typeTimer)
  busy.value = true
  loadError.value = ''
  try {
    const data = await searchDictionary(word)
    totalWords.value = data.total_words || totalWords.value
    entries.value = data.entries || []
    suggestions.value = entries.value.length ? [] : data.suggestions || []
    activeWord.value = data.query || word
    searched.value = true
  } catch (e) {
    loadError.value = getErrorMessage(e, 'Dictionary search failed')
  } finally {
    busy.value = false
  }
}
</script>

<style scoped>
.page-container {
  max-width: 720px;
  margin: 0 auto;
}
</style>
