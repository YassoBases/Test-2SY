<template>
  <div id="teacher-voice-profile-upload" class="teacher-voice-upload tds-scope">
    <div
      v-if="hasAnySample && !replacing"
      class="teacher-voice-upload__success"
    >
      <div class="teacher-voice-upload__success-row">
        <v-icon icon="mdi-check-circle" color="success" size="22" />
        <span class="teacher-voice-upload__success-text">{{ $t('teacher.status.voiceUploaded') }}</span>
        <span v-if="isProcessing" class="teacher-voice-upload__success-hint">{{ $t('teacher.status.analyzingVoice') }}</span>
      </div>
      <TeacherButton size="small" variant="ghost" @click="requestVoiceReplace()">
        {{ $t('teacher.actions.replaceSample') }}
      </TeacherButton>
    </div>

    <div v-else class="teacher-voice-upload__panel">
      <VoiceRecorder
        upload-only
        :sample-status="latestSampleStatus"
        :uploading="uploading"
        @upload="onUpload"
      />
      <TeacherButton
        v-if="hasAnySample && replacing"
        size="small"
        variant="ghost"
        class="teacher-voice-upload__cancel"
        @click="replacing = false"
      >
        {{ $t('common.cancel') }}
      </TeacherButton>
    </div>

    <v-alert
      v-if="error"
      type="error"
      variant="tonal"
      density="compact"
      class="teacher-voice-upload__alert rounded-lg mt-3"
      closable
      @click:close="error = ''"
    >
      {{ error }}
    </v-alert>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import VoiceRecorder from '../VoiceRecorder.vue'
import { TeacherButton } from '../design-system/index.js'
import { useTeacherVoiceProfile } from '../../../composables/useTeacherVoiceProfile.js'
import { getErrorMessage } from '../../../api/client.js'
import { useToast } from '../../../composables/useToast.js'

const props = defineProps({
  embedded: { type: Boolean, default: false },
})

const { showSuccess, showError } = useToast()

const {
  uploading,
  hasAnySample,
  isProcessing,
  latestSampleStatus,
  replaceRequested,
  loadProfile,
  uploadVoice,
  registerConsumer,
  unregisterConsumer,
  clearReplaceRequest,
  requestVoiceReplace,
} = useTeacherVoiceProfile()

const replacing = ref(false)
const error = ref('')

watch(hasAnySample, (has) => {
  if (has && !replaceRequested.value) replacing.value = false
})

watch(replaceRequested, (requested) => {
  if (requested) {
    replacing.value = false
    clearReplaceRequest()
  }
})

async function onUpload(blobOrFile) {
  error.value = ''
  try {
    await uploadVoice(blobOrFile)
    replacing.value = false
    showSuccess(t('teacher.status.voiceUploadSuccess'))
  } catch (e) {
    error.value = getErrorMessage(e, t('teacher.errors.uploadRecording'))
    showError(error.value)
  }
}

onMounted(async () => {
  if (props.embedded) return
  registerConsumer()
  try {
    await loadProfile()
  } catch (e) {
    error.value = getErrorMessage(e, t('teacher.errors.loadVoice'))
  }
})

onUnmounted(() => {
  if (props.embedded) return
  unregisterConsumer()
})
</script>

<style scoped>
.teacher-voice-upload {
  margin-bottom: var(--em-space-lg);
}

.teacher-voice-upload__success {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: var(--em-space-md);
  padding: var(--em-space-md) var(--em-space-lg);
  border-radius: var(--em-radius-lg, 16px);
  border: 1px solid color-mix(in srgb, var(--em-success, #22c55e) 30%, var(--em-border-subtle));
  background: var(--em-surface-control, rgba(var(--v-theme-on-surface), 0.03));
}

.teacher-voice-upload__success-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--em-space-sm);
}

.teacher-voice-upload__success-text {
  font-size: 0.9375rem;
  font-weight: 700;
  color: var(--em-text);
}

.teacher-voice-upload__success-hint {
  font-size: 0.8125rem;
  color: var(--em-text-muted);
}

.teacher-voice-upload__cancel {
  margin-top: var(--em-space-sm);
}
</style>
