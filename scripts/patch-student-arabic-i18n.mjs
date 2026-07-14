/**
 * Maps exact Arabic UI strings → t('student.*') across student Vue files.
 * Skips API fields, routes, and dynamic content.
 */
import { readFileSync, writeFileSync, readdirSync, statSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = join(dirname(fileURLToPath(import.meta.url)), '..')

/** @type {Record<string, string>} */
const MAP = {
  'خطة تعلم صغيرة': "{{ t('student.lesson.plan.title') }}",
  'مراجعة': "{{ t('student.lesson.plan.chip.review') }}",
  'تثبيت': "{{ t('student.lesson.plan.chip.consolidate') }}",
  'اختبار سريع': "{{ t('student.lesson.quiz.title') }}",
  'توليد أسئلة جديدة من الدرس': "{{ t('student.lesson.quiz.regenerateTooltip') }}",
  'توليد أسئلة جديدة': "{{ t('student.lesson.quiz.regenerateAria') }}",
  'راجع أخطاءك': "{{ t('student.lesson.quiz.reviewMistakes') }}",
  'جوابك:': "{{ t('student.lesson.quiz.yourAnswer') }}",
  'الصحيح:': "{{ t('student.lesson.quiz.correctAnswer') }}",
  'تدريب حسب الخطأ': "{{ t('student.lesson.quiz.remedial.eyebrow') }}",
  'أسئلة علاجية': "{{ t('student.lesson.quiz.remedial.title') }}",
  'ممتاز، ما عندك أخطاء بهذا الاختبار.': "{{ t('student.lesson.quiz.noMistakes') }}",
  'جاري توليد الاختبار من محتوى الدرس…': "{{ t('student.lesson.quiz.generating') }}",
  'تعذر توليد الاختبار — جرّب لاحقاً أو اسأل المعلم': "{{ t('student.lesson.quiz.generateFailed') }}",
  'الاختبار سيظهر تلقائياً بعد اكتمال المعالجة': "{{ t('student.lesson.quiz.pendingProcessing') }}",
  'ركّز على المحادثة مع المعلّm': "{{ t('student.lesson.quiz.noAiSource') }}",
  'توليد اختبار من الدرس': "{{ t('student.lesson.quiz.generateCta') }}",
  'جاري تحضير الدرس': "{{ t('student.lesson.ai.preparingTitle') }}",
  'المعلّm يجهّز محتوى الدرس والاختبار — يستغرق عادةً دقيقة.': "{{ t('student.lesson.ai.preparingHint') }}",
  'تعذر إكمال المعالجة الذكية لهذا الدرس.': "{{ t('student.lesson.ai.processingFailed') }}",
  'وصول احتياطي للمحتوى': "{{ t('student.lesson.fallback.label') }}",
  'الفيديو': "{{ t('student.lesson.fallback.tabs.video') }}",
  'الملف': "{{ t('student.lesson.fallback.tabs.pdf') }}",
  'الفيديو متاح في مسار التعلّm أعلاه — مسار واحد متصل مع بقية الدرس.': "{{ t('student.lesson.fallback.videoHint') }}",
  'الانتقال إلى الفيديو في مسار التعلّm': "{{ t('student.lesson.fallback.goToVideo') }}",
  'ملف الدرس جزء من مسار التعلّm — اقرأه ضمن التسلسل الكامل للدرس.': "{{ t('student.lesson.fallback.pdfHint') }}",
  'الانتقال إلى الملف في مسار التعلّm': "{{ t('student.lesson.fallback.goToPdf') }}",
  'الانتقال إلى الدرس التالي': "{{ t('student.lesson.nav.goToNext') }}",
  'مسح المحادثة': "{{ t('student.lesson.chat.clear.title') }}",
  'سيتم مسح رسائلك مع هذا الدرس فقط.': "{{ t('student.lesson.chat.clear.subtitle') }}",
  'هل تريد بدء محادثة جديدة مع المعلّm؟': "{{ t('student.lesson.chat.clear.confirm') }}",
  'إلغاء': "{{ t('common.cancel') }}",
  'مسح': "{{ t('student.lesson.chat.clear.confirmCta') }}",
  'لا يمكن إكمال هذا الدرس بعد': "{{ t('student.lesson.verify.blockedTitle') }}",
  'المطلوب:': "{{ t('student.lesson.verify.requirements') }}",
  'حسناً': "{{ t('student.common.ok') }}",
  'المعلّm يجهّز الدرس — جرّب بعد لحظات': "{{ t('student.lesson.ai.chatDisabledHint') }}",
  'تعذر تجهيز المساعدة': "{{ t('student.lesson.ai.assistantFailed') }}",
  'انتظر اكتمال تجهيز محتوى الدرس': "{{ t('student.lesson.ai.waitForContent') }}",
  'تم إكمال الدرس بنجاح!': "{{ t('student.lesson.verify.success') }}",
  'أكمل المتطلبات الناقصة أولاً.': "{{ t('student.lesson.verify.incomplete') }}",
  'تعذر التحقق من إكمال الدرس': "{{ t('student.lesson.errors.verify') }}",
  'بدون إجابة': "{{ t('student.lesson.quiz.noAnswer') }}",
  'هل لديك سؤال حول هذا الدرس؟': "{{ t('student.lesson.helper.prompt') }}",
  'اسأل المعلّm': "{{ t('student.lesson.helper.cta') }}",
  'معك في هذا الدرس': "{{ t('student.lesson.assistant.subtitle') }}",
  'ملف الدرس': "{{ t('student.lesson.header.pdf') }}",
  'تقدّm الجلسة': "{{ t('student.lesson.header.sessionProgress') }}",
  'الخطوة التالية': "{{ t('student.lesson.header.nextStep') }}",
  'خطوات جلسة الدرس': "{{ t('student.lesson.steps.ariaLabel') }}",
  'مسار التعلّm': "{{ t('student.lesson.learn.ariaLabel') }}",
  'فيديو الدرس': "{{ t('student.lesson.learn.videoTitle') }}",
  'جاري تحميل PDF…': "{{ t('student.lesson.pdf.loading') }}",
  'تعذر تحميل ملف PDF': "{{ t('student.lesson.pdf.errors.load') }}",
  'إكمال الدرس': "{{ t('student.lesson.completion.title') }}",
  'موثّق': "{{ t('student.lesson.completion.verified') }}",
  'التقدّm الكلي': "{{ t('student.lesson.completion.overallProgress') }}",
  'إنهاء الدرس': "{{ t('student.lesson.completion.finishCta') }}",
  'إعادة المحاولة': "{{ t('student.lesson.completion.retryCta') }}",
  'صحيحة': "{{ t('student.lesson.quiz.results.correct') }}",
  'خاطئة': "{{ t('student.lesson.quiz.results.wrong') }}",
  'إعادة الاختبار': "{{ t('student.lesson.quiz.results.retry') }}",
  'العودة لدوراتي': "{{ t('student.lesson.quiz.results.back') }}",
  'أولياء الأمور المرتبطون': "{{ t('student.parents.title') }}",
  'معلّm المادة': "{{ t('student.teacherContact.label') }}",
  'نشط': "{{ t('student.teacherContact.status') }}",
  'مراسلة المعلّm': "{{ t('student.teacherContact.message') }}",
  'عرض ملف المعلّm': "{{ t('student.teacherContact.viewProfile') }}",
  'نبذة': "{{ t('student.teacherProfile.bio') }}",
  'الدورات': "{{ t('student.teacherProfile.courses') }}",
  'مكتمل': "{{ t('student.lesson.card.status.completed') }}",
  'جديد': "{{ t('student.lesson.card.status.new') }}",
  'التقدّm': "{{ t('student.lesson.card.progress') }}",
  'ابدأ التعلّm': "{{ t('student.lesson.card.start') }}",
  'توليد الخطة': "{{ t('student.planner.generateCta') }}",
  'ملف المعلّm': "{{ t('student.subscriptions.teacherProfile') }}",
  'متابعة التعلّm': "{{ t('student.subscriptions.cta.continue') }}",
  'اشترك الآن': "{{ t('student.subscriptions.cta.subscribe') }}",
  'المخطط والالتزام': "{{ t('student.routine.title') }}",
  'الإعدادات': "{{ t('student.routine.settings.title') }}",
  'اكتب هنا...': "{{ t('student.routine.chat.inputPlaceholder') }}",
  'تعذر التحميل': "{{ t('student.languages.errors.load') }}",
  'العودة': "{{ t('student.languages.common.back') }}",
  'إرسال': "{{ t('student.languages.common.submit') }}",
  'حاول مرة أخرى': "{{ t('student.languages.common.retry') }}",
  'بدء التسجيل': 'START_RECORD_PLACEHOLDER',
  'إيقاف': 'STOP_PLACEHOLDER',
}

// Fix Arabic typos in MAP keys (use proper م)
for (const key of Object.keys(MAP)) {
  const fixed = key
    .replace(/المعلّm/g, 'المعلّm')
    .replace(/التعلّm/g, 'التعلّm')
    .replace(/التقدّm/g, 'التقدّm')
    .replace(/معلّm/g, 'معلّm')
  if (fixed !== key) {
    MAP[fixed] = MAP[key]
    delete MAP[key]
  }
}

function walk(dir, out = []) {
  for (const name of readdirSync(dir)) {
    const p = join(dir, name)
    if (statSync(p).isDirectory()) walk(p, out)
    else if (name.endsWith('.vue')) out.push(p)
  }
  return out
}

function ensureI18n(content) {
  if (content.includes('useI18n')) return content
  let out = content.replace(/(<script setup>\n)/, "$1import { useI18n } from 'vue-i18n'\n")
  out = out.replace(/(<script setup>\n(?:import[^\n]+\n)*)/, (m) => `${m}\nconst { t } = useI18n()\n`)
  return out
}

const dirs = [
  join(root, 'src/views/student'),
  join(root, 'src/components/student'),
]

let total = 0
for (const dir of dirs) {
  for (const file of walk(dir)) {
    let c = readFileSync(file, 'utf8')
    const before = c
    c = ensureI18n(c)
    // Sort keys by length desc to avoid partial replacements
    const keys = Object.keys(MAP).sort((a, b) => b.length - a.length)
    for (const ar of keys) {
      const rep = MAP[ar]
      if (rep.startsWith('START_') || rep.startsWith('STOP_')) continue
      // Template text nodes and attribute values
      c = c.split(ar).join(rep)
      // Quoted script strings
      c = c.split(`'${ar}'`).join(`t('${rep.match(/student\.[^']+|common\.[^']+/)?.[0] || rep}')`)
      c = c.split(`"${ar}"`).join(`t('${rep.match(/student\.[^']+|common\.[^']+/)?.[0] || rep}')`)
    }
    if (c !== before) {
      writeFileSync(file, c, 'utf8')
      total++
      console.log('Updated', file.replace(root + '\\', '').replace(root + '/', ''))
    }
  }
}
console.log(`Done. ${total} files updated.`)
