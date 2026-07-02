/**
 * Applies student-scope i18n migrations to language views + routine view.
 * Run: node scripts/migrate-student-i18n.mjs && node scripts/patch-student-i18n-complete.mjs
 */
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..')

function patch(file, pairs) {
  const fp = path.join(root, file)
  let s = fs.readFileSync(fp, 'utf8')
  for (const [from, to] of pairs) {
    if (!s.includes(from)) {
      console.warn(`[skip] ${file}: not found: ${from.slice(0, 60)}…`)
      continue
    }
    s = s.replace(from, to)
  }
  fs.writeFileSync(fp, s)
  console.log(`patched ${file}`)
}

// ── Hub ──
patch('src/views/student/languages/StudentLanguagesHubView.vue', [
  ['eyebrow="تعلّم اللغات"', ':eyebrow="t(\'student.languages.hub.header.eyebrow\')"'],
  ['title="رحلتك في الإنجليزية"', ':title="t(\'student.languages.hub.header.title\')"'],
  ['subtitle="ابدأ من مهمتك اليوم — خطوة واحدة في كل مرة"', ':subtitle="t(\'student.languages.hub.header.subtitle\')"'],
  ['<p class="lang-placement-gate__eyebrow">الخطوة الأولى</p>', '<p class="lang-placement-gate__eyebrow">{{ t(\'student.languages.hub.placement.eyebrow\') }}</p>'],
  ['<h2 class="lang-placement-gate__title">حدّد مستواك لنبدأ رحلتك</h2>', '<h2 class="lang-placement-gate__title">{{ t(\'student.languages.hub.placement.title\') }}</h2>'],
  [`<p class="lang-placement-gate__body">
            اختبار قصير يوضّح لك أين أنت وما مهمتك التالية — لا يمكن بدء الدروس قبله.
          </p>`, `<p class="lang-placement-gate__body">
            {{ t('student.languages.hub.placement.body') }}
          </p>`],
  ['            ابدأ اختبار تحديد المستوى\n', '            {{ t(\'student.languages.hub.placement.cta\') }}\n'],
  [`            <span v-if="access.expires_at">
              اشتراكك {{ statusLabel }} — ينتهي {{ formatDate(access.expires_at) }}
            </span>
            <span v-else>اشتراكك {{ statusLabel }}</span>`, `            <span v-if="access.expires_at">
              {{ t('student.languages.hub.subscription.expires', { status: statusLabel, date: formatDate(access.expires_at) }) }}
            </span>
            <span v-else>{{ t('student.languages.hub.subscription.status', { status: statusLabel }) }}</span>`],
  ['              المسار الكامل\n', '              {{ t(\'student.languages.hub.footer.fullPath\') }}\n'],
  ['              الرؤى\n', '              {{ t(\'student.languages.hub.footer.insights\') }}\n'],
  ['              نتائج التحديد\n', '              {{ t(\'student.languages.hub.footer.placementResults\') }}\n'],
  [`            <span v-else-if="access.next_allowed_retake_date" class="text-medium-emphasis">
              {{ t('student.lesson.quiz.results.retry') }} بعد {{ formatDate(access.next_allowed_retake_date) }}
            </span>`, `            <span v-else-if="access.next_allowed_retake_date" class="text-medium-emphasis">
              {{ t('student.languages.hub.footer.retakeAfter', { date: formatDate(access.next_allowed_retake_date) }) }}
            </span>`],
  ["import { computed, onMounted, ref } from 'vue'\nimport { useRouter } from 'vue-router'", "import { computed, onMounted, ref } from 'vue'\nimport { useI18n } from 'vue-i18n'\nimport { useRouter } from 'vue-router'"],
  ['const router = useRouter()', "const { t } = useI18n()\nconst router = useRouter()"],
  [`    active: t('student.teacherContact.status'),
    expiring_soon: 'ينتهي قريباً',
    expired: 'منتهي',
    pending: 'غير مفعّل',`, `    active: t('student.languages.hub.status.active'),
    expiring_soon: t('student.languages.hub.status.expiringSoon'),
    expired: t('student.languages.hub.status.expired'),
    pending: t('student.languages.hub.status.pending'),`],
  ['  return `${pct}% نحو ${next}`', "  return t('student.languages.hub.journeyProgress', { pct, next })"],
])

// ── Practice hub ──
patch('src/views/student/languages/StudentLanguagePracticeHubView.vue', [
  ['eyebrow="تعلّم اللغات"', ':eyebrow="t(\'student.languages.hub.header.eyebrow\')"'],
  ['title="تمرّن"', ':title="t(\'student.languages.practice.title\')"'],
  ['subtitle="اختر مهارة — كل التدريب في مكان واحد"', ':subtitle="t(\'student.languages.practice.subtitle\')"'],
  ["import PageHeader from '../../../components/common/PageHeader.vue'", "import { computed } from 'vue'\nimport { useI18n } from 'vue-i18n'\nimport PageHeader from '../../../components/common/PageHeader.vue'"],
  ['const skills = LANGUAGE_PRACTICE_SKILLS', `const { t } = useI18n()

const skills = computed(() =>
  LANGUAGE_PRACTICE_SKILLS.map((s) => ({
    ...s,
    label: t(\`student.languages.practice.skills.\${s.key}.label\`),
    description: t(\`student.languages.practice.skills.\${s.key}.description\`),
  })),
)`],
])

// ── Subscribe ──
patch('src/views/student/languages/StudentLanguageSubscribeView.vue', [
  ['eyebrow="اشتراك مميز"', ':eyebrow="t(\'student.languages.subscribe.eyebrow\')"'],
  ['title="تعلّم اللغة الإنجليزية"', ':title="t(\'student.languages.subscribe.title\')"'],
  ['subtitle="فعّل اشتراكك للوصول إلى اختبار المستوى والمسار الشخصي"', ':subtitle="t(\'student.languages.subscribe.subtitle\')"'],
  ["import { onMounted, ref } from 'vue'", "import { onMounted, ref } from 'vue'\nimport { useI18n } from 'vue-i18n'"],
  ['const router = useRouter()', "const { t } = useI18n()\nconst router = useRouter()"],
  ["error.value = getErrorMessage(e, 'تعذر تحميل المنتج')", "error.value = getErrorMessage(e, t('student.languages.subscribe.errors.load'))"],
  ["success.value = 'تم تفعيل الاشتراك — سيتم توجيهك لبدء اختبار المستوى قريباً (المرحلة التالية).'", "success.value = t('student.languages.subscribe.success')"],
  ["error.value = getErrorMessage(e, 'فشل الاشتراك')", "error.value = getErrorMessage(e, t('student.languages.subscribe.errors.subscribe'))"],
])

// ── Scenario library ──
patch('src/views/student/languages/StudentLanguageScenarioLibraryView.vue', [
  ['eyebrow="تعلّم اللغات"', ':eyebrow="t(\'student.languages.hub.header.eyebrow\')"'],
  ['title="سيناريوهات المحادثة"', ':title="t(\'student.languages.scenarios.library.title\')"'],
  ['subtitle="تمرّن على الإنجليزية في مواقف حياتية موجّهة"', ':subtitle="t(\'student.languages.scenarios.library.subtitle\')"'],
  ['          الكل\n', '          {{ t(\'student.languages.scenarios.all\') }}\n'],
  ['              موصى به\n', '              {{ t(\'student.languages.scenarios.recommended\') }}\n'],
  ['title="لا توجد سيناريوهات"', ':title="t(\'student.languages.scenarios.empty\')"'],
  ["import { onMounted, ref } from 'vue'", "import { onMounted, ref } from 'vue'\nimport { useI18n } from 'vue-i18n'"],
  ['const router = useRouter()', "const { t } = useI18n()\nconst router = useRouter()"],
  ["error.value = e?.response?.data?.detail || 'تعذر تحميل السيناريوهات'", "error.value = e?.response?.data?.detail || t('student.languages.scenarios.errors.load')"],
])

// ── Certificates ──
patch('src/views/student/languages/StudentLanguageCertificatesView.vue', [
  ['eyebrow="تعلّم اللغات"', ':eyebrow="t(\'student.languages.hub.header.eyebrow\')"'],
  ['title="الشهادات"', ':title="t(\'student.languages.certificates.title\')"'],
  ['subtitle="شهادات CEFR عند إتقان جميع المهارات للمستوى"', ':subtitle="t(\'student.languages.certificates.subtitle\')"'],
  ['<h3 class="text-h6 font-weight-bold mb-4">أهلية الشهادات</h3>', '<h3 class="text-h6 font-weight-bold mb-4">{{ t(\'student.languages.certificates.eligibility\') }}</h3>'],
  ['<h3 class="text-h6 font-weight-bold mb-4">شهاداتك</h3>', '<h3 class="text-h6 font-weight-bold mb-4">{{ t(\'student.languages.certificates.yours\') }}</h3>'],
  ['<th>المستوى</th>', '<th>{{ t(\'student.languages.certificates.table.level\') }}</th>'],
  ['<th>رقم الشهادة</th>', '<th>{{ t(\'student.languages.certificates.table.number\') }}</th>'],
  ['<th>تاريخ الإصدار</th>', '<th>{{ t(\'student.languages.certificates.table.issued\') }}</th>'],
  ['<th>رمز التحقق</th>', '<th>{{ t(\'student.languages.certificates.table.verify\') }}</th>'],
  ['<th class="text-end">إجراءات</th>', '<th class="text-end">{{ t(\'student.languages.certificates.table.actions\') }}</th>'],
  ['                  التحقق\n', '                  {{ t(\'student.languages.certificates.verify\') }}\n'],
  [`          لا توجد شهادات بعد. أكمل جميع المهارات للمستوى المطلوب للحصول على شهادتك الأولى.`, `          {{ t('student.languages.certificates.empty') }}`],
  ["import { onMounted, ref } from 'vue'", "import { onMounted, ref } from 'vue'\nimport { useI18n } from 'vue-i18n'"],
  ['function statusLabel(item) {\n  if (item.issued) return \'صادرة\'\n  if (item.eligible) return \'مؤهل\'\n  return \'غير مؤهل بعد\'\n}', `function statusLabel(item) {
  if (item.issued) return t('student.languages.certificates.status.issued')
  if (item.eligible) return t('student.languages.certificates.status.eligible')
  return t('student.languages.certificates.status.notYet')
}`],
  ["function requirementText(level) {\n  return `القراءة والاستماع والكتابة والتحدث ≥ ${level}`\n}", "function requirementText(level) {\n  return t('student.languages.certificates.requirement', { level })\n}"],
  ["loadError.value = err.response?.data?.detail?.message || err.message || 'تعذّر تحميل الشهادات'", "loadError.value = err.response?.data?.detail?.message || err.message || t('student.languages.certificates.errors.load')"],
])
patch('src/views/student/languages/StudentLanguageCertificatesView.vue', [
  ['const loadError = ref(\'\')', "const { t } = useI18n()\nconst loadError = ref('')"],
])

console.log('Done patching language views (batch 1).')

// ── Reading ──
patch('src/views/student/languages/StudentLanguageReadingView.vue', [
  ['eyebrow="تعلّم اللغات"', ':eyebrow="t(\'student.languages.hub.header.eyebrow\')"'],
  ['title="القراءة"', ':title="t(\'student.languages.skills.reading\')"'],
  ['subtitle="دروس القراءة حسب مستواك الحالي"', ':subtitle="t(\'student.languages.reading.subtitle\')"'],
  [`      مستواك في القراءة: <strong>{{ listMeta.student_level }}</strong> —
      الدروس المتاحة حالياً عند مستوى <strong>{{ listMeta.lesson_level }}</strong>
      (سيتم إضافة محتوى أعلى قريباً).`, `      {{ t('student.languages.common.levelLine', { skill: t('student.languages.skills.reading'), student: listMeta.student_level, lesson: listMeta.lesson_level }) }}
      {{ t('student.languages.common.higherContentSoon') }}`],
  ['<div class="text-subtitle-1 font-weight-bold mb-3">الدروس</div>', '<div class="text-subtitle-1 font-weight-bold mb-3">{{ t(\'student.languages.common.lessons\') }}</div>'],
  ['            لا توجد دروس منشورة لمستواك حالياً.', '            {{ t(\'student.languages.common.emptyLessons\') }}'],
  ['<div class="text-body-1 text-medium-emphasis">اختر درساً من القائمة.</div>', '<div class="text-body-1 text-medium-emphasis">{{ t(\'student.languages.common.selectLesson\') }}</div>'],
  ['<div class="text-subtitle-1 font-weight-bold mb-4">الأسئلة</div>', '<div class="text-subtitle-1 font-weight-bold mb-4">{{ t(\'student.languages.common.questions\') }}</div>'],
  [`              {{ t('student.languages.common.submit') }} الإجابات`, `              {{ t('student.languages.common.submitAnswers') }}`],
  [`              النتيجة: {{ submitResult.score_percent }}% —
              {{ submitResult.passed ? 'نجحت في الدرس' : t('student.languages.common.retry') }}`, `              {{ t('student.languages.reading.resultLine', {
                score: submitResult.score_percent,
                status: submitResult.passed ? t('student.languages.common.passedLesson') : t('student.languages.common.retry'),
              }) }}`],
  ["import { computed, onMounted, ref } from 'vue'\nimport { useRouter } from 'vue-router'", "import { computed, onMounted, ref } from 'vue'\nimport { useI18n } from 'vue-i18n'\nimport { useRouter } from 'vue-router'"],
  ['const { access, loadAccess } = useLanguageAccess()', "const { t } = useI18n()\nconst { access, loadAccess } = useLanguageAccess()"],
  ["loadError.value = getErrorMessage(e, 'تعذر تحميل دروس القراءة')", "loadError.value = getErrorMessage(e, t('student.languages.reading.errors.loadList'))"],
  ["loadError.value = getErrorMessage(e, 'تعذر تحميل الدرس')", "loadError.value = getErrorMessage(e, t('student.languages.reading.errors.loadLesson'))"],
  ["loadError.value = getErrorMessage(e, `تعذر ${t('student.languages.common.submit')} الإجابات`)", "loadError.value = getErrorMessage(e, t('student.languages.common.submitAnswers'))"],
  ["in_progress: 'جاري',", "in_progress: t('student.languages.common.inProgress'),"],
])

// ── Listening ──
patch('src/views/student/languages/StudentLanguageListeningView.vue', [
  ['eyebrow="تعلّم اللغات"', ':eyebrow="t(\'student.languages.hub.header.eyebrow\')"'],
  ['title="الاستماع"', ':title="t(\'student.languages.skills.listening\')"'],
  ['subtitle="استمع وأجب عن الأسئلة"', ':subtitle="t(\'student.languages.listening.subtitle\')"'],
  [`      مستواك في الاستماع: <strong>{{ listMeta.student_level }}</strong> —
      الدروس المتاحة حالياً عند مستوى <strong>{{ listMeta.lesson_level }}</strong>.`, `      {{ t('student.languages.common.levelLineShort', { skill: t('student.languages.skills.listening'), student: listMeta.student_level, lesson: listMeta.lesson_level }) }}.`],
  ['<div class="text-subtitle-1 font-weight-bold mb-3">الدروس</div>', '<div class="text-subtitle-1 font-weight-bold mb-3">{{ t(\'student.languages.common.lessons\') }}</div>'],
  ['            لا توجد دروس منشورة لمستواك حالياً.', '            {{ t(\'student.languages.common.emptyLessons\') }}'],
  ['<div class="text-body-1 text-medium-emphasis">اختر درساً من القائمة.</div>', '<div class="text-body-1 text-medium-emphasis">{{ t(\'student.languages.common.selectLesson\') }}</div>'],
  [`              title="{{ t('student.lesson.fallback.tabs.pdf') }} الصوتي غير متوفر"`, `:title="t('student.languages.listening.audioUnavailableTitle')"`],
  ['              يمكنك الإجابة عن الأسئلة عندما يتوفر الصوت لاحقاً. لن يتعطل التطبيق.', '              {{ t(\'student.languages.listening.audioUnavailableBody\') }}'],
  [`              {{ t('student.languages.common.submit') }} الإجابات`, `              {{ t('student.languages.common.submitAnswers') }}`],
  ['              النتيجة: {{ submitResult.score_percent }}%', '              {{ t(\'student.languages.listening.resultLine\', { score: submitResult.score_percent }) }}'],
  ["import { computed, onMounted, ref } from 'vue'\nimport { useRouter } from 'vue-router'", "import { computed, onMounted, ref } from 'vue'\nimport { useI18n } from 'vue-i18n'\nimport { useRouter } from 'vue-router'"],
  ['const { access, loadAccess } = useLanguageAccess()', "const { t } = useI18n()\nconst { access, loadAccess } = useLanguageAccess()"],
  ["loadError.value = getErrorMessage(e, 'تعذر تحميل دروس الاستماع')", "loadError.value = getErrorMessage(e, t('student.languages.listening.errors.loadList'))"],
  ["loadError.value = getErrorMessage(e, 'تعذر تحميل الدرس')", "loadError.value = getErrorMessage(e, t('student.languages.reading.errors.loadLesson'))"],
  ["loadError.value = getErrorMessage(e, `تعذر ${t('student.languages.common.submit')} الإجابات`)", "loadError.value = getErrorMessage(e, t('student.languages.common.submitAnswers'))"],
])

// ── Progress ──
patch('src/views/student/languages/StudentLanguageProgressView.vue', [
  ['eyebrow="تعلّم اللغات"', ':eyebrow="t(\'student.languages.hub.header.eyebrow\')"'],
  ['title="التحليلات والتقدّم"', ':title="t(\'student.languages.progress.title\')"'],
  ['subtitle="مستواك وإنجازاتك وإحصائيات تعلّمك"', ':subtitle="t(\'student.languages.progress.subtitle\')"'],
  ['<div class="text-subtitle-1 font-weight-bold mb-3">اتجاه التحسّن</div>', '<div class="text-subtitle-1 font-weight-bold mb-3">{{ t(\'student.languages.progress.trend\') }}</div>'],
  [`              الأسبوع الأخير: {{ dash.improvement_trend?.recent_week_average ?? '—' }}%
              · السابق: {{ dash.improvement_trend?.prior_week_average ?? '—' }}%`, `              {{ t('student.languages.progress.trendWeeks', {
                recent: dash.improvement_trend?.recent_week_average ?? '—',
                prior: dash.improvement_trend?.prior_week_average ?? '—',
              }) }}`],
  ['<div class="text-subtitle-1 font-weight-bold mb-3">إحصائيات التعلّم</div>', '<div class="text-subtitle-1 font-weight-bold mb-3">{{ t(\'student.languages.progress.statsTitle\') }}</div>'],
  ['<div class="text-caption text-medium-emphasis">محادثات</div>', '<div class="text-caption text-medium-emphasis">{{ t(\'student.languages.progress.stats.conversations\') }}</div>'],
  ['<div class="text-caption text-medium-emphasis">تمارين تحدث</div>', '<div class="text-caption text-medium-emphasis">{{ t(\'student.languages.progress.stats.speaking\') }}</div>'],
  ['<div class="text-caption text-medium-emphasis">تمارين كتابة</div>', '<div class="text-caption text-medium-emphasis">{{ t(\'student.languages.progress.stats.writing\') }}</div>'],
  ['<div class="text-caption text-medium-emphasis">وقت الدراسة (د)</div>', '<div class="text-caption text-medium-emphasis">{{ t(\'student.languages.progress.stats.studyMinutes\') }}</div>'],
  ['<div class="text-caption text-medium-emphasis">أهداف {{ t(\'student.lesson.card.status.completed\') }}ة</div>', '<div class="text-caption text-medium-emphasis">{{ t(\'student.languages.progress.stats.objectives\') }}</div>'],
  ['<div class="text-caption text-medium-emphasis">سيناريوهات</div>', '<div class="text-caption text-medium-emphasis">{{ t(\'student.languages.progress.stats.scenarios\') }}</div>'],
  ['<div class="text-subtitle-1 font-weight-bold">الإنجازات</div>', '<div class="text-subtitle-1 font-weight-bold">{{ t(\'student.languages.progress.achievements\') }}</div>'],
  ['<div class="text-subtitle-1 font-weight-bold mb-3">تقدّم السيناريوهات</div>', '<div class="text-subtitle-1 font-weight-bold mb-3">{{ t(\'student.languages.progress.scenarioProgress\') }}</div>'],
  [`              {{ sc.mastery_label_ar }} · أفضل نتيجة {{ sc.best_score }} · {{ sc.completion_count }} مرة`, `              {{ t('student.languages.progress.scenarioLine', { mastery: sc.mastery_label_ar, score: sc.best_score, count: sc.completion_count }) }}`],
  ['<div class="text-subtitle-1 font-weight-bold mb-3">النشاط الأخير</div>', '<div class="text-subtitle-1 font-weight-bold mb-3">{{ t(\'student.languages.progress.recentActivity\') }}</div>'],
  ['<div v-else class="text-body-2 text-medium-emphasis">لا يوجد نشاط بعد.</div>', '<div v-else class="text-body-2 text-medium-emphasis">{{ t(\'student.languages.progress.noActivity\') }}</div>'],
  ["import { computed, onMounted, ref } from 'vue'", "import { computed, onMounted, ref } from 'vue'\nimport { useI18n } from 'vue-i18n'"],
  ['const { access, loadAccess } = useLanguageAccess()', "const { t } = useI18n()\nconst { access, loadAccess } = useLanguageAccess()"],
  [`    { key: 'reading', label: 'القراءة', score: scores.reading, level: levels.reading },
    { key: 'listening', label: 'الاستماع', score: scores.listening, level: levels.listening },
    { key: 'writing', label: 'الكتابة', score: scores.writing, level: levels.writing },
    { key: 'speaking', label: 'التحدث', score: scores.speaking, level: levels.speaking },
    { key: 'vocabulary', label: 'المفردات', score: scores.vocabulary, level: null },`, `    { key: 'reading', label: t('student.languages.skills.reading'), score: scores.reading, level: levels.reading },
    { key: 'listening', label: t('student.languages.skills.listening'), score: scores.listening, level: levels.listening },
    { key: 'writing', label: t('student.languages.skills.writing'), score: scores.writing, level: levels.writing },
    { key: 'speaking', label: t('student.languages.skills.speaking'), score: scores.speaking, level: levels.speaking },
    { key: 'vocabulary', label: t('student.languages.skills.vocabulary'), score: scores.vocabulary, level: null },`],
  ["loadError.value = getErrorMessage(e, 'تعذر تحميل التحليلات')", "loadError.value = getErrorMessage(e, t('student.languages.progress.errors.load'))"],
])

console.log('Done patching language views (batch 2).')

// ── Lessons ──
patch('src/views/student/languages/StudentLanguageLessonsView.vue', [
  ['eyebrow="تعلّم اللغات"', ':eyebrow="t(\'student.languages.hub.header.eyebrow\')"'],
  ['title="دروس القواعد والمفردات"', ':title="t(\'student.languages.lessonsPage.title\')"'],
  ['subtitle="دروس قصيرة تشرح القواعد والمفردات — مع أمثلة وتمارين سريعة"', ':subtitle="t(\'student.languages.lessonsPage.subtitle\')"'],
  ['        دروس لمستواك الحالي: <strong>{{ level }}</strong>', '        {{ t(\'student.languages.lessonsPage.levelBanner\', { level }) }}'],
  ['<div class="text-body-2 text-medium-emphasis">لا توجد دروس متاحة لمستواك حالياً.</div>', '<div class="text-body-2 text-medium-emphasis">{{ t(\'student.languages.lessonsPage.empty\') }}</div>'],
  ['<div class="text-overline text-medium-emphasis mb-1">أمثلة</div>', '<div class="text-overline text-medium-emphasis mb-1">{{ t(\'student.languages.lessonsPage.examples\') }}</div>'],
  ['<div class="text-overline text-medium-emphasis mb-1">تمرين</div>', '<div class="text-overline text-medium-emphasis mb-1">{{ t(\'student.languages.lessonsPage.practice\') }}</div>'],
  ['                        إظهار الإجابة', '                        {{ t(\'student.languages.lessonsPage.showAnswer\') }}'],
  ["import { computed, onMounted, reactive, ref } from 'vue'", "import { computed, onMounted, reactive, ref } from 'vue'\nimport { useI18n } from 'vue-i18n'"],
  ['const router = useRouter()', "const { t } = useI18n()\nconst router = useRouter()"],
  [`    { type: 'grammar', label: 'القواعد', icon: 'mdi-format-letter-case' },
    { type: 'vocabulary', label: 'المفردات', icon: 'mdi-book-alphabet' },`, `    { type: 'grammar', label: t('student.languages.lessonsPage.type.grammar'), icon: 'mdi-format-letter-case' },
    { type: 'vocabulary', label: t('student.languages.lessonsPage.type.vocabulary'), icon: 'mdi-book-alphabet' },`],
  ["loadError.value = getErrorMessage(e, 'تعذر تحميل الدروس')", "loadError.value = getErrorMessage(e, t('student.languages.lessonsPage.errors.load'))"],
])

// ── Scenario detail ──
patch('src/views/student/languages/StudentLanguageScenarioDetailView.vue', [
  ['eyebrow="السيناريوهات"', ':eyebrow="t(\'student.languages.scenarios.eyebrow\')"'],
  [`:title="detail?.title_ar || detail?.title_en || 'سيناريو'"`, `:title="detail?.title_ar || detail?.title_en || t('student.languages.scenarios.detail.defaultTitle')"`],
  ['<v-btn variant="text" prepend-icon="mdi-arrow-right" class="mb-4" @click="goBack">كل السيناريوهات</v-btn>', '<v-btn variant="text" prepend-icon="mdi-arrow-right" class="mb-4" @click="goBack">{{ t(\'student.languages.scenarios.detail.back\') }}</v-btn>'],
  ['<v-chip variant="tonal">المستوى {{ detail.level_min }}+</v-chip>', '<v-chip variant="tonal">{{ t(\'student.languages.scenarios.detail.level\', { level: detail.level_min }) }}</v-chip>'],
  ['          تكيّف: {{ detail.effective_level }}', '          {{ t(\'student.languages.scenarios.detail.adaptive\', { level: detail.effective_level }) }}'],
  ['<div class="text-caption font-weight-bold text-medium-emphasis mb-2">ستلعب دور</div>', '<div class="text-caption font-weight-bold text-medium-emphasis mb-2">{{ t(\'student.languages.scenarios.detail.studentRole\') }}</div>'],
  ['<div class="text-caption font-weight-bold text-medium-emphasis mb-2">شخصية الذكاء الاصطناعي</div>', '<div class="text-caption font-weight-bold text-medium-emphasis mb-2">{{ t(\'student.languages.scenarios.detail.aiRole\') }}</div>'],
  ['<div class="text-caption font-weight-bold text-medium-emphasis mb-2">المهارات المستهدفة</div>', '<div class="text-caption font-weight-bold text-medium-emphasis mb-2">{{ t(\'student.languages.scenarios.detail.targetSkills\') }}</div>'],
  ['<div class="text-caption text-medium-emphasis mb-1">الرسالة الافتتاحية</div>', '<div class="text-caption text-medium-emphasis mb-1">{{ t(\'student.languages.scenarios.detail.opening\') }}</div>'],
  [`        {{ detail.locked ? \`مقفل — يتطلب \${detail.level_min}\` : 'بدء السيناريو' }}`, `        {{ detail.locked ? t('student.languages.scenarios.detail.locked', { level: detail.level_min }) : t('student.languages.scenarios.detail.start') }}`],
  ["import { onMounted, ref } from 'vue'", "import { onMounted, ref } from 'vue'\nimport { useI18n } from 'vue-i18n'"],
  ['const route = useRoute()', "const { t } = useI18n()\nconst route = useRoute()"],
  ["error.value = e?.response?.data?.detail || 'تعذر تحميل السيناريو'", "error.value = e?.response?.data?.detail || t('student.languages.scenarios.detail.errors.load')"],
  ["error.value = e?.response?.data?.detail || 'تعذر بدء السيناريو'", "error.value = e?.response?.data?.detail || t('student.languages.scenarios.detail.errors.start')"],
])

// ── Scenario conversation ──
patch('src/views/student/languages/StudentLanguageScenarioConversationView.vue', [
  ['eyebrow="السيناريوهات"', ':eyebrow="t(\'student.languages.scenarios.eyebrow\')"'],
  [`:title="session?.scenario?.title_ar || session?.scenario?.title_en || 'محادثة'"`, `:title="session?.scenario?.title_ar || session?.scenario?.title_en || t('student.languages.scenarios.conversation.defaultTitle')"`],
  ['<v-btn size="small" variant="text" prepend-icon="mdi-arrow-right" @click="goBack">السيناريوهات</v-btn>', '<v-btn size="small" variant="text" prepend-icon="mdi-arrow-right" @click="goBack">{{ t(\'student.languages.scenarios.conversation.back\') }}</v-btn>'],
  ['        المستوى {{ session.effective_level }}', '        {{ t(\'student.languages.scenarios.conversation.level\', { level: session.effective_level }) }}'],
  ['        إنهاء والحصول على التقييم', '        {{ t(\'student.languages.scenarios.conversation.finish\') }}'],
  ['<span class="text-caption">جاري التفكير…</span>', '<span class="text-caption">{{ t(\'student.languages.scenarios.conversation.thinking\') }}</span>'],
  [`            {{ recording ? 'إيقاف' : 'تحدّث' }}`, `            {{ recording ? t('student.languages.scenarios.conversation.stop') : t('student.languages.scenarios.conversation.speak') }}`],
  ['<span v-if="recording" class="text-caption text-error">جاري التسجيل…</span>', '<span v-if="recording" class="text-caption text-error">{{ t(\'student.languages.scenarios.conversation.recording\') }}</span>'],
  ['placeholder="أو اكتب ردّك بالإنجليزية…"', ':placeholder="t(\'student.languages.scenarios.conversation.placeholder\')"'],
  ["import { nextTick, onMounted, ref } from 'vue'", "import { nextTick, onMounted, ref } from 'vue'\nimport { useI18n } from 'vue-i18n'"],
  ['const route = useRoute()', "const { t } = useI18n()\nconst route = useRoute()"],
  ["error.value = e?.response?.data?.detail || 'تعذر تحميل الجلسة'", "error.value = e?.response?.data?.detail || t('student.languages.scenarios.conversation.errors.load')"],
  ["error.value = e?.response?.data?.detail || `تعذر ${t('student.languages.common.submit')} الرسالة`", "error.value = e?.response?.data?.detail || t('student.languages.scenarios.conversation.errors.message')"],
  ["error.value = e?.response?.data?.detail || 'تعذر معالجة الصوت'", "error.value = e?.response?.data?.detail || t('student.languages.scenarios.conversation.errors.voice')"],
  ["error.value = e?.response?.data?.detail || 'تعذر إنهاء الجلسة'", "error.value = e?.response?.data?.detail || t('student.languages.scenarios.conversation.errors.end')"],
])

// ── Scenario completion ──
patch('src/views/student/languages/StudentLanguageScenarioCompletionView.vue', [
  ['eyebrow="السيناريوهات"', ':eyebrow="t(\'student.languages.scenarios.eyebrow\')"'],
  ['title="اكتمل السيناريو"', ':title="t(\'student.languages.scenarios.completion.title\')"'],
  ['subtitle="ملخص أدائك"', ':subtitle="t(\'student.languages.scenarios.completion.subtitle\')"'],
  [`<div class="text-h6 mb-1">{{ feedback.scenario?.title_ar || feedback.scenario?.title_en || 'انتهى السيناريو' }}</div>`, `<div class="text-h6 mb-1">{{ feedback.scenario?.title_ar || feedback.scenario?.title_en || t('student.languages.scenarios.completion.defaultTitle') }}</div>`],
  ['<div class="text-subtitle-2 font-weight-bold mb-2">ما نجح</div>', '<div class="text-subtitle-2 font-weight-bold mb-2">{{ t(\'student.languages.scenarios.completion.wentWell\') }}</div>'],
  ['<div class="text-subtitle-2 font-weight-bold mb-2">ما يحتاج تحسين</div>', '<div class="text-subtitle-2 font-weight-bold mb-2">{{ t(\'student.languages.scenarios.completion.toImprove\') }}</div>'],
  ['<div class="text-subtitle-2 font-weight-bold mb-2">التصحيحات</div>', '<div class="text-subtitle-2 font-weight-bold mb-2">{{ t(\'student.languages.scenarios.completion.corrections\') }}</div>'],
  ['<div class="text-subtitle-2 font-weight-bold mb-2">مفردات مقترحة</div>', '<div class="text-subtitle-2 font-weight-bold mb-2">{{ t(\'student.languages.scenarios.completion.vocabulary\') }}</div>'],
  ['<div class="text-subtitle-2 font-weight-bold mb-2">السيناريو التالي الموصى به</div>', '<div class="text-subtitle-2 font-weight-bold mb-2">{{ t(\'student.languages.scenarios.completion.nextRecommended\') }}</div>'],
  ['            ابدأ', '            {{ t(\'student.languages.scenarios.completion.start\') }}'],
  ['<v-btn color="secondary" variant="flat" @click="goLibrary">تصفّح السيناريوهات</v-btn>', '<v-btn color="secondary" variant="flat" @click="goLibrary">{{ t(\'student.languages.scenarios.completion.browse\') }}</v-btn>'],
  ['<v-alert v-else type="warning" variant="tonal">لا يتوفر تقييم لهذه الجلسة.</v-alert>', '<v-alert v-else type="warning" variant="tonal">{{ t(\'student.languages.scenarios.completion.noFeedback\') }}</v-alert>'],
  ["import { computed, onMounted, ref } from 'vue'", "import { computed, onMounted, ref } from 'vue'\nimport { useI18n } from 'vue-i18n'"],
  ['const route = useRoute()', "const { t } = useI18n()\nconst route = useRoute()"],
  [`    { key: 'communication', label: 'تواصل', value: scores.communication ?? 0 },
    { key: 'grammar', label: 'قواعد', value: scores.grammar ?? 0 },
    { key: 'vocabulary', label: 'مفردات', value: scores.vocabulary ?? 0 },
    { key: 'fluency', label: 'طلاقة', value: scores.fluency ?? 0 },`, `    { key: 'communication', label: t('student.languages.scenarios.scores.communication'), value: scores.communication ?? 0 },
    { key: 'grammar', label: t('student.languages.scenarios.scores.grammar'), value: scores.grammar ?? 0 },
    { key: 'vocabulary', label: t('student.languages.scenarios.scores.vocabulary'), value: scores.vocabulary ?? 0 },
    { key: 'fluency', label: t('student.languages.scenarios.scores.fluency'), value: scores.fluency ?? 0 },`],
])

// ── Curriculum ──
patch('src/views/student/languages/StudentLanguageCurriculumView.vue', [
  ['eyebrow="تعلّم اللغات"', ':eyebrow="t(\'student.languages.hub.header.eyebrow\')"'],
  ['title="مسارك التعليمي"', ':title="t(\'student.languages.curriculum.title\')"'],
  [`subtitle="أين أنت اليوم — وما {{ t('student.lesson.header.nextStep') }} في رحلتك"`, `:subtitle="t('student.languages.curriculum.subtitle')"`],
  ['<div class="text-subtitle-2 mb-2">القواعد</div>', '<div class="text-subtitle-2 mb-2">{{ t(\'student.languages.curriculum.rules\') }}</div>'],
  ['<div class="text-subtitle-2 mb-2">أمثلة</div>', '<div class="text-subtitle-2 mb-2">{{ t(\'student.languages.curriculum.examples\') }}</div>'],
  ['<v-btn color="secondary" variant="flat" block @click="practiceFromLesson">انتقل للتمرين</v-btn>', '<v-btn color="secondary" variant="flat" block @click="practiceFromLesson">{{ t(\'student.languages.curriculum.goPractice\') }}</v-btn>'],
  ["error.value = getErrorMessage(e, 'تعذر تحميل اختبار الترقية')", "error.value = getErrorMessage(e, t('student.languages.curriculum.errors.promotion'))"],
  ["error.value = getErrorMessage(e, `تعذر ${t('student.languages.common.submit')} الاختبار`)", "error.value = getErrorMessage(e, t('student.languages.curriculum.errors.submitTest'))"],
  ["error.value = getErrorMessage(e, 'تعذر تحميل الدرس')", "error.value = getErrorMessage(e, t('student.languages.curriculum.errors.loadLesson'))"],
  ["error.value = getErrorMessage(e, 'تعذر تحميل المسار التعليمي')", "error.value = getErrorMessage(e, t('student.languages.curriculum.errors.loadPath'))"],
])

// ── Curriculum useI18n ──
patch('src/views/student/languages/StudentLanguageCurriculumView.vue', [
  ["import { computed, onMounted, ref } from 'vue'", "import { computed, onMounted, ref } from 'vue'\nimport { useI18n } from 'vue-i18n'"],
  ['const router = useRouter()', "const { t } = useI18n()\nconst router = useRouter()"],
])

// ── Placement ──
patch('src/views/student/languages/StudentLanguagePlacementView.vue', [
  ['eyebrow="تعلّم اللغات"', ':eyebrow="t(\'student.languages.hub.header.eyebrow\')"'],
  ['title="اختبار تحديد المستوى"', ':title="t(\'student.languages.placement.title\')"'],
  ['subtitle="أجب على الأسئلة الأربعة المهارات لتحديد مستواك"', ':subtitle="t(\'student.languages.placement.subtitle\')"'],
  [`            {{ stepLabel }} — سؤال {{ currentIndexInStep + 1 }} / {{ currentStepQuestions.length }}`, `            {{ t('student.languages.placement.progress', { step: stepLabel, current: currentIndexInStep + 1, total: currentStepQuestions.length }) }}`],
  ['            {{ totalAnswered }} / {{ totalQuestions }} مُجاب', '            {{ t(\'student.languages.placement.answered\', { answered: totalAnswered, total: totalQuestions }) }}'],
  ['            سجّل إجابتك صوتياً. سيتم حفظ التسجيل تلقائياً.', '            {{ t(\'student.languages.placement.speaking.hint\') }}'],
  ['            الحد الأدنى: {{ speakingMinSeconds }} ثانية', '            {{ t(\'student.languages.placement.speaking.minimum\', { seconds: speakingMinSeconds }) }}'],
  ['            {{ recordingElapsed }} / {{ speakingMinSeconds }} ثانية', '            {{ t(\'student.languages.placement.speaking.elapsed\', { elapsed: recordingElapsed, total: speakingMinSeconds }) }}'],
  ['              بدء التسجيل', '              {{ t(\'student.languages.placement.startRecording\') }}'],
  ['              إيقاف', '              {{ t(\'student.languages.placement.stopRecording\') }}'],
  ['<div class="text-caption text-medium-emphasis mb-1">آخر تسجيل محفوظ</div>', '<div class="text-caption text-medium-emphasis mb-1">{{ t(\'student.languages.placement.speaking.lastRecording\') }}</div>'],
  ['              المدة المحفوظة: {{ savedSpeakingDuration }} ثانية', '              {{ t(\'student.languages.placement.speaking.savedDuration\', { seconds: savedSpeakingDuration }) }}'],
  ['<v-btn variant="tonal" :disabled="isFirst" @click="prev">السابق</v-btn>', '<v-btn variant="tonal" :disabled="isFirst" @click="prev">{{ t(\'student.languages.placement.prev\') }}</v-btn>'],
  ['<v-btn v-if="!isLast" color="secondary" variant="flat" @click="next">التالي</v-btn>', '<v-btn v-if="!isLast" color="secondary" variant="flat" @click="next">{{ t(\'student.languages.placement.next\') }}</v-btn>'],
  ['              إنهاء وإظهار النتائج', '              {{ t(\'student.languages.placement.finishCta\') }}'],
  ['<div class="text-h6 font-weight-bold">نتيجة تحديد المستوى</div>', '<div class="text-h6 font-weight-bold">{{ t(\'student.languages.placement.results.title\') }}</div>'],
  ['<div class="text-caption text-medium-emphasis">المنهجية: {{ results.overall_calculation_method || \'bottleneck\' }}</div>', '<div class="text-caption text-medium-emphasis">{{ t(\'student.languages.placement.results.method\', { method: results.overall_calculation_method || \'bottleneck\' }) }}</div>'],
  ['            المستوى العام: {{ results.overall_level || \'—\' }}', '            {{ t(\'student.languages.placement.results.overallLevel\', { level: results.overall_level || \'—\' }) }}'],
  ['<strong>نقطة القوة:</strong>', '<strong>{{ t(\'student.languages.placement.results.strength\') }}</strong>'],
  ['<strong>محور التركيز:</strong>', '<strong>{{ t(\'student.languages.placement.results.focus\') }}</strong>'],
  ['<strong>المدة التقديرية للمسار:</strong>', '<strong>{{ t(\'student.languages.placement.results.duration\') }}</strong>'],
  ['            (تقدير مبدئي — سيتم تحسينه في لوحة التعلّم)', '            {{ t(\'student.languages.placement.results.durationNote\') }}'],
  ['<v-btn color="secondary" variant="flat" @click="startJourney">ابدأ رحلة التعلّم</v-btn>', '<v-btn color="secondary" variant="flat" @click="startJourney">{{ t(\'student.languages.placement.startJourney\') }}</v-btn>'],
  ["import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'\nimport { useRouter } from 'vue-router'", "import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'\nimport { useI18n } from 'vue-i18n'\nimport { useRouter } from 'vue-router'"],
  ['const router = useRouter()', "const { t } = useI18n()\nconst router = useRouter()"],
  [`const steps = [
  { key: 'reading', label: 'القراءة' },
  { key: 'listening', label: 'الاستماع' },
  { key: 'writing', label: 'الكتابة' },
  { key: 'speaking', label: 'التحدث' },
]`, `const steps = computed(() => [
  { key: 'reading', label: t('student.languages.skills.reading') },
  { key: 'listening', label: t('student.languages.skills.listening') },
  { key: 'writing', label: t('student.languages.skills.writing') },
  { key: 'speaking', label: t('student.languages.skills.speaking') },
])`],
  ['const stepIndex = computed(() => steps.findIndex((s) => s.key === activeStep.value))', 'const stepIndex = computed(() => steps.value.findIndex((s) => s.key === activeStep.value))'],
  ['const stepLabel = computed(() => steps.find((s) => s.key === activeStep.value)?.label || \'\')', 'const stepLabel = computed(() => steps.value.find((s) => s.key === activeStep.value)?.label || \'\')'],
  ['const isLast = computed(() => stepIndex.value === steps.length - 1 && currentIndexInStep.value >= currentStepQuestions.value.length - 1)', 'const isLast = computed(() => stepIndex.value === steps.value.length - 1 && currentIndexInStep.value >= currentStepQuestions.value.length - 1)'],
  ['  if (stepIndex.value < steps.length - 1) {\n    activeStep.value = steps[stepIndex.value + 1].key', '  if (stepIndex.value < steps.value.length - 1) {\n    activeStep.value = steps.value[stepIndex.value + 1].key'],
  ['    activeStep.value = steps[stepIndex.value - 1].key', '    activeStep.value = steps.value[stepIndex.value - 1].key'],
  ["loadError.value = getErrorMessage(e, 'تعذر حفظ الإجابة')", "loadError.value = getErrorMessage(e, t('student.languages.placement.errors.save'))"],
  [`        ? \`أكمل سؤال التحدث: \${promptText}\`
        : 'أكمل جميع أسئلة التحدث قبل إنهاء الاختبار'`, `        ? t('student.languages.placement.errors.speakingComplete', { prompt: promptText })
        : t('student.languages.placement.errors.speakingAll')`],
  ["loadError.value = getErrorMessage(e, 'تعذر إنهاء اختبار تحديد المستوى')", "loadError.value = getErrorMessage(e, t('student.languages.placement.errors.submit'))"],
  ["loadError.value = `التسجيل فارغ — ${t('student.languages.common.retry')}`", "loadError.value = t('student.languages.placement.emptyRecording')"],
  ["loadError.value = getErrorMessage(e, 'تعذر بدء التسجيل')", "loadError.value = getErrorMessage(e, t('student.languages.placement.errors.recording'))"],
  ["loadError.value = getErrorMessage(e, 'تعذر رفع التسجيل')", "loadError.value = getErrorMessage(e, t('student.languages.placement.errors.upload'))"],
  ["const msg = getErrorMessage(e, 'تعذر بدء اختبار تحديد المستوى')", "const msg = getErrorMessage(e, t('student.languages.placement.errors.start'))"],
  ["const ok = window.confirm('لديك إجابات غير محفوظة. هل تريد المغادرة؟')", "const ok = window.confirm(t('student.languages.placement.leaveConfirm'))"],
  [`  const map = {
    reading: 'القراءة',
    listening: 'الاستماع',
    writing: 'الكتابة',
    speaking: 'التحدث',
  }`, `  const map = {
    reading: t('student.languages.skills.reading'),
    listening: t('student.languages.skills.listening'),
    writing: t('student.languages.skills.writing'),
    speaking: t('student.languages.skills.speaking'),
  }`],
  ["  if (weeks === 1) return 'حوالي أسبوع واحد'\n  if (weeks === 2) return 'حوالي أسبوعين'\n  return `حوالي ${weeks} أسابيع`", "  if (weeks === 1) return t('student.languages.placement.duration.oneWeek')\n  if (weeks === 2) return t('student.languages.placement.duration.twoWeeks')\n  return t('student.languages.placement.duration.weeks', { n: weeks })"],
])

console.log('Done patching language views (batch 4).')
