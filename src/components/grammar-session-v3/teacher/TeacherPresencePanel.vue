<template>
  <aside class="teacher-panel" :aria-label="t('student.grammarTeacher.panel.aria')">
    <div class="teacher-panel__avatar">
      <EmptyTeacherPlaceholder :voice-state="voiceForPlaceholder" size="lg" :show-mic="showMic" />
      <span class="teacher-panel__status" :class="`teacher-panel__status--${presenceState}`">
        {{ statusLabel }}
      </span>
    </div>

    <div class="teacher-panel__body">
      <div class="teacher-panel__identity">
        <h2 class="teacher-panel__name">{{ teacherName }}</h2>
        <p class="teacher-panel__role">{{ t('student.grammarTeacher.panel.role') }}</p>
      </div>

      <p v-if="teacherFocus" class="teacher-panel__focus">
        <span class="teacher-panel__focus-label">{{ t('student.grammarTeacher.panel.focus') }}</span>
        <span class="eng-island" dir="ltr">{{ teacherFocus }}</span>
      </p>

      <p class="teacher-panel__mood">{{ moodLabel }}</p>

      <div class="teacher-panel__bubble" role="status">
        <p>{{ teacherMessage || t('student.grammarTeacher.panel.idle') }}</p>
      </div>

      <div class="teacher-panel__voice-ready" aria-hidden="true">
        <span class="voice-chip">{{ t('student.grammarTeacher.voice.speaking') }}</span>
        <span class="voice-chip">{{ t('student.grammarTeacher.voice.listening') }}</span>
        <span class="voice-chip">{{ t('student.grammarTeacher.voice.thinking') }}</span>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import EmptyTeacherPlaceholder from '../../ai-session/EmptyTeacherPlaceholder.vue'

const props = defineProps({
  teacherName: { type: String, default: 'Alex' },
  teacherFocus: { type: String, default: '' },
  teacherMood: { type: String, default: 'encouraging' },
  teacherMessage: { type: String, default: '' },
  presenceState: { type: String, default: 'idle' },
})

const { t } = useI18n()

const voiceForPlaceholder = computed(() => {
  if (props.presenceState === 'speaking') return 'teacher_speaking'
  if (props.presenceState === 'listening') return 'listening'
  return 'idle'
})

const showMic = computed(() => props.presenceState === 'listening')

const statusLabel = computed(() => {
  if (props.presenceState === 'thinking') return t('student.grammarTeacher.presence.thinking')
  if (props.presenceState === 'speaking') return t('student.grammarTeacher.presence.speaking')
  if (props.presenceState === 'listening') return t('student.grammarTeacher.presence.listening')
  return t('student.grammarTeacher.presence.withYou')
})

const moodLabel = computed(() =>
  t(`student.grammarTeacher.mood.${props.teacherMood}`, props.teacherMood),
)
</script>

<style scoped>
.teacher-panel {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 16px;
  padding: 16px 18px;
  border-radius: 20px;
  background:
    color-mix(in srgb, var(--color-primary, #6366f1) 8%, var(--surface-elevated, #fff));
  border: 1px solid color-mix(in srgb, var(--color-primary, #6366f1) 16%, transparent);
}

.teacher-panel__avatar {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.teacher-panel__status {
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--color-primary-deep, #4f46e5);
}

.teacher-panel__name {
  margin: 0;
  font-size: 1.15rem;
  font-family: var(--font-display, Tajawal, sans-serif);
}

.teacher-panel__role {
  margin: 2px 0 0;
  font-size: 0.8rem;
  color: var(--text-muted, #3f4f63);
}

.teacher-panel__focus {
  margin: 10px 0 0;
  font-size: 0.85rem;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.teacher-panel__focus-label {
  font-weight: 700;
  color: var(--text-muted, #3f4f63);
}

.teacher-panel__mood {
  margin: 6px 0 0;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--color-primary-deep, #4f46e5);
}

.teacher-panel__bubble {
  margin-block-start: 12px;
  padding: 14px 16px;
  border-radius: 16px 16px 16px 6px;
  background: var(--surface-elevated, #fff);
  box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--color-primary, #6366f1) 12%, transparent);
}

.teacher-panel__bubble p {
  margin: 0;
  font-size: 1.05rem;
  line-height: 1.55;
}

.teacher-panel__voice-ready {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-block-start: 10px;
  opacity: 0.55;
}

.voice-chip {
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  padding: 3px 8px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--text-muted, #3f4f63) 12%, transparent);
}

.eng-island {
  unicode-bidi: isolate;
}

@media (max-width: 640px) {
  .teacher-panel {
    grid-template-columns: 1fr;
  }

  .teacher-panel__avatar {
    flex-direction: row;
    justify-content: flex-start;
  }
}
</style>
