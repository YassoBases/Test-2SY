<template>
  <section class="glass-card pa-5 pa-md-6 spk-package-panel text-center" aria-labelledby="spk-pkg-done-title">
    <v-icon color="success" size="48" class="mb-3" aria-hidden="true">mdi-check-circle</v-icon>
    <h3 id="spk-pkg-done-title" class="text-h5 font-weight-bold mb-2">
      {{ t('student.languages.speakingJourney.packageLesson.completeTitle') }}
    </h3>
    <p class="text-body-1 text-medium-emphasis mb-2">
      {{
        t('student.languages.speakingJourney.packageLesson.completeBody', {
          title: title || '',
        })
      }}
    </p>
    <v-alert
      v-if="ready"
      type="success"
      variant="tonal"
      class="mb-5 rounded-lg text-start"
      role="status"
    >
      {{ t('student.languages.speakingJourney.packageLesson.readyForDiscussion') }}
    </v-alert>
    <div class="d-flex flex-wrap justify-center gap-3">
      <v-btn color="primary" class="spk-pressable" @click="$emit('start-discussion')">
        {{ t('student.languages.speakingJourney.packageLesson.startDiscussion') }}
      </v-btn>
      <v-btn variant="tonal" class="spk-pressable" @click="$emit('restart')">
        {{ t('student.languages.speakingJourney.packageLesson.restart') }}
      </v-btn>
    </div>
  </section>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

defineProps({
  ready: { type: Boolean, default: false },
  title: { type: String, default: '' },
})
defineEmits(['restart', 'start-discussion'])
const { t } = useI18n()
</script>
