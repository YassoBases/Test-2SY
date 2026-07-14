/**
 * Static verification for the Alex mic session UI / zombie teardown fix.
 *
 * Run: node scripts/verify_alex_mic_session_ui.mjs
 *
 * NOTE: STATIC only. REAL BROWSER LISTENING + MIC ACCEPTANCE is still required.
 */

import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'

const __dirname = dirname(fileURLToPath(import.meta.url))
const composable = resolve(__dirname, '../src/composables/useLiveConversation.js')
const shell = resolve(__dirname, '../src/components/language/LanguageSpeakingLiveShell.vue')
const liveApi = resolve(__dirname, '../src/api/speakingLive.js')
const enLocale = resolve(__dirname, '../src/locales/en/student.json')

const src = readFileSync(composable, 'utf8')
const shellSrc = readFileSync(shell, 'utf8')
const apiSrc = readFileSync(liveApi, 'utf8')
const en = JSON.parse(readFileSync(enLocale, 'utf8'))

function fnBody(name, text = src) {
  const start = text.indexOf(`function ${name}(`)
  if (start === -1) return ''
  let paren = 0
  let i = text.indexOf('(', start)
  for (; i < text.length; i += 1) {
    if (text[i] === '(') paren += 1
    else if (text[i] === ')') {
      paren -= 1
      if (paren === 0) break
    }
  }
  const open = text.indexOf('{', i)
  if (open === -1) return ''
  let depth = 0
  for (let j = open; j < text.length; j += 1) {
    if (text[j] === '{') depth += 1
    else if (text[j] === '}') {
      depth -= 1
      if (depth === 0) return text.slice(open, j + 1)
    }
  }
  return ''
}

const cleanupBody = fnBody('_cleanupMedia')
const startBody = fnBody('startLiveSession')
const pipelineBody = fnBody('_startAudioPipeline')
const handleBody = fnBody('_handleEviMessage')
const live = en.languages?.speaking?.live || {}

const checks = [
  {
    id: 'A',
    name: 'intro card only for idle/ended (not error)',
    pass:
      /showHero = computed\(\(\) => state\.value === 'idle' \|\| state\.value === 'ended'\)/.test(shellSrc) &&
      !shellSrc.includes("['idle', 'error', 'ended']"),
  },
  {
    id: 'B',
    name: 'live surface renders for active and error via showLiveSurface',
    pass:
      shellSrc.includes('v-if="showLiveSurface"') &&
      src.includes("!['idle', 'ended'].includes(state.value)") &&
      shellSrc.includes('errorMessage'),
  },
  {
    id: 'C',
    name: 'mute toggle present in UI and runtime',
    pass:
      shellSrc.includes('toggleMute') &&
      shellSrc.includes('mdi-microphone-off') &&
      src.includes('function toggleMute') &&
      src.includes('micMuted.value') &&
      /if \(micMuted\.value\) return/.test(pipelineBody),
  },
  {
    id: 'D',
    name: 'End button present on live surface',
    pass: shellSrc.includes('endConversation') && shellSrc.includes('onEnd'),
  },
  {
    id: 'E',
    name: 'ws closed on cleanup / start failure (no zombie)',
    pass:
      cleanupBody.includes('_closeWebSocket()') &&
      startBody.includes('_cleanupMedia()') &&
      src.includes('function _closeWebSocket'),
  },
  {
    id: 'F',
    name: 'input 16k linear16 contract unchanged',
    pass:
      /sample_rate: 16000/.test(src) &&
      /encoding: 'linear16'/.test(src) &&
      pipelineBody.includes('new Int16Array(input.length)') &&
      pipelineBody.includes("type: 'audio_input'"),
  },
  {
    id: 'G',
    name: 'live student transcript: interim path + finalize clears utterance',
    pass:
      src.includes('currentStudentUtterance') &&
      handleBody.includes('msg.interim') &&
      handleBody.includes('_clearCurrentStudentUtterance()') &&
      apiSrc.includes('verbose_transcription') &&
      shellSrc.includes('currentStudentUtterance'),
  },
  {
    id: 'H',
    name: 'interim cleared on interruption / reconnect / teardown / new session',
    pass:
      (src.match(/_clearCurrentStudentUtterance\(\)/g) || []).length >= 5 &&
      handleBody.includes("type === 'user_interruption'") &&
      fnBody('_attemptReconnect').includes('_clearCurrentStudentUtterance()') &&
      startBody.includes('_clearCurrentStudentUtterance()') &&
      cleanupBody.includes('_clearCurrentStudentUtterance()'),
  },
  {
    id: 'I',
    name: 'mic diagnostics present (safe prefix)',
    pass: src.includes('[Alex Mic Diagnostic]') && src.includes('getUserMedia_about_to_call'),
  },
  {
    id: 'J',
    name: 'i18n keys for mute/listening/speaking present',
    pass: Boolean(live.mute && live.unmute && live.listeningHint && live.speakingNow && live.listeningLabel),
  },
  {
    id: 'K',
    name: 'pipeline start failure falls back / reports without silent zombie path',
    pass:
      pipelineBody.includes('audio_context_sampleRate_fallback') || startBody.includes('start_failed'),
  },
  {
    id: 'L',
    name: 'no fabricated streaming from S4; final user_message remains authoritative',
    pass:
      handleBody.includes("type === 'user_message' && !msg.interim") &&
      handleBody.includes("_appendTranscript('student'") &&
      !src.includes('S4') &&
      !src.includes('fake live'),
  },
]

const results = checks.map((c) => ({ id: c.id, name: c.name, pass: Boolean(c.pass) }))
const pass = results.every((r) => r.pass)

console.log('[verify_alex_mic_session_ui]')
for (const r of results) {
  console.log(`  ${r.pass ? 'PASS' : 'FAIL'}  ${r.id}. ${r.name}`)
}
console.log(
  pass
    ? '\nRESULT: PASS (static only — REAL BROWSER MIC + LISTENING ACCEPTANCE REQUIRED)'
    : '\nRESULT: FAIL',
)
process.exit(pass ? 0 : 1)
