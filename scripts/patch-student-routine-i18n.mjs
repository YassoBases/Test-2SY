/**
 * Migrates StudentRoutineView.vue to full i18n.
 */
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const fp = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'src/views/student/StudentRoutineView.vue')
let s = fs.readFileSync(fp, 'utf8')

function rep(from, to) {
  if (!s.includes(from)) {
    console.warn('[skip]', from.slice(0, 70))
    return
  }
  s = s.replace(from, to)
}

// ── Script: add useI18n ──
rep(
  "import { computed, nextTick, onMounted, ref, watch } from 'vue'\nimport RoutineWeekPreview",
  "import { computed, nextTick, onMounted, ref, watch } from 'vue'\nimport { useI18n } from 'vue-i18n'\nimport RoutineWeekPreview",
)
rep(
  "const step = ref('onboarding')",
  "const { t } = useI18n()\n\nconst step = ref('onboarding')",
)

// ── Static data → i18n ──
rep(
  `const grades = [
  { value: '7', label: 'سابع' }, { value: '8', label: 'ثامن' }, { value: '9', label: 'تاسع' },
  { value: '10', label: 'عاشر' }, { value: '11', label: 'حادي عشر' }, { value: '12', label: 'ثاني عشر' },
  { value: 'bac', label: 'بكالوريا' },
]`,
  `const GRADE_VALUES = ['7', '8', '9', '10', '11', '12', 'bac']
const grades = computed(() =>
  GRADE_VALUES.map((value) => ({
    value,
    label: t(\`student.routine.grades.\${value === 'bac' ? 'bac' : 'g' + value}\`),
  })),
)`,
)

rep(
  `const dayNames = [
  { value: 0, label: 'اثنين' }, { value: 1, label: 'ثلاثاء' }, { value: 2, label: 'أربعاء' },
  { value: 3, label: 'خميس' }, { value: 4, label: 'جمعة' }, { value: 5, label: 'سبت' }, { value: 6, label: 'أحد' },
]`,
  `const DAY_SHORT_KEYS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
const dayNames = computed(() =>
  DAY_SHORT_KEYS.map((key, i) => ({ value: i, label: t(\`student.routine.days.\${key}\`) })),
)`,
)

rep(
  `const GRADE_INFO = {
  '7-9':    { sleep_ideal: '22:00', study_hours: '1-2 س',  notes: 'توازن دراسة ونشاط' },
  '10-11':  { sleep_ideal: '23:00', study_hours: '2-3 س',  notes: 'راحة قبل الدراسة' },
  '12-bac': { sleep_ideal: '23:30', study_hours: '4-6 س',  notes: 'نوم 7 ساعات لا تنقص' },
}
const gradeInfo = computed(() => {
  const g = form.value.grade_level
  if (['7','8','9'].includes(g)) return GRADE_INFO['7-9']
  if (['10','11'].includes(g)) return GRADE_INFO['10-11']
  return GRADE_INFO['12-bac']
})`,
  `const GRADE_INFO_BASE = {
  '7-9':    { sleep_ideal: '22:00', studyKey: '79' },
  '10-11':  { sleep_ideal: '23:00', studyKey: '1011' },
  '12-bac': { sleep_ideal: '23:30', studyKey: '12bac' },
}
const gradeInfo = computed(() => {
  const g = form.value.grade_level
  const base = ['7', '8', '9'].includes(g) ? GRADE_INFO_BASE['7-9']
    : ['10', '11'].includes(g) ? GRADE_INFO_BASE['10-11']
    : GRADE_INFO_BASE['12-bac']
  return {
    sleep_ideal: base.sleep_ideal,
    study_hours: t(\`student.routine.gradeInfo.studyHours.\${base.studyKey}\`),
    notes: t(\`student.routine.gradeInfo.notes.\${base.studyKey}\`),
  }
})`,
)

rep(
  `const DAY_STAGE_LABELS = {
  day_6: 'الأحد', day_0: 'الاثنين', day_1: 'الثلاثاء', day_2: 'الأربعاء',
  day_3: 'الخميس', day_4: 'الجمعة', day_5: 'السبت',
}`,
  `const DAY_STAGE_KEYS = {
  day_6: 'sunday', day_0: 'monday', day_1: 'tuesday', day_2: 'wednesday',
  day_3: 'thursday', day_4: 'friday', day_5: 'saturday',
}
const DAY_STAGE_LABELS = computed(() =>
  Object.fromEntries(
    Object.entries(DAY_STAGE_KEYS).map(([k, dk]) => [k, t(\`student.routine.days.\${dk}\`)]),
  ),
)`,
)

rep(
  '    label: DAY_STAGE_LABELS[s],',
  '    label: DAY_STAGE_LABELS.value[s],',
)

rep(
  `const progressLabel = computed(() => {
  const done = dayProgress.value.filter(d => d.status === 'done').length
  if (done === 0) return 'لسا ما بدأنا — يلا نحكي عن أول يوم بأسبوعك'
  if (done === DAY_STAGE_ORDER.length) return 'تمام! كل الأيام جاهزة — برنامجك قاعد يتبنى الآن'
  return \`جمعنا \${done} من \${DAY_STAGE_ORDER.length} أيام — كمل معي شوي وخلصنا\`
})`,
  `const progressLabel = computed(() => {
  const done = dayProgress.value.filter(d => d.status === 'done').length
  if (done === 0) return t('student.routine.progress.notStarted')
  if (done === DAY_STAGE_ORDER.length) return t('student.routine.progress.allDone')
  return t('student.routine.progress.partial', { done, total: DAY_STAGE_ORDER.length })
})`,
)

rep(
  "messages.value.push({ role: 'assistant', content: 'مرحباً! أنا جاهز لبناء برنامجك اليومي الكامل.\\nخبّرني: شو عندك يوم الاثنين؟ من أي ساعة لأي ساعة؟' })",
  "messages.value.push({ role: 'assistant', content: t('student.routine.messages.welcome') })",
)

rep(
  "messages.value.push({ role: 'user', content: `بدي أعدّل يوم ${label} 📝` })",
  "messages.value.push({ role: 'user', content: t('student.routine.messages.editDay', { day: label }) })",
)

rep(
  "} catch { reviewText.value = 'البرنامج جاهز! يمكنك مشاهدته الآن.' }",
  "} catch { reviewText.value = t('student.routine.messages.scheduleReady') }",
)

rep(
  'messages.value.push({ role: \'assistant\', content: `حدث خطأ أثناء بناء البرنامج. ${t(\'student.languages.common.retry\')}.` })',
  "messages.value.push({ role: 'assistant', content: t('student.routine.messages.buildError') })",
)

rep(
  "messages.value.push({ role: 'assistant', content: `حدث خطأ، ${t('student.languages.common.retry')}.` })",
  "messages.value.push({ role: 'assistant', content: t('student.routine.messages.genericError') })",
)

rep(
  "} catch { messages.value.push({ role: 'assistant', content: `حدث خطأ في حفظ البرنامج. ${t('student.languages.common.retry')}.` }) }",
  "} catch { messages.value.push({ role: 'assistant', content: t('student.routine.messages.saveError') }) }",
)

rep(
  "messages.value.push({ role: 'assistant', content: `حدث خطأ في رفع الصورة. ${t('student.languages.common.retry')}.` })",
  "messages.value.push({ role: 'assistant', content: t('student.routine.messages.uploadError') })",
)

rep(
  'else messages.value.push({ role: \'assistant\', content: `تم حفظ ${res.saved} امتحان ✅`, ...extra })',
  "else messages.value.push({ role: 'assistant', content: t('student.routine.messages.examsSaved', { count: res.saved }), ...extra })",
)

rep(
  "const text = valid.map(e => `امتحان ${e.subject} بتاريخ ${e.date} الساعة ${e.time || '9:00'}`).join('، ')",
  "const text = valid.map(e => t('student.routine.messages.examLine', { subject: e.subject, date: e.date, time: e.time || '9:00' })).join('، ')",
)

rep(
  `const ARABIC_DAY_NAMES = ['الأحد', 'الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت']
const ARABIC_MONTH_NAMES = ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو', 'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر']
function formatExamDate(dateStr) {
  if (!dateStr) return 'تاريخ غير محدد'`,
  `function formatExamDate(dateStr) {
  if (!dateStr) return t('student.routine.exams.unknownDate')`,
)

// formatExamDate body - replace Arabic month logic with Intl
rep(
  `  const d = new Date(dateStr)
  if (isNaN(d.getTime())) return dateStr
  const dayName = ARABIC_DAY_NAMES[d.getDay()]
  const day = d.getDate()
  const month = ARABIC_MONTH_NAMES[d.getMonth()]
  return \`\${dayName} \${day} \${month}\`
}`,
  `  try {
    return new Date(dateStr).toLocaleDateString(undefined, { weekday: 'long', day: 'numeric', month: 'long' })
  } catch {
    return dateStr
  }
}`,
)

rep(
  "const scheduleDayLabels = ['الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت', 'الأحد']",
  'const scheduleDayLabels = computed(() => DAY_STAGE_ORDER.map((s) => DAY_STAGE_LABELS.value[s]))',
)

// activityLabel helper after activityIcons
rep(
  `const activityIcons = {
  'رياضة': 'mdi-basketball',
  'دروس خاصة': 'mdi-account-school-outline',
  'نشاط ديني': 'mdi-mosque',
  'موسيقى': 'mdi-music-note-outline',
  'لغات': 'mdi-translate',
}`,
  `const activityIcons = {
  'رياضة': 'mdi-basketball',
  'دروس خاصة': 'mdi-account-school-outline',
  'نشاط ديني': 'mdi-mosque',
  'موسيقى': 'mdi-music-note-outline',
  'لغات': 'mdi-translate',
}
const ACTIVITY_LABEL_KEYS = {
  'رياضة': 'sport',
  'دروس خاصة': 'tutoring',
  'نشاط ديني': 'religious',
  'موسيقى': 'music',
  'لغات': 'languages',
}
function activityLabel(act) {
  const key = ACTIVITY_LABEL_KEYS[act]
  return key ? t(\`student.routine.activities.\${key}\`) : act
}
function dayTypeLabel(type) {
  if (type === 'مدرسة') return t('student.routine.dayType.school')
  if (type === 'عطلة') return t('student.routine.dayType.weekend')
  return type
}`,
)

// Fix scheduleDayLabels usage if .value needed
rep('scheduleDayLabels[', 'scheduleDayLabels.value[')

// ── Template ──
rep(
  '<p class="text-caption text-medium-emphasis">ذكاء اصطناعي يبني برنامجك الكامل — من الصحيان للنوم</p>',
  '<p class="text-caption text-medium-emphasis">{{ t(\'student.routine.subtitle\') }}</p>',
)
rep('<h3 class="text-h6 font-weight-bold mb-1">خليني أتعرف عليك أولاً</h3>', '<h3 class="text-h6 font-weight-bold mb-1">{{ t(\'student.routine.onboarding.hero.title\') }}</h3>')
rep('<p class="text-caption text-medium-emphasis mb-0">شوية معلومات بسيطة وبنبني برنامجك المثالي سوا 🚀</p>', '<p class="text-caption text-medium-emphasis mb-0">{{ t(\'student.routine.onboarding.hero.subtitleEmoji\') }}</p>')
rep('<p class="text-body-1 font-weight-bold mb-0">في أي صف أنت؟</p>', '<p class="text-body-1 font-weight-bold mb-0">{{ t(\'student.routine.onboarding.grade.title\') }}</p>')
rep('<p class="text-caption text-medium-emphasis mb-0">هذا بيساعدنا نخصص برنامجك على عمرك</p>', '<p class="text-caption text-medium-emphasis mb-0">{{ t(\'student.routine.onboarding.grade.subtitle\') }}</p>')
rep('<p class="text-body-1 font-weight-bold mb-0">مواعيد المدرسة</p>', '<p class="text-body-1 font-weight-bold mb-0">{{ t(\'student.routine.onboarding.school.title\') }}</p>')
rep('<p class="text-caption text-medium-emphasis mb-0">من أي ساعة لأي ساعة دوامك؟</p>', '<p class="text-caption text-medium-emphasis mb-0">{{ t(\'student.routine.onboarding.school.subtitle\') }}</p>')
rep('label="من"', ':label="t(\'student.routine.common.from\')"')
rep('label="لـ"', ':label="t(\'student.routine.common.to\')"')
rep('<p class="text-body-1 font-weight-bold mb-0">الصحيان والنوم</p>', '<p class="text-body-1 font-weight-bold mb-0">{{ t(\'student.routine.onboarding.sleep.title\') }}</p>')
rep('<p class="text-caption text-medium-emphasis mb-0">روتين النوم أساس يومك الناجح</p>', '<p class="text-caption text-medium-emphasis mb-0">{{ t(\'student.routine.onboarding.sleep.subtitle\') }}</p>')
rep('label="وقت الصحيان"', ':label="t(\'student.routine.onboarding.wakeTime\')"')
rep('label="وقت النوم"', ':label="t(\'student.routine.onboarding.sleepTime\')"')
rep('<p class="text-body-1 font-weight-bold mb-0">أيام المدرسة</p>', '<p class="text-body-1 font-weight-bold mb-0">{{ t(\'student.routine.onboarding.schoolDays.title\') }}</p>')
rep('<p class="text-caption text-medium-emphasis mb-0">اختار الأيام يلي عندك فيها دوام</p>', '<p class="text-caption text-medium-emphasis mb-0">{{ t(\'student.routine.onboarding.schoolDays.subtitle\') }}</p>')
rep('<!-- 5. الأ{{ t(\'student.teacherContact.status\') }}ة -->', '<!-- 5. activities -->')
rep('<p class="text-body-1 font-weight-bold mb-0">عندك نشاطات إضافية؟</p>', '<p class="text-body-1 font-weight-bold mb-0">{{ t(\'student.routine.onboarding.activities.heading\') }}</p>')
rep('<p class="text-caption text-medium-emphasis mb-0">رياضة، دروس خاصة، أو أي شي بياخد من وقتك أسبوعياً</p>', '<p class="text-caption text-medium-emphasis mb-0">{{ t(\'student.routine.onboarding.activities.subtitle\') }}</p>')
rep('<p class="text-body-2 font-weight-bold mb-0">{{ act }} — متى وأي أيام؟</p>', '<p class="text-body-2 font-weight-bold mb-0">{{ t(\'student.routine.onboarding.activities.when\', { name: activityLabel(act) }) }}</p>')
rep('<p class="text-caption mb-1 text-medium-emphasis">الأيام</p>', '<p class="text-caption mb-1 text-medium-emphasis">{{ t(\'student.routine.onboarding.activities.days\') }}</p>')
rep('label="المادة"', ':label="t(\'student.routine.onboarding.activities.subject\')"')
rep('placeholder="رياضيات، كيمياء..."', ':placeholder="t(\'student.routine.onboarding.activities.subjectPlaceholder\')"')
rep('<span>التالي — حكي مع المساعد</span>', '<span>{{ t(\'student.routine.onboarding.nextCta\') }}</span>')
rep('<span class="text-body-2 font-weight-bold">الصف {{ form.grade_level }} —</span>', '<span class="text-body-2 font-weight-bold">{{ t(\'student.routine.preview.gradeChip\', { grade: form.grade_level }) }} —</span>')
rep('<v-chip size="x-small" color="primary" variant="tonal">نوم: {{ gradeInfo.sleep_ideal }}</v-chip>', '<v-chip size="x-small" color="primary" variant="tonal">{{ t(\'student.routine.gradeInfo.sleep\', { time: gradeInfo.sleep_ideal }) }}</v-chip>')
rep('<v-chip size="x-small" color="success" variant="tonal">دراسة: {{ gradeInfo.study_hours }}</v-chip>', '<v-chip size="x-small" color="success" variant="tonal">{{ t(\'student.routine.gradeInfo.study\', { hours: gradeInfo.study_hours }) }}</v-chip>')
rep('<div class="text-caption" style="color:rgba(34,211,238,0.6);line-height:1">مساعدك الذكي</div>', '<div class="text-caption" style="color:rgba(34,211,238,0.6);line-height:1">{{ t(\'student.routine.chat.assistantLabel\') }}</div>')
rep('<span>جدول امتحاناتك القادمة</span>', '<span>{{ t(\'student.routine.chat.examTable.title\') }}</span>')
rep('<span class="exam-col-label">المادة</span>', '<span class="exam-col-label">{{ t(\'student.routine.chat.examTable.subject\') }}</span>')
rep('<span class="exam-col-label">التاريخ</span>', '<span class="exam-col-label">{{ t(\'student.routine.chat.examTable.date\') }}</span>')
rep('<span class="exam-col-label">الوقت</span>', '<span class="exam-col-label">{{ t(\'student.routine.chat.examTable.time\') }}</span>')
rep("{{ ex.subject || 'مادة غير محددة' }}", "{{ ex.subject || t('student.routine.chat.examTable.unknownSubject') }}")
rep("{{ ex.time || 'غير محدد' }}", "{{ ex.time || t('student.routine.chat.examTable.unknownTime') }}")
rep('<span>برنامجك الأسبوعي جاهز — هيك حيكون شكله</span>', '<span>{{ t(\'student.routine.chat.scheduleReady\') }}</span>')
rep('<span v-if="!(msg.scheduleCards[String(di)] || []).length" class="sac-empty">يوم فارغ</span>', '<span v-if="!(msg.scheduleCards[String(di)] || []).length" class="sac-empty">{{ t(\'student.routine.chat.emptyDay\') }}</span>')
rep(`<span class="typing-label">{{ t('student.routine.title') }} يكتب...</span>`, `<span class="typing-label">{{ t('student.routine.chat.typingWithName', { name: t('student.routine.chat.assistantLabel') }) }}</span>`)
rep('<span class="pinned-question-label">سؤال للمساعد</span>', '<span class="pinned-question-label">{{ t(\'student.routine.chat.pinnedLabel\') }}</span>')
rep('                رفع جدول الامتحانات', '                {{ t(\'student.routine.chat.uploadExams\') }}')
rep('                إدخال يدوي', '                {{ t(\'student.routine.chat.manualExams\') }}')
rep('<p class="text-caption font-weight-bold mb-2">امتحاناتك القادمة:</p>', '<p class="text-caption font-weight-bold mb-2">{{ t(\'student.routine.chat.upcomingExams\') }}</p>')
rep('placeholder="المادة"', ':placeholder="t(\'student.routine.chat.examTable.subject\')"')
rep('placeholder="الوقت"', ':placeholder="t(\'student.routine.chat.examTable.time\')"')
rep('<v-btn size="x-small" variant="tonal" @click="manualExams.push({subject:\'\',date:\'\',time:\'\'})">+ إضافة</v-btn>', '<v-btn size="x-small" variant="tonal" @click="manualExams.push({subject:\'\',date:\'\',time:\'\'})">{{ t(\'student.routine.chat.addExam\') }}</v-btn>')
rep(`<v-btn size="x-small" color="primary" variant="tonal" @click="sendManualExams">{{ t('student.languages.common.submit') }} للذكاء</v-btn>`, `<v-btn size="x-small" color="primary" variant="tonal" @click="sendManualExams">{{ t('student.routine.chat.submitToAi') }}</v-btn>`)
rep('<h3 class="text-h6 font-weight-bold">معاينة البرنامج</h3>', '<h3 class="text-h6 font-weight-bold">{{ t(\'student.routine.preview.title\') }}</h3>')
rep('<v-icon start>mdi-check</v-icon>تأكيد وحفظ', '<v-icon start>mdi-check</v-icon>{{ t(\'student.routine.preview.confirmSave\') }}')
rep('<p class="text-body-2 font-weight-bold mb-0">راجع معلوماتك قبل ما نبني برنامجك</p>', '<p class="text-body-2 font-weight-bold mb-0">{{ t(\'student.routine.preview.reviewTitle\') }}</p>')
rep(`<p class="text-caption text-medium-emphasis mb-0">تأكد إنها {{ t('student.lesson.quiz.results.correct') }}، أو عدّل أي يوم بالضغط على القلم ✏️</p>`, `<p class="text-caption text-medium-emphasis mb-0">{{ t('student.routine.preview.reviewHint') }}</p>`)
rep('<v-chip size="small" variant="tonal" color="primary" prepend-icon="mdi-school-outline">الصف {{ summaryData.grade_level }}</v-chip>', '<v-chip size="small" variant="tonal" color="primary" prepend-icon="mdi-school-outline">{{ t(\'student.routine.preview.gradeChip\', { grade: summaryData.grade_level }) }}</v-chip>')
rep('<v-chip size="small" variant="tonal" color="info" prepend-icon="mdi-clock-school-outline">المدرسة {{ summaryData.school_start }} – {{ summaryData.school_end }}</v-chip>', '<v-chip size="small" variant="tonal" color="info" prepend-icon="mdi-clock-school-outline">{{ t(\'student.routine.preview.schoolChip\', { start: summaryData.school_start, end: summaryData.school_end }) }}</v-chip>')
rep('<v-chip size="small" variant="tonal" color="warning" prepend-icon="mdi-weather-sunset-up">استيقاظ {{ summaryData.wake_time }}</v-chip>', '<v-chip size="small" variant="tonal" color="warning" prepend-icon="mdi-weather-sunset-up">{{ t(\'student.routine.preview.wakeChip\', { time: summaryData.wake_time }) }}</v-chip>')
rep('<v-chip size="small" variant="tonal" color="secondary" prepend-icon="mdi-weather-night">نوم {{ summaryData.sleep_time }}</v-chip>', '<v-chip size="small" variant="tonal" color="secondary" prepend-icon="mdi-weather-night">{{ t(\'student.routine.preview.sleepChip\', { time: summaryData.sleep_time }) }}</v-chip>')
rep(`                تعديل {{ t('student.routine.settings.title') }}`, `                {{ t('student.routine.preview.editSettings') }}`)
rep('<p class="cs-days-title"><v-icon size="16" color="cyan">mdi-calendar-week</v-icon> أيامك السبعة</p>', '<p class="cs-days-title"><v-icon size="16" color="cyan">mdi-calendar-week</v-icon> {{ t(\'student.routine.preview.sevenDays\') }}</p>')
rep(`<v-chip size="x-small" :color="d.type === 'مدرسة' ? 'primary' : 'success'" variant="tonal">{{ d.type }}</v-chip>`, `<v-chip size="x-small" :color="d.type === 'مدرسة' ? 'primary' : 'success'" variant="tonal">{{ dayTypeLabel(d.type) }}</v-chip>`)
rep('<v-icon start>mdi-rocket-launch-outline</v-icon> تأكيد المعلومات وابني برنامجي', '<v-icon start>mdi-rocket-launch-outline</v-icon> {{ t(\'student.routine.preview.confirmBuild\') }}')
rep('<p class="text-body-2 font-weight-bold mb-0">جاري بناء برنامجك...</p>', '<p class="text-body-2 font-weight-bold mb-0">{{ t(\'student.routine.preview.building\') }}</p>')
rep('<p class="text-caption text-medium-emphasis mb-0">كل ما حكينا عن يوم، رح ينعلّم هون 👇</p>', '<p class="text-caption text-medium-emphasis mb-0">{{ t(\'student.routine.preview.buildingHint\') }}</p>')
rep('text="عدّل هذا اليوم"', ':text="t(\'student.routine.preview.editDay\')"')
rep(`<h3 class="text-h6 font-weight-bold">{{ t('student.lesson.plan.chip.review') }} الذكاء الاصطناعي</h3>`, `<h3 class="text-h6 font-weight-bold">{{ t('student.routine.review.aiTitle') }}</h3>`)
rep('<p class="text-caption text-medium-emphasis">اقتراحات لتحسين برنامجك</p>', '<p class="text-caption text-medium-emphasis">{{ t(\'student.routine.review.subtitle\') }}</p>')
rep('<p class="text-body-2 text-medium-emphasis">الذكاء الاصطناعي يراجع برنامجك...</p>', '<p class="text-body-2 text-medium-emphasis">{{ t(\'student.routine.review.loading\') }}</p>')
rep('<p class="text-body-2 font-weight-bold mb-3">الاقتراحات:</p>', '<p class="text-body-2 font-weight-bold mb-3">{{ t(\'student.routine.review.suggestions\') }}</p>')
rep(`{{ s.priority === 'high' ? 'مهم' : s.priority === 'medium' ? 'متوسط' : 'اختياري' }}`, `{{ s.priority === 'high' ? t('student.routine.review.priority.high') : s.priority === 'medium' ? t('student.routine.review.priority.medium') : t('student.routine.review.priority.low') }}`)
rep('<v-btn variant="tonal" color="secondary" @click="step = \'chat\'"><v-icon start>mdi-pencil</v-icon>تعديل البرنامج</v-btn>', '<v-btn variant="tonal" color="secondary" @click="step = \'chat\'"><v-icon start>mdi-pencil</v-icon>{{ t(\'student.routine.review.editSchedule\') }}</v-btn>')
rep('<v-btn color="primary" size="large" @click="finishReview"><v-icon start>mdi-calendar-check</v-icon>انتهيت — شوف برنامجي</v-btn>', '<v-btn color="primary" size="large" @click="finishReview"><v-icon start>mdi-calendar-check</v-icon>{{ t(\'student.routine.review.finish\') }}</v-btn>')
rep('<h3 class="text-h6 font-weight-bold mb-3">معاينة برنامجك المحفوظ</h3>', '<h3 class="text-h6 font-weight-bold mb-3">{{ t(\'student.routine.review.savedPreview\') }}</h3>')
rep('<h3 class="text-h6 font-weight-bold">برنامجك الأسبوعي</h3>', '<h3 class="text-h6 font-weight-bold">{{ t(\'student.routine.view.weeklyTitle\') }}</h3>')
rep(`<v-icon start>mdi-refresh</v-icon>ت{{ t('student.lesson.card.status.new') }} الأسبوع`, `<v-icon start>mdi-refresh</v-icon>{{ t('student.routine.view.renewWeek') }}`)
rep(`<p class="text-caption text-medium-emphasis mb-0">تعديل بياناتك بدون {{ t('student.lesson.chat.clear.confirmCta') }} البرنامج</p>`, `<p class="text-caption text-medium-emphasis mb-0">{{ t('student.routine.settings.subtitle') }}</p>`)
rep('<p class="text-body-2 mb-2 font-weight-medium">الصف</p>', '<p class="text-body-2 mb-2 font-weight-medium">{{ t(\'student.routine.settings.grade\') }}</p>')
rep('<p class="text-body-2 mb-2 font-weight-medium">وقت المدرسة</p>', '<p class="text-body-2 mb-2 font-weight-medium">{{ t(\'student.routine.settings.schoolTime\') }}</p>')
rep('<p class="text-body-2 mb-2 font-weight-medium">الصحيان والنوم</p>', '<p class="text-body-2 mb-2 font-weight-medium">{{ t(\'student.routine.settings.sleepSection\') }}</p>')
rep('label="صحيان"', ':label="t(\'student.routine.settings.wakeShort\')"')
rep('label="نوم"', ':label="t(\'student.routine.settings.sleepShort\')"')
rep('<p class="text-body-2 mb-2 font-weight-medium">أيام المدرسة</p>', '<p class="text-body-2 mb-2 font-weight-medium">{{ t(\'student.routine.settings.schoolDays\') }}</p>')
rep(`            حذف البرنامج والبدء من {{ t('student.lesson.card.status.new') }}`, `            {{ t('student.routine.settings.deleteSchedule') }}`)
rep('<v-icon start>mdi-check</v-icon>حفظ التعديلات', '<v-icon start>mdi-check</v-icon>{{ t(\'student.routine.settings.saveChanges\') }}')
rep('<h3 class="text-h6 font-weight-bold">حذف البرنامج؟</h3>', '<h3 class="text-h6 font-weight-bold">{{ t(\'student.routine.delete.title\') }}</h3>')
rep(`<p class="text-body-2 text-medium-emphasis mt-2">هذا سي{{ t('student.lesson.chat.clear.confirmCta') }} برنامجك الأسبوعي وسجل المحادثة. {{ t('student.routine.settings.title') }} تبقى.</p>`, `<p class="text-body-2 text-medium-emphasis mt-2">{{ t('student.routine.delete.body') }}</p>`)
rep('<v-btn color="error" :loading="deleting" @click="doDeleteProfile">نعم، احذف</v-btn>', '<v-btn color="error" :loading="deleting" @click="doDeleteProfile">{{ t(\'student.routine.delete.confirm\') }}</v-btn>')
rep('<h3 class="text-h6 font-weight-bold">تأكيد الامتحانات</h3>', '<h3 class="text-h6 font-weight-bold">{{ t(\'student.routine.exams.confirmTitle\') }}</h3>')
rep('<p class="text-caption text-medium-emphasis mb-0">راجع البيانات المستخرجة وعدّلها إذا لزم</p>', '<p class="text-caption text-medium-emphasis mb-0">{{ t(\'student.routine.exams.confirmSubtitle\') }}</p>')
rep(`<p>لم يتم التعرف على امتحانات في {{ t('student.lesson.fallback.tabs.pdf') }}</p>`, `<p>{{ t('student.routine.exams.noneDetected') }}</p>`)
rep('              label="التاريخ"', ':label="t(\'student.routine.chat.examTable.date\')"')
rep('            إضافة امتحان', '            {{ t(\'student.routine.exams.add\') }}')
rep('<v-icon start>mdi-content-save-outline</v-icon>حفظ الامتحانات', '<v-icon start>mdi-content-save-outline</v-icon>{{ t(\'student.routine.exams.save\') }}')

// Display activity labels in onboarding chips only
rep('{{ activityIcons[act] }} {{ act }}', '{{ activityIcons[act] }} {{ activityLabel(act) }}')

fs.writeFileSync(fp, s)
console.log('Patched StudentRoutineView.vue')
