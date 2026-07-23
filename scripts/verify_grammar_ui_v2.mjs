/** Frontend-only smoke checks for Grammar UI V2. */
import fs from 'node:fs'
import path from 'node:path'

const root = process.cwd()
const read = (p) => fs.readFileSync(path.join(root, p), 'utf8')

const home = read('src/views/student/grammar/StudentGrammarView.vue')
const comp = read('src/composables/useGrammarEngineHome.js')
const card = read('src/components/grammar-v2/GrammarStageCard.vue')
const roadmap = read('src/components/grammar-v2/GrammarCefrRoadmap.vue')
const topic = read('src/views/student/grammar/GrammarTopicView.vue')
const router = read('src/router/index.js')

const checks = [
  ['home GrammarHeroV2', home.includes('GrammarHeroV2')],
  ['home CefrRoadmap', home.includes('GrammarCefrRoadmap')],
  ['home EngineSidebar', home.includes('GrammarEngineSidebar')],
  ['home surfaces actionError', home.includes('actionError')],
  ['home passes anchor-cefr', home.includes(':anchor-cefr')],
  ['no LanguageModuleTabs on home', !home.includes('LanguageModuleTabs')],
  ['no GrammarLessonCard on home', !home.includes('GrammarLessonCard')],
  ['composable fetchLearningJourney', comp.includes('fetchLearningJourney')],
  ['composable startGrammarLesson', comp.includes('startGrammarLesson')],
  ['composable completeGrammarActivity', comp.includes('completeGrammarActivity')],
  ['composable getErrorMessage', comp.includes('getErrorMessage')],
  ['composable anchorCefr', comp.includes('anchorCefr')],
  ['composable no unlocked_ids invent', !comp.includes('unlocked_ids')],
  ['roadmap uses anchorCefr', roadmap.includes('anchorCefr')],
  ['roadmap overwrites openMap', roadmap.includes('delete openMap[key]')],
  ['topic surfaces actionError', topic.includes('actionError')],
  ['card interactive current', card.includes("status === 'current'")],
  ['card interactive completed', card.includes("status === 'completed'")],
  ['route grammar/review', router.includes("path: 'grammar/review'")],
  ['route grammar/complete', router.includes("path: 'grammar/complete'")],
  ['route grammar/topic', router.includes("path: 'grammar/topic/:grammarId'")],
  ['v2 components dir', fs.existsSync(path.join(root, 'src/components/grammar-v2'))],
]

let ok = true
for (const [name, passed] of checks) {
  console.log(`${passed ? 'PASS' : 'FAIL'} ${name}`)
  if (!passed) ok = false
}
process.exit(ok ? 0 : 1)
