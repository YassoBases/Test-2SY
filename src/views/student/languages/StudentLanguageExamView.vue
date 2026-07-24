<template>
  <div class="page-container slide-up-enter-active">
    <PageHeader
      eyebrow="Learn languages"
      eyebrow-icon="mdi-clipboard-text-clock"
      title="AI Placement Exam"
      subtitle="Speaking, listening, reading and writing — then a full level report"
    />
    <LanguageModuleTabs />

    <v-alert v-if="loadError" type="error" variant="tonal" class="mb-4 rounded-lg">{{ loadError }}</v-alert>

    <!-- INTRO -->
    <template v-if="view === 'intro'">
    <v-card class="glass-card pa-6 exam-intro text-center" variant="flat">
      <v-icon size="52" color="secondary" class="mb-2">mdi-medal-outline</v-icon>
      <h3 class="text-h6 font-weight-bold mb-1">Full level test — every core skill</h3>
      <p class="intro-time-copy mb-4" dir="ltr">
        You have 60 minutes. You'll speak, listen, read and write. Each skill is graded separately, then
        we map you to a CEFR level and unlock your learning path.
      </p>
      <v-alert color="warning" variant="tonal" density="compact" icon="mdi-timer-alert-outline" class="mb-4 text-start" dir="ltr">
        The timer starts only after you confirm the instructions and begin the exam.
      </v-alert>
      <v-row dense class="mb-2 text-start">
        <v-col v-for="k in INTRO_SKILLS" :key="k" cols="6" sm="4">
          <div class="skill-pill glass-card pa-3 h-100">
            <v-icon :icon="SECTION_META[k].icon" color="secondary" class="mb-1" />
            <div class="font-weight-bold text-body-2">{{ SECTION_META[k].label }}</div>
            <div class="text-caption text-medium-emphasis">{{ SECTION_META[k].hint }}</div>
          </div>
        </v-col>
      </v-row>
      <p class="text-caption text-medium-emphasis mb-0">
        Includes a short speaking task, then a full CEFR level report.
      </p>
      <v-btn color="secondary" variant="flat" size="large" :loading="busy" :disabled="rateLimitBlocked" prepend-icon="mdi-play" class="mt-3" @click="openInstructions">
        Start the exam
      </v-btn>
      <div class="skip-placement-box mt-4" dir="rtl">
        <div class="text-body-2 font-weight-bold mb-1">بدك تتخطى اختبار تحديد المستوى؟</div>
        <p class="text-caption text-medium-emphasis mb-3">اختر المستوى الذي تريد البدء منه، ثم افتح المنصة مباشرة.</p>
        <div class="skip-level-grid mb-3">
          <button
            v-for="level in SKIP_LEVEL_OPTIONS"
            :key="level"
            type="button"
            class="skip-level-chip"
            :class="{ 'skip-level-chip--selected': skipBaselineLevel === level }"
            :aria-pressed="skipBaselineLevel === level"
            :disabled="busy || rateLimitBlocked"
            @click="skipBaselineLevel = level"
          >
            {{ level }}
          </button>
        </div>
        <v-btn
          color="secondary"
          variant="tonal"
          size="small"
          :loading="busy"
          :disabled="rateLimitBlocked"
          prepend-icon="mdi-fast-forward"
          @click="skipPlacement"
        >
          تخطي الاختبار والبدء من {{ skipBaselineLevel }}
        </v-btn>
      </div>
      <v-btn
        v-if="evaluationFailed && sessionId"
        color="warning"
        variant="tonal"
        size="large"
        :loading="busy"
        :disabled="rateLimitBlocked"
        prepend-icon="mdi-refresh"
        class="mt-3 ml-2"
        @click="retryEvaluation"
      >
        Retry report evaluation
      </v-btn>
    </v-card>

    <v-dialog v-model="instructionsDialog" max-width="620">
      <v-card class="exam-instructions-dialog" rounded="lg">
        <v-card-title class="d-flex align-center gap-2">
          <v-icon icon="mdi-clipboard-text-clock-outline" color="secondary" />
          Before You Begin
        </v-card-title>
        <v-card-text>
          <v-alert color="warning" variant="tonal" density="compact" icon="mdi-timer-outline" class="mb-4" dir="ltr">
            You will have 60 minutes. The timer starts when you press Begin exam.
          </v-alert>
          <div class="instruction-list" dir="ltr">
            <div class="instruction-row">
              <v-icon icon="mdi-school-outline" color="secondary" size="20" />
              <span>The exam includes speaking, listening, reading, and writing.</span>
            </div>
            <div class="instruction-row">
              <v-icon icon="mdi-arrow-decision-outline" color="secondary" size="20" />
              <span>Questions adapt to your answers, so later tasks may become easier or harder.</span>
            </div>
            <div class="instruction-row">
              <v-icon icon="mdi-microphone-outline" color="secondary" size="20" />
              <span>For speaking, record or upload your audio, then submit it manually.</span>
            </div>
            <div class="instruction-row">
              <v-icon icon="mdi-shield-check-outline" color="secondary" size="20" />
              <span>Do not use grammar tools, translation, or outside help during the exam.</span>
            </div>
          </div>
        </v-card-text>
        <v-card-actions class="justify-end">
          <v-btn variant="text" :disabled="busy" @click="instructionsDialog = false">Cancel</v-btn>
          <v-btn color="secondary" variant="flat" prepend-icon="mdi-play" :loading="busy" :disabled="rateLimitBlocked" @click="start">
            Begin exam
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    </template>

    <!-- EXAM -->
    <template v-else-if="view === 'exam' && state">
      <!-- section stepper -->
      <v-card class="glass-card pa-3 mb-3" variant="flat">
        <div class="d-flex align-center justify-space-between flex-wrap gap-2">
          <div class="d-flex align-center gap-2 flex-wrap">
            <v-chip
              v-for="(sec, i) in state.sections"
              :key="sec"
              size="small"
              :color="i === state.section_index ? 'secondary' : undefined"
              :variant="isSectionDone(sec) ? 'flat' : i === state.section_index ? 'flat' : 'tonal'"
              :prepend-icon="isSectionDone(sec) ? 'mdi-check' : skillIcon(sec)"
              :disabled="busy || timeExpired"
              class="section-tab-chip"
              @click="jumpToSection(sec)"
            >
              {{ skillLabel(sec) }}
            </v-chip>
          </div>
          <div class="exam-toolbar-actions">
            <v-chip
              size="small"
              :color="timerColor"
              variant="tonal"
              prepend-icon="mdi-timer-outline"
              class="exam-timer-chip"
            >
              {{ timeRemainingText }}
            </v-chip>
            <v-btn
              size="small"
              color="warning"
              variant="tonal"
              prepend-icon="mdi-restart"
              :loading="busy"
              :disabled="rateLimitBlocked"
              @click="startFresh"
            >
              Start fresh
            </v-btn>
          </div>
        </div>
        <v-progress-linear
          :model-value="(100 * (state.completed_sections || []).length) / state.section_total"
          color="secondary" height="6" rounded class="mt-2"
        />
        <v-alert v-if="!timeExpired" :color="timerColor" variant="tonal" density="compact" icon="mdi-timer-outline" class="mt-3 mb-0" dir="ltr">
          Time remaining: {{ timeRemainingText }}. The exam closes automatically when the timer reaches 00:00.
        </v-alert>
        <v-alert v-if="timeExpired" type="error" variant="tonal" density="compact" class="mt-3 mb-0">
          Time is up. Start a fresh attempt to take the placement exam again.
        </v-alert>
      </v-card>

      <v-card
        v-if="state.phase === 'failed' && state.error_code === 'time_expired'"
        class="glass-card pa-8 text-center"
        variant="flat"
      >
        <v-icon icon="mdi-timer-alert-outline" color="error" size="44" class="mb-3" />
        <h3 class="text-subtitle-1 font-weight-bold mb-1">The exam time is up</h3>
        <p class="text-caption text-medium-emphasis mb-3">
          The placement exam is limited to 60 minutes. Start a fresh attempt when you are ready.
        </p>
        <v-btn color="warning" variant="tonal" prepend-icon="mdi-restart" :loading="busy" :disabled="rateLimitBlocked" @click="startFresh">
          Start fresh
        </v-btn>
      </v-card>

      <!-- preparing next section (content generated in the background) -->
      <v-card v-else-if="state.phase === 'preparing'" class="glass-card pa-8 text-center" variant="flat">
        <v-progress-circular indeterminate color="secondary" size="40" class="mb-3" />
        <h3 class="text-subtitle-1 font-weight-bold mb-1">Preparing your next section…</h3>
        <p class="text-caption text-medium-emphasis mb-0">Generating fresh questions just for you.</p>
      </v-card>

      <!-- SPEAKING / INTERVIEW (chat — scoring is shown only at the end, in the report) -->
      <v-card v-if="isSpeakingPhase" class="glass-card pa-4 mb-3 speaking-exam-card" variant="flat">
        <div class="speaking-header mb-3">
          <div>
            <v-chip v-if="state.speaking?.scenario_title" size="small" color="secondary" variant="tonal" :prepend-icon="state.phase === 'interview' ? 'mdi-account-voice' : 'mdi-drama-masks'" class="mb-2">
              {{ state.speaking.scenario_title }}
            </v-chip>
            <div class="text-caption text-medium-emphasis">{{ speakingTurnText }}</div>
          </div>
          <v-chip size="small" :color="speakingStatusColor" variant="tonal" :prepend-icon="speakingStatusIcon">
            {{ speakingStatusLabel }}
          </v-chip>
        </div>
        <v-alert v-if="state.phase === 'interview'" type="info" variant="tonal" density="compact" class="mb-2">
          Phase 2 — a quick spoken interview to pinpoint your exact level.
        </v-alert>

        <section v-if="currentSpeakingPrompt" class="speaking-question-card mb-3" dir="ltr">
          <div class="text-caption text-medium-emphasis mb-1">Examiner prompt</div>
          <p class="text-body-1 font-weight-medium mb-0">{{ currentSpeakingPrompt }}</p>
        </section>

        <div v-if="answeredSpeakingTurnCount || busy" class="speaking-progress-note mb-3">
          <div v-if="answeredSpeakingTurnCount" class="d-flex align-center gap-2 text-caption text-medium-emphasis">
            <v-icon icon="mdi-check-circle-outline" color="success" size="16" />
            <span>{{ answeredSpeakingTurnCount }} previous answer{{ answeredSpeakingTurnCount === 1 ? '' : 's' }} saved. Continue with the current prompt.</span>
          </div>
          <div v-if="busy" class="d-flex align-center gap-2 text-medium-emphasis py-1">
            <v-progress-circular indeterminate size="16" width="2" color="secondary" />
            <span class="text-caption">Listening to your answer…</span>
          </div>
        </div>

        <div class="recorder-box pa-3 text-center">
          <v-btn
            :color="recorder.recording.value ? 'error' : 'secondary'"
            :variant="recorder.recording.value ? 'flat' : 'tonal'"
            :loading="preparingSpeech"
            size="large" :icon="recorder.recording.value ? 'mdi-stop' : 'mdi-microphone'"
            :disabled="busy || preparingSpeech || (timeExpired && !recorder.recording.value)" @click="handleSpeakingRecordToggle"
          />
          <div class="text-caption text-medium-emphasis mt-1">
            <span v-if="preparingSpeech">Preparing live transcript…</span>
            <span v-else-if="recorder.recording.value">Recording… {{ recorder.formattedTime.value }} — tap to stop</span>
            <span v-else-if="recorder.audioBlob.value">Audio ready — submit once for secure transcription</span>
            <span v-else>Tap to record your spoken answer</span>
          </div>
          <div v-if="recorder.recording.value" class="recorder-waveform mt-3" aria-hidden="true">
            <span v-for="(height, i) in recorder.barHeights.value" :key="i" :style="{ height: `${height}px` }" />
          </div>
          <v-btn
            v-if="recorder.audioBlob.value && !recorder.recording.value"
            size="small"
            variant="text"
            color="secondary"
            prepend-icon="mdi-refresh"
            class="mt-2"
            :disabled="busy || preparingSpeech || timeExpired"
            @click="discardSpeakingTake"
          >
            Record again
          </v-btn>
          <div class="text-caption text-medium-emphasis mt-2">— or —</div>
          <v-file-input
            v-model="uploadFile"
            accept="audio/*"
            density="compact"
            variant="outlined"
            hide-details
            prepend-icon="mdi-upload"
            label="Upload an audio file"
            class="mt-2 upload-input"
            :disabled="busy || preparingSpeech || recorder.recording.value || timeExpired"
            @update:model-value="onUpload"
          />
        </div>

        <!-- Transcript preview: display-only, English-hinted, LTR-forced (this exam is
             English-only even though the app defaults to an Arabic/RTL UI). Always visible in
             a stable location below the recorder box (never nested inside it, never appearing
             suddenly) for the current speaking question -- shows a neutral placeholder until
             real text arrives, then the live transcript as deltas come in. Stays visible after
             recording stops so the student can review it before Submit; cleared on a fresh/
             re-recorded take, a new question or successful submit (applyState), or moving on
             (restart/startFresh/unmount). Styled as a draft-answer card: same rounded/colored
             family as the submitted-answer chat bubble below, but dashed and muted to read as
             "not yet submitted" rather than final. -->
        <div class="live-caption-box mt-3" dir="ltr">
          <div class="live-caption-label text-caption text-medium-emphasis d-flex align-center mb-1">
            <v-icon icon="mdi-closed-caption-outline" size="14" class="mr-1" />
            Transcript preview
          </div>
          <div class="live-caption-text">
            <span v-if="liveCaption.transcript.value">{{ liveCaption.transcript.value }}</span>
            <span v-else class="live-caption-placeholder text-medium-emphasis">Your spoken answer will appear here while you record.</span>
          </div>
        </div>

        <div class="speaking-action-bar mt-3">
          <div class="mcq-action-status" :class="recorder.audioBlob.value ? 'text-success' : 'text-medium-emphasis'">
            <v-icon :icon="recorder.audioBlob.value ? 'mdi-check-circle-outline' : 'mdi-microphone-outline'" size="16" />
            <span>{{ speakingActionText }}</span>
          </div>
          <v-btn
            color="secondary" variant="flat" :loading="busy"
            :disabled="busy || preparingSpeech || !recorder.audioBlob.value || recorder.recording.value || rateLimitBlocked || timeExpired"
            prepend-icon="mdi-send" @click="sendSpeaking"
          >
            Submit answer
          </v-btn>
        </div>
      </v-card>

      <!-- LISTENING / READING / GRAMMAR-VOCAB (MCQ) -->
      <v-card
        v-else-if="isMcqPhase && state.mcq"
        class="glass-card pa-4 mb-3 exam-ltr-card"
        :class="{ 'exam-ltr-card--reading': state.phase === 'reading' }"
        variant="flat"
        dir="ltr"
      >
        <div class="mcq-card-header mb-3">
          <div>
            <div class="text-caption text-medium-emphasis">
          {{ skillLabel(state.phase) }} — question {{ state.mcq.item_index + 1 }}
            </div>
            <div v-if="mcqSectionSubtitle" class="text-body-2 text-medium-emphasis">
              {{ mcqSectionSubtitle }}
            </div>
          </div>
          <v-chip
            v-if="isMcqBundle || isGapFillBundle"
            size="small"
            :color="canSubmitMcq ? 'success' : 'warning'"
            variant="tonal"
            :prepend-icon="canSubmitMcq ? 'mdi-check-circle-outline' : 'mdi-progress-pencil'"
          >
            {{ mcqProgressText }}
          </v-chip>
        </div>

        <template v-if="state.phase === 'listening'">
          <section class="listening-audio-panel mb-3">
            <div class="d-flex align-center justify-space-between gap-2 flex-wrap mb-2">
              <div>
                <div class="reading-panel-label text-caption text-medium-emphasis mb-1">Audio</div>
                <p v-if="state.mcq.situation" class="text-body-2 text-medium-emphasis mb-0">{{ state.mcq.situation }}</p>
              </div>
              <v-chip size="small" :color="listensLeft ? 'secondary' : 'warning'" variant="tonal" prepend-icon="mdi-volume-high">
                {{ listenCount === 0 ? `${MAX_LISTENS} plays available` : `${listensLeft} plays left` }}
              </v-chip>
            </div>
            <template v-if="state.mcq.audio_url && !audioFailed">
              <audio
                :src="audioSrc(state.mcq.audio_url)"
                :controls="listenCount < MAX_LISTENS"
                class="w-100 mb-2"
                @play="onListenPlay"
                @error="onAudioUnavailable"
                @loadedmetadata="onAudioMetadata"
              />
              <div class="text-caption" :class="listeningRequiresPlayback ? 'text-medium-emphasis' : 'text-success'">
                <template v-if="listeningRequiresPlayback">Play the audio to unlock the question.</template>
                <template v-else>The question is unlocked.</template>
              </div>
            </template>
            <v-alert v-else type="warning" variant="tonal" density="compact" class="mb-0">
              Audio playback is unavailable for this clip.
            </v-alert>
          </section>
        </template>
        <template v-else-if="state.phase === 'reading'">
          <section class="reading-passage-panel">
            <div class="reading-panel-label text-caption text-medium-emphasis mb-1">Passage</div>
            <div class="passage-box pa-3">{{ state.mcq.passage }}</div>
          </section>
        </template>
        <p v-else class="text-body-2 text-medium-emphasis mb-3" dir="ltr">{{ state.mcq.instructions }}</p>

        <!-- Listening questions remain hidden until a real audio playback begins. -->
        <section class="mcq-question-shell">
        <template v-if="showMcqQuestion">
          <p v-if="state.mcq.question && !isMcqBundle && !isGapFillBundle" class="text-body-1 font-weight-medium mb-2">{{ state.mcq.question }}</p>

          <template v-if="isMcqBundle">
            <div
              v-for="(sq, sIdx) in state.mcq.subquestions"
              :key="sIdx"
              class="mcq-bundle-block mb-4"
              :class="subquestionStateClass(sq, sIdx)"
            >
              <div class="bundle-question-head mb-2">
                <p class="bundle-question-title text-body-1 font-weight-medium mb-0">
                  {{ sIdx + 1 }}. {{ sq.question }}
                </p>
                <v-chip
                  size="x-small"
                  :color="subquestionTypeColor(sq)"
                  variant="tonal"
                  :prepend-icon="subquestionTypeIcon(sq)"
                >
                  {{ subquestionTypeLabel(sq) }}
                </v-chip>
              </div>
              <p class="text-caption text-medium-emphasis mb-2">{{ subquestionInstruction(sq) }}</p>
              <template v-if="isTextAnswerSubquestion(sq)">
                <div v-if="hasSubquestionWordBank(sq)" class="word-bank-box mb-2">
                  <div class="text-caption text-medium-emphasis mb-1">Word bank</div>
                  <div class="d-flex flex-wrap gap-2">
                    <v-chip
                      v-for="(w, i) in sq.word_bank"
                      :key="i"
                      size="small"
                      :variant="bundleAnswers[sIdx] === w ? 'flat' : 'tonal'"
                      color="secondary"
                      class="word-bank-chip"
                      :disabled="timeExpired"
                      @click="selectSubquestionWord(sIdx, w)"
                    >
                      {{ w }}
                    </v-chip>
                  </div>
                </div>
                <v-text-field
                  v-model="bundleAnswers[sIdx]"
                  variant="outlined"
                  density="compact"
                  dir="ltr"
                  hide-details
                  class="mb-1"
                  :placeholder="textAnswerPlaceholder(sq)"
                  :disabled="timeExpired"
                />
              </template>
              <template v-else-if="isMatchingSubquestion(sq)">
                <div v-for="(item, mIdx) in sq.matching_items" :key="mIdx" class="matching-row mb-3">
                  <div class="matching-row__prompt">
                    <span class="text-caption text-medium-emphasis d-block mb-1">Match</span>
                    <span>{{ cleanMatchingPrompt(item) }}</span>
                  </div>
                  <v-radio-group
                    v-model="bundleChoices[sIdx][mIdx]"
                    hide-details
                    class="matching-answer-options"
                    :disabled="timeExpired"
                  >
                    <v-radio
                      v-for="option in matchSelectItems(sq)"
                      :key="option.value"
                      :value="option.value"
                      :label="option.title"
                      density="compact"
                    />
                  </v-radio-group>
                </div>
              </template>
              <v-radio-group v-else v-model="bundleChoices[sIdx]" hide-details class="mb-0 mcq-options-ltr" :disabled="timeExpired">
                <v-radio v-for="(opt, i) in sq.options" :key="i" :value="i" :label="opt" />
              </v-radio-group>
              <div v-if="shouldHighlightMissing(sq, sIdx)" class="missing-answer-note text-caption mt-2">
                This one still needs an answer.
              </div>
            </div>
          </template>

          <template v-else-if="isGapFillBundle">
            <p class="text-caption text-medium-emphasis mb-2">Complete the notes below.</p>
            <p class="note-completion-box pa-3 mb-3" dir="ltr">
              <template v-for="(part, pIdx) in noteTemplateParts" :key="pIdx">
                <span v-if="part.type === 'text'">{{ part.value }}</span>
                <input
                  v-else
                  v-model="bundleAnswers[part.index]"
                  type="text"
                  class="note-blank-input"
                  :aria-label="`Blank ${part.index + 1}`"
                  :disabled="timeExpired"
                >
              </template>
            </p>
          </template>

          <template v-else-if="isGapFillQuestion">
            <div v-if="wordBankOptions.length" class="word-bank-box mb-2">
              <div class="text-caption text-medium-emphasis mb-1">Word bank</div>
              <div class="d-flex flex-wrap gap-2">
                <v-chip
                  v-for="(w, i) in wordBankOptions"
                  :key="i"
                  size="small"
                  :variant="gapFillAnswer === w ? 'flat' : 'tonal'"
                  color="secondary"
                  class="word-bank-chip"
                  :disabled="timeExpired"
                  @click="selectGapFillWord(w)"
                >
                  {{ w }}
                </v-chip>
              </div>
            </div>
            <v-text-field
              v-model="gapFillAnswer"
              variant="outlined"
              dir="ltr"
              hide-details
              class="mb-3"
              placeholder="Type your answer…"
              :disabled="timeExpired"
            />
          </template>
          <v-radio-group v-else v-model="choice" hide-details class="mb-3 mcq-options-ltr" :disabled="timeExpired">
            <v-radio v-for="(opt, i) in state.mcq.options" :key="i" :value="i" :label="opt" />
          </v-radio-group>

          <div class="mcq-action-bar">
            <div class="mcq-action-status" :class="canSubmitMcq ? 'text-success' : 'text-medium-emphasis'">
              <v-icon :icon="canSubmitMcq ? 'mdi-check-circle-outline' : 'mdi-alert-circle-outline'" size="16" />
              <span>{{ mcqStatusText }}</span>
            </div>
            <v-btn color="secondary" variant="flat" :loading="busy" :disabled="!canSubmitMcq || rateLimitBlocked || timeExpired" prepend-icon="mdi-arrow-right" @click="sendMcq">
              Next
            </v-btn>
          </div>
        </template>
        <p v-else-if="listeningRequiresPlayback" class="text-caption text-medium-emphasis mb-0">Listen first — the question appears after you play the clip.</p>
        </section>
      </v-card>

      <v-card v-else-if="state.phase === 'content_unavailable'" class="glass-card pa-8 text-center" variant="flat">
        <v-icon icon="mdi-cloud-alert" color="warning" size="42" class="mb-3" />
        <h3 class="text-subtitle-1 font-weight-bold mb-1">This section is temporarily unavailable</h3>
        <p class="text-caption text-medium-emphasis mb-3">
          This is a technical content problem, not a missing answer. Your completed work is preserved.
        </p>
        <v-btn color="warning" variant="tonal" prepend-icon="mdi-refresh" :loading="busy" :disabled="rateLimitBlocked" @click="retryContent">
          Retry section preparation
        </v-btn>
      </v-card>

      <!-- WRITING -->
      <v-card v-else-if="state.phase === 'writing' && state.writing" class="glass-card pa-4 mb-3 writing-exam-card" variant="flat">
        <div class="writing-header mb-3">
          <div>
            <div class="text-caption text-medium-emphasis mb-1">Writing - Task {{ state.writing.task_index || 1 }} of {{ state.writing.task_total || 1 }}</div>
            <div class="text-body-2 text-medium-emphasis">{{ writingTaskProgressText }}</div>
          </div>
          <v-chip size="small" color="secondary" variant="tonal" :prepend-icon="writingTaskIcon">
            {{ writingTaskLabel }}
          </v-chip>
        </div>
        <v-progress-linear :model-value="writingTaskProgressPercent" color="secondary" height="6" rounded class="mb-3" />
        <section class="writing-prompt-box mb-3" dir="ltr">
          <div class="reading-panel-label text-caption text-medium-emphasis mb-1">Prompt</div>
          <p class="text-body-1 font-weight-medium mb-2">{{ state.writing.prompt }}</p>
          <div v-if="writingTaskMeta" class="text-caption text-medium-emphasis">
            {{ writingTaskMeta }}
          </div>
        </section>
        <v-textarea
          v-model="writingText"
          variant="outlined"
          rows="6"
          dir="ltr"
          :disabled="busy || timeExpired"
          placeholder="Write your answer in English…"
          counter
          hide-details="auto"
          class="writing-answer-box"
        />
        <div class="writing-word-panel mt-2">
          <div class="d-flex align-center justify-space-between gap-2 flex-wrap mb-1">
            <span class="text-caption" :class="writingWordCountClass">{{ writingWordStatusText }}</span>
            <span class="text-caption text-medium-emphasis">{{ wordCount }} words</span>
          </div>
          <v-progress-linear :model-value="writingWordProgressPercent" :color="writingWordProgressColor" height="6" rounded />
        </div>
        <div class="writing-action-bar mt-3">
          <div class="mcq-action-status" :class="wordCount >= state.writing.min_words ? 'text-success' : 'text-medium-emphasis'">
            <v-icon :icon="wordCount >= state.writing.min_words ? 'mdi-check-circle-outline' : 'mdi-pencil-outline'" size="16" />
            <span>{{ writingActionText }}</span>
          </div>
          <v-btn color="secondary" variant="flat" :loading="busy" :disabled="wordCount < state.writing.min_words || rateLimitBlocked || timeExpired" prepend-icon="mdi-check" @click="sendWriting">
            {{ writingSubmitLabel }}
          </v-btn>
        </div>
      </v-card>
    </template>

    <!-- SMART LOADER -->
    <v-card v-else-if="view === 'evaluating'" class="glass-card pa-8 text-center exam-loader" variant="flat">
      <div class="loader-orb mb-4">
        <v-progress-circular indeterminate :size="76" :width="5" color="secondary" />
        <v-icon size="30" color="secondary" class="loader-orb__icon">mdi-brain</v-icon>
      </div>
      <h3 class="text-h6 font-weight-bold mb-2">Grading all four skills</h3>
      <p class="text-body-2 text-medium-emphasis loader-msg">{{ loaderMsg }}</p>
    </v-card>

    <!-- REPORT -->
    <template v-else-if="view === 'report' && report">
      <v-card class="glass-card report-hero pa-6 mb-4 text-center" variant="flat">
        <div class="text-caption text-medium-emphasis mb-1">Your overall level</div>
        <div class="cefr-badge">{{ report.overall_level }}</div>
        <div v-if="report.confidence" class="d-flex align-center justify-center gap-2 mt-3 flex-wrap">
          <v-chip size="small" :color="confidenceColor" variant="tonal" prepend-icon="mdi-shield-check">
            Confidence {{ Math.round(report.confidence * 100) }}%
          </v-chip>
        </div>
        <p v-if="consistencyNote" class="text-caption text-medium-emphasis mt-2 mb-0">{{ consistencyNote }}</p>
        <p v-if="report.summary" class="text-body-2 mt-3 mb-0 report-summary">{{ report.summary }}</p>
      </v-card>

      <v-row class="mb-2">
        <v-col v-for="s in skillRows" :key="s.key" cols="6" sm="3">
          <v-card class="glass-card kpi-card pa-4 text-center" variant="flat">
            <v-icon :icon="s.icon" color="secondary" class="mb-1" />
            <div class="text-caption text-medium-emphasis">{{ s.label }}</div>
            <div class="text-h6 font-weight-bold">{{ s.level }}</div>
            <v-progress-linear :model-value="s.pct" :color="barColor(s.pct)" height="6" rounded class="mt-1" />
            <div class="text-caption text-medium-emphasis mt-1">Score {{ s.detail }}</div>
            <div v-if="s.evidence" class="text-caption text-disabled">{{ s.evidence }}</div>
          </v-card>
        </v-col>
      </v-row>

      <section v-if="readingDiagnostics.length" class="section-block">
        <div class="section-block__head">
          <h3 class="section-block__title">Reading breakdown</h3>
          <p class="section-block__subtitle mb-0">
            {{ readingEvidenceSummary }}
          </p>
        </div>
        <v-card class="glass-card pa-3" variant="flat">
          <div v-for="c in readingDiagnostics" :key="c.key" class="mb-2">
            <div class="d-flex justify-space-between text-body-2">
              <span>{{ c.label }}</span>
              <span class="font-weight-bold">{{ c.correct }}/{{ c.answered }}</span>
            </div>
            <v-progress-linear :model-value="c.score" :color="barColor(c.score)" height="6" rounded />
          </div>
        </v-card>
      </section>

      <!-- strongest / weakest + time to next level -->
      <v-row class="mb-2" dense>
        <v-col v-if="report.strongest_skill" cols="6" sm="4">
          <v-card class="glass-card kpi-card kpi-card--success pa-3" variant="flat">
            <div class="text-caption text-medium-emphasis">Strongest skill</div>
            <div class="font-weight-bold text-capitalize">{{ report.strongest_skill }}</div>
          </v-card>
        </v-col>
        <v-col v-if="report.weakest_skill" cols="6" sm="4">
          <v-card class="glass-card kpi-card kpi-card--warning pa-3" variant="flat">
            <div class="text-caption text-medium-emphasis">Focus skill</div>
            <div class="font-weight-bold text-capitalize">{{ report.weakest_skill }}</div>
          </v-card>
        </v-col>
        <v-col v-if="report.weeks_to_next_level" cols="12" sm="4">
          <v-card class="glass-card kpi-card pa-3" variant="flat">
            <div class="text-caption text-medium-emphasis">Est. to next level</div>
            <div class="font-weight-bold">~{{ report.weeks_to_next_level }} weeks</div>
          </v-card>
        </v-col>
      </v-row>

      <!-- speaking breakdown (transcript-assessable criteria) -->
      <section v-if="speakingCriteria.length" class="section-block">
        <div class="section-block__head">
          <h3 class="section-block__title">Speaking breakdown</h3>
          <p class="section-block__subtitle mb-0">Transcript-based criteria; pronunciation is unassessed</p>
        </div>
        <v-card class="glass-card pa-3" variant="flat">
          <div v-for="c in speakingCriteria" :key="c.key" class="mb-2">
            <div class="d-flex justify-space-between text-body-2">
              <span>{{ c.label }}</span><span class="font-weight-bold">{{ c.value.toFixed(1) }}/10</span>
            </div>
            <v-progress-linear :model-value="c.value * 10" :color="barColor(c.value * 10)" height="6" rounded />
          </div>
        </v-card>
      </section>

      <!-- speaking, turn by turn (the detailed per-answer feedback, kept for the end) -->
      <section v-if="report.speaking_turns?.length" class="section-block">
        <div class="section-block__head">
          <h3 class="section-block__title">Speaking — turn by turn</h3>
          <p class="section-block__subtitle mb-0">What you said and how to improve each answer</p>
        </div>
        <v-card v-for="(t, i) in report.speaking_turns" :key="i" class="glass-card pa-3 mb-2" variant="flat" dir="ltr">
          <div v-if="t.question" class="text-caption text-medium-emphasis mb-1">Q: {{ t.question }}</div>
          <p v-if="t.transcription" class="text-body-2 mb-2">“{{ t.transcription }}”</p>
          <div v-if="t.grammar_vocab_feedback" class="text-caption mb-1"><strong>Language:</strong> {{ t.grammar_vocab_feedback }}</div>
          <div v-if="t.pronunciation_feedback" class="text-caption mb-1"><strong>Pronunciation:</strong> {{ t.pronunciation_feedback }}</div>
          <div v-if="t.fluency_note" class="text-caption"><strong>Fluency:</strong> {{ t.fluency_note }}</div>
        </v-card>
      </section>

      <!-- writing breakdown (IELTS 4 criteria) -->
      <section v-if="writingCriteria.length" class="section-block">
        <div class="section-block__head">
          <h3 class="section-block__title">Writing breakdown</h3>
          <p class="section-block__subtitle mb-0">The four IELTS writing criteria</p>
        </div>
        <v-card class="glass-card pa-3" variant="flat">
          <div v-for="c in writingCriteria" :key="c.key" class="mb-2">
            <div class="d-flex justify-space-between text-body-2">
              <span>{{ c.label }}</span><span class="font-weight-bold">{{ c.value.toFixed(1) }}/10</span>
            </div>
            <v-progress-linear :model-value="c.value * 10" :color="barColor(c.value * 10)" height="6" rounded />
          </div>
        </v-card>
      </section>

      <v-row class="mb-2">
        <v-col v-if="report.strengths?.length" cols="12" sm="6">
          <section class="section-block">
            <div class="section-block__head"><h3 class="section-block__title">Strengths</h3></div>
            <v-card class="glass-card pa-3" variant="flat">
              <div v-for="(x, i) in report.strengths" :key="i" class="text-body-2 mb-1"><v-icon size="16" color="success" icon="mdi-check-circle" /> {{ x }}</div>
            </v-card>
          </section>
        </v-col>
        <v-col v-if="report.weaknesses?.length" cols="12" sm="6">
          <section class="section-block">
            <div class="section-block__head"><h3 class="section-block__title">To work on</h3></div>
            <v-card class="glass-card pa-3" variant="flat">
              <div v-for="(x, i) in report.weaknesses" :key="i" class="text-body-2 mb-1"><v-icon size="16" color="warning" icon="mdi-alert-circle" /> {{ x }}</div>
            </v-card>
          </section>
        </v-col>
      </v-row>

      <section v-if="reportUsesScorerFallback || examCorrections.length" class="section-block">
        <div class="section-block__head">
          <h3 class="section-block__title">Language feedback</h3>
          <p class="section-block__subtitle mb-0">Key points from your writing and speaking answers</p>
        </div>
        <v-alert
          v-if="reportUsesScorerFallback"
          type="info"
          variant="tonal"
          class="mb-2 rounded-lg"
          icon="mdi-information-outline"
        >
          Detailed corrections will be available after a full report evaluation. This result uses a conservative fallback score.
        </v-alert>
        <v-card v-else class="glass-card pa-3 mb-2" variant="flat">
          <LanguageCorrectionList :errors="examCorrections" />
        </v-card>
      </section>

      <section v-if="report.recommendations?.length" class="section-block">
        <div class="section-block__head"><h3 class="section-block__title">Your study plan</h3></div>
        <v-card class="glass-card pa-3" variant="flat">
          <div v-for="(x, i) in report.recommendations" :key="i" class="text-body-2 mb-1 d-flex gap-2">
            <v-icon size="16" color="secondary" icon="mdi-arrow-right-circle" />
            <span><strong>{{ i + 1 }}.</strong> {{ x }}</span>
          </div>
        </v-card>
      </section>

      <v-alert v-if="report.recommended_starting_lesson_topic" type="info" variant="tonal" class="mb-4 rounded-lg" icon="mdi-lightbulb-on-outline">
        <strong>Start here:</strong> {{ report.recommended_starting_lesson_topic }}
      </v-alert>

      <div class="d-flex gap-2 flex-wrap">
        <v-btn color="secondary" variant="flat" :to="ROUTES.STUDENT_LANGUAGES" prepend-icon="mdi-view-dashboard-outline">
          Go to my learning home
        </v-btn>
        <v-btn variant="tonal" :to="ROUTES.STUDENT_LANGUAGES_CURRICULUM" prepend-icon="mdi-map-marker-path">
          My learning path
        </v-btn>
        <v-btn variant="text" :loading="busy" prepend-icon="mdi-restart" @click="restart">Take it again</v-btn>
      </div>
    </template>

    <LoadingState v-else-if="view === 'loading'" variant="cards" :count="2" class="mb-6" />
  </div>
</template>

<script setup>
import { computed, onUnmounted, ref, watch } from 'vue'
import PageHeader from '../../../components/common/PageHeader.vue'
import LoadingState from '../../../components/common/LoadingState.vue'
import LanguageModuleTabs from '../../../components/language/LanguageModuleTabs.vue'
import LanguageCorrectionList from '../../../components/language/LanguageCorrectionList.vue'
import { useVoiceRecorder } from '../../../composables/useVoiceRecorder.js'
import { useLiveTranscriptionPreview } from '../../../composables/useLiveTranscriptionPreview.js'
import { syncLevelSeen } from '../../../composables/useLevelUp.js'
import {
  initiateExam,
  fetchExamState,
  submitSpeakingTurn,
  createSpeakingLiveTranscriptionSession,
  answerExamMcq,
  submitExamWriting,
  fetchExamReport,
  retryExamEvaluation,
  abandonExam,
  skipPlacementExam,
} from '../../../api/language.js'
import { getErrorMessage } from '../../../api/client.js'
import { mediaUrl } from '../../../utils/media.js'
import { ROUTES } from '../../../constants/app.js'

const SECTION_META = {
  speaking: { label: 'Speaking', icon: 'mdi-microphone', hint: 'Talk to the AI' },
  listening: { label: 'Listening', icon: 'mdi-headphones', hint: 'Listen & answer' },
  reading: { label: 'Reading', icon: 'mdi-book-open-page-variant', hint: 'Read & answer' },
  grammar_vocab: { label: 'Grammar/Vocab', icon: 'mdi-format-letter-case', hint: 'Use English accurately' },
  writing: { label: 'Writing', icon: 'mdi-pencil', hint: 'Write a reply' },
  interview: { label: 'Interview', icon: 'mdi-account-voice', hint: 'Guided follow-up' },
}
// Core skills shown on the intro screen (the interview is a Phase-2 deep-dive).
// "grammar_vocab" is dropped from the active exam (product decision) but SECTION_META/isMcqPhase/
// skillRows below keep it so any already-persisted session or historical report still renders.
const INTRO_SKILLS = ['speaking', 'listening', 'reading', 'writing']
const SKIP_LEVEL_OPTIONS = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
const CONSISTENCY_LABEL = {
  consistent: 'Spoken and written performance matched — high-confidence result',
  speaking_stronger: 'You performed noticeably stronger speaking than in writing',
  writing_stronger: 'You performed noticeably stronger in writing than speaking',
  live_phase_unavailable: 'Based on the written phase only',
}

const view = ref('intro') // intro | exam | evaluating | report | loading
const loadError = ref('')
const busy = ref(false)
const rateLimitBlocked = ref(false)
const examTimeRemaining = ref(null)
const instructionsDialog = ref(false)
const skipBaselineLevel = ref('B1')

const sessionId = ref(null)
const state = ref(null)
const lastFeedback = ref(null)
const report = ref(null)
const evaluationFailed = ref(false)
const submissionRequestId = ref('')

const reportUsesScorerFallback = computed(() => {
  const r = report.value
  if (!r) return false
  if (r.scorer_fallback_used) return true
  const summary = String(r.summary || '').toLowerCase()
  if (summary.includes('ai grader unavailable')) return true
  return (r.recommendations || []).some((item) =>
    /retry report evaluation|refresh detailed rubric feedback/i.test(String(item || '')),
  )
})

const examCorrections = computed(() =>
  (report.value?.detected_errors || [])
    .filter((e) => e?.original_text && e?.corrected_text)
    .slice(0, 5)
    .map((e) => ({
      original: e.original_text,
      corrected: e.corrected_text,
      type: e.type === 'pronunciation' ? 'pronunciation' : 'grammar',
      explanation: e.rule_explanation || '',
    })),
)

watch(
  () => report.value?.overall_level,
  (level) => {
    syncLevelSeen(level, { allowLower: true })
  },
  { immediate: true },
)

const recorder = useVoiceRecorder({ minSeconds: 1 })
// Speaking's live transcript preview (UX only -- see useLiveTranscriptionPreview.js). Never sent
// for grading; the official transcript remains whatever the backend returns after Submit.
const liveCaption = useLiveTranscriptionPreview()
// True only during the brief window between tapping the mic and the actual recording starting,
// while we give the live-caption channel a bounded chance to become ready first (see
// handleSpeakingRecordToggle) -- never blocks the exam past this timeout.
const preparingSpeech = ref(false)
const LIVE_CAPTION_READY_TIMEOUT_MS = 3000
const uploadFile = ref(null)
const choice = ref(null)
const writingText = ref('')
// Gap Fill Listening answer (question_type === 'gap_fill'). Separate from `choice` since the two
// question types are mutually exclusive per item -- never both populated at once.
const gapFillAnswer = ref('')
const isGapFillQuestion = computed(() => (state.value?.mcq?.question_type || 'mcq') === 'gap_fill')
// Display-only (A1/A2 Gap Fill rows always have one, B1+ optional). Never shown for MCQ.
const wordBankOptions = computed(() => {
  const wb = state.value?.mcq?.word_bank
  return Array.isArray(wb) ? wb : []
})

// Listening bundles (Phase 6): one audio, several sub-answers submitted together.
// bundleChoices[i]/bundleAnswers[i] holds the answer for subquestion/blank i -- resized in
// applyState() whenever a new item loads. Legacy (non-bundle) items never populate these.
const bundleChoices = ref([])
const bundleAnswers = ref([])
const isMcqBundle = computed(() => Array.isArray(state.value?.mcq?.subquestions) && state.value.mcq.subquestions.length > 0)
const bundleQuestionCount = computed(() => state.value?.mcq?.subquestions?.length || 0)
const isTextAnswerSubquestion = (sq) => ['short_answer', 'constructed_response', 'gap_fill'].includes(sq?.response_type || '')
const isMatchingSubquestion = (sq) => (sq?.response_type || '') === 'matching'
const hasSubquestionWordBank = (sq) => (
  sq?.response_type === 'gap_fill' && Array.isArray(sq?.word_bank) && sq.word_bank.length > 0
)
const hasNonChoiceSubquestions = computed(() => (
  Array.isArray(state.value?.mcq?.subquestions)
  && state.value.mcq.subquestions.some((sq) => (sq?.response_type || 'mcq') !== 'mcq')
))
const hasBlankMarker = (text = '') => /_{2,}|\{\{\d+\}\}|\.{3,}|…/.test(String(text || ''))
const textAnswerPlaceholder = (sq) => (
  sq?.response_type === 'gap_fill'
    ? `${hasBlankMarker(sq.question) ? 'Fill the blank' : 'Type the answer'}${sq.max_words ? ` (${sq.max_words} words max)` : ''}`
    : `Short answer${sq?.max_words ? ` (${sq.max_words} words max)` : ''}`
)
const matchSelectItems = (sq) => (Array.isArray(sq?.match_options) ? sq.match_options : [])
  .map((title, value) => ({ title, value }))
const answeredBundleCount = computed(() => (
  isMcqBundle.value
    ? state.value.mcq.subquestions.filter((sq, idx) => isSubquestionAnswered(sq, idx)).length
    : 0
))
const answeredBlankCount = computed(() => (
  isGapFillBundle.value ? bundleAnswers.value.filter((a) => (a || '').trim().length > 0).length : 0
))
const mcqProgressText = computed(() => {
  if (isMcqBundle.value) return `${answeredBundleCount.value}/${bundleQuestionCount.value} answered`
  if (isGapFillBundle.value) return `${answeredBlankCount.value}/${state.value.mcq.blank_count} blanks`
  return canSubmitMcq.value ? 'Ready' : 'Not answered'
})
const mcqStatusText = computed(() => {
  if (canSubmitMcq.value) return 'Ready to continue'
  if (isMcqBundle.value) return `${answeredBundleCount.value} of ${bundleQuestionCount.value} questions answered`
  if (isGapFillBundle.value) return `${answeredBlankCount.value} of ${state.value.mcq.blank_count} blanks filled`
  if (isGapFillQuestion.value) return 'Type your answer to continue'
  return 'Choose one answer to continue'
})
const mcqSectionSubtitle = computed(() => {
  const phase = state.value?.phase
  if (phase === 'reading' && isMcqBundle.value) {
    return `Passage set - ${answeredBundleCount.value} of ${bundleQuestionCount.value} answered`
  }
  if (phase === 'listening') {
    if (listeningRequiresPlayback.value) return 'Play the audio to unlock the question'
    if (isMcqBundle.value) return `Audio set - ${answeredBundleCount.value} of ${bundleQuestionCount.value} answered`
    return canSubmitMcq.value ? 'Question answered' : 'Question unlocked'
  }
  if (isMcqBundle.value) return `${answeredBundleCount.value} of ${bundleQuestionCount.value} answered`
  return ''
})
const isGapFillBundle = computed(() => (
  !!state.value?.mcq?.note_template && Number.isInteger(state.value?.mcq?.blank_count) && state.value.mcq.blank_count > 0
))
// Splits note_template on {{1}}/{{2}}/{{3}} into an ordered list of text/blank segments so the
// template can render inline inputs interleaved with the surrounding note text.
const noteTemplateParts = computed(() => {
  const tpl = state.value?.mcq?.note_template || ''
  const parts = []
  let lastIndex = 0
  const re = /\{\{(\d+)\}\}/g
  let match
  while ((match = re.exec(tpl))) {
    if (match.index > lastIndex) parts.push({ type: 'text', value: tpl.slice(lastIndex, match.index) })
    parts.push({ type: 'blank', index: Number(match[1]) - 1 })
    lastIndex = match.index + match[0].length
  }
  if (lastIndex < tpl.length) parts.push({ type: 'text', value: tpl.slice(lastIndex) })
  return parts
})

const canSubmitMcq = computed(() => {
  if (isMcqBundle.value) {
    return state.value.mcq.subquestions.every((sq, idx) => (
      isTextAnswerSubquestion(sq)
        ? (bundleAnswers.value[idx] || '').trim().length > 0
        : isMatchingSubquestion(sq)
          ? Array.isArray(bundleChoices.value[idx])
            && bundleChoices.value[idx].length === (sq.matching_items || []).length
            && bundleChoices.value[idx].every((c) => c !== null && c !== undefined)
        : bundleChoices.value[idx] !== null && bundleChoices.value[idx] !== undefined
    ))
  }
  if (isGapFillBundle.value) {
    return bundleAnswers.value.length === state.value.mcq.blank_count
      && bundleAnswers.value.every((a) => (a || '').trim().length > 0)
  }
  return isGapFillQuestion.value ? gapFillAnswer.value.trim().length > 0 : choice.value !== null
})

function ensureSubmissionRequestId() {
  if (!submissionRequestId.value) {
    submissionRequestId.value = globalThis.crypto?.randomUUID?.()
      || `placement-${Date.now()}-${Math.random().toString(36).slice(2)}`
  }
  return submissionRequestId.value
}

function selectSubquestionWord(index, word) {
  bundleAnswers.value[index] = String(word || '')
}

function selectGapFillWord(word) {
  gapFillAnswer.value = String(word || '')
}

function subquestionResponseType(sq) {
  return String(sq?.response_type || 'mcq').trim() || 'mcq'
}

function subquestionTypeLabel(sq) {
  const type = subquestionResponseType(sq)
  if (type === 'gap_fill') return 'Word bank answer'
  if (type === 'short_answer' || type === 'constructed_response') return 'Short answer'
  if (type === 'matching') return 'Matching'
  return 'Multiple choice'
}

function subquestionTypeIcon(sq) {
  const type = subquestionResponseType(sq)
  if (type === 'gap_fill') return 'mdi-format-textbox'
  if (type === 'short_answer' || type === 'constructed_response') return 'mdi-pencil-outline'
  if (type === 'matching') return 'mdi-call-split'
  return 'mdi-radiobox-marked'
}

function subquestionTypeColor(sq) {
  const type = subquestionResponseType(sq)
  if (type === 'gap_fill') return 'info'
  if (type === 'short_answer' || type === 'constructed_response') return 'secondary'
  if (type === 'matching') return 'warning'
  return 'primary'
}

function subquestionInstruction(sq) {
  const type = subquestionResponseType(sq)
  const maxWords = sq?.max_words ? `${sq.max_words} words max` : ''
  if (type === 'gap_fill') return hasSubquestionWordBank(sq) ? `Use the word bank or type the answer${maxWords ? ` (${maxWords})` : ''}.` : `Type the missing word or phrase${maxWords ? ` (${maxWords})` : ''}.`
  if (type === 'short_answer' || type === 'constructed_response') return `Answer briefly in English${maxWords ? ` (${maxWords})` : ''}.`
  if (type === 'matching') return 'Choose the best match for each line.'
  return 'Choose one answer.'
}

function cleanMatchingPrompt(text) {
  return String(text || '').replace(/^answer\s+to:\s*/i, '').trim()
}

function isSubquestionAnswered(sq, idx) {
  if (isTextAnswerSubquestion(sq)) return (bundleAnswers.value[idx] || '').trim().length > 0
  if (isMatchingSubquestion(sq)) {
    return Array.isArray(bundleChoices.value[idx])
      && bundleChoices.value[idx].length === (sq.matching_items || []).length
      && bundleChoices.value[idx].every((c) => c !== null && c !== undefined)
  }
  return bundleChoices.value[idx] !== null && bundleChoices.value[idx] !== undefined
}

function shouldHighlightMissing(sq, idx) {
  return answeredBundleCount.value > 0 && !isSubquestionAnswered(sq, idx)
}

function subquestionStateClass(sq, idx) {
  const type = subquestionResponseType(sq).replaceAll('_', '-')
  return [
    `mcq-bundle-block--${type}`,
    {
      'is-answered': isSubquestionAnswered(sq, idx),
      'is-missing': shouldHighlightMissing(sq, idx),
    },
  ]
}

// Listening integrity: questions hidden until first listen; max 2 replays.
const MAX_LISTENS = 2
const listenCount = ref(0)
const audioFailed = ref(false)
const listeningRequiresPlayback = computed(() =>
  state.value?.phase === 'listening'
  && listenCount.value === 0
)
const showMcqQuestion = computed(() => state.value?.phase !== 'listening' || !listeningRequiresPlayback.value)
let prepAttempts = 0

const wordCount = computed(() => writingText.value.trim().split(/\s+/).filter(Boolean).length)
const writingTargetText = computed(() => {
  const writing = state.value?.writing
  if (!writing) return ''
  if (writing.max_words) return `target ${writing.min_words}-${writing.max_words} words`
  return `min ${writing.min_words} words`
})
const writingTaskLabel = computed(() => {
  const taskType = String(state.value?.writing?.task_type || '').trim()
  return taskType ? titleCaseTask(taskType) : 'Writing task'
})
const writingTaskIcon = computed(() => {
  const taskType = String(state.value?.writing?.task_type || '').toLowerCase()
  if (taskType.includes('email') || taskType.includes('message')) return 'mdi-email-outline'
  if (taskType.includes('essay') || taskType.includes('opinion')) return 'mdi-comment-text-outline'
  if (taskType.includes('narrative') || taskType.includes('story') || taskType.includes('describe')) return 'mdi-image-text'
  if (taskType.includes('report')) return 'mdi-file-chart-outline'
  return 'mdi-pencil-outline'
})
const writingTaskProgressText = computed(() => {
  const writing = state.value?.writing
  if (!writing) return 'Writing task'
  return `${Number(writing.task_index || 1)} of ${Number(writing.task_total || 1)} writing tasks`
})
const writingTaskProgressPercent = computed(() => {
  const writing = state.value?.writing
  if (!writing) return 0
  return Math.min(100, (Number(writing.task_index || 1) / Math.max(1, Number(writing.task_total || 1))) * 100)
})
const writingTaskMeta = computed(() => {
  const writing = state.value?.writing
  if (!writing) return ''
  const parts = []
  if (writing.task_type) parts.push(titleCaseTask(writing.task_type))
  if (writingTargetText.value) parts.push(writingTargetText.value)
  if (writing.student_instructions) parts.push(writing.student_instructions)
  return parts.join(' - ')
})
const writingWordCountClass = computed(() => {
  const writing = state.value?.writing
  if (!writing || wordCount.value < writing.min_words) return 'text-medium-emphasis'
  if (writing.max_words && wordCount.value > writing.max_words) return 'text-warning'
  return 'text-success'
})
const writingWordsMissing = computed(() => Math.max(0, Number(state.value?.writing?.min_words || 0) - wordCount.value))
const writingWordsOver = computed(() => {
  const maxWords = Number(state.value?.writing?.max_words || 0)
  return maxWords > 0 ? Math.max(0, wordCount.value - maxWords) : 0
})
const writingWordStatusText = computed(() => {
  if (!state.value?.writing) return `${wordCount.value} words`
  if (writingWordsMissing.value > 0) return `${writingWordsMissing.value} more words needed`
  if (writingWordsOver.value > 0) return `${writingWordsOver.value} words over the suggested limit`
  return writingTargetText.value ? `Within ${writingTargetText.value}` : 'Minimum reached'
})
const writingWordProgressPercent = computed(() => {
  const writing = state.value?.writing
  if (!writing) return 0
  const target = Number(writing.max_words || writing.min_words || 1)
  return Math.min(100, (wordCount.value / Math.max(1, target)) * 100)
})
const writingWordProgressColor = computed(() => {
  if (writingWordsMissing.value > 0) return 'secondary'
  if (writingWordsOver.value > 0) return 'warning'
  return 'success'
})
const writingActionText = computed(() => {
  if (writingWordsMissing.value > 0) return `${writingWordsMissing.value} more words required before submit`
  if (writingWordsOver.value > 0) return 'You can submit, but the answer is longer than requested'
  return 'Ready to submit'
})
const writingSubmitLabel = computed(() => {
  const writing = state.value?.writing
  return writing && Number(writing.task_index || 1) < Number(writing.task_total || 1) ? 'Next task' : 'Finish exam'
})

function titleCaseTask(value) {
  return String(value || '')
    .replace(/^task\d+_?/i, '')
    .replaceAll('_', ' ')
    .trim()
    .replace(/\b\w/g, (c) => c.toUpperCase()) || 'Writing task'
}

const LOADER_MESSAGES = [
  'Reviewing your spoken answers…',
  'Scoring listening comprehension…',
  'Scoring reading comprehension…',
  'Checking grammar and vocabulary…',
  'Grading your writing…',
  'Mapping each skill to a CEFR level…',
  'Writing your placement report…',
]
const loaderMsg = ref(LOADER_MESSAGES[0])
let loaderTimer = null
let pollTimer = null
let prepTimer = null
let pollRunId = 0
let rateLimitTimer = null
let examTimer = null
let expirySyncing = false
// Bumped by every fresh-session action (start/startFresh/restart) so an in-flight speaking
// submission from a now-abandoned session can recognize itself as obsolete when it settles.
let examGeneration = 0

const isSpeakingPhase = computed(() => state.value?.phase === 'speaking' || state.value?.phase === 'interview')
const isMcqPhase = computed(() => ['listening', 'reading', 'grammar_vocab'].includes(state.value?.phase))
const timeExpired = computed(() => {
  if (!state.value) return false
  return Boolean(state.value?.time_expired)
    || (state.value?.phase === 'failed' && state.value?.error_code === 'time_expired')
    || Number(examTimeRemaining.value) <= 0
})
const timeRemainingText = computed(() => {
  const raw = examTimeRemaining.value ?? state.value?.time_remaining_seconds ?? 0
  const totalSeconds = Math.max(0, Math.ceil(Number(raw) || 0))
  const minutes = Math.floor(totalSeconds / 60)
  const seconds = totalSeconds % 60
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
})
const timerColor = computed(() => {
  const remaining = Number(examTimeRemaining.value ?? state.value?.time_remaining_seconds ?? 0)
  if (timeExpired.value || remaining <= 5 * 60) return 'error'
  if (remaining <= 15 * 60) return 'warning'
  return 'secondary'
})
const speakingTurnText = computed(() => {
  const speaking = state.value?.speaking
  if (!speaking) return 'Speaking'
  return `${skillLabel(state.value?.phase)} - answer ${Number(speaking.turn || 1)} of ${Number(speaking.total_turns || 1)}`
})
const speakingStatusLabel = computed(() => {
  if (busy.value) return 'Submitting'
  if (preparingSpeech.value) return 'Preparing'
  if (recorder.recording.value) return 'Recording'
  if (recorder.audioBlob.value) return 'Audio ready'
  return 'Ready'
})
const speakingStatusIcon = computed(() => {
  if (busy.value) return 'mdi-send-clock-outline'
  if (preparingSpeech.value) return 'mdi-timer-sand'
  if (recorder.recording.value) return 'mdi-record-circle-outline'
  if (recorder.audioBlob.value) return 'mdi-check-circle-outline'
  return 'mdi-microphone-outline'
})
const speakingStatusColor = computed(() => {
  if (busy.value || preparingSpeech.value) return 'warning'
  if (recorder.recording.value) return 'error'
  if (recorder.audioBlob.value) return 'success'
  return 'secondary'
})
const speakingActionText = computed(() => {
  if (preparingSpeech.value) return 'Preparing transcript preview'
  if (recorder.recording.value) return 'Stop recording before submitting'
  if (recorder.audioBlob.value) return 'Audio ready for secure transcription'
  return 'Record or upload an answer to continue'
})
const currentSpeakingPrompt = computed(() => String(state.value?.speaking?.examiner_message || '').trim())
const answeredSpeakingTurnCount = computed(() => speakingChat.value.filter((message) => message.role === 'student').length)

// Running chat log for the spoken sections (examiner questions + your transcribed answers).
// No scoring is shown during the exam — all evaluation comes at the end in the report.
const speakingChat = ref([])
function pushExaminer(text) {
  const t = (text || '').trim()
  if (!t) return
  const last = speakingChat.value[speakingChat.value.length - 1]
  if (last && last.role === 'examiner' && last.text === t) return
  speakingChat.value.push({ role: 'examiner', text: t })
}
function pushStudent(text) {
  const t = (text || '').trim()
  if (t) speakingChat.value.push({ role: 'student', text: t })
}

function skillLabel(k) {
  return SECTION_META[k]?.label || k
}
function skillIcon(k) {
  return SECTION_META[k]?.icon || 'mdi-circle-small'
}
// Free section navigation: a section's own completion no longer implies every earlier tab is
// also done, so each tab's checkmark reads its own status from the backend instead of assuming
// "index < current index" (state.completed_sections) rather than the tab's index.
function isSectionDone(sec) {
  return (state.value?.completed_sections || []).includes(sec)
}
function audioSrc(url) {
  return mediaUrl(url)
}

const skillRows = computed(() => {
  const r = report.value
  if (!r) return []
  const percentAsScore10 = (value) => ((Number(value) || 0) / 10).toFixed(1)
  const score10 = (value) => (Number(value) || 0).toFixed(1)
  const rows = [
    {
      key: 'speaking',
      label: 'Speaking',
      icon: 'mdi-microphone',
      level: r.speaking_level,
      pct: (r.speaking_score || 0) * 10,
      detail: `${score10(r.speaking_score)}/10`,
      evidence: 'rubric score',
    },
    {
      key: 'listening',
      label: 'Listening',
      icon: 'mdi-headphones',
      level: r.listening_level,
      pct: r.listening_score_percent || 0,
      detail: `${percentAsScore10(r.listening_score_percent)}/10`,
      evidence: `${Math.round(r.listening_score_percent || 0)}% correct`,
    },
    {
      key: 'reading',
      label: 'Reading',
      icon: 'mdi-book-open-page-variant',
      level: r.reading_level,
      pct: r.reading_score_percent || 0,
      detail: `${percentAsScore10(r.reading_score_percent)}/10`,
      evidence: `${Math.round(r.reading_score_percent || 0)}% correct`,
    },
    {
      key: 'writing',
      label: 'Writing',
      icon: 'mdi-pencil',
      level: r.writing_level,
      pct: (r.writing_score || 0) * 10,
      detail: `${score10(r.writing_score)}/10`,
      evidence: 'rubric score',
    },
  ]
  if (r.grammar_vocab_level) {
    rows.splice(3, 0, {
      key: 'grammar_vocab',
      label: 'Grammar/Vocab',
      icon: 'mdi-format-letter-case',
      level: r.grammar_vocab_level,
      pct: r.grammar_vocab_score_percent || 0,
      detail: `${percentAsScore10(r.grammar_vocab_score_percent)}/10`,
      evidence: `${Math.round(r.grammar_vocab_score_percent || 0)}% correct`,
    })
  }
  return rows
})

const confidenceColor = computed(() => {
  const c = report.value?.confidence || 0
  if (c >= 0.85) return 'success'
  if (c >= 0.7) return 'secondary'
  return 'warning'
})
const consistencyNote = computed(() => CONSISTENCY_LABEL[report.value?.cross_phase_consistency] || '')

const writingCriteria = computed(() => {
  const b = report.value?.writing_breakdown
  if (!b || !Object.keys(b).length) return []
  return [
    { key: 'task_fulfillment', label: 'Task fulfillment', value: b.task_fulfillment || b.task_achievement || 0 },
    { key: 'communicative_achievement', label: 'Communicative achievement', value: b.communicative_achievement || 0 },
    { key: 'organization', label: 'Organization', value: b.organization || b.coherence || 0 },
    { key: 'grammar', label: 'Grammar', value: b.grammar || 0 },
    { key: 'vocabulary', label: 'Vocabulary', value: b.vocabulary || b.lexical || 0 },
    { key: 'spelling_punctuation', label: 'Spelling & punctuation', value: b.spelling_punctuation || 0 },
  ]
})

const readingDiagnostics = computed(() => {
  const b = report.value?.reading_breakdown?.by_subskill
  if (!b || !Object.keys(b).length) return []
  return Object.entries(b).map(([key, value]) => ({
    key,
    label: key.split('_').map((part) => part.charAt(0).toUpperCase() + part.slice(1)).join(' '),
    answered: value.answered || 0,
    correct: value.correct || 0,
    score: value.score_percent || 0,
  }))
})

const readingEvidenceSummary = computed(() => {
  const b = report.value?.reading_breakdown || {}
  const items = b.items_answered || 0
  const avgWords = Math.round(b.average_passage_word_count || 0)
  const levels = Array.isArray(b.levels_seen) && b.levels_seen.length ? b.levels_seen.join(', ') : 'no levels'
  return `${items} texts across ${levels}${avgWords ? ` · avg ${avgWords} words` : ''}`
})

const speakingCriteria = computed(() => {
  const b = report.value?.speaking_breakdown
  if (!b || !Object.keys(b).length) return []
  const criteria = [
    { key: 'fluency', label: 'Fluency & coherence', value: b.fluency || 0 },
    { key: 'lexical', label: 'Lexical resource', value: b.lexical || 0 },
    { key: 'grammar', label: 'Grammar', value: b.grammar || 0 },
  ]
  if (Object.prototype.hasOwnProperty.call(b, 'pronunciation')) {
    criteria.push({ key: 'pronunciation', label: 'Pronunciation', value: b.pronunciation || 0 })
  }
  return criteria
})

function barColor(pct) {
  if (pct >= 75) return 'success'
  if (pct >= 50) return 'secondary'
  if (pct >= 35) return 'warning'
  return 'error'
}

function onUpload(file) {
  const f = Array.isArray(file) ? file[0] : file
  if (f) recorder.setBlob(f)
}

function onListenPlay() {
  listenCount.value += 1
}

const listensLeft = computed(() => Math.max(0, MAX_LISTENS - listenCount.value))

function onAudioUnavailable() {
  audioFailed.value = true
}

function onAudioMetadata(event) {
  const duration = Number(event?.target?.duration || 0)
  if (!Number.isFinite(duration) || duration <= 0.2) {
    audioFailed.value = true
  }
}

function stopExamTimer() {
  if (examTimer) clearInterval(examTimer)
  examTimer = null
}

function resetExamTimer() {
  stopExamTimer()
  examTimeRemaining.value = null
}

function shouldRunExamTimer(data) {
  return data
    && ['speaking', 'interview', 'listening', 'reading', 'grammar_vocab', 'writing', 'preparing', 'content_unavailable'].includes(data.phase)
    && !data.time_expired
}

function markLocalTimeExpired(message = 'Time is up. Please start a fresh attempt.') {
  examTimeRemaining.value = 0
  loadError.value = message
  state.value = {
    ...(state.value || {}),
    phase: 'failed',
    error_code: 'time_expired',
    error_message: message,
    time_expired: true,
    time_remaining_seconds: 0,
  }
  if (recorder.recording.value) recorder.toggleRecording()
  liveCaption.stop()
  preparingSpeech.value = false
}

function isExpiredExamState(data) {
  return data?.phase === 'failed' && data?.error_code === 'time_expired'
}

async function initiateReplacingExpiredAttempt() {
  let data = await initiateExam()
  if (isExpiredExamState(data) && data?.session_id) {
    try {
      await abandonExam(data.session_id)
    } catch {
      /* continue; the backend may already have made this expired attempt inert */
    }
    data = await initiateExam()
  }
  return data
}

async function onExamTimerTick() {
  if (examTimeRemaining.value == null) return
  examTimeRemaining.value = Math.max(0, Math.ceil(Number(examTimeRemaining.value) || 0) - 1)
  if (examTimeRemaining.value > 0) return

  stopExamTimer()
  if (expirySyncing || !sessionId.value) {
    markLocalTimeExpired()
    return
  }
  expirySyncing = true
  try {
    const fresh = await fetchExamState(sessionId.value)
    applyState(fresh)
  } catch (error) {
    const detail = error?.response?.data?.detail
    markLocalTimeExpired(detail?.message || 'Time is up. Please start a fresh attempt.')
  } finally {
    expirySyncing = false
  }
}

function syncExamTimer(data) {
  const remaining = Number(data?.time_remaining_seconds)
  examTimeRemaining.value = Number.isFinite(remaining) ? Math.max(0, Math.ceil(remaining)) : null
  stopExamTimer()
  if (shouldRunExamTimer(data)) {
    examTimer = setInterval(onExamTimerTick, 1000)
  }
}

function applyState(data) {
  if (prepTimer) { clearTimeout(prepTimer); prepTimer = null }
  const previousWritingToken = state.value?.prompt_token || state.value?.writing?.prompt_token || ''
  const nextWritingToken = data?.prompt_token || data?.writing?.prompt_token || ''
  state.value = data
  syncExamTimer(data)
  submissionRequestId.value = ''
  // A freshly-applied, current state supersedes any earlier error (e.g. a stale-answer recovery
  // or a prior failed attempt) -- never leave an old banner showing next to a now-current question.
  loadError.value = ''
  if (data.last_feedback) lastFeedback.value = data.last_feedback
  // reset per-section inputs
  choice.value = null
  gapFillAnswer.value = ''
  bundleChoices.value = Array.isArray(data?.mcq?.subquestions)
    ? data.mcq.subquestions.map((sq) => (
      isMatchingSubquestion(sq) ? new Array((sq.matching_items || []).length).fill(null) : null
    ))
    : []
  bundleAnswers.value = Array.isArray(data?.mcq?.subquestions)
    ? new Array(data.mcq.subquestions.length).fill('')
    : Number.isInteger(data?.mcq?.blank_count) ? new Array(data.mcq.blank_count).fill('') : []
  recorder.reset()
  // Every freshly-applied state is a new question/section (or a recovery back to the current
  // one) -- any live caption connection/text from before must not carry over.
  liveCaption.stop()
  liveCaption.reset()
  uploadFile.value = null
  listenCount.value = 0
  audioFailed.value = false
  if (nextWritingToken && nextWritingToken !== previousWritingToken) {
    writingText.value = ''
  }
  if (data.phase === 'evaluating') {
    startEvaluating()
  } else if (data.phase === 'completed') {
    loadReport()
  } else {
    if (data.phase !== 'preparing') prepAttempts = 0
    view.value = 'exam'
    if (data.phase === 'preparing') schedulePrepPoll()
    // Append the examiner's current question to the spoken chat log. Live captions must not open
    // the microphone here; they start only after the student taps the recording button.
    if (isSpeakingPhase.value) pushExaminer(data.speaking?.examiner_message)
  }
}

function retryAfterMs(error, fallbackMs) {
  const headers = error?.response?.headers
  const raw = headers?.['retry-after'] ?? headers?.get?.('retry-after')
  if (raw == null || raw === '') return fallbackMs
  const seconds = Number(raw)
  if (Number.isFinite(seconds) && seconds >= 0) {
    return Math.min(5 * 60 * 1000, Math.max(1000, Math.ceil(seconds * 1000)))
  }
  const retryAt = Date.parse(raw)
  if (Number.isFinite(retryAt)) {
    return Math.min(5 * 60 * 1000, Math.max(1000, retryAt - Date.now()))
  }
  return fallbackMs
}

function handleRequestError(error, fallbackMessage) {
  const detail = error?.response?.data?.detail
  if (detail?.code === 'time_expired') {
    markLocalTimeExpired(detail.message || 'Time is up. Please start a fresh attempt.')
    return
  }
  if (error?.response?.status !== 429) {
    loadError.value = getErrorMessage(error, fallbackMessage)
    return
  }
  const delayMs = retryAfterMs(error, 30_000)
  const seconds = Math.max(1, Math.ceil(delayMs / 1000))
  rateLimitBlocked.value = true
  if (rateLimitTimer) clearTimeout(rateLimitTimer)
  rateLimitTimer = setTimeout(() => {
    rateLimitTimer = null
    rateLimitBlocked.value = false
  }, delayMs)
  loadError.value = `Too many requests. Please retry in ${seconds} seconds.`
}

async function recoverStaleState(error) {
  const detail = error?.response?.data?.detail
  if (detail?.code !== 'stale_exam_state' || !sessionId.value) return false
  try {
    // Silent recovery: the UI now shows the true current question, so no scary banner is shown
    // for a stale answer once we've successfully resynced -- applyState() clears any leftover
    // loadError from the request that just got rejected. Only a genuine recovery failure (below)
    // or a non-stale error (handled by the caller) should ever surface a visible message.
    applyState(await fetchExamState(sessionId.value))
  } catch (refreshError) {
    handleRequestError(refreshError, 'The exam state changed and could not be refreshed')
  }
  return true
}

function schedulePrepPoll(delayMs = 2500) {
  if (timeExpired.value) return
  prepAttempts += 1
  if (prepAttempts > 30) {
    loadError.value = 'Required exam content is temporarily unavailable. Your answers were preserved.'
    state.value = { ...state.value, phase: 'content_unavailable', evidence_status: 'content_unavailable' }
    return
  }
  prepTimer = setTimeout(async () => {
    prepTimer = null
    try {
      applyState(await fetchExamState(sessionId.value))
    } catch (e) {
      schedulePrepPoll(retryAfterMs(e, 2500))
    }
  }, delayMs)
}

function openInstructions() {
  if (busy.value || rateLimitBlocked.value) return
  instructionsDialog.value = true
}

async function skipPlacement() {
  if (busy.value || rateLimitBlocked.value) return
  busy.value = true
  loadError.value = ''
  try {
    await skipPlacementExam(skipBaselineLevel.value)
    window.location.assign(ROUTES.STUDENT_LANGUAGES)
  } catch (e) {
    handleRequestError(e, 'Could not skip the placement exam')
  } finally {
    busy.value = false
  }
}

async function start() {
  if (busy.value || rateLimitBlocked.value) return
  examGeneration += 1
  resetExamTimer()
  busy.value = true
  loadError.value = ''
  try {
    const data = await initiateReplacingExpiredAttempt()
    sessionId.value = data.session_id
    lastFeedback.value = null
    speakingChat.value = []
    instructionsDialog.value = false
    applyState(data)
  } catch (e) {
    handleRequestError(e, 'Could not start the exam')
  } finally {
    busy.value = false
  }
}

async function retryContent() {
  if (!sessionId.value || busy.value || rateLimitBlocked.value || timeExpired.value) return
  busy.value = true
  loadError.value = ''
  // An explicit retry always gets a fresh auto-poll budget. Without this, once prepAttempts had
  // already passed 30 from an earlier wait, applyState's "phase === 'preparing' -> schedulePrepPoll()"
  // path would immediately re-exceed the cap on the very next tick and show "temporarily
  // unavailable" again even though the server had genuinely just started a new attempt.
  prepAttempts = 0
  try {
    applyState(await fetchExamState(sessionId.value))
  } catch (e) {
    handleRequestError(e, 'Could not retry section preparation')
  } finally {
    busy.value = false
  }
}

// Free section navigation: clicking any section tab jumps straight there, without requiring
// earlier sections to be completed first. Purely a read (GET .../state?section=X) -- never
// resets the exam, never touches any section's saved answers/progress; applyState() below just
// swaps which section's already-existing content is being displayed.
async function jumpToSection(sectionName) {
  if (!sectionName || busy.value || rateLimitBlocked.value || timeExpired.value) return
  if (sectionName === state.value?.phase) return
  busy.value = true
  loadError.value = ''
  try {
    applyState(await fetchExamState(sessionId.value, sectionName))
  } catch (e) {
    handleRequestError(e, 'Could not switch to that section')
  } finally {
    busy.value = false
  }
}

async function startFresh() {
  if (busy.value || rateLimitBlocked.value) return
  examGeneration += 1
  busy.value = true
  loadError.value = ''
  try {
    if (sessionId.value) await abandonExam(sessionId.value)
  } catch {
    /* continue with a fresh initiate attempt */
  } finally {
    sessionId.value = null
    report.value = null
    state.value = null
    lastFeedback.value = null
    speakingChat.value = []
    writingText.value = ''
    choice.value = null
    listenCount.value = 0
    audioFailed.value = false
    uploadFile.value = null
    resetExamTimer()
    recorder.reset()
    liveCaption.stop()
    liveCaption.reset()
    prepAttempts = 0
    busy.value = false
  }
  await start()
}

function discardSpeakingTake() {
  recorder.reset()
  liveCaption.stop()
  liveCaption.reset()
  uploadFile.value = null
  submissionRequestId.value = ''
}

async function handleSpeakingRecordToggle() {
  if (timeExpired.value && !recorder.recording.value) return
  if (recorder.recording.value) {
    // Keep the preview visible after stopping so the student can review it before submitting.
    recorder.toggleRecording()
    liveCaption.stop()
    return
  }
  if (recorder.audioBlob.value) {
    liveCaption.stop()
    liveCaption.reset()
  }
  recorder.toggleRecording()
  if (!liveCaption.unavailable.value) {
    liveCaption.start(() => createSpeakingLiveTranscriptionSession(sessionId.value))
  }
}
async function sendSpeaking() {
  if (!recorder.audioBlob.value || busy.value || rateLimitBlocked.value || timeExpired.value) return
  busy.value = true
  loadError.value = ''
  // Identity of the question this submission answers. If a restart/fresh-start happens (a new
  // generation) or the exam otherwise already moved past this turn before the response arrives,
  // this attempt's outcome is obsolete and must be silently ignored -- never applied, never
  // shown as a stale-answer banner, since the UI (or a newer attempt) has already moved on.
  const myGeneration = examGeneration
  const submittedTurnToken = state.value?.turn_token || state.value?.speaking?.turn_token || ''
  // Free section navigation: which speaking-like section (speaking/interview) is actually being
  // viewed, since it may differ from the session's internal progress cursor.
  const submittedSection = state.value?.phase
  const isObsolete = () =>
    myGeneration !== examGeneration
    || submittedTurnToken !== (state.value?.turn_token || state.value?.speaking?.turn_token || '')
  try {
    const data = await submitSpeakingTurn(
      sessionId.value,
      recorder.audioBlob.value,
      recorder.elapsed.value,
      ensureSubmissionRequestId(),
      state.value.state_revision,
      submittedTurnToken,
      submittedSection,
    )
    if (isObsolete()) return
    // Show what the student said as a chat bubble (no scoring shown until the final report).
    pushStudent(data.last_feedback?.transcription)
    applyState(data)
  } catch (e) {
    if (isObsolete()) return
    if (e?.response?.data?.detail?.code === 'stale_exam_state') {
      // Background content preparation merges into the exam state moments after the exam starts
      // (all section content is cache-backed now, so the merge lands while the student is still
      // recording their first answer) and bumps state_revision -- making the revision this
      // submission carries stale even though the question itself never changed. The turn token
      // only rotates when a turn is actually answered, so if the fresh state still shows the
      // SAME token, this is that harmless background bump: retry once with the fresh revision
      // instead of silently discarding the student's recording.
      try {
        const fresh = await fetchExamState(sessionId.value, submittedSection)
        if (isObsolete()) return
        const freshToken = fresh?.turn_token || fresh?.speaking?.turn_token || ''
        if (freshToken && freshToken === submittedTurnToken && fresh?.state_revision) {
          const retry = await submitSpeakingTurn(
            sessionId.value,
            recorder.audioBlob.value,
            recorder.elapsed.value,
            ensureSubmissionRequestId(),
            fresh.state_revision,
            submittedTurnToken,
            submittedSection,
          )
          if (isObsolete()) return
          pushStudent(retry.last_feedback?.transcription)
          applyState(retry)
          return
        }
        // The question genuinely moved on -- same silent resync recoverStaleState performs.
        applyState(fresh)
        return
      } catch (retryError) {
        if (isObsolete()) return
        if (!(await recoverStaleState(retryError))) handleRequestError(retryError, 'Could not submit your answer')
        return
      }
    }
    if (!(await recoverStaleState(e))) handleRequestError(e, 'Could not submit your answer')
  } finally {
    // Only release busy for the generation that set it -- a stale attempt from an abandoned
    // session must not clear the busy flag a newer start/restart is currently using.
    if (myGeneration === examGeneration) busy.value = false
  }
}

async function sendMcq() {
  if (!canSubmitMcq.value || busy.value || rateLimitBlocked.value || timeExpired.value) return
  const mcqBundle = isMcqBundle.value
  const gapFillBundle = isGapFillBundle.value
  const gapFill = isGapFillQuestion.value
  busy.value = true
  loadError.value = ''
  try {
    const subquestionAnswers = mcqBundle && hasNonChoiceSubquestions.value
      ? state.value.mcq.subquestions.map((sq, idx) => (
        isTextAnswerSubquestion(sq) ? bundleAnswers.value[idx].trim() : bundleChoices.value[idx]
      ))
      : undefined
    const data = await answerExamMcq(
      sessionId.value,
      (mcqBundle || gapFillBundle || gapFill) ? null : choice.value,
      ensureSubmissionRequestId(),
      state.value.state_revision,
      state.value.question_token || state.value.mcq?.question_token,
      (!mcqBundle && !gapFillBundle && gapFill) ? gapFillAnswer.value.trim() : undefined,
      mcqBundle && !hasNonChoiceSubquestions.value ? bundleChoices.value : undefined,
      gapFillBundle ? bundleAnswers.value.map((a) => a.trim()) : undefined,
      // Free section navigation: which section (listening/reading/grammar_vocab) is being viewed,
      // since it may differ from the session's internal progress cursor.
      state.value.phase,
      subquestionAnswers,
    )
    applyState(data)
  } catch (e) {
    if (!(await recoverStaleState(e))) handleRequestError(e, 'Could not save your answer')
  } finally {
    busy.value = false
  }
}

async function sendWriting() {
  if (wordCount.value < (state.value?.writing?.min_words || 0) || busy.value || rateLimitBlocked.value || timeExpired.value) return
  busy.value = true
  loadError.value = ''
  const submittedPromptToken = state.value?.prompt_token || state.value?.writing?.prompt_token
  try {
    const data = await submitExamWriting(
      sessionId.value,
      writingText.value.trim(),
      ensureSubmissionRequestId(),
      state.value.state_revision,
      submittedPromptToken,
    )
    if (data.status === 'processing') {
      startEvaluating()
    } else {
      const nextPromptToken = data?.prompt_token || data?.writing?.prompt_token
      if (data?.phase === 'writing' && nextPromptToken && nextPromptToken !== submittedPromptToken) {
        writingText.value = ''
      }
      applyState(data)
    }
  } catch (e) {
    if (!(await recoverStaleState(e))) handleRequestError(e, 'Could not submit your writing')
  } finally {
    busy.value = false
  }
}

async function retryEvaluation() {
  if (!sessionId.value || busy.value || rateLimitBlocked.value) return
  busy.value = true
  loadError.value = ''
  try {
    await retryExamEvaluation(sessionId.value)
    evaluationFailed.value = false
    startEvaluating()
  } catch (e) {
    handleRequestError(e, 'Could not retry the placement evaluation')
  } finally {
    busy.value = false
  }
}

function startEvaluating() {
  finishLoading()
  resetExamTimer()
  const runId = pollRunId
  evaluationFailed.value = false
  view.value = 'evaluating'
  let i = 0
  loaderMsg.value = LOADER_MESSAGES[0]
  loaderTimer = setInterval(() => {
    i = (i + 1) % LOADER_MESSAGES.length
    loaderMsg.value = LOADER_MESSAGES[i]
  }, 1500)
  const startedAt = Date.now()
  let attempts = 0
  const pollReport = async () => {
    pollTimer = null
    attempts += 1
    let nextDelay = 2000
    try {
      const r = await fetchExamReport(sessionId.value)
      if (runId !== pollRunId) return
      const elapsed = Date.now() - startedAt
      if (r.status === 'completed' && r.report && elapsed >= 4000) {
        report.value = r.report
        finishLoading()
        view.value = 'report'
        return
      } else if (r.status === 'failed') {
        finishLoading()
        evaluationFailed.value = true
        loadError.value = r.error_message || 'The report could not be generated. Please retry the evaluation.'
        view.value = 'intro'
        return
      }
    } catch (e) {
      if (runId !== pollRunId) return
      nextDelay = retryAfterMs(e, 2000)
    }
    if (attempts > 45) {
      finishLoading()
      loadError.value = 'Report is taking too long. Please try again later.'
      view.value = 'intro'
      return
    }
    if (runId === pollRunId) pollTimer = setTimeout(pollReport, nextDelay)
  }
  pollTimer = setTimeout(pollReport, 0)
}

async function loadReport() {
  resetExamTimer()
  try {
    const r = await fetchExamReport(sessionId.value)
    if (r.report) {
      report.value = r.report
      view.value = 'report'
    }
  } catch (e) {
    if (e?.response?.status === 429) {
      pollTimer = setTimeout(loadReport, retryAfterMs(e, 30_000))
    } else {
      loadError.value = getErrorMessage(e, 'Could not load your report')
    }
  }
}

function finishLoading() {
  pollRunId += 1
  if (loaderTimer) clearInterval(loaderTimer)
  if (pollTimer) clearTimeout(pollTimer)
  if (prepTimer) clearTimeout(prepTimer)
  loaderTimer = null
  pollTimer = null
  prepTimer = null
}

async function restart() {
  // Best-effort: drop any unfinished attempt so the next start is guaranteed fresh. Bumping the
  // generation marks any still-in-flight speaking submission from this abandoned session as
  // obsolete (see sendSpeaking); resetting busy here (rather than leaving it for that stale
  // attempt's own finally, which now intentionally no-ops across generations) ensures the intro
  // screen's Start button isn't left disabled by a request that no longer owns it.
  examGeneration += 1
  busy.value = false
  liveCaption.stop()
  liveCaption.reset()
  if (sessionId.value) {
    try { await abandonExam(sessionId.value) } catch { /* ignore */ }
  }
  sessionId.value = null
  report.value = null
  state.value = null
  resetExamTimer()
  lastFeedback.value = null
  speakingChat.value = []
  writingText.value = ''
  prepAttempts = 0
  audioFailed.value = false
  loadError.value = ''
  view.value = 'intro'
}

onUnmounted(() => {
  finishLoading()
  resetExamTimer()
  if (rateLimitTimer) clearTimeout(rateLimitTimer)
  liveCaption.stop()
  liveCaption.reset()
})
</script>

<style scoped>
.page-container { max-width: 960px; margin: 0 auto; }
.exam-intro { border: 1px solid rgba(var(--v-theme-secondary), 0.25); }
.intro-time-copy {
  color: rgba(var(--v-theme-on-surface), 0.86);
  font-size: clamp(1rem, 1.8vw, 1.22rem);
  font-weight: 800;
  line-height: 1.55;
}
.skill-pill { border: 1px solid rgba(255, 255, 255, 0.08); }
.skip-placement-box {
  max-width: 520px;
  margin-inline: auto;
  border: 1px solid rgba(var(--v-theme-secondary), 0.16);
  border-radius: 16px;
  background: rgba(var(--v-theme-surface), 0.58);
  padding: 14px;
}
.skip-level-grid {
  display: flex;
  justify-content: center;
  gap: 8px;
  flex-wrap: wrap;
}
.skip-level-chip {
  min-width: 48px;
  border: 1px solid rgba(var(--v-theme-secondary), 0.24);
  border-radius: 999px;
  background: rgba(var(--v-theme-surface), 0.88);
  color: rgb(var(--v-theme-on-surface));
  cursor: pointer;
  font-weight: 800;
  padding: 7px 13px;
}
.skip-level-chip:disabled {
  cursor: not-allowed;
  opacity: 0.64;
}
.skip-level-chip--selected {
  border-color: rgba(var(--v-theme-secondary), 0.72);
  background: rgba(var(--v-theme-secondary), 0.14);
  color: rgb(var(--v-theme-secondary));
}
.section-tab-chip:not(.v-chip--disabled) { cursor: pointer; }
.exam-instructions-dialog {
  border: 1px solid rgba(var(--v-theme-secondary), 0.18);
}
.instruction-list {
  display: grid;
  gap: 10px;
}
.instruction-row {
  display: grid;
  grid-template-columns: 24px 1fr;
  align-items: start;
  gap: 10px;
  color: rgba(var(--v-theme-on-surface), 0.82);
  line-height: 1.45;
}
.exam-toolbar-actions {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.exam-timer-chip {
  font-variant-numeric: tabular-nums;
  min-width: 86px;
  justify-content: center;
}
.exam-ltr-card {
  direction: ltr;
  text-align: left;
}
.mcq-card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}
.exam-ltr-card .passage-box,
.exam-ltr-card .mcq-bundle-block,
.exam-ltr-card .note-completion-box,
.exam-ltr-card .mcq-question-shell {
  direction: ltr;
  text-align: left;
}
.exam-ltr-card--reading {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.reading-passage-panel {
  min-width: 0;
}
.mcq-question-shell {
  min-width: 0;
}
.reading-panel-label {
  text-transform: uppercase;
  letter-spacing: 0;
  font-weight: 700;
}
.listening-audio-panel,
.speaking-question-card,
.writing-prompt-box,
.writing-word-panel {
  border: 1px solid rgba(var(--v-theme-secondary), 0.18);
  border-radius: 8px;
  background: rgba(var(--v-theme-secondary), 0.05);
  padding: 12px;
}
.speaking-exam-card {
  direction: ltr;
  text-align: left;
}
.speaking-header,
.writing-header,
.speaking-action-bar,
.writing-action-bar {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}
.speaking-question-card,
.writing-exam-card,
.writing-prompt-box,
.writing-answer-box {
  direction: ltr;
  text-align: left;
}
.speaking-progress-note {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  direction: ltr;
  text-align: left;
}
.writing-answer-box :deep(textarea) {
  direction: ltr;
  text-align: left;
  line-height: 1.55;
}
.speaking-action-bar,
.writing-action-bar {
  position: sticky;
  bottom: 12px;
  z-index: 2;
  padding: 10px 12px;
  border: 1px solid rgba(var(--v-theme-secondary), 0.18);
  border-radius: 8px;
  background: rgba(var(--v-theme-surface), 0.92);
  backdrop-filter: blur(12px);
}
.recorder-waveform {
  display: flex;
  align-items: end;
  justify-content: center;
  gap: 4px;
  height: 54px;
}
.recorder-waveform span {
  width: 4px;
  min-height: 8px;
  border-radius: 999px;
  background: rgb(var(--v-theme-secondary));
  transition: height 0.08s ease;
}
.mcq-options-ltr {
  direction: ltr;
  text-align: left;
}
.mcq-options-ltr :deep(.v-selection-control-group) {
  align-items: flex-start;
}
.mcq-options-ltr :deep(.v-selection-control) {
  direction: ltr;
  flex-direction: row;
  justify-content: flex-start;
  text-align: left;
}
.mcq-options-ltr :deep(.v-selection-control__wrapper) {
  order: 0;
  margin-inline-start: 0;
  margin-inline-end: 8px;
}
.mcq-options-ltr :deep(.v-label) {
  direction: ltr;
  order: 1;
  text-align: left;
}
.bundle-question-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
}
.bundle-question-title {
  min-width: 0;
  line-height: 1.45;
}
.matching-row {
  border: 1px solid rgba(var(--v-theme-on-surface), 0.08);
  border-radius: 8px;
  padding: 10px;
  background: rgba(var(--v-theme-surface), 0.55);
}
.matching-row__prompt {
  color: rgba(var(--v-theme-on-surface), 0.82);
  line-height: 1.35;
}
.matching-answer-options :deep(.v-selection-control-group) {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 4px 10px;
}
.matching-answer-options :deep(.v-selection-control) {
  align-items: flex-start;
  min-height: 34px;
  direction: ltr;
  text-align: left;
}
.matching-answer-options :deep(.v-selection-control__wrapper) {
  margin-inline-start: 0;
  margin-inline-end: 6px;
}
.matching-answer-options :deep(.v-label) {
  white-space: normal;
  line-height: 1.35;
}
.word-bank-box {
  border: 1px dashed rgba(var(--v-theme-secondary), 0.28);
  border-radius: 8px;
  padding: 8px 10px;
  background: rgba(var(--v-theme-secondary), 0.05);
}
.word-bank-chip {
  cursor: pointer;
}
.mcq-bundle-block {
  border: 1px solid transparent;
  border-radius: 8px;
  padding: 10px 10px 12px;
  transition: border-color 0.18s ease, background 0.18s ease;
}
.mcq-bundle-block.is-answered {
  background: rgba(var(--v-theme-success), 0.04);
  border-color: rgba(var(--v-theme-success), 0.16);
}
.mcq-bundle-block.is-missing {
  background: rgba(var(--v-theme-warning), 0.05);
  border-color: rgba(var(--v-theme-warning), 0.34);
}
.missing-answer-note {
  color: rgb(var(--v-theme-warning));
}
.mcq-action-bar {
  position: sticky;
  bottom: 12px;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 8px;
  padding: 10px 12px;
  border: 1px solid rgba(var(--v-theme-secondary), 0.18);
  border-radius: 8px;
  background: rgba(var(--v-theme-surface), 0.92);
  backdrop-filter: blur(12px);
}
.mcq-action-status {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
  font-size: 0.8125rem;
}
@media (max-width: 760px) {
  .page-container { max-width: 820px; }
  .exam-ltr-card--reading {
    display: flex;
  }
  .reading-passage-panel {
    margin-bottom: 12px;
  }
}
@media (max-width: 640px) {
  .mcq-card-header,
  .bundle-question-head,
  .mcq-action-bar,
  .speaking-header,
  .writing-header,
  .speaking-action-bar,
  .writing-action-bar {
    align-items: stretch;
    flex-direction: column;
  }
  .matching-row {
    grid-template-columns: 1fr;
  }
}
.examiner-q { line-height: 1.5; }
.exam-chat { max-height: 320px; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; }
.exam-msg-row { display: flex; }
.exam-msg-row.is-user { justify-content: flex-end; }
.exam-msg-row.is-ai { justify-content: flex-start; }
.exam-msg { max-width: 86%; padding: 9px 13px; border-radius: 14px; line-height: 1.45; }
.exam-msg--user { background: rgba(var(--v-theme-secondary), 0.16); border: 1px solid rgba(var(--v-theme-secondary), 0.3); }
.exam-msg--ai { background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.08); }
.recorder-box { border: 1px dashed rgba(var(--v-theme-secondary), 0.4); border-radius: 14px; }
.live-caption-box {
  /* Same rounded/colored family as .exam-msg (the submitted-answer bubble below), but dashed
     and more muted -- reads as "draft, not yet submitted" rather than a final answer. */
  background: rgba(var(--v-theme-secondary), 0.07); border: 1px dashed rgba(var(--v-theme-secondary), 0.35);
  border-radius: 14px; padding: 10px 14px; text-align: left;
}
.live-caption-label { letter-spacing: 0.02em; }
.live-caption-text {
  /* No text-size utility class on purpose -- inherits the same base size as .exam-msg so it
     reads as real answer text, not tiny helper copy. min-height reserves the placeholder's own
     line so the box doesn't visually jump when the first real delta replaces it. */
  line-height: 1.5; min-height: 1.5em; max-height: 4.5em; overflow-y: auto;
  white-space: pre-wrap; word-break: break-word; text-align: left;
}
.live-caption-placeholder {
  /* Deliberately smaller/lighter than real transcript text (which inherits the larger, unstyled
     base size above) so the placeholder reads as helper copy, not as if it were an answer. */
  font-size: 0.875rem; font-style: italic;
}
.upload-input { max-width: 360px; margin-inline: auto; }
.passage-box {
  background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px; line-height: 1.75; max-height: none; overflow: visible; white-space: pre-line;
}
.note-completion-box {
  background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px; line-height: 2.1; white-space: pre-line;
}
.note-blank-input {
  display: inline-block; width: 8em; margin: 0 4px; padding: 1px 4px;
  border: none; border-bottom: 2px solid rgba(var(--v-theme-secondary), 0.6);
  background: transparent; font: inherit; color: inherit; text-align: center;
}
.note-blank-input:focus { outline: none; border-bottom-color: rgb(var(--v-theme-secondary)); }
.mcq-bundle-block:not(:last-child) { border-bottom: 1px solid rgba(255, 255, 255, 0.08); padding-bottom: 12px; }
.feedback-card { border: 1px solid rgba(var(--v-theme-secondary), 0.3); }

.exam-loader { border: 1px solid rgba(var(--v-theme-secondary), 0.25); }
.loader-orb { position: relative; display: inline-grid; place-items: center; }
.loader-orb__icon { position: absolute; }
.loader-msg { min-height: 1.4em; transition: opacity 0.3s; }

.report-hero { border: 1px solid rgba(var(--v-theme-secondary), 0.3); }
.cefr-badge {
  display: inline-block; font-size: 2.6rem; font-weight: 800; letter-spacing: 0.04em;
  padding: 6px 26px; border-radius: 16px; color: #fff;
  background: linear-gradient(135deg, var(--em-purple, #7c6cf0), var(--em-cyan, #22d3ee));
  box-shadow: 0 14px 36px -10px rgba(124, 108, 240, 0.6);
}
.report-summary { max-width: 60ch; margin-inline: auto; color: rgba(var(--v-theme-on-surface), 0.78); }
</style>
