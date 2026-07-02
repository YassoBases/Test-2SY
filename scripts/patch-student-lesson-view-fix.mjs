/** Fix remaining StudentLessonView Arabic with regex (Unicode-safe). */
import { readFileSync, writeFileSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const path = join(dirname(fileURLToPath(import.meta.url)), '..', 'src/views/student/StudentLessonView.vue')
let c = readFileSync(path, 'utf8')

const reps = [
  [/(?<=mdi-message-text"><\/v-icon>\n)\s*اسأل المعلّm/m, "                {{ t('student.lesson.tabs.askTeacher') }}"],
  [/{{ t\('student\.lesson\.fallback\.tabs\.video'\) }} متاح في مسار التعلّm أعلاه — مسار واحد متصل مع بقية الدرس\./g, "{{ t('student.lesson.fallback.videoHint') }}"],
  [/>\s*الانتقال إلى الفيديو في مسار التعلّm\s*</g, ">{{ t('student.lesson.fallback.goToVideo') }}<"],
  [/>\s*ملف الدرس جزء من مسار التعلّm — اقرأه ضمن التسلسل الكامل للدرس\.\s*</g, ">{{ t('student.lesson.fallback.pdfHint') }}<"],
  [/>\s*الانتقال إلى الملف في مسار التعلّm\s*</g, ">{{ t('student.lesson.fallback.goToPdf') }}<"],
  [/>\s*هل تريد بدء محادثة جديدة مع المعلّm؟\s*</g, ">{{ t('student.lesson.chat.clear.confirm') }}<"],
  [/:\s*'ركّز على المحادثة مع المعلّm'/g, ": t('student.lesson.quiz.noAiSource')"],
  [/<div class="text-caption">المعلّm يجهّز محتوى الدرس والاختبار — يستغرق عادةً دقيقة\.<\/div>/g, '<div class="text-caption">{{ t(\'student.lesson.ai.preparingHint\') }}</div>'],
  [/if \(lesson\.value\.ai_processing\) return 'المعلّm يجهّز الدرس — جرّب بعد لحظات'/g, "if (lesson.value.ai_processing) return t('student.lesson.ai.chatDisabledHint')"],
  [/if \(lesson\.value\.ai_error\) return lesson\.value\.error_message \|\| 'تعذر تجهيز المساعدة'/g, "if (lesson.value.ai_error) return lesson.value.error_message || t('student.lesson.ai.assistantFailed')"],
  [/if \(hasAiSource\.value\) return 'انتظر اكتمال تجهيز محتوى الدرس'/g, "if (hasAiSource.value) return t('student.lesson.ai.waitForContent')"],
  [/totalLessons\.value \? `الدرس \$\{currentLessonNumber\.value\} من \$\{totalLessons\.value\}` : ''/g, "totalLessons.value ? t('student.lesson.flow.position', { n: currentLessonNumber.value, total: totalLessons.value }) : ''"],
  [/result\.message \|\| 'تم إكمال الدرس بنجاح!'/g, "result.message || t('student.lesson.verify.success')"],
  [/result\.message \|\| 'أكمل المتطلبات الناقصة أولاً\.'/g, "result.message || t('student.lesson.verify.incomplete')"],
  [/getErrorMessage\(err, 'تعذر التحقق من إكمال الدرس'\)/g, "getErrorMessage(err, t('student.lesson.errors.verify'))"],
  [/q\.options\[quizAnswers\[q\.id\]\] \?\? 'بدون إجابة'/g, "q.options[quizAnswers[q.id]] ?? t('student.lesson.quiz.noAnswer')"],
  [/text: 'ولّدي اختباراً من الدرس حتى تقيسي فهمك\.'/g, "text: t('student.lesson.flow.generateQuiz.text')"],
  [/cta: 'توليد اختبار'/g, "cta: t('student.lesson.flow.generateQuiz.cta')"],
  [/mistakes === 1\s*\?\s*'باقي خطأ واحد\. راجعيه ثم جرّبي اختباراً جديداً لتوصلي إلى 100%\.'/g, "mistakes === 1 ? t('student.lesson.flow.mistakes.one')"],
  [/:\s*`باقي \$\{mistakes\} أخطاء\. راجعيها ثم جرّبي اختباراً جديداً لتوصلي إلى 100%\.`/g, ": t('student.lesson.flow.mistakes.many', { n: mistakes })"],
  [/cta: 'اختبار جديد'/g, "cta: t('student.lesson.flow.mistakes.cta')"],
  [/text: 'اسألي المعلّm سؤالاً واحداً عن الدرس حتى تكتمل جلسة التعلم\.'/g, "text: t('student.lesson.flow.askTeacher.text')"],
  [/cta: 'اسألني'/g, "cta: t('student.lesson.flow.askTeacher.cta')"],
  [/text: 'مكتمل\. خلصتِ الاختبار بدون أخطاء وتفاعلتِ مع المعلّm\.'/g, "text: t('student.lesson.flow.complete.text')"],
  [/cta: 'تحدّي جديد'/g, "cta: t('student.lesson.flow.complete.cta')"],
  [/mistakeReview\.value\.length \? 'خطة مراجعة مركزة' : 'خطة تثبيت سريعة'/g, "mistakeReview.value.length ? t('student.lesson.flow.plan.reviewLabel') : t('student.lesson.flow.plan.consolidateLabel')"],
  [/title: 'راجعي نقطة الخطأ'/g, "title: t('student.lesson.flow.plan.reviewMistake.title')"],
  [/\? `ركزي على الجواب الصحيح: \$\{firstMistake\.correct\}\.`/g, "? t('student.lesson.flow.plan.reviewMistake.withAnswer', { answer: firstMistake.correct })"],
  [/:\s*'راجعي الأسئلة التي ظهرت فيها أخطاء\.'/g, ": t('student.lesson.flow.plan.reviewMistake.generic')"],
  [/title: 'اسألي المعلّm عنها'/g, "title: t('student.lesson.flow.plan.askTeacher.title')"],
  [/description: 'خلي المعلّm يشرح سبب الخطأ بجملة مبسطة من الدرس\.'/g, "description: t('student.lesson.flow.plan.askTeacher.description')"],
  [/cta: 'اشرح الخطأ'/g, "cta: t('student.lesson.flow.plan.askTeacher.cta')"],
  [/title: 'أسئلة علاجية'/g, "title: t('student.lesson.flow.plan.remedial.title')"],
  [/description: 'تدرّبي بسؤالين على نفس فكرة الخطأ قبل إعادة الاختبار\.'/g, "description: t('student.lesson.flow.plan.remedial.description')"],
  [/remedialQuestions\.value\.length \? 'إعادة توليد' : 'ابدأ'/g, "remedialQuestions.value.length ? t('student.lesson.flow.plan.remedial.regenerate') : t('student.lesson.flow.plan.remedial.start')"],
  [/title: 'اختبار متابعة'/g, "title: t('student.lesson.flow.plan.followUp.title')"],
  [/description: 'بعد المراجعة جرّبي اختباراً جديداً حتى ترتفع النتيجة\.'/g, "description: t('student.lesson.flow.plan.followUp.description')"],
  [/title: 'الفهم الأساسي مكتمل'/g, "title: t('student.lesson.flow.plan.mastery.title')"],
  [/description: 'نتيجتك كاملة، فانتقلي من الحفظ إلى تثبيت الفكرة\.'/g, "description: t('student.lesson.flow.plan.mastery.description')"],
  [/title: 'سؤال تحدّي'/g, "title: t('student.lesson.flow.plan.challenge.title')"],
  [/keywordText \? `اطلبي سؤالاً أعمق عن: \$\{keywordText\}\.` : 'اطلبي سؤالاً أعمق من الدرس\.'/g, "keywordText ? t('student.lesson.flow.plan.challenge.withKeywords', { keywords: keywordText }) : t('student.lesson.flow.plan.challenge.generic')"],
  [/cta: 'تحدّي'/g, "cta: t('student.lesson.flow.plan.challenge.cta')"],
  [/title: 'اختبار مختلف'/g, "title: t('student.lesson.flow.plan.newQuiz.title')"],
  [/description: 'ولّدي اختباراً جديداً لتتأكدي أن الفهم ثابت\.'/g, "description: t('student.lesson.flow.plan.newQuiz.description')"],
  [/if \(remaining <= 0\) return 'اكتمل الاختبار\.'/g, "if (remaining <= 0) return t('student.lesson.flow.quiz.remaining.done')"],
  [/if \(remaining === 1\) return 'بقي سؤال واحد لإكمال الاختبار\.'/g, "if (remaining === 1) return t('student.lesson.flow.quiz.remaining.one')"],
  [/if \(remaining === 2\) return 'بقي سؤالان لإكمال الاختبار\.'/g, "if (remaining === 2) return t('student.lesson.flow.quiz.remaining.two')"],
  [/return `بقي \$\{remaining\} أسئلة لإكمال الاختبار\.`/g, "return t('student.lesson.flow.quiz.remaining.many', { n: remaining })"],
]

for (const [re, to] of reps) {
  const before = c
  c = c.replace(re, to)
  if (c === before) console.warn('no match', re.toString().slice(0, 60))
}

writeFileSync(path, c, 'utf8')
console.log('Fixed StudentLessonView')
