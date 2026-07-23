<template>
  <div
    class="teacher-placeholder"
    :class="[`teacher-placeholder--${size}`, `teacher-placeholder--${voiceState}`]"
    role="img"
    :aria-label="t('student.grammarSession.teacher.aria')"
  >
    <v-icon :icon="icon" :size="iconSize" aria-hidden="true" />
    <span v-if="showMic" class="teacher-placeholder__mic" aria-hidden="true">
      <v-icon icon="mdi-microphone" size="12" />
    </span>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  voiceState: { type: String, default: 'idle' },
  size: { type: String, default: 'md' },
  showMic: { type: Boolean, default: false },
})

const { t } = useI18n()

const iconSize = computed(() => (props.size === 'lg' ? 36 : props.size === 'sm' ? 20 : 28))

const icon = computed(() => {
  if (props.voiceState === 'listening' || props.voiceState === 'student_speaking') {
    return 'mdi-ear-hearing'
  }
  if (props.voiceState === 'teacher_speaking') return 'mdi-account-voice'
  return 'mdi-robot-happy-outline'
})
</script>

<style scoped>
.teacher-placeholder {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  color: var(--color-primary-deep, #4f46e5);
  background:
    radial-gradient(circle at 30% 20%, rgba(99, 102, 241, 0.22), transparent 55%),
    color-mix(in srgb, var(--color-primary, #6366f1) 14%, #fff);
}

.teacher-placeholder--sm {
  width: 40px;
  height: 40px;
}

.teacher-placeholder--md {
  width: 56px;
  height: 56px;
}

.teacher-placeholder--lg {
  width: 72px;
  height: 72px;
}

.teacher-placeholder--teacher_speaking {
  animation: teacher-pulse 1.4s ease-in-out infinite;
}

.teacher-placeholder--listening,
.teacher-placeholder--student_speaking {
  outline: 2px solid color-mix(in srgb, var(--color-primary, #6366f1) 45%, transparent);
}

.teacher-placeholder__mic {
  position: absolute;
  inset-inline-end: -2px;
  bottom: -2px;
  width: 20px;
  height: 20px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--surface-elevated, #fff);
  color: var(--color-primary, #6366f1);
}

@keyframes teacher-pulse {
  0%,
  100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.04);
  }
}

@media (prefers-reduced-motion: reduce) {
  .teacher-placeholder--teacher_speaking {
    animation: none;
  }
}
</style>
