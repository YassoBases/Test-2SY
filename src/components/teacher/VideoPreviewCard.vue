<template>
  <v-card class="media-preview-panel pa-4" variant="flat">
    <div class="media-preview-panel__head">
      <div class="media-preview-panel__icon-wrap">
        <img v-if="thumbnail" :src="thumbnail" alt="" class="media-preview-panel__thumb" />
        <div v-else-if="previewUrl" class="media-preview-panel__thumb media-preview-panel__thumb--video">
          <video :src="previewUrl" muted playsinline preload="metadata" class="media-preview-panel__thumb-video" />
        </div>
        <div v-else class="media-preview-panel__thumb media-preview-panel__thumb--placeholder">
          <v-icon color="secondary" size="28">mdi-video</v-icon>
        </div>
      </div>

      <div class="media-preview-panel__meta min-width-0">
        <p class="media-preview-panel__name">{{ file?.name || '—' }}</p>
        <div class="media-preview-panel__stats">
          <span v-if="durationLabel" class="media-preview-panel__stat" dir="ltr">
            <v-icon size="14">mdi-clock-outline</v-icon>
            {{ durationLabel }}
          </span>
          <span v-if="file" class="media-preview-panel__stat" dir="ltr">
            <v-icon size="14">mdi-harddisk</v-icon>
            {{ formatFileSize(file.size) }}
          </span>
        </div>
      </div>

      <v-btn
        v-if="file"
        size="small"
        variant="text"
        color="error"
        rounded="lg"
        class="flex-shrink-0"
        @click="$emit('remove')"
      >
        {{ $t('common.delete') }}
      </v-btn>
    </div>
  </v-card>
</template>

<script setup>
import { onUnmounted, ref, watch, computed } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import { formatFileSize } from '../../utils/format.js'
import { extractVideoFileMetadata } from '../../utils/videoFileMetadata.js'
import { formatMediaDuration } from '../../utils/videoEmbed.js'

const props = defineProps({
  file: { type: Object, default: null },
})

defineEmits(['remove'])

const previewUrl = ref('')
const duration = ref(0)
const thumbnail = ref(null)

const durationLabel = computed(() => formatMediaDuration(duration.value))

watch(
  () => props.file,
  async (file) => {
    if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
    previewUrl.value = ''
    duration.value = 0
    thumbnail.value = null

    if (!file) return

    previewUrl.value = URL.createObjectURL(file)
    const meta = await extractVideoFileMetadata(file)
    duration.value = meta.duration
    thumbnail.value = meta.thumbnail
  },
  { immediate: true },
)

onUnmounted(() => {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
})
</script>

<style scoped>
.media-preview-panel {
  background: var(--em-card-l1, rgb(var(--v-theme-surface))) !important;
  border: 1px solid var(--em-border-subtle, rgba(var(--v-border-color), 0.14));
  border-radius: var(--em-radius-lg, 12px);
}

.media-preview-panel__head {
  display: flex;
  align-items: center;
  gap: 14px;
}

.media-preview-panel__icon-wrap {
  flex-shrink: 0;
}

.media-preview-panel__thumb {
  display: block;
  width: 112px;
  height: 64px;
  object-fit: cover;
  border-radius: 10px;
  background: #0f172a;
  overflow: hidden;
}

.media-preview-panel__thumb--video {
  position: relative;
}

.media-preview-panel__thumb-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.media-preview-panel__thumb--placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(var(--v-theme-on-surface), 0.06);
}

.media-preview-panel__name {
  margin: 0 0 6px;
  font-size: 0.9375rem;
  font-weight: 700;
  line-height: 1.35;
  color: var(--em-text, rgb(var(--v-theme-on-surface)));
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.media-preview-panel__stats {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.media-preview-panel__stat {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--em-text-muted, rgba(var(--v-theme-on-surface), 0.62));
  font-variant-numeric: tabular-nums;
}

.min-width-0 {
  min-width: 0;
}
</style>
