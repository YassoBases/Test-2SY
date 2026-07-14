<template>
  <v-dialog
    :model-value="show"
    persistent
    max-width="460"
    class="processing-modal"
    scrim="rgba(4, 8, 20, 0.85)"
  >
    <v-card class="processing-card pa-8 pa-md-10 text-center" rounded="xl">
      <div class="ai-ring mx-auto mb-8">
        <div class="ai-ring__orbit" />
        <div class="ai-ring__orbit ai-ring__orbit--inner" />
        <div class="ai-ring__core">
          <EduSparkBrandIcon context="loading" />
        </div>
      </div>

      <span class="section-eyebrow section-eyebrow--center mb-2">
        <v-icon size="14" class="me-1">mdi-creation</v-icon>
        {{ $t('teacher.processing.aiWorking') }}
      </span>
      <h3 class="section-title text-h5 mb-2">{{ title || t('teacher.processing.lessonTitle') }}</h3>
      <p class="section-subtitle mx-auto mb-8">
        {{ subtitle || `${t('teacher.processing.extractFrom')} PDF ${t('teacher.processing.voiceAnalysis')}` }}
      </p>

      <v-progress-linear
        :model-value="progress"
        height="10"
        rounded
        class="progress-glow mb-3"
        color="primary"
        bg-color="rgba(124, 108, 240, 0.15)"
      />

      <div class="d-flex align-center justify-space-between text-caption mb-4">
        <span class="text-medium-emphasis">{{ stepLabel }}</span>
        <v-chip color="secondary" variant="tonal" size="x-small" class="font-weight-bold">
          {{ progress }}%
        </v-chip>
      </div>

      <div class="processing-steps d-flex justify-center gap-2 flex-wrap">
        <v-chip
          v-for="(_, i) in 5"
          :key="i"
          :color="step >= i ? 'primary' : undefined"
          :variant="step >= i ? 'flat' : 'outlined'"
          size="x-small"
          :class="{ 'step-dot--done': step > i }"
        >
          {{ i + 1 }}
        </v-chip>
      </div>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import EduSparkBrandIcon from '../common/EduSparkBrandIcon.vue'

const props = defineProps({
  show: { type: Boolean, default: false },
  progress: { type: Number, default: 0 },
  step: { type: Number, default: 0 },
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' },
})

const steps = computed(() => [
  `${t('teacher.processing.readFile')} PDF...`,
  t('teacher.processing.extractText'),
  t('teacher.processing.analyzeVoice'),
  t('teacher.processing.buildStyle'),
  t('teacher.processing.prepareTeacher'),
])

const stepLabel = computed(() => steps.value[props.step] ?? steps.value[0])
</script>

<style scoped>
.processing-steps :deep(.v-chip) {
  min-width: 32px;
  justify-content: center;
}

.step-dot--done {
  box-shadow: 0 0 12px rgba(34, 211, 238, 0.4);
}
</style>
