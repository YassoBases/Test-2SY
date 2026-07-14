<template>
  <v-card class="media-preview-panel pa-4" variant="flat">
    <div class="d-flex align-center justify-space-between mb-3 flex-wrap gap-2">
      <div class="d-flex align-center gap-2 min-width-0">
        <v-icon color="primary">mdi-file-pdf-box</v-icon>
        <div class="min-width-0">
          <p class="text-subtitle-2 font-weight-bold mb-0">{{ $t('teacher.actions.openPdfPreview') }}</p>
          <p class="text-caption text-medium-emphasis text-truncate mb-0">{{ previewLabel }}</p>
        </div>
      </div>
      <div class="d-flex align-center gap-2 flex-shrink-0">
        <v-chip v-if="file && !error" color="success" size="small" variant="tonal" prepend-icon="mdi-check">
          {{ $t('teacher.status.ready') }}
        </v-chip>
        <v-btn
          v-if="file"
          size="small"
          variant="text"
          color="error"
          rounded="lg"
          @click="$emit('remove')"
        >
          {{ $t('common.delete') }}
        </v-btn>
      </div>
    </div>

    <div
      class="pdf-preview-frame rounded-lg"
      :class="{ 'pdf-preview-frame--error': error, 'pdf-preview-frame--empty': !file }"
    >
      <template v-if="error">
        <v-icon size="48" color="error" class="mb-2">mdi-file-alert</v-icon>
        <p class="text-body-2 text-error mb-0">{{ error }}</p>
      </template>
      <template v-else-if="file">
        <div v-if="rendering" class="text-center pa-6">
          <v-progress-circular indeterminate color="primary" size="32" />
          <p class="text-caption text-medium-emphasis mt-3 mb-0">{{ $t('teacher.status.loadingPreview') }}</p>
        </div>
        <canvas v-show="!rendering" ref="canvasRef" class="pdf-canvas" />
        <div v-if="!rendering && pageCount > 1" class="d-flex justify-center align-center gap-2 mt-3">
          <v-btn icon size="small" variant="tonal" :disabled="currentPage <= 1" @click="changePage(-1)">
            <v-icon>mdi-chevron-right</v-icon>
          </v-btn>
          <span class="text-caption" dir="ltr">{{ currentPage }} / {{ pageCount }}</span>
          <v-btn icon size="small" variant="tonal" :disabled="currentPage >= pageCount" @click="changePage(1)">
            <v-icon>mdi-chevron-left</v-icon>
          </v-btn>
        </div>
      </template>
      <template v-else>
        <v-icon size="48" color="grey" class="mb-2 opacity-60">mdi-file-hidden</v-icon>
        <p class="text-body-2 text-medium-emphasis mb-0">{{ $t('teacher.pdf.uploadForPreview') }}</p>
      </template>
    </div>

    <v-row v-if="file && !error" class="mt-3" dense>
      <v-col cols="6">
        <div class="stat-box text-center pa-3 rounded-lg">
          <div class="text-h6 font-weight-bold" dir="ltr">{{ pageCount }}</div>
          <div class="text-caption text-medium-emphasis">{{ $t('teacher.labels.pages') }}</div>
        </div>
      </v-col>
      <v-col cols="6">
        <div class="stat-box text-center pa-3 rounded-lg">
          <div class="text-h6 font-weight-bold" dir="ltr">{{ formatFileSize(file.size) }}</div>
          <div class="text-caption text-medium-emphasis">{{ $t('teacher.labels.fileSize') }}</div>
        </div>
      </v-col>
    </v-row>
  </v-card>
</template>

<script setup>
import { computed, nextTick, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import { formatFileSize } from '../../utils/format.js'
import { renderPdfPageToCanvas } from '../../utils/pdfPreview.js'

defineEmits(['remove'])

const props = defineProps({
  file: { type: Object, default: null },
  pageCount: { type: Number, default: 1 },
  uploading: { type: Boolean, default: false },
  error: { type: String, default: null },
})

const canvasRef = ref(null)
const rendering = ref(false)
const currentPage = ref(1)
const localPageCount = ref(1)

const pageCount = computed(() => Math.max(props.pageCount || 0, localPageCount.value || 1))

const previewLabel = computed(() => {
  if (props.error) return t('teacher.lessons.previewFailed')
  if (props.file) return props.file.name
  return t('teacher.status.waitingFile')
})

async function drawPage(page = currentPage.value) {
  if (!props.file || props.error || !canvasRef.value) return
  rendering.value = true
  try {
    const total = await renderPdfPageToCanvas(props.file, canvasRef.value, page)
    localPageCount.value = total
    currentPage.value = Math.min(page, total)
  } catch {
    /* parent handles validation errors */
  } finally {
    rendering.value = false
  }
}

function changePage(delta) {
  const next = currentPage.value + delta
  if (next < 1 || next > pageCount.value) return
  currentPage.value = next
  drawPage(next)
}

watch(
  () => props.file,
  async (file) => {
    currentPage.value = 1
    localPageCount.value = props.pageCount || 1
    if (!file) return
    await nextTick()
    drawPage(1)
  },
  { immediate: true },
)
</script>

<style scoped>
.media-preview-panel {
  background: rgb(var(--v-theme-surface)) !important;
  border: 1px solid rgba(var(--v-border-color), 0.14);
  border-radius: 12px;
}

.pdf-preview-frame {
  background: rgba(var(--v-theme-on-surface), 0.03);
  border: 1px solid rgba(var(--v-border-color), 0.12);
  min-height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 12px;
  overflow: auto;
}

.pdf-preview-frame--error {
  border-color: rgba(var(--v-theme-error), 0.35);
}

.pdf-preview-frame--empty {
  min-height: 160px;
}

.pdf-canvas {
  max-width: 100%;
  height: auto;
  border-radius: 6px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.stat-box {
  background: rgba(var(--v-theme-on-surface), 0.04);
  border: 1px solid rgba(var(--v-border-color), 0.1);
}

.min-width-0 {
  min-width: 0;
}
</style>
