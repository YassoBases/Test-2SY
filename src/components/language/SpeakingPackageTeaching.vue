<template>
  <section class="glass-card pa-5 pa-md-6 spk-package-panel" aria-labelledby="spk-pkg-teach-title">
    <div class="text-overline text-medium-emphasis mb-2">
      {{ t('student.languages.speakingJourney.packageLesson.section.teaching') }}
    </div>
    <h3 id="spk-pkg-teach-title" class="text-h6 font-weight-bold mb-4">
      {{ t('student.languages.speakingJourney.packageLesson.teachingTitle') }}
    </h3>

    <v-alert
      v-if="!blocks.length"
      type="info"
      variant="tonal"
      class="mb-4 rounded-lg"
      role="status"
    >
      {{ t('student.languages.speakingJourney.packageLesson.teachingEmpty') }}
    </v-alert>

    <div v-else class="spk-teach-stack mb-5">
      <article
        v-for="block in blocks"
        :key="block.block_id"
        class="spk-teach-card"
        :class="{ 'is-done': completedSet.has(block.block_id) }"
      >
        <div class="d-flex align-center justify-space-between gap-2 mb-2">
          <v-chip size="small" variant="outlined">{{ block.kind }}</v-chip>
          <v-chip
            v-if="completedSet.has(block.block_id)"
            size="x-small"
            color="success"
            variant="tonal"
          >
            {{ t('student.languages.speakingJourney.packageLesson.viewed') }}
          </v-chip>
        </div>
        <h4 class="text-subtitle-1 font-weight-bold mb-2">{{ block.title }}</h4>
        <p class="text-body-2 mb-3">{{ block.body }}</p>
        <v-btn
          size="small"
          variant="tonal"
          class="spk-pressable"
          :disabled="completedSet.has(block.block_id)"
          @click="$emit('view', block.block_id)"
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
  blocks: { type: Array, default: () => [] },
  completedIds: { type: Array, default: () => [] },
  advancing: { type: Boolean, default: false },
})
defineEmits(['view', 'continue'])
const { t } = useI18n()
const completedSet = computed(() => new Set(props.completedIds || []))
</script>
