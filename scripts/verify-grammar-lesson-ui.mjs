import fs from 'node:fs'
import path from 'node:path'

const root = process.cwd()
const componentPath = path.join(root, 'src/components/grammar-lesson-v4/GrammarLessonPage.vue')
const routePath = path.join(root, 'src/views/student/grammar/GrammarTopicView.vue')
const previewPath = path.join(root, 'src/views/student/grammar/GrammarLessonPreviewView.vue')
const enginePath = path.join(root, 'src/composables/useGrammarEngineHome.js')
const sessionPath = path.join(root, 'src/composables/useGrammarLessonSession.js')
const apiPath = path.join(root, 'src/api/grammar.js')
const routerPath = path.join(root, 'src/router/index.js')
const chatDrawerPath = path.join(root, 'src/components/grammar-lesson-v4/GrammarLessonTutorChatDrawer.vue')
const source = fs.readFileSync(componentPath, 'utf8')
const routeSource = fs.readFileSync(routePath, 'utf8')
const previewSource = fs.readFileSync(previewPath, 'utf8')
const engineSource = fs.readFileSync(enginePath, 'utf8')
const sessionSource = fs.readFileSync(sessionPath, 'utf8')
const apiSource = fs.readFileSync(apiPath, 'utf8')
const routerSource = fs.readFileSync(routerPath, 'utf8')
const chatDrawerSource = fs.readFileSync(chatDrawerPath, 'utf8')

function assert(condition, message) {
  if (!condition) {
    throw new Error(message)
  }
}

const fiveAreas = [
  'افهم الفكرة',
  'شوف كيف تعمل',
  'القاعدة والأخطاء',
  'تدرّب خطوة بخطوة',
  'استخدمها بنفسك',
]
const visibleSectionAreas = fiveAreas.slice(0, 4)

for (const area of visibleSectionAreas) {
  assert(source.includes(area), `Missing five-part learner area: ${area}`)
}

const orderedMarkers = visibleSectionAreas.map((area) => source.indexOf(area))
assert(orderedMarkers.every((index) => index >= 0), 'One or more five-part areas are absent')
assert(
  orderedMarkers.every((index, position) => position === 0 || index > orderedMarkers[position - 1]),
  'Five-part learner areas are not in the approved order',
)
assert(
  source.includes("task.type === 'open_response'") && source.includes('sentence_count_min'),
  'The use-it-yourself production task must remain inside the practice sequence',
)

const requiredMarkers = [
  'student_content',
  'compactConceptBlocks',
  'modelExamples',
  'visibleExamples',
  'highlightTargetForm',
  'displayTargetForm',
  'targetFormCandidates',
  'TARGET_FORM_LABELS',
  'useCases',
  'patterns',
  'mistakes',
  'compactRuleBlocks',
  'visibleMistakes',
  'extraMistakes',
  'visualSummary',
  'practiceTasks',
  'activePracticeIndex',
  'activePracticeTask',
  'orderedPracticeTasks',
  'evaluateGrammarLessonPreviewPractice',
  'checkPracticeAnswer',
  'canCheckPractice',
  'practiceEvaluationRevisionId',
  'canonical_revision_id',
  'revisionIdFromLessonId',
  'canonical-([0-9a-f]{8}',
  'revision_id: practiceEvaluationRevisionId.value',
  'practiceResults',
  'GrammarLessonTutorChatDrawer',
  'tutorChatOpen',
  'openTutorForSection',
  'ask-part-button',
  'tutor-open-button',
  'practiceAttempts',
  'practiceCompleted',
  'activePracticeResult',
  'practice-feedback',
  'practice-summary',
  'task-type-chip',
  'round-title',
  'currentPracticeRoundTitle',
  'choice-dot',
  'choice-text',
  'mcq-card',
  'mcq-title',
  'mcq-instruction',
  'mcq-sentence',
  'isChoiceLikeTask',
  'choiceOptionValue',
  "role: 'radio'",
  "'aria-checked'",
  "dir: 'ltr', 'aria-labelledby'",
  'v-if="!isChoiceLikeTask(activePracticeTask)"',
  "task.type === 'multiple_choice'",
  "task.type === 'sentence_builder'",
  "task.type === 'transformation'",
  "task.type === 'short_answer'",
  "task.type === 'open_response'",
  'word_chips',
  'selected-token',
  'removeToken',
  'starter-chip',
  'sentence_count_min',
  'sentence_count_max',
  'recognitionTaskOptions',
  'ما الكلمة التي تتغير في الأمثلة حسب الفاعل؟',
  'تحقّق من الإجابة',
  'السؤال التالي',
  'إنهاء التدريب',
  "type: 'recognition'",
  'recognitionOptions',
  'previousPractice',
  'nextPractice',
  'useTasks',
  'activeUseIndex',
  'showReflection',
  "task.type === 'choice'",
  "task.type === 'fill_blank'",
  "task.type === 'reorder'",
  "task.type === 'correction'",
  'resetReorder',
  'dir="rtl"',
  'lang="ar"',
  'lang="en"',
  'aria-live="polite"',
  '@media (max-width: 720px)',
  '@media (prefers-reduced-motion: no-preference)',
  ':disabled="!canFinishLesson"',
  "@click=\"$emit('finish', grammarCompletionPayload())\"",
  'correctPracticeCount',
  'previewMode',
  'collapse-panel',
  'شرح أكثر',
  'أخطاء إضافية',
  'production-card',
  'Complete Lesson',
  'v-if="!hasCanonicalContent"',
  'Start Fresh Lesson',
  'hasCanonicalGrammarLessonContent',
  'retryMessage',
]

for (const marker of requiredMarkers) {
  assert(source.includes(marker), `Missing expected UI marker: ${marker}`)
}

const forbiddenMarkers = [
  'Meaning First',
  'Model Examples',
  'Notice the Grammar',
  'Noticing',
  'Explanation',
  'Form and Rules',
  'Arabic bridge',
  'Guided Practice',
  'Supported Production',
  'Transfer',
  'Exit Check',
  '<h2>Reflection</h2>',
  'Temporary Legacy View',
  'server_teaching_metadata',
  'expected_answer',
  'sample_answer',
  'success_criteria',
  'misconception',
  'feedback_reasoning',
  'similar_retry_prompt',
  'Correctness will require',
  'correct answer',
  'Incorrect answer',
]

for (const marker of forbiddenMarkers) {
  assert(!source.includes(marker), `Forbidden active UI marker found: ${marker}`)
}

assert(
  source.indexOf('compactConceptBlocks') < source.indexOf('visibleExamples'),
  'Arabic concept content should be wired before examples',
)
assert(
  source.indexOf('visibleExamples') < source.indexOf('compactRuleBlocks'),
  'Examples should be wired before rule breakdown',
)
assert(
  source.includes('activePracticeTask') && !source.includes('v-for="item in practiceTasks"'),
  'Practice must render one active task rather than all tasks',
)
assert(
  source.includes('responses[task.id]') && source.includes('previousPractice') && source.includes('previousUse'),
  'Responses must persist while moving between sequential tasks',
)
assert(
  routeSource.includes("../../../components/grammar-lesson-v4/GrammarLessonPage.vue"),
  'Active Grammar topic route is not using the canonical lesson page',
)
assert(
  routerSource.includes("path: 'grammar/lesson-preview'") &&
    routerSource.includes('GrammarLessonPreviewView.vue'),
  'Canonical Grammar preview route is not registered',
)
assert(
    previewSource.includes('fetchGrammarLessonPreview') &&
    previewSource.includes('GrammarLessonPage') &&
    previewSource.includes('preview-mode') &&
    previewSource.includes(':preview-revision-id="revisionId"') &&
    !previewSource.includes('startGrammarLesson') &&
    !previewSource.includes('completeGrammarActivity') &&
    !previewSource.includes('useGrammarLessonSession'),
  'Grammar preview view must load safely through the preview endpoint and avoid student session side effects',
)
assert(
  apiSource.includes('fetchGrammarLessonPreview') &&
    apiSource.includes("api.get('/student/grammar/lesson/preview'") &&
    apiSource.includes('evaluateGrammarLessonPreviewPractice') &&
    apiSource.includes("api.post('/student/grammar/lesson/preview/practice/evaluate'") &&
    apiSource.includes('createGrammarLessonPreviewChatSession') &&
    apiSource.includes('sendGrammarLessonPreviewChatMessage') &&
    apiSource.includes('/student/grammar/lesson/preview/chat/sessions') &&
    apiSource.includes('revision_id'),
  'Grammar preview API client is not wired',
)
assert(
  chatDrawerSource.includes('اسأل المعلّم') &&
    chatDrawerSource.includes('quickActions') &&
    chatDrawerSource.includes('sendGrammarLessonPreviewChatMessage') &&
    chatDrawerSource.includes('@keydown.ctrl.enter.prevent') &&
    chatDrawerSource.includes('grammar-chat__message') &&
    !chatDrawerSource.includes('input_tokens') &&
    !chatDrawerSource.includes('output_tokens') &&
    !chatDrawerSource.includes('private_provider_metadata') &&
    !chatDrawerSource.includes('server_teaching_metadata') &&
    !chatDrawerSource.includes('expected_answer'),
  'Grammar lesson tutor chat drawer is missing safe chat behavior markers',
)
assert(
  engineSource.includes('isStaleGrammarSessionError') &&
    engineSource.includes('session_not_found') &&
    engineSource.includes('activity session') &&
    engineSource.includes('clearLesson()') &&
    engineSource.includes('hasCanonicalGrammarLessonContent') &&
    engineSource.includes('ROUTES.STUDENT_GRAMMAR'),
  'Grammar engine home does not recover from stale activity sessions',
)
assert(
  sessionSource.includes('grammar_lesson_methodology_v2_arabic_first') &&
    sessionSource.includes('edumind.grammar.activeLesson.v2') &&
    sessionSource.includes('edumind.grammar.activeLesson.v1') &&
    sessionSource.includes('retry_required') &&
    sessionSource.includes('validExplainedExamples') &&
    sessionSource.includes('validRulesAndMistakes') &&
    sessionSource.includes('validPractice') &&
    sessionSource.includes('maxMistakeCount') &&
    sessionSource.includes('isGenericFiller'),
  'Grammar lesson session cache does not enforce current authored-content integrity',
)
assert(
  !source.includes('orientationText'),
  'The active lesson page must not render generic orientation above the Arabic concept explanation',
)

console.log('Grammar lesson UI verification passed')
