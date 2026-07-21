<template>
  <div class="spk-live-bridge">
    <LoadingState v-if="loading" :label="t('student.languages.speakingJourney.liveBridge.settingSceneLoading')" />

    <v-alert v-else-if="error" type="error" variant="tonal" class="mb-4 rounded-lg" role="alert">
      {{ error }}
      <template #append>
        <v-btn variant="text" size="small" class="spk-pressable" @click="$emit('retry')">
          {{ t('common.retry', 'Retry') }}
        </v-btn>
      </template>
    </v-alert>

    <template v-else>
      <!-- Mission Brief (preparation) -->
      <section
        v-if="preparation && journeyPhase === 'preparation'"
        class="glass-card pa-5 pa-md-6 spk-mission-brief"
        aria-labelledby="spk-bridge-prep-title"
      >
        <SpeakingCaseContinuityStrip
          :story-title="preparation.story_title"
          :student-role="preparation.student_role"
          :characters="prepOtherCharacters"
          :decision="preparation.decision_point"
          :vocabulary="preparation.vocabulary_focus"
          :grammar="preparation.grammar_focus"
          mode="brief"
        />

        <div class="text-overline text-medium-emphasis mb-2">
          {{ t('student.languages.speakingJourney.liveBridge.prepEyebrow') }}
        </div>
        <h3 id="spk-bridge-prep-title" class="text-h6 font-weight-bold mb-2">
          {{ preparation.story_title || t('student.languages.speakingJourney.liveBridge.prepTitle') }}
        </h3>
        <p class="text-body-2 text-medium-emphasis mb-4">
          {{ t('student.languages.speakingJourney.liveBridge.prepLead') }}
        </p>

        <dl class="spk-brief-grid mb-4">
          <div v-if="preparation.student_role" class="spk-brief-item">
            <dt>{{ t('student.languages.speakingJourney.liveBridge.roleLabel') }}</dt>
            <dd>{{ preparation.student_role }}</dd>
          </div>
          <div v-if="prepOtherCharacters.length" class="spk-brief-item">
            <dt>{{ t('student.languages.speakingJourney.liveBridge.charactersLabel') }}</dt>
            <dd>{{ prepOtherCharacters.join(' · ') }}</dd>
          </div>
          <div v-if="preparation.setting" class="spk-brief-item">
            <dt>{{ t('student.languages.speakingJourney.liveBridge.settingLabel') }}</dt>
            <dd>{{ preparation.setting }}</dd>
          </div>
          <div v-if="preparation.decision_point" class="spk-brief-item">
            <dt>{{ t('student.languages.speakingJourney.liveBridge.decisionLabel') }}</dt>
            <dd>{{ preparation.decision_point }}</dd>
          </div>
          <div v-if="prepSpeakingGoal" class="spk-brief-item spk-brief-item--full">
            <dt>{{ t('student.languages.speakingJourney.liveBridge.speakingGoalLabel') }}</dt>
            <dd>{{ prepSpeakingGoal }}</dd>
          </div>
        </dl>

        <div v-if="preparation.vocabulary_focus?.length" class="spk-chip-row mb-2">
          <span class="spk-chip-row__label">{{ t('student.languages.speakingJourney.liveBridge.vocabFocus') }}</span>
          <v-chip
            v-for="(word, idx) in preparation.vocabulary_focus.slice(0, 5)"
            :key="`prep-vocab-${idx}`"
            size="small"
            variant="tonal"
            class="mr-1 mb-1"
          >
            {{ word }}
          </v-chip>
        </div>
        <div v-if="preparation.grammar_focus?.[0]" class="spk-chip-row mb-4">
          <span class="spk-chip-row__label">{{ t('student.languages.speakingJourney.liveBridge.grammarFocus') }}</span>
          <v-chip size="small" variant="tonal" color="info">{{ preparation.grammar_focus[0] }}</v-chip>
        </div>

        <v-alert
          v-if="!micGateDismissed"
          type="info"
          variant="tonal"
          density="compact"
          closable
          class="mb-4 rounded-lg text-start"
          @click:close="micGateDismissed = true"
        >
          <strong>{{ t('student.languages.speakingJourney.liveBridge.micGateTitle') }}:</strong>
          {{ t('student.languages.speakingJourney.liveBridge.micGateBody') }}
        </v-alert>

        <v-expand-transition>
          <div v-if="showFullBrief" class="spk-brief-full mb-4">
            <pre class="spk-scenario__brief text-body-2">{{ preparation.student_brief }}</pre>
            <div v-if="preparation.must_do?.length" class="mt-3">
              <div class="text-caption text-medium-emphasis mb-1">
                {{ t('student.languages.speakingJourney.liveBridge.mustDoTitle') }}
              </div>
              <ul class="mb-0 pl-4">
                <li v-for="(item, idx) in preparation.must_do" :key="idx" class="text-body-2 mb-1">
                  {{ item }}
                </li>
              </ul>
            </div>
            <div v-if="preparation.stakes" class="mt-3">
              <div class="text-caption text-medium-emphasis mb-1">
                {{ t('student.languages.speakingJourney.liveBridge.stakesLabel') }}
              </div>
              <p class="text-body-2 mb-0">{{ preparation.stakes }}</p>
            </div>
          </div>
        </v-expand-transition>

        <v-btn
          variant="text"
          size="small"
          class="spk-pressable mb-4"
          :append-icon="showFullBrief ? 'mdi-chevron-up' : 'mdi-chevron-down'"
          @click="showFullBrief = !showFullBrief"
        >
          {{
            showFullBrief
              ? t('student.languages.speakingJourney.liveBridge.hideDetails')
              : t('student.languages.speakingJourney.liveBridge.viewDetails')
          }}
        </v-btn>

        <div class="d-flex flex-wrap gap-3">
          <v-btn
            color="primary"
            size="large"
            class="spk-pressable"
            :loading="busy"
            @click="$emit('start-practice')"
          >
            {{ t('student.languages.speakingJourney.liveBridge.startPractice') }}
          </v-btn>
          <v-btn variant="text" class="spk-pressable" :disabled="busy" @click="$emit('skip-scene-practice')">
            {{ t('student.languages.speakingJourney.liveBridge.skipScenePractice') }}
          </v-btn>
        </div>
      </section>

      <!-- Scene Practice Room (GPT rehearsal) -->
      <section
        v-else-if="journeyPhase === 'gpt_rehearsal'"
        class="glass-card pa-5 pa-md-6 spk-rehearsal-room"
        aria-labelledby="spk-bridge-reh-title"
      >
        <SpeakingCaseContinuityStrip
          :story-title="sceneCase.storyTitle"
          :student-role="sceneCase.studentRole"
          :characters="sceneCase.characters"
          :decision="sceneCase.decision"
          :vocabulary="sceneCase.vocabulary"
          :grammar="sceneCase.grammar"
          mode="scene_practice"
        />

        <div class="text-overline text-medium-emphasis mb-2">
          {{ t('student.languages.speakingJourney.liveBridge.rehearsalEyebrow') }}
        </div>
        <h3 id="spk-bridge-reh-title" class="text-h6 font-weight-bold mb-2">
          {{ t('student.languages.speakingJourney.liveBridge.rehearsalTitle') }}
        </h3>
        <p class="text-body-2 text-medium-emphasis mb-3">
          {{ t('student.languages.speakingJourney.liveBridge.rehearsalLead') }}
        </p>

        <v-alert type="info" variant="tonal" class="mb-4 rounded-lg" density="compact">
          {{ t('student.languages.speakingJourney.liveBridge.notHume') }}
          <span v-if="rehearsal?.gpt_role"> · {{ rehearsal.gpt_role }}</span>
        </v-alert>

        <div class="spk-rehearsal-stage text-center mb-4">
          <div
            class="spk-orb"
            :class="{
              'spk-orb--listening': sceneOrbListening,
              'spk-orb--turn': sceneOrbYourTurn,
              'spk-orb--handoff': sceneVoiceMode === 'partner_speaking' || sceneVoiceMode === 'thinking',
            }"
            aria-hidden="true"
          />
          <div class="spk-rehearsal-state text-caption font-weight-bold text-uppercase mt-2">
            {{ sceneStateLabel }}
          </div>
          <p v-if="displayPartnerLine" class="spk-rehearsal-line text-body-1 font-weight-medium mt-3 mb-0">
            {{ displayPartnerLine }}
          </p>
        </div>

        <v-alert
          v-if="latestCoachTip"
          type="success"
          variant="tonal"
          density="compact"
          closable
          class="mb-3 rounded-lg text-start"
          @click:close="dismissCoachTip"
        >
          <strong>{{ t('student.languages.speakingJourney.liveBridge.coachWhisper') }}:</strong>
          {{ latestCoachTip }}
        </v-alert>

        <v-alert
          v-if="sceneVoiceActive && !useTypedFallback"
          type="success"
          variant="tonal"
          density="compact"
          class="mb-3 rounded-lg"
        >
          {{ t('student.languages.speakingJourney.liveBridge.sceneVoiceActive') }}
        </v-alert>

        <v-alert type="info" variant="tonal" density="compact" class="mb-4 rounded-lg" v-if="useTypedFallback">
          {{ t('student.languages.speakingJourney.liveBridge.typedFallbackHint') }}
        </v-alert>

        <div v-if="sceneVoiceActive && !useTypedFallback" class="d-flex justify-center mb-4">
          <v-btn
            :color="sceneVoiceMode === 'recording' ? 'error' : 'primary'"
            size="large"
            class="spk-pressable"
            :prepend-icon="sceneVoiceMode === 'recording' ? 'mdi-microphone' : 'mdi-microphone-outline'"
            :loading="sceneVoiceMode === 'thinking'"
            :disabled="sceneVoiceMode === 'thinking' || sceneVoiceMode === 'partner_speaking' || sceneVoiceMode === 'priming'"
            @pointerdown.prevent="onRecordPointerDown"
            @pointerup.prevent="onRecordPointerUp"
            @pointerleave="onRecordPointerUp"
            @pointercancel="onRecordPointerUp"
          >
            {{
              sceneVoiceMode === 'recording'
                ? t('student.languages.speakingJourney.liveBridge.releaseToSend')
                : t('student.languages.speakingJourney.liveBridge.holdToSpeak')
            }}
          </v-btn>
        </div>

        <v-btn
          v-if="turns.length > 1"
          variant="text"
          size="small"
          class="spk-pressable mb-2"
          :append-icon="showTranscript ? 'mdi-chevron-up' : 'mdi-chevron-down'"
          @click="showTranscript = !showTranscript"
        >
          {{
            showTranscript
              ? t('student.languages.speakingJourney.liveBridge.hideDetails')
              : t('student.languages.speakingJourney.liveBridge.viewDetails')
          }}
        </v-btn>
        <v-expand-transition>
          <div v-if="showTranscript" class="spk-reh-turns mb-4 spk-reh-turns--dim" role="log" aria-live="polite">
            <div
              v-for="(turn, idx) in turns"
              :key="idx"
              class="mb-3"
              :class="turn.role === 'student' ? 'text-end' : 'text-start'"
            >
              <div
                class="d-inline-block pa-3 rounded-lg text-body-2"
                :class="turn.role === 'student' ? 'bg-primary-lighten-5' : 'bg-grey-lighten-4'"
              >
                {{ turn.text }}
              </div>
            </div>
          </div>
        </v-expand-transition>

        <v-textarea
          v-if="useTypedFallback"
          :model-value="draft"
          rows="3"
          auto-grow
          hide-details
          class="mb-3"
          :label="t('student.languages.speakingJourney.liveBridge.yourLine')"
          :disabled="busy"
          @update:model-value="$emit('update:draft', $event)"
        />
        <div v-if="useTypedFallback" class="d-flex flex-wrap gap-3">
          <v-btn
            color="primary"
            class="spk-pressable"
            :loading="busy"
            :disabled="!(draft || '').trim()"
            @click="$emit('submit-turn')"
          >
            {{ t('student.languages.speakingJourney.liveBridge.sendLine') }}
          </v-btn>
          <v-btn
            variant="tonal"
            class="spk-pressable"
            :loading="busy"
            @click="$emit('finish-rehearsal')"
          >
            {{ t('student.languages.speakingJourney.liveBridge.finishRehearsal') }}
          </v-btn>
        </div>
        <div v-else class="d-flex flex-wrap gap-3 justify-center">
          <v-btn
            variant="tonal"
            class="spk-pressable"
            :loading="busy"
            @click="$emit('finish-rehearsal')"
          >
            {{ t('student.languages.speakingJourney.liveBridge.finishRehearsal') }}
          </v-btn>
        </div>
      </section>

      <!-- Mission Complete + Handoff Corridor (ready for live) -->
      <section
        v-else-if="readyForLive && liveContext"
        class="glass-card pa-5 pa-md-6 text-center spk-handoff"
        aria-labelledby="spk-bridge-live-title"
      >
        <template v-if="handoffStage === 'mission_complete'">
          <v-icon color="success" size="48" class="mb-2 spk-pop-active" aria-hidden="true">
            mdi-trophy-outline
          </v-icon>
          <div class="text-overline text-medium-emphasis mb-1">
            {{ t('student.languages.speakingJourney.liveBridge.missionCompleteTitle') }}
          </div>
          <h3 id="spk-bridge-live-title" class="text-h6 font-weight-bold mb-2">
            {{ t('student.languages.speakingJourney.liveBridge.missionCompleteBody') }}
          </h3>
          <p class="text-body-2 spk-handoff__insight mb-2">“{{ missionCompleteInsight }}”</p>
          <p class="text-caption text-medium-emphasis mb-0">
            {{ t('student.languages.speakingJourney.liveBridge.missionCompleteConfidence') }}
          </p>
        </template>
        <template v-else>
          <div class="spk-orb spk-orb--handoff mb-3" aria-hidden="true" />
          <div class="text-overline text-medium-emphasis mb-1">
            {{ t('student.languages.speakingJourney.liveBridge.alexJoining') }}
          </div>
          <h3 id="spk-bridge-live-title" class="text-h6 font-weight-bold mb-2">
            {{
              handoffStage === 'retry'
                ? t('student.languages.speakingJourney.liveBridge.liveTitle')
                : t('student.languages.speakingJourney.liveBridge.handoffAlexEntering')
            }}
          </h3>
          <p class="text-body-2 text-medium-emphasis mb-4">
            {{ t('student.languages.speakingJourney.liveBridge.handoffEnding') }}
          </p>
          <v-progress-linear
            v-if="handoffStage === 'corridor' || handoffStage === 'connecting'"
            indeterminate
            color="success"
            rounded
            height="6"
            class="mb-4 spk-handoff__bar"
          />
          <v-btn
            v-if="handoffStage === 'retry'"
            color="primary"
            size="large"
            class="spk-pressable"
            :loading="preparingLive"
            @click="retryGoLive"
          >
            {{ t('student.languages.speakingJourney.liveBridge.retryLiveScene') }}
          </v-btn>
        </template>
      </section>

      <section v-else class="glass-card pa-5 text-center">
        <p class="text-body-2 text-medium-emphasis mb-3">
          {{ t('student.languages.speakingJourney.liveBridge.empty') }}
        </p>
        <v-btn color="primary" class="spk-pressable" :loading="busy" @click="$emit('prepare')">
          {{ t('student.languages.speakingJourney.liveBridge.buildScenario') }}
        </v-btn>
      </section>
    </template>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import LoadingState from '../common/LoadingState.vue'
import SpeakingCaseContinuityStrip from './SpeakingCaseContinuityStrip.vue'

const props = defineProps({
  loading: { type: Boolean, default: false },
  busy: { type: Boolean, default: false },
  preparingLive: { type: Boolean, default: false },
  error: { type: String, default: '' },
  journeyPhase: { type: String, default: 'idle' },
  preparation: { type: Object, default: null },
  rehearsal: { type: Object, default: null },
  liveContext: { type: Object, default: null },
  readyForLive: { type: Boolean, default: false },
  turns: { type: Array, default: () => [] },
  draft: { type: String, default: '' },
  sceneVoiceMode: { type: String, default: 'idle' },
  sceneVoiceActive: { type: Boolean, default: false },
})

const emit = defineEmits([
  'prepare',
  'start-practice',
  'skip-scene-practice',
  'submit-turn',
  'finish-rehearsal',
  'start-recording',
  'stop-recording',
  'go-live',
  'retry',
  'update:draft',
])

const { t } = useI18n()

const showFullBrief = ref(false)
const showTranscript = ref(false)
const micGateDismissed = ref(false)
const dismissedCoachTip = ref('')

function otherCharacters(characters, role) {
  const list = Array.isArray(characters) ? characters.filter(Boolean) : []
  const roleLower = String(role || '').toLowerCase()
  return list.filter((name) => String(name || '').toLowerCase() !== roleLower)
}

const prepOtherCharacters = computed(() =>
  otherCharacters(props.preparation?.characters, props.preparation?.student_role),
)

const prepSpeakingGoal = computed(() => {
  const prep = props.preparation
  if (!prep) return ''
  return prep.objectives?.[0] || prep.continuation_hook || ''
})

/** Prefer rehearsal.scenario, fall back to preparation so the Continuity Strip never blanks. */
const sceneCase = computed(() => {
  const scen = props.rehearsal?.scenario || {}
  const prep = props.preparation || {}
  const role = scen.student_role || prep.student_role || ''
  const characters = scen.characters || prep.characters || []
  return {
    storyTitle: scen.story_title || prep.story_title || '',
    studentRole: role,
    characters: otherCharacters(characters, role),
    decision: scen.decision_point || prep.decision_point || '',
    vocabulary: scen.vocabulary_focus || prep.vocabulary_focus || [],
    grammar: scen.grammar_focus || prep.grammar_focus || [],
  }
})

const lastPartnerLine = computed(() => {
  const list = props.turns || []
  for (let i = list.length - 1; i >= 0; i -= 1) {
    if (list[i]?.role === 'assistant') return list[i].text
  }
  return ''
})

const useTypedFallback = computed(
  () => !props.sceneVoiceActive || props.sceneVoiceMode === 'fallback',
)

const sceneOrbListening = computed(
  () =>
    props.sceneVoiceActive &&
    (props.sceneVoiceMode === 'listening' ||
      props.sceneVoiceMode === 'priming' ||
      props.sceneVoiceMode === 'recording'),
)

const sceneOrbYourTurn = computed(
  () =>
    useTypedFallback.value ||
    props.sceneVoiceMode === 'listening' ||
    props.sceneVoiceMode === 'idle',
)

const sceneStateLabel = computed(() => {
  if (props.sceneVoiceMode === 'priming') {
    return t('student.languages.speakingJourney.liveBridge.connectingScene')
  }
  if (props.sceneVoiceMode === 'recording') {
    return t('student.languages.speakingJourney.liveBridge.recordingLabel')
  }
  if (props.sceneVoiceMode === 'thinking') {
    return t('student.languages.speakingJourney.liveBridge.thinkingLabel')
  }
  if (props.sceneVoiceMode === 'partner_speaking') {
    return t('student.languages.speakingJourney.liveBridge.partnerSpeaking')
  }
  if (props.sceneVoiceActive) {
    return t('student.languages.speakingJourney.liveBridge.yourTurnLabel')
  }
  if (props.busy) {
    return t('student.languages.speakingJourney.liveBridge.listeningLabel')
  }
  return t('student.languages.speakingJourney.liveBridge.yourTurnLabel')
})

let recordArmed = false

function onRecordPointerDown() {
  if (
    props.sceneVoiceMode === 'thinking' ||
    props.sceneVoiceMode === 'partner_speaking' ||
    props.sceneVoiceMode === 'priming'
  ) {
    return
  }
  recordArmed = true
  emit('start-recording')
}

function onRecordPointerUp() {
  if (!recordArmed) return
  recordArmed = false
  if (props.sceneVoiceMode === 'recording') {
    emit('stop-recording')
  }
}

const displayPartnerLine = computed(() => lastPartnerLine.value)

const latestCoachTipRaw = computed(() => {
  const notes = props.rehearsal?.coaching_notes || []
  const corrections = props.rehearsal?.corrections || []
  return notes[notes.length - 1] || corrections[corrections.length - 1] || ''
})

const latestCoachTip = computed(() =>
  latestCoachTipRaw.value && latestCoachTipRaw.value !== dismissedCoachTip.value
    ? latestCoachTipRaw.value
    : '',
)

function dismissCoachTip() {
  dismissedCoachTip.value = latestCoachTipRaw.value
}

const missionCompleteInsight = computed(() => {
  const notes = props.rehearsal?.coaching_notes || []
  return notes[notes.length - 1] || t('student.languages.speakingJourney.liveBridge.missionCompleteInsightFallback')
})

/** Mission Complete → Handoff Corridor beat sequence (local UI only, no API change). */
const MISSION_COMPLETE_MS = 2400
const CORRIDOR_MS = 3000
const CONNECT_GRACE_MS = 1200

const handoffStage = ref('idle') // idle | mission_complete | corridor | connecting | retry
let missionCompleteTimer = null
let corridorTimer = null
let connectGraceTimer = null

function clearHandoffTimers() {
  if (missionCompleteTimer) clearTimeout(missionCompleteTimer)
  if (corridorTimer) clearTimeout(corridorTimer)
  if (connectGraceTimer) clearTimeout(connectGraceTimer)
  missionCompleteTimer = null
  corridorTimer = null
  connectGraceTimer = null
}

function startHandoff() {
  if (handoffStage.value !== 'idle') return
  handoffStage.value = 'mission_complete'
  clearHandoffTimers()
  missionCompleteTimer = setTimeout(() => {
    handoffStage.value = 'corridor'
    corridorTimer = setTimeout(() => {
      if (handoffStage.value !== 'corridor') return
      handoffStage.value = 'connecting'
      emit('go-live')
    }, CORRIDOR_MS)
  }, MISSION_COMPLETE_MS)
}

function resetHandoff() {
  clearHandoffTimers()
  handoffStage.value = 'idle'
}

watch(
  () => props.readyForLive && Boolean(props.liveContext),
  (isReady) => {
    if (isReady) startHandoff()
    else resetHandoff()
  },
  { immediate: true },
)

watch(
  () => props.preparingLive,
  (isPreparing, wasPreparing) => {
    // Only treat a finished prepare-live as failure while still on this corridor beat.
    // Success navigates to Alex; do not briefly flash Retry on the still-mounted bridge tab.
    if (!(wasPreparing && !isPreparing)) return
    if (handoffStage.value !== 'connecting' && handoffStage.value !== 'corridor') return
    if (props.error) {
      handoffStage.value = 'retry'
      return
    }
    clearTimeout(connectGraceTimer)
    connectGraceTimer = setTimeout(() => {
      if (
        (handoffStage.value === 'connecting' || handoffStage.value === 'corridor') &&
        props.readyForLive &&
        !props.preparingLive
      ) {
        handoffStage.value = 'retry'
      }
    }, CONNECT_GRACE_MS)
  },
)

function retryGoLive() {
  handoffStage.value = 'connecting'
  emit('go-live')
}

onBeforeUnmount(clearHandoffTimers)
</script>

<style scoped>
.spk-scenario__brief {
  white-space: pre-wrap;
  font-family: inherit;
  margin: 0;
  line-height: 1.55;
}

.spk-brief-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 0.9rem 1.25rem;
  margin: 0;
}

.spk-brief-item dt {
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  opacity: 0.6;
  margin-bottom: 0.2rem;
}

.spk-brief-item dd {
  margin: 0;
  font-size: 0.92rem;
  font-weight: 600;
  line-height: 1.4;
}

.spk-brief-item--full {
  grid-column: 1 / -1;
}

.spk-chip-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.25rem;
}

.spk-chip-row__label {
  font-size: 0.72rem;
  font-weight: 700;
  opacity: 0.6;
  margin-right: 0.4rem;
}

.spk-rehearsal-stage {
  padding: 1.5rem 1rem;
  border-radius: 18px;
  background: radial-gradient(circle at center, rgba(var(--v-theme-primary), 0.06), transparent 70%);
}

.spk-rehearsal-state {
  letter-spacing: 0.06em;
  opacity: 0.7;
}

.spk-rehearsal-line {
  max-width: 46ch;
  margin-inline: auto;
}

.spk-reh-turns--dim {
  opacity: 0.75;
}

.spk-handoff__insight {
  max-width: 46ch;
  margin-inline: auto;
  font-style: italic;
}

.spk-handoff__bar {
  max-width: 220px;
  margin-inline: auto;
}

/* Decorative scene-partner orb — CSS-only, no real voice yet */
.spk-orb {
  width: 72px;
  height: 72px;
  margin-inline: auto;
  border-radius: 50%;
  background: radial-gradient(circle at 35% 30%, rgba(var(--v-theme-primary), 0.85), rgba(var(--v-theme-primary), 0.35));
  box-shadow: 0 0 0 0 rgba(var(--v-theme-primary), 0.35);
  animation: spk-orb-pulse 2.4s ease-in-out infinite;
}

.spk-orb--listening {
  animation-duration: 1.1s;
  background: radial-gradient(circle at 35% 30%, rgba(var(--v-theme-secondary), 0.85), rgba(var(--v-theme-secondary), 0.35));
}

.spk-orb--turn {
  animation-duration: 2.6s;
}

.spk-orb--handoff {
  background: radial-gradient(circle at 35% 30%, rgba(var(--v-theme-success), 0.85), rgba(var(--v-theme-success), 0.35));
}

@keyframes spk-orb-pulse {
  0%,
  100% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(var(--v-theme-primary), 0.35);
  }
  50% {
    transform: scale(1.08);
    box-shadow: 0 0 0 14px rgba(var(--v-theme-primary), 0);
  }
}

@media (prefers-reduced-motion: reduce) {
  .spk-orb {
    animation: none;
  }
}
</style>
