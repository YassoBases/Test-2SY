/**
 * M12.4 — frontend Scene Practice voice ownership verifier.
 * Proves the UI is a thin client: record → /rehearsal/respond → play.
 * No Realtime, no WebRTC, no client dialogue ownership.
 */
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
let PASS = 0
let FAIL = 0

function check(name, cond, detail = '') {
  if (cond) {
    PASS += 1
    console.log(`  OK  ${name}`)
  } else {
    FAIL += 1
    console.log(` FAIL ${name}${detail ? ` — ${detail}` : ''}`)
  }
}

function read(rel) {
  return fs.readFileSync(path.join(ROOT, rel), 'utf8')
}

console.log('\n=== M12.4 Frontend Scene Practice Voice ===\n')

const voicePath = 'src/composables/useScenePracticeVoice.js'
const realtimePath = 'src/composables/useScenePracticeRealtime.js'
const apiPath = 'src/api/speakingLiveBridge.js'
const viewPath = 'src/views/student/languages/StudentLanguageSpeakingView.vue'
const bridgeUiPath = 'src/components/language/SpeakingLiveBridge.vue'
const bridgeCompPath = 'src/composables/useSpeakingLiveBridge.js'

check('useScenePracticeVoice exists', fs.existsSync(path.join(ROOT, voicePath)))
check('useScenePracticeRealtime deleted', !fs.existsSync(path.join(ROOT, realtimePath)))

const voice = read(voicePath)
const api = read(apiPath)
const view = read(viewPath)
const bridgeUi = read(bridgeUiPath)
const bridgeComp = read(bridgeCompPath)

check('voice has no openai realtime url', !/openai\.com\/v1\/realtime/i.test(voice))
check('voice has no RTCPeerConnection', !/RTCPeerConnection/.test(voice))
check('voice has no mintRealtime', !/mintSpeakingRealtime|realtime-session/.test(voice))
check('voice uses MediaRecorder', /MediaRecorder/.test(voice))
check('voice plays audio_b64', /audio_b64/.test(voice) && /playAudioB64|atob/.test(voice))
check('voice does not own turns array', !/turns\.value\s*=/.test(voice) && !/turns\.value\.push/.test(voice))
check('voice modes include recording/thinking', /recording/.test(voice) && /thinking/.test(voice))

check('api has respondSpeakingRehearsal', /respondSpeakingRehearsal/.test(api))
check('api posts /rehearsal/respond', /rehearsal\/respond/.test(api))

check('bridge composable has respondVoice', /respondVoice/.test(bridgeComp))
check('view imports useScenePracticeVoice', /useScenePracticeVoice/.test(view))
check('view does not import Realtime', !/useScenePracticeRealtime/.test(view))
check('view does not sync client transcript', !/syncBridgeRehearsal|getSyncPayload|syncRehearsal\(/.test(view))
check('view primes voice on sceneVoiceShouldRun', /primeSceneVoice|prime\(/.test(view))
check('view wires start/stop recording', /onSceneStartRecording/.test(view) && /onSceneStopRecording/.test(view))
check('view renders bridgeTurns (server)', /:turns="bridgeTurns"/.test(view))
check('view does not use sceneRealtimeTurns', !/sceneRealtimeTurns/.test(view))

check('UI emit start-recording', /start-recording/.test(bridgeUi))
check('UI emit stop-recording', /stop-recording/.test(bridgeUi))
check('UI no toggle-scene-mute', !/toggle-scene-mute/.test(bridgeUi))
check('UI uses sceneVoiceMode', /sceneVoiceMode/.test(bridgeUi))
check('UI hold-to-speak', /holdToSpeak|releaseToSend/.test(bridgeUi))
check('UI coach tip from rehearsal (server)', /rehearsal\?\.coaching_notes/.test(bridgeUi))

console.log(`\nResult: ${PASS} passed, ${FAIL} failed\n`)
process.exit(FAIL === 0 ? 0 : 1)
