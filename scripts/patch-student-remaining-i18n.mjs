/**
 * Batch-patches remaining student Vue files with i18n t() calls.
 * Run after: node scripts/migrate-student-i18n.mjs
 */
import { readFileSync, writeFileSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = join(dirname(fileURLToPath(import.meta.url)), '..')

function ensureI18n(content) {
  let out = content
  if (!out.includes('useI18n')) {
    out = out.replace(
      /(<script setup>\n)/,
      "$1import { useI18n } from 'vue-i18n'\n",
    )
    out = out.replace(
      /(<script setup>\n(?:import[^\n]+\n)*)/,
      (m) => `${m}\nconst { t } = useI18n()\n`,
    )
  }
  return out
}

/** @type {Record<string, Array<[string|RegExp, string]>>} */
const patches = {
  'src/views/student/StudentSubscriptionsView.vue': [
    ['eyebrow="اشترك وافتح موادك"', ':eyebrow="t(\'student.subscriptions.header.eyebrow\')"'],
    ['title="الاشتراكات"', ':title="t(\'student.subscriptions.header.title\')"'],
    ['مواد مفعّلة', '{{ t(\'student.subscriptions.kpi.unlocked\') }}'],
    ['مواد متاحة لصفك', '{{ t(\'student.subscriptions.kpi.available\') }}'],
    [':aria-label="`ملف المعلّم ${course.teacher_name}`"', ':aria-label="t(\'student.subscriptions.teacherProfileAria\', { name: course.teacher_name })"'],
    ['>مفعّل</v-chip>', '>{{ t(\'student.subscriptions.status.unlocked\') }}</v-chip>'],
    ['>مقفل</v-chip>', '>{{ t(\'student.subscriptions.status.locked\') }}</v-chip>'],
    ['>ملف المعلّم</v-btn>', '>{{ t(\'student.subscriptions.teacherProfile\') }}</v-btn>'],
    ['>فيديو {{ course.video_count }}', '>{{ t(\'student.subscriptions.chips.video\', { n: course.video_count }) }}'],
    ['>PDF {{ course.pdf_count }}', '>{{ t(\'student.subscriptions.chips.pdf\', { n: course.pdf_count }) }}'],
    ['>واجب {{ course.homework_count }}', '>{{ t(\'student.subscriptions.chips.homework\', { n: course.homework_count }) }}'],
    ['>ذكي {{ course.ai_lesson_count }}', '>{{ t(\'student.subscriptions.chips.ai\', { n: course.ai_lesson_count }) }}'],
    ['{{ course.lesson_count }} درس', '{{ t(\'student.subscriptions.chips.lessons\', { n: course.lesson_count }) }}'],
    ['>متابعة التعلّم</v-btn>', '>{{ t(\'student.subscriptions.cta.continue\') }}</v-btn>'],
    ['>اشترك الآن</v-btn>', '>{{ t(\'student.subscriptions.cta.subscribe\') }}</v-btn>'],
    ["description=\"لا توجد مواد منشورة لصفك حالياً — سيظهر المحتوى عند رفع المعلمين لدروسهم.\"", ':description="t(\'student.subscriptions.empty\')"'],
    ["session.value?.name?.split(' ')[0] || 'طالب'", "session.value?.name?.split(' ')[0] || t('student.common.defaultStudentName')"],
    ['? `الصف ${catalog.value.grade} — جميع المواد المتاحة من معلميك` : \'حدّد صفك من التسجيل\'',
      "? t('student.subscriptions.header.subtitleWithGrade', { grade: catalog.value.grade }) : t('student.subscriptions.header.subtitleNoGrade')"],
    ["getErrorMessage(e, 'تعذر تحميل الاشتراكات')", "getErrorMessage(e, t('student.subscriptions.errors.load'))"],
    ['successMsg.value = `تم تفعيل ${course.subject_name} — يمكنك فتح الدروس الآن`',
      "successMsg.value = t('student.subscriptions.success.activated', { subject: course.subject_name })"],
    ["getErrorMessage(e, 'تعذر إتمام الاشتراك')", "getErrorMessage(e, t('student.subscriptions.errors.subscribe'))"],
    ["getErrorMessage(e, 'تعذر تحميل ملف المعلّم')", "getErrorMessage(e, t('student.subscriptions.errors.loadTeacherProfile'))"],
  ],
  'src/views/student/StudentAchievementsView.vue': [
    ['eyebrow="التقدّم والإنجازات"', ':eyebrow="t(\'student.achievements.header.eyebrow\')"'],
    ['title="🏆 إنجازاتي"', ':title="t(\'student.achievements.header.title\')"'],
    ['subtitle="تتبّع مستواك ونقاط XP وسلسلة التعلّم والشارات"', ':subtitle="t(\'student.achievements.header.subtitle\')"'],
    ['>المستوى {{ profile.level }}</div>', '>{{ t(\'student.achievements.level\', { n: profile.level }) }}</div>'],
    ['{{ profile.total_xp?.toLocaleString(\'ar-SY\') }} XP إجمالي', "{{ t('student.achievements.totalXp', { xp: profile.total_xp?.toLocaleString() }) }}"],
    ['>تقدّم المستوى</span>', '>{{ t(\'student.achievements.levelProgress\') }}</span>'],
    ['{{ profile.xp_to_next_level?.toLocaleString(\'ar-SY\') }} XP للمستوى {{ profile.level + 1 }}',
      "{{ t('student.achievements.xpToNext', { xp: profile.xp_to_next_level?.toLocaleString(), n: profile.level + 1 }) }}"],
    ['>أعلى مستوى!</span>', '>{{ t(\'student.achievements.maxLevel\') }}</span>'],
    ['أطول سلسلة: {{ profile.longest_streak }} يوم', "{{ t('student.achievements.longestStreak', { n: profile.longest_streak }) }}"],
    ['{{ profile.achievement_count }} / {{ profile.badges?.length || 0 }} شارة',
      "{{ t('student.achievements.badgeCount', { earned: profile.achievement_count, total: profile.badges?.length || 0 }) }}"],
    ['>آخر نشاط XP</h3>', '>{{ t(\'student.achievements.sections.recentXp\') }}</h3>'],
    ['>أحدث الإنجازات ومصادر النقاط</p>', '>{{ t(\'student.achievements.sections.recentXpSubtitle\') }}</p>'],
    ['>سلسلة الدراسة</h3>', '>{{ t(\'student.achievements.sections.streak\') }}</h3>'],
    ['>التزامك اليومي يبني سلسلة أقوى</p>', '>{{ t(\'student.achievements.sections.streakSubtitle\') }}</p>'],
    ['>يوم متتالي</div>', '>{{ t(\'student.achievements.sections.streakDays\') }}</div>'],
    ['>الهدف التالي: 30 يوماً للشارة الذهبية', '>{{ t(\'student.achievements.sections.streakGoal\') }}'],
    ['>الشارات</h3>', '>{{ t(\'student.achievements.sections.badges\') }}</h3>'],
    ['>افتح الشارات بالتعلّم والالتزام — المقفلة بالرمادي</p>', '>{{ t(\'student.achievements.sections.badgesSubtitle\') }}</p>'],
    ['>قواعد كسب XP</h3>', '>{{ t(\'student.achievements.sections.xpRules\') }}</h3>'],
    ['>القيم الحالية من نظام التلعيب — تُحدَّث تلقائياً من الخادم</p>', '>{{ t(\'student.achievements.sections.xpRulesSubtitle\') }}</p>'],
    ['>مكافآت مستقبلية</h3>', '>{{ t(\'student.achievements.sections.futureRewards\') }}</h3>'],
    ['>قريباً — للمعلومات فقط في هذه المرحلة</p>', '>{{ t(\'student.achievements.sections.futureRewardsSubtitle\') }}</p>'],
  ],
  'src/views/student/StudentPlannerView.vue': [
    ['eyebrow="مخطط دراسي ذكي"', ':eyebrow="t(\'student.planner.header.eyebrow\')"'],
    ['title="المخطط الذكي"', ':title="t(\'student.planner.header.title\')"'],
    ['subtitle="خطة أسبوعية مبنية على أدائك — مواد ضعيفة، امتحانات قادمة، وسلسلة التعلم"', ':subtitle="t(\'student.planner.header.subtitle\')"'],
    ['>توليد الخطة</v-btn>', '>{{ t(\'student.planner.generateCta\') }}</v-btn>'],
    ['>الخطة الأسبوعية</h3>', '>{{ t(\'student.planner.sections.weeklyPlan\') }}</h3>'],
    ['>مهامك موزّعة على أيام الأسبوع حسب الأولوية</p>', '>{{ t(\'student.planner.sections.weeklyPlanSubtitle\') }}</p>'],
    ['>تحليل المواد</h3>', '>{{ t(\'student.planner.sections.subjectAnalysis\') }}</h3>'],
    ['>قوي · متوسط · ضعيف — بناءً على الدرجات والإكمال</p>', '>{{ t(\'student.planner.sections.subjectAnalysisSubtitle\') }}</p>'],
    ['>توصيات ذكية</h3>', '>{{ t(\'student.planner.sections.recommendations\') }}</h3>'],
    ['>🔥 عالية · ⚠️ متوسطة · ✅ منخفضة</p>', '>{{ t(\'student.planner.sections.recommendationsSubtitle\') }}</p>'],
    ["ref('يُولّد المخطط تلقائياً من درجاتك وتقدّمك — أو تحدّث مع المساعد لتخصيص الجدول')",
      "ref(t('student.planner.banner.default'))"],
    ["bannerMessage.value = 'تم إعادة ترتيب الجدول بناءً على أدائك الحالي'",
      "bannerMessage.value = t('student.planner.banner.reordered')"],
  ],
  'src/components/student/StudentCourseCard.vue': [
    ['>الصف {{ course.grade }}</v-chip>', '>{{ t(\'student.course.card.grade\', { grade: course.grade }) }}</v-chip>'],
    ['{{ course.lesson_count }} درس', "{{ t('student.course.card.lessonCount', { n: course.lesson_count }) }}"],
    ['>التقدّم</span>', '>{{ t(\'student.course.card.progress\') }}</span>'],
    ['ينتهي خلال {{ course.days_until_expiry }} يوم', "{{ t('student.course.card.expiringSoon', { n: course.days_until_expiry }) }}"],
    ["course.lock_reason || 'اشترك لفتح المادة'", "course.lock_reason || t('student.course.card.lockReason')"],
    ['>متابعة التعلّم</v-btn>', '>{{ t(\'student.course.card.continue\') }}</v-btn>'],
    ["course.subscription_status === 'expired' ? 'تجديد الاشتراك' : 'اشترك لفتح المادة'",
      "course.subscription_status === 'expired' ? t('student.course.card.renew') : t('student.course.card.subscribe')"],
  ],
  'src/components/student/StudentLessonCard.vue': [
    ['>مكتمل</v-chip>', '>{{ t(\'student.lesson.card.status.completed\') }}</v-chip>'],
    ['>جديد</v-chip>', '>{{ t(\'student.lesson.card.status.new\') }}</v-chip>'],
    ['>التقدّم</span>', '>{{ t(\'student.lesson.card.progress\') }}</span>'],
    ['{{ lesson.pages }} ص', "{{ t('student.lesson.card.pages', { n: lesson.pages }) }}"],
    ['>ابدأ التعلّم</v-btn>', '>{{ t(\'student.lesson.card.start\') }}</v-btn>'],
    ['>ملف الدرس</v-btn>', '>{{ t(\'student.lesson.card.pdf\') }}</v-btn>'],
  ],
}

for (const [rel, replacements] of Object.entries(patches)) {
  const path = join(root, rel)
  let content = readFileSync(path, 'utf8')
  content = ensureI18n(content)
  for (const [from, to] of replacements) {
    if (typeof from === 'string') {
      if (!content.includes(from)) {
        console.warn(`[skip] ${rel}: not found: ${from.slice(0, 60)}...`)
        continue
      }
      content = content.split(from).join(to)
    }
  }
  writeFileSync(path, content, 'utf8')
  console.log(`Patched ${rel}`)
}

console.log('Done.')
