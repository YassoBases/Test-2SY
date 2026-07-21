<template>
  <div
    class="spk-guided-discussion speaking-runtime"
    role="region"
    :aria-label="t('student.languages.speakingJourney.discussion.region')"
  >
    <LoadingState
      v-if="loading && !state"
      variant="cards"
      :count="2"
      :label="t('student.languages.speakingJourney.discussion.loading')"
      class="mb-4"
    />

    <v-alert
      v-if="error"
      type="error"
      variant="tonal"
      class="mb-4 rounded-lg"
      role="alert"
    >
      {{ error }}
      <template #append>
        <v-btn size="small" variant="text" class="spk-pressable" @click="$emit('retry')">
          {{ t('student.languages.speakingJourney.runtime.retry') }}
        </v-btn>
      </template>
    </v-alert>

    <v-alert
      v-if="!state && !loading"
      type="info"
      variant="tonal"
      class="mb-4 rounded-lg"
      role="status"
    >
      <div class="text-subtitle-2 font-weight-bold mb-1">
        {{ t('student.languages.speakingJourney.discussion.emptyTitle') }}
      </div>
      <p class="text-body-2 mb-3">
        {{
          needsLesson
            ? t('student.languages.speakingJourney.discussion.finishLessonFirst')
            : t('student.languages.speakingJourney.discussion.emptyBody')
        }}
      </p>
      <div class="d-flex flex-wrap gap-2">
        <v-btn
          v-if="needsLesson"
          color="primary"
          class="spk-pressable"
          @click="$emit('go-lesson')"
        >
          {{ t('student.languages.speakingJourney.discussion.goToLesson') }}
        </v-btn>
        <v-btn
          color="primary"
          :variant="needsLesson ? 'tonal' : 'flat'"
          class="spk-pressable"
          :loading="loading"
          @click="$emit('open')"
        >
          {{ t('student.languages.speakingJourney.discussion.start') }}
        </v-btn>
      </div>
    </v-alert>

    <template v-if="state">
      <header class="spk-disc-header mb-4">
        <div class="spk-disc-header__meta">
          <span class="spk-disc-header__eyebrow">
            {{ t('student.languages.speakingJourney.discussion.eyebrow') }}
          </span>
          <h2 class="spk-disc-header__title" dir="ltr">{{ packageTitle }}</h2>
          <p class="spk-disc-header__progress">
            {{
              t('student.languages.speakingJourney.discussion.progress', {
                current: Math.min(stepIndex + 1, stepsTotal || 1),
                total: stepsTotal || 1,
              })
            }}
          </p>
          <v-progress-linear
            :model-value="progressPercent"
            color="primary"
            height="6"
            rounded
            class="mt-2"
          />
        </div>
        <div class="spk-disc-header__status" :class="`is-${voiceMode || 'idle'}`">
          {{ statusLabel }}
        </div>
      </header>

      <!-- Featured tutor question + obvious listen control -->
      <section
        v-if="!completed && latestTutorText"
        class="spk-disc-question mb-4"
        aria-live="polite"
      >
        <div class="spk-disc-question__label">
          {{ t('student.languages.speakingJourney.discussion.currentQuestion') }}
        </div>
        <p class="spk-disc-question__text" dir="ltr">{{ latestTutorText }}</p>
        <div class="spk-disc-question__actions">
          <v-btn
            color="primary"
            size="large"
            rounded="lg"
            class="spk-pressable"
            :disabled="!hasTutorAudio || voiceMode === 'recording'"
            :loading="voiceMode === 'partner_speaking'"
            @click="$emit('replay-audio')"
          >
            <v-icon start>
              {{ voiceMode === 'partner_speaking' ? 'mdi-volume-high' : 'mdi-play-circle' }}
            </v-icon>
            {{
              voiceMode === 'partner_speaking'
                ? t('student.languages.speakingJourney.discussion.tutorSpeaking')
                : hasTutorAudio
                  ? t('student.languages.speakingJourney.discussion.listenAgain')
                  : t('student.languages.speakingJourney.discussion.audioPreparing')
            }}
          </v-btn>
          <p v-if="!hasTutorAudio" class="spk-disc-question__hint mb-0">
            {{ t('student.languages.speakingJourney.discussion.audioPreparingHint') }}
          </p>
        </div>
      </section>

      <section
        class="spk-disc-thread mb-4"
        :aria-label="t('student.languages.speakingJourney.discussion.thread')"
      >
        <article
          v-for="(turn, idx) in displayTurns"
          :key="`${turn.role}-${idx}-${turn.created_at || idx}`"
          class="spk-disc-turn"
          :class="`spk-disc-turn--${turn.role}`"
        >
          <div class="spk-disc-turn__role">
            {{ t(`student.languages.speakingJourney.discussion.role.${turn.role}`, turn.role) }}
          </div>
          <p class="spk-disc-turn__text" dir="ltr">{{ turn.text }}</p>
          <v-alert
            v-if="turn.correction_brief"
            type="warning"
            variant="tonal"
            density="compact"
            class="mt-2 rounded-lg"
            role="status"
          >
            <strong>{{ t('student.languages.speakingJourney.discussion.correction') }}:</strong>
            <span dir="ltr"> {{ turn.correction_brief }}</span>
          </v-alert>
        </article>
      </section>

      <section v-if="!completed" class="spk-disc-mic mb-4">
        <p class="spk-disc-mic__hint">
          {{ t('student.languages.speakingJourney.discussion.voiceHint') }}
        </p>

        <div v-if="lastHeard" class="spk-disc-mic__heard" dir="ltr">
          {{ t('student.languages.speakingJourney.discussion.heard', { text: lastHeard }) }}
        </div>

        <v-btn
          v-if="voiceActive"
          color="primary"
          size="x-large"
          rounded="pill"
          class="spk-disc-mic__btn spk-pressable"
          :class="{ 'is-recording': voiceMode === 'recording' }"
          :loading="submitting || voiceMode === 'thinking'"
          :disabled="submitting || voiceMode === 'thinking' || voiceMode === 'partner_speaking'"
          @pointerdown.prevent="$emit('start-recording')"
          @pointerup.prevent="$emit('stop-recording')"
          @pointerleave.prevent="voiceMode === 'recording' && $emit('stop-recording')"
        >
          <v-icon start size="28">
            {{ voiceMode === 'recording' ? 'mdi-microphone' : 'mdi-microphone-outline' }}
          </v-icon>
          {{
            voiceMode === 'recording'
              ? t('student.languages.speakingJourney.discussion.releaseToSend')
              : t('student.languages.speakingJourney.discussion.holdToSpeak')
          }}
        </v-btn>

        <div v-else class="spk-disc-mic__typed">
          <v-alert type="info" variant="tonal" class="mb-3 rounded-lg" density="compact">
            {{ t('student.languages.speakingJourney.discussion.typedFallback') }}
          </v-alert>
          <v-textarea
            id="spk-discussion-input"
            :model-value="draft"
            rows="3"
            auto-grow
            maxlength="4000"
            dir="ltr"
            :placeholder="t('student.languages.speakingJourney.discussion.placeholder')"
            :disabled="submitting"
            class="mb-3"
            @update:model-value="$emit('update:draft', $event)"
          />
          <v-btn
            color="primary"
            class="spk-pressable"
            :loading="submitting"
            :disabled="!draft.trim()"
            @click="$emit('submit')"
          >
            {{ t('student.languages.speakingJourney.discussion.send') }}
          </v-btn>
        </div>
      </section>

      <section v-else class="spk-disc-closed text-center">
        <v-icon color="success" size="48" class="mb-2" aria-hidden="true">mdi-microphone-message</v-icon>
        <div class="text-overline text-medium-emphasis mb-1">
          {{ t('student.languages.speakingJourney.discussion.caseClosedTitle') }}
        </div>
        <h3 class="text-h6 font-weight-bold mb-2" dir="ltr">
          {{ caseTitle || packageTitle || t('student.languages.speakingJourney.discussion.completeTitle') }}
        </h3>
        <p class="text-body-2 text-medium-emphasis mb-3">
          {{ t('student.languages.speakingJourney.discussion.caseClosedLead') }}
        </p>

        <v-alert v-if="readyForAlex" type="success" variant="tonal" class="mb-4 rounded-lg text-start">
          {{ t('student.languages.speakingJourney.discussion.readyForAlex') }}
        </v-alert>

        <div class="d-flex flex-wrap gap-3 justify-center">
          <v-btn
            v-if="readyForAlex"
            color="primary"
            size="large"
            class="spk-pressable"
            @click="$emit('start-alex')"
          >
            {{ t('student.languages.speakingJourney.discussion.continueToAlex') }}
          </v-btn>
          <v-btn variant="tonal" class="spk-pressable" @click="$emit('restart')">
            {{ t('student.languages.speakingJourney.discussion.restart') }}
          </v-btn>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import LoadingState from '../common/LoadingState.vue'

const props = defineProps({
  loading: { type: Boolean, default: false },
  submitting: { type: Boolean, default: false },
  advancing: { type: Boolean, default: false },
  error: { type: String, default: '' },
  draft: { type: String, default: '' },
  state: { type: Object, default: null },
  packageTitle: { type: String, default: '' },
  currentStep: { type: Object, default: null },
  turns: { type: Array, default: () => [] },
  phase: { type: String, default: '' },
  completed: { type: Boolean, default: false },
  readyForAlex: { type: Boolean, default: false },
  canAdvance: { type: Boolean, default: false },
  stepsTotal: { type: Number, default: 0 },
  stepIndex: { type: Number, default: 0 },
  progressPercent: { type: Number, default: 0 },
  caseTitle: { type: String, default: '' },
  setting: { type: String, default: '' },
  characterHooks: { type: [Array, String], default: '' },
  voiceMode: { type: String, default: 'idle' },
  voiceActive: { type: Boolean, default: false },
  lastHeard: { type: String, default: '' },
  needsLesson: { type: Boolean, default: false },
  hasTutorAudio: { type: Boolean, default: false },
})

defineEmits([
  'open',
  'submit',
  'advance',
  'restart',
  'retry',
  'go-lesson',
  'update:draft',
  'start-alex',
  'start-recording',
  'stop-recording',
  'replay-audio',
])

const { t } = useI18n()

const displayTurns = computed(() =>
  (props.turns || []).filter((turn) => turn.role !== 'system' || Boolean(turn.text)),
)

const latestTutorText = computed(() => {
  const turns = props.turns || []
  for (let i = turns.length - 1; i >= 0; i -= 1) {
    if (turns[i]?.role === 'assistant' && turns[i]?.text) return turns[i].text
  }
  return props.currentStep?.prompt || ''
})

const statusLabel = computed(() => {
  const mode = props.voiceMode || 'idle'
  if (mode === 'partner_speaking') {
    return t('student.languages.speakingJourney.discussion.tutorSpeaking')
  }
  if (mode === 'recording') {
    return t('student.languages.speakingJourney.discussion.voiceMode.recording')
  }
  if (mode === 'thinking') {
    return t('student.languages.speakingJourney.discussion.voiceMode.thinking')
  }
  return t('student.languages.speakingJourney.discussion.yourTurn')
})
</script>

<style scoped>
.spk-disc-header {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  border-radius: 1rem;
  background: rgb(var(--v-theme-surface));
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}

.spk-disc-header__eyebrow {
  display: block;
  font-size: 0.75rem;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: rgba(var(--v-theme-on-surface), 0.6);
  margin-bottom: 0.25rem;
}

.spk-disc-header__title {
  margin: 0 0 0.35rem;
  font-size: 1.25rem;
  font-weight: 700;
  line-height: 1.3;
  unicode-bidi: isolate;
}

.spk-disc-header__progress {
  margin: 0;
  font-size: 0.875rem;
  color: rgba(var(--v-theme-on-surface), 0.65);
}

.spk-disc-header__status {
  flex-shrink: 0;
  padding: 0.4rem 0.85rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 600;
  background: rgba(var(--v-theme-primary), 0.12);
  color: rgb(var(--v-theme-primary));
}

.spk-disc-header__status.is-recording {
  background: rgba(var(--v-theme-error), 0.14);
  color: rgb(var(--v-theme-error));
}

.spk-disc-header__status.is-partner_speaking,
.spk-disc-header__status.is-thinking {
  background: rgba(var(--v-theme-secondary), 0.14);
  color: rgb(var(--v-theme-secondary));
}

.spk-disc-question {
  padding: 1.35rem 1.5rem;
  border-radius: 1.1rem;
  background: linear-gradient(
    160deg,
    rgba(var(--v-theme-primary), 0.1),
    rgba(var(--v-theme-surface), 1) 55%
  );
  border: 1px solid rgba(var(--v-theme-primary), 0.22);
}

.spk-disc-question__label {
  font-size: 0.8rem;
  font-weight: 700;
  color: rgb(var(--v-theme-primary));
  margin-bottom: 0.65rem;
}

.spk-disc-question__text {
  margin: 0 0 1.15rem;
  font-size: 1.1rem;
  line-height: 1.55;
  font-weight: 600;
  text-align: start;
  unicode-bidi: isolate;
  color: rgb(var(--v-theme-on-surface));
}

.spk-disc-question__actions {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.5rem;
}

.spk-disc-question__hint {
  font-size: 0.8rem;
  color: rgba(var(--v-theme-on-surface), 0.55);
}

.spk-disc-thread {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.spk-disc-turn {
  padding: 0.95rem 1.1rem;
  border-radius: 0.9rem;
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  background: rgb(var(--v-theme-surface));
}

.spk-disc-turn--assistant {
  background: rgba(var(--v-theme-primary), 0.06);
  border-color: rgba(var(--v-theme-primary), 0.16);
}

.spk-disc-turn--student {
  background: rgba(var(--v-theme-secondary), 0.06);
  border-color: rgba(var(--v-theme-secondary), 0.16);
}

.spk-disc-turn__role {
  font-size: 0.75rem;
  font-weight: 700;
  margin-bottom: 0.35rem;
  color: rgba(var(--v-theme-on-surface), 0.55);
}

.spk-disc-turn__text {
  margin: 0;
  font-size: 0.98rem;
  line-height: 1.55;
  text-align: start;
  unicode-bidi: isolate;
}

.spk-disc-mic {
  padding: 1.35rem 1.5rem;
  border-radius: 1.1rem;
  text-align: center;
  background: rgb(var(--v-theme-surface));
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}

.spk-disc-mic__hint {
  margin: 0 0 1rem;
  font-size: 0.92rem;
  color: rgba(var(--v-theme-on-surface), 0.65);
}

.spk-disc-mic__heard {
  margin: 0 0 1rem;
  font-size: 0.85rem;
  color: rgba(var(--v-theme-on-surface), 0.7);
  unicode-bidi: isolate;
}

.spk-disc-mic__btn {
  min-width: min(100%, 280px);
  min-height: 56px;
  font-weight: 700;
}

.spk-disc-mic__btn.is-recording {
  box-shadow: 0 0 0 4px rgba(var(--v-theme-error), 0.2);
}

.spk-disc-closed {
  padding: 1.75rem 1.5rem;
  border-radius: 1.1rem;
  background: rgb(var(--v-theme-surface));
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}

.spk-disc-mic__typed {
  text-align: start;
}
</style>
