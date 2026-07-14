<template>
  <TeacherWorkspaceCard
    class="teacher-voice-workspace tds-scope"
    :title="$t('teacher.voice.samplesTitle')"
    :meta="$t('teacher.voice.samplesMeta')"
    :aria-label="$t('teacher.voice.libraryAria')"
  >
    <v-alert
      v-if="error"
      type="error"
      variant="tonal"
      density="compact"
      class="teacher-voice-workspace__alert rounded-lg"
      closable
      @click:close="error = ''"
    >
      {{ error }}
    </v-alert>

    <div class="teacher-voice-workspace__toolbar">
      <div class="teacher-voice-workspace__progress-line">
        <span class="teacher-voice-workspace__progress-label">
          {{ $t('teacher.voice.samplesCountShort', { count: sampleCount, max: maxVoiceSamples }) }}
        </span>
        <v-progress-linear
          :model-value="progressPercent"
          height="4"
          rounded
          color="primary"
          class="teacher-voice-workspace__progress-bar"
        />
      </div>
      <p class="teacher-voice-workspace__progress-hint">
        {{ $t('teacher.voice.moreSamplesHint') }}
      </p>

      <div class="teacher-voice-workspace__add">
        <TeacherButton
          v-if="canAddMore && hasAnySample && !uploadPanelOpen"
          size="small"
          variant="primary"
          prepend-icon="mdi-plus"
          @click="openUploadPanel()"
        >
          {{ $t('teacher.actions.uploadVoiceAnother') }}
        </TeacherButton>
        <TeacherButton
          v-else-if="!canAddMore && hasAnySample"
          size="small"
          variant="ghost"
          disabled
        >
          {{ $t('teacher.voice.maxSamplesShort', { max: maxVoiceSamples }) }}
        </TeacherButton>
      </div>
    </div>

    <div
      v-if="uploadPanelOpen || !hasAnySample"
      id="teacher-voice-library-upload"
      class="teacher-voice-workspace__upload"
    >
      <p v-if="replaceTargetId" class="teacher-voice-workspace__upload-label">
        {{ $t('teacher.voice.replaceTarget', { name: replaceTargetName }) }}
      </p>
      <VoiceRecorder
        upload-only
        :sample-status="latestSampleStatus"
        :uploading="uploading"
        @upload="onUpload"
      />
      <TeacherButton
        v-if="hasAnySample && uploadPanelOpen"
        size="small"
        variant="ghost"
        @click="closeUploadPanel"
      >
        {{ $t('common.cancel') }}
      </TeacherButton>
    </div>

    <ul v-if="librarySamples.length" class="teacher-voice-workspace__list" role="list">
      <li v-for="sample in librarySamples" :key="sample.id" class="teacher-voice-workspace__list-item" role="listitem">
        <TeacherVoiceSampleCard
          :display-name="sample.displayName"
          :duration-seconds="sample.duration_seconds"
          :uploaded-at="formatDate(sample.uploaded_at)"
          :status-label="friendlyVoiceSampleStatus(sample)"
          :is-default="sample.isDefault"
          :preview-url="previewUrls[sample.id] || ''"
          :preview-loading="previewingId === sample.id"
          :deleting="deletingId === sample.id"
          :can-listen="sample.ready"
          @listen="loadPreview(sample)"
          @replace="openUploadPanel(sample.id)"
          @delete="confirmDelete(sample)"
        />
      </li>
    </ul>

    <TeacherFormHint variant="info" class="teacher-voice-workspace__tip">
      {{ $t('teacher.voice.firstDefaultHint') }}
    </TeacherFormHint>

    <v-dialog v-model="deleteDialog" max-width="440">
      <v-card class="tds-scope pa-5 rounded-xl" variant="flat">
        <h3 class="text-h6 font-weight-bold mb-3">{{ $t('teacher.voice.deleteTitle') }}</h3>
        <v-alert
          v-if="sampleToDelete?.isDefault && readyCount <= 1"
          type="warning"
          variant="tonal"
          density="compact"
          class="mb-4"
        >
          {{ $t('teacher.voice.deleteLastWarning') }}
        </v-alert>
        <p v-else class="text-body-2 mb-0">{{ $t('teacher.voice.deleteConfirmQuestion', { name: sampleToDelete?.displayName }) }}</p>
        <div class="d-flex justify-end gap-2 mt-4">
          <TeacherButton variant="ghost" @click="deleteDialog = false">{{ $t('common.cancel') }}</TeacherButton>
          <TeacherButton variant="danger" :loading="deletingId != null" @click="deleteSample">
            {{ $t('common.delete') }}
          </TeacherButton>
        </div>
      </v-card>
    </v-dialog>
  </TeacherWorkspaceCard>
</template>

<script setup>
import { computed, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import VoiceRecorder from './VoiceRecorder.vue'
import TeacherVoiceSampleCard from './profile/TeacherVoiceSampleCard.vue'
import {
  TeacherWorkspaceCard,
  TeacherFormHint,
  TeacherButton,
} from './design-system/index.js'
import { previewTeacherVoiceSample } from '../../api/teacher.js'
import { getErrorMessage, getApiBaseUrl } from '../../api/client.js'
import { useToast } from '../../composables/useToast.js'
import { friendlyVoiceSampleStatus, useTeacherVoiceProfile } from '../../composables/useTeacherVoiceProfile.js'

const { showSuccess, showError } = useToast()

const {
  librarySamples,
  hasAnySample,
  readyCount,
  sampleCount,
  canAddMore,
  maxVoiceSamples,
  latestSampleStatus,
  uploading,
  uploadPanelOpen,
  replaceTargetId,
  replaceRequested,
  loadProfile,
  uploadVoice,
  deleteVoiceSample,
  registerConsumer,
  unregisterConsumer,
  openUploadPanel,
  closeUploadPanel,
  clearReplaceRequest,
} = useTeacherVoiceProfile()

const error = ref('')
const deletingId = ref(null)
const deleteDialog = ref(false)
const sampleToDelete = ref(null)
const previewingId = ref(null)
const previewUrls = reactive({})
const previewText = ref(t('teacher.voice.previewText'))

const progressPercent = computed(() =>
  Math.min(100, (sampleCount.value / maxVoiceSamples) * 100),
)

const replaceTargetName = computed(() => {
  if (!replaceTargetId.value) return ''
  return librarySamples.value.find((s) => s.id === replaceTargetId.value)?.displayName || t('teacher.voice.sampleFallback')
})

watch(replaceRequested, (requested) => {
  if (requested) clearReplaceRequest()
})

function formatDate(iso) {
  if (!iso) return ''
  try {
    return new Intl.DateTimeFormat('ar-SY', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(iso))
  } catch {
    return iso
  }
}

function resolveAudioUrl(path) {
  if (!path) return ''
  if (path.startsWith('http')) return path
  const base = getApiBaseUrl()?.replace(/\/api\/?$/, '') || ''
  return `${base}${path}`
}

function confirmDelete(sample) {
  sampleToDelete.value = sample
  deleteDialog.value = true
}

async function deleteSample() {
  if (!sampleToDelete.value) return
  const sampleId = sampleToDelete.value.id
  deletingId.value = sampleId
  error.value = ''
  try {
    await deleteVoiceSample(sampleId)
    delete previewUrls[sampleId]
    deleteDialog.value = false
    sampleToDelete.value = null
    showSuccess(t('teacher.status.sampleDeleted'))
  } catch (e) {
    error.value = getErrorMessage(e, t('teacher.errors.deleteSample'))
    showError(error.value)
  } finally {
    deletingId.value = null
  }
}

async function onUpload(blobOrFile) {
  error.value = ''
  const replacingId = replaceTargetId.value
  try {
    await uploadVoice(blobOrFile)
    if (replacingId) {
      try {
        await deleteVoiceSample(replacingId)
        delete previewUrls[replacingId]
      } catch (e) {
        showError(getErrorMessage(e, t('teacher.success.replacePartial')))
      }
    }
    closeUploadPanel()
    showSuccess(replacingId ? t('teacher.status.sampleReplaced') : t('teacher.status.sampleAdded'))
  } catch (e) {
    error.value = getErrorMessage(e, t('teacher.errors.uploadRecording'))
    showError(error.value)
  }
}

async function loadPreview(sample) {
  previewingId.value = sample.id
  previewUrls[sample.id] = ''
  try {
    const result = await previewTeacherVoiceSample(sample.id, previewText.value)
    if (result.audio_url) {
      previewUrls[sample.id] = resolveAudioUrl(result.audio_url)
    }
  } catch (e) {
    showError(getErrorMessage(e, t('teacher.errors.previewVoice')))
  } finally {
    previewingId.value = null
  }
}

onMounted(async () => {
  registerConsumer()
  try {
    await loadProfile()
  } catch (e) {
    error.value = getErrorMessage(e, t('teacher.errors.loadVoice'))
  }
})

onUnmounted(() => {
  unregisterConsumer()
})
</script>

<style scoped>
.teacher-voice-workspace {
  margin-bottom: var(--em-space-xl);
}

.teacher-voice-workspace__alert {
  margin-bottom: var(--em-space-md);
}

.teacher-voice-workspace__toolbar {
  margin-bottom: var(--em-space-sm);
}

.teacher-voice-workspace__progress-line {
  display: flex;
  align-items: center;
  gap: var(--em-space-md);
  margin-bottom: 4px;
}

.teacher-voice-workspace__progress-label {
  flex-shrink: 0;
  font-size: 0.8125rem;
  font-weight: 700;
  color: var(--em-text);
}

.teacher-voice-workspace__progress-bar {
  flex: 1;
  min-width: 4rem;
}

.teacher-voice-workspace__progress-hint {
  margin: 0 0 var(--em-space-sm);
  font-size: 0.75rem;
  line-height: 1.4;
  color: var(--em-text-muted);
}

.teacher-voice-workspace__add {
  margin-bottom: var(--em-space-sm);
}

.teacher-voice-workspace__upload {
  margin-bottom: var(--em-space-sm);
}

.teacher-voice-workspace__upload-label {
  margin: 0 0 var(--em-space-sm);
  font-size: 0.8125rem;
  color: var(--em-text-muted);
}

.teacher-voice-workspace__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: var(--em-space-md);
}

.teacher-voice-workspace__list-item {
  margin: 0;
  padding: 0;
}

.teacher-voice-workspace__tip {
  margin-top: 0;
  margin-bottom: 0;
}
</style>
