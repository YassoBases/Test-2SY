/**
 * Batch 3: exact-string i18n patches for remaining student components/views.
 * Run: node scripts/migrate-student-i18n.mjs && node scripts/patch-student-i18n-batch3.mjs
 */
import { readFileSync, writeFileSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = join(dirname(fileURLToPath(import.meta.url)), '..')

function ensureI18n(content) {
  if (content.includes('useI18n')) return content
  let out = content.replace(/(<script setup>\n)/, "$1import { useI18n } from 'vue-i18n'\n")
  out = out.replace(/(<script setup>\n(?:import[^\n]+\n)*)/, (m) => `${m}\nconst { t } = useI18n()\n`)
  return out
}

/** @type {Record<string, Array<[string, string]>>} */
const patches = {
  'src/components/student/TeacherContactCard.vue': [
    ['<div class="text-overline text-medium-emphasis mb-2">معلّم المادة</div>', '<div class="text-overline text-medium-emphasis mb-2">{{ t(\'student.teacherContact.label\') }}</div>'],
    ['label="السماح لولي الأمر بالمشاركة"', ':label="t(\'student.teacherContact.includeParent\')"'],
    ['text="يجب الاشتراك بالمادة أولاً للتواصل مع المعلم"', ':text="t(\'student.teacherContact.subscribeTooltip\')"'],
    ['              مراسلة المعلّم', '              {{ t(\'student.teacherContact.message\') }}'],
    ['        مراسلة المعلّم', '        {{ t(\'student.teacherContact.message\') }}'],
    ['        عرض ملف المعلّم', '        {{ t(\'student.teacherContact.viewProfile\') }}'],
    ["const statusLabel = 'نشط'", "const statusLabel = computed(() => t('student.teacherContact.status'))"],
    ["import { computed, ref } from 'vue'", "import { computed, ref } from 'vue'\nimport { useI18n } from 'vue-i18n'"],
    ['defineEmits([', "const { t } = useI18n()\n\ndefineEmits(["],
  ],
  'src/components/student/StudentTeacherProfileDialog.vue': [
    ['{{ profile.subject_name }} — الصف {{ profile.grade }}', "{{ t('student.teacherProfile.subtitle', { subject: profile.subject_name, grade: profile.grade }) }}"],
    ['· {{ profile.student_count }} طالب', "{{ t('student.teacherProfile.studentCount', { n: profile.student_count }) }}"],
    ['<div class="text-overline text-medium-emphasis mb-1">نبذة</div>', '<div class="text-overline text-medium-emphasis mb-1">{{ t(\'student.teacherProfile.bio\') }}</div>'],
    ['<div class="text-overline text-medium-emphasis mb-2">الدورات</div>', '<div class="text-overline text-medium-emphasis mb-2">{{ t(\'student.teacherProfile.courses\') }}</div>'],
    ["import TeacherAvatar from '../onboarding/TeacherAvatar.vue'", "import { useI18n } from 'vue-i18n'\nimport TeacherAvatar from '../onboarding/TeacherAvatar.vue'"],
    ['defineProps({', "const { t } = useI18n()\n\ndefineProps({"],
  ],
  'src/components/student/StudentLinkedParentsSection.vue': [
    ['      أولياء الأمور المرتبطون', '      {{ t(\'student.parents.title\') }}'],
    ['      الحسابات التي يمكنها متابعة تقدّمك — للعرض فقط ولا يمكنك إزالة الربط من هنا', '      {{ t(\'student.parents.subtitle\') }}'],
    ['      لا يوجد أولياء أمور مرتبطون بهذا الحساب', '      {{ t(\'student.parents.empty\') }}'],
    ['            <div class="text-caption text-medium-emphasis">إجمالي المرتبطين</div>', '            <div class="text-caption text-medium-emphasis">{{ t(\'student.parents.summary.total\') }}</div>'],
    ['            <div class="text-caption text-medium-emphasis">نشطون مؤخراً</div>', '            <div class="text-caption text-medium-emphasis">{{ t(\'student.parents.summary.recent\') }}</div>'],
    ["{{ p.display_name?.charAt(0) || 'و' }}", "{{ p.display_name?.charAt(0) || t('student.parents.defaultInitial') }}"],
    ['                  نشط', '                  {{ t(\'student.parents.status.active\') }}'],
    ['                  رُبط: {{ formatSubscriptionDate(p.linked_at) }}', "                  {{ t('student.parents.linkedAt', { date: formatSubscriptionDate(p.linked_at) }) }}"],
    ['                  آخر مشاهدة: {{ formatSubscriptionDate(p.last_viewed_at) }}', "                  {{ t('student.parents.lastSeen', { date: formatSubscriptionDate(p.last_viewed_at) }) }}"],
    ['                <span v-else class="text-medium-emphasis">لم يُسجّل نشاط مشاهدة بعد</span>', '                <span v-else class="text-medium-emphasis">{{ t(\'student.parents.noActivity\') }}</span>'],
    ["getErrorMessage(err, 'تعذر تحميل أولياء الأمور المرتبطين')", "getErrorMessage(err, t('student.parents.errors.load'))"],
  ],
  'src/components/student/lesson/TeacherHelperCard.vue': [
    ['هل لديك سؤال حول هذا الدرس؟', "{{ t('student.lesson.helper.prompt') }}"],
    ['        اسأل المعلّm', '        {{ t(\'student.lesson.helper.cta\') }}'],
  ],
  'src/components/student/lesson/LessonAssistantPanel.vue': [
    ['معك في هذا الدرس', "{{ t('student.lesson.assistant.subtitle') }}"],
  ],
  'src/components/student/lesson/LessonSessionHeader.vue': [
    ['ملف الدرس', "{{ t('student.lesson.header.pdf') }}"],
    ['تقدّم الجلسة', "{{ t('student.lesson.header.sessionProgress') }}"],
    ['الخطوة التالية', "{{ t('student.lesson.header.nextStep') }}"],
  ],
  'src/components/student/LessonPdfViewer.vue': [
    ['جاري تحميل PDF…', "{{ t('student.lesson.pdf.loading') }}"],
    ['تعذر تحميل ملف PDF', "t('student.lesson.pdf.errors.load')"],
  ],
  'src/components/student/QuizResults.vue': [
    ['{{ correct }} من {{ total }} إجابات صحيحة', "{{ t('student.lesson.quiz.results.summary', { correct, total }) }}"],
    ['صحيحة', "{{ t('student.lesson.quiz.results.correct') }}"],
    ['خاطئة', "{{ t('student.lesson.quiz.results.wrong') }}"],
    ['إعادة الاختبار', "{{ t('student.lesson.quiz.results.retry') }}"],
    ['العودة لدوراتي', "{{ t('student.lesson.quiz.results.back') }}"],
  ],
  'src/components/student/home/JourneyHero.vue': [
    ["headline: 'ابدأ رحلتك'", "headline: ''"],
    ["lessonTitle: 'مهمتك التعليمية تظهر هنا'", "lessonTitle: ''"],
    ["ctaLabel: 'ابدأ'", "ctaLabel: ''"],
  ],
  'src/views/student/StudentAchievementsView.vue': [
    ['              <span>الهدف التالي: 30 يوماً للشارة الذهبية</span>', '              <span>{{ t(\'student.achievements.sections.streakGoal\') }}</span>'],
  ],
  'src/views/student/StudentPlannerView.vue': [
    ['            توليد الخطة', '            {{ t(\'student.planner.generateCta\') }}'],
  ],
}

for (const [rel, pairs] of Object.entries(patches)) {
  const path = join(root, rel)
  let c = readFileSync(path, 'utf8')
  if (!c.includes('useI18n') && rel !== 'src/components/student/TeacherContactCard.vue' && rel !== 'src/components/student/StudentTeacherProfileDialog.vue') {
    c = ensureI18n(c)
  }
  for (const [from, to] of pairs) {
    if (!c.includes(from)) {
      console.warn(`[skip] ${rel}: ${from.slice(0, 50)}`)
      continue
    }
    c = c.split(from).join(to)
  }
  writeFileSync(path, c, 'utf8')
  console.log('Patched', rel)
}

console.log('Done batch3.')
