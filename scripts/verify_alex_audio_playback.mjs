/**
 * Static verification for the Alex/EVI assistant output playback fix.
 *
 * Proves the vendor-aligned WAV decode + sequential queue architecture is in
 * place and the old raw-PCM/24kHz/stop-previous behavior is gone.
 *
 * Run: node scripts/verify_alex_audio_playback.mjs
 *
 * NOTE: This is a STATIC source check only. It CANNOT prove real speaker
 * output is intelligible. REAL BROWSER LISTENING IS STILL REQUIRED.
 */

import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'

const __dirname = dirname(fileURLToPath(import.meta.url))
const target = resolve(__dirname, '../src/composables/useLiveConversation.js')
const src = readFileSync(target, 'utf8')

/** Extract the body of a top-level function by brace matching. */
function fnBody(name) {
  const start = src.indexOf(`function ${name}(`)
  if (start === -1) return ''
  // Skip the parameter list (which may contain destructuring braces) by
  // matching parentheses first, then take the first brace after the params.
  let paren = 0
  let i = src.indexOf('(', start)
  for (; i < src.length; i += 1) {
    if (src[i] === '(') paren += 1
    else if (src[i] === ')') {
      paren -= 1
      if (paren === 0) break
    }
  }
  const open = src.indexOf('{', i)
  if (open === -1) return ''
  let depth = 0
  for (let j = open; j < src.length; j += 1) {
    if (src[j] === '{') depth += 1
    else if (src[j] === '}') {
      depth -= 1
      if (depth === 0) return src.slice(open, j + 1)
    }
  }
  return ''
}

/** Extract the `if (type === '<t>')` branch block from _handleEviMessage. */
function eviBranch(t) {
  const marker = `type === '${t}'`
  const at = src.indexOf(marker)
  if (at === -1) return ''
  const open = src.indexOf('{', at)
  let depth = 0
  for (let i = open; i < src.length; i += 1) {
    if (src[i] === '{') depth += 1
    else if (src[i] === '}') {
      depth -= 1
      if (depth === 0) return src.slice(open, i + 1)
    }
  }
  return ''
}

const audioOutputBranch = eviBranch('audio_output')
const userInterruptionBranch = eviBranch('user_interruption')
const userMessageBranch = eviBranch('user_message')
const pumpBody = fnBody('_pumpAssistantPlayback')
const clearBody = fnBody('_clearAssistantPlayback')
const idleBody = fnBody('_assistantPlaybackIdle')
const pipelineBody = fnBody('_startAudioPipeline')

const checks = [
  {
    id: 'A',
    name: 'old raw PCM output interpretation is gone',
    pass:
      !src.includes('_playPcmBase64') &&
      !/new Int16Array\(bytes\.buffer\)/.test(src) &&
      !/createBuffer\(1,/.test(src) &&
      !/\/ 32768/.test(src),
  },
  {
    id: 'B',
    name: 'no hardcoded 24000 output playback rate remains',
    pass: !src.includes('24000'),
  },
  {
    id: 'C',
    name: 'decodeAudioData is used for EVI WAV output',
    pass: /playbackContext\.decodeAudioData\(/.test(pumpBody),
  },
  {
    id: 'D',
    name: 'sequential playback queue with nextPlaybackStartTime cursor exists',
    pass:
      src.includes('playbackByteQueue') &&
      src.includes('nextPlaybackStartTime') &&
      /Math\.max\(\s*ctx\.currentTime,\s*nextPlaybackStartTime\s*\)/.test(src) &&
      /nextPlaybackStartTime = startAt \+ audioBuffer\.duration/.test(src),
  },
  {
    id: 'E',
    name: 'audio_output enqueues and does NOT stop previous playback',
    pass: audioOutputBranch.includes('_enqueueAssistantAudio') && !audioOutputBranch.includes('.stop('),
  },
  {
    id: 'F',
    name: 'single sequential pump preserves chunk order (ordered shift + isPumping guard)',
    pass:
      /if \(isPumping\) return/.test(pumpBody) &&
      pumpBody.includes('playbackByteQueue.shift()') &&
      /while \(playbackByteQueue\.length\)/.test(pumpBody),
  },
  {
    id: 'G',
    name: 'user_interruption clears playback',
    pass: userInterruptionBranch.includes('_clearAssistantPlayback()'),
  },
  {
    id: 'H',
    name: 'non-interim user_message clears playback',
    pass:
      userMessageBranch.includes('_clearAssistantPlayback()') &&
      src.includes("type === 'user_message' && !msg.interim"),
  },
  {
    id: 'I',
    name: 'disconnect/end/reset/reconnect/cleanup all clear playback',
    pass:
      (src.match(/_clearAssistantPlayback\(\)/g) || []).length >= 6 &&
      fnBody('endLiveSession').includes('_clearAssistantPlayback()') &&
      fnBody('_cleanupMedia').includes('_clearAssistantPlayback()') &&
      fnBody('_attemptReconnect').includes('_clearAssistantPlayback()') &&
      fnBody('startLiveSession').includes('_clearAssistantPlayback()'),
  },
  {
    id: 'J',
    name: 'stale async decode cannot resurrect cancelled audio (epoch token)',
    pass:
      /playbackEpoch \+= 1/.test(clearBody) &&
      /const epoch = playbackEpoch/.test(pumpBody) &&
      /epoch !== playbackEpoch/.test(pumpBody),
  },
  {
    id: 'K',
    name: 'Alex speaking state is queue-aware',
    pass:
      idleBody.includes('playbackByteQueue.length === 0') &&
      idleBody.includes('scheduledSources.size === 0') &&
      idleBody.includes('!isPumping') &&
      src.includes('_maybeReturnToReady'),
  },
  {
    id: 'L',
    name: 'microphone input PCM path remains unchanged (linear16 16k mono)',
    pass:
      pipelineBody.includes('new Int16Array(input.length)') &&
      pipelineBody.includes("type: 'audio_input'") &&
      /sample_rate: 16000/.test(src) &&
      /encoding: 'linear16'/.test(src),
  },
]

const results = checks.map((c) => ({ id: c.id, name: c.name, pass: Boolean(c.pass) }))
const pass = results.every((r) => r.pass)

console.log('[verify_alex_audio_playback]')
for (const r of results) {
  console.log(`  ${r.pass ? 'PASS' : 'FAIL'}  ${r.id}. ${r.name}`)
}
console.log(pass ? '\nRESULT: PASS (static only — REAL BROWSER LISTENING REQUIRED)' : '\nRESULT: FAIL')
process.exit(pass ? 0 : 1)
