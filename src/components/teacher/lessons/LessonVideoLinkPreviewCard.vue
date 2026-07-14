<template>
  <div class="lesson-link-preview" :class="{ 'lesson-link-preview--loading': loading }">
    <div v-if="loading" class="lesson-link-preview__loading">
      <v-progress-circular indeterminate size="28" width="3" color="primary" />
      <span>{{ $t('teacher.status.recognizingLink') }}</span>
    </div>

    <template v-else-if="preview">
      <div class="lesson-link-preview__success">
        <v-icon size="18" class="lesson-link-preview__success-icon">mdi-check-circle</v-icon>
        <span>{{ $t('teacher.status.videoRecognized') }}</span>
      </div>

      <div class="lesson-link-preview__body">
        <div class="lesson-link-preview__thumb-wrap">
          <img
            v-if="preview.thumbnail"
            :src="preview.thumbnail"
            alt=""
            class="lesson-link-preview__thumb"
          />
          <div v-else class="lesson-link-preview__thumb lesson-link-preview__thumb--placeholder">
            <v-icon :icon="platform.icon" size="36" />
          </div>
        </div>

        <div class="lesson-link-preview__meta min-width-0">
          <p class="lesson-link-preview__title">{{ preview.title || t('teacher.lessons.videoNoTitle') }}</p>
          <p v-if="durationLabel" class="lesson-link-preview__duration" dir="ltr">{{ durationLabel }}</p>
          <div class="lesson-link-preview__platform">
            <v-icon :icon="platform.icon" size="18" class="lesson-link-preview__platform-icon" />
            <span>{{ platform.label }}</span>
          </div>
        </div>
      </div>
    </template>

    <div v-else-if="error" class="lesson-link-preview__error">
      <v-icon size="18" color="error">mdi-alert-circle-outline</v-icon>
      <span>{{ error }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import { detectVideoPlatform, formatMediaDuration } from '../../../utils/videoEmbed.js'

const props = defineProps({
  preview: { type: Object, default: null },
  url: { type: String, default: '' },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
})

const platform = computed(() => detectVideoPlatform(props.url || props.preview?.url))
const durationLabel = computed(() => formatMediaDuration(props.preview?.duration))
</script>

<style scoped>
.lesson-link-preview {
  margin-top: 14px;
  padding: 16px;
  border-radius: var(--em-radius-lg, 14px);
  border: 1px solid var(--em-border-subtle);
  background: var(--em-card-l1, var(--em-surface-raised));
}

.lesson-link-preview--loading {
  min-height: 88px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.lesson-link-preview__loading {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.8125rem;
  color: var(--em-text-muted);
}

.lesson-link-preview__success {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 12px;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--em-success, #16a34a);
}

.lesson-link-preview__success-icon {
  color: var(--em-success, #16a34a);
}

.lesson-link-preview__body {
  display: flex;
  gap: 14px;
  align-items: flex-start;
}

.lesson-link-preview__thumb-wrap {
  flex-shrink: 0;
  width: 128px;
}

.lesson-link-preview__thumb {
  display: block;
  width: 128px;
  height: 72px;
  object-fit: cover;
  border-radius: 10px;
  background: rgba(var(--v-theme-on-surface), 0.06);
}

.lesson-link-preview__thumb--placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--em-text-muted);
}

.lesson-link-preview__title {
  margin: 0 0 6px;
  font-size: 0.9375rem;
  font-weight: 700;
  line-height: 1.35;
  color: var(--em-text);
}

.lesson-link-preview__duration {
  margin: 0 0 8px;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--em-text-muted);
  font-variant-numeric: tabular-nums;
}

.lesson-link-preview__platform {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--em-text-muted);
  background: var(--em-surface-control, rgba(var(--v-theme-on-surface), 0.04));
  border: 1px solid var(--em-border-subtle);
}

.lesson-link-preview__platform-icon {
  color: var(--em-primary, #6366f1);
}

.lesson-link-preview__error {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.8125rem;
  color: rgb(var(--v-theme-error));
}

.min-width-0 {
  min-width: 0;
}
</style>
