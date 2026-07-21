<template>
  <section class="glass-card pa-5 pa-md-6 spk-package-panel" aria-labelledby="spk-pkg-mini-title">
    <div class="text-overline text-medium-emphasis mb-2">
      {{ t('student.languages.speakingJourney.packageLesson.section.mini_practice') }}
    </div>
    <h3 id="spk-pkg-mini-title" class="text-h6 font-weight-bold mb-2">
      {{ t('student.languages.speakingJourney.packageLesson.miniTitle') }}
    </h3>
    <p class="text-body-2 text-medium-emphasis mb-4">
      {{ t('student.languages.speakingJourney.packageLesson.miniLead') }}
    </p>

    <div class="spk-mini-prep mb-5">
      <template v-if="storySpine?.continuation_hook || storySpine?.decision_point">
        <h4 class="text-subtitle-2 font-weight-bold mb-2">
          {{ t('student.languages.speakingJourney.packageLesson.miniPrompt') }}
        </h4>
        <p class="text-body-1 mb-2">
          {{ storySpine.continuation_hook || mini?.prompt || '—' }}
        </p>
        <p v-if="storySpine.decision_point" class="text-body-2 mb-3">
          {{ storySpine.decision_point }}
        </p>
        <p v-if="storySpine.setting || (storySpine.characters || []).length" class="text-caption text-medium-emphasis mb-0">
          {{ storySpine.setting }}
          <span v-if="(storySpine.characters || []).length">
            ·
            {{
              (storySpine.characters || [])
                .map((c) => c.name || c)
                .filter(Boolean)
                .join(', ')
            }}
          </span>
        </p>
      </template>
      <template v-else>
        <h4 class="text-subtitle-2 font-weight-bold mb-2">
          {{ t('student.languages.speakingJourney.packageLesson.miniPrompt') }}
        </h4>
        <p class="text-body-1 mb-3">{{ mini?.prompt || '—' }}</p>
        <h4 class="text-subtitle-2 font-weight-bold mb-2">
          {{ t('student.languages.speakingJourney.packageLesson.miniScaffold') }}
        </h4>
        <p class="text-body-2 text-medium-emphasis mb-0">{{ mini?.scaffold || '—' }}</p>
      </template>
    </div>

    <v-alert type="warning" variant="tonal" class="mb-4 rounded-lg" role="status">
      {{ t('student.languages.speakingJourney.packageLesson.miniNoRecord') }}
    </v-alert>

    <div class="d-flex flex-wrap gap-3">
      <v-btn
        variant="tonal"
        class="spk-pressable"
        :disabled="prepDone"
        @click="$emit('prep-complete')"
      >
        {{
          prepDone
            ? t('student.languages.speakingJourney.packageLesson.miniPrepDone')
            : t('student.languages.speakingJourney.packageLesson.miniMarkReady')
        }}
      </v-btn>
      <v-btn
        color="primary"
        size="large"
        class="spk-pressable"
        :loading="advancing"
        :disabled="!prepDone"
        @click="$emit('continue')"
      >
        {{ t('student.languages.speakingJourney.packageLesson.finishLesson') }}
      </v-btn>
    </div>
  </section>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

defineProps({
  mini: { type: Object, default: null },
  storySpine: { type: Object, default: null },
  prepDone: { type: Boolean, default: false },
  advancing: { type: Boolean, default: false },
})
defineEmits(['prep-complete', 'continue'])
const { t } = useI18n()
</script>
