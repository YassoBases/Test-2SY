<template>
  <article class="tds-scope tds-content-editor">
    <div class="tds-content-editor__head">
      <div class="tds-content-editor__meta">
        <v-icon class="tds-content-editor__icon" :color="iconColor" size="20">{{ icon }}</v-icon>
        <div>
          <p class="tds-content-editor__label">{{ label }}</p>
          <p class="tds-content-editor__status">{{ statusText }}</p>
        </div>
      </div>

      <div class="tds-content-editor__actions">
        <TeacherButton
          v-if="hasCurrent && !removed && !replacementFile"
          size="small"
          variant="danger"
          @click="$emit('remove')"
        >
          <v-icon start size="16">mdi-delete</v-icon>
          {{ $t('common.delete') }}
        </TeacherButton>
        <TeacherButton
          v-if="removed"
          size="small"
          variant="tonal"
          @click="$emit('undo-remove')"
        >
          <v-icon start size="16">mdi-undo</v-icon>
          {{ $t('teacher.actions.undo') }}
        </TeacherButton>
        <TeacherButton
          size="small"
          variant="tonal"
          @click="fileInput?.click()"
        >
          <v-icon start size="16">mdi-upload</v-icon>
          {{ hasCurrent && !removed ? $t('common.update') : $t('teacher.actions.uploadPdf') }}
        </TeacherButton>
        <input
          ref="fileInput"
          type="file"
          :accept="accept"
          class="d-none"
          @change="onPick"
        />
      </div>
    </div>

    <div v-if="replacementFile && previewComponent" class="tds-content-editor__preview">
      <component :is="previewComponent" :file="replacementFile" @remove="clearReplacement" />
    </div>

    <div v-else-if="replacementFile && kind === 'audio'" class="tds-content-editor__audio-box">
      <p class="tds-content-editor__audio-name">{{ replacementFile.name }}</p>
      <audio v-if="replacementPreviewUrl" :src="replacementPreviewUrl" controls class="w-100 mb-2" />
      <TeacherButton size="small" variant="danger" @click="clearReplacement">
        <v-icon start size="16">mdi-close</v-icon>
        {{ $t('teacher.actions.cancelReplace') }}
      </TeacherButton>
    </div>

    <div v-else-if="hasCurrent && !removed && currentUrl" class="tds-content-editor__preview">
      <video v-if="kind === 'video'" :src="currentUrl" controls class="w-100" preload="metadata" />
      <iframe v-else-if="kind === 'pdf'" :src="currentUrl" class="pdf-iframe w-100" title="PDF" />
      <div v-else-if="kind === 'audio'" class="pa-3">
        <audio :src="currentUrl" controls class="w-100" />
      </div>
    </div>

    <TeacherWarningCard
      v-else-if="removed"
      variant="warning"
      :message="$t('teacher.labels.willDeleteOnSave', { type: label })"
    />

    <p v-else class="tds-content-editor__empty">
      {{ $t('teacher.labels.noTypeUploadNew', { type: label }) }}
    </p>
  </article>
</template>

<script setup>
import { computed, onUnmounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import VideoPreviewCard from './VideoPreviewCard.vue'
import PdfPreviewCard from './PdfPreviewCard.vue'
import TeacherButton from './design-system/TeacherButton.vue'
import TeacherWarningCard from './design-system/TeacherWarningCard.vue'
import { MAX_PDF_SIZE_BYTES, MAX_PDF_SIZE_LABEL } from '../../constants/app.js'

const props = defineProps({
  kind: { type: String, required: true },
  label: { type: String, required: true },
  icon: { type: String, required: true },
  iconColor: { type: String, default: 'primary' },
  accept: { type: String, required: true },
  hasCurrent: { type: Boolean, default: false },
  currentUrl: { type: String, default: '' },
  currentFilename: { type: String, default: '' },
  removed: { type: Boolean, default: false },
  replacementFile: { type: Object, default: null },
})

const emit = defineEmits(['remove', 'undo-remove', 'replace', 'clear-replace', 'validation-error'])

const fileInput = ref(null)
const replacementPreviewUrl = ref('')

const previewComponent = computed(() => {
  if (props.kind === 'video') return VideoPreviewCard
  if (props.kind === 'pdf') return PdfPreviewCard
  return null
})

const statusText = computed(() => {
  if (props.removed) return t('teacher.lessons.willDeleteOnSave')
  if (props.replacementFile) return t('teacher.labels.replaceFile', { name: props.replacementFile.name })
  if (props.hasCurrent) return props.currentFilename || t('teacher.lessons.currentFile')
  return t('teacher.status.notUploaded')
})

watch(
  () => props.replacementFile,
  (file) => {
    if (replacementPreviewUrl.value) URL.revokeObjectURL(replacementPreviewUrl.value)
    replacementPreviewUrl.value = file && props.kind === 'audio' ? URL.createObjectURL(file) : ''
  },
  { immediate: true },
)

function onPick(event) {
  const file = event.target.files?.[0]
  if (!file) return
  if (props.kind === 'pdf' && file.size > MAX_PDF_SIZE_BYTES) {
    emit('validation-error', t('teacher.lessons.fileTooLarge', { size: MAX_PDF_SIZE_LABEL }))
    if (fileInput.value) fileInput.value.value = ''
    return
  }
  emit('replace', file)
  if (fileInput.value) fileInput.value.value = ''
}

function clearReplacement() {
  emit('clear-replace')
}

onUnmounted(() => {
  if (replacementPreviewUrl.value) URL.revokeObjectURL(replacementPreviewUrl.value)
})
</script>
