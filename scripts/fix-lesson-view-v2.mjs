import { readFileSync, writeFileSync } from 'node:fs'

const p = 'src/views/student/StudentLessonView.vue'
let c = readFileSync(p, 'utf8')

function sub(re, to) {
  const b = c
  c = c.replace(re, to)
  if (b === c) console.warn('miss', String(re).slice(0, 50))
}

sub(/^\s*اسأل [\u0600-\u06FF\s]+$/m, "                {{ t('student.lesson.tabs.askTeacher') }}")
sub(/\{\{ t\('student\.lesson\.fallback\.tabs\.video'\) \}\}[^\n]+/g, "{{ t('student.lesson.fallback.videoHint') }}")
sub(/>\s*الانتقال إلى الفيديو[^\n]+</g, ">{{ t('student.lesson.fallback.goToVideo') }}<")
sub(/>\s*ملف الدرس جزء[^\n]+</g, ">{{ t('student.lesson.fallback.pdfHint') }}<")
sub(/>\s*الانتقال إلى الملف[^\n]+</g, ">{{ t('student.lesson.fallback.goToPdf') }}<")
sub(/>\s*هل تريد[^\n]+</g, ">{{ t('student.lesson.chat.clear.confirm') }}<")
sub(/:\s*'ركّز على المحادثة[^']+'/g, ": t('student.lesson.quiz.noAiSource')")
sub(/<div class="text-caption">المعل[^\n]+<\/div>/g, '<div class="text-caption">{{ t(\'student.lesson.ai.preparingHint\') }}</div>')
sub(/if \(lesson\.value\.ai_processing\) return 'المعل[^']+'/g, "if (lesson.value.ai_processing) return t('student.lesson.ai.chatDisabledHint')")
sub(/text: 'اسألي المعل[^']+'/g, "text: t('student.lesson.flow.askTeacher.text')")
sub(/text: 'مكتمل\.[^']+'/g, "text: t('student.lesson.flow.complete.text')")
sub(/title: 'اسألي المعل[^']+'/g, "title: t('student.lesson.flow.plan.askTeacher.title')")
sub(/description: 'خلي المعل[^']+'/g, "description: t('student.lesson.flow.plan.askTeacher.description')")
sub(/title: 'تعذر تحميل الدرس'/g, "title: t('student.lesson.errors.loadTitle')")
sub(/getErrorMessage\(err, 'تعذر تحميل هذا الدرس[^']+'\)/g, "getErrorMessage(err, t('student.lesson.errors.load'))")

writeFileSync(p, c)
console.log('ok')
