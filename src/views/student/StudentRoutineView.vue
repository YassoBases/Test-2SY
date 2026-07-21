<template>
  <div class="routine-page slide-up-enter-active">
    <v-row class="mb-4">
      <v-col><h2 class="text-h5 font-weight-bold">{{ t('student.routine.title') }}</h2><p class="text-caption text-medium-emphasis">{{ t('student.routine.subtitle') }}</p></v-col>
    </v-row>

    <!-- ─── ONBOARDING ─────────────────────────────────────────────── -->
    <div v-if="step === 'onboarding'" class="onboarding-wrap">
      <!-- Hero -->
      <div class="onboarding-hero mb-5">
        <div class="hero-icon"><v-icon size="26" color="cyan">mdi-account-star-outline</v-icon></div>
        <div>
          <h3 class="text-h6 font-weight-bold mb-1">{{ t('student.routine.onboarding.hero.title') }}</h3>
          <p class="text-caption text-medium-emphasis mb-0">{{ t('student.routine.onboarding.hero.subtitleEmoji') }}</p>
        </div>
      </div>

      <!-- 1. grade -->
      <v-card class="onb-section mb-4" variant="flat">
        <div class="onb-section-header">
          <div class="onb-icon onb-icon-primary"><v-icon size="20">mdi-school-outline</v-icon></div>
          <div>
            <p class="text-body-1 font-weight-bold mb-0">{{ t('student.routine.onboarding.grade.title') }}</p>
            <p class="text-caption text-medium-emphasis mb-0">{{ t('student.routine.onboarding.grade.subtitle') }}</p>
          </div>
        </div>
        <v-chip-group v-model="form.grade_level" mandatory selected-class="grade-chip-active" class="grade-chips">
          <v-chip v-for="g in grades" :key="g.value" :value="g.value" class="grade-chip" variant="flat">{{ g.label }}</v-chip>
        </v-chip-group>
      </v-card>

      <!-- 2. school hours -->
      <v-card class="onb-section mb-4" variant="flat">
        <div class="onb-section-header">
          <div class="onb-icon onb-icon-info"><v-icon size="20">mdi-clock-school-outline</v-icon></div>
          <div>
            <p class="text-body-1 font-weight-bold mb-0">{{ t('student.routine.onboarding.school.title') }}</p>
            <p class="text-caption text-medium-emphasis mb-0">{{ t('student.routine.onboarding.school.subtitle') }}</p>
          </div>
        </div>
        <div class="time-pair">
          <v-select v-model="form.school_start" :items="timeOptions" :label="t('student.routine.common.from')" density="comfortable" variant="outlined" hide-details prepend-inner-icon="mdi-clock-start" class="time-field" />
          <div class="time-divider"><v-icon size="18" color="cyan">mdi-arrow-left-thin</v-icon></div>
          <v-select v-model="form.school_end" :items="timeOptions" :label="t('student.routine.common.to')" density="comfortable" variant="outlined" hide-details prepend-inner-icon="mdi-clock-end" class="time-field" />
        </div>
      </v-card>

      <!-- 3. wake and sleep -->
      <v-card class="onb-section mb-4" variant="flat">
        <div class="onb-section-header">
          <div class="onb-icon onb-icon-warning"><v-icon size="20">mdi-weather-night-partly-cloudy</v-icon></div>
          <div>
            <p class="text-body-1 font-weight-bold mb-0">{{ t('student.routine.onboarding.sleep.title') }}</p>
            <p class="text-caption text-medium-emphasis mb-0">{{ t('student.routine.onboarding.sleep.subtitle') }}</p>
          </div>
        </div>
        <v-row dense>
          <v-col cols="12" sm="6">
            <div class="sleep-field-wrap sleep-wake">
              <div class="sleep-field-icon sleep-icon-wake"><v-icon size="20" color="amber">mdi-weather-sunny</v-icon></div>
              <v-select v-model="form.wake_time" :items="timeOptions" :label="t('student.routine.onboarding.wakeTime')" density="comfortable" variant="outlined" hide-details class="sleep-field-select" />
            </div>
          </v-col>
          <v-col cols="12" sm="6">
            <div class="sleep-field-wrap sleep-sleep">
              <div class="sleep-field-icon sleep-icon-sleep"><v-icon size="20" color="indigo-lighten-2">mdi-weather-night</v-icon></div>
              <v-select v-model="form.sleep_time" :items="timeOptions" :label="t('student.routine.onboarding.sleepTime')" density="comfortable" variant="outlined" hide-details class="sleep-field-select" />
            </div>
          </v-col>
        </v-row>
      </v-card>

      <!-- 4. school days -->
      <v-card class="onb-section mb-4" variant="flat">
        <div class="onb-section-header">
          <div class="onb-icon onb-icon-success"><v-icon size="20">mdi-calendar-week-outline</v-icon></div>
          <div>
            <p class="text-body-1 font-weight-bold mb-0">{{ t('student.routine.onboarding.schoolDays.title') }}</p>
            <p class="text-caption text-medium-emphasis mb-0">{{ t('student.routine.onboarding.schoolDays.subtitle') }}</p>
          </div>
        </div>
        <div class="day-chips">
          <button
            v-for="d in dayNames" :key="d.value"
            type="button"
            class="day-chip"
            :class="{ 'day-chip-active': selectedSchoolDays.includes(d.value) }"
            @click="toggleSchoolDay(d.value)"
          >
            {{ d.label }}
          </button>
        </div>
      </v-card>

      <!-- 5. activities -->
      <v-card class="onb-section mb-4" variant="flat">
        <div class="onb-section-header">
          <div class="onb-icon onb-icon-secondary"><v-icon size="20">mdi-star-four-points-outline</v-icon></div>
          <div>
            <p class="text-body-1 font-weight-bold mb-0">{{ t('student.routine.onboarding.activities.heading') }}</p>
            <p class="text-caption text-medium-emphasis mb-0">{{ t('student.routine.onboarding.activities.subtitle') }}</p>
          </div>
        </div>
        <v-chip-group v-model="selectedActivities" multiple selected-class="activity-chip-active" class="activity-chips mb-1">
          <v-chip v-for="a in activities" :key="a" :value="a" class="activity-chip" variant="flat">
            <v-icon start size="17">{{ activityIcons[a] }}</v-icon>{{ activityLabel(a) }}
          </v-chip>
        </v-chip-group>

        <div v-for="act in selectedActivities" :key="act" class="activity-detail mt-3">
          <div class="d-flex align-center gap-2 mb-3">
            <v-icon size="18" color="cyan">{{ activityIcons[act] }}</v-icon>
            <p class="text-body-2 font-weight-bold mb-0">{{ t('student.routine.onboarding.activities.when', { name: activityLabel(act) }) }}</p>
          </div>
          <v-row dense>
            <v-col cols="12" sm="5">
              <p class="text-caption mb-1 text-medium-emphasis">{{ t('student.routine.onboarding.activities.days') }}</p>
              <v-chip-group v-model="activityDetails[act].days" multiple selected-class="grade-chip-active">
                <v-chip v-for="d in dayNames" :key="d.value" :value="d.value" size="small" variant="flat" class="mini-chip">{{ d.label }}</v-chip>
              </v-chip-group>
            </v-col>
            <v-col cols="6" sm="3"><v-select v-model="activityDetails[act].start" :items="timeOptions" :label="t('student.routine.common.from')" density="compact" variant="outlined" hide-details /></v-col>
            <v-col cols="6" sm="3"><v-select v-model="activityDetails[act].end" :items="timeOptions" :label="t('student.routine.common.to')" density="compact" variant="outlined" hide-details /></v-col>
            <v-col v-if="act === ROUTINE_TUTORING_ACTIVITY" cols="12" sm="4">
              <v-text-field v-model="activityDetails[act].subject" :label="t('student.routine.onboarding.activities.subject')" density="compact" variant="outlined" hide-details :placeholder="t('student.routine.onboarding.activities.subjectPlaceholder')" />
            </v-col>
          </v-row>
        </div>
      </v-card>

      <!-- Next button -->
      <div class="onb-next-wrap" @click="logOnboardingNextAttempt">
        <v-btn
          class="onb-next-btn"
          size="x-large"
          :loading="saving"
          :disabled="onboardingNextDisabled"
          @click="saveOnboarding"
        >
          <span>{{ t('student.routine.onboarding.nextCta') }}</span>
          <v-icon end size="20">mdi-arrow-left</v-icon>
        </v-btn>
      </div>
    </div>

    <!-- ─── CHAT ──────────────────────────────────────────────────── -->
    <div v-else-if="step === 'chat'">
      <!-- grade info bar -->
      <v-card class="glass-card pa-3 mb-4" variant="flat">
        <div class="d-flex align-center gap-3 flex-wrap">
          <v-icon color="primary" size="18">mdi-lightbulb-outline</v-icon>
          <span class="text-body-2 font-weight-bold">{{ t('student.routine.preview.gradeChip', { grade: form.grade_level }) }} —</span>
          <v-chip size="x-small" color="primary" variant="tonal">{{ t('student.routine.gradeInfo.sleep', { time: gradeInfo.sleep_ideal }) }}</v-chip>
          <v-chip size="x-small" color="success" variant="tonal">{{ t('student.routine.gradeInfo.study', { hours: gradeInfo.study_hours }) }}</v-chip>
          <span class="text-caption text-medium-emphasis">{{ gradeInfo.notes }}</span>
        </div>
      </v-card>

      <v-row>
        <!-- ── Chat panel ── -->
        <v-col cols="12" lg="5">
          <v-card class="chat-card glass-card" variant="flat">
            <!-- Header -->
            <div class="chat-header">
              <div class="d-flex align-center gap-2">
                <div class="ai-avatar"><v-icon size="18" color="cyan">mdi-calendar-heart</v-icon></div>
                <div>
                  <div class="text-body-2 font-weight-bold">{{ t('student.routine.title') }}</div>
                  <div class="text-caption" style="color:rgba(34,211,238,0.6);line-height:1">{{ t('student.routine.chat.assistantLabel') }}</div>
                </div>
              </div>
              <div class="d-flex gap-1 align-center">
                <v-btn size="x-small" variant="text" color="medium-emphasis" prepend-icon="mdi-cog-outline" @click="openSettings">{{ t('student.routine.settings.title') }}</v-btn>
              </div>
            </div>

            <!-- Messages -->
            <div ref="chatBox" class="chat-messages">
              <template v-for="(msg, i) in messages" :key="i">
                <!-- User message -->
                <div v-if="msg.role === 'user'" class="msg-row msg-user">
                  <div class="msg-bubble msg-bubble-user">
                    <span class="msg-text">{{ msg.content }}</span>
                  </div>
                  <div class="user-avatar-sm"><v-icon size="14" color="white">mdi-account</v-icon></div>
                </div>
                <!-- AI message -->
                <div v-else class="msg-row msg-ai">
                  <div class="ai-avatar-sm"><v-icon size="15" color="cyan">mdi-robot-happy-outline</v-icon></div>
                  <div class="msg-ai-body">
                    <span class="ai-name">{{ t('student.routine.title') }}</span>
                    <template v-if="splitMessage(msg.content).text">
                      <!-- Success confirmation — green badge with checkmark -->
                      <div v-if="successBadgeText(splitMessage(msg.content).text)" class="success-badge-card">
                        <div class="sb-icon"><v-icon size="15" color="white">mdi-check-bold</v-icon></div>
                        <span class="sb-text">{{ successBadgeText(splitMessage(msg.content).text) }}</span>
                      </div>
                      <div v-else class="msg-bubble msg-bubble-ai">
                        <span class="msg-text">{{ splitMessage(msg.content).text }}</span>
                      </div>
                    </template>
                    <!-- Question — visually distinct card -->
                    <div v-if="i < messages.length - 1 && splitMessage(msg.content).question" class="msg-question-card">
                      <div class="q-icon-badge"><v-icon size="14" color="amber">mdi-chat-question-outline</v-icon></div>
                      <span class="q-text">{{ splitMessage(msg.content).question }}</span>
                    </div>
                    <template v-if="!splitMessage(msg.content).text && !splitMessage(msg.content).question">
                      <div v-if="successBadgeText(msg.content)" class="success-badge-card">
                        <div class="sb-icon"><v-icon size="15" color="white">mdi-check-bold</v-icon></div>
                        <span class="sb-text">{{ successBadgeText(msg.content) }}</span>
                      </div>
                      <div v-else class="msg-bubble msg-bubble-ai">
                        <span class="msg-text">{{ msg.content }}</span>
                      </div>
                    </template>
                    <!-- Saved exams — visual schedule table -->
                    <div v-if="msg.examsTable && msg.examsTable.length" class="exam-table-card">
                      <div class="exam-table-header">
                        <v-icon size="17" color="amber">mdi-calendar-alert-outline</v-icon>
                        <span>{{ t('student.routine.chat.examTable.title') }}</span>
                      </div>
                      <div class="exam-table-rows">
                        <div class="exam-row exam-row-head">
                          <span class="exam-col-label">{{ t('student.routine.chat.examTable.subject') }}</span>
                          <span class="exam-col-label">{{ t('student.routine.chat.examTable.date') }}</span>
                          <span class="exam-col-label">{{ t('student.routine.chat.examTable.time') }}</span>
                        </div>
                        <div v-for="(ex, ei) in msg.examsTable" :key="ei" class="exam-row">
                          <span class="exam-subject"><v-icon size="15" color="primary">mdi-book-open-page-variant-outline</v-icon>{{ ex.subject || t('student.routine.chat.examTable.unknownSubject') }}</span>
                          <span class="exam-date"><v-icon size="14" color="info">mdi-calendar-outline</v-icon>{{ formatExamDate(ex.date) }}</span>
                          <span class="exam-time"><v-icon size="14" color="success">mdi-clock-outline</v-icon>{{ ex.time || t('student.routine.chat.examTable.unknownTime') }}</span>
                        </div>
                      </div>
                    </div>
                    <!-- Schedule ready for confirmation — compact per-day timeline card -->
                    <div v-if="msg.scheduleCards" class="schedule-announce-card">
                      <div class="sac-header">
                        <v-icon size="17" color="cyan">mdi-calendar-check-outline</v-icon>
                        <span>{{ t('student.routine.chat.scheduleReady') }}</span>
                      </div>
                      <div class="sac-days">
                        <div v-for="(label, di) in scheduleDayLabels" :key="di" class="sac-day-row">
                          <span class="sac-day-label">{{ label }}</span>
                          <div class="sac-timeline">
                            <span
                              v-for="(slot, si) in (msg.scheduleCards[String(di)] || [])" :key="si"
                              class="sac-dot" :style="{ background: slotMeta(slot.type).color }"
                              :title="`${slot.title} — ${slot.start}-${slot.end}`"
                            >
                              <v-icon size="9" color="white">{{ slotMeta(slot.type).icon }}</v-icon>
                            </span>
                            <span v-if="!(msg.scheduleCards[String(di)] || []).length" class="sac-empty">{{ t('student.routine.chat.emptyDay') }}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </template>
              <!-- Typing indicator (waiting for the AI to respond) -->
              <div v-if="awaitingResponse" class="msg-row msg-ai">
                <div class="ai-avatar-sm"><v-icon size="15" color="cyan">mdi-robot-happy-outline</v-icon></div>
                <div class="msg-bubble msg-bubble-ai typing-bubble">
                  <span class="dot"></span><span class="dot"></span><span class="dot"></span>
                  <span class="typing-label">{{ t('student.routine.chat.typingWithName', { name: t('student.routine.chat.assistantLabel') }) }}</span>
                </div>
              </div>
              <!-- Streaming reply — revealed word by word -->
              <div v-if="streamingActive" class="msg-row msg-ai">
                <div class="ai-avatar-sm"><v-icon size="15" color="cyan">mdi-robot-happy-outline</v-icon></div>
                <div class="msg-ai-body">
                  <span class="ai-name">{{ t('student.routine.title') }}</span>
                  <div class="msg-bubble msg-bubble-ai">
                    <span class="msg-text">{{ streamingText }}<span class="stream-cursor">▍</span></span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Pinned question card — current question, prominent -->
            <div v-if="currentQuestion" class="pinned-question">
              <div class="pinned-question-icon"><v-icon size="18" color="amber">mdi-chat-question-outline</v-icon></div>
              <div class="pinned-question-body">
                <span class="pinned-question-label">{{ t('student.routine.chat.pinnedLabel') }}</span>
                <span class="pinned-question-text">{{ currentQuestion }}</span>
              </div>
            </div>

            <!-- Exam buttons -->
            <div class="chat-actions">
              <v-btn size="small" variant="tonal" color="warning" :loading="uploading" prepend-icon="mdi-image-plus" @click="$refs.examFile.click()">
                {{ t('student.routine.chat.uploadExams') }}
              </v-btn>
              <p class="text-caption text-medium-emphasis mb-0 mt-1">{{ t('student.routine.chat.uploadPdfFormats') }}</p>
              <v-btn size="small" variant="tonal" color="secondary" prepend-icon="mdi-pencil" @click="showExamForm = !showExamForm">
                {{ t('student.routine.chat.manualExams') }}
              </v-btn>
              <input ref="examFile" type="file" accept="image/*,.pdf" style="display:none" @change="uploadExam" />
            </div>

            <!-- Manual exam form -->
            <div v-if="showExamForm" class="exam-form pa-3 mb-2 mx-3 rounded-lg">
              <p class="text-caption font-weight-bold mb-2">{{ t('student.routine.chat.upcomingExams') }}</p>
              <div v-for="(exam, i) in manualExams" :key="i" class="d-flex gap-1 mb-2 align-center">
                <v-text-field v-model="exam.subject" :placeholder="t('student.routine.chat.examTable.subject')" density="compact" hide-details variant="outlined" style="max-width:100px" />
                <v-text-field v-model="exam.date" type="date" density="compact" hide-details variant="outlined" style="max-width:130px" />
                <v-select v-model="exam.time" :items="timeOptions" :placeholder="t('student.routine.chat.examTable.time')" density="compact" hide-details style="max-width:90px" />
                <v-btn icon="mdi-close" size="x-small" variant="text" @click="manualExams.splice(i,1)" />
              </div>
              <div class="d-flex gap-2">
                <v-btn size="x-small" variant="tonal" @click="manualExams.push({subject:'',date:'',time:''})">{{ t('student.routine.chat.addExam') }}</v-btn>
                <v-btn size="x-small" color="primary" variant="tonal" @click="sendManualExams">{{ t('student.routine.chat.submitToAi') }}</v-btn>
              </div>
            </div>

            <!-- Input -->
            <div class="chat-input-row">
              <v-textarea
                v-model="userMessage"
                :placeholder="t('student.routine.chat.inputPlaceholder')"
                density="compact"
                variant="outlined"
                hide-details
                rows="1"
                max-rows="4"
                auto-grow
                no-resize
                class="chat-input"
                @keydown.enter.exact.prevent="sendMessage"
              />
              <v-btn icon color="primary" size="small" :loading="chatting" @click="sendMessage" class="send-btn">
                <v-icon>mdi-send</v-icon>
              </v-btn>
            </div>
          </v-card>
        </v-col>

        <!-- ── Preview panel ── -->
        <v-col cols="12" lg="7">
          <v-card class="glass-card pa-4" variant="flat">
            <div class="d-flex align-center justify-space-between mb-3">
              <h3 class="text-h6 font-weight-bold">{{ t('student.routine.preview.title') }}</h3>
              <v-btn v-if="pendingSchedule" color="success" size="small" @click="confirmSchedule">
                <v-icon start>mdi-check</v-icon>{{ t('student.routine.preview.confirmSave') }}
              </v-btn>
            </div>
            <RoutineWeekPreview v-if="pendingSchedule" :days="pendingSchedule" />

            <!-- Pre-build confirmation summary card — review & edit before generating -->
            <div v-else-if="showConfirmCard" class="confirm-summary-card">
              <div class="cs-header">
                <div class="cs-header-icon"><v-icon size="20" color="success">mdi-clipboard-check-outline</v-icon></div>
                <div>
                  <p class="text-body-2 font-weight-bold mb-0">{{ t('student.routine.preview.reviewTitle') }}</p>
                  <p class="text-caption text-medium-emphasis mb-0">{{ t('student.routine.preview.reviewHint') }}</p>
                </div>
              </div>

              <div class="cs-info-chips">
                <v-chip size="small" variant="tonal" color="primary" prepend-icon="mdi-school-outline">{{ t('student.routine.preview.gradeChip', { grade: summaryData.grade_level }) }}</v-chip>
                <v-chip size="small" variant="tonal" color="info" prepend-icon="mdi-clock-school-outline">{{ t('student.routine.preview.schoolChip', { start: summaryData.school_start, end: summaryData.school_end }) }}</v-chip>
                <v-chip size="small" variant="tonal" color="warning" prepend-icon="mdi-weather-sunset-up">{{ t('student.routine.preview.wakeChip', { time: summaryData.wake_time }) }}</v-chip>
                <v-chip size="small" variant="tonal" color="secondary" prepend-icon="mdi-weather-night">{{ t('student.routine.preview.sleepChip', { time: summaryData.sleep_time }) }}</v-chip>
              </div>

              <div v-if="summaryActivitiesList.length" class="cs-activities">
                <v-chip
                  v-for="a in summaryActivitiesList" :key="a.name"
                  size="small" variant="outlined"
                  :prepend-icon="activityIcons[a.name] || 'mdi-star-outline'"
                >
                  {{ a.name }}<template v-if="a.detail"> — {{ a.detail }}</template>
                </v-chip>
              </div>

              <v-btn size="x-small" variant="text" color="medium-emphasis" prepend-icon="mdi-cog-outline" class="cs-edit-settings-btn" @click="openSettings">
                {{ t('student.routine.preview.editSettings') }}
              </v-btn>

              <v-divider class="my-3" />

              <p class="cs-days-title"><v-icon size="16" color="cyan">mdi-calendar-week</v-icon> {{ t('student.routine.preview.sevenDays') }}</p>
              <div class="cs-days">
                <div v-for="d in summaryData.days" :key="d.day" class="cs-day-item">
                  <div class="cs-day-head">
                    <span class="cs-day-label">{{ d.label }}</span>
                    <v-chip size="x-small" :color="d.type === ROUTINE_DAY_TYPE_SCHOOL ? 'primary' : 'success'" variant="tonal">{{ dayTypeLabel(d.type) }}</v-chip>
                    <v-spacer />
                    <v-btn
                      size="x-small" variant="text" density="comfortable"
                      :icon="editingDay === d.day ? 'mdi-check-bold' : 'mdi-pencil-outline'"
                      :color="editingDay === d.day ? 'success' : 'medium-emphasis'"
                      @click="toggleEditDay(d.day)"
                    />
                  </div>
                  <v-textarea
                    v-if="editingDay === d.day"
                    v-model="editedDays[d.day]"
                    density="compact" variant="outlined" rows="2" auto-grow hide-details
                    class="cs-day-edit"
                  />
                  <template v-else>
                    <!-- Day summary — extracted time slots with activity icons -->
                    <div v-if="daySlotsOrNull(editedDays[d.day])" class="cs-day-slots">
                      <span v-for="(s, si) in daySlotsOrNull(editedDays[d.day])" :key="si" class="cs-slot-chip">
                        <v-icon size="12" :color="s.color">{{ s.icon }}</v-icon>
                        <span class="cs-slot-time">{{ s.time }}</span>
                        <span v-if="s.ctx" class="cs-slot-ctx">{{ s.ctx }}</span>
                      </span>
                    </div>
                    <p class="cs-day-text">{{ editedDays[d.day] }}</p>
                  </template>
                </div>
              </div>

              <v-btn color="success" block size="large" class="cs-confirm-btn mt-4" :loading="confirmingSummary" @click="submitConfirmSummary">
                <v-icon start>mdi-rocket-launch-outline</v-icon> {{ t('student.routine.preview.confirmBuild') }}
              </v-btn>
            </div>

            <div v-else class="schedule-progress">
              <div class="progress-intro">
                <v-icon size="22" color="cyan">mdi-progress-clock</v-icon>
                <div>
                  <p class="text-body-2 font-weight-bold mb-0">{{ t('student.routine.preview.building') }}</p>
                  <p class="text-caption text-medium-emphasis mb-0">{{ t('student.routine.preview.buildingHint') }}</p>
                </div>
              </div>

              <div class="day-progress-grid">
                <div v-for="d in dayProgress" :key="d.label" class="day-progress-item" :class="`dp-${d.status}`">
                  <div class="dp-icon">
                    <v-icon v-if="d.status === 'done'" size="15">mdi-check-bold</v-icon>
                    <v-icon v-else-if="d.status === 'current'" size="15">mdi-pencil-outline</v-icon>
                    <v-icon v-else size="15">mdi-clock-outline</v-icon>
                  </div>
                  <span class="dp-label">{{ d.label }}</span>
                  <v-tooltip v-if="d.status === 'done'" :text="t('student.routine.preview.editDay')" location="top">
                    <template #activator="{ props }">
                      <v-btn
                        v-bind="props"
                        size="x-small" variant="text" icon="mdi-pencil-outline"
                        color="medium-emphasis" class="dp-edit-btn"
                        :disabled="chatting"
                        @click="requestEditDay(d.dayNum)"
                      />
                    </template>
                  </v-tooltip>
                </div>
              </div>

              <div class="progress-bar-row">
                <v-progress-linear :model-value="progressPercent" color="cyan" bg-color="rgba(255,255,255,0.06)" height="7" rounded />
                <span class="text-caption text-medium-emphasis mt-2 d-block text-center">{{ progressLabel }}</span>
              </div>
            </div>
          </v-card>
        </v-col>
      </v-row>
    </div>

    <!-- ─── REVIEW ─────────────────────────────────────────────────── -->
    <div v-else-if="step === 'review'">
      <v-card class="glass-card pa-6 mb-6" variant="flat">
        <div class="d-flex align-center gap-3 mb-4">
          <v-icon color="primary" size="28">mdi-brain</v-icon>
          <div>
            <h3 class="text-h6 font-weight-bold">{{ t('student.routine.review.aiTitle') }}</h3>
            <p class="text-caption text-medium-emphasis">{{ t('student.routine.review.subtitle') }}</p>
          </div>
        </div>
        <div v-if="reviewLoading" class="text-center pa-6">
          <v-progress-circular indeterminate color="primary" size="40" class="mb-3" />
          <p class="text-body-2 text-medium-emphasis">{{ t('student.routine.review.loading') }}</p>
        </div>
        <template v-else>
          <v-alert v-if="reviewText" type="info" variant="tonal" class="mb-4 text-body-2" :text="reviewText" />
          <div v-if="suggestions.length" class="mb-6">
            <p class="text-body-2 font-weight-bold mb-3">{{ t('student.routine.review.suggestions') }}</p>
            <v-card
              v-for="s in suggestions" :key="s.id"
              class="suggestion-card mb-3 pa-4"
              :class="{ 'suggestion-accepted': s.accepted === true, 'suggestion-rejected': s.accepted === false }"
              variant="flat"
            >
              <div class="d-flex align-center justify-space-between gap-3 flex-wrap">
                <div class="flex-1">
                  <div class="d-flex align-center gap-2 mb-1">
                    <v-chip :color="s.priority === 'high' ? 'error' : s.priority === 'medium' ? 'warning' : 'success'" size="x-small" variant="tonal">
                      {{ s.priority === 'high' ? t('student.routine.review.priority.high') : s.priority === 'medium' ? t('student.routine.review.priority.medium') : t('student.routine.review.priority.low') }}
                    </v-chip>
                    <span class="text-body-2 font-weight-bold">{{ s.title }}</span>
                  </div>
                  <p class="text-caption text-medium-emphasis mb-0">{{ s.description }}</p>
                </div>
                <div class="d-flex gap-1">
                  <v-btn v-if="s.accepted !== true" size="small" color="success" variant="tonal" icon="mdi-check" @click="s.accepted = true" />
                  <v-btn v-if="s.accepted !== false" size="small" color="error" variant="tonal" icon="mdi-close" @click="s.accepted = false" />
                  <v-btn v-if="s.accepted !== undefined" size="small" variant="text" icon="mdi-refresh" @click="s.accepted = undefined" />
                </div>
              </div>
            </v-card>
          </div>
          <div class="d-flex gap-3 justify-end flex-wrap">
            <v-btn variant="tonal" color="secondary" @click="step = 'chat'"><v-icon start>mdi-pencil</v-icon>{{ t('student.routine.review.editSchedule') }}</v-btn>
            <v-btn color="primary" size="large" @click="finishReview"><v-icon start>mdi-calendar-check</v-icon>{{ t('student.routine.review.finish') }}</v-btn>
          </div>
        </template>
      </v-card>
      <v-card v-if="weekLoading || weekDays" class="glass-card pa-4" variant="flat">
        <h3 class="text-h6 font-weight-bold mb-3">{{ t('student.routine.review.savedPreview') }}</h3>
        <div v-if="weekLoading && !weekDays" class="pa-4">
          <v-skeleton-loader type="list-item-two-line@3" />
        </div>
        <RoutineWeekPreview v-else-if="weekDays" :days="weekDays" />
      </v-card>
    </div>

    <!-- ─── VIEW ──────────────────────────────────────────────────── -->
    <div v-else-if="step === 'view'">
      <div class="d-flex justify-space-between align-center mb-4 flex-wrap gap-2">
        <h3 class="text-h6 font-weight-bold">{{ t('student.routine.view.weeklyTitle') }}</h3>
        <div class="d-flex gap-2">
          <v-btn variant="tonal" color="secondary" :loading="renewing" @click="doRenewWeek">
            <v-icon start>mdi-refresh</v-icon>{{ t('student.routine.view.renewWeek') }}
          </v-btn>
          <v-btn variant="tonal" color="primary" @click="openSettings">
            <v-icon start>mdi-cog-outline</v-icon>{{ t('student.routine.settings.title') }}
          </v-btn>
        </div>
      </div>
      <div v-if="weekLoading && !weekDays" class="pa-2">
        <v-skeleton-loader type="list-item-two-line@4" />
      </div>
      <RoutineWeekPreview
        v-else
        :days="weekDays || {}"
        :interactive="true"
        :loading-slot="loadingSlot"
        @complete="onSlotComplete"
        @miss="onSlotMiss"
        @undo="onSlotUndo"
      />
    </div>

    <!-- ═══════════════════════════════════════════════════════════════
         DIALOGS
    ══════════════════════════════════════════════════════════════════ -->

    <!-- ── Settings dialog ── -->
    <v-dialog v-model="showSettings" max-width="680" scrollable>
      <v-card class="pa-6" rounded="xl">
        <div class="d-flex align-center justify-space-between mb-5">
          <div>
            <h3 class="text-h6 font-weight-bold">{{ t('student.routine.settings.title') }}</h3>
            <p class="text-caption text-medium-emphasis mb-0">{{ t('student.routine.settings.subtitle') }}</p>
          </div>
          <v-btn icon="mdi-close" variant="text" @click="showSettings = false" />
        </div>

        <v-row>
          <v-col cols="12" md="6">
            <p class="text-body-2 mb-2 font-weight-medium">{{ t('student.routine.settings.grade') }}</p>
            <v-chip-group v-model="settingsForm.grade_level" mandatory selected-class="bg-primary">
              <v-chip v-for="g in grades" :key="g.value" :value="g.value" filter size="small">{{ g.label }}</v-chip>
            </v-chip-group>
          </v-col>
          <v-col cols="12" md="6">
            <p class="text-body-2 mb-2 font-weight-medium">{{ t('student.routine.settings.schoolTime') }}</p>
            <v-row dense>
              <v-col cols="6"><v-select v-model="settingsForm.school_start" :items="timeOptions" :label="t('student.routine.common.from')" density="compact" /></v-col>
              <v-col cols="6"><v-select v-model="settingsForm.school_end" :items="timeOptions" :label="t('student.routine.common.to')" density="compact" /></v-col>
            </v-row>
          </v-col>
          <v-col cols="12" md="6">
            <p class="text-body-2 mb-2 font-weight-medium">{{ t('student.routine.settings.sleepSection') }}</p>
            <v-row dense>
              <v-col cols="6"><v-select v-model="settingsForm.wake_time" :items="timeOptions" :label="t('student.routine.settings.wakeShort')" density="compact" /></v-col>
              <v-col cols="6"><v-select v-model="settingsForm.sleep_time" :items="timeOptions" :label="t('student.routine.settings.sleepShort')" density="compact" /></v-col>
            </v-row>
          </v-col>
          <v-col cols="12">
            <p class="text-body-2 mb-2 font-weight-medium">{{ t('student.routine.settings.schoolDays') }}</p>
            <v-chip-group v-model="settingsForm.school_days" multiple selected-class="bg-primary">
              <v-chip v-for="d in dayNames" :key="d.value" :value="d.value" filter size="small">{{ d.label }}</v-chip>
            </v-chip-group>
          </v-col>
        </v-row>

        <v-divider class="my-5" />

        <div class="d-flex gap-3 justify-space-between flex-wrap">
          <!-- delete schedule -->
          <v-btn
            variant="tonal"
            color="error"
            prepend-icon="mdi-delete-outline"
            :loading="deleting"
            @click="confirmDelete = true"
          >
            {{ t('student.routine.settings.deleteSchedule') }}
          </v-btn>
          <!-- save -->
          <div class="d-flex gap-2">
            <v-btn variant="text" @click="showSettings = false">{{ t('common.cancel') }}</v-btn>
            <v-btn color="primary" :loading="savingSettings" @click="saveSettings">
              <v-icon start>mdi-check</v-icon>{{ t('student.routine.settings.saveChanges') }}
            </v-btn>
          </div>
        </div>
      </v-card>
    </v-dialog>

    <!-- ── Delete confirmation dialog ── -->
    <v-dialog v-model="confirmDelete" max-width="400">
      <v-card class="pa-5" rounded="xl">
        <div class="text-center mb-4">
          <v-icon size="48" color="error" class="mb-2">mdi-alert-circle-outline</v-icon>
          <h3 class="text-h6 font-weight-bold">{{ t('student.routine.delete.title') }}</h3>
          <p class="text-body-2 text-medium-emphasis mt-2">{{ t('student.routine.delete.body') }}</p>
        </div>
        <div class="d-flex gap-3 justify-center">
          <v-btn variant="tonal" @click="confirmDelete = false">{{ t('common.cancel') }}</v-btn>
          <v-btn color="error" :loading="deleting" @click="doDeleteProfile">{{ t('student.routine.delete.confirm') }}</v-btn>
        </div>
      </v-card>
    </v-dialog>

    <!-- ── Exam confirmation dialog ── -->
    <v-dialog v-model="showExamDialog" max-width="600" scrollable>
      <v-card class="pa-5" rounded="xl">
        <div class="d-flex align-center justify-space-between mb-4">
          <div>
            <h3 class="text-h6 font-weight-bold">{{ t('student.routine.exams.confirmTitle') }}</h3>
            <p class="text-caption text-medium-emphasis mb-0">{{ t('student.routine.exams.confirmSubtitle') }}</p>
          </div>
          <v-btn icon="mdi-close" variant="text" @click="showExamDialog = false" />
        </div>

        <div v-if="!pendingExams.length" class="text-center pa-6 text-medium-emphasis">
          <v-icon size="40" class="mb-2">mdi-calendar-remove-outline</v-icon>
          <p>{{ t('student.routine.exams.noneDetected') }}</p>
        </div>

        <div v-else>
          <div
            v-for="(exam, i) in pendingExams"
            :key="i"
            class="exam-row pa-3 rounded-lg mb-2 d-flex align-center gap-2 flex-wrap"
          >
            <v-text-field
              v-model="exam.subject"
              :label="t('student.routine.onboarding.activities.subject')"
              density="compact"
              hide-details
              variant="outlined"
              style="min-width:110px;flex:1"
            />
            <v-text-field
              v-model="exam.date"
              type="date"
:label="t('student.routine.chat.examTable.date')"
              density="compact"
              hide-details
              variant="outlined"
              style="min-width:140px;flex:1"
            />
            <v-select
              v-model="exam.time"
              :items="timeOptions"
              :label="t('student.routine.chat.examTable.time')"
              density="compact"
              hide-details
              style="min-width:100px;max-width:130px"
            />
            <v-btn icon="mdi-delete-outline" size="x-small" variant="text" color="error" @click="pendingExams.splice(i,1)" />
          </div>
          <v-btn
            variant="tonal"
            size="small"
            class="mt-1 mb-3"
            prepend-icon="mdi-plus"
            @click="pendingExams.push({subject:'',date:'',time:''})"
          >
            {{ t('student.routine.exams.add') }}
          </v-btn>
        </div>

        <v-divider class="mb-4" />
        <div class="d-flex gap-3 justify-end">
          <v-btn variant="text" @click="showExamDialog = false">{{ t('common.cancel') }}</v-btn>
          <v-btn
            color="primary"
            :loading="savingExams"
            :disabled="!pendingExams.length"
            @click="saveExams"
          >
            <v-icon start>mdi-content-save-outline</v-icon>{{ t('student.routine.exams.save') }}
          </v-btn>
        </div>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import RoutineWeekPreview from '../../components/routine/RoutineWeekPreview.vue'
import { MAX_PDF_SIZE_BYTES, MAX_PDF_SIZE_LABEL } from '../../constants/app.js'
import {
  chatRoutine, completeSlot, confirmSchedule as confirmApi,
  confirmSummary as confirmSummaryApi, editDay as editDayApi,
  deleteProfile, getRoutineProfile, getWeekRoutine,
  missSlot, renewWeek, reviewRoutine,
  saveConfirmedExams, saveOnboarding as saveApi,
  undoSlot, updateSettings, uploadExamSchedule,
} from '../../api/routine.js'
import {
  ROUTINE_ACTIVITIES,
  ROUTINE_ACTIVITY_ICONS,
  ROUTINE_ACTIVITY_ICON_GROUPS,
  ROUTINE_ACTIVITY_LABEL_KEYS,
  ROUTINE_DAY_TYPE_SCHOOL,
  ROUTINE_DAY_TYPE_WEEKEND,
  ROUTINE_QUESTION_KEYWORDS,
  ROUTINE_QUESTION_MARK,
  ROUTINE_QUESTION_MARKER_LINE,
  ROUTINE_QUESTION_PREFIX,
  ROUTINE_TIME_HOUR_PREFIX,
  ROUTINE_TIME_SLOT_RE,
  ROUTINE_TUTORING_ACTIVITY,
} from '../../constants/routineLexicon.js'

const { t } = useI18n()

const step = ref('onboarding')
const saving = ref(false)
const savingSettings = ref(false)
const savingExams = ref(false)
const deleting = ref(false)
const chatting = ref(false)
const uploading = ref(false)
const renewing = ref(false)
const reviewLoading = ref(false)
const showExamForm = ref(false)
const showSettings = ref(false)
const showExamDialog = ref(false)
const confirmDelete = ref(false)
const manualExams = ref([{ subject: '', date: '', time: '' }])
const pendingExams = ref([])
const userMessage = ref('')
const messages = ref([])
const currentStage = ref('start')
const pendingSchedule = ref(null)
const weekDays = ref(null)
const weekLoading = ref(false)
const chatBox = ref(null)
const reviewText = ref('')
const suggestions = ref([])
const loadingSlot = ref(null)
const awaitingResponse = ref(false)
const streamingActive = ref(false)
const streamingText = ref('')
const summaryData = ref(null)
const confirmingSummary = ref(false)
const editingDay = ref(null)
const editedDays = ref({})

// ─── Static data ──────────────────────────────────────────────────
const GRADE_VALUES = ['7', '8', '9', '10', '11', '12', 'bac']
const grades = computed(() =>
  GRADE_VALUES.map((value) => ({
    value,
    label: t(`student.routine.grades.${value === 'bac' ? 'bac' : 'g' + value}`),
  })),
)
const activities = ROUTINE_ACTIVITIES
const activityIcons = ROUTINE_ACTIVITY_ICONS
const ACTIVITY_LABEL_KEYS = ROUTINE_ACTIVITY_LABEL_KEYS
function activityLabel(act) {
  const key = ACTIVITY_LABEL_KEYS[act]
  return key ? t(`student.routine.activities.${key}`) : act
}
function dayTypeLabel(type) {
  if (type === ROUTINE_DAY_TYPE_SCHOOL) return t('student.routine.dayType.school')
  if (type === ROUTINE_DAY_TYPE_WEEKEND) return t('student.routine.dayType.weekend')
  return type
}
const DAY_SHORT_KEYS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
const dayNames = computed(() =>
  DAY_SHORT_KEYS.map((key, i) => ({ value: i, label: t(`student.routine.days.${key}`) })),
)
const timeOptions = [
  '04:00','04:30','05:00','05:30','06:00','06:30','07:00','07:30','08:00','08:30',
  '09:00','09:30','10:00','10:30','11:00','11:30','12:00','12:30','13:00','13:30',
  '14:00','14:30','15:00','15:30','16:00','16:30','17:00','17:30','18:00','18:30',
  '19:00','19:30','20:00','20:30','21:00','21:30','22:00','22:30','23:00','23:30',
]

// ─── Form state ───────────────────────────────────────────────────
const selectedActivities = ref([])
const selectedSchoolDays = ref([0, 1, 2, 3, 4])
const form = ref({ grade_level: '', school_start: '', school_end: '', wake_time: '', sleep_time: '' })
const settingsForm = ref({ grade_level: '', school_start: '', school_end: '', wake_time: '', sleep_time: '', school_days: [0,1,2,3,4] })
const activityDetails = ref({})

watch(selectedActivities, (list) => {
  list.forEach(a => {
    if (!activityDetails.value[a]) activityDetails.value[a] = { days: [], start: '', end: '', subject: '' }
  })
}, { immediate: true })

// ─── Grade info ───────────────────────────────────────────────────
const GRADE_INFO_BASE = {
  '7-9':    { sleep_ideal: '22:00', studyKey: '79' },
  '10-11':  { sleep_ideal: '23:00', studyKey: '1011' },
  '12-bac': { sleep_ideal: '23:30', studyKey: '12bac' },
}
const gradeInfo = computed(() => {
  const g = form.value.grade_level
  const base = ['7', '8', '9'].includes(g) ? GRADE_INFO_BASE['7-9']
    : ['10', '11'].includes(g) ? GRADE_INFO_BASE['10-11']
    : GRADE_INFO_BASE['12-bac']
  return {
    sleep_ideal: base.sleep_ideal,
    study_hours: t(`student.routine.gradeInfo.studyHours.${base.studyKey}`),
    notes: t(`student.routine.gradeInfo.notes.${base.studyKey}`),
  }
})

// ─── Day-collection progress (mirrors backend STAGES order) ──────
const DAY_STAGE_ORDER = ['day_6', 'day_0', 'day_1', 'day_2', 'day_3', 'day_4', 'day_5']
const DAY_STAGE_KEYS = {
  day_6: 'sunday', day_0: 'monday', day_1: 'tuesday', day_2: 'wednesday',
  day_3: 'thursday', day_4: 'friday', day_5: 'saturday',
}
const DAY_STAGE_LABELS = computed(() =>
  Object.fromEntries(
    Object.entries(DAY_STAGE_KEYS).map(([k, dk]) => [k, t(`student.routine.days.${dk}`)]),
  ),
)
const POST_DAY_STAGES = ['confirm', 'build', 'review', 'done']

const dayProgress = computed(() => {
  const idx = DAY_STAGE_ORDER.indexOf(currentStage.value)
  const allDone = POST_DAY_STAGES.includes(currentStage.value)
  return DAY_STAGE_ORDER.map((s, i) => ({
    stage: s,
    dayNum: parseInt(s.split('_')[1], 10),
    label: DAY_STAGE_LABELS.value[s],
    status: allDone ? 'done' : idx === -1 ? 'pending' : i < idx ? 'done' : i === idx ? 'current' : 'pending',
  }))
})

const progressPercent = computed(() => {
  const done = dayProgress.value.filter(d => d.status === 'done').length
  return Math.round((done / DAY_STAGE_ORDER.length) * 100)
})

const progressLabel = computed(() => {
  const done = dayProgress.value.filter(d => d.status === 'done').length
  if (done === 0) return t('student.routine.progress.notStarted')
  if (done === DAY_STAGE_ORDER.length) return t('student.routine.progress.allDone')
  return t('student.routine.progress.partial', { done, total: DAY_STAGE_ORDER.length })
})

function onboardingNextDisabledReason() {
  if (!form.value.grade_level) return 'missing grade_level'
  if (!form.value.school_start) return 'missing school_start'
  if (!form.value.wake_time) return 'missing wake_time'
  return null
}

const onboardingNextDisabled = computed(() => !!onboardingNextDisabledReason())

function logOnboardingNextAttempt() {
  const reason = onboardingNextDisabledReason()
  console.log('[routine-onboarding] next click', {
    step: step.value,
    disabled: !!reason,
    disabledReason: reason,
    form: { ...form.value },
    schoolDays: [...selectedSchoolDays.value],
    activities: [...selectedActivities.value],
  })
}

async function saveOnboarding() {
  logOnboardingNextAttempt()
  const blocked = onboardingNextDisabledReason()
  if (blocked) {
    console.warn('[routine-onboarding] blocked before save:', blocked)
    return
  }
  if (!form.value.grade_level) {
    console.warn('[routine-onboarding] blocked: empty grade_level')
    return
  }
  saving.value = true
  console.log('[routine-onboarding] POST /student/routine/onboarding', {
    grade_level: form.value.grade_level,
    school_start: form.value.school_start,
    school_end: form.value.school_end,
    wake_time: form.value.wake_time,
    sleep_time: form.value.sleep_time,
    school_days: selectedSchoolDays.value,
  })
  try {
    const activities_obj = {}
    selectedActivities.value.forEach(a => { activities_obj[a] = true })
    const res = await saveApi({ ...form.value, school_days: selectedSchoolDays.value, activities: { ...activities_obj, details: activityDetails.value } })
    console.log('[routine-onboarding] save ok → chat', res)
    currentStage.value = 'exams'
    step.value = 'chat'
    console.log('[routine-onboarding] step transition', { from: 'onboarding', to: step.value, currentStage: currentStage.value })
    if (res?.initial_message) messages.value.push({ role: 'assistant', content: res.initial_message })
    else pushWelcome()
    await scrollChat()
  } catch (err) {
    console.error('[routine-onboarding] save failed — step stays onboarding', {
      status: err?.response?.status,
      detail: err?.response?.data?.detail ?? err?.message,
      url: err?.config?.url,
    })
  } finally { saving.value = false }
}

// ─── Confirmation summary card ────────────────────────────────────
const showConfirmCard = computed(() => currentStage.value === 'confirm' && !!summaryData.value && !pendingSchedule.value)

const summaryActivitiesList = computed(() => {
  const acts = summaryData.value?.activities || {}
  const details = acts.details || {}
  return Object.keys(acts)
    .filter(k => k !== 'details' && acts[k])
    .map(name => {
      const d = details[name] || {}
      const parts = []
      if (d.start && d.end) parts.push(`${d.start} - ${d.end}`)
      if (d.subject) parts.push(d.subject)
      return { name, detail: parts.join(' · ') }
    })
})

watch(summaryData, (val) => {
  if (val?.days) {
    const next = {}
    for (const d of val.days) next[d.day] = d.text
    editedDays.value = next
    editingDay.value = null
  }
})

function toggleEditDay(day) {
  editingDay.value = editingDay.value === day ? null : day
}

async function submitConfirmSummary() {
  if (confirmingSummary.value) return
  confirmingSummary.value = true
  try {
    const days = {}
    for (const [k, v] of Object.entries(editedDays.value)) days[k] = (v || '').trim()
    const res = await confirmSummaryApi(days)
    summaryData.value = null
    if (res.stage) currentStage.value = res.stage
    if (res.reply) await streamReply(res.reply)
    if (res.schedule) {
      const week = await getWeekRoutine()
      weekDays.value = week.days
      step.value = 'view'
    }
  } catch {
    messages.value.push({ role: 'assistant', content: t('student.routine.messages.buildError') })
    await scrollChat()
  } finally {
    confirmingSummary.value = false
  }
}

// ─── Week schedule (read-only load) ─────────────────────────────
async function loadWeekSchedule({ showLoading = false } = {}) {
  if (showLoading) weekLoading.value = true
  try {
    const week = await getWeekRoutine()
    weekDays.value = week.days
    const hasSlots = Object.values(week.days || {}).some((d) => d.length > 0)
    if (!hasSlots && step.value === 'view') {
      step.value = 'chat'
      if (!messages.value.length) pushWelcome()
    }
    return week
  } catch {
    return null
  } finally {
    if (showLoading) weekLoading.value = false
  }
}

// ─── Mount ────────────────────────────────────────────────────────
onMounted(async () => {
  try {
    const profile = await getRoutineProfile()
    if (profile.grade_level) form.value.grade_level = profile.grade_level
    if (profile.school_start) form.value.school_start = profile.school_start
    if (profile.school_end) form.value.school_end = profile.school_end
    if (profile.wake_time) form.value.wake_time = profile.wake_time
    if (profile.sleep_time) form.value.sleep_time = profile.sleep_time
    if (profile.school_days?.length) selectedSchoolDays.value = profile.school_days
    if (profile.chat_stage) currentStage.value = profile.chat_stage
    if (profile.summary_data) summaryData.value = profile.summary_data
    const scheduleReady = profile.onboarding_complete || ['build', 'review', 'done'].includes(profile.chat_stage)
    if (scheduleReady) {
      if (profile.has_schedule) {
        step.value = 'view'
      } else {
        step.value = 'chat'
        pushWelcome()
      }
      void loadWeekSchedule({ showLoading: true })
    } else if (profile.grade_level) {
      step.value = 'chat'
      if (!profile.summary_data && !messages.value.length) pushWelcome()
    }
  } catch {}
})

function pushWelcome() {
  messages.value.push({ role: 'assistant', content: t('student.routine.messages.welcome') })
}

// ─── Onboarding ───────────────────────────────────────────────────
function toggleSchoolDay(value) {
  const idx = selectedSchoolDays.value.indexOf(value)
  if (idx === -1) selectedSchoolDays.value.push(value)
  else selectedSchoolDays.value.splice(idx, 1)
}

// ─── Settings ─────────────────────────────────────────────────────
function openSettings() {
  settingsForm.value = {
    grade_level: form.value.grade_level,
    school_start: form.value.school_start,
    school_end: form.value.school_end,
    wake_time: form.value.wake_time,
    sleep_time: form.value.sleep_time,
    school_days: [...selectedSchoolDays.value],
  }
  showSettings.value = true
}

async function saveSettings() {
  savingSettings.value = true
  try {
    await updateSettings({ ...settingsForm.value })
    form.value.grade_level = settingsForm.value.grade_level
    form.value.school_start = settingsForm.value.school_start
    form.value.school_end = settingsForm.value.school_end
    form.value.wake_time = settingsForm.value.wake_time
    form.value.sleep_time = settingsForm.value.sleep_time
    selectedSchoolDays.value = settingsForm.value.school_days
    showSettings.value = false
  } finally { savingSettings.value = false }
}

async function doDeleteProfile() {
  deleting.value = true
  try {
    await deleteProfile()
    messages.value = []
    weekDays.value = null
    pendingSchedule.value = null
    currentStage.value = 'exams'
    confirmDelete.value = false
    showSettings.value = false
    step.value = 'chat'
    pushWelcome()
  } finally { deleting.value = false }
}

// ─── Chat ─────────────────────────────────────────────────────────
async function sendMessage() {
  const msg = userMessage.value.trim()
  if (!msg || chatting.value) return
  messages.value.push({ role: 'user', content: msg })
  userMessage.value = ''
  chatting.value = true
  awaitingResponse.value = true
  await scrollChat()
  try {
    const res = await chatRoutine(msg)
    awaitingResponse.value = false
    if (res.stage) currentStage.value = res.stage
    summaryData.value = res.summary_data || null
    const scheduleExtra = (res.schedule && res.stage !== 'build') ? { scheduleCards: res.schedule } : {}
    await streamReply(res.reply, scheduleExtra)
    if (res.stage === 'build' && res.schedule) {
      const week = await getWeekRoutine()
      weekDays.value = week.days
      step.value = 'view'
    } else if (res.schedule) {
      pendingSchedule.value = res.schedule
    }
  } catch {
    awaitingResponse.value = false
    messages.value.push({ role: 'assistant', content: t('student.routine.messages.genericError') })
  }
  finally { chatting.value = false; await scrollChat() }
}

// ─── Streaming (typewriter reveal) ────────────────────────────────
async function streamReply(text, extra = {}) {
  if (!text) return
  streamingActive.value = true
  streamingText.value = ''
  const tokens = text.split(/(\s+)/)
  const wordCount = tokens.filter(t => t.trim()).length
  const delay = wordCount > 90 ? 10 : wordCount > 45 ? 16 : 26
  for (const t of tokens) {
    streamingText.value += t
    await scrollChat()
    await new Promise(r => setTimeout(r, delay))
  }
  messages.value.push({ role: 'assistant', content: text, ...extra })
  streamingActive.value = false
  streamingText.value = ''
  await scrollChat()
}

// ─── Edit a completed day (without losing other days) ─────────────
async function requestEditDay(dayNum) {
  if (chatting.value || awaitingResponse.value || streamingActive.value) return
  const label = DAY_STAGE_LABELS[`day_${dayNum}`] || ''
  messages.value.push({ role: 'user', content: t('student.routine.messages.editDay', { day: label }) })
  chatting.value = true
  awaitingResponse.value = true
  await scrollChat()
  try {
    const res = await editDayApi(dayNum)
    awaitingResponse.value = false
    if (res.stage) currentStage.value = res.stage
    summaryData.value = null
    pendingSchedule.value = null
    await streamReply(res.reply)
  } catch {
    awaitingResponse.value = false
    messages.value.push({ role: 'assistant', content: t('student.routine.messages.genericError') })
  } finally {
    chatting.value = false
    await scrollChat()
  }
}

// ─── Confirm schedule ─────────────────────────────────────────────
async function confirmSchedule() {
  if (!pendingSchedule.value) return
  try {
    await confirmApi(pendingSchedule.value)
    const week = await getWeekRoutine()
    weekDays.value = week.days
    pendingSchedule.value = null
    step.value = 'review'
    reviewLoading.value = true
    suggestions.value = []
    reviewText.value = ''
    try {
      const res = await reviewRoutine()
      reviewText.value = res.text || ''
      suggestions.value = (res.suggestions || []).map(s => ({ ...s, accepted: undefined }))
    } catch { reviewText.value = t('student.routine.messages.scheduleReady') }
    finally { reviewLoading.value = false }
  } catch { messages.value.push({ role: 'assistant', content: t('student.routine.messages.saveError') }) }
}

function finishReview() { step.value = 'view' }

// ─── Exam upload ──────────────────────────────────────────────────
async function uploadExam(e) {
  const file = e.target.files?.[0]
  if (!file) return
  const isPdf =
    file.type === 'application/pdf' || String(file.name || '').toLowerCase().endsWith('.pdf')
  if (isPdf && file.size > MAX_PDF_SIZE_BYTES) {
    messages.value.push({
      role: 'assistant',
      content: t('student.routine.messages.pdfTooLarge', { size: MAX_PDF_SIZE_LABEL }),
    })
    e.target.value = ''
    await scrollChat()
    return
  }
  uploading.value = true
  try {
    const res = await uploadExamSchedule(file)
    pendingExams.value = (res.exams || []).map(ex => ({ ...ex }))
    showExamDialog.value = true
  } catch {
    messages.value.push({ role: 'assistant', content: t('student.routine.messages.uploadError') })
    await scrollChat()
  } finally {
    uploading.value = false
    e.target.value = ''
  }
}

async function saveExams() {
  savingExams.value = true
  try {
    const valid = pendingExams.value.filter(e => e.subject && e.date)
    const res = await saveConfirmedExams(valid)
    showExamDialog.value = false
    if (res.stage) currentStage.value = res.stage
    const extra = (res.exams && res.exams.length) ? { examsTable: res.exams } : {}
    if (res.reply) await streamReply(res.reply, extra)
    else messages.value.push({ role: 'assistant', content: t('student.routine.messages.examsSaved', { count: res.saved }), ...extra })
    await scrollChat()
  } finally { savingExams.value = false }
}

// ─── Renew ────────────────────────────────────────────────────────
async function doRenewWeek() {
  renewing.value = true
  try {
    const res = await renewWeek()
    if (res.renewed) {
      const week = await getWeekRoutine()
      weekDays.value = week.days
    }
  } finally { renewing.value = false }
}

// ─── Manual exams ─────────────────────────────────────────────────
async function sendManualExams() {
  const valid = manualExams.value.filter(e => e.subject && e.date)
  if (!valid.length) return
  const text = valid.map(e => t('student.routine.messages.examLine', { subject: e.subject, date: e.date, time: e.time || '9:00' })).join('، ')
  userMessage.value = text
  await sendMessage()
  showExamForm.value = false
  manualExams.value = [{ subject: '', date: '', time: '' }]
}

// ─── Slot actions ─────────────────────────────────────────────────
async function onSlotComplete(id) {
  loadingSlot.value = id + '_complete'
  try { const res = await completeSlot(id); updateSlotStatus(id, res.status) }
  finally { loadingSlot.value = null }
}
async function onSlotMiss(id) {
  loadingSlot.value = id + '_miss'
  try { const res = await missSlot(id); updateSlotStatus(id, res.status) }
  finally { loadingSlot.value = null }
}
async function onSlotUndo(id) {
  loadingSlot.value = id + '_undo'
  try { const res = await undoSlot(id); updateSlotStatus(id, res.status) }
  finally { loadingSlot.value = null }
}
function updateSlotStatus(id, status) {
  if (!weekDays.value) return
  for (const day of Object.values(weekDays.value)) {
    const slot = day.find(s => s.id === id)
    if (slot) { slot.status = status; break }
  }
}

// ─── Exam table formatting ────────────────────────────────────────
function formatExamDate(dateStr) {
  if (!dateStr) return t('student.routine.exams.unknownDate')
  try {
    return new Date(dateStr).toLocaleDateString(undefined, { weekday: 'long', day: 'numeric', month: 'long' })
  } catch {
    return dateStr
  }
}

// ─── Success messages → green badge with checkmark ────────────────
function successBadgeText(text) {
  if (!text) return null
  const trimmed = text.trim()
  if (!trimmed.includes('✅') || trimmed.includes('\n') || trimmed.length > 90) return null
  return trimmed.replace(/✅/g, '').trim()
}

// ─── Day summaries → time-slot chips with activity icons ──────────
const ACTIVITY_ICON_GROUPS = ROUTINE_ACTIVITY_ICON_GROUPS
function iconForActivity(text) {
  for (const g of ACTIVITY_ICON_GROUPS) {
    if (g.keys.some(k => text.includes(k))) return { icon: g.icon, color: g.color }
  }
  return { icon: 'mdi-clock-time-four-outline', color: 'grey' }
}
const TIME_SLOT_RE = ROUTINE_TIME_SLOT_RE
function extractTimeSlots(text) {
  if (!text) return []
  const slots = []
  TIME_SLOT_RE.lastIndex = 0
  let m
  while ((m = TIME_SLOT_RE.exec(text)) && slots.length < 6) {
    const time = m[1].replace(new RegExp(`${ROUTINE_TIME_HOUR_PREFIX}\\s*`), '').trim()
    const ctx = (m[2] || '').trim().replace(/^[\s,،\-]+/, '')
    slots.push({ time, ctx, ...iconForActivity(m[0]) })
  }
  return slots
}
function daySlotsOrNull(text) {
  const slots = extractTimeSlots(text)
  return slots.length >= 2 ? slots : null
}

// ─── Schedule confirmation card → per-day mini timeline ───────────
const scheduleDayLabels = computed(() => DAY_STAGE_ORDER.map((s) => DAY_STAGE_LABELS.value[s]))
const SLOT_TYPE_META = {
  school: { icon: 'mdi-school', color: '#2196F3' },
  study: { icon: 'mdi-book-open', color: '#9C27B0' },
  sport: { icon: 'mdi-run', color: '#4CAF50' },
  meal: { icon: 'mdi-food', color: '#FF9800' },
  sleep: { icon: 'mdi-sleep', color: '#3F51B5' },
  prayer: { icon: 'mdi-hands-pray', color: '#009688' },
  family: { icon: 'mdi-home-heart', color: '#E91E63' },
  private_lesson: { icon: 'mdi-account-school', color: '#673AB7' },
  free: { icon: 'mdi-coffee', color: '#9E9E9E' },
  other: { icon: 'mdi-calendar', color: '#9E9E9E' },
}
function slotMeta(type) { return SLOT_TYPE_META[type] || SLOT_TYPE_META.other }

// ─── Message splitting ────────────────────────────────────────────
function splitMessage(text) {
  const lines = text.split('\n')
  let questionStart = -1
  let skipMarker = false
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim()
    if (line === ROUTINE_QUESTION_MARKER_LINE) { questionStart = i; skipMarker = true; break }
    if (line.startsWith(ROUTINE_QUESTION_PREFIX) && line.includes(':')) { questionStart = i; break }
    if (line.includes(ROUTINE_QUESTION_MARK) && ROUTINE_QUESTION_KEYWORDS.some(k => line.includes(k))) { questionStart = i; break }
  }
  if (questionStart === -1) return { text: text, question: '' }
  const textPart = lines.slice(0, questionStart).join('\n').trim()
  const questionPart = lines.slice(questionStart + (skipMarker ? 1 : 0)).join('\n').trim()
  return { text: textPart, question: questionPart }
}

const currentQuestion = computed(() => {
  const aiMessages = messages.value.filter(m => m.role === 'assistant' || m.role === 'ai')
  if (!aiMessages.length) return ''
  const last = aiMessages[aiMessages.length - 1]
  return splitMessage(last.content).question
})

async function scrollChat() {
  await nextTick()
  if (chatBox.value) chatBox.value.scrollTop = chatBox.value.scrollHeight
}
</script>

<style scoped>
.routine-page { max-width: 1400px; margin-inline: auto; }
.flex-1 { flex: 1; }

/* ─── Chat card ─────────────────────────────────────────── */
.chat-card {
  display: flex;
  flex-direction: column;
  height: 620px;
  overflow: hidden;
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px 12px;
  border-bottom: 1px solid rgba(255,255,255,0.07);
  flex-shrink: 0;
}

.ai-avatar {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  background: rgba(34,211,238,0.12);
  border: 1px solid rgba(34,211,238,0.25);
  display: flex;
  align-items: center;
  justify-content: center;
}

.ai-avatar-sm {
  width: 24px;
  height: 24px;
  border-radius: 8px;
  background: rgba(34,211,238,0.1);
  border: 1px solid rgba(34,211,238,0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 2px;
}

/* ─── Messages ──────────────────────────────────────────── */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 14px 14px 8px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 0;
  scrollbar-width: thin;
  scrollbar-color: rgba(255,255,255,0.1) transparent;
}

.msg-row {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  animation: msgFadeIn 0.28s ease;
}
.msg-user { flex-direction: row-reverse; }
.msg-ai { flex-direction: row; }

@keyframes msgFadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* Avatars — give each sender a clear identity */
.ai-avatar-sm {
  width: 28px; height: 28px;
  border-radius: 9px;
  background: linear-gradient(135deg, rgba(34,211,238,0.22), rgba(124,108,240,0.18));
  border: 1px solid rgba(34,211,238,0.35);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  margin-top: 3px;
  box-shadow: 0 2px 10px rgba(34,211,238,0.12);
}
.user-avatar-sm {
  width: 26px; height: 26px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgb(124,108,240), rgb(99,82,220));
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  margin-top: 4px;
  box-shadow: 0 2px 8px rgba(124,108,240,0.3);
}
.ai-name {
  font-size: 11px;
  font-weight: 700;
  color: rgba(34,211,238,0.65);
  margin-inline-start: 3px;
}

.msg-ai-body {
  display: flex;
  flex-direction: column;
  gap: 5px;
  max-width: 82%;
}

.msg-bubble {
  padding: 11px 14px;
  border-radius: 15px;
  line-height: 1.6;
}

.msg-bubble-user {
  background: linear-gradient(135deg, rgba(124,108,240,0.28), rgba(124,108,240,0.18));
  border: 1px solid rgba(124,108,240,0.32);
  border-radius: 15px 15px 4px 15px;
  max-width: 82%;
}

.msg-bubble-ai {
  background: rgba(255,255,255,0.045);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 4px 15px 15px 15px;
}

.msg-text {
  font-size: 13.5px;
  white-space: pre-wrap;
  word-break: break-word;
}

/* Question inside chat history — visually distinct (warm vs. neutral info) */
.msg-question-card {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  background: rgba(255,179,0,0.06);
  border: 1px solid rgba(255,179,0,0.22);
  border-radius: 12px;
  padding: 9px 12px;
}
.q-icon-badge {
  width: 22px; height: 22px;
  border-radius: 7px;
  background: rgba(255,179,0,0.16);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  margin-top: 1px;
}
.q-text {
  font-size: 12.5px;
  line-height: 1.55;
  color: rgba(255,213,128,0.85);
  white-space: pre-wrap;
}

/* ─── Success message → green badge with checkmark ──────── */
.success-badge-card {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
  padding: 7px 14px 7px 8px;
  border-radius: 999px;
  background: linear-gradient(135deg, rgba(76,175,80,0.22), rgba(76,175,80,0.1));
  border: 1px solid rgba(76,175,80,0.4);
  box-shadow: 0 2px 10px rgba(76,175,80,0.12);
}
.sb-icon {
  width: 22px; height: 22px;
  border-radius: 50%;
  background: rgb(76,175,80);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.sb-text {
  font-size: 12.5px;
  font-weight: 700;
  color: rgb(165,214,167);
}

/* ─── Schedule confirmation — per-day mini timeline card ─── */
.schedule-announce-card {
  margin-top: 8px;
  border-radius: 14px;
  padding: 12px 14px;
  border: 1px solid rgba(34,211,238,0.24);
  background: linear-gradient(160deg, rgba(34,211,238,0.06), rgba(255,255,255,0.015));
  box-shadow: 0 4px 16px rgba(0,0,0,0.12);
}
.sac-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12.5px;
  font-weight: 700;
  color: rgb(165,235,245);
  margin-bottom: 10px;
}
.sac-days { display: flex; flex-direction: column; gap: 6px; }
.sac-day-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.sac-day-label {
  font-size: 11px;
  font-weight: 700;
  color: rgba(255,255,255,0.55);
  width: 52px;
  flex-shrink: 0;
}
.sac-timeline {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
}
.sac-dot {
  width: 18px; height: 18px;
  border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  cursor: default;
}
.sac-empty {
  font-size: 11px;
  color: rgba(255,255,255,0.3);
}

/* ─── Saved exams — visual schedule table ───────────────── */
.exam-table-card {
  margin-top: 8px;
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid rgba(255,179,0,0.26);
  background: linear-gradient(160deg, rgba(255,179,0,0.07), rgba(255,255,255,0.015));
  box-shadow: 0 4px 16px rgba(0,0,0,0.12);
}
.exam-table-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  font-size: 12.5px;
  font-weight: 700;
  color: rgb(255,213,128);
  background: rgba(255,179,0,0.12);
  border-bottom: 1px solid rgba(255,179,0,0.2);
}
.exam-table-rows { display: flex; flex-direction: column; }
.exam-row {
  display: grid;
  grid-template-columns: 1.3fr 1.3fr 1fr;
  gap: 6px;
  align-items: center;
  padding: 9px 14px;
  font-size: 12px;
}
.exam-row:not(.exam-row-head):not(:last-child) { border-bottom: 1px solid rgba(255,255,255,0.05); }
.exam-row:not(.exam-row-head):nth-child(even) { background: rgba(255,255,255,0.022); }
.exam-row-head { padding-bottom: 4px; }
.exam-col-label {
  font-size: 10.5px;
  font-weight: 700;
  letter-spacing: 0.3px;
  color: rgba(255,255,255,0.35);
}
.exam-subject, .exam-date, .exam-time {
  display: flex;
  align-items: center;
  gap: 5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.exam-subject { font-weight: 700; color: rgba(255,255,255,0.9); }
.exam-date, .exam-time { color: rgba(255,255,255,0.6); }

/* ─── Typing dots ───────────────────────────────────────── */
.typing-bubble { display: flex; align-items: center; gap: 6px; padding: 12px 16px; }
.dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: rgba(34,211,238,0.6);
  animation: bounce 1.2s infinite;
}
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }
.typing-label {
  font-size: 11.5px;
  color: rgba(255,255,255,0.4);
  margin-inline-start: 4px;
}
@keyframes bounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-5px); opacity: 1; }
}

.stream-cursor {
  display: inline-block;
  color: rgba(34,211,238,0.75);
  margin-inline-start: 1px;
  animation: cursorBlink 0.9s steps(1) infinite;
}
@keyframes cursorBlink {
  0%, 50% { opacity: 1; }
  50.01%, 100% { opacity: 0; }
}

/* ─── Pinned question — current, prominent & distinct ───── */
.pinned-question {
  display: flex;
  align-items: flex-start;
  gap: 11px;
  margin: 0 12px 10px;
  padding: 12px 14px;
  background: linear-gradient(135deg, rgba(255,179,0,0.1), rgba(255,179,0,0.03));
  border: 1px solid rgba(255,179,0,0.32);
  border-radius: 14px;
  flex-shrink: 0;
  position: relative;
  overflow: hidden;
}
.pinned-question::before {
  content: '';
  position: absolute;
  inset-inline-start: 0;
  top: 0; bottom: 0;
  width: 3px;
  background: rgb(255,179,0);
}
.pinned-question-icon {
  width: 32px; height: 32px;
  border-radius: 10px;
  background: rgba(255,179,0,0.15);
  border: 1px solid rgba(255,179,0,0.3);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.pinned-question-body { display: flex; flex-direction: column; gap: 2px; }
.pinned-question-label {
  font-size: 11px;
  font-weight: 700;
  color: rgb(255,179,0);
}
.pinned-question-text {
  font-size: 13.5px;
  line-height: 1.6;
  font-weight: 500;
  white-space: pre-wrap;
}

/* ─── Schedule progress (preview panel before schedule exists) ── */
.schedule-progress { padding: 8px 6px 14px; }
.progress-intro {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  margin-bottom: 18px;
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(34,211,238,0.08), rgba(124,108,240,0.05));
  border: 1px solid rgba(34,211,238,0.18);
}
.day-progress-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 20px;
}
.day-progress-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 14px;
  border-radius: 12px;
  border: 1.5px solid rgba(255,255,255,0.08);
  background: rgba(255,255,255,0.03);
  transition: all 0.25s ease;
  flex: 1 1 calc(33.33% - 10px);
  min-width: 110px;
}
.dp-icon {
  width: 26px; height: 26px;
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.dp-label { font-size: 12.5px; font-weight: 600; }
.dp-edit-btn {
  margin-inline-start: auto;
  opacity: 0.55;
  transition: opacity 0.2s ease;
}
.dp-edit-btn:hover { opacity: 1; }

.day-progress-item.dp-pending { color: rgba(255,255,255,0.4); }
.day-progress-item.dp-pending .dp-icon { background: rgba(255,255,255,0.05); color: rgba(255,255,255,0.3); }

.day-progress-item.dp-current {
  border-color: rgba(255,179,0,0.4);
  background: rgba(255,179,0,0.07);
  box-shadow: 0 4px 14px rgba(255,179,0,0.15);
  transform: translateY(-1px);
}
.day-progress-item.dp-current .dp-icon { background: rgba(255,179,0,0.18); color: rgb(255,179,0); }
.day-progress-item.dp-current .dp-label { color: rgb(255,213,128); }

.day-progress-item.dp-done {
  border-color: rgba(76,175,80,0.35);
  background: rgba(76,175,80,0.06);
}
.day-progress-item.dp-done .dp-icon { background: rgba(76,175,80,0.18); color: rgb(76,175,80); }
.day-progress-item.dp-done .dp-label { color: rgba(255,255,255,0.85); }

.progress-bar-row { padding: 0 4px; }

/* ─── Pre-build confirmation summary card ──────────────── */
.confirm-summary-card { padding: 6px 4px 4px; }
.cs-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 16px;
  margin-bottom: 16px;
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(76,175,80,0.1), rgba(34,211,238,0.04));
  border: 1px solid rgba(76,175,80,0.22);
}
.cs-header-icon {
  width: 38px; height: 38px;
  border-radius: 11px;
  display: flex; align-items: center; justify-content: center;
  background: rgba(76,175,80,0.16);
  flex-shrink: 0;
}
.cs-info-chips, .cs-activities {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
}
.cs-edit-settings-btn { margin-bottom: 4px; }
.cs-days-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 700;
  color: rgba(255,255,255,0.75);
  margin-bottom: 12px;
}
.cs-days {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 360px;
  overflow-y: auto;
  padding-inline-end: 4px;
}
.cs-day-item {
  padding: 10px 14px;
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.08);
  background: rgba(255,255,255,0.025);
}
.cs-day-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}
.cs-day-label { font-size: 13px; font-weight: 700; }
.cs-day-slots {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 6px;
}
.cs-slot-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 9px;
  border-radius: 999px;
  background: rgba(255,255,255,0.045);
  border: 1px solid rgba(255,255,255,0.08);
  font-size: 11px;
  white-space: nowrap;
}
.cs-slot-time { font-weight: 700; color: rgba(255,255,255,0.85); }
.cs-slot-ctx { color: rgba(255,255,255,0.5); }
.cs-day-text {
  font-size: 12.5px;
  color: rgba(255,255,255,0.65);
  line-height: 1.6;
  margin: 0;
  white-space: pre-wrap;
}
.cs-day-edit { font-size: 12.5px; }
.cs-confirm-btn { font-weight: 700; letter-spacing: 0.2px; }

/* ─── Chat actions row ──────────────────────────────────── */
.chat-actions {
  display: flex;
  gap: 8px;
  padding: 6px 12px 4px;
  flex-wrap: wrap;
  flex-shrink: 0;
}

/* ─── Chat input ────────────────────────────────────────── */
.chat-input-row {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  padding: 8px 12px 12px;
  border-top: 1px solid rgba(255,255,255,0.06);
  flex-shrink: 0;
}
.chat-input { flex: 1; }
.send-btn { flex-shrink: 0; }

/* ─── Exam form ─────────────────────────────────────────── */
.exam-form {
  background: rgba(255,200,0,0.05);
  border: 1px solid rgba(255,200,0,0.2);
  flex-shrink: 0;
}

/* ─── Exam confirmation row ─────────────────────────────── */
.exam-row {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
}

/* ═══════════════════════════════════════════════════════════
   ONBOARDING — redesign
═══════════════════════════════════════════════════════════ */
.onboarding-wrap { max-width: 760px; margin-inline: auto; }

.onboarding-hero {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px 20px;
  border-radius: 18px;
  background: linear-gradient(135deg, rgba(124,108,240,0.14), rgba(34,211,238,0.08));
  border: 1px solid rgba(124,108,240,0.2);
}
.hero-icon {
  width: 48px; height: 48px;
  border-radius: 14px;
  background: rgba(34,211,238,0.12);
  border: 1px solid rgba(34,211,238,0.3);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}

/* Section card */
.onb-section {
  background: rgba(255,255,255,0.035);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 16px;
  padding: 20px;
  transition: border-color 0.2s ease;
}
.onb-section:hover { border-color: rgba(255,255,255,0.12); }

.onb-section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}
.onb-icon {
  width: 40px; height: 40px;
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.onb-icon-primary  { background: rgba(124,108,240,0.15); color: rgb(124,108,240); border: 1px solid rgba(124,108,240,0.3); }
.onb-icon-info     { background: rgba(34,211,238,0.13);  color: rgb(34,211,238);  border: 1px solid rgba(34,211,238,0.3); }
.onb-icon-warning  { background: rgba(255,183,77,0.14);  color: rgb(255,183,77);  border: 1px solid rgba(255,183,77,0.3); }
.onb-icon-success  { background: rgba(76,175,80,0.14);   color: rgb(76,175,80);   border: 1px solid rgba(76,175,80,0.3); }
.onb-icon-secondary{ background: rgba(236,72,153,0.13);  color: rgb(236,72,153);  border: 1px solid rgba(236,72,153,0.28); }

/* Grade chips */
.grade-chips { gap: 8px; row-gap: 8px; flex-wrap: wrap; }
.grade-chip {
  background: rgba(255,255,255,0.05) !important;
  border: 1.5px solid rgba(255,255,255,0.12) !important;
  font-weight: 500;
  transition: all 0.18s ease;
}
:deep(.grade-chip-active) {
  background: linear-gradient(135deg, rgba(124,108,240,0.9), rgba(34,211,238,0.75)) !important;
  border-color: transparent !important;
  color: #fff !important;
  font-weight: 700;
  box-shadow: 0 4px 14px rgba(124,108,240,0.35);
  transform: translateY(-1px);
}

/* School time pair */
.time-pair {
  display: flex;
  align-items: center;
  gap: 10px;
}
.time-field { flex: 1; }
.time-divider {
  flex-shrink: 0;
  width: 34px; height: 34px;
  border-radius: 50%;
  background: rgba(34,211,238,0.08);
  border: 1px solid rgba(34,211,238,0.25);
  display: flex; align-items: center; justify-content: center;
  margin-top: -22px;
}

/* Sleep / wake fields */
.sleep-field-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 6px 6px 4px;
  border-radius: 12px;
  border: 1px solid transparent;
}
.sleep-field-icon {
  width: 38px; height: 38px;
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.sleep-icon-wake  { background: rgba(255,193,7,0.13);  border: 1px solid rgba(255,193,7,0.28); }
.sleep-icon-sleep { background: rgba(99,102,241,0.15); border: 1px solid rgba(99,102,241,0.3); }
.sleep-field-select { flex: 1; }

/* School day chips — circular badges */
.day-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.day-chip {
  min-width: 64px;
  padding: 9px 16px;
  border-radius: 12px;
  background: rgba(255,255,255,0.04);
  border: 1.5px solid rgba(255,255,255,0.1);
  color: rgba(255,255,255,0.75);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.18s ease;
}
.day-chip:hover { border-color: rgba(76,175,80,0.4); color: #fff; }
.day-chip-active {
  background: linear-gradient(135deg, rgba(76,175,80,0.85), rgba(34,211,238,0.6));
  border-color: transparent;
  color: #fff;
  font-weight: 700;
  box-shadow: 0 4px 14px rgba(76,175,80,0.3);
  transform: translateY(-1px);
}

/* Activity chips */
.activity-chips { gap: 8px; row-gap: 8px; flex-wrap: wrap; }
.activity-chip {
  background: rgba(255,255,255,0.05) !important;
  border: 1.5px solid rgba(255,255,255,0.12) !important;
  font-weight: 500;
}
:deep(.activity-chip-active) {
  background: linear-gradient(135deg, rgba(236,72,153,0.85), rgba(124,108,240,0.7)) !important;
  border-color: transparent !important;
  color: #fff !important;
  font-weight: 700;
  box-shadow: 0 4px 14px rgba(236,72,153,0.3);
  transform: translateY(-1px);
}
.mini-chip {
  background: rgba(255,255,255,0.05) !important;
  border: 1px solid rgba(255,255,255,0.1) !important;
}

/* Next button */
.onb-next-wrap {
  display: flex;
  justify-content: center;
  margin-top: 28px;
  margin-bottom: 12px;
}
.onb-next-btn {
  background: linear-gradient(135deg, rgb(124,108,240), rgb(34,211,238)) !important;
  color: #fff !important;
  font-weight: 700;
  font-size: 15px;
  border-radius: 16px !important;
  padding: 0 38px !important;
  height: 56px !important;
  box-shadow: 0 8px 28px rgba(124,108,240,0.35);
  transition: transform 0.18s ease, box-shadow 0.18s ease;
  text-transform: none;
  letter-spacing: 0;
}
.onb-next-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 34px rgba(124,108,240,0.45);
}
.onb-next-btn:disabled {
  background: rgba(255,255,255,0.08) !important;
  color: rgba(255,255,255,0.35) !important;
  box-shadow: none;
}

/* ─── Onboarding activity (chat-step legacy panel reuse) ── */
.activity-detail {
  background: rgba(124,108,240,0.07);
  border: 1px solid rgba(124,108,240,0.18);
  border-radius: 14px;
  padding: 16px;
}

/* ─── Review suggestions ────────────────────────────────── */
.suggestion-card {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.1);
  transition: all 0.2s ease;
}
.suggestion-accepted { border-color: rgba(76,175,80,0.5) !important; background: rgba(76,175,80,0.07) !important; }
.suggestion-rejected { border-color: rgba(244,67,54,0.3) !important; background: rgba(244,67,54,0.04) !important; opacity: 0.65; }
</style>
