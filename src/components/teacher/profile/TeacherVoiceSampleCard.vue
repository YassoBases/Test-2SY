<template>
  <div class="teacher-voice-sample-row tds-scope" :class="{ 'teacher-voice-sample-row--default': isDefault }">
    <div class="teacher-voice-sample-row__main">
      <div class="teacher-voice-sample-row__info">
        <span class="teacher-voice-sample-row__name">{{ displayName }}</span>
        <span class="teacher-voice-sample-row__meta">{{ metaLine }}</span>
      </div>

      <div class="teacher-voice-sample-row__badges">
        <span class="teacher-voice-sample-row__badge" :class="statusBadgeClass">{{ statusLabel }}</span>
        <span v-if="isDefault" class="teacher-voice-sample-row__badge teacher-voice-sample-row__badge--default">
          {{ $t('teacher.status.default') }}
        </span>
      </div>

      <div class="teacher-voice-sample-row__actions">
        <v-btn
          icon
          size="small"
          variant="text"
          :loading="previewLoading"
          :disabled="!canListen"
          :aria-label="$t('teacher.actions.listen')"
          @click="$emit('listen')"
        >
          <v-icon icon="mdi-play-circle-outline" size="20" />
        </v-btn>
        <v-btn
          icon
          size="small"
          variant="text"
          :aria-label="$t('common.update')"
          @click="$emit('replace')"
        >
          <v-icon icon="mdi-swap-horizontal" size="20" />
        </v-btn>
        <v-btn
          icon
          size="small"
          variant="text"
          :loading="deleting"
          :aria-label="$t('common.delete')"
          @click="$emit('delete')"
        >
          <v-icon icon="mdi-delete-outline" size="20" />
        </v-btn>
      </div>
    </div>

    <div v-if="previewUrl" class="teacher-voice-sample-row__preview">
      <TeacherVoiceMediaPlayer :src="previewUrl" :loading="previewLoading" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import TeacherVoiceMediaPlayer from './TeacherVoiceMediaPlayer.vue'

const props = defineProps({
  displayName: { type: String, required: true },
  durationSeconds: { type: Number, default: null },
  uploadedAt: { type: String, default: '' },
  statusLabel: { type: String, default: '' },
  isDefault: { type: Boolean, default: false },
  previewUrl: { type: String, default: '' },
  previewLoading: { type: Boolean, default: false },
  deleting: { type: Boolean, default: false },
  canListen: { type: Boolean, default: true },
})

defineEmits(['listen', 'replace', 'delete'])

const durationText = computed(() => {
  if (props.durationSeconds == null || props.durationSeconds <= 0) return ''
  return `${Math.round(props.durationSeconds)}${t('teacher.voice.secondsShort')}`
})

const metaLine = computed(() => {
  const parts = []
  if (durationText.value) parts.push(durationText.value)
  if (props.uploadedAt) parts.push(props.uploadedAt)
  return parts.join(' · ')
})

const statusBadgeClass = computed(() => {
  if (props.statusLabel === t('teacher.status.readyF')) return 'teacher-voice-sample-row__badge--ready'
  if (props.statusLabel === t('teacher.status.preparing')) return 'teacher-voice-sample-row__badge--processing'
  if (props.statusLabel === t('teacher.status.notAvailable')) return 'teacher-voice-sample-row__badge--failed'
  return ''
})
</script>

<style scoped>
.teacher-voice-sample-row {
  border: 1px solid var(--em-border-subtle);
  border-radius: var(--em-radius-sm, 8px);
  background: var(--em-surface-control, rgba(var(--v-theme-on-surface), 0.02));
  overflow: hidden;
}

.teacher-voice-sample-row--default {
  border-color: color-mix(in srgb, var(--em-primary) 22%, var(--em-border-subtle));
}

.teacher-voice-sample-row__main {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto auto;
  align-items: center;
  gap: var(--em-space-sm) var(--em-space-md);
  min-height: 56px;
  padding: 6px 8px 6px 10px;
}

@media (min-width: 640px) {
  .teacher-voice-sample-row__main {
    min-height: 60px;
    padding: 8px 10px 8px 12px;
  }
}

.teacher-voice-sample-row__info {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.teacher-voice-sample-row__name {
  font-size: 0.8125rem;
  font-weight: 700;
  line-height: 1.3;
  color: var(--em-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.teacher-voice-sample-row__meta {
  font-size: 0.75rem;
  line-height: 1.3;
  color: var(--em-text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.teacher-voice-sample-row__badges {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.teacher-voice-sample-row__badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 0.6875rem;
  font-weight: 600;
  line-height: 1.4;
  border: 1px solid var(--em-border-subtle);
  color: var(--em-text-muted);
  background: transparent;
  white-space: nowrap;
}

.teacher-voice-sample-row__badge--ready {
  color: var(--em-success, #22c55e);
  border-color: color-mix(in srgb, var(--em-success, #22c55e) 35%, var(--em-border-subtle));
  background: color-mix(in srgb, var(--em-success, #22c55e) 8%, transparent);
}

.teacher-voice-sample-row__badge--processing {
  color: var(--em-primary-deep, var(--em-primary));
  border-color: color-mix(in srgb, var(--em-primary) 30%, var(--em-border-subtle));
}

.teacher-voice-sample-row__badge--failed {
  color: var(--em-warning, #f59e0b);
  border-color: color-mix(in srgb, var(--em-warning, #f59e0b) 30%, var(--em-border-subtle));
}

.teacher-voice-sample-row__badge--default {
  color: var(--em-primary-deep, var(--em-primary));
  border-color: color-mix(in srgb, var(--em-primary) 28%, var(--em-border-subtle));
  background: color-mix(in srgb, var(--em-primary) 8%, transparent);
}

.teacher-voice-sample-row__actions {
  display: flex;
  align-items: center;
  gap: 0;
  flex-shrink: 0;
}

.teacher-voice-sample-row__actions :deep(.v-btn) {
  width: 32px;
  height: 32px;
}

.teacher-voice-sample-row__preview {
  padding: 0 10px 8px;
  border-top: 1px solid var(--em-border-subtle);
}

.teacher-voice-sample-row__preview :deep(.teacher-voice-player__shell) {
  padding: var(--em-space-sm);
  gap: var(--em-space-sm);
}

.teacher-voice-sample-row__preview :deep(.teacher-voice-player__icon) {
  width: 32px;
  height: 32px;
}

.teacher-voice-sample-row__preview :deep(.teacher-voice-player__audio) {
  height: 32px;
}

.teacher-voice-sample-row__preview :deep(.teacher-voice-player__caption) {
  display: none;
}
</style>
