/** Smoke checks for AI Grammar Session V3 — Phase P0 (frontend runtime only). */
import fs from 'node:fs'
import path from 'node:path'

const root = process.cwd()
const read = (p) => fs.readFileSync(path.join(root, p), 'utf8')
const exists = (p) => fs.existsSync(path.join(root, p))

const runtime = read('src/composables/useGrammarSessionRuntime.js')
const topic = read('src/views/student/grammar/GrammarTopicView.vue')
const shell = read('src/components/grammar-session-v3/GrammarSessionRuntime.vue')
const stages = read('src/constants/grammarSessionStages.js')

const components = [
  'src/components/ai-session/SessionHeader.vue',
  'src/components/ai-session/SessionTimeline.vue',
  'src/components/ai-session/SessionStageContainer.vue',
  'src/components/ai-session/SessionFooter.vue',
  'src/components/ai-session/StageProgress.vue',
  'src/components/ai-session/LessonProgress.vue',
  'src/components/ai-session/SessionControls.vue',
  'src/components/ai-session/EmptyTeacherPlaceholder.vue',
  'src/components/ai-session/StageTransition.vue',
]

const stageViews = [
  'WelcomeStage',
  'MissionStage',
  'LearnStage',
  'PracticeStage',
  'SpeakingStage',
  'WritingStage',
  'ReflectionStage',
  'CompleteStage',
]

const checks = [
  ['runtime stages list', stages.includes('WELCOME') && stages.includes('COMPLETE')],
  ['runtime sessionStorage', runtime.includes('sessionStorage')],
  ['runtime voice placeholders', runtime.includes('teacherVoiceState')],
  ['topic uses GrammarSessionRuntime', topic.includes('GrammarSessionRuntime')],
  ['topic does not use GrammarLessonDetail', !topic.includes('GrammarLessonDetail')],
  ['shell leave confirm', shell.includes('leaveConfirm') || shell.includes('onBeforeRouteLeave')],
  ['shell StageTransition', shell.includes('StageTransition')],
  ['en i18n grammarSession', read('src/locales/en/student.json').includes('"grammarSession"')],
  ['ar i18n grammarSession', read('src/locales/ar/student.json').includes('"grammarSession"')],
  ...components.map((p) => [`component ${path.basename(p)}`, exists(p)]),
  ...stageViews.map((name) => [
    `stage ${name}`,
    exists(`src/components/grammar-session-v3/stages/${name}.vue`),
  ]),
]

let ok = true
for (const [name, passed] of checks) {
  console.log(`${passed ? 'PASS' : 'FAIL'} ${name}`)
  if (!passed) ok = false
}
process.exit(ok ? 0 : 1)
