<template>
  <v-card v-if="hasAnalysis" class="teacher-panel pa-6 mb-4" variant="flat">
    <div class="d-flex align-center gap-2 mb-4">
      <v-icon color="primary" size="28">mdi-school-outline</v-icon>
      <div>
        <div class="text-overline text-medium-emphasis">{{ t('student.languages.writingJourney.teacher.eyebrow') }}</div>
        <h3 class="text-h6 font-weight-bold mb-0">{{ t('student.languages.writingJourney.teacher.title') }}</h3>
      </div>
      <v-chip
        v-if="analysis.cefr_estimate"
        color="primary"
        variant="tonal"
        size="small"
        class="ms-auto"
      >
        {{ t('student.languages.writingJourney.teacher.cefrChip', { level: analysis.cefr_estimate }) }}
      </v-chip>
    </div>

    <v-alert
      v-if="analysis.encouragement"
      type="info"
      variant="tonal"
      density="comfortable"
      class="mb-4 rounded-lg"
      icon="mdi-hand-heart-outline"
      dir="ltr"
    >
      {{ analysis.encouragement }}
    </v-alert>

    <div v-if="analysis.cefr_reason" class="section mb-4">
      <div class="section-title">{{ t('student.languages.writingJourney.teacher.cefrTitle') }}</div>
      <p class="text-body-2 mb-0" dir="ltr">{{ analysis.cefr_reason }}</p>
    </div>

    <div v-if="dimensionRows.length" class="section mb-4">
      <div class="section-title">{{ t('student.languages.writingJourney.teacher.dimensionsTitle') }}</div>
      <div v-for="row in dimensionRows" :key="row.key" class="dimension-row">
        <span class="dimension-label">{{ row.label }}</span>
        <span class="text-body-2 text-medium-emphasis" dir="ltr">{{ row.value }}</span>
      </div>
    </div>

    <div v-if="analysis.grammar_notes?.length" class="section mb-4">
      <div class="section-title">{{ t('student.languages.writingJourney.teacher.grammarTitle') }}</div>
      <div v-for="(note, idx) in analysis.grammar_notes" :key="`g-${idx}`" class="grammar-note">
        <div class="text-body-2 font-weight-medium" dir="ltr">{{ note.issue }}</div>
        <div v-if="note.rule" class="grammar-line" dir="ltr">
          <strong>{{ t('student.languages.writingJourney.teacher.rule') }}:</strong> {{ note.rule }}
        </div>
        <div v-if="note.fix" class="grammar-line" dir="ltr">
          <strong>{{ t('student.languages.writingJourney.teacher.fix') }}:</strong> {{ note.fix }}
        </div>
        <div v-if="note.example" class="grammar-line grammar-example" dir="ltr">
          <strong>{{ t('student.languages.writingJourney.teacher.example') }}:</strong> {{ note.example }}
        </div>
      </div>
    </div>

    <div v-if="hasVocabulary" class="section mb-4">
      <div class="section-title">{{ t('student.languages.writingJourney.teacher.vocabularyTitle') }}</div>
      <p v-if="analysis.vocabulary_range" class="text-body-2 mb-2" dir="ltr">{{ analysis.vocabulary_range }}</p>
      <div v-if="analysis.repeated_words?.length" class="mb-2">
        <span class="text-caption text-medium-emphasis me-2">{{ t('student.languages.writingJourney.teacher.repeated') }}:</span>
        <v-chip v-for="w in analysis.repeated_words" :key="`r-${w}`" size="x-small" variant="tonal" color="warning" class="me-1">{{ w }}</v-chip>
      </div>
      <div v-if="analysis.missing_topic_words?.length" class="mb-2">
        <span class="text-caption text-medium-emphasis me-2">{{ t('student.languages.writingJourney.teacher.missing') }}:</span>
        <v-chip v-for="w in analysis.missing_topic_words" :key="`m-${w}`" size="x-small" variant="tonal" color="primary" class="me-1">{{ w }}</v-chip>
      </div>
      <ul v-if="analysis.vocabulary_suggestions?.length" class="tip-list">
        <li v-for="(s, idx) in analysis.vocabulary_suggestions" :key="`vs-${idx}`" dir="ltr">{{ s }}</li>
      </ul>
    </div>

    <div v-if="analysis.progress_comparison" class="section mb-4">
      <div class="section-title">{{ t('student.languages.writingJourney.teacher.progressTitle') }}</div>
      <p class="text-body-2 mb-0" dir="ltr">{{ analysis.progress_comparison }}</p>
    </div>

    <div v-if="analysis.learning_diagnosis" class="diagnosis-box mb-3">
      <v-icon color="primary" size="20" class="me-2">mdi-lightbulb-on-outline</v-icon>
      <span class="text-body-2" dir="ltr">{{ analysis.learning_diagnosis }}</span>
    </div>

    <div v-if="analysis.revision_priority" class="mission-box">
      <v-icon color="secondary" size="20" class="me-2">mdi-target</v-icon>
      <span class="text-body-2 font-weight-medium" dir="ltr">{{ analysis.revision_priority }}</span>
    </div>

    <div v-if="provenance" class="provenance mt-4" dir="ltr">
      <v-icon size="14" class="me-1">mdi-shield-check-outline</v-icon>
      {{ provenance }}
    </div>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  analysis: { type: Object, default: null },
})

const { t } = useI18n()

const hasAnalysis = computed(() => Boolean(props.analysis?.available))

const hasVocabulary = computed(() => {
  const a = props.analysis
  if (!a) return false
  return Boolean(
    a.vocabulary_range ||
      a.repeated_words?.length ||
      a.missing_topic_words?.length ||
      a.vocabulary_suggestions?.length,
  )
})

const provenance = computed(() => {
  const a = props.analysis
  if (!a || !a.provider) return ''
  const parts = [a.provider]
  if (a.model_name) parts.push(a.model_name)
  if (a.analyzer_version) parts.push(`v${a.analyzer_version}`)
  return t('student.languages.writingJourney.teacher.analysedBy', { info: parts.join(' · ') })
})

const dimensionRows = computed(() => {
  const a = props.analysis
  if (!a) return []
  const keys = [
    ['task_response', 'taskResponse'],
    ['topic_understanding', 'topic'],
    ['idea_development', 'ideaDevelopment'],
    ['organization', 'organization'],
    ['coherence', 'coherence'],
    ['goal_alignment', 'goalAlignment'],
    ['vocabulary', 'vocabulary'],
  ]
  return keys
    .filter(([field]) => a[field])
    .map(([field, labelKey]) => ({
      key: field,
      label: t(`student.languages.writingJourney.teacher.dim.${labelKey}`),
      value: a[field],
    }))
})
</script>

<style scoped>
.teacher-panel {
  border-radius: 20px;
  border: 1px solid rgba(var(--v-theme-primary), 0.14);
}
.section-title {
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: rgba(var(--v-theme-on-surface), 0.6);
  margin-bottom: 0.5rem;
}
.dimension-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem 0.75rem;
  padding: 0.4rem 0;
  border-bottom: 1px dashed rgba(var(--v-theme-on-surface), 0.08);
}
.dimension-label {
  font-weight: 600;
  min-width: 8rem;
}
.grammar-note {
  padding: 0.65rem 0.85rem;
  border-radius: 12px;
  background: rgba(var(--v-theme-warning), 0.06);
  margin-bottom: 0.6rem;
}
.grammar-line {
  font-size: 0.85rem;
  margin-top: 0.15rem;
}
.grammar-example {
  font-style: italic;
}
.tip-list {
  margin: 0.25rem 0 0;
  padding-inline-start: 1.25rem;
}
.diagnosis-box,
.mission-box {
  display: flex;
  align-items: flex-start;
  padding: 0.75rem 0.9rem;
  border-radius: 12px;
}
.diagnosis-box {
  background: rgba(var(--v-theme-primary), 0.06);
}
.mission-box {
  background: rgba(var(--v-theme-secondary), 0.08);
}
.provenance {
  font-size: 0.72rem;
  color: rgba(var(--v-theme-on-surface), 0.5);
  display: flex;
  align-items: center;
}
</style>
