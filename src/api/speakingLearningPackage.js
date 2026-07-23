import { api } from './client.js'



/** Create via full constraints (backend-owned payload). Prefer ensure/startLearning. */

export function createSpeakingLearningPackage({

  constraints,

  authorMode = 'auto',

  useCache = true,

} = {}) {

  return api

    .post('/student/languages/speaking/learning-packages', {

      constraints: constraints || {},

      author_mode: authorMode,

      use_cache: Boolean(useCache),

    })

    .then((r) => r.data)

}



export function fetchSpeakingLearningPackage(packageId) {

  return api

    .get(`/student/languages/speaking/learning-packages/${packageId}`)

    .then((r) => r.data)

}



export function fetchSpeakingLearningPackageStatus(packageId) {

  return api

    .get(`/student/languages/speaking/learning-packages/${packageId}/status`)

    .then((r) => r.data)

}



/** Reuse active frozen package for current journey mission, else generate (E1). */

export function ensureSpeakingLearningPackage({ authorMode = 'auto', useCache = true } = {}) {

  return api

    .post('/student/languages/speaking/runtime/ensure-package', {

      author_mode: authorMode,

      use_cache: Boolean(useCache),

    })

    .then((r) => r.data)

}



/** Start Learning: journey session + ensure package + open lesson. */

export function startSpeakingLearning({

  authorMode = 'auto',

  useCache = true,

  forceRestartLesson = false,

} = {}) {

  return api

    .post('/student/languages/speaking/runtime/start-learning', {

      author_mode: authorMode,

      use_cache: Boolean(useCache),

      force_restart_lesson: Boolean(forceRestartLesson),

    })

    .then((r) => r.data)

}


