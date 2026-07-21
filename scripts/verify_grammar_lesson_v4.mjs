/** Smoke checks for Grammar Lesson V4 (single-page). */
import fs from 'node:fs'
import path from 'node:path'

const root = process.cwd()
const read = (p) => fs.readFileSync(path.join(root, p), 'utf8')
const exists = (p) => fs.existsSync(path.join(root, p))

const topic = read('src/views/student/grammar/GrammarTopicView.vue')
const page = read('src/components/grammar-lesson-v4/GrammarLessonPage.vue')
const util = read('src/utils/grammarLessonV4Content.js')

const checks = [
  ['topic uses GrammarLessonPage', topic.includes('GrammarLessonPage')],
  ['topic does not use GrammarSessionRuntime', !topic.includes('GrammarSessionRuntime')],
  ['page has explanation section', page.includes('G4ExplanationSection')],
  ['page has examples section', page.includes('G4ExamplesSection')],
  ['page has ask section', page.includes('G4AskSection')],
  ['page has practice section', page.includes('G4PracticeSection')],
  ['page has summary section', page.includes('G4SummarySection')],
  ['no stage machine in page', !page.includes('WELCOME') && !page.includes('currentStage')],
  ['practice min 15', util.includes('minCount = 15')],
  ['off-topic guard', util.includes('isLikelyOffTopic')],
  ['composable exists', exists('src/composables/useGrammarLessonV4.js')],
  ['en grammarV4', read('src/locales/en/student.json').includes('"grammarV4"')],
  ['ar grammarV4', read('src/locales/ar/student.json').includes('"grammarV4"')],
]

let ok = true
for (const [name, passed] of checks) {
  console.log(`${passed ? 'PASS' : 'FAIL'} ${name}`)
  if (!passed) ok = false
}
process.exit(ok ? 0 : 1)
