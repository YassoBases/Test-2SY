<template>
  <div>
    <template v-if="phase === 'dashboard'">
      <v-card class="promo-status pa-6 mb-4" variant="flat">
        <div class="text-overline text-medium-emphasis mb-1">
          {{ t('student.languages.writingPromotion.status.eyebrow') }}
        </div>
        <h3 class="text-h5 font-weight-bold mb-2">{{ headline }}</h3>
        <p class="text-body-2 text-medium-emphasis mb-4">{{ summary }}</p>

        <div class="stats-grid mb-4">
          <div class="stat">
            <div class="stat-label">{{ t('student.languages.writingPromotion.status.officialCefr') }}</div>
            <div class="stat-value">{{ journey?.official_writing_level || status?.readiness?.official_cefr || '—' }}</div>
          </div>
          <div class="stat">
            <div class="stat-label">{{ t('student.languages.writingPromotion.status.learningStage') }}</div>
            <div class="stat-value">{{ journey?.learning_stage_label || '—' }}</div>
          </div>
          <div class="stat">
            <div class="stat-label">{{ t('student.languages.writingPromotion.status.promotionReadiness') }}</div>
            <div class="stat-value">{{ readinessScore }}/100</div>
          </div>
          <div class="stat">
            <div class="stat-label">{{ t('student.languages.writingPromotion.status.targetCefr') }}</div>
            <div class="stat-value">{{ journey?.promotion_target || status?.eligibility?.target_cefr || '—' }}</div>
          </div>
        </div>

        <v-progress-linear
          :model-value="readinessScore"
          color="secondary"
          height="10"
          rounded
          class="mb-3"
        />

        <p v-if="estimatedRemaining != null" class="text-body-2 mb-3">
          {{ t('student.languages.writingPromotion.status.estimatedRemaining', { value: estimatedRemaining }) }}
        </p>

        <div v-if="blockers.length" class="mb-2">
          <div class="text-subtitle-2 font-weight-bold mb-2">
            {{ t('student.languages.writingPromotion.status.primaryBlocker') }}
          </div>
          <ul class="blocker-list">
            <li v-for="item in blockers" :key="item">{{ item }}</li>
          </ul>
        </div>
      </v-card>

      <div class="d-flex flex-wrap gap-3">
        <v-btn
          v-if="canStart"
          color="secondary"
          variant="flat"
          size="x-large"
          :loading="sessionLoading"
          prepend-icon="mdi-rocket-launch"
          class="px-8"
          @click="$emit('start')"
        >
          {{ t('student.languages.writingPromotion.actions.startTest', { level: targetLevel }) }}
        </v-btn>
        <v-btn
          v-else-if="hasActiveSession"
          color="secondary"
          variant="flat"
          size="x-large"
          :loading="sessionLoading"
          prepend-icon="mdi-play-circle-outline"
          class="px-8"
          @click="$emit('resume')"
        >
          {{ t('student.languages.writingPromotion.actions.resumeTest') }}
        </v-btn>
        <v-btn
          v-else
          color="secondary"
          variant="tonal"
          size="x-large"
          prepend-icon="mdi-pencil"
          class="px-8"
          @click="$emit('practice')"
        >
          {{ t('student.languages.writingPromotion.actions.keepPracticing') }}
        </v-btn>
      </div>
    </template>

    <template v-else-if="phase === 'session' && session">
      <v-card class="pa-6 mb-4" variant="flat">
        <div class="text-overline text-medium-emphasis mb-1">WPA</div>
        <h3 class="text-h6 font-weight-bold mb-4">
          {{ t('student.languages.writingPromotion.session.title', { level: session.target_cefr }) }}
        </h3>
        <div v-for="task in session.tasks" :key="task.task_id" class="task-block mb-6">
          <div class="text-subtitle-1 font-weight-bold mb-1">{{ task.genre }} · {{ task.task_type }}</div>
          <p class="text-body-2 mb-2">{{ task.prompt }}</p>
          <div class="text-caption text-medium-emphasis mb-2">
            {{ task.min_words }}–{{ task.max_words }} words
          </div>
          <v-textarea
            v-model="drafts[task.task_id]"
            :label="t('student.languages.writingPromotion.session.draftLabel')"
            rows="8"
            variant="outlined"
            auto-grow
          />
        </div>
        <div class="d-flex flex-wrap gap-2">
          <v-btn color="secondary" variant="flat" :loading="submitting" @click="$emit('submit', { ...drafts })">
            {{ t('student.languages.writingPromotion.actions.submitTest') }}
          </v-btn>
          <v-btn variant="tonal" @click="$emit('cancel')">
            {{ t('student.languages.writingPromotion.actions.cancel') }}
          </v-btn>
        </div>
      </v-card>
    </template>

    <template v-else-if="phase === 'result' && submitResult">
      <v-card class="pa-6 mb-4" variant="flat">
        <h3 class="text-h6 font-weight-bold mb-2">
          {{ submitResult.result === 'PASSED' || submitResult.result === 'PASS'
            ? t('student.languages.writingPromotion.result.passTitle')
            : t('student.languages.writingPromotion.result.failTitle') }}
        </h3>
        <p class="text-body-1 mb-4">
          {{ t('student.languages.writingPromotion.result.score', { score: submitResult.overall_score }) }}
        </p>
        <ul class="mb-4">
          <li v-for="tr in submitResult.task_results" :key="tr.task_id">
            {{ tr.task_id }}: {{ tr.score }}% — {{ tr.passed ? 'Pass' : 'Needs work' }}
          </li>
        </ul>
        <div class="d-flex flex-wrap gap-2">
          <v-btn
            v-if="submitResult.overall_passed"
            color="success"
            variant="flat"
            :loading="promoting"
            prepend-icon="mdi-stairs-up"
            @click="$emit('promote')"
          >
            {{ t('student.languages.writingPromotion.actions.promote') }}
          </v-btn>
          <v-btn variant="tonal" color="secondary" @click="$emit('back')">
            {{ t('student.languages.writingPromotion.actions.backToStatus') }}
          </v-btn>
        </div>
      </v-card>
    </template>

    <template v-else-if="phase === 'success' && promotionResult">
      <v-card class="pa-6 mb-4 success-card" variant="flat">
        <h3 class="text-h6 font-weight-bold mb-2">
          {{ t('student.languages.writingPromotion.success.title', { level: promotionResult.new_cefr }) }}
        </h3>
        <p class="text-body-1 mb-4">{{ promotionResult.summary }}</p>
        <v-btn color="secondary" variant="flat" @click="$emit('continue')">
          {{ t('student.languages.writingPromotion.actions.continue') }}
        </v-btn>
      </v-card>
    </template>
  </div>
</template>

<script setup>
import { computed, reactive, watch } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  phase: { type: String, default: 'dashboard' },
  journey: { type: Object, default: null },
  status: { type: Object, default: null },
  canStart: { type: Boolean, default: false },
  hasActiveSession: { type: Boolean, default: false },
  sessionLoading: { type: Boolean, default: false },
  session: { type: Object, default: null },
  submitting: { type: Boolean, default: false },
  submitResult: { type: Object, default: null },
  promoting: { type: Boolean, default: false },
  promotionResult: { type: Object, default: null },
})

defineEmits(['start', 'resume', 'submit', 'cancel', 'promote', 'back', 'continue', 'practice'])

const { t } = useI18n()
const drafts = reactive({})

watch(
  () => props.session?.tasks,
  (tasks) => {
    for (const task of tasks || []) {
      if (!(task.task_id in drafts)) drafts[task.task_id] = ''
    }
  },
  { immediate: true },
)

const targetLevel = computed(
  () => props.journey?.promotion_target || props.status?.eligibility?.target_cefr || '',
)
const readinessScore = computed(
  () => props.journey?.readiness_score ?? props.status?.readiness?.readiness_score ?? 0,
)
const estimatedRemaining = computed(
  () => props.journey?.estimated_lessons_remaining ?? null,
)
const blockers = computed(
  () => props.journey?.primary_blockers || props.status?.readiness?.primary_blockers || [],
)

const headline = computed(() => {
  if (props.hasActiveSession) return t('student.languages.writingPromotion.status.sessionActive')
  if (props.canStart) return t('student.languages.writingPromotion.status.eligible')
  return t('student.languages.writingPromotion.status.notEligible')
})

const summary = computed(() => {
  if (props.hasActiveSession) return t('student.languages.writingPromotion.session.resumeHint')
  if (props.canStart) return t('student.languages.writingPromotion.status.eligibleHint')
  return props.journey?.wpa_reason || props.status?.eligibility?.reason || ''
})
</script>

<style scoped>
.promo-status,
.success-card {
  border-radius: 24px;
  border: 1px solid rgba(var(--v-theme-on-surface), 0.06);
}
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 0.75rem;
}
.stat {
  padding: 0.75rem;
  border-radius: 12px;
  background: rgba(var(--v-theme-on-surface), 0.04);
}
.stat-label {
  font-size: 0.75rem;
  color: rgba(var(--v-theme-on-surface), 0.62);
}
.stat-value {
  font-weight: 700;
}
.blocker-list {
  margin: 0;
  padding-inline-start: 1.25rem;
}
.task-block {
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(var(--v-theme-on-surface), 0.08);
}
</style>
