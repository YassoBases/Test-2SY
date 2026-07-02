/** Fix embedded {{ t() }} inside quoted strings and corrupted partial replacements. */
import { readFileSync, writeFileSync, readdirSync, statSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = join(dirname(fileURLToPath(import.meta.url)), '..')

const REPLACEMENTS = [
  ["getErrorMessage(e, 'تعذر {{ t('student.languages.common.submit') }} الإجابات')", "getErrorMessage(e, t('student.languages.errors.submitAnswers'))"],
  ["getErrorMessage(e, 'تعذر ال{{ t('student.languages.common.submit') }}')", "getErrorMessage(e, t('student.languages.errors.submitWriting'))"],
  ["getErrorMessage(e, 'تعذr {{ t('student.languages.common.submit') }} الاختبار')", "getErrorMessage(e, t('student.languages.errors.submitTest'))"],
  ["getErrorMessage(e, 'تعذر {{ t('student.languages.common.submit') }} الاختبار')", "getErrorMessage(e, t('student.languages.errors.submitTest'))"],
  ["getErrorMessage(e, 'تعذر حفظ ال{{ t('student.lesson.plan.chip.review') }}')", "getErrorMessage(e, t('student.languages.errors.saveReview'))"],
  ["e?.response?.data?.detail || 'تعذر {{ t('student.languages.common.submit') }} الرسالة'", "e?.response?.data?.detail || t('student.languages.errors.submitMessage')"],
  ["loadError.value = 'التسجيل فارغ — {{ t('student.languages.common.retry') }}'", "loadError.value = t('student.languages.errors.emptyRecording')"],
  ["return `${step.label} — {{ t('student.lesson.card.status.completed') }}ة`", "return `${step.label} — ${t('student.lesson.card.status.completed')}`"],
  ["return 'راجع الدرس و{{ t('student.languages.common.retry') }}'", "return t('student.lesson.quiz.results.review')"],
  ["label: 'مشاهدة {{ t('student.lesson.fallback.tabs.video') }} بالكامل (90%)'", "label: t('student.lesson.completion.requirements.video')"],
  ["detail: p.quiz_submitted ? 'تم ال{{ t('student.languages.common.submit') }}' : 'لم يُرسل بعد'", "detail: p.quiz_submitted ? t('student.lesson.completion.quizSubmitted.yes') : t('student.lesson.completion.quizSubmitted.no')"],
  ["return p.quiz_submitted ? 'تم ال{{ t('student.languages.common.submit') }}' : 'لم يُرسل بعد'", "return p.quiz_submitted ? t('student.lesson.completion.quizSubmitted.yes') : t('student.lesson.completion.quizSubmitted.no')"],
  ['{{ t(\'student.teacherContact.status\') }}ون مؤخراً', "{{ t('student.parents.summary.recent') }}"],
  ['أهداف {{ t(\'student.lesson.card.status.completed\') }}ة', "{{ t('student.languages.progress.goalsCompleted') }}"],
  ['subtitle="أين أنت اليوم — وما {{ t(\'student.lesson.header.nextStep\') }} في رحلتك"', ':subtitle="t(\'student.languages.curriculum.subtitle\')"'],
  ['title="{{ t(\'student.lesson.fallback.tabs.pdf\') }} الصوتي غير متوفر"', ':title="t(\'student.languages.listening.noAudio\')"'],
  ['{{ t(\'student.languages.common.submit\') }} الإجابات', "{{ t('student.languages.reading.submitAnswers') }}"],
  ['{{ t(\'student.languages.common.back\') }} للدورة', "{{ t('student.manualQuiz.backToCourse') }}"],
  ['{{ t(\'student.lesson.quiz.results.retry\') }} بعد', "{{ t('student.languages.hub.retakeAfter') }}"],
]

function walk(dir, out = []) {
  for (const name of readdirSync(dir)) {
    const p = join(dir, name)
    if (statSync(p).isDirectory()) walk(p, out)
    else if (name.endsWith('.vue')) out.push(p)
  }
  return out
}

for (const dir of [join(root, 'src/views/student'), join(root, 'src/components/student')]) {
  for (const file of walk(dir)) {
    let c = readFileSync(file, 'utf8')
    const before = c
    for (const [from, to] of REPLACEMENTS) {
      c = c.split(from).join(to)
    }
    // generic: '...{{ t('KEY') }}...' in script -> template literal
    c = c.replace(/'([^'\\]*)\{\{\s*t\('([^']+)'\)\s*\}\}([^'\\]*)'/g, (_, pre, key, post) => {
      if (!pre && !post) return `t('${key}')`
      return `\`${pre}\${t('${key}')}${post}\``
    })
    if (c !== before) {
      writeFileSync(file, c, 'utf8')
      console.log('Fixed', file.replace(root + '\\', ''))
    }
  }
}
console.log('Done')
