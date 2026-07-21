<template>
  <div class="teacher-msg" :class="{ 'teacher-msg--compact': compact }">
    <div class="teacher-msg__meta">
      <EmptyTeacherPlaceholder :voice-state="voiceState" size="sm" />
      <span class="teacher-msg__who">{{ name }}</span>
    </div>
    <div class="teacher-msg__bubble">
      <slot />
    </div>
  </div>
</template>

<script setup>
import EmptyTeacherPlaceholder from '../../ai-session/EmptyTeacherPlaceholder.vue'

defineProps({
  name: { type: String, default: 'Alex' },
  voiceState: { type: String, default: 'idle' },
  compact: { type: Boolean, default: false },
})
</script>

<style scoped>
.teacher-msg {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.teacher-msg__meta {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.teacher-msg__who {
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--color-primary-deep, #4f46e5);
}

.teacher-msg__bubble {
  padding: 16px 18px;
  border-radius: 18px 18px 18px 6px;
  background: color-mix(in srgb, var(--color-primary, #6366f1) 12%, #fff);
  font-size: 1.1rem;
  line-height: 1.55;
  max-width: 40rem;
}

.teacher-msg--compact .teacher-msg__bubble {
  font-size: 1rem;
  padding: 12px 14px;
}
</style>
