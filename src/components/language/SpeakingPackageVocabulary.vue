<template>
  <section class="glass-card pa-5 pa-md-6 spk-package-panel" aria-labelledby="spk-pkg-vocab-title">
    <div class="text-overline text-medium-emphasis mb-2">
      {{ t('student.languages.speakingJourney.packageLesson.section.vocabulary') }}
    </div>
    <h3 id="spk-pkg-vocab-title" class="text-h6 font-weight-bold mb-4">
      {{ t('student.languages.speakingJourney.packageLesson.vocabTitle') }}
    </h3>

    <v-alert
      v-if="!entries.length"
      type="info"
      variant="tonal"
      class="mb-4 rounded-lg"
      role="status"
    >
      {{ t('student.languages.speakingJourney.packageLesson.vocabEmpty') }}
    </v-alert>

    <div v-else class="spk-vocab-grid mb-5">
      <article
        v-for="entry in entries"
        :key="entry.vocabulary_id"
        class="spk-vocab-card"
        :class="{ 'is-viewed': viewedSet.has(entry.vocabulary_id) }"
      >
        <div class="d-flex align-start justify-space-between gap-2 mb-2">
          <h4 class="text-subtitle-1 font-weight-bold mb-0">{{ entry.surface }}</h4>
          <v-chip
            v-if="viewedSet.has(entry.vocabulary_id)"
            size="x-small"
            color="success"
            variant="tonal"
          >
            {{ t('student.languages.speakingJourney.packageLesson.viewed') }}
          </v-chip>
        </div>
        <p class="text-body-2 mb-2">
          <strong>{{ t('student.languages.speakingJourney.packageLesson.gloss') }}:</strong>
          {{ entry.brief_gloss }}
        </p>
        <p v-if="entry.example_reuse" class="text-body-2 text-medium-emphasis mb-3">
          <strong>{{ t('student.languages.speakingJourney.packageLesson.usage') }}:</strong>
          {{ entry.example_reuse }}
        </p>
        <p class="text-caption text-medium-emphasis mb-3">
          {{
            t('student.languages.speakingJourney.packageLesson.contextRef', {
              ref: entry.context_span_ref || '—',
            })
          }}
        </p>
        <v-btn
          size="small"
          variant="tonal"
          class="spk-pressable"
          :disabled="viewedSet.has(entry.vocabulary_id)"
          @click="$emit('view', entry.vocabulary_id)"
        >
          {{ t('student.languages.speakingJourney.packageLesson.markViewed') }}
        </v-btn>
      </article>
    </div>

    <v-btn color="primary" size="large" class="spk-pressable" :loading="advancing" @click="$emit('continue')">
      {{ t('student.languages.speakingJourney.packageLesson.continue') }}
    </v-btn>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  entries: { type: Array, default: () => [] },
  viewedIds: { type: Array, default: () => [] },
  advancing: { type: Boolean, default: false },
})
defineEmits(['view', 'continue'])
const { t } = useI18n()
const viewedSet = computed(() => new Set(props.viewedIds || []))
</script>
