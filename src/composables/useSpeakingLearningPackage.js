import { computed, ref } from 'vue'

import {

  createSpeakingLearningPackage,

  ensureSpeakingLearningPackage,

  fetchSpeakingLearningPackage,

  fetchSpeakingLearningPackageStatus,

  startSpeakingLearning,

} from '../api/speakingLearningPackage.js'



export function useSpeakingLearningPackage() {

  const packageResult = ref(null)

  const startResult = ref(null)

  const loading = ref(false)

  const starting = ref(false)

  const error = ref('')



  const packageId = computed(

    () =>

      packageResult.value?.package_id ||

      startResult.value?.package?.package_id ||

      null,

  )

  const reused = computed(() =>

    Boolean(packageResult.value?.reused || startResult.value?.package?.reused),

  )

  const packageData = computed(

    () =>

      packageResult.value?.package ||

      startResult.value?.package?.package ||

      null,

  )

  const lessonFromStart = computed(() => startResult.value?.lesson || null)



  async function ensurePackage(opts = {}) {

    loading.value = true

    error.value = ''

    try {

      const data = await ensureSpeakingLearningPackage(opts)

      packageResult.value = data

      return data

    } catch (err) {

      error.value =

        err?.response?.data?.detail || err?.message || 'Failed to prepare learning package'

      throw err

    } finally {

      loading.value = false

    }

  }



  async function startLearning(opts = {}) {

    starting.value = true

    error.value = ''

    try {

      const data = await startSpeakingLearning(opts)

      startResult.value = data

      if (data?.package) {

        packageResult.value = {

          success: true,

          reused: data.package.reused,

          cached: data.package.cached,

          package_id: data.package.package_id,

          content_item_id: data.package.content_item_id,

          status: data.package.status,

          constraints_fingerprint: data.package.constraints_fingerprint,

          content_fingerprint: data.package.content_fingerprint,

          package: data.package.package,

        }

      }

      return data

    } catch (err) {

      error.value =

        err?.response?.data?.detail || err?.message || 'Failed to start learning'

      throw err

    } finally {

      starting.value = false

    }

  }



  async function createPackage(payload) {

    loading.value = true

    error.value = ''

    try {

      const data = await createSpeakingLearningPackage(payload)

      packageResult.value = data

      return data

    } catch (err) {

      error.value =

        err?.response?.data?.detail || err?.message || 'Failed to create learning package'

      throw err

    } finally {

      loading.value = false

    }

  }



  async function loadPackage(packageIdValue) {

    loading.value = true

    error.value = ''

    try {

      const data = await fetchSpeakingLearningPackage(packageIdValue)

      packageResult.value = data

      return data

    } catch (err) {

      error.value =

        err?.response?.data?.detail || err?.message || 'Failed to load learning package'

      throw err

    } finally {

      loading.value = false

    }

  }



  async function loadStatus(packageIdValue) {

    return fetchSpeakingLearningPackageStatus(packageIdValue)

  }



  function clear() {

    packageResult.value = null

    startResult.value = null

    error.value = ''

  }



  return {

    packageResult,

    startResult,

    loading,

    starting,

    error,

    packageId,

    reused,

    packageData,

    lessonFromStart,

    ensurePackage,

    startLearning,

    createPackage,

    loadPackage,

    loadStatus,

    clear,

  }

}


