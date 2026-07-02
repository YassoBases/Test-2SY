/**
 * StudentLessonView i18n patches — exact string replacements only.
 */
import { readFileSync, writeFileSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = join(dirname(fileURLToPath(import.meta.url)), '..')
const rel = 'src/views/student/StudentLessonView.vue'

/** @type {Array<[string, string]>} */
const pairs = [
  ['          العودة إلى الدروس', '          {{ t(\'student.lesson.nav.backToLessons\') }}'],
  ['            الدرس السابق', '            {{ t(\'student.lesson.nav.previous\') }}'],
  ['            الدرس التالي', '            {{ t(\'student.lesson.nav.next\') }}'],
  ['                اسأل المعلّm', '                {{ t(\'student.lesson.tabs.askTeacher\') }}'],
  ['                اختبر نفسك', '                {{ t(\'student.lesson.tabs.quiz\') }}'],
  ['                <span class="section-eyebrow mb-1">تقدمك</span>', '                <span class="section-eyebrow mb-1">{{ t(\'student.lesson.progress.eyebrow\') }}</span>'],
  ['                <h3 class="text-h6 font-weight-bold mb-0">جلسة التعلم</h3>', '                <h3 class="text-h6 font-weight-bold mb-0">{{ t(\'student.lesson.progress.sessionTitle\') }}</h3>'],
  ['                <span>الخطوة التالية</span>', '                <span>{{ t(\'student.lesson.progress.nextStep\') }}</span>'],
  ['                <span>أسئلة</span>', '                <span>{{ t(\'student.lesson.progress.stats.questions\') }}</span>'],
  ['                <span>اختبار</span>', '                <span>{{ t(\'student.lesson.progress.stats.quiz\') }}</span>'],
  ['                <span>أخطاء</span>', '                <span>{{ t(\'student.lesson.progress.stats.mistakes\') }}</span>'],
  ['              التغذية الراجعة', '              {{ t(\'student.lesson.feedback.title\') }}'],
  ['              أجب على الأسئلة لتحصل على تغذية راجعة فورية', '              {{ t(\'student.lesson.feedback.empty\') }}'],
  ['                  <h3 class="text-h6 font-weight-bold mb-0">خطة تعلم صغيرة</h3>', '                  <h3 class="text-h6 font-weight-bold mb-0">{{ t(\'student.lesson.plan.title\') }}</h3>'],
  ["                  {{ mistakeReview.length ? 'مراجعة' : 'تثبيت' }}", "                  {{ mistakeReview.length ? t('student.lesson.plan.chip.review') : t('student.lesson.plan.chip.consolidate') }}"],
  ['                اختبار سريع', '                {{ t(\'student.lesson.quiz.title\') }}'],
  ['text="توليد أسئلة جديدة من الدرس"', ':text="t(\'student.lesson.quiz.regenerateTooltip\')"'],
  ['aria-label="توليد أسئلة جديدة"', ':aria-label="t(\'student.lesson.quiz.regenerateAria\')"'],
  ['                <h3 class="text-h6 font-weight-bold mb-0">راجع أخطاءك</h3>', '                <h3 class="text-h6 font-weight-bold mb-0">{{ t(\'student.lesson.quiz.reviewMistakes\') }}</h3>'],
  ['                  <span class="text-error">جوابك:</span>', '                  <span class="text-error">{{ t(\'student.lesson.quiz.yourAnswer\') }}</span>'],
  ['                  <span class="text-success">الصحيح:</span>', '                  <span class="text-success">{{ t(\'student.lesson.quiz.correctAnswer\') }}</span>'],
  ['                  <span class="section-eyebrow mb-1">تدريب حسب الخطأ</span>', '                  <span class="section-eyebrow mb-1">{{ t(\'student.lesson.quiz.remedial.eyebrow\') }}</span>'],
  ['                  <h3 class="text-h6 font-weight-bold mb-0">أسئلة علاجية</h3>', '                  <h3 class="text-h6 font-weight-bold mb-0">{{ t(\'student.lesson.quiz.remedial.title\') }}</h3>'],
  ['              ممتاز، ما عندك أخطاء بهذا الاختبار.', '              {{ t(\'student.lesson.quiz.noMistakes\') }}'],
  ["                  ? 'جاري توليد الاختبار من محتوى الدرس…'", "                  ? t('student.lesson.quiz.generating')"],
  ["                    ? 'تعذر توليد الاختبار — جرّب لاحقاً أو اسأل المعلم'", "                    ? t('student.lesson.quiz.generateFailed')"],
  ["                      ? 'الاختبار سيظهر تلقائياً بعد اكتمال المعالجة'", "                      ? t('student.lesson.quiz.pendingProcessing')"],
  ["                      : 'ركّز على المحادثة مع المعلّm'", "                      : t('student.lesson.quiz.noAiSource')"],
  ['              توليد اختبار من الدرس', '              {{ t(\'student.lesson.quiz.generateCta\') }}'],
  ['          <strong>جاري تحضير الدرس</strong>', '          <strong>{{ t(\'student.lesson.ai.preparingTitle\') }}</strong>'],
  ['          <div class="text-caption">المعلّm يجهّز محتوى الدرس والاختبار — يستغرق عادةً دقيقة.</div>', '          <div class="text-caption">{{ t(\'student.lesson.ai.preparingHint\') }}</div>'],
  ["      {{ lesson.error_message || 'تعذر إكمال المعالجة الذكية لهذا الدرس.' }}", "      {{ lesson.error_message || t('student.lesson.ai.processingFailed') }}"],
  ['      <span class="lesson-fallback-card__label">وصول احتياطي للمحتوى</span>', '      <span class="lesson-fallback-card__label">{{ t(\'student.lesson.fallback.label\') }}</span>'],
  ['          الفيديو', '          {{ t(\'student.lesson.fallback.tabs.video\') }}'],
  ['          الملف', '          {{ t(\'student.lesson.fallback.tabs.pdf\') }}'],
  ['                الفيديو متاح في مسار التعلّm أعلاه — مسار واحد متصل مع بقية الدرس.', '                {{ t(\'student.lesson.fallback.videoHint\') }}'],
  ['                الانتقال إلى الفيديو في مسار التعلّm', '                {{ t(\'student.lesson.fallback.goToVideo\') }}'],
  ['                ملف الدرس جزء من مسار التعلّm — اقرأه ضمن التسلسل الكامل للدرس.', '                {{ t(\'student.lesson.fallback.pdfHint\') }}'],
  ['                الانتقال إلى الملف في مسار التعلّm', '                {{ t(\'student.lesson.fallback.goToPdf\') }}'],
  ['        الانتقال إلى الدرس التالي', '        {{ t(\'student.lesson.nav.goToNext\') }}'],
  ['            <h3 class="text-h6 font-weight-bold mb-0">مسح المحادثة</h3>', '            <h3 class="text-h6 font-weight-bold mb-0">{{ t(\'student.lesson.chat.clear.title\') }}</h3>'],
  ['            <p class="text-caption text-medium-emphasis mb-0">سيتم مسح رسائلك مع هذا الدرس فقط.</p>', '            <p class="text-caption text-medium-emphasis mb-0">{{ t(\'student.lesson.chat.clear.subtitle\') }}</p>'],
  ['          هل تريد بدء محادثة جديدة مع المعلّm؟', '          {{ t(\'student.lesson.chat.clear.confirm\') }}'],
  ['          <v-btn variant="text" :disabled="isClearingChat" @click="clearDialog = false">إلغاء</v-btn>', '          <v-btn variant="text" :disabled="isClearingChat" @click="clearDialog = false">{{ t(\'student.lesson.chat.clear.cancel\') }}</v-btn>'],
  ['            مسح', '            {{ t(\'student.lesson.chat.clear.confirmCta\') }}'],
  ['        <h3 class="text-h6 font-weight-bold mb-2">لا يمكن إكمال هذا الدرس بعد</h3>', '        <h3 class="text-h6 font-weight-bold mb-2">{{ t(\'student.lesson.verify.blockedTitle\') }}</h3>'],
  ['        <p class="text-subtitle-2 font-weight-bold mb-2">المطلوب:</p>', '        <p class="text-subtitle-2 font-weight-bold mb-2">{{ t(\'student.lesson.verify.requirements\') }}</p>'],
  ['        <v-btn block rounded="lg" @click="verifyDialog = false">حسناً</v-btn>', '        <v-btn block rounded="lg" @click="verifyDialog = false">{{ t(\'student.common.ok\') }}</v-btn>'],
  ["  if (lesson.value.ai_processing) return 'المعلّm يجهّز الدرس — جرّب بعد لحظات'", "  if (lesson.value.ai_processing) return t('student.lesson.ai.chatDisabledHint')"],
  ["getErrorMessage(e, 'تعذر تجهيز المساعدة')", "getErrorMessage(e, t('student.lesson.ai.assistantFailed'))"],
  ["getErrorMessage(e, 'انتظر اكتمال تجهيز محتوى الدرس')", "getErrorMessage(e, t('student.lesson.ai.waitForContent'))"],
  ["getErrorMessage(e, 'تعذر التحقق من إكمال الدرس')", "getErrorMessage(e, t('student.lesson.errors.verify'))"],
  ["verifySuccess.value ? 'تم إكمال الدرس بنجاح!' : 'أكمل المتطلبات الناقصة أولاً.'", "verifySuccess.value ? t('student.lesson.verify.success') : t('student.lesson.verify.incomplete')"],
  ["return 'بدون إجابة'", "return t('student.lesson.quiz.noAnswer')"],
  ["import { computed, onMounted", "import { useI18n } from 'vue-i18n'\nimport { computed, onMounted"],
  ['const route = useRoute()', 'const route = useRoute()\nconst { t } = useI18n()'],
]

let c = readFileSync(join(root, rel), 'utf8')
for (const [from, to] of pairs) {
  if (!c.includes(from)) {
    console.warn('[skip]', from.slice(0, 55))
    continue
  }
  c = c.split(from).join(to)
}
writeFileSync(join(root, rel), c, 'utf8')
console.log('Patched StudentLessonView.vue')
