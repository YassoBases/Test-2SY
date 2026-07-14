import { computed, ref } from 'vue'
import {
  fetchTeacherVoiceProfile,
  uploadTeacherVoiceSample,
  deleteTeacherVoiceSample,
} from '../api/teacher.js'
import { MAX_VOICE_SAMPLES } from '../constants/teacherVoice.js'

const profile = ref(null)
const uploading = ref(false)
const replaceRequested = ref(false)
const uploadPanelOpen = ref(false)
const replaceTargetId = ref(null)
let pollTimer = null
let consumerCount = 0

function stopPoll() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

async function loadProfileInternal() {
  profile.value = await fetchTeacherVoiceProfile()
  const pending = (profile.value?.samples || []).some((s) =>
    ['pending', 'processing'].includes(s.processing_status),
  )
  if (pending && !pollTimer) {
    pollTimer = setInterval(async () => {
      try {
        profile.value = await fetchTeacherVoiceProfile()
        const stillPending = (profile.value?.samples || []).some((s) =>
          ['pending', 'processing'].includes(s.processing_status),
        )
        if (!stillPending) stopPoll()
      } catch {
        stopPoll()
      }
    }, 2500)
  } else if (!pending) {
    stopPoll()
  }
}

function sortByUploadedAsc(list) {
  return [...list].sort(
    (a, b) => new Date(a.uploaded_at || 0).getTime() - new Date(b.uploaded_at || 0).getTime(),
  )
}

export function useTeacherVoiceProfile() {
  const samples = computed(() => profile.value?.samples || [])

  const activeSample = computed(() => {
    const list = samples.value
    return list.find((s) => s.is_latest_ready) || list.find((s) => s.ready) || list[0] || null
  })

  const hasAnySample = computed(() => samples.value.length > 0)

  const hasReadyVoice = computed(() =>
    Boolean(profile.value?.has_ready_profile && activeSample.value?.ready),
  )

  const isProcessing = computed(() => {
    const s = activeSample.value?.processing_status
    return s === 'pending' || s === 'processing'
  })

  const isFailed = computed(() => activeSample.value?.processing_status === 'failed')

  const readyCount = computed(() => samples.value.filter((s) => s.ready).length)

  const sampleCount = computed(() => samples.value.length)

  const canAddMore = computed(() => sampleCount.value < MAX_VOICE_SAMPLES)

  const defaultSampleId = computed(() => {
    const readyOldest = sortByUploadedAsc(samples.value.filter((s) => s.ready))
    if (readyOldest.length) return readyOldest[0].id
    const oldest = sortByUploadedAsc(samples.value)
    return oldest[0]?.id ?? null
  })

  const librarySamples = computed(() => {
    const asc = sortByUploadedAsc(samples.value)
    const numberById = new Map(asc.map((s, index) => [s.id, index + 1]))
    return [...samples.value]
      .sort(
        (a, b) => new Date(b.uploaded_at || 0).getTime() - new Date(a.uploaded_at || 0).getTime(),
      )
      .map((sample) => ({
        ...sample,
        displayName: `عينة ${numberById.get(sample.id) ?? '—'}`,
        isDefault: sample.id === defaultSampleId.value,
      }))
  })

  const latestSampleStatus = computed(() => {
    const latest = samples.value[0]
    if (!latest) return null
    return {
      has_sample: true,
      id: latest.id,
      processing_status: latest.processing_status,
      status_label: latest.status_label,
      duration_seconds: latest.duration_seconds,
      uploaded_at: latest.uploaded_at,
      error_message: latest.error_message,
      ready: latest.ready,
    }
  })

  async function loadProfile() {
    await loadProfileInternal()
  }

  async function uploadVoice(blobOrFile) {
    uploading.value = true
    try {
      const file =
        blobOrFile instanceof File
          ? blobOrFile
          : new File([blobOrFile], 'voice-sample.webm', { type: blobOrFile.type || 'audio/webm' })
      await uploadTeacherVoiceSample(file)
      await loadProfileInternal()
    } finally {
      uploading.value = false
    }
  }

  async function deleteVoiceSample(sampleId) {
    profile.value = await deleteTeacherVoiceSample(sampleId)
    await loadProfileInternal()
  }

  function registerConsumer() {
    consumerCount++
  }

  function unregisterConsumer() {
    consumerCount--
    if (consumerCount <= 0) {
      consumerCount = 0
      stopPoll()
    }
  }

  function openUploadPanel(replaceSampleId = null) {
    replaceTargetId.value = replaceSampleId
    uploadPanelOpen.value = true
    replaceRequested.value = false
    document.getElementById('teacher-voice-library-upload')?.scrollIntoView({
      behavior: 'smooth',
      block: 'nearest',
    })
  }

  function closeUploadPanel() {
    uploadPanelOpen.value = false
    replaceTargetId.value = null
  }

  function requestVoiceReplace(sampleId = null) {
    replaceRequested.value = true
    openUploadPanel(sampleId)
  }

  function clearReplaceRequest() {
    replaceRequested.value = false
  }

  return {
    profile,
    uploading,
    replaceRequested,
    uploadPanelOpen,
    replaceTargetId,
    samples,
    librarySamples,
    activeSample,
    hasAnySample,
    hasReadyVoice,
    isProcessing,
    isFailed,
    readyCount,
    sampleCount,
    canAddMore,
    defaultSampleId,
    latestSampleStatus,
    maxVoiceSamples: MAX_VOICE_SAMPLES,
    loadProfile,
    uploadVoice,
    deleteVoiceSample,
    registerConsumer,
    unregisterConsumer,
    openUploadPanel,
    closeUploadPanel,
    requestVoiceReplace,
    clearReplaceRequest,
  }
}

export function friendlyVoiceSampleStatus(sample) {
  if (sample?.ready) return 'جاهزة'
  if (['pending', 'processing'].includes(sample?.processing_status)) return 'قيد التجهيز'
  if (sample?.processing_status === 'failed') return 'غير متاحة'
  return '—'
}
