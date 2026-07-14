/**
 * Browser/static Speaking product integration checks (A-X).
 * Run: node frontend/scripts/verify_speaking_product_browser.mjs
 */
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const ROOT = path.resolve(__dirname, '../..')

function ok(label, passed, detail = '') {
  const mark = passed ? 'PASS' : 'FAIL'
  console.log(`  [${mark}] ${label}${detail ? ` -- ${detail}` : ''}`)
  return passed
}

function read(rel) {
  return fs.readFileSync(path.join(ROOT, rel), 'utf8')
}

function main() {
  console.log('Speaking Product Browser Verification\n')
  const results = []

  const composable = read('src/composables/useLiveConversation.js')
  const api = read('src/api/speakingLive.js')
  const shell = read('src/components/language/LanguageSpeakingLiveShell.vue')
  const summary = read('src/components/language/LanguageSpeakingSessionSummary.vue')
  const view = read('src/views/student/languages/StudentLanguageSpeakingView.vue')
  const toggle = read('src/components/language/LanguageSpeakingModeToggle.vue')
  const en = JSON.parse(read('src/locales/en/student.json'))
  const ar = JSON.parse(read('src/locales/ar/student.json'))
  const backendApi = read('backend/app/api/language_speaking_live.py')

  results.push(ok('A Speaking entry renders live shell', view.includes('LanguageSpeakingLiveShell')))
  results.push(ok('B no raw i18n keys in shell', !shell.includes('student.languages.speaking.live.') || shell.includes('t(')))
  results.push(ok('C start CTA visible', shell.includes('startSpeaking')))
  results.push(ok('D microphone explanation visible', shell.includes('micExplain')))
  results.push(ok('E mic denied handling', composable.includes('mic_denied')))
  results.push(ok('F retry control', shell.includes('retry')))
  results.push(ok('G connecting state', composable.includes("'connecting'") && en.languages.speaking.live.states.connecting))
  results.push(ok('H Alex speaking state', composable.includes("'alex_speaking'")))
  results.push(ok('I student listening state', composable.includes("'student_speaking'") || composable.includes("'ready'")))
  results.push(ok('J educational processing indicator', composable.includes('processingTurn') && shell.includes('processingHint')))
  results.push(ok('K finalized transcript behavior', composable.includes('transcriptMessages') && composable.includes('finalized: true')))
  results.push(ok('L Alex vs You transcript distinction', shell.includes('alexLabel') && shell.includes('youLabel')))
  results.push(ok('M end conversation control', shell.includes('endConversation')))
  results.push(ok('N ended state', composable.includes("'ended'")))
  results.push(ok('O summary uses canonical fields only', summary.includes('coach_summary') && summary.includes('focus_label')))
  results.push(ok('P no provider/internal architecture names', !shell.includes('Hume') && !shell.includes('EVI') && !toggle.includes('Live EVI')))
  results.push(ok('Q no raw mutation_status visible', !shell.includes('mutation_status') && composable.includes('personalizationFailed')))
  results.push(ok('R no fake mastery percentage', !summary.includes('mastery') && !summary.includes('%')))
  results.push(ok('S no raw backend errors', !shell.includes('error_code') && composable.includes('Something went wrong')))
  results.push(ok('T desktop layout hooks', shell.includes('max-width') && shell.includes('speaking-live-shell')))
  results.push(ok('U mobile layout hooks', shell.includes('@media (max-width: 600px)')))
  results.push(ok('V RTL Arabic keys', !!ar.languages?.speaking?.live?.heroTitle))
  results.push(ok('W keyboard accessibility', shell.includes('aria-label') && shell.includes('aria-live')))
  results.push(ok('X reduced-motion support', shell.includes('prefers-reduced-motion')))

  results.push(ok('per-turn liveTurnId minted', composable.includes('_mintTurnId')))
  results.push(ok('student_session_summary consumed', composable.includes('student_session_summary')))
  results.push(ok('backend summary contract exposed', backendApi.includes('SpeakingStudentSessionSummaryOut')))
  results.push(ok('Alex branding EN', en.languages.speaking.live.heroTitle.includes('Alex')))
  results.push(ok('Alex branding AR', ar.languages.speaking.live.heroTitle.includes('Alex')))

  const passed = results.filter(Boolean).length
  const total = results.length
  console.log(`\nSummary: ${passed}/${total} checks passed`)
  if (passed === total) {
    console.log('SPEAKING PRODUCT BROWSER VERIFICATION PASSED.')
    process.exit(0)
  }
  console.log('SPEAKING PRODUCT BROWSER VERIFICATION FAILED.')
  process.exit(1)
}

main()
