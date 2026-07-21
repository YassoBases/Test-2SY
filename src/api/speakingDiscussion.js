import { api } from './client.js'



/** Voice discussion turns often include Claude + local TTS/STT. */

const DISCUSSION_VOICE_TIMEOUT_MS = 5 * 60 * 1000



export function openSpeakingDiscussion({ packageId, forceRestart } = {}) {

  return api

    .post(

      '/student/languages/speaking/discussion/open',

      {

        package_id: packageId || null,

        force_restart: Boolean(forceRestart),

      },

      { timeout: DISCUSSION_VOICE_TIMEOUT_MS },

    )

    .then((r) => r.data)

}



export function fetchActiveSpeakingDiscussion() {

  return api

    .get('/student/languages/speaking/discussion/active', {

      timeout: 60 * 1000,

    })

    .then((r) => r.data)

}



export function submitSpeakingDiscussion(studentResponse) {

  return api

    .post(

      '/student/languages/speaking/discussion/submit',

      {

        student_response: studentResponse,

      },

      { timeout: DISCUSSION_VOICE_TIMEOUT_MS },

    )

    .then((r) => r.data)

}



export function submitSpeakingDiscussionVoice(blob, { filename = 'discussion_turn.webm' } = {}) {

  const form = new FormData()

  form.append('file', blob, filename)

  if (blob?.type) form.append('mime_type', blob.type)

  return api

    .post('/student/languages/speaking/discussion/submit-voice', form, {

      headers: { 'Content-Type': 'multipart/form-data' },

      timeout: DISCUSSION_VOICE_TIMEOUT_MS,

    })

    .then((r) => r.data)

}



export function advanceSpeakingDiscussion() {

  return api

    .post('/student/languages/speaking/discussion/advance', null, {

      timeout: DISCUSSION_VOICE_TIMEOUT_MS,

    })

    .then((r) => r.data)

}


