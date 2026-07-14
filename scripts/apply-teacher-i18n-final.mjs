/**
 * Fast targeted i18n patch for remaining teacher hardcoded strings.
 * Does NOT use broad regex — only explicit per-file replacements.
 */
import fs from 'fs'
import path from 'path'

const ROOT = path.resolve(import.meta.dirname, '..')

/** @type {[string, string, string][]} */
const newEntries = [
  ['labels.gradeNumber', 'Grade {grade}', 'الصف {grade}'],
  ['labels.subjectGradeDash', '{subject} — Grade {grade}', '{subject} — الصف {grade}'],
  ['labels.subjectGradeDot', '{subject} · Grade {grade}', '{subject} · الصف {grade}'],
  ['labels.studentCount', '{count} students', '{count} طالب'],
  ['labels.lessonCount', '{count} lessons', '{count} دروس'],
  ['labels.lessonsPublished', '{count} lessons published', '{count} دروس منشورة'],
  ['labels.quizCount', '{count} quizzes', '{count} كويز'],
  ['labels.pointsCount', '{count} points', '{count} نقطة'],
  ['labels.questionCount', '{count} questions', '{count} سؤال'],
  ['labels.optionNumber', 'Option {n}', 'خيار {n}'],
  ['labels.optionTextNumber', 'Option {n} text', 'نص الخيار {n}'],
  ['labels.trueLabel', 'True', 'صح'],
  ['labels.falseLabel', 'False', 'خطأ'],
  ['labels.choicesCount', '{count} options', '{count} خيارات'],
  ['labels.pagesCount', '{count} pages', '{count} صفحة'],
  ['labels.minutesCount', '{count} minutes', '{count} دقيقة'],
  ['labels.durationShort', '{n} min', '{n} د'],
  ['labels.dayCount', '{count} days', '{count} يوم'],
  ['labels.essayCount', '{count} essay', '{count} مقالي'],
  ['labels.titleAsterisk', 'Title *', 'العنوان *'],
  ['labels.orgInstitution', 'Organization / Institution', 'الجهة / المؤسسة'],
  ['labels.institutionSchool', 'Institution / School', 'المؤسسة / المدرسة'],
  ['labels.documentTitleAsterisk', 'Document title *', 'عنوان المستند *'],
  ['labels.lastEditAt', 'Last edit {date}', 'آخر تعديل {date}'],
  ['labels.lastActivityAt', 'Last activity {date}', 'آخر نشاط {date}'],
  ['labels.averageValue', 'Average {value}', 'متوسط {value}'],
  ['labels.willDeleteOnSave', 'Will delete {type} on save', 'سيتم حذف {type} عند الحفظ'],
  ['labels.noTypeUploadNew', 'No {type} — upload a new file', 'لا يوجد {type} — ارفع ملفاً جديداً'],
  ['labels.replaceFile', 'Replace: {name}', 'استبدال: {name}'],
  ['labels.studentInitial', 'S', 'ط'],
  ['labels.teacherInitial', 'T', 'م'],
  ['labels.currencySyp', '{amount} SYP', '{amount} ل.س'],

  ['students.avgScoreLabel', 'Average score', 'متوسط النتيجة'],
  ['students.editNoteTitle', 'Edit note', 'تعديل الملاحظة'],
  ['students.subjectGradeCaption', '{subject} — Grade {grade}', '{subject} — الصف {grade}'],

  ['grades.oneActiveClass', 'One active class', 'صف واحد نشط'],
  ['grades.activeClassesCount', '{count} active classes', '{count} صفوف نشطة'],
  ['grades.activeOfTotal', '{active} of {total} classes', '{active} من {total} صفوف'],
  ['grades.subjectCourseDesc', 'Subject {subject} — Grade {grade}', 'مادة {subject} — الصف {grade}'],

  ['quizzes.deleteConfirmTitle', 'Delete quiz «{title}»?', 'حذف الكويز «{title}»؟'],
  ['quizzes.questionsPointsSummary', '{questions} questions · {points} points', '{questions} سؤال · {points} نقطة'],
  ['quizzes.questionIndex', 'Question {index}', 'سؤال {index}'],
  ['quizzes.questionDetail', 'Question {n} · {type} · {points} points', 'سؤال {n} · {type} · {points} نقطة'],
  ['quizzes.attemptsTotal', '{count} attempts', '{count} محاولة'],
  ['quizzes.attemptsCompleted', '{completed} of {total} completed attempts', '{completed} من {total} محاولة مكتملة'],
  ['quizzes.enrolledPercent', '{percent}% of enrolled', '{percent}% من المسجّلين'],
  ['quizzes.totalScoreAttempts', 'Total quiz score: {points} · {count} attempts', 'إجمالي درجات الكويز: {points} · {count} محاولة'],
  ['quizzes.zeroQuizzes', '0 quizzes', '0 كويز'],
  ['quizzes.oneQuiz', '1 quiz', '1 كويز'],
  ['quizzes.twoQuizzes', '2 quizzes', '2 كويز'],
  ['quizzes.nQuizzes', '{count} quizzes', '{count} كويز'],
  ['quizzes.oneAttempt', '1 attempt', '1 محاولة'],
  ['quizzes.nAttempts', '{count} attempts', '{count} محاولة'],
  ['quizzes.highestResult', 'Highest result', 'أعلى نتيجة'],
  ['quizzes.lastUpdatedAt', 'Last updated: {date}', 'آخر تحديث: {date}'],
  ['quizzes.passingPercent', 'Passing {percent}%', 'النجاح {percent}%'],
  ['quizzes.unpublish', 'Unpublish', 'إلغاء النشر'],
  ['quizzes.pointsMeta', '{earned} of {max} points', '{earned} نقطة'],

  ['cv.sectionsNav', 'Experience · Certificates · Achievements · Publications', 'خبرات · شهادات · إنجازات · منشورات تعليمية'],

  ['profileEntry.editTitle', 'Edit', 'تعديل'],
  ['profileEntry.addTitle', 'Add', 'إضافة'],

  ['voice.samplesCountShort', '{count} / {max} voice samples', '{count} / {max} عينة صوت'],
  ['voice.maxSamplesShort', 'Maximum {max} samples', 'الحد الأقصى {max} عينات'],
  ['voice.replaceTarget', 'Replace {name}', 'استبدال {name}'],
  ['voice.deleteConfirmQuestion', 'Delete {name}?', 'هل تريد حذف {name}؟'],

  ['pdf.dragDropPdf', 'Drag PDF file and drop here', 'اسحب ملف PDF وأفلته هنا'],
  ['pdf.orClickChoose', 'or click to choose file — PDF only · up to {size}', 'أو انقر لاختيار ملف — PDF فقط · حتى {size}'],
  ['pdf.choosePdfFile', 'Choose PDF file', 'اختيار ملف PDF'],
  ['pdf.uploadZoneAria', 'PDF upload zone — drag file or click to choose', 'منطقة رفع PDF، اسحب الملف أو انقر للاختيار'],
  ['pdf.uploadForPreview', 'Upload a PDF file to preview', 'ارفع ملف PDF لعرض المعاينة'],

  ['lessons.dragVideoDrop', 'Drag video and drop here', 'اسحب الفيديو وأفلته هنا'],
  ['lessons.dragDropGeneric', 'Drag and drop here', 'اسحب وأفلت هنا'],
  ['lessons.pasteVideoLink', 'Paste a YouTube, Vimeo, Google Drive, or direct MP4 link — ideal for generating title and description.', 'الصق رابط YouTube أو Vimeo أو Google Drive أو MP4 مباشر — مثالي لتوليد العنوان والوصف.'],
  ['lessons.videoLinkFormats', 'YouTube · Vimeo · Google Drive · direct MP4 link', 'YouTube · Vimeo · Google Drive · رابط MP4 مباشر'],
  ['lessons.uploadPdfHint', 'Upload a PDF for the lesson — as important as video', 'ارفع ملف PDF للدرس — بنفس أهمية الفيديو'],
  ['lessons.dragPdfDrop', 'Drag PDF and drop here', 'اسحب PDF وأفلته هنا'],
  ['lessons.pdfFormats', 'PDF · up to {size}', 'PDF · حتى {size}'],
  ['lessons.videoLinkTab', 'Video link', 'رابط فيديو'],
  ['lessons.uploadPdfTab', 'Upload PDF', 'رفع PDF'],
  ['lessons.noPdf', 'No PDF', 'لا يوجد PDF'],
  ['lessons.fromOfStudents', '{completed} of {total} students', '{completed} من أصل {total} طالب'],
  ['lessons.aiToolsTitle', 'AI tools', 'أدوات AI'],
  ['lessons.defaultToolbarTitle', 'Lessons', 'الدروس'],
  ['lessons.generating', '✨ Generating...', '✨ جاري التوليد...'],
  ['lessons.generate', '✨ Generate', '✨ توليد'],
  ['lessons.generateTitleDesc', '✨ Generate title & description', '✨ توليد العنوان والوصف'],
  ['lessons.fileMustBePdf', 'File must be PDF', 'الملف يجب أن يكون PDF'],
  ['lessons.fileTooLarge', 'File is larger than {size}', 'الملف أكبر من {size}'],
  ['lessons.uploadPdfRequired', 'Upload a PDF file', 'ارفع ملف PDF'],
  ['lessons.lessonTitleAsterisk', 'Lesson title *', 'عنوان الدرس *'],
  ['lessons.openPdfAria', 'Open PDF file', 'فتح ملف PDF'],

  ['course.createClassBtn', 'Create class', 'إنشاء الصف'],
  ['course.imageFormats', 'PNG or JPG · WebP', 'PNG أو JPG · WebP'],

  ['dashboard.teacherDefault', 'Teacher', 'المعلم'],
  ['dashboard.teacherInitial', 'T', 'م'],

  ['studentPreview.noActivity', 'No recorded activity', 'بدون نشاط مسجّل'],
  ['studentPreview.lastActivityRelative', 'Last activity {relative}', 'آخر نشاط {relative}'],

  ['parentNotes.editNoteTitle', 'Edit note', 'تعديل الملاحظة'],

  ['errors.serverNoQuizId', 'Server response missing quiz ID', 'استجابة الخادم لا تحتوي على معرّف الكويز'],
]

function setNested(obj, keyPath, value) {
  const parts = keyPath.split('.')
  let cur = obj
  for (let i = 0; i < parts.length - 1; i++) {
    cur[parts[i]] ??= {}
    cur = cur[parts[i]]
  }
  cur[parts[parts.length - 1]] = value
}

function mergeLocales() {
  for (const lang of ['en', 'ar']) {
    const file = path.join(ROOT, `src/locales/${lang}/teacher.json`)
    const data = JSON.parse(fs.readFileSync(file, 'utf8'))
    for (const [key, enText, arText] of newEntries) {
      setNested(data, key, lang === 'en' ? enText : arText)
    }
    fs.writeFileSync(file, JSON.stringify(data, null, 2) + '\n', 'utf8')
  }
}

function ensureUseI18n(content) {
  if (!content.includes("t('teacher.") && !content.includes('$t(')) return content
  if (content.includes('useI18n')) return content
  if (!content.includes('<script setup>')) return content
  return content.replace(
    /<script setup>\s*\n/,
    "<script setup>\nimport { useI18n } from 'vue-i18n'\n\nconst { t } = useI18n()\n\n",
  )
}

/** @type {Record<string, (c: string) => string>} */
const filePatches = {
  'src/views/teacher/TeacherStudentsView.vue': (c) =>
    c
      .replace('{{ total }} طالب', "{{ $t('teacher.labels.studentCount', { count: total }) }}")
      .replace(
        "<td>{{ s.grade ? `الصف ${s.grade}` : '—' }}</td>",
        "<td>{{ s.grade ? $t('teacher.labels.gradeNumber', { grade: s.grade }) : '—' }}</td>",
      )
      .replace(
        "{{ s.is_active ? 'نشط' : 'منتهٍ' }}",
        "{{ s.is_active ? $t('teacher.status.active') : $t('teacher.status.expired') }}",
      )
      .replace(
        'const gradeItems = ACADEMIC_GRADES.map((g) => ({ title: `الصف ${g}`, value: g }))',
        "const gradeItems = ACADEMIC_GRADES.map((g) => ({ title: t('teacher.labels.gradeNumber', { grade: g }), value: g }))",
      ),

  'src/views/teacher/TeacherSetupView.vue': (c) =>
    c.replace(
      '<p class="text-caption text-medium-emphasis mb-2">الصف {{ grade }}</p>',
      "<p class=\"text-caption text-medium-emphasis mb-2\">{{ $t('teacher.labels.gradeNumber', { grade }) }}</p>",
    ),

  'src/views/teacher/TeacherQuizzesView.vue': (c) =>
    c
      .replace(
        '<p class="teacher-quiz-create-sheet__course-meta">الصف {{ course.grade }}</p>',
        "<p class=\"teacher-quiz-create-sheet__course-meta\">{{ $t('teacher.labels.gradeNumber', { grade: course.grade }) }}</p>",
      )
      .replace(
        'return `${courseSubject(course)} • الصف ${course.grade}`',
        "return `${courseSubject(course)} • ${t('teacher.labels.gradeNumber', { grade: course.grade })}`",
      )
      .replace(
        'const gradePhrase = `الصف ${grade}`.toLowerCase()',
        "const gradePhrase = t('teacher.labels.gradeNumber', { grade }).toLowerCase()",
      )
      .replace(
        'if (!confirm(`حذف الكويز «${item.quiz.title}»؟`)) return',
        "if (!confirm(t('teacher.quizzes.deleteConfirmTitle', { title: item.quiz.title }))) return",
      ),

  'src/views/teacher/TeacherAnalyticsView.vue': (c) =>
    c.replace(
      'classLabel: `${course.subject_name} · الصف ${course.grade}`',
      "classLabel: t('teacher.analytics.classLabel', { subject: course.subject_name, grade: course.grade })",
    ),

  'src/views/teacher/TeacherStudentProfileView.vue': (c) =>
    c
      .replace(
        'الإحصائيات التالية خاصة بموادك فقط:',
        "{{ $t('teacher.students.statsScope') }}",
      )
      .replace(
        "{{ profile.info.account_status === 'active' ? 'نشط' : 'منتهٍ' }}",
        "{{ profile.info.account_status === 'active' ? $t('teacher.status.active') : $t('teacher.status.expired') }}",
      )
      .replace(
        '<template #subtitle>{{ profile.info.grade ? `الصف ${profile.info.grade}` : \'—\' }}</template>',
        "<template #subtitle>{{ profile.info.grade ? $t('teacher.labels.gradeNumber', { grade: profile.info.grade }) : '—' }}</template>",
      )
      .replace(
        '{{ c.subject_name }} — الصف {{ c.grade }}',
        "{{ $t('teacher.students.subjectGradeCaption', { subject: c.subject_name, grade: c.grade }) }}",
      )
      .replace(
        "{{ editingNote ? 'تعديل الملاحظة' : 'ملاحظة جديدة' }}",
        "{{ editingNote ? $t('teacher.students.editNoteTitle') : $t('teacher.students.newNote') }}",
      )
      .replace("label: 'متوسط النتيجة'", "label: t('teacher.students.avgScoreLabel')")
      .replace('`${a.active_streak} يوم`', "t('teacher.labels.dayCount', { count: a.active_streak })")
      .replace(
        "const map = { active: 'نشط', expiring_soon: 'ينتهي قريباً', expired: 'منتهٍ', pending: 'معلّق' }",
        "const map = { active: t('teacher.status.active'), expiring_soon: t('teacher.status.expiringSoon'), expired: t('teacher.status.expired'), pending: t('teacher.status.pending') }",
      )
      .replace("noteError.value = 'أدخل نص الملاحظة'", "noteError.value = t('teacher.validation.enterNote')")
      .replace(
        "if (!window.confirm('حذف هذه الملاحظة؟')) return",
        "if (!window.confirm(t('teacher.confirm.deleteNote'))) return",
      ),

  'src/views/teacher/TeacherQuizResultsView.vue': (c) =>
    c
      .replace('آخر تحديث: {{ lastUpdatedLabel }}', "{{ $t('teacher.quizzes.lastUpdatedAt', { date: lastUpdatedLabel }) }}")
      .replace(
        'description="عندما يبدأ الطلاب بحل الكويز ستظهر نتائجهم هنا مع إمكانية المراجعة والتصحيح."',
        ":description=\"$t('teacher.quizzes.noAttemptsHint')\"",
      )
      .replace('· {{ attempt.pending_essay_count }} مقالي', "· {{ $t('teacher.labels.essayCount', { count: attempt.pending_essay_count }) }}")
      .replace(
        ':meta="`${formatScore(ans.points_earned ?? 0, ans.max_points)} نقطة`"',
        ":meta=\"$t('teacher.labels.pointsCount', { count: formatScore(ans.points_earned ?? 0, ans.max_points) })\"",
      )
      .replace('label="النقاط"', ":label=\"$t('teacher.labels.points')\"")
      .replace(
        "if (subject && grade) return `${subject} · الصف ${grade}`",
        "if (subject && grade) return t('teacher.analytics.classLabel', { subject, grade })",
      )
      .replace(
        "if (completed === total) return `${total} محاولة`",
        "if (completed === total) return t('teacher.quizzes.attemptsTotal', { count: total })",
      )
      .replace(
        'return `${completed} من ${total} محاولة مكتملة`',
        "return t('teacher.quizzes.attemptsCompleted', { completed, total })",
      )
      .replace(
        'return `${analytics.value.completion_rate ?? 0}% من المسجّلين`',
        "return t('teacher.quizzes.enrolledPercent', { percent: analytics.value.completion_rate ?? 0 })",
      )
      .replace(
        "const points = total != null ? `${total} نقطة` : '—'",
        "const points = total != null ? t('teacher.labels.pointsCount', { count: total }) : '—'",
      )
      .replace(
        'return `إجمالي درجات الكويز: ${points} · ${count} محاولة`',
        "return t('teacher.quizzes.totalScoreAttempts', { points, count })",
      )
      .replace(
        'message: `يوجد ${pending} إجابة مقالية تحتاج مراجعة يدوية قبل اعتماد الدرجة النهائية.`',
        "message: t('teacher.quizzes.essayReviewHint', { count: pending })",
      )
      .replace(
        'message: `${belowPassing.length} طالب/ة حصلوا على أقل من ${passing}% — قد يحتاجون متابعة إضافية.`',
        "message: t('teacher.quizzes.belowPassingHint', { count: belowPassing.length, threshold: passing })",
      )
      .replace(
        'message: `${inProgress} طالب/ة ما زالوا يحلّون الكويز ولم يُسلّموا بعد.`',
        "message: t('teacher.quizzes.inProgressHint', { count: inProgress })",
      )
      .replace(
        'message: `أكمل ${analytics.value.completion_rate}% فقط من الطلاب المسجّلين (${analytics.value.attempted_count} من ${analytics.value.enrolled_students}).`',
        "message: t('teacher.quizzes.lowCompletionHint', { percent: analytics.value.completion_rate, count: `${analytics.value.attempted_count} / ${analytics.value.enrolled_students}` })",
      )
      .replace(
        'message: `الفجوة بين أعلى نتيجة (${formatPercent(highest)}) وأدنى نتيجة (${formatPercent(lowest)}) تشير إلى اختلاف مستويات الفهم.`',
        "message: t('teacher.quizzes.varianceHint', { high: formatPercent(highest), low: formatPercent(lowest) })",
      )
      .replace("title: 'لا توجد محاولات بعد'", "title: t('teacher.quizzes.noAttempts')")
      .replace(
        "const map = { in_progress: 'جاري', submitted: 'مُسلَّم', graded: 'مُصحَّح' }",
        "const map = { in_progress: t('teacher.status.inProgress'), submitted: t('teacher.status.submitted'), graded: t('teacher.status.graded') }",
      )
      .replace(
        "if ('selected_index' in answer) return `خيار ${Number(answer.selected_index) + 1}`",
        "if ('selected_index' in answer) return t('teacher.labels.optionNumber', { n: Number(answer.selected_index) + 1 })",
      )
      .replace(
        "if ('value' in answer) return answer.value ? 'صح' : 'خطأ'",
        "if ('value' in answer) return answer.value ? t('teacher.labels.trueLabel') : t('teacher.labels.falseLabel')",
      ),

  'src/views/teacher/TeacherQuizBuilderView.vue': (c) =>
    c
      .replace(
        '{{ questions.length }} سؤال · {{ totalPoints }} نقطة',
        "{{ $t('teacher.quizzes.questionsPointsSummary', { questions: questions.length, points: totalPoints }) }}",
      )
      .replace(
        "quiz.title?.trim() || (isNew.value ? 'كويز جديد' : 'كويز')",
        "quiz.title?.trim() || (isNew.value ? t('teacher.quizzes.newQuiz') : t('teacher.labels.quiz'))",
      )
      .replace(
        "? `${quiz.duration_minutes} د`",
        "? t('teacher.labels.durationShort', { n: quiz.duration_minutes })",
      )
      .replace(": 'غير محدود'", ": t('teacher.status.unlimited')")
      .replace(
        "|| `خيار ${i + 1}`",
        "|| t('teacher.labels.optionNumber', { n: i + 1 })",
      )
      .replace(
        "dueAtError.value = 'موعد التسليم يجب أن يكون في المستقبل'",
        "dueAtError.value = t('teacher.quizzes.deadlineFuture')",
      )
      .replace(
        "throw new Error('موعد التسليم غير صالح')",
        "throw new Error(t('teacher.quizzes.deadlineInvalid'))",
      )
      .replace(
        "questionFormError.value = 'نص السؤال مطلوب'",
        "questionFormError.value = t('teacher.quizzes.questionRequired')",
      )
      .replace(
        "questionFormError.value = 'النقاط يجب أن تكون 1 على الأقل'",
        "questionFormError.value = t('teacher.quizzes.pointsMin')",
      )
      .replace(
        "questionFormError.value = 'أضف خيارين على الأقل'",
        "questionFormError.value = t('teacher.quizzes.minTwoOptions')",
      )
      .replace(
        "questionFormError.value = 'الإجابة النموذجية مطلوبة'",
        "questionFormError.value = t('teacher.quizzes.modelAnswerRequired')",
      )
      .replace(
        "throw new Error('استجابة الخادم لا تحتوي على معرّف الكويز')",
        "throw new Error(t('teacher.errors.serverNoQuizId'))",
      )
      .replace(
        "if (!confirm('حذف هذا السؤال؟')) return",
        "if (!confirm(t('teacher.quizzes.deleteQuestionConfirm'))) return",
      ),

  'src/views/teacher/TeacherLessonsView.vue': (c) =>
    c.replace(
      'course_label: `${detail.subject_name} — الصف ${detail.grade}`',
      "course_label: t('teacher.labels.subjectGradeDash', { subject: detail.subject_name, grade: detail.grade })",
    ),

  'src/views/teacher/TeacherLessonPreviewView.vue': (c) =>
    c
      .replace(
        "{{ lesson.is_visible ? 'منشور' : 'مخفي' }}",
        "{{ lesson.is_visible ? $t('teacher.status.published') : $t('teacher.status.hidden') }}",
      )
      .replace(
        'هذا الدرس يحتاج إعادة معالجة AI بعد تعديل المحتوى. اضغط «إعادة معالجة AI» أعلاه.',
        "{{ $t('teacher.lessons.needsReprocessBanner') }}",
      )
      .replace(
        '<p v-else class="text-center text-medium-emphasis pa-8 mb-0">لا يوجد PDF</p>',
        "<p v-else class=\"text-center text-medium-emphasis pa-8 mb-0\">{{ $t('teacher.lessons.noPdf') }}</p>",
      )
      .replace(
        'هذه المعاينة تعرض محتوى الدرس كما يراه الطالب (فيديو / PDF / صوت). المعلّم الذكي والكويز متاحان للطلاب بعد اكتمال المعالجة.',
        "{{ $t('teacher.lessons.previewNote') }}",
      )
      .replace(
        "if (lesson.value.grade) parts.push(`الصف ${lesson.value.grade}`)",
        "if (lesson.value.grade) parts.push(t('teacher.labels.gradeNumber', { grade: lesson.value.grade }))",
      )
      .replace(
        "const map = { draft: 'مسودة', processing: 'جاري المعالجة', processed: 'جاهز', error: 'خطأ' }",
        "const map = { draft: t('teacher.status.draft'), processing: t('teacher.status.processing'), processed: t('teacher.status.ready'), error: t('teacher.status.error') }",
      )
      .replace(
        "showInfo('بدأت إعادة معالجة الذكاء الاصطناعي')",
        "showInfo(t('teacher.status.processingAiRetry'))",
      ),

  'src/views/teacher/TeacherGradesView.vue': (c) =>
    c
      .replace(
        "return n === 1 ? 'صف واحد نشط' : `${n} صفوف نشطة`",
        "return n === 1 ? t('teacher.grades.oneActiveClass') : t('teacher.grades.activeClassesCount', { count: n })",
      )
      .replace(
        'return `${n} من ${courses.value.length} صفوف`',
        "return t('teacher.grades.activeOfTotal', { active: n, total: courses.value.length })",
      ),

  'src/views/teacher/TeacherGradeDetailView.vue': (c) =>
    c
      .replace(
        "{{ course.is_published ? 'منشور' : 'مسودة' }}",
        "{{ course.is_published ? $t('teacher.status.published') : $t('teacher.status.draft') }}",
      )
      .replace(
        'return `${course.value.subject_name} — الصف ${course.value.grade}`',
        "return t('teacher.labels.subjectGradeDash', { subject: course.value.subject_name, grade: course.value.grade })",
      )
      .replace(
        'return course.value.description || `مادة ${course.value.subject_name} — الصف ${course.value.grade}`',
        "return course.value.description || t('teacher.grades.subjectCourseDesc', { subject: course.value.subject_name, grade: course.value.grade })",
      )
      .replace(
        "return `${v.toLocaleString('ar-SY')} ل.س`",
        "return t('teacher.labels.currencySyp', { amount: v.toLocaleString('ar-SY') })",
      ),

  'src/components/teacher/ProcessingOverlay.vue': (c) =>
    c
      .replace(
        "{{ subtitle || 'نستخرج المحتوى من PDF ونحلّل أسلوب صوتك لبناء المعلّم الذكي' }}",
        "{{ subtitle || `${t('teacher.processing.extractFrom')} PDF ${t('teacher.processing.voiceAnalysis')}` }}",
      )
      .replace(
        `const steps = [
  'قراءة ملف PDF...',
  'استخراج النص والصور...',
  'تحليل عينة الصوت...',
  'بناء نموذج أسلوب الشرح...',
  'إعداد المعلّم الذكي...',
]`,
        `const steps = computed(() => [
  t('teacher.processing.readFile') + ' PDF...',
  t('teacher.processing.extractText'),
  t('teacher.processing.analyzeVoice'),
  t('teacher.processing.buildStyle'),
  t('teacher.processing.prepareTeacher'),
])`,
      )
      .replace(
        'const stepLabel = computed(() => steps[props.step] ?? steps[0])',
        'const stepLabel = computed(() => steps.value[props.step] ?? steps.value[0])',
      ),

  'src/components/teacher/quizzes/TeacherQuizClassContext.vue': (c) =>
    c.replace(
      'return `الصف ${props.grade}`',
      "return t('teacher.labels.gradeNumber', { grade: props.grade })",
    ),

  'src/components/teacher/quizzes/TeacherQuizClassGroup.vue': (c) =>
    c
      .replace(
        '<h2 :id="headingId" class="teacher-quiz-group__grade">الصف {{ grade }}</h2>',
        "<h2 :id=\"headingId\" class=\"teacher-quiz-group__grade\">{{ $t('teacher.labels.gradeNumber', { grade }) }}</h2>",
      )
      .replace("if (n === 0) return '0 كويز'", "if (n === 0) return t('teacher.quizzes.zeroQuizzes')")
      .replace("if (n === 1) return '1 كويز'", "if (n === 1) return t('teacher.quizzes.oneQuiz')")
      .replace("if (n === 2) return '2 كويز'", "if (n === 2) return t('teacher.quizzes.twoQuizzes')")
      .replace('return `${n} كويز`', "return t('teacher.quizzes.nQuizzes', { count: n })"),

  'src/components/teacher/TeacherVoiceProfileSection.vue': (c) =>
    c
      .replace(
        '{{ sampleCount }} / {{ maxVoiceSamples }} عينة صوت',
        "{{ $t('teacher.voice.samplesCountShort', { count: sampleCount, max: maxVoiceSamples }) }}",
      )
      .replace(
        'الحد الأقصى {{ maxVoiceSamples }} عينات',
        "{{ $t('teacher.voice.maxSamplesShort', { max: maxVoiceSamples }) }}",
      )
      .replace(
        'استبدال {{ replaceTargetName }}',
        "{{ $t('teacher.voice.replaceTarget', { name: replaceTargetName }) }}",
      )
      .replace(
        'هل تريد حذف {{ sampleToDelete?.displayName }}؟',
        "{{ $t('teacher.voice.deleteConfirmQuestion', { name: sampleToDelete?.displayName }) }}",
      )
      .replace(
        "const previewText = ref('مرحباً بكم في درسنا اليوم. لنبدأ بشرح هذه النقطة المهمة معاً.')",
        "const previewText = ref(t('teacher.voice.previewText'))",
      )
      .replace(
        "showSuccess(replacingId ? 'تم استبدال العينة' : 'تمت إضافة العينة')",
        "showSuccess(replacingId ? t('teacher.status.sampleReplaced') : t('teacher.status.sampleAdded'))",
      ),

  'src/components/teacher/TeacherProfileEntryList.vue': (c) =>
    c
      .replace(
        "{{ editingId ? 'تعديل' : 'إضافة' }} — {{ title }}",
        "{{ editingId ? $t('teacher.profileEntry.editTitle') : $t('teacher.profileEntry.addTitle') }} — {{ title }}",
      )
      .replace('label="العنوان *"', ":label=\"$t('teacher.labels.titleAsterisk')\"")
      .replace('label="الجهة / المؤسسة"', ":label=\"$t('teacher.labels.orgInstitution')\"")
      .replace('label="المؤسسة / المدرسة"', ":label=\"$t('teacher.labels.institutionSchool')\"")
      .replace("default: 'لا توجد عناصر بعد'", "default: ''")
      .replace("emit('error', 'أدخل العنوان')", "emit('error', t('teacher.validation.enterTitle'))")
      .replace(
        "if (!window.confirm('حذف هذا العنصر؟')) return",
        "if (!window.confirm(t('teacher.confirm.deleteItem'))) return",
      ),

  'src/components/teacher/TeacherProfileCvEditor.vue': (c) =>
    c.replace(
      'خبرات · شهادات · إنجازات · منشورات تعليمية',
      "{{ $t('teacher.cv.sectionsNav') }}",
    ),

  'src/components/teacher/TeacherPortfolioEditor.vue': (c) =>
    c
      .replace('label="عنوان المستند *"', ":label=\"$t('teacher.labels.documentTitleAsterisk')\"")
      .replace("label: 'إجمالي الطلاب'", "label: t('teacher.portfolio.totalStudents')")
      .replace("onError('أدخل العنوان واختر ملفاً')", "onError(t('teacher.validation.enterTitleAndFile'))")
      .replace(
        "if (!window.confirm('حذف هذا المستند؟')) return",
        "if (!window.confirm(t('teacher.confirm.deleteDocument'))) return",
      ),

  'src/components/teacher/TeacherPortfolioDisplay.vue': (c) =>
    c.replace(
      "return { certificate: 'شهادة', degree: 'درجة علمية', training: 'تدريب' }[type] || type",
      "return { certificate: t('teacher.portfolio.certificate'), degree: t('teacher.portfolio.degree'), training: t('teacher.portfolio.training') }[type] || type",
    ),

  'src/components/teacher/TeacherParentNotesSection.vue': (c) =>
    c
      .replace(
        "{{ editing ? 'تعديل الملاحظة' : 'ملاحظة لولي الأمر' }}",
        "{{ editing ? $t('teacher.parentNotes.editNoteTitle') : $t('teacher.parentNotes.noteForParent') }}",
      )
      .replace("label_ar: 'منخفض'", "label_ar: t('teacher.parentNotes.priorityLow')")
      .replace("label_ar: 'متوسط'", "label_ar: t('teacher.parentNotes.priorityMedium')")
      .replace("label_ar: 'مرتفع'", "label_ar: t('teacher.parentNotes.priorityHigh')")
      .replace("label_ar: 'عاجل'", "label_ar: t('teacher.parentNotes.priorityUrgent')")
      .replace(
        "if (!window.confirm('حذف هذه الملاحظة؟')) return",
        "if (!window.confirm(t('teacher.confirm.deleteNote'))) return",
      )
      .replace(
        "if (!window.confirm('إغلاق المحادثة؟ لن يتمكن أحد من إضافة ردود جديدة.')) return",
        "if (!window.confirm(t('teacher.parentNotes.closeConfirm'))) return",
      ),

  'src/components/teacher/quizzes/TeacherQuizWorkspaceCard.vue': (c) =>
    c
      .replace('آخر تعديل {{ updatedLabel }}', "{{ $t('teacher.labels.lastEditAt', { date: updatedLabel }) }}")
      .replace('متوسط {{ averageLabel }}', "{{ $t('teacher.labels.averageValue', { value: averageLabel }) }}")
      .replace(
        "return props.quiz.is_published ? 'منشور' : 'مسودة'",
        "return props.quiz.is_published ? t('teacher.status.published') : t('teacher.status.draft')",
      )
      .replace("if (n === 1) return '1 محاولة'", "if (n === 1) return t('teacher.quizzes.oneAttempt')")
      .replace('return `${n} محاولة`', "return t('teacher.quizzes.nAttempts', { count: n })"),

  'src/components/teacher/quizzes/TeacherQuizResultsSummary.vue': (c) =>
    c.replace(
      'أعلى نتيجة',
      "{{ $t('teacher.quizzes.highestResult') }}",
    ),

  'src/components/teacher/quizzes/TeacherQuizQuestionEditor.vue': (c) =>
    c
      .replace('label="النقاط"', ":label=\"$t('teacher.labels.points')\"")
      .replace(
        'description="أضف خيارين على الأقل وحدد الإجابة الصحيحة"',
        ":description=\"$t('teacher.quizzes.optionsHint')\"",
      )
      .replace(':label="`خيار ${i + 1}`"', ":label=\"$t('teacher.labels.optionNumber', { n: i + 1 })\"")
      .replace(
        ':placeholder="`نص الخيار ${i + 1}`"',
        ":placeholder=\"$t('teacher.labels.optionTextNumber', { n: i + 1 })\"",
      )
      .replace('label="صح"', ":label=\"$t('teacher.labels.trueLabel')\"")
      .replace(
        'description="يُقارَن إجابة الطالب نصياً مع هذه الإجابة"',
        ":description=\"$t('teacher.quizzes.modelAnswerHint')\"",
      )
      .replace(
        'لا توجد إجابة نموذجية — سيُصحَّح هذا السؤال يدوياً من قبل المعلم بعد تسليم الطالب.',
        "{{ $t('teacher.quizzes.essayHint') }}",
      )
      .replace(
        "{{ editingQuestionId ? 'حفظ التعديل' : 'إضافة السؤال' }}",
        "{{ editingQuestionId ? $t('teacher.actions.saveQuestion') : $t('teacher.actions.addQuestionBtn') }}",
      )
      .replace("default: 'كويز جديد'", "default: ''")
      .replace(
        "props.editingQuestionId ? 'تعديل السؤال' : 'إضافة سؤال جديد'",
        "props.editingQuestionId ? t('teacher.quizzes.editQuestion') : t('teacher.quizzes.addNewQuestion')",
      ),

  'src/components/teacher/quizzes/TeacherQuizQuestionCard.vue': (c) =>
    c
      .replace('سؤال {{ index }}', "{{ $t('teacher.quizzes.questionIndex', { index }) }}")
      .replace('{{ question.points }} نقطة', "{{ $t('teacher.labels.pointsCount', { count: question.points }) }}")
      .replace('{{ choicesCount }} خيارات', "{{ $t('teacher.labels.choicesCount', { count: choicesCount }) }}"),

  'src/components/teacher/quizzes/TeacherQuizPreviewDialog.vue': (c) =>
    c
      .replace(
        'النجاح {{ passingScore }}%',
        "{{ $t('teacher.quizzes.passingPercent', { percent: passingScore }) }}",
      )
      .replace(
        '{{ questions.length }} سؤال',
        "{{ $t('teacher.labels.questionCount', { count: questions.length }) }}",
      )
      .replace(
        'سؤال {{ idx + 1 }} · {{ typeLabel(q.question_type) }} · {{ q.points }} نقطة',
        "{{ $t('teacher.quizzes.questionDetail', { n: idx + 1, type: typeLabel(q.question_type), points: q.points }) }}",
      )
      .replace(
        'if (Number.isFinite(n) && n >= 1) return `${n} دقيقة`',
        "if (Number.isFinite(n) && n >= 1) return t('teacher.labels.minutesCount', { count: n })",
      ),

  'src/components/teacher/quizzes/TeacherQuizDetailHero.vue': (c) =>
    c
      .replace(
        'آخر تعديل: {{ updatedLabel }}',
        "{{ $t('teacher.labels.lastUpdated') }} {{ updatedLabel }}",
      )
      .replace(
        "{{ isPublished ? 'إلغاء النشر' : 'نشر' }}",
        "{{ isPublished ? $t('teacher.quizzes.unpublish') : $t('teacher.actions.publish') }}",
      )
      .replace("default: 'مساحة الكويز'", "default: ''")
      .replace(
        "return props.isPublished ? 'منشور' : 'مسودة'",
        "return props.isPublished ? t('teacher.status.published') : t('teacher.status.draft')",
      ),

  'src/components/teacher/profile/TeacherVoiceSampleCard.vue': (c) =>
    c
      .replace(
        'return `${Math.round(props.durationSeconds)} ث`',
        "return `${Math.round(props.durationSeconds)}${t('teacher.voice.secondsShort')}`",
      )
      .replace("props.statusLabel === 'جاهزة'", "props.statusLabel === t('teacher.status.readyF')")
      .replace("props.statusLabel === 'قيد التجهيز'", "props.statusLabel === t('teacher.status.preparing')")
      .replace("props.statusLabel === 'غير متاحة'", "props.statusLabel === t('teacher.status.notAvailable')"),

  'src/components/teacher/PdfUploadBox.vue': (c) =>
    c
      .replace(
        '<h3 class="section-title text-h4 mb-2">اسحب ملف PDF وأفلته هنا</h3>',
        "<h3 class=\"section-title text-h4 mb-2\">{{ $t('teacher.pdf.dragDropPdf') }}</h3>",
      )
      .replace(
        'أو انقر لاختيار ملف — PDF فقط · حتى {{ maxSizeLabel }}',
        "{{ $t('teacher.pdf.orClickChoose', { size: maxSizeLabel }) }}",
      )
      .replace('اختيار ملف PDF', "{{ $t('teacher.pdf.choosePdfFile') }}")
      .replace(
        "if (props.file) return `ملف مرفوع: ${props.file.name}`",
        "if (props.file) return `${t('teacher.pdf.uploadedFile')} ${props.file.name}`",
      )
      .replace(
        "return 'منطقة رفع PDF، اسحب الملف أو انقر للاختيار'",
        "return t('teacher.pdf.uploadZoneAria')",
      ),

  'src/components/teacher/PdfPreviewCard.vue': (c) =>
    c.replace(
      'ارفع ملف PDF لعرض المعاينة',
      "{{ $t('teacher.pdf.uploadForPreview') }}",
    ),

  'src/components/teacher/lessons/TeacherStudentWorkspaceRow.vue': (c) =>
    c
      .replace(
        'الإكمال الموثّق',
        "{{ $t('teacher.lessons.documentedCompletion') }}",
      )
      .replace(
        'آخر نشاط {{ lastActivity }}',
        "{{ $t('teacher.labels.lastActivityAt', { date: lastActivity }) }}",
      )
      .replace("if (!n) return 'ط'", "if (!n) return t('teacher.labels.studentInitial')"),

  'src/components/teacher/lessons/TeacherStudentSummaryPanel.vue': (c) =>
    c
      .replace(
        '🏆 أفضل الطلاب في هذا الصف',
        "{{ $t('teacher.students.topStudents') }}",
      )
      .replace('return `${n} طالب`', "return t('teacher.labels.studentCount', { count: n })")
      .replace(
        "label: expiring === 1 ? 'اشتراك ينتهي قريباً' : `${expiring} اشتراكات تنتهي قريباً`",
        "label: expiring === 1 ? t('teacher.students.subExpiring') : t('teacher.students.subsExpiring')",
      )
      .replace(
        "label: inactive === 1 ? 'طالب غير نشط' : `${inactive} غير نشطين`",
        "label: inactive === 1 ? t('teacher.students.inactiveStudent') : t('teacher.status.inactive')",
      )
      .replace(
        "label: followUp === 1 ? 'طالب بحاجة متابعة' : `${followUp} بحاجة متابعة`",
        "label: followUp === 1 ? t('teacher.students.needsFollowUp') : t('teacher.students.needsFollowUp')",
      ),

  'src/components/teacher/lessons/TeacherStudentPremiumCard.vue': (c) =>
    c
      .replace(
        'آخر نشاط {{ lastActivity }}',
        "{{ $t('teacher.labels.lastActivityAt', { date: lastActivity }) }}",
      )
      .replace("if (!n) return 'ط'", "if (!n) return t('teacher.labels.studentInitial')"),

  'src/components/teacher/lessons/TeacherLessonWorkspaceToolbar.vue': (c) =>
    c
      .replace("default: 'الدروس'", "default: ''")
      .replace('return `${n} دروس`', "return t('teacher.labels.lessonCount', { count: n })"),

  'src/components/teacher/lessons/TeacherLessonPremiumCard.vue': (c) =>
    c
      .replace('title="أدوات AI"', ":title=\"$t('teacher.lessons.aiToolsTitle')\"")
      .replace(
        'آخر تعديل {{ lastUpdated }}',
        "{{ $t('teacher.labels.lastEditAt', { date: lastUpdated }) }}",
      )
      .replace(
        '{{ completion.completed }} من أصل {{ completion.total }} طالب',
        "{{ $t('teacher.lessons.fromOfStudents', { completed: completion.completed, total: completion.total }) }}",
      ),

  'src/components/teacher/lessons/TeacherClassWorkspaceToolbar.vue': (c) =>
    c
      .replace("default: 'الدروس'", "default: ''")
      .replace('return `${n} دروس`', "return t('teacher.labels.lessonCount', { count: n })"),

  'src/components/teacher/lessons/LessonVideoSourcePanel.vue': (c) =>
    c
      .replace(
        'اسحب الفيديو وأفلته هنا',
        "{{ $t('teacher.lessons.dragVideoDrop') }}",
      )
      .replace(
        'الصق رابط YouTube أو Vimeo أو Google Drive أو MP4 مباشر — مثالي لتوليد العنوان والوصف.',
        "{{ $t('teacher.lessons.pasteVideoLink') }}",
      ),

  'src/components/teacher/lessons/LessonSourcePanel.vue': (c) =>
    c
      .replace(
        'اسحب وأفلت هنا',
        "{{ $t('teacher.lessons.dragDropGeneric') }}",
      )
      .replace(
        'YouTube · Vimeo · Google Drive · رابط MP4 مباشر',
        "{{ $t('teacher.lessons.videoLinkFormats') }}",
      )
      .replace(
        'ارفع ملف PDF للدرس — بنفس أهمية الفيديو',
        "{{ $t('teacher.lessons.uploadPdfHint') }}",
      )
      .replace(
        'اسحب PDF وأفلته هنا',
        "{{ $t('teacher.lessons.dragPdfDrop') }}",
      )
      .replace(
        'PDF · حتى {{ maxPdfLabel }}',
        "{{ $t('teacher.lessons.pdfFormats', { size: maxPdfLabel }) }}",
      )
      .replace(
        "{ value: 'video-link', label: 'رابط فيديو', icon: 'mdi-link-variant' }",
        "{ value: 'video-link', label: t('teacher.lessons.videoLinkTab'), icon: 'mdi-link-variant' }",
      )
      .replace(
        "{ value: 'pdf', label: 'رفع PDF', icon: 'mdi-file-pdf-box' }",
        "{ value: 'pdf', label: t('teacher.lessons.uploadPdfTab'), icon: 'mdi-file-pdf-box' }",
      ),

  'src/components/teacher/lessons/LessonAiProcessingCard.vue': (c) =>
    c.replace(
      `const steps = [
  'تحويل المحتوى إلى نص',
  'إنشاء الملخص',
  'إنشاء الكويز',
  'إنشاء الملاحظات',
  'إنشاء البطاقات التعليمية',
]`,
      `const steps = computed(() => [
  t('teacher.processing.toText'),
  t('teacher.processing.summary'),
  t('teacher.processing.quiz'),
  t('teacher.processing.notes'),
  t('teacher.processing.flashcards'),
])`,
    ),

  'src/components/teacher/LessonContentEditorCard.vue': (c) =>
    c
      .replace(
        "{{ hasCurrent && !removed ? 'استبدال' : 'رفع' }}",
        "{{ hasCurrent && !removed ? $t('common.update') : $t('teacher.actions.uploadPdf') }}",
      )
      .replace(
        ':message="`سيتم حذف ${label} عند الحفظ`"',
        ":message=\"$t('teacher.labels.willDeleteOnSave', { type: label })\"",
      )
      .replace(
        'لا يوجد {{ label }} — ارفع ملفاً جديداً',
        "{{ $t('teacher.labels.noTypeUploadNew', { type: label }) }}",
      )
      .replace(
        'if (props.replacementFile) return `استبدال: ${props.replacementFile.name}`',
        "if (props.replacementFile) return t('teacher.labels.replaceFile', { name: props.replacementFile.name })",
      ),

  'src/components/teacher/LessonCard.vue': (c) =>
    c
      .replace(
        '{{ lesson.pages }} صفحة',
        "{{ $t('teacher.labels.pagesCount', { count: lesson.pages }) }}",
      )
      .replace(
        '{{ lesson.students }} طالب',
        "{{ $t('teacher.labels.studentCount', { count: lesson.students }) }}",
      )
      .replace('aria-label="فتح ملف PDF"', ":aria-label=\"$t('teacher.lessons.openPdfAria')\""),

  'src/components/teacher/EditCourseDialog.vue': (c) =>
    c
      .replace(
        'description="اسم الصف ووصف قصير يساعد طلابك على فهم المحتوى"',
        ":description=\"$t('teacher.course.basicDesc')\"",
      )
      .replace(
        'description="حدّد المادة والسعر لهذا الصف"',
        ":description=\"$t('teacher.course.editTeachingDesc')\"",
      )
      .replace(
        'description="اختر متى يصبح الصف متاحاً لطلابك"',
        ":description=\"$t('teacher.course.publishDesc')\"",
      )
      .replace(
        'description="عند التفعيل يظهر الصف للطلاب المشتركين. يمكنك إبقاءه كمسودة والعمل عليه بهدوء."',
        ":description=\"$t('teacher.course.publishHint')\"",
      )
      .replace(
        "return grade ? `الصف ${grade}` : '—'",
        "return grade ? t('teacher.labels.gradeNumber', { grade }) : '—'",
      ),

  'src/components/teacher/dashboard/TeacherOverviewSection.vue': (c) =>
    c.replace(
      'description="ستظهر المقاييس عند إنشاء الصفوف واشتراك الطلاب"',
      ":description=\"$t('teacher.dashboard.metricsHint')\"",
    ),

  'src/components/teacher/dashboard/TeacherDashboardHero.vue': (c) =>
    c
      .replace("default: 'المعلم'", "default: ''")
      .replace(
        "default: 'مساحة عملك — دروسك، صفوفك، وطلابك في مكان واحد'",
        "default: ''",
      )
      .replace("default: 'إدارة الصفوف'", "default: ''")
      .replace("default: 'الرسائل'", "default: ''")
      .replace("return props.name.slice(0, 2) || 'م'", "return props.name.slice(0, 2) || t('teacher.dashboard.teacherInitial')"),

  'src/components/teacher/dashboard/TeacherClassesSection.vue': (c) =>
    c
      .replace(
        '<span class="teacher-class-card__grade">الصف {{ course.grade }}</span>',
        "<span class=\"teacher-class-card__grade\">{{ $t('teacher.labels.gradeNumber', { grade: course.grade }) }}</span>",
      )
      .replace(
        '{{ course.subscribed_students }} طالب',
        "{{ $t('teacher.labels.studentCount', { count: course.subscribed_students }) }}",
      )
      .replace(
        '{{ course.lesson_count }} درس',
        "{{ $t('teacher.labels.lessonCount', { count: course.lesson_count }) }}",
      )
      .replace(
        '{{ course.quiz_count ?? 0 }} كويز',
        "{{ $t('teacher.labels.quizCount', { count: course.quiz_count ?? 0 }) }}",
      ),

  'src/components/teacher/CreateCourseDialog.vue': (c) =>
    c
      .replace('إنشاء الصف', "{{ $t('teacher.course.createClassBtn') }}")
      .replace(
        'grades.value.map((g) => ({ label: `الصف ${g}`, value: g }))',
        "grades.value.map((g) => ({ label: t('teacher.labels.gradeNumber', { grade: g }), value: g }))",
      ),

  'src/components/teacher/classes/TeacherClassWorkspaceCard.vue': (c) =>
    c
      .replace(
        '<span class="teacher-class-workspace__badge">الصف {{ course.grade }}</span>',
        "<span class=\"teacher-class-workspace__badge\">{{ $t('teacher.labels.gradeNumber', { grade: course.grade }) }}</span>",
      )
      .replace(
        "{{ course.is_published ? 'منشور' : 'مسودة' }}",
        "{{ course.is_published ? $t('teacher.status.published') : $t('teacher.status.draft') }}",
      )
      .replace(
        '{{ course.subscribed_students }} طالب',
        "{{ $t('teacher.labels.studentCount', { count: course.subscribed_students }) }}",
      )
      .replace(
        '{{ course.lesson_count }} درس',
        "{{ $t('teacher.labels.lessonCount', { count: course.lesson_count }) }}",
      )
      .replace(
        '{{ course.quiz_count ?? 0 }} كويز',
        "{{ $t('teacher.labels.quizCount', { count: course.quiz_count ?? 0 }) }}",
      )
      .replace("if (!n) return 'م'", "if (!n) return t('teacher.labels.teacherInitial')")
      .replace(
        'return `${n} دروس منشورة`',
        "return t('teacher.labels.lessonsPublished', { count: n })",
      )
      .replace(
        "return `${v.toLocaleString('ar-SY')} ل.س`",
        "return t('teacher.labels.currencySyp', { amount: v.toLocaleString('ar-SY') })",
      ),

  'src/components/teacher/classes/TeacherClassFilters.vue': (c) =>
    c.replace('الصف {{ g }}', "{{ $t('teacher.labels.gradeNumber', { grade: g }) }}"),

  'src/components/teacher/classes/CourseImageUploadCard.vue': (c) =>
    c.replace('PNG أو JPG · WebP', "{{ $t('teacher.course.imageFormats') }}"),

  'src/components/teacher/AddLessonDialog.vue': (c) =>
    c
      .replace(
        '<span class="add-lesson-field-label">عنوان الدرس *</span>',
        "<span class=\"add-lesson-field-label\">{{ $t('teacher.lessons.lessonTitleAsterisk') }}</span>",
      )
      .replace(
        "return generating.value === target ? '✨ جاري التوليد...' : '✨ توليد'",
        "return generating.value === target ? t('teacher.lessons.generating') : t('teacher.lessons.generate')",
      )
      .replace(
        "return generating.value === 'both' ? '✨ جاري التوليد...' : '✨ توليد العنوان والوصف'",
        "return generating.value === 'both' ? t('teacher.lessons.generating') : t('teacher.lessons.generateTitleDesc')",
      )
      .replace(
        "error.value = 'الملف يجب أن يكون PDF'",
        "error.value = t('teacher.lessons.fileMustBePdf')",
      )
      .replace(
        'error.value = `الملف أكبر من ${MAX_PDF_SIZE_LABEL}`',
        "error.value = t('teacher.lessons.fileTooLarge', { size: MAX_PDF_SIZE_LABEL })",
      )
      .replace(
        "error.value = 'ارفع ملف PDF'",
        "error.value = t('teacher.lessons.uploadPdfRequired')",
      )
      .replace(
        "if (pdf || video) showInfo('بدأت معالجة الذكاء الاصطناعي')",
        "if (pdf || video) showInfo(t('teacher.status.processingAi'))",
      ),

  'src/components/teacher/lessons/TeacherStudentPreviewRow.vue': (c) =>
    c
      .replace(
        'return relative ? `آخر نشاط ${relative}` : \'بدون نشاط مسجّل\'',
        "return relative ? t('teacher.studentPreview.lastActivityRelative', { relative }) : t('teacher.studentPreview.noActivity')",
      )
      .replace("if (!n) return 'ط'", "if (!n) return t('teacher.labels.studentInitial')"),

  'src/components/teacher/lessons/TeacherLessonWorkspaceRow.vue': (c) =>
    c.replace('title="أدوات AI"', ":title=\"$t('teacher.lessons.aiToolsTitle')\""),
}

function applyPatches() {
  const migrated = []
  for (const [rel, patch] of Object.entries(filePatches)) {
    const file = path.join(ROOT, rel)
    if (!fs.existsSync(file)) {
      console.warn('missing', rel)
      continue
    }
    const original = fs.readFileSync(file, 'utf8')
    let next = patch(original)
    next = ensureUseI18n(next)
    if (next !== original) {
      fs.writeFileSync(file, next, 'utf8')
      migrated.push(rel)
    }
  }
  return migrated
}

mergeLocales()
const migrated = applyPatches()
console.log('New keys added:', newEntries.length)
console.log('Files patched:', migrated.length)
migrated.forEach((f) => console.log(' -', f))
