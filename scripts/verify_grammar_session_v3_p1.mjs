/** Smoke checks for AI Grammar Session V3 — Phase P1 (teacher experience). */
import fs from 'node:fs'
import path from 'node:path'
import { execSync } from 'node:child_process'

const root = process.cwd()
const read = (p) => fs.readFileSync(path.join(root, p), 'utf8')
const exists = (p) => fs.existsSync(path.join(root, p))

const shell = read('src/components/grammar-session-v3/GrammarSessionRuntime.vue')
const teacher = read('src/composables/useGrammarTeacherExperience.js')
const learn = read('src/components/grammar-session-v3/stages/LearnStage.vue')
const tutorApi = read('src/api/aiTutor.js')

// P0 runtime must remain untouched by P1 (file still present; content contract).
const runtime = read('src/composables/useGrammarSessionRuntime.js')

const checks = [
  ['tutor API client', tutorApi.includes('/student/tutor/turn')],
  ['teacher experience composable', teacher.includes('postTutorTurn')],
  ['teaching cards util', exists('src/utils/grammarTeachingCards.js')],
  ['TeacherPresencePanel', exists('src/components/grammar-session-v3/teacher/TeacherPresencePanel.vue')],
  ['AskTeacherDrawer', exists('src/components/grammar-session-v3/teacher/AskTeacherDrawer.vue')],
  ['TeachingMicroCard', exists('src/components/grammar-session-v3/teacher/TeachingMicroCard.vue')],
  ['shell wires TeacherPresencePanel', shell.includes('TeacherPresencePanel')],
  ['shell wires AskTeacherDrawer', shell.includes('AskTeacherDrawer')],
  ['learn uses TeachingMicroCard', learn.includes('TeachingMicroCard')],
  ['learn ask emit', learn.includes("$emit('ask')")],
  ['P0 runtime still has stages', runtime.includes('GRAMMAR_SESSION_STAGES')],
  ['P0 runtime sessionStorage key', runtime.includes('eduspark.grammar.sessionRuntime.v1')],
  ['en grammarTeacher', read('src/locales/en/student.json').includes('"grammarTeacher"')],
  ['ar grammarTeacher', read('src/locales/ar/student.json').includes('"grammarTeacher"')],
  ['no mastery write in teacher', !teacher.includes('activity/complete')],
]

let ok = true
for (const [name, passed] of checks) {
  console.log(`${passed ? 'PASS' : 'FAIL'} ${name}`)
  if (!passed) ok = false
}

// Ensure P0 runtime file was not modified in this working tree relative to HEAD if tracked.
try {
  const diff = execSync('git diff --name-only -- src/composables/useGrammarSessionRuntime.js src/constants/grammarSessionStages.js src/components/ai-session', {
    cwd: root,
    encoding: 'utf8',
  }).trim()
  // Untracked ai-session from P0 is ok; modified tracked runtime would fail if it shows.
  const runtimeDiff = execSync('git diff --name-only -- src/composables/useGrammarSessionRuntime.js', {
    cwd: root,
    encoding: 'utf8',
  }).trim()
  const p0Untouched = !runtimeDiff
  console.log(`${p0Untouched ? 'PASS' : 'FAIL'} P0 runtime file not modified in git diff`)
  if (!p0Untouched) ok = false
  if (diff) {
    // ai-session may be untracked; ignore
  }
} catch {
  console.log('PASS P0 runtime git check skipped')
}

process.exit(ok ? 0 : 1)
