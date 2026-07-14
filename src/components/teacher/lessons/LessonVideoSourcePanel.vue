<template>
  <div class="lesson-video-source">
    <v-tabs v-model="tab" class="lesson-video-source__tabs" density="comfortable" grow>
      <v-tab value="upload">{{ $t('teacher.actions.uploadVideo') }}</v-tab>
      <v-tab value="link">{{ $t('teacher.labels.videoLink') }}</v-tab>
    </v-tabs>

    <v-window v-model="tab" class="lesson-video-source__window">
      <v-window-item value="upload">
        <div
          class="lesson-video-source__dropzone"
          :class="{ 'lesson-video-source__dropzone--active': dragOver, 'lesson-video-source__dropzone--filled': !!videoFile }"
          role="button"
          tabindex="0"
          @click="triggerPick"
          @keydown.enter.space.prevent="triggerPick"
          @dragenter.prevent="dragOver = true"
          @dragover.prevent="dragOver = true"
          @dragleave.prevent="dragOver = false"
          @drop.prevent="onDrop"
        >
          <template v-if="!videoFile">
            <v-icon size="40" class="lesson-video-source__dropzone-icon">mdi-cloud-upload-outline</v-icon>
            <p class="lesson-video-source__dropzone-title">{{ $t('teacher.lessons.dragVideoDrop') }}</p>
            <p class="lesson-video-source__dropzone-hint">{{ $t('teacher.actions.browse') }}</p>
            <p class="lesson-video-source__dropzone-formats">MP4 · MOV · WebM</p>
          </template>
          <template v-else>
            <v-icon size="36" class="lesson-video-source__dropzone-icon">mdi-check-circle-outline</v-icon>
            <p class="lesson-video-source__dropzone-title">{{ videoFile.name }}</p>
            <p class="lesson-video-source__dropzone-hint">{{ formatFileSize(videoFile.size) }}</p>
            <div class="lesson-video-source__dropzone-actions">
              <v-btn size="small" variant="tonal" rounded="lg" @click.stop="triggerPick">{{ $t('common.update') }}</v-btn>
              <v-btn size="small" variant="text" color="error" rounded="lg" @click.stop="$emit('clear-video')">
                {{ $t('common.delete') }}
              </v-btn>
            </div>
          </template>
        </div>

        <VideoPreviewCard
          v-if="videoFile"
          :file="videoFile"
          class="lesson-video-source__preview"
          @remove="$emit('clear-video')"
        />

        <v-progress-linear
          v-if="uploadProgress > 0 && uploadProgress < 100"
          :model-value="uploadProgress"
          color="primary"
          height="6"
          rounded
          class="lesson-video-source__progress"
        />
      </v-window-item>

      <v-window-item value="link">
        <p class="lesson-video-source__link-intro">
          {{ $t('teacher.lessons.pasteVideoLink') }}
        </p>
        <v-text-field
          :model-value="videoUrl"
          :label="$t('teacher.labels.videoLink')"
          placeholder="https://..."
          variant="outlined"
          density="comfortable"
          prepend-inner-icon="mdi-link-variant"
          hide-details="auto"
          class="add-lesson-field"
          @update:model-value="$emit('update:videoUrl', $event)"
        />
        <v-alert
          v-if="videoUrl && !videoFile"
          type="info"
          variant="tonal"
          density="comfortable"
          class="lesson-video-source__link-note rounded-lg"
        >
          {{ $t('teacher.lessons.linkFullProcessing') }}
        </v-alert>
      </v-window-item>
    </v-window>

    <input
      ref="fileInput"
      type="file"
      accept="video/*"
      class="d-none"
      @change="onPick"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import VideoPreviewCard from '../VideoPreviewCard.vue'
import { formatFileSize } from '../../../utils/format.js'

defineProps({
  videoFile: { type: Object, default: null },
  videoUrl: { type: String, default: '' },
  uploadProgress: { type: Number, default: 0 },
})

const emit = defineEmits(['update:videoFile', 'update:videoUrl', 'clear-video'])

const tab = ref('upload')
const dragOver = ref(false)
const fileInput = ref(null)

function triggerPick() {
  fileInput.value?.click()
}

function applyFile(file) {
  if (!file || !String(file.type || '').startsWith('video/')) return
  emit('update:videoFile', file)
}

function onPick(e) {
  applyFile(e.target.files?.[0])
  e.target.value = ''
}

function onDrop(e) {
  dragOver.value = false
  applyFile(e.dataTransfer?.files?.[0])
}
</script>
