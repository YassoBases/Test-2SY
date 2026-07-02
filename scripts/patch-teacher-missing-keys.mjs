import fs from 'fs'
import path from 'path'

const ROOT = path.resolve(import.meta.dirname, '..')

/** @type {Record<string, Record<string, [string, string]>>} */
const MISSING = {
  course: {
    createClassBtn: ['Create class', 'إنشاء الصف'],
    imageFormats: ['JPG, PNG, or WebP — up to 5 MB', 'JPG أو PNG أو WebP — حتى 5 ميجابايت'],
  },
  cv: {
    sectionsNav: ['Profile sections', 'أقسام الملف'],
  },
  dashboard: {
    teacherInitial: ['T', 'م'],
  },
  errors: {
    serverNoQuizId: ['Server response missing quiz ID', 'استجابة الخادم لا تحتوي على معرّف الكويز'],
  },
  grades: {
    oneActiveClass: ['One active class', 'صف واحد نشط'],
    activeClassesCount: ['{count} active classes', '{count} صفوف نشطة'],
    activeOfTotal: ['{active} of {total} classes', '{active} من {total} صفوف'],
    subjectCourseDesc: ['{subject} — Grade {grade}', '{subject} — الصف {grade}'],
  },
  labels: {
    averageValue: ['Average {value}', 'متوسط {value}'],
    choicesCount: ['{count} choices', '{count} خيارات'],
    currencySyp: ['{amount} SYP', '{amount} ل.س'],
    dayCount: ['{count} days', '{count} يوم'],
    documentTitleAsterisk: ['Document title *', 'عنوان المستند *'],
    durationShort: ['{n} min', '{n} د'],
    essayCount: ['{count} essay', '{count} مقالي'],
    falseLabel: ['False', 'خطأ'],
    trueLabel: ['True', 'صح'],
    gradeNumber: ['Grade {grade}', 'الصف {grade}'],
    institutionSchool: ['Institution / school', 'المؤسسة / المدرسة'],
    lastActivityAt: ['Last activity: {date}', 'آخر نشاط: {date}'],
    lastEditAt: ['Last edit: {date}', 'آخر تعديل: {date}'],
    lessonCount: ['{count} lessons', '{count} دروس'],
    lessonsPublished: ['{count} lessons published', '{count} دروس منشورة'],
    minutesCount: ['{count} min', '{count} دقيقة'],
    noTypeUploadNew: ['No {type} — upload a new file', 'لا يوجد {type} — ارفع ملفاً جديداً'],
    optionNumber: ['Option {n}', 'خيار {n}'],
    optionTextNumber: ['Option {n} text', 'نص الخيار {n}'],
    orgInstitution: ['Organization / institution', 'الجهة / المؤسسة'],
    pagesCount: ['{count} pages', '{count} صفحة'],
    pointsCount: ['{count} points', '{count} نقطة'],
    questionCount: ['{count} questions', '{count} أسئلة'],
    quizCount: ['{count} quizzes', '{count} كويز'],
    replaceFile: ['Replace: {name}', 'استبدال: {name}'],
    studentCount: ['{count} students', '{count} طالب'],
    studentInitial: ['S', 'ط'],
    subjectGradeDash: ['{subject} — Grade {grade}', '{subject} — الصف {grade}'],
    teacherInitial: ['T', 'م'],
    titleAsterisk: ['Title *', 'العنوان *'],
    willDeleteOnSave: ['{type} will be deleted on save', 'سيتم حذف {type} عند الحفظ'],
    homework: ['Homework', 'واجب'],
    composite: ['Composite', 'متكامل'],
    lessonDefault: ['Lesson', 'درس'],
    statusError: ['Error', 'يوجد خطأ'],
  },
  lessons: {
    aiToolsTitle: ['AI tools', 'أدوات الذكاء الاصطناعي'],
    defaultToolbarTitle: ['Lessons', 'الدروس'],
    dragDropGeneric: ['Drag and drop here', 'اسحب وأفلته هنا'],
    dragPdfDrop: ['Drag PDF file', 'اسحب ملف PDF'],
    dragVideoDrop: ['Drag video file or choose from device', 'اسحب ملف الفيديو أو اختره من جهازك'],
    fileMustBePdf: ['File must be PDF', 'الملف يجب أن يكون PDF'],
    fromOfStudents: ['{completed} of {total} students', '{completed} من {total} طالب'],
    generate: ['Generate', 'توليد'],
    generateTitleDesc: ['Generate title & description', 'توليد العنوان والوصف'],
    generating: ['Generating…', 'جاري التوليد...'],
    lessonTitleAsterisk: ['Lesson title *', 'عنوان الدرس *'],
    noPdf: ['No PDF', 'لا يوجد PDF'],
    openPdfAria: ['Open PDF', 'فتح PDF'],
    pasteVideoLink: ['Paste video link', 'الصق رابط الفيديو'],
    pdfFormats: ['PDF only — up to {size}', 'PDF فقط — حتى {size}'],
    uploadPdfHint: ['PDF is used for AI processing and student review', 'يُستخدم PDF للمعالجة الذكية ومراجعة الطالب'],
    uploadPdfRequired: ['Upload a PDF file', 'ارفع ملف PDF'],
    uploadPdfTab: ['Upload PDF', 'رفع PDF'],
    videoLinkFormats: ['YouTube, Vimeo, or direct link', 'يوتيوب، فيمو، أو رابط مباشر'],
    videoLinkTab: ['Video link', 'رابط فيديو'],
  },
  parentNotes: {
    editNoteTitle: ['Edit note', 'تعديل الملاحظة'],
  },
  pdf: {
    choosePdfFile: ['Choose PDF file', 'اختر ملف PDF'],
    dragDropPdf: ['Upload PDF', 'رفع PDF'],
    orClickChoose: ['or click to choose — up to {size}', 'أو انقر للاختيار — حتى {size}'],
    uploadForPreview: ['Upload a PDF to show preview', 'ارفع PDF لعرض المعاينة'],
    uploadZoneAria: ['PDF upload zone', 'منطقة رفع PDF'],
  },
  profileEntry: {
    addTitle: ['Add', 'إضافة'],
    editTitle: ['Edit', 'تعديل'],
  },
  quizzes: {
    attemptsCompleted: ['{completed} of {total} completed attempts', '{completed} من {total} محاولة مكتملة'],
    attemptsTotal: ['{count} attempts', '{count} محاولة'],
    deleteConfirmTitle: ['Delete quiz «{title}»?', 'حذف الكويز «{title}»؟'],
    enrolledPercent: ['{percent}% of enrolled', '{percent}% من المسجّلين'],
    highestResult: ['Highest result', 'أعلى نتيجة'],
    lastUpdatedAt: ['Last updated: {date}', 'آخر تحديث: {date}'],
    nAttempts: ['{count} attempts', '{count} محاولة'],
    nQuizzes: ['{count} quizzes', '{count} كويز'],
    oneQuiz: ['One quiz', 'كويز واحد'],
    passingPercent: ['Passing {percent}%', 'النجاح {percent}%'],
    questionDetail: ['Question {n} — {type} · {points} pts', 'سؤال {n} — {type} · {points} نقطة'],
    questionIndex: ['Question {index}', 'سؤال {index}'],
    questionsPointsSummary: ['{questions} questions · {points} points', '{questions} سؤال · {points} نقطة'],
    totalScoreAttempts: ['Total quiz score: {points} · {count} attempts', 'إجمالي درجات الكويز: {points} · {count} محاولة'],
    twoQuizzes: ['Two quizzes', 'كويزان'],
    unpublish: ['Unpublish', 'إلغاء النشر'],
    zeroQuizzes: ['No quizzes', 'لا كويزات'],
    types: {
      multiple_choice: ['Multiple choice', 'اختيار من متعدد'],
      true_false: ['True / false', 'صح / خطأ'],
      short_answer: ['Short answer', 'إجابة قصيرة'],
      essay: ['Essay (manual grading)', 'مقالي (تصحيح يدوي)'],
    },
  },
  studentPreview: {
    lastActivityRelative: ['Last activity {relative}', 'آخر نشاط {relative}'],
    noActivity: ['No activity', 'بدون نشاط'],
  },
  students: {
    avgScoreLabel: ['Average score', 'متوسط النتيجة'],
    editNoteTitle: ['Edit note', 'تعديل الملاحظة'],
    subjectGradeCaption: ['{subject} — Grade {grade}', '{subject} — الصف {grade}'],
    needsFollowUp: ['Need follow-up', 'بحاجة متابعة'],
  },
  voice: {
    deleteConfirmQuestion: ['Delete {name}?', 'هل تريد حذف {name}؟'],
    maxSamplesShort: ['Max {max} samples', 'الحد الأقصى {max} عينات'],
    replaceTarget: ['Replace {name}', 'استبدال {name}'],
    samplesCountShort: ['{count} / {max} samples', '{count} / {max} عينة'],
    subjectsForGrade: ['Subjects for {grade}', 'مواد {grade}'],
  },
}

function mergeMissing(target, source) {
  for (const [section, keys] of Object.entries(source)) {
    target[section] ??= {}
    for (const [key, pair] of Object.entries(keys)) {
      if (Array.isArray(pair)) {
        if (target[section][key] === undefined) target[section][key] = pair[0]
      } else {
        target[section][key] ??= {}
        mergeMissing({ [section]: target[section][key] }, { [key]: pair })
      }
    }
  }
}

function mergeMissingAr(target, source) {
  for (const [section, keys] of Object.entries(source)) {
    target[section] ??= {}
    for (const [key, pair] of Object.entries(keys)) {
      if (Array.isArray(pair)) {
        if (target[section][key] === undefined) target[section][key] = pair[1]
      } else {
        target[section][key] ??= {}
        mergeMissingAr({ [section]: target[section][key] }, { [key]: pair })
      }
    }
  }
}

for (const locale of ['en', 'ar']) {
  const file = path.join(ROOT, 'src/locales', locale, 'teacher.json')
  const data = JSON.parse(fs.readFileSync(file, 'utf8'))
  if (locale === 'en') mergeMissing(data, MISSING)
  else mergeMissingAr(data, MISSING)
  fs.writeFileSync(file, JSON.stringify(data, null, 2) + '\n', 'utf8')
}

console.log('Patched missing teacher.json keys')
