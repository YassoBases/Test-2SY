<template>
  <div class="page-container slide-up-enter-active">
    <PageHeader eyebrow="Learn languages" eyebrow-icon="mdi-pencil" title="Writing" subtitle="Writing exercises without artificial intelligence assessment" />
    <LanguageModuleTabs />

    <v-alert v-if="focus" type="success" variant="tonal" class="mb-4 rounded-lg" density="comfortable" icon="mdi-target">
      Practising: <strong>{{ focus }}</strong>
    </v-alert>
    <v-alert v-if="loadError" type="error" variant="tonal" class="mb-4">{{ loadError }}</v-alert>
    <LoadingState v-if="loading" variant="cards" :count="3" class="mb-6" />

    <v-row v-else>
      <v-col cols="12" md="4">
        <section class="section-block">
          <div class="section-block__head">
            <h3 class="section-block__title">Exercises</h3>
          </div>
          <v-list density="comfortable" class="glass-card pa-0">
            <v-list-item
              v-for="p in prompts"
              :key="p.id"
              :active="selectedId === p.id"
              rounded="lg"
              @click="selectPrompt(p.id)"
            >
              <v-list-item-title>{{ p.title }}</v-list-item-title>
              <v-list-item-subtitle v-if="p.progress?.completed_at">complete</v-list-item-subtitle>
            </v-list-item>
          </v-list>
          <EmptyState v-if="!prompts.length" compact preset="languageExercise" />
        </section>
      </v-col>
      <v-col cols="12" md="8">
        <EmptyState
          v-if="!selectedId && prompts.length"
          compact
          icon="mdi-cursor-default-click-outline"
          title="Choose an exercise"
          description="Select an exercise from the list to begin."
        />
        <v-card v-else-if="prompt" class="glass-card pa-6" variant="flat">
          <div class="text-h6 mb-2" dir="ltr">{{ prompt.prompt }}</div>
          <div class="text-caption mb-2">minimum: {{ prompt.min_words }} words · {{ prompt.min_sentences }} sentences</div>
          <v-textarea v-model="text" rows="8" auto-grow dir="ltr" />
          <div class="text-caption mt-2">words: {{ wordCount }} · sentences: {{ sentenceCount }}</div>
          <v-alert
            v-if="validationMessage"
            type="warning"
            variant="tonal"
            density="comfortable"
            class="mt-3 rounded-lg"
            dir="ltr"
          >
            {{ validationMessage }}
          </v-alert>
          <v-btn
            color="secondary"
            class="mt-4"
            :loading="submitting"
            :disabled="!canSubmit"
            @click="submit"
          >
            Send
          </v-btn>
          <v-alert v-if="result" class="mt-4" :type="result.passed ? 'success' : 'warning'" variant="tonal">
            Result: {{ result.score_percent }}% — {{ result.passed ? 'complete' : 'Try again' }}
          </v-alert>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import PageHeader from '../../../components/common/PageHeader.vue'
import LoadingState from '../../../components/common/LoadingState.vue'
import EmptyState from '../../../components/common/EmptyState.vue'
import LanguageModuleTabs from '../../../components/language/LanguageModuleTabs.vue'
import { fetchWritingPrompt, fetchWritingPrompts, submitWritingPrompt } from '../../../api/language.js'
import { useLanguageGate } from '../../../composables/useLanguageGate.js'
import { useLanguageAccess } from '../../../composables/useLanguageAccess.js'
import {
  countWritingSentences,
  countWritingWords,
  minWordsRequiredMessage,
  validateWritingText,
} from '../../../utils/languageValidation.js'

const router = useRouter()
const route = useRoute()
const focus = ref(route.query.focus ? String(route.query.focus) : '')
const { access, loadAccess } = useLanguageAccess()
const { handleLanguageApiError, getErrorMessage } = useLanguageGate()

const prompts = ref([])
const loading = ref(true)
const loadError = ref('')
const selectedId = ref(null)
const prompt = ref(null)
const text = ref('')
const submitting = ref(false)
const result = ref(null)

const wordCount = computed(() => countWritingWords(text.value))
const sentenceCount = computed(() => countWritingSentences(text.value))

const validationMessage = computed(() => {
  if (!prompt.value || !text.value.trim()) return ''
  const check = validateWritingText(text.value, {
    minWords: prompt.value.min_words,
    minSentences: prompt.value.min_sentences,
  })
  return check.ok ? '' : check.message
})

const canSubmit = computed(() => {
  if (!prompt.value || !text.value.trim()) return false
  return validateWritingText(text.value, {
    minWords: prompt.value.min_words,
    minSentences: prompt.value.min_sentences,
  }).ok
})

onMounted(async () => {
  try {
    await loadAccess(true)
    if (access.value?.redirect) {
      router.push(access.value.redirect)
      return
    }
    const res = await fetchWritingPrompts()
    prompts.value = res.prompts || []
  } catch (e) {
    if (!handleLanguageApiError(e, access.value)) {
      loadError.value = getErrorMessage(e, 'Unable to download')
    }
  } finally {
    loading.value = false
  }
})

async function selectPrompt(id) {
  selectedId.value = id
  result.value = null
  loadError.value = ''
  try {
    prompt.value = await fetchWritingPrompt(id)
    text.value = prompt.value.progress?.submitted_text || ''
  } catch (e) {
    if (!handleLanguageApiError(e, access.value)) {
      loadError.value = getErrorMessage(e, 'Unable to load the exercise')
    }
  }
}

async function submit() {
  if (!selectedId.value || !prompt.value) return
  const check = validateWritingText(text.value, {
    minWords: prompt.value.min_words,
    minSentences: prompt.value.min_sentences,
  })
  if (!check.ok) {
    loadError.value = check.message || minWordsRequiredMessage(prompt.value.min_words)
    return
  }
  submitting.value = true
  loadError.value = ''
  try {
    result.value = await submitWritingPrompt(selectedId.value, text.value)
    const res = await fetchWritingPrompts()
    prompts.value = res.prompts || []
  } catch (e) {
    loadError.value = getErrorMessage(e, 'Unable to send')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.page-container { max-width: 1100px; margin: 0 auto; }
</style>
