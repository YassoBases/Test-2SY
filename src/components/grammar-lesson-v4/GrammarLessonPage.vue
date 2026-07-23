<template>
  <article class="grammar-lesson" aria-labelledby="grammar-lesson-title">
    <header class="lesson-header">
      <AppButton variant="ghost" prepend-icon="mdi-arrow-left" @click="$emit('back')">
        Back to Grammar
      </AppButton>

      <div class="lesson-header__main">
        <h1 id="grammar-lesson-title" class="lesson-header__title" dir="ltr" lang="en">
          {{ displayName }}
        </h1>
        <span v-if="resolvedCefr" class="meta-chip">{{ resolvedCefr }}</span>
        <p v-if="lessonGoal" class="lesson-header__goal" :dir="textDir(lessonGoal)">
          {{ lessonGoal }}
        </p>
        <button
          v-if="chatAvailable"
          type="button"
          class="tutor-open-button"
          @click="openTutorForSection('lesson', 'الدرس كامل', lessonGoal || displayName)"
        >
          اسأل المعلّم
        </button>
      </div>
    </header>

    <section v-if="!hasCanonicalContent" class="lesson-part lesson-part--refresh">
      <h2 dir="rtl" lang="ar">ابدأ الدرس من جديد</h2>
      <p dir="rtl" lang="ar">{{ retryMessage }}</p>
      <AppButton variant="primary" prepend-icon="mdi-refresh" @click="$emit('retry')">
        Start Fresh Lesson
      </AppButton>
    </section>

    <template v-else>
      <section class="lesson-part lesson-part--concept" aria-labelledby="part-concept">
        <p class="part-number">1</p>
        <h2 id="part-concept" dir="rtl" lang="ar">افهم الفكرة</h2>

        <button
          v-if="chatAvailable"
          type="button"
          class="ask-part-button"
          @click="openTutorForSection('concept', 'افهم الفكرة', compactConceptBlocks.join(' '))"
        >
          اسأل عن هالجزء
        </button>

        <div class="concept-surface" dir="rtl" lang="ar">
          <p
            v-for="(block, index) in compactConceptBlocks"
            :key="`compact-concept-${index}`"
            class="concept-copy"
          >
            {{ block }}
          </p>

          <div v-if="conceptComparison" class="comparison-card">
            <p dir="rtl" lang="ar">{{ conceptComparison.arabic }}</p>
            <p dir="ltr" lang="en" v-html="conceptComparison.english" />
          </div>

          <p v-if="compactWhyEnglish" class="concept-soft">
            {{ compactWhyEnglish }}
          </p>

          <aside v-if="compactTakeaway" class="takeaway-box">
            <strong>{{ compactTakeaway.title }}</strong>
            <p>{{ compactTakeaway.text }}</p>
          </aside>

          <details v-if="expandedConceptBlocks.length" class="collapse-panel">
            <summary>شرح أكثر</summary>
            <div class="collapse-body">
              <p
                v-for="(block, index) in expandedConceptBlocks"
                :key="`expanded-concept-${index}`"
                :dir="block.dir"
                :lang="block.dir === 'rtl' ? 'ar' : 'en'"
              >
                {{ block.text }}
              </p>
            </div>
          </details>
        </div>
      </section>

      <section v-if="visibleExamples.length || useCases.length" class="lesson-part" aria-labelledby="part-examples">
        <p class="part-number">2</p>
        <h2 id="part-examples" dir="rtl" lang="ar">شوف كيف تعمل</h2>

        <button
          v-if="chatAvailable"
          type="button"
          class="ask-part-button"
          @click="openTutorForSection('examples', 'شوف كيف تعمل', examplesContextText)"
        >
          اسأل عن هالجزء
        </button>

        <div v-if="visibleExamples.length" class="example-grid">
          <article
            v-for="example in visibleExamples"
            :key="example.id || example.sentence"
            class="example-card"
            :class="{ 'example-line--contrast': isContrastExample(example) }"
          >
            <span v-if="example.label" class="example-kind" dir="rtl" lang="ar">{{ example.label }}</span>
            <p class="example-sentence" dir="ltr" lang="en" v-html="highlightTargetForm(example)" />
            <p v-if="example.arabic_meaning" class="example-meaning" dir="rtl" lang="ar">
              {{ shortText(example.arabic_meaning, 80) }}
            </p>
            <p v-if="example.arabic_explanation" class="example-explain" dir="rtl" lang="ar">
              {{ shortText(example.arabic_explanation, 120) }}
            </p>
          </article>
        </div>

        <details v-if="useCases.length" class="collapse-panel">
          <summary>أمثلة إضافية</summary>
          <div class="use-case-flow">
            <article v-for="item in useCases" :key="item.id || item.label" class="use-case-line">
              <h3 :dir="textDir(item.label)" :lang="textDir(item.label) === 'rtl' ? 'ar' : 'en'">
                {{ item.label }}
              </h3>
              <p v-if="item.explanation" :dir="textDir(item.explanation)">
                {{ item.explanation }}
              </p>
              <p v-if="item.example" class="use-case-example" dir="ltr" lang="en">
                {{ item.example }}
              </p>
              <p v-if="item.arabic_explanation" class="use-case-arabic" dir="rtl" lang="ar">
                {{ item.arabic_explanation }}
              </p>
            </article>
          </div>
        </details>
      </section>

      <section v-if="hasRuleArea" class="lesson-part" aria-labelledby="part-rules">
        <p class="part-number">3</p>
        <h2 id="part-rules" dir="rtl" lang="ar">القاعدة والأخطاء</h2>

        <button
          v-if="chatAvailable"
          type="button"
          class="ask-part-button"
          @click="openTutorForSection('rules', 'القاعدة والأخطاء', rulesContextText)"
        >
          اسأل عن هالجزء
        </button>

        <div v-if="compactRuleBlocks.length" class="rule-card-grid">
          <article v-for="item in compactRuleBlocks" :key="item.id" class="rule-card">
            <p class="rule-symbol" dir="ltr" lang="en" v-html="item.symbol" />
            <p class="rule-explain" dir="rtl" lang="ar">{{ item.explain }}</p>
          </article>
        </div>

        <div v-if="visibleMistakes.length" class="mistake-flow mistake-flow--compact">
          <article v-for="item in visibleMistakes" :key="item.id || item.incorrect" class="mistake-card">
            <div class="mistake-pair">
              <p class="mistake-wrong" dir="ltr" lang="en">✕ {{ item.incorrect }}</p>
              <p class="mistake-right" dir="ltr" lang="en">✓ {{ item.correct }}</p>
            </div>
            <p v-if="item.why" class="mistake-reason" :dir="textDir(item.why)">
              {{ shortText(item.why, 120) }}
            </p>
          </article>
        </div>

        <details v-if="extraMistakes.length || patterns.length || ruleNotes.length || visualSummary.length" class="collapse-panel">
          <summary>أخطاء إضافية</summary>

          <div v-if="extraMistakes.length" class="mistake-flow">
            <article v-for="item in extraMistakes" :key="item.id || item.incorrect" class="mistake-line">
              <div class="mistake-pair">
                <p class="mistake-wrong" dir="ltr" lang="en">✕ {{ item.incorrect }}</p>
                <p class="mistake-right" dir="ltr" lang="en">✓ {{ item.correct }}</p>
              </div>
              <p v-if="item.why" class="mistake-reason" :dir="textDir(item.why)">
                {{ shortText(item.why, 140) }}
              </p>
            </article>
          </div>

          <div v-if="visualSummary.length" class="quick-summary" aria-label="Quick summary">
            <div v-for="item in visualSummary" :key="`${item.label}-${item.value}`" class="summary-item">
              <span :dir="textDir(item.label)">{{ item.label }}</span>
              <strong dir="ltr" lang="en">{{ item.value }}</strong>
              <small v-if="item.warning" :dir="textDir(item.warning)">{{ item.warning }}</small>
            </div>
          </div>
        </details>
      </section>

      <section v-if="practiceTasks.length" class="lesson-part lesson-part--interactive" aria-labelledby="part-practice">
        <p class="part-number">4</p>
        <h2 id="part-practice" dir="rtl" lang="ar">تدرّب خطوة بخطوة</h2>

        <button
          v-if="chatAvailable"
          type="button"
          class="ask-part-button"
          @click="openTutorForSection('practice', 'تدرّب خطوة بخطوة', practiceContextText)"
        >
          اسأل عن هالجزء
        </button>

        <div v-if="!practiceCompleted" class="practice-shell" dir="rtl" lang="ar">
          <div class="step-meta" aria-live="polite">
            <span>السؤال {{ activePracticeIndex + 1 }} من {{ practiceTasks.length }}</span>
            <div class="progress-track" aria-hidden="true">
              <span :style="{ width: practiceProgress }" />
            </div>
          </div>

          <p v-if="!isChoiceLikeTask(activePracticeTask)" class="round-title">{{ currentPracticeRoundTitle }}</p>
          <span v-if="!isChoiceLikeTask(activePracticeTask)" class="task-type-chip">{{ practiceTypeLabel(activePracticeTask) }}</span>

          <LessonTask
            :task="activePracticeTask"
            :responses="responses"
            :disabled="isPracticeResolved(activePracticeTask)"
            @select-token="selectToken"
            @remove-token="removeToken"
            @reset-reorder="resetReorder"
          />

          <div
            v-if="activePracticeResult"
            class="practice-feedback"
            :class="{ 'practice-feedback--correct': activePracticeResult.correct }"
            role="status"
          >
            <p>{{ activePracticeResult.feedback }}</p>
            <p v-if="activePracticeResult.hint" class="practice-hint">{{ activePracticeResult.hint }}</p>
          </div>

          <p v-if="practiceError" class="practice-error">{{ practiceError }}</p>

          <div class="step-actions">
            <button
              type="button"
              class="primary-button"
              :disabled="!canCheckPractice"
              @click="checkPracticeAnswer"
            >
              {{ evaluatingPractice ? 'جار التحقق...' : 'تحقّق من الإجابة' }}
            </button>
            <button
              v-if="activePracticeResult?.may_continue"
              type="button"
              class="text-button"
              @click="nextPractice"
            >
              {{ activePracticeIndex === practiceTasks.length - 1 ? 'إنهاء التدريب' : 'السؤال التالي' }}
            </button>
          </div>
        </div>

        <div v-else class="practice-summary" dir="rtl" lang="ar">
          <strong>أنهيت التدريب القصير.</strong>
          <p>صحيح من أول محاولة: {{ firstTryCorrectCount }} من {{ allGrammarTasks.length }}.</p>
          <p>احتاج مساعدة: {{ helpedPracticeCount }}.</p>
          <p>تابع الآن واستخدم الجمل عن نفسك بهدوء.</p>
          <button type="button" class="primary-button" @click="activePracticeIndex = Math.max(0, practiceTasks.length - 1); practiceCompleted = false">
            راجع السؤال الأخير
          </button>
        </div>
      </section>
    </template>

    <section v-if="chatAvailable" class="lesson-tutor-cta" dir="rtl" lang="ar">
      <div>
        <strong>محتاج توضيح؟</strong>
        <p>اسأل المعلّم عن أي نقطة بالدرس، وبيشرحها بصوت ونص.</p>
      </div>
      <button
        type="button"
        class="tutor-open-button tutor-open-button--bottom"
        @click="openTutorForSection('lesson', 'الدرس كامل', lessonGoal || displayName)"
      >
        اسأل المعلّم
      </button>
    </section>

    <footer v-if="hasCanonicalContent" class="lesson-completion">
      <p v-if="previewMode" class="completion-copy" dir="rtl" lang="ar">
        هذه معاينة محلية للمراجعة فقط. لا يتم حفظ أي تقدم أو إرسال إجابات.
      </p>
      <p v-else-if="false" class="completion-copy" dir="rtl" lang="ar">
        عند الانتهاء من القراءة والردود الظاهرة، يمكنك إنهاء الدرس.
      </p>
      <p v-else class="completion-copy" dir="rtl" lang="ar">
        {{ completionCopy }}
      </p>
      <AppButton
        v-if="!previewMode"
        variant="primary"
        prepend-icon="mdi-check-circle-outline"
        :loading="finishing"
        :disabled="!canFinishLesson"
        @click="$emit('finish', grammarCompletionPayload())"
      >
        Complete Lesson
      </AppButton>
    </footer>

    <GrammarLessonTutorChatDrawer
      v-if="chatAvailable"
      :open="tutorChatOpen"
      :revision-id="practiceEvaluationRevisionId"
      :context="tutorChatContext"
      :preview-mode="previewMode"
      @close="tutorChatOpen = false"
    />

    <button
      v-if="chatAvailable && !tutorChatOpen"
      type="button"
      class="tutor-floating-button"
      aria-label="اسأل المعلّم عن الدرس"
      @click="openTutorForSection('lesson', 'الدرس كامل', lessonGoal || displayName)"
    >
      <span aria-hidden="true">؟</span>
      اسأل المعلّم
    </button>
  </article>
</template>

<script setup>
import { computed, defineComponent, h, reactive, ref } from 'vue'
import AppButton from '../ui/AppButton.vue'
import GrammarLessonTutorChatDrawer from './GrammarLessonTutorChatDrawer.vue'
import {
  CURRENT_GRAMMAR_METHODOLOGY_VERSION,
  hasCanonicalGrammarLessonContent,
} from '../../composables/useGrammarLessonSession'
import {
  evaluateGrammarLessonPractice,
  evaluateGrammarLessonPreviewPractice,
} from '../../api/grammar.js'

const props = defineProps({
  lesson: { type: Object, required: true },
  cefr: { type: String, default: '' },
  finishing: { type: Boolean, default: false },
  previewMode: { type: Boolean, default: false },
  previewRevisionId: { type: String, default: '' },
})

defineEmits(['back', 'finish', 'retry'])

const responses = reactive({})
const practiceResults = reactive({})
const practiceAttempts = reactive({})
const practiceFirstTryCorrect = reactive({})
const practiceHelpNeeded = reactive({})
const activePracticeIndex = ref(0)
const activeUseIndex = ref(0)
const evaluatingPractice = ref(false)
const practiceCompleted = ref(false)
const practiceError = ref('')
const tutorChatOpen = ref(false)
const tutorChatContext = ref(null)

const TARGET_FORM_LABELS = {
  affirmative_am: 'am',
  affirmative_is: 'is',
  affirmative_are: 'are',
  negative_am_not: 'am not',
  negative_is_not: "is not / isn't",
  negative_are_not: "are not / aren't",
  question_am: 'Am I ...?',
  question_is: 'Is he/she/it ...?',
  question_are: 'Are you/we/they ...?',
  short_answer_am: "Yes, I am. / No, I'm not.",
  short_answer_is: "Yes, she is. / No, she isn't.",
  short_answer_are: "Yes, they are. / No, they aren't.",
}

const TARGET_FORM_HIGHLIGHTS = {
  affirmative_am: ['am'],
  affirmative_is: ['is'],
  affirmative_are: ['are'],
  negative_am_not: ['are not', 'is not', "aren't", "isn't", 'am not'],
  negative_is_not: ["isn't", 'is not'],
  negative_are_not: ["aren't", 'are not'],
  question_am: ['Am'],
  question_is: ['Is'],
  question_are: ['Are'],
  short_answer_am: ["I'm not", 'am'],
  short_answer_is: ["isn't", 'is'],
  short_answer_are: ["aren't", 'are'],
}

const BE_CONCEPT_INTRO = [
  'بالعربي نستطيع أن نقول: «أنا طالب» بدون فعل ظاهر بين «أنا» و«طالب». لكن بالإنجليزي لا تكفي جملة I student، لأن الجملة تحتاج كلمة تربط الشخص بالاسم أو الصفة أو المكان.',
  'هذه الكلمة هي فعل be. في الحاضر يظهر بثلاثة أشكال: am مع I، و is مع he/she/it، و are مع you/we/they.',
  'فكّر فيها كجسر صغير: تختار الشكل المناسب للفاعل، ثم تقول من الشخص، أين هو، أو كيف يشعر. لذلك ابدأ بسؤال واحد: من هو الفاعل؟ بعدها اختر am أو is أو are.',
]

function parseMaybeJson(value) {
  if (!value || typeof value !== 'string') return value
  try {
    return JSON.parse(value)
  } catch {
    return null
  }
}

function hasRenderablePreviewContent(lesson) {
  const raw = lesson?.student_content
  const previewContent = raw && typeof raw === 'object' ? raw : parseMaybeJson(raw)
  const required = [
    'orientation',
    'meaning_hook',
    'model_examples',
    'noticing',
    'concept_explanation',
    'form_and_rules',
    'arabic_clarification',
    'contrasts_and_mistakes',
    'understanding_checks',
    'guided_practice',
    'supported_production',
    'transfer',
    'exit_check',
    'reflection',
  ]
  return !!(
    lesson?.methodology_version === CURRENT_GRAMMAR_METHODOLOGY_VERSION &&
    lesson?.authoring_status === 'ready' &&
    previewContent &&
    typeof previewContent === 'object' &&
    required.every((key) => previewContent[key] !== undefined && previewContent[key] !== null)
  )
}

const content = computed(() => {
  const raw = props.lesson?.student_content
  if (raw && typeof raw === 'object') return raw
  const parsed = parseMaybeJson(raw)
  return parsed && typeof parsed === 'object' ? parsed : {}
})

const hasCanonicalContent = computed(() =>
  props.previewMode ? hasRenderablePreviewContent(props.lesson) : hasCanonicalGrammarLessonContent(props.lesson),
)
const displayName = computed(
  () =>
    cleanDisplayName(props.lesson.display_name) ||
    cleanDisplayName(props.lesson.lesson_title) ||
    formatGrammarName(props.lesson.grammar_target || props.lesson.grammar_id) ||
    'Grammar Lesson',
)
const resolvedCefr = computed(() => props.lesson.cefr_level || props.cefr || '')
const retryMessage = computed(
  () =>
    props.lesson.retry_message ||
    'تعذّر تجهيز الدرس بالشكل المطلوب. حاول إنشاء الدرس مرة أخرى.',
)
const lessonGoal = computed(() =>
  hasCanonicalContent.value ? 'فكرة قصيرة، مثال واضح، ثم تدريب سريع.' : '',
)
const modelExamples = computed(() => arrayOf(content.value?.model_examples))
const conceptArabicBlocks = computed(() => {
  const explanation = conceptBlocks(content.value?.concept_explanation)
  const arabic = content.value?.arabic_clarification?.arabic
  return [
    ...explanation,
    ...(arabic ? [{ text: String(arabic), dir: textDir(arabic) }] : []),
  ].filter((block, index, list) => block.text && list.findIndex((item) => item.text === block.text) === index)
})
const compactConceptBlocks = computed(() => (isPresentBeLesson.value ? BE_CONCEPT_INTRO : conceptArabicBlocks.value.slice(0, 3).map((item) => shortText(item.text, 180))))
const expandedConceptBlocks = computed(() => conceptArabicBlocks.value)
const conceptComparison = computed(() =>
  isPresentBeLesson.value
    ? {
        arabic: 'أنا طالب',
        english: 'I <mark>am</mark> a student.',
      }
    : null,
)
const compactWhyEnglish = computed(() =>
  isPresentBeLesson.value
    ? 'الإنجليزية تحتاج am/is/are لأن الفاعل لا يقف وحده مع اسم أو صفة أو مكان.'
    : shortText(content.value?.meaning_hook?.why_it_matters || '', 160),
)
const compactTakeaway = computed(() =>
  isPresentBeLesson.value
    ? {
        title: 'الخلاصة',
        text: 'لا تقل I student. قل: I am a student.',
      }
    : null,
)
const patterns = computed(() => arrayOf(content.value?.form_and_rules?.patterns))
const ruleNotes = computed(() => arrayOf(content.value?.form_and_rules?.rule_notes))
const useCases = computed(() => arrayOf(content.value?.form_and_rules?.use_cases))
const visualSummary = computed(() => arrayOf(content.value?.form_and_rules?.visual_summary))
const mistakes = computed(() => arrayOf(content.value?.contrasts_and_mistakes))
const hasRuleArea = computed(
  () =>
    compactRuleBlocks.value.length ||
    mistakes.value.length ||
    visualSummary.value.length ||
    !!content.value?.arabic_clarification?.arabic_english_contrast,
)
const compactRuleBlocks = computed(() => {
  if (isPresentBeLesson.value) {
    return [
      { id: 'rule_am', symbol: 'I → <mark>am</mark>', explain: 'مع I نستخدم am فقط.' },
      { id: 'rule_is', symbol: 'He / She / It → <mark>is</mark>', explain: 'مع المفرد الغائب نستخدم is.' },
      { id: 'rule_are', symbol: 'You / We / They → <mark>are</mark>', explain: 'مع you/we/they نستخدم are.' },
      { id: 'rule_not', symbol: 'be + <mark>not</mark>', explain: 'للنفي نضع not بعد am/is/are.' },
      { id: 'rule_question', symbol: '<mark>Is</mark> he ready?', explain: 'في السؤال نضع am/is/are قبل الفاعل.' },
      { id: 'rule_short_answer', symbol: 'Yes, he <mark>is</mark>.', explain: 'في الجواب القصير نكرر الشكل الصحيح.' },
    ]
  }
  return patterns.value.slice(0, 4).map((pattern, index) => ({
    id: pattern.id || `pattern_${index}`,
    symbol: escapeHtml(pattern.pattern || pattern.example || ''),
    explain: shortText(pattern.explanation || pattern.meaning || '', 120),
  }))
})
const visibleMistakes = computed(() => {
  if (isPresentBeLesson.value) {
    return [
      {
        id: 'compact_delete_be',
        incorrect: 'I student.',
        correct: 'I am a student.',
        why: 'في العربية يمكن أن نحذف فعل الربط، لكن الإنجليزية تحتاج am.',
      },
      {
        id: 'compact_agreement',
        incorrect: 'She are tired.',
        correct: 'She is tired.',
        why: 'She تأخذ is، وليس are.',
      },
      {
        id: 'compact_do_be',
        incorrect: 'Do you are ready?',
        correct: 'Are you ready?',
        why: 'مع be لا نستخدم do؛ نبدأ السؤال بـ are.',
      },
    ]
  }
  return mistakes.value.slice(0, 3)
})
const extraMistakes = computed(() => {
  if (isPresentBeLesson.value) {
    return mistakes.value.filter((item) => ['mistake_3', 'mistake_4', 'mistake_6'].includes(String(item.id || '')))
  }
  return mistakes.value.slice(3)
})
const visibleExamples = computed(() => {
  if (!isPresentBeLesson.value) return modelExamples.value.slice(0, 4)
  const affirmative = modelExamples.value[0] || {}
  const negative = modelExamples.value[1] || {}
  return [
    {
      ...affirmative,
      label: 'إثبات',
      sentence: 'She is a nurse.',
      target_form: 'affirmative_is',
      arabic_meaning: affirmative.arabic_meaning || 'هي ممرضة.',
      arabic_explanation: 'استخدمنا is لأن الفاعل she.',
    },
    {
      ...negative,
      label: 'نفي',
      sentence: 'We are not late.',
      target_form: 'negative_are_not',
      arabic_meaning: negative.arabic_meaning || 'نحن لسنا متأخرين.',
      arabic_explanation: 'استخدمنا are مع we، ثم أضفنا not للنفي.',
    },
    {
      id: 'ex_question_split',
      label: 'سؤال',
      sentence: 'Is he ready?',
      target_form: 'question_is',
      arabic_meaning: 'هل هو جاهز؟',
      arabic_explanation: 'بدأنا بـ is قبل he لأننا نسأل.',
    },
    {
      id: 'ex_answer_split',
      label: 'جواب قصير',
      sentence: 'Yes, he is.',
      target_form: 'short_answer_is',
      arabic_meaning: 'نعم، هو جاهز.',
      arabic_explanation: 'في الجواب القصير نكرر is مع he.',
    },
  ]
})
const examplesContextText = computed(() =>
  visibleExamples.value.map((item) => `${item.sentence || ''} ${item.arabic_explanation || ''}`.trim()).join(' / '),
)
const rulesContextText = computed(() =>
  [
    ...compactRuleBlocks.value.map((item) => `${stripHtml(item.symbol)}: ${item.explain}`),
    ...visibleMistakes.value.map((item) => `${item.incorrect} -> ${item.correct}. ${item.why || ''}`),
  ].join(' / '),
)
const allGrammarTasks = computed(() => orderedPracticeTasks())
const practiceTasks = computed(() => allGrammarTasks.value)
const activePracticeTask = computed(() => practiceTasks.value[activePracticeIndex.value] || null)
const practiceContextText = computed(() => {
  const task = activePracticeTask.value || {}
  return [task.prompt, task.context, task.sentence_with_blank, task.incorrect_sentence].filter(Boolean).join(' ')
})
const practiceProgress = computed(() => `${((activePracticeIndex.value + 1) / Math.max(practiceTasks.value.length, 1)) * 100}%`)
const activePracticeResult = computed(() => {
  const id = activePracticeTask.value?.id
  return id ? practiceResults[id] || null : null
})
const correctPracticeCount = computed(() => allGrammarTasks.value.filter((task) => practiceResults[task.id]?.correct).length)
const canFinishLesson = computed(() => (
  allGrammarTasks.value.length >= 14 &&
  correctPracticeCount.value === allGrammarTasks.value.length
))
const completionCopy = computed(() => {
  if (canFinishLesson.value) {
    return 'كل تمارين القواعد محلولة صح. فيك تنهي الدرس وتنتقل لتطبيق القاعدة بالمهارات.'
  }
  return `حل كل تمارين القواعد صح قبل الإنهاء: ${correctPracticeCount.value} من ${allGrammarTasks.value.length}.`
})
const currentPracticeRoundTitle = computed(() => activePracticeTask.value?.round_title || 'تدرّب')
const practiceEvaluationRevisionId = computed(() => String(
  props.previewRevisionId ||
    props.lesson?.revision_id ||
    props.lesson?.canonical_revision_id ||
    revisionIdFromLessonId(props.lesson?.lesson_id) ||
    '',
).trim())
const chatAvailable = computed(() => hasCanonicalContent.value && !!practiceEvaluationRevisionId.value)
const canCheckPractice = computed(() => (
  !!activePracticeTask.value &&
  !!practiceEvaluationRevisionId.value &&
  !evaluatingPractice.value &&
  !isPracticeResolved(activePracticeTask.value) &&
  hasResponse(activePracticeTask.value)
))
const firstTryCorrectCount = computed(() => practiceTasks.value.filter((task) => practiceFirstTryCorrect[task.id]).length)
const helpedPracticeCount = computed(() => practiceTasks.value.filter((task) => practiceHelpNeeded[task.id]).length)
const exitProductionTask = computed(() => content.value?.exit_check?.production || null)
const useTasks = computed(() => [
  ...arrayOf(content.value?.supported_production),
  ...(content.value?.transfer ? [content.value.transfer] : []),
  ...(exitProductionTask.value ? [exitProductionTask.value] : []),
])
const activeUseTask = computed(() => useTasks.value[activeUseIndex.value] || null)
const useProgress = computed(() => `${((activeUseIndex.value + 1) / Math.max(useTasks.value.length, 1)) * 100}%`)
const hasReflection = computed(() => {
  const r = content.value?.reflection || {}
  return !!(r.summary || r.next_step || r.next_focus || r.encouragement)
})
const showReflection = computed(() => false && hasReflection.value && (!useTasks.value.length || activeUseIndex.value >= useTasks.value.length || allTasksAnswered(useTasks.value)))
const isPresentBeLesson = computed(() => String(props.lesson?.grammar_id || props.lesson?.grammar_target || '').trim() === 'gram_be_present')
const targetForms = computed(() => {
  const forms = new Set()
  for (const example of modelExamples.value) {
    const label = displayTargetForm(example.target_form)
    if (label) forms.add(label)
  }
  for (const pattern of patterns.value) {
    if (pattern.pattern) forms.add(String(pattern.pattern))
  }
  return Array.from(forms).slice(0, 6)
})

function arrayOf(value) {
  if (Array.isArray(value)) return value.filter(Boolean)
  if (typeof value === 'string') {
    const parsed = parseListString(value)
    if (Array.isArray(parsed)) return parsed.filter(Boolean)
  }
  return []
}

function parseListString(value) {
  const text = String(value || '').trim()
  if (!text.startsWith('[') || !text.endsWith(']')) return null
  const parsed = parseMaybeJson(text) || parseMaybeJson(text.replace(/'/g, '"'))
  return Array.isArray(parsed) ? parsed : null
}

function orderedPracticeTasks() {
  const available = [
    ...arrayOf(content.value?.understanding_checks),
    ...arrayOf(content.value?.guided_practice),
  ]
  if (available.some((item) => isRichPracticeType(item?.type))) {
    return available
  }
  const tasks = []
  const noticing = content.value?.noticing
  if (noticing?.id) {
    tasks.push({
      ...noticing,
      type: 'recognition',
      prompt: recognitionPrompt(noticing),
      options: recognitionTaskOptions(noticing),
    })
  }

  for (const type of ['choice', 'fill_blank', 'reorder', 'correction']) {
    const task = available.find((item) => item?.type === type && !tasks.some((selected) => selected.id === item.id))
    if (task) tasks.push(task)
  }
  return tasks.slice(0, 5)
}

function isRichPracticeType(type) {
  return ['multiple_choice', 'sentence_builder', 'transformation', 'short_answer', 'open_response'].includes(String(type || ''))
}

function isChoiceLikeTask(task) {
  return ['choice', 'multiple_choice', 'recognition'].includes(String(task?.type || ''))
}

function conceptBlocks(value) {
  if (Array.isArray(value)) {
    return value.filter(Boolean).map((text) => ({ text: String(text), dir: textDir(text) }))
  }
  if (value && typeof value === 'object') {
    return [
      value.arabic_concept_intro,
      value.arabic_concept_introduction,
      value.english_bridge,
      value.summary,
      value.text,
    ]
      .filter(Boolean)
      .map((text) => ({ text: String(text), dir: textDir(text) }))
  }
  return value ? [{ text: String(value), dir: textDir(value) }] : []
}

function textDir(value) {
  return /[\u0600-\u06ff]/.test(String(value || '')) ? 'rtl' : 'ltr'
}

function cleanDisplayName(value) {
  const text = String(value || '').trim()
  if (!text || /^gram_/i.test(text) || /^speaking:\s*gram_/i.test(text)) return ''
  return text
}

function formatGrammarName(value) {
  const text = String(value || '').trim().replace(/^gram_/i, '')
  if (!text) return ''
  return text
    .split(/[_\s-]+/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ')
}

function fieldId(id) {
  return `grammar-field-${String(id || 'item').replace(/[^a-zA-Z0-9_-]/g, '-')}`
}

function revisionIdFromLessonId(value) {
  const match = String(value || '').match(/^canonical-([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$/i)
  return match?.[1] || ''
}

function isContrastExample(example) {
  const text = `${example?.teaching_purpose || ''} ${example?.sentence || ''}`.toLowerCase()
  return text.includes('mistake') || text.includes('contrast') || text.includes("don't")
}

function purposeLabel(example) {
  const purpose = String(example?.teaching_purpose || '').toLowerCase()
  if (purpose.includes('contrast') || purpose.includes('mistake')) return 'لاحظ الفرق في هذا المثال.'
  if (purpose.includes('form')) return 'هذا المثال يوضح شكل القاعدة.'
  if (purpose.includes('meaning')) return 'هذا المثال يوضح المعنى.'
  return ''
}

function shortText(value, maxLength = 140) {
  const text = String(value || '').replace(/\s+/g, ' ').trim()
  if (text.length <= maxLength) return text
  return `${text.slice(0, maxLength).trim()}…`
}

function cleanOptionalText(value) {
  const text = String(value || '').trim()
  if (!text || /^none$/i.test(text) || /^null$/i.test(text)) return ''
  return text
}

function escapeHtml(value) {
  return String(value || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

function stripHtml(value) {
  return String(value || '').replace(/<[^>]*>/g, '').replace(/\s+/g, ' ').trim()
}

function openTutorForSection(sectionKey, title, text) {
  tutorChatContext.value = {
    section_key: sectionKey,
    title,
    text: shortText(text, 240),
  }
  tutorChatOpen.value = true
}

function displayTargetForm(value) {
  const key = String(value || '').trim()
  if (!key) return ''
  if (TARGET_FORM_LABELS[key]) return TARGET_FORM_LABELS[key]
  if (/^[a-z0-9]+(?:_[a-z0-9]+)+$/i.test(key)) return ''
  return key
}

function targetFormCandidates(value) {
  const key = String(value || '').trim()
  if (!key) return []
  if (TARGET_FORM_HIGHLIGHTS[key]) return TARGET_FORM_HIGHLIGHTS[key]
  if (/^[a-z0-9]+(?:_[a-z0-9]+)+$/i.test(key)) return []
  if (key.length > 40 || /[+()]/.test(key)) return []
  return [key]
}

function highlightTargetForm(example) {
  const sentence = escapeHtml(example?.sentence)
  for (const form of targetFormCandidates(example?.target_form)) {
    const escapedForm = escapeHtml(form)
    const index = sentence.toLowerCase().indexOf(escapedForm.toLowerCase())
    if (index >= 0) {
      return `${sentence.slice(0, index)}<mark>${sentence.slice(index, index + escapedForm.length)}</mark>${sentence.slice(index + escapedForm.length)}`
    }
  }
  return sentence
}

function selectToken(taskId, token) {
  const current = Array.isArray(responses[taskId]) ? responses[taskId] : []
  const next = current.includes(token)
    ? current.filter((item) => item !== token)
    : [...current, token]
  responses[taskId] = next
}

function resetReorder(taskId) {
  responses[taskId] = []
}

function removeToken(taskId, index) {
  const current = Array.isArray(responses[taskId]) ? responses[taskId] : []
  responses[taskId] = current.filter((_, itemIndex) => itemIndex !== index)
}

function hasResponse(task) {
  if (!task?.id) return false
  const value = responses[task.id]
  if (Array.isArray(value)) return value.length > 0
  return String(value || '').trim().length > 0
}

function isPracticeResolved(task) {
  if (!task?.id) return false
  return !!practiceResults[task.id]?.may_continue
}

function practiceTypeLabel(task) {
  const labels = {
    recognition: 'لاحظ القاعدة',
    choice: 'اختيار',
    multiple_choice: 'اختيار',
    fill_blank: 'املأ الفراغ',
    reorder: 'رتّب الكلمات',
    sentence_builder: 'ركّب الجملة',
    transformation: 'حوّل الجملة',
    correction: 'صحّح الجملة',
    short_answer: 'جواب قصير',
    open_response: 'كتابة قصيرة',
  }
  return labels[task?.type] || 'تدريب'
}

function allTasksAnswered(tasks) {
  return tasks.every((task) => hasResponse(task))
}

function previousPractice() {
  activePracticeIndex.value = Math.max(0, activePracticeIndex.value - 1)
}

async function checkPracticeAnswer() {
  const task = activePracticeTask.value
  if (!task?.id || !practiceEvaluationRevisionId.value || !canCheckPractice.value) return
  practiceError.value = ''
  evaluatingPractice.value = true
  const attemptNumber = Math.min((practiceAttempts[task.id] || 0) + 1, 2)
  try {
    const evaluatePractice = props.previewMode
      ? evaluateGrammarLessonPreviewPractice
      : evaluateGrammarLessonPractice
    const result = await evaluatePractice({
      revision_id: practiceEvaluationRevisionId.value,
      item_id: task.id,
      learner_response: responses[task.id],
      attempt_number: attemptNumber,
    })
    practiceAttempts[task.id] = result.attempt_number || attemptNumber
    practiceResults[task.id] = result
    if (result.correct && attemptNumber === 1) {
      practiceFirstTryCorrect[task.id] = true
    }
    if (!result.correct || attemptNumber > 1) {
      practiceHelpNeeded[task.id] = true
    }
  } catch {
    practiceError.value = 'تعذّر التحقق من الإجابة الآن. حاول مرة أخرى.'
  } finally {
    evaluatingPractice.value = false
  }
}

function nextPractice() {
  if (activePracticeIndex.value < practiceTasks.value.length - 1) {
    activePracticeIndex.value += 1
    practiceError.value = ''
    return
  }
  practiceCompleted.value = true
}

function grammarCompletionPayload() {
  const answers = {}
  for (const task of practiceTasks.value) {
    if (!task?.id) continue
    answers[task.id] = responses[task.id]
  }
  return { answers }
}

function recognitionOptions(task) {
  const options = arrayOf(task?.options).map(choiceOptionValue).filter(Boolean)
  if (options.length) return options
  return arrayOf(task?.expected_observations).map(choiceOptionValue).filter(Boolean)
}

function choiceOptionValue(option) {
  if (typeof option === 'string' || typeof option === 'number') return String(option).trim()
  if (option && typeof option === 'object') {
    return String(option.value ?? option.label ?? option.text ?? '').trim()
  }
  return ''
}

function recognitionPrompt(task) {
  if (isPresentBeLesson.value) {
    return 'ما الكلمة التي تتغير في الأمثلة حسب الفاعل؟'
  }
  return task?.prompt || 'اختر الملاحظة الصحيحة من الأمثلة.'
}

function recognitionTaskOptions(task) {
  if (isPresentBeLesson.value) {
    return ['am / is / are', 'do / does', 'was / were']
  }
  return arrayOf(task?.expected_observations)
}

function splitBlankSentence(value) {
  const text = String(value || '')
  const marker = text.match(/_{3,}/)?.[0] || '_____'
  return text.split(marker)
}

function previousUse() {
  activeUseIndex.value = Math.max(0, activeUseIndex.value - 1)
}

function nextUse() {
  if (activeUseIndex.value < useTasks.value.length) {
    activeUseIndex.value += 1
  }
}

const LessonTask = defineComponent({
  name: 'LessonTask',
  props: {
    task: { type: Object, required: false, default: null },
    responses: { type: Object, required: true },
    disabled: { type: Boolean, default: false },
  },
  emits: ['select-token', 'remove-token', 'reset-reorder'],
  setup(taskProps, { emit }) {
    function update(value) {
      if (taskProps.task?.id) {
        taskProps.responses[taskProps.task.id] = value
      }
    }

    function renderInput(task, id) {
      if (task.type === 'choice' || task.type === 'multiple_choice' || task.type === 'recognition') {
        const options = recognitionOptions(task)
        if (!options.length) {
          return h('input', {
            id,
            class: 'text-input',
            value: taskProps.responses[task.id] || '',
            'aria-label': task.prompt || 'Write your observation',
            disabled: taskProps.disabled,
            onInput: (event) => update(event.target.value),
          })
        }
        return h(
          'section',
          { class: 'mcq-card', dir: 'rtl', lang: 'ar', 'aria-labelledby': `${id}-title` },
          [
            h('p', { id: `${id}-title`, class: 'mcq-title' }, 'اختر الإجابة الصحيحة'),
            task.prompt
              ? h('p', { id: `${id}-label`, class: 'mcq-instruction', dir: 'rtl', lang: 'ar' }, task.prompt)
              : null,
            task.context
              ? h('p', { class: 'mcq-sentence', dir: 'ltr', lang: 'en' }, task.context)
              : null,
            h(
              'div',
              { class: 'choice-list', role: 'radiogroup', dir: 'ltr', 'aria-labelledby': `${id}-label` },
              options.map((option) =>
                h('button', {
                  key: option,
                  type: 'button',
                  role: 'radio',
                  class: ['choice-option', taskProps.responses[task.id] === option && 'choice-option--selected'],
                  'aria-checked': taskProps.responses[task.id] === option ? 'true' : 'false',
                  disabled: taskProps.disabled,
                  onClick: () => update(option),
                }, [
                  h('span', { class: 'choice-text', dir: textDir(option), lang: textDir(option) === 'rtl' ? 'ar' : 'en' }, option),
                  h('span', { class: 'choice-dot', 'aria-hidden': 'true' }),
                ]),
              ),
            ),
          ],
        )
      }
      if (task.type === 'fill_blank') {
        const parts = splitBlankSentence(task.sentence_with_blank)
        return h('div', { class: 'blank-line' }, [
          h('span', { dir: 'ltr', lang: 'en' }, parts[0] || ''),
          h('input', {
            id,
            class: 'inline-input',
            value: taskProps.responses[task.id] || '',
            'aria-label': task.prompt || 'Fill in the blank',
            disabled: taskProps.disabled,
            onInput: (event) => update(event.target.value),
          }),
          h('span', { dir: 'ltr', lang: 'en' }, parts.slice(1).join('')),
        ])
      }
      if (task.type === 'reorder' || task.type === 'sentence_builder') {
        const selected = Array.isArray(taskProps.responses[task.id]) ? taskProps.responses[task.id] : []
        const chips = arrayOf(task.word_chips || task.reorder_tokens)
        return h('div', { class: 'reorder-block' }, [
          h(
            'div',
            { class: 'token-list', role: 'list', 'aria-label': 'Available tokens' },
            chips.map((token, index) =>
              h('button', {
                key: `${token}-${index}`,
                type: 'button',
                class: ['token-button', selected.includes(token) && 'token-button--selected'],
                disabled: taskProps.disabled,
                onClick: () => emit('select-token', task.id, token),
              }, token),
            ),
          ),
          h(
            'div',
            { class: ['reorder-answer', selected.length && 'reorder-answer--filled'], dir: 'ltr', lang: 'en' },
            selected.length
              ? [
                  h('p', { class: 'reorder-sentence', dir: 'ltr', lang: 'en' }, selected.join(' ')),
                  h(
                    'div',
                    { class: 'selected-token-list', dir: 'ltr', lang: 'en' },
                    selected.map((token, index) =>
                      h('button', {
                        key: `${token}-selected-${index}`,
                        type: 'button',
                        class: 'selected-token',
                        title: 'Remove word',
                        disabled: taskProps.disabled,
                        onClick: () => emit('remove-token', task.id, index),
                      }, token),
                    ),
                  ),
                ]
              : [h('span', { dir: 'rtl', lang: 'ar' }, 'رتّب الكلمات هنا.')],
          ),
          h('button', {
            type: 'button',
            class: 'text-button text-button--small',
            disabled: taskProps.disabled,
            onClick: () => emit('reset-reorder', task.id),
          }, 'مسح'),
        ])
      }
      if (task.type === 'transformation') {
        return h('div', { class: 'correction-block' }, [
          h('p', { class: 'task-context', dir: 'ltr', lang: 'en' }, task.original_sentence),
          task.transformation_goal
            ? h('p', { class: 'task-scaffold', dir: textDir(task.transformation_goal) }, task.transformation_goal)
            : null,
          h('input', {
            id,
            class: 'text-input',
            value: taskProps.responses[task.id] || '',
            'aria-label': task.prompt || 'Write the transformed sentence',
            disabled: taskProps.disabled,
            onInput: (event) => update(event.target.value),
          }),
        ])
      }
      if (task.type === 'correction') {
        return h('div', { class: 'correction-block' }, [
          h('p', { class: 'incorrect-sentence', dir: 'ltr', lang: 'en' }, task.incorrect_sentence),
          h('input', {
            id,
            class: 'text-input',
            value: taskProps.responses[task.id] || '',
            'aria-label': task.prompt || 'Write the corrected sentence',
            disabled: taskProps.disabled,
            onInput: (event) => update(event.target.value),
          }),
        ])
      }
      if (task.type === 'short_answer') {
        return h('div', { class: 'correction-block' }, [
          h('p', { class: 'task-context task-context--question', dir: 'ltr', lang: 'en' }, task.context),
          h('input', {
            id,
            class: 'text-input',
            value: taskProps.responses[task.id] || '',
            'aria-label': task.prompt || 'Write a short answer',
            disabled: taskProps.disabled,
            onInput: (event) => update(event.target.value),
          }),
        ])
      }
      if (task.type === 'open_response') {
        return h('div', { class: 'open-response-block' }, [
          task.sentence_count_min
            ? h('p', { class: 'task-scaffold', dir: 'rtl', lang: 'ar' }, `اكتب ${task.sentence_count_min}-${task.sentence_count_max || 4} جمل قصيرة.`)
            : null,
          arrayOf(task.starters).length
            ? h('div', { class: 'starter-chip-row' }, arrayOf(task.starters).map((starter) =>
                h('span', { key: starter, class: 'starter-chip', dir: 'ltr', lang: 'en' }, starter),
              ))
            : null,
          h('textarea', {
            id,
            class: 'text-area',
            rows: 5,
            dir: 'ltr',
            lang: 'en',
            value: taskProps.responses[task.id] || '',
            placeholder: cleanOptionalText(task.scaffold) || 'I am ...',
            'aria-label': task.prompt || 'Write your response',
            disabled: taskProps.disabled,
            onInput: (event) => update(event.target.value),
          }),
        ])
      }
      return h('textarea', {
        id,
        class: 'text-area',
        rows: 4,
        dir: 'ltr',
        lang: 'en',
        value: taskProps.responses[task.id] || '',
        placeholder: cleanOptionalText(task.scaffold) || 'Write here.',
        'aria-label': task.prompt || 'Write your response',
        disabled: taskProps.disabled,
        onInput: (event) => update(event.target.value),
      })
    }

    return () => {
      const task = taskProps.task
      if (!task) return null
      const id = fieldId(task.id)
      if (isChoiceLikeTask(task)) {
        return h('div', { class: 'task-panel task-panel--choice' }, [
          renderInput(task, id),
        ])
      }
      return h('div', { class: 'task-panel' }, [
        task.context ? h('p', { class: 'task-context', dir: textDir(task.context) }, task.context) : null,
        h('label', { id: `${id}-label`, class: 'field-label', for: id, dir: textDir(task.prompt) }, task.prompt),
        cleanOptionalText(task.scaffold)
          ? h('p', { class: 'task-scaffold', dir: textDir(task.scaffold) }, cleanOptionalText(task.scaffold))
          : null,
        renderInput(task, id),
        h('p', { class: 'safe-note', dir: 'rtl', lang: 'ar' }, 'أجب ثم اضغط تحقّق من الإجابة.'),
      ])
    }
  },
})
</script>

<style scoped>
.grammar-lesson {
  --lesson-surface: #fffdf8;
  --lesson-surface-warm: #fbf6ed;
  --lesson-surface-soft: #f7f1e8;
  --lesson-border: rgba(63, 49, 34, 0.14);
  --lesson-text: #242018;
  --lesson-muted: #6f655b;
  --lesson-accent: #41685a;
  --lesson-accent-soft: rgba(65, 104, 90, 0.12);
  --lesson-warning: #9d6630;
  --lesson-danger: #9d463d;
  width: min(100%, 880px);
  margin-inline: auto;
  padding: 0 0 56px;
  color: var(--lesson-text);
}

.lesson-header,
.lesson-part,
.lesson-completion {
  border: 1px solid var(--lesson-border);
  background: var(--lesson-surface);
  border-radius: 14px;
  box-shadow: 0 18px 45px rgba(80, 62, 40, 0.07);
}

.lesson-header {
  padding: 18px 20px;
  margin-block-end: 18px;
  display: grid;
  gap: 14px;
}

.lesson-header__main {
  display: grid;
  gap: 8px;
}

.lesson-header__title {
  margin: 0;
  font-size: clamp(1.55rem, 3vw, 2.1rem);
  line-height: 1.1;
  letter-spacing: 0;
}

.lesson-header__goal {
  margin: 0;
  max-width: 720px;
  color: var(--lesson-muted);
  line-height: 1.55;
}

.meta-chip {
  width: fit-content;
  border: 1px solid var(--lesson-border);
  background: var(--lesson-surface-warm);
  border-radius: 999px;
  padding: 5px 10px;
  font-size: 0.85rem;
  color: var(--lesson-muted);
}

.tutor-open-button,
.ask-part-button {
  width: fit-content;
  border: 1px solid rgba(65, 104, 90, 0.22);
  border-radius: 999px;
  background: var(--lesson-accent);
  color: #ffffff;
  padding: 9px 14px;
  font: inherit;
  font-weight: 900;
  cursor: pointer;
}

.ask-part-button {
  margin-block: -4px 16px;
  background: var(--lesson-accent-soft);
  color: var(--lesson-accent);
}

.tutor-open-button:focus-visible,
.ask-part-button:focus-visible {
  outline: 3px solid rgba(65, 104, 90, 0.28);
  outline-offset: 2px;
}

.tutor-open-button--bottom {
  flex: 0 0 auto;
}

.lesson-tutor-cta {
  margin-block: 18px;
  border: 1px solid rgba(65, 104, 90, 0.2);
  background: linear-gradient(135deg, rgba(65, 104, 90, 0.1), #fffdf8 58%);
  border-radius: 14px;
  padding: 16px 18px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  box-shadow: 0 14px 32px rgba(80, 62, 40, 0.06);
}

.lesson-tutor-cta strong {
  display: block;
  color: var(--lesson-accent);
  font-size: 1.05rem;
  margin-block-end: 4px;
}

.lesson-tutor-cta p {
  margin: 0;
  color: var(--lesson-muted);
  line-height: 1.55;
}

.tutor-floating-button {
  position: fixed;
  inset-block-end: 24px;
  inset-inline-end: 24px;
  z-index: 60;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border: 1px solid rgba(65, 104, 90, 0.22);
  border-radius: 999px;
  background: var(--lesson-accent);
  color: #ffffff;
  box-shadow: 0 18px 42px rgba(28, 59, 50, 0.22);
  padding: 13px 18px;
  font: inherit;
  font-weight: 900;
  cursor: pointer;
}

.tutor-floating-button span {
  width: 24px;
  height: 24px;
  display: grid;
  place-items: center;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.18);
}

.tutor-floating-button:focus-visible {
  outline: 3px solid rgba(65, 104, 90, 0.28);
  outline-offset: 3px;
}

.lesson-part {
  position: relative;
  padding: 24px;
  margin-block: 16px;
  overflow: hidden;
}

.lesson-part h2 {
  margin: 0 0 18px;
  font-size: clamp(1.4rem, 2.6vw, 1.9rem);
  line-height: 1.25;
  letter-spacing: 0;
}

.part-number {
  position: absolute;
  inset-block-start: 20px;
  inset-inline-end: 22px;
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  border-radius: 999px;
  background: var(--lesson-accent-soft);
  color: var(--lesson-accent);
  font-weight: 800;
  margin: 0;
}

.concept-surface,
.collapse-body,
.production-card,
.task-panel,
.reflection-panel {
  display: grid;
  gap: 14px;
}

.task-panel--choice {
  gap: 0;
}

.concept-surface {
  max-width: 760px;
  text-align: right;
  font-family: Tajawal, var(--font-body, system-ui), sans-serif;
}

.concept-copy,
.concept-soft,
.takeaway-box p,
.example-explain,
.example-meaning,
.use-case-arabic,
.mistake-reason,
.completion-copy,
.safe-note {
  line-height: 1.7;
}

.concept-copy {
  margin: 0;
  font-size: 1.12rem;
}

.concept-soft {
  margin: 0;
  color: var(--lesson-muted);
  font-size: 1.02rem;
}

.comparison-card {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  align-items: stretch;
}

.comparison-card p {
  margin: 0;
  border: 1px solid var(--lesson-border);
  background: #ffffff;
  border-radius: 10px;
  padding: 14px;
  font-size: clamp(1.25rem, 2.8vw, 1.65rem);
  font-weight: 800;
  text-align: center;
}

.comparison-card :deep(mark),
.example-sentence :deep(mark),
.rule-symbol :deep(mark) {
  background: rgba(200, 137, 61, 0.26);
  color: inherit;
  border-radius: 5px;
  padding: 0 4px;
}

.takeaway-box {
  border-inline-start: 4px solid var(--lesson-accent);
  background: var(--lesson-surface-warm);
  border-radius: 10px;
  padding: 13px 15px;
}

.takeaway-box strong {
  display: block;
  color: var(--lesson-accent);
  margin-block-end: 5px;
}

.takeaway-box p {
  margin: 0;
}

.collapse-panel {
  margin-block-start: 10px;
  border: 1px solid var(--lesson-border);
  border-radius: 10px;
  background: var(--lesson-surface-warm);
  overflow: hidden;
}

.collapse-panel summary {
  cursor: pointer;
  padding: 12px 14px;
  font-weight: 800;
  color: var(--lesson-accent);
}

.collapse-body,
.use-case-flow {
  padding: 0 14px 14px;
}

.collapse-body p,
.use-case-line p {
  margin: 0;
  color: var(--lesson-muted);
  line-height: 1.75;
}

.example-grid,
.rule-card-grid,
.mistake-flow,
.quick-summary,
.starter-lines {
  display: grid;
  gap: 12px;
}

.example-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.example-card,
.rule-card,
.mistake-card,
.mistake-line,
.summary-item,
.production-card {
  border: 1px solid var(--lesson-border);
  background: #ffffff;
  border-radius: 12px;
  padding: 16px;
}

.production-card {
  gap: 18px;
  background: linear-gradient(180deg, #ffffff 0%, var(--lesson-surface-warm) 100%);
}

.production-card .task-panel {
  border: 1px solid var(--lesson-border);
  border-radius: 12px;
  background: #ffffff;
  padding: 16px;
}

.production-card .open-response-block {
  display: grid;
  gap: 12px;
}

.production-card .text-area {
  min-height: 170px;
}

.production-card .safe-note {
  margin: 0;
}

.production-card .step-actions {
  justify-content: flex-start;
}

.example-kind {
  display: inline-flex;
  width: fit-content;
  margin-block-end: 10px;
  border-radius: 999px;
  background: var(--lesson-accent-soft);
  color: var(--lesson-accent);
  padding: 4px 9px;
  font-size: 0.82rem;
  font-weight: 800;
}

.example-sentence {
  margin: 0 0 8px;
  font-size: clamp(1.35rem, 2.8vw, 1.9rem);
  line-height: 1.32;
  font-weight: 800;
}

.example-meaning,
.example-explain,
.example-purpose,
.use-case-line p,
.rule-explain,
.safe-note,
.soft-copy,
.task-context,
.task-scaffold {
  color: var(--lesson-muted);
}

.example-meaning,
.example-explain {
  margin: 4px 0 0;
}

.rule-card-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
  margin-block-end: 18px;
}

.rule-symbol {
  margin: 0 0 7px;
  font-size: 1.2rem;
  font-weight: 900;
}

.rule-explain {
  margin: 0;
}

.mistake-flow--compact {
  margin-block-start: 4px;
}

.mistake-pair {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.mistake-wrong,
.mistake-right {
  margin: 0;
  border-radius: 9px;
  padding: 10px 12px;
  background: var(--lesson-surface-warm);
  font-weight: 800;
}

.mistake-wrong {
  color: var(--lesson-danger);
}

.mistake-right {
  color: var(--lesson-accent);
}

.mistake-reason {
  margin: 10px 0 0;
}

.quick-summary {
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  margin-block-start: 14px;
}

.summary-item {
  display: grid;
  gap: 5px;
}

.summary-item span,
.summary-item small {
  color: var(--lesson-muted);
  font-size: 0.86rem;
}

.step-meta {
  display: grid;
  grid-template-columns: auto 1fr;
  align-items: center;
  gap: 12px;
  margin-block-end: 18px;
  color: var(--lesson-muted);
  font-weight: 700;
}

.progress-track {
  height: 8px;
  border-radius: 999px;
  background: var(--lesson-surface-soft);
  overflow: hidden;
}

.progress-track span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--lesson-accent);
}

.practice-shell {
  display: grid;
  gap: 14px;
}

.task-type-chip {
  width: fit-content;
  border-radius: 999px;
  background: var(--lesson-accent-soft);
  color: var(--lesson-accent);
  padding: 5px 11px;
  font-weight: 800;
  font-size: 0.88rem;
}

.round-title {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 900;
  color: var(--lesson-text);
}

.practice-feedback,
.practice-summary {
  border: 1px solid rgba(157, 102, 48, 0.22);
  background: rgba(157, 102, 48, 0.08);
  border-radius: 12px;
  padding: 14px 16px;
}

.practice-feedback--correct {
  border-color: rgba(65, 104, 90, 0.26);
  background: var(--lesson-accent-soft);
}

.practice-feedback p,
.practice-summary p {
  margin: 0;
  line-height: 1.7;
}

.practice-hint {
  color: var(--lesson-muted);
  margin-block-start: 6px !important;
}

.practice-error {
  margin: 0;
  color: var(--lesson-danger);
  font-weight: 800;
}

.practice-summary {
  display: grid;
  gap: 8px;
}

.practice-summary strong {
  color: var(--lesson-accent);
}

.field-label {
  display: block;
  margin-block: 8px 12px;
  font-weight: 800;
  line-height: 1.55;
  font-size: 1.08rem;
}

.text-area,
.text-input,
.inline-input,
.starter-line input {
  width: 100%;
  border: 1px solid var(--lesson-border);
  border-radius: 12px;
  background: #ffffff;
  color: var(--lesson-text);
  padding: 14px 15px;
  font: inherit;
  font-size: 1.05rem;
  line-height: 1.5;
}

.text-area {
  resize: vertical;
  min-height: 136px;
  white-space: pre-wrap;
}

.inline-input {
  width: min(220px, 100%);
  min-height: 48px;
  margin-inline: 10px;
  text-align: center;
  font-weight: 900;
}

.blank-line {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  line-height: 1.8;
  border: 1px solid var(--lesson-border);
  background: var(--lesson-surface-warm);
  border-radius: 12px;
  padding: 14px 16px;
  direction: ltr;
  font-size: 1.2rem;
  font-weight: 800;
}

.choice-list,
.token-list,
.step-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.choice-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(96px, 1fr));
  align-items: stretch;
  gap: 10px;
}

.mcq-card {
  width: min(100%, 620px);
  margin-inline: auto;
  border: 1px solid var(--lesson-border);
  background: #ffffff;
  border-radius: 12px;
  padding: 16px;
  display: grid;
  gap: 10px;
  text-align: right;
}

.mcq-title {
  margin: 0;
  color: var(--lesson-text);
  font-size: 1.12rem;
  font-weight: 900;
  line-height: 1.4;
}

.mcq-instruction {
  margin: 0;
  color: var(--lesson-muted);
  line-height: 1.55;
}

.mcq-sentence {
  margin: 2px 0 4px;
  border: 1px solid var(--lesson-border);
  background: var(--lesson-surface-warm);
  border-radius: 10px;
  padding: 13px 15px;
  color: var(--lesson-text);
  font-size: clamp(1.25rem, 3vw, 1.65rem);
  font-weight: 900;
  line-height: 1.35;
  text-align: center;
  unicode-bidi: isolate;
}

.choice-option,
.token-button,
.text-button,
.primary-button {
  min-height: 44px;
  border: 1px solid var(--lesson-border);
  border-radius: 999px;
  padding: 10px 16px;
  cursor: pointer;
  font: inherit;
}

.choice-option,
.token-button {
  background: var(--lesson-surface-warm);
  color: var(--lesson-text);
}

.choice-option {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 9px;
  border-width: 2px;
  border-radius: 12px;
  background: #ffffff;
  text-align: center;
  box-shadow: 0 6px 16px rgba(80, 62, 40, 0.05);
}

.choice-dot {
  width: 16px;
  height: 16px;
  flex: 0 0 16px;
  border-radius: 999px;
  border: 2px solid var(--lesson-border);
  background: #ffffff;
}

.choice-text {
  flex: 0 1 auto;
  line-height: 1.45;
  font-size: 1.05rem;
  font-weight: 850;
  unicode-bidi: isolate;
}

.choice-option--selected,
.token-button--selected {
  border-color: var(--lesson-accent);
  background: var(--lesson-accent-soft);
}

.choice-option--selected .choice-dot {
  border-color: var(--lesson-accent);
  background: var(--lesson-accent);
  box-shadow: inset 0 0 0 3px #ffffff;
}

.primary-button {
  background: var(--lesson-accent);
  color: #ffffff;
  border-color: var(--lesson-accent);
  font-weight: 850;
  box-shadow: 0 8px 18px rgba(65, 104, 90, 0.18);
}

.text-button {
  background: transparent;
  color: var(--lesson-accent);
}

.text-button--small {
  min-height: 34px;
  padding: 6px 11px;
  margin-block-start: 8px;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.primary-button:disabled {
  border-color: rgba(65, 104, 90, 0.24);
  background: rgba(65, 104, 90, 0.13);
  color: var(--lesson-accent);
  opacity: 1;
  box-shadow: none;
}

.choice-option:disabled,
.token-button:disabled {
  opacity: 0.78;
}

.choice-option--selected:disabled,
.token-button--selected:disabled {
  opacity: 1;
}

.reorder-answer {
  min-height: 58px;
  border: 1px dashed var(--lesson-border);
  border-radius: 10px;
  padding: 12px 14px;
  margin: 10px 0 0;
  color: var(--lesson-muted);
  display: grid;
  gap: 10px;
  background: #ffffff;
  text-align: left;
}

.reorder-answer--filled {
  border-style: solid;
  border-color: rgba(65, 104, 90, 0.26);
  background: var(--lesson-surface-warm);
}

.reorder-sentence {
  margin: 0;
  color: var(--lesson-text);
  font-size: clamp(1.25rem, 2.5vw, 1.55rem);
  font-weight: 900;
  line-height: 1.55;
  letter-spacing: 0;
  word-spacing: 0.18em;
  white-space: normal;
  direction: ltr;
  unicode-bidi: isolate;
}

.selected-token-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  direction: ltr;
}

.selected-token,
.starter-chip {
  border: 1px solid var(--lesson-accent);
  background: var(--lesson-accent-soft);
  color: var(--lesson-accent);
  border-radius: 999px;
  padding: 7px 11px;
  font-weight: 800;
}

.selected-token {
  cursor: pointer;
  direction: ltr;
  unicode-bidi: isolate;
  margin: 0;
}

.starter-chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.incorrect-sentence {
  color: var(--lesson-danger);
  background: rgba(157, 70, 61, 0.08);
  border-radius: 8px;
  padding: 10px 12px;
}

.safe-note {
  margin-block-start: 8px;
  font-size: 0.9rem;
}

.production-title {
  margin: 0;
  font-size: 1.18rem;
  font-weight: 800;
  line-height: 1.6;
}

.starter-line {
  display: grid;
  grid-template-columns: minmax(120px, 180px) 1fr;
  gap: 14px;
  align-items: center;
  border: 1px solid var(--lesson-border);
  border-radius: 12px;
  background: var(--lesson-surface-warm);
  padding: 12px;
}

.starter-line span {
  font-weight: 900;
  color: var(--lesson-accent);
}

.reflection-panel {
  background: var(--lesson-surface-warm);
  border-radius: 12px;
  padding: 16px;
}

.reflection-panel p {
  margin: 0;
  line-height: 1.75;
}

.lesson-completion {
  margin-block-start: 18px;
  padding: 18px 22px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.completion-copy {
  margin: 0;
  color: var(--lesson-muted);
}

button:focus-visible,
textarea:focus-visible,
input:focus-visible {
  outline: 3px solid rgba(65, 104, 90, 0.35);
  outline-offset: 2px;
}

@media (max-width: 720px) {
  .grammar-lesson {
    width: 100%;
  }

  .lesson-header,
  .lesson-part,
  .lesson-completion {
    border-radius: 12px;
    padding: 18px;
  }

  .part-number {
    position: static;
    margin-block-end: 10px;
  }

  .comparison-card,
  .example-grid,
  .rule-card-grid,
  .mistake-pair,
  .step-meta,
  .starter-line {
    grid-template-columns: 1fr;
  }

  .lesson-completion {
    flex-direction: column;
    align-items: stretch;
  }

  .lesson-tutor-cta {
    flex-direction: column;
    align-items: stretch;
  }

  .tutor-open-button--bottom {
    width: 100%;
    justify-content: center;
  }

  .tutor-floating-button {
    inset-inline: 16px;
    inset-block-end: 16px;
    justify-content: center;
  }
}

@media (prefers-reduced-motion: no-preference) {
  .lesson-part,
  .lesson-header,
  .lesson-completion {
    animation: lesson-rise 220ms ease-out both;
  }

  @keyframes lesson-rise {
    from {
      opacity: 0;
      transform: translateY(8px);
    }

    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
}
</style>

<style>
.grammar-lesson .task-panel--choice {
  gap: 0;
}

.grammar-lesson .mcq-card {
  width: min(100%, 560px);
  margin-inline: auto;
  border: 1px solid var(--lesson-border);
  background: #ffffff;
  border-radius: 12px;
  padding: 16px;
  display: grid;
  gap: 10px;
  text-align: right;
}

.grammar-lesson .mcq-title {
  margin: 0;
  color: var(--lesson-text);
  font-size: 1.08rem;
  font-weight: 900;
  line-height: 1.35;
}

.grammar-lesson .mcq-instruction {
  margin: 0;
  color: var(--lesson-muted);
  font-size: 0.98rem;
  line-height: 1.5;
}

.grammar-lesson .mcq-sentence {
  margin: 4px 0 2px;
  border: 1px solid var(--lesson-border);
  background: var(--lesson-surface-warm);
  border-radius: 10px;
  padding: 12px 14px;
  color: var(--lesson-text);
  font-size: clamp(1.2rem, 2.4vw, 1.5rem);
  font-weight: 900;
  line-height: 1.35;
  text-align: center;
  direction: ltr;
  unicode-bidi: isolate;
}

.grammar-lesson .choice-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(88px, 1fr));
  gap: 8px;
  align-items: stretch;
  direction: ltr;
}

.grammar-lesson .choice-option {
  min-height: 44px;
  width: 100%;
  border: 2px solid var(--lesson-border);
  border-radius: 999px;
  background: #fffdf8;
  color: var(--lesson-text);
  padding: 9px 14px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font: inherit;
  text-align: center;
  box-shadow: none;
  transition: background-color 140ms ease, border-color 140ms ease, color 140ms ease, transform 140ms ease;
}

.grammar-lesson .choice-option:hover:not(:disabled) {
  border-color: rgba(65, 104, 90, 0.5);
  background: rgba(65, 104, 90, 0.08);
}

.grammar-lesson .choice-option:active:not(:disabled) {
  transform: translateY(1px);
}

.grammar-lesson .choice-option--selected {
  border-color: var(--lesson-accent);
  background: rgba(65, 104, 90, 0.16);
  color: var(--lesson-accent);
}

.grammar-lesson .choice-text {
  display: block;
  line-height: 1.35;
  font-size: 1.05rem;
  font-weight: 900;
  direction: ltr;
  unicode-bidi: isolate;
}

.grammar-lesson .choice-dot {
  display: none;
}

.grammar-lesson .primary-button {
  background: var(--lesson-accent);
  color: #ffffff;
  border-color: var(--lesson-accent);
  font-weight: 850;
  box-shadow: 0 8px 18px rgba(65, 104, 90, 0.18);
}

.grammar-lesson .primary-button:disabled {
  border-color: rgba(65, 104, 90, 0.28);
  background: rgba(65, 104, 90, 0.14);
  color: var(--lesson-accent);
  opacity: 1;
  box-shadow: none;
}

@media (max-width: 520px) {
  .grammar-lesson .mcq-card {
    width: 100%;
    padding: 14px;
  }

  .grammar-lesson .choice-list {
    grid-template-columns: 1fr;
  }
}
</style>
