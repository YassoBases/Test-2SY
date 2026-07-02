<template>
  <div class="shadowing-panel">
    <v-alert type="info" variant="tonal" class="mb-4 rounded-lg" density="comfortable">
      Listen to each sentence, then press <strong>Repeat</strong> and say it. You will get a match and
      pronunciation score.
      <v-chip v-if="level" size="x-small" color="secondary" variant="flat" class="ml-2">Level {{ level }}</v-chip>
    </v-alert>

    <v-alert v-if="focus" type="success" variant="tonal" class="mb-4 rounded-lg" density="comfortable" icon="mdi-target">
      Practising: <strong>{{ focus }}</strong>
    </v-alert>

    <div v-if="loading" class="text-center py-8">
      <v-progress-circular indeterminate color="secondary" />
    </div>

    <template v-else>
      <v-card v-if="focusItems.length" class="glass-card pa-4 mb-4" variant="flat">
        <div class="d-flex align-center gap-2 mb-3">
          <v-icon size="18" color="success">mdi-target</v-icon>
          <span class="text-subtitle-2">For your focus</span>
        </div>
        <LanguageShadowingExercise v-for="s in focusItems" :key="s.id" :target="s.text" class="mb-3" />
      </v-card>

      <v-card v-if="conversationItems.length" class="glass-card pa-4 mb-4" variant="flat">
        <div class="d-flex align-center gap-2 mb-3">
          <v-icon size="18" color="secondary">mdi-robot-happy-outline</v-icon>
          <span class="text-subtitle-2">From your conversations</span>
          <v-chip size="x-small" color="secondary" variant="tonal">your fixes</v-chip>
        </div>
        <LanguageShadowingExercise
          v-for="s in conversationItems"
          :key="s.id"
          :target="s.text"
          class="mb-3"
        />
      </v-card>

      <v-card class="glass-card pa-4" variant="flat">
        <div class="d-flex align-center gap-2 mb-3">
          <v-icon size="18" color="secondary">mdi-format-list-bulleted</v-icon>
          <span class="text-subtitle-2">Practice sentences — Level {{ level }}</span>
        </div>
        <LanguageShadowingExercise
          v-for="s in levelItems"
          :key="s.id"
          :target="s.text"
          class="mb-3"
        />
        <p v-if="!levelItems.length" class="text-body-2 text-medium-emphasis mb-0">
          No practice sentences available yet.
        </p>
      </v-card>
    </template>

    <v-alert v-if="error" type="error" variant="tonal" class="rounded-lg mt-3">{{ error }}</v-alert>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import LanguageShadowingExercise from './LanguageShadowingExercise.vue'
import { fetchShadowSentences } from '../../api/language.js'
import { getErrorMessage } from '../../api/client.js'

const route = useRoute()
const focus = ref(route.query.focus ? String(route.query.focus) : '')
const sentences = ref([])
const level = ref('')
const loading = ref(true)
const error = ref('')

const focusItems = computed(() => sentences.value.filter((s) => s.source === 'focus'))
const conversationItems = computed(() => sentences.value.filter((s) => s.source === 'conversation'))
const levelItems = computed(() => sentences.value.filter((s) => s.source === 'level'))

onMounted(async () => {
  try {
    const data = await fetchShadowSentences(focus.value || undefined)
    sentences.value = data.sentences || []
    level.value = data.level || ''
  } catch (e) {
    error.value = getErrorMessage(e, 'Could not load shadowing sentences')
  } finally {
    loading.value = false
  }
})
</script>
