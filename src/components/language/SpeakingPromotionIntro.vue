<template>
  <div class="speaking-promotion-intro speaking-runtime">
    <v-card class="glass-card pa-6 mb-4" variant="flat">
      <div class="text-overline text-medium-emphasis mb-1">
        {{ t('student.languages.speakingJourney.assessment.eyebrow') }}
      </div>
      <h2 class="text-h5 font-weight-bold mb-2">
        {{ t('student.languages.speakingJourney.assessment.intro.title') }}
      </h2>
      <p class="text-body-2 text-medium-emphasis mb-4">
        {{ t('student.languages.speakingJourney.assessment.intro.lead') }}
      </p>

      <v-row dense class="mb-4">
        <v-col cols="6" sm="3">
          <div class="stat-label">{{ t('student.languages.speakingJourney.assessment.source') }}</div>
          <div class="stat-value" dir="ltr">{{ sourceCefr || '—' }}</div>
        </v-col>
        <v-col cols="6" sm="3">
          <div class="stat-label">{{ t('student.languages.speakingJourney.assessment.target') }}</div>
          <div class="stat-value" dir="ltr">{{ targetCefr || '—' }}</div>
        </v-col>
        <v-col cols="6" sm="3">
          <div class="stat-label">{{ t('student.languages.speakingJourney.assessment.duration') }}</div>
          <div class="stat-value">
            {{
              estimatedDurationSeconds
                ? t('student.languages.speakingJourney.assessment.durationValue', {
                    minutes: Math.ceil(estimatedDurationSeconds / 60),
                  })
                : '—'
            }}
          </div>
        </v-col>
        <v-col cols="6" sm="3">
          <div class="stat-label">{{ t('student.languages.speakingJourney.assessment.intro.tasks') }}</div>
          <div class="stat-value">
            {{ t('student.languages.speakingJourney.assessment.taskCount', { n: taskCount }) }}
          </div>
        </v-col>
      </v-row>

      <v-alert
        type="info"
        variant="tonal"
        density="comfortable"
        class="mb-4 rounded-lg"
        prepend-icon="mdi-information-outline"
      >
        {{ t('student.languages.speakingJourney.assessment.intro.instructions') }}
      </v-alert>

      <v-alert
        type="success"
        variant="tonal"
        density="comfortable"
        class="mb-4 rounded-lg"
        prepend-icon="mdi-timer-sand"
      >
        {{ t('student.languages.speakingJourney.assessment.intro.preparation') }}
      </v-alert>

      <v-alert
        v-if="hasInteractionGaps"
        type="warning"
        variant="tonal"
        density="comfortable"
        class="mb-4 rounded-lg"
        prepend-icon="mdi-account-voice-off"
      >
        {{ t('student.languages.speakingJourney.assessment.interactionGapNote') }}
      </v-alert>

      <v-alert v-if="sessionError" type="error" variant="tonal" class="mb-4 rounded-lg" role="alert">
        {{ sessionError }}
      </v-alert>

      <div class="d-flex flex-wrap gap-2">
        <v-btn
          color="primary"
          class="em-btn em-btn--primary spk-pressable"
          prepend-icon="mdi-play"
          :loading="loading"
          :aria-label="t('student.languages.speakingJourney.assessment.intro.begin')"
          @click="$emit('begin')"
        >
          {{ t('student.languages.speakingJourney.assessment.intro.begin') }}
        </v-btn>
        <v-btn
          variant="tonal"
          class="spk-pressable"
          :disabled="loading"
          @click="$emit('back')"
        >
          {{ t('student.languages.speakingJourney.assessment.intro.back') }}
        </v-btn>
      </div>
    </v-card>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

defineProps({
  sourceCefr: { type: String, default: null },
  targetCefr: { type: String, default: null },
  estimatedDurationSeconds: { type: Number, default: 0 },
  taskCount: { type: Number, default: 0 },
  hasInteractionGaps: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
  sessionError: { type: String, default: '' },
})

defineEmits(['begin', 'back'])

const { t } = useI18n()
</script>

<style scoped>
.stat-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: rgba(var(--v-theme-on-surface), 0.6);
}
.stat-value {
  font-size: 1.1rem;
  font-weight: 800;
}
</style>
