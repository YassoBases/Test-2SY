<template>
  <div class="teacher-voice-player tds-scope">
    <div class="teacher-voice-player__shell">
      <div class="teacher-voice-player__icon" aria-hidden="true">
        <v-icon icon="mdi-waveform" size="22" />
      </div>
      <audio
        :src="src"
        controls
        controlslist="nodownload"
        class="teacher-voice-player__audio"
        :class="{ 'teacher-voice-player__audio--loading': loading }"
      />
    </div>
    <p v-if="caption" class="teacher-voice-player__caption">{{ caption }}</p>
  </div>
</template>

<script setup>
defineProps({
  src: { type: String, required: true },
  caption: { type: String, default: '' },
  loading: { type: Boolean, default: false },
})
</script>

<style scoped>
.teacher-voice-player__shell {
  display: flex;
  align-items: center;
  gap: var(--em-space-md);
  padding: var(--em-space-md) var(--em-space-lg);
  border-radius: var(--em-radius-lg, 16px);
  border: 1px solid var(--em-border-subtle);
  background: var(--em-surface-control, rgba(var(--v-theme-on-surface), 0.04));
}

.teacher-voice-player__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  flex-shrink: 0;
  border-radius: 50%;
  background: color-mix(in srgb, var(--em-primary) 14%, transparent);
  color: var(--em-primary-deep, var(--em-primary));
}

.teacher-voice-player__audio {
  flex: 1;
  min-width: 0;
  height: 40px;
  border-radius: 999px;
}

.teacher-voice-player__audio--loading {
  opacity: 0.55;
}

.teacher-voice-player__caption {
  margin: var(--em-space-sm) 0 0;
  font-size: 0.75rem;
  color: var(--em-text-muted);
  text-align: center;
}
</style>
