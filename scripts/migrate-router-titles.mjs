import fs from 'fs'

const path = 'src/router/index.js'
let s = fs.readFileSync(path, 'utf8')

const replacements = [
  ["title: 'مرحباً بك'", "titleKey: 'routes.welcome'"],
  ["title: 'تسجيل الدخول'", "titleKey: 'routes.login'"],
  ["title: 'إنشاء حساب'", "titleKey: 'routes.register'"],
  ["title: 'نسيت كلمة المرور'", "titleKey: 'routes.forgotPassword'"],
  ["title: 'إعادة تعيين كلمة المرور'", "titleKey: 'routes.resetPassword'"],
  ["title: 'تأكيد البريد الإلكتروني'", "titleKey: 'routes.verifyEmail'"],
  ["title: 'التحقق الثنائي'", "titleKey: 'routes.twoFactor'"],
  ["title: 'التحقق من الشهادة'", "titleKey: 'routes.verifyCertificate'"],
  ["title: 'اختيار الصف'", "titleKey: 'routes.onboardingGrade'"],
  ["title: 'تخصيص تجربتك'", "titleKey: 'routes.onboardingPersonalize'"],
  ["title: 'اختيار المواد'", "titleKey: 'routes.onboardingSubjects'"],
  ["title: 'اختيار المعلمين'", "titleKey: 'routes.onboardingTeachers'"],
  ["title: 'الدفع'", "titleKey: 'routes.studentPayment'"],
  ["title: 'تم الدفع'", "titleKey: 'routes.studentPaymentSuccess'"],
  ["title: 'إعداد المعلم'", "titleKey: 'routes.teacherSetup'"],
  ["title: 'لوحة المعلم'", "titleKey: 'routes.teacherDashboard'"],
  ["title: 'الصفوف'", "titleKey: 'routes.teacherGrades'"],
  ["title: 'تفاصيل الصف'", "titleKey: 'routes.teacherGradeDetail'"],
  ["title: 'الدروس'", "titleKey: 'routes.teacherLessons'"],
  ["title: 'معاينة الدرس'", "titleKey: 'routes.teacherLessonPreview'"],
  ["title: 'تعديل الدرس'", "titleKey: 'routes.teacherLessonEdit'"],
  ["title: 'الطلاب'", "titleKey: 'routes.teacherStudents'"],
  ["title: 'ملف الطالب'", "titleKey: 'routes.teacherStudentProfile'"],
  ["title: 'الكويزات'", "titleKey: 'routes.teacherQuizzes'"],
  ["title: 'منشئ الكويز'", "titleKey: 'routes.teacherQuizBuilder'"],
  ["title: 'نتائج الكويز'", "titleKey: 'routes.teacherQuizResults'"],
  ["title: 'التحليلات'", "titleKey: 'routes.teacherAnalytics'"],
  ["title: 'الرسائل'", "titleKey: 'routes.teacherMessages'"],
  ["title: 'الملف الشخصي'", "titleKey: 'routes.teacherProfile'"],
  ["title: 'رحلتي'", "titleKey: 'routes.studentDashboard'"],
  ["title: 'الدورة'", "titleKey: 'routes.studentCourse'"],
  ["title: 'جلسة التعلّم'", "titleKey: 'routes.studentLesson'"],
  ["title: 'المخطط والالتزام'", "titleKey: 'routes.studentRoutine'"],
  ["title: 'المخطط الذكي'", "titleKey: 'routes.studentPlanner'"],
  ["title: 'إنجازاتي'", "titleKey: 'routes.studentAchievements'"],
  ["title: 'كويز'", "titleKey: 'routes.studentManualQuiz'"],
  ["title: 'الاشتراكات'", "titleKey: 'routes.studentSubscriptions'"],
  ["title: 'اللغات'", "titleKey: 'routes.studentLanguages'"],
  ["title: 'اشتراك اللغات'", "titleKey: 'routes.studentLanguagesSubscribe'"],
  ["title: 'اختبار تحديد المستوى'", "titleKey: 'routes.studentLanguagesPlacement'"],
  ["title: 'القراءة'", "titleKey: 'routes.studentLanguagesReading'"],
  ["title: 'الاستماع'", "titleKey: 'routes.studentLanguagesListening'"],
  ["title: 'التقدّم'", "titleKey: 'routes.studentLanguagesProgress'"],
  ["title: 'المسار التعليمي'", "titleKey: 'routes.studentLanguagesCurriculum'"],
  ["title: 'تمرّن'", "titleKey: 'routes.studentLanguagesPractice'"],
  ["title: 'دروس القواعد'", "titleKey: 'routes.studentLanguagesLessons'"],
  ["title: 'المفردات'", "titleKey: 'routes.studentLanguagesVocabulary'"],
  ["title: 'الكتابة'", "titleKey: 'routes.studentLanguagesWriting'"],
  ["title: 'التحدث'", "titleKey: 'routes.studentLanguagesSpeaking'"],
  ["title: 'سيناريوهات المحادثة'", "titleKey: 'routes.studentLanguagesScenarios'"],
  ["title: 'تفاصيل السيناريو'", "titleKey: 'routes.studentLanguagesScenarioDetail'"],
  ["title: 'محادثة السيناريو'", "titleKey: 'routes.studentLanguagesScenarioSession'"],
  ["title: 'اكتمال السيناريo'", "titleKey: 'routes.studentLanguagesScenarioComplete'"],
  ["title: 'الشهادات'", "titleKey: 'routes.studentLanguagesCertificates'"],
  ["title: 'لوحة المتابعة'", "titleKey: 'routes.parentDashboard'"],
  ["title: 'الأداء الأكاديمي'", "titleKey: 'routes.parentPerformance'"],
  ["title: 'الحضور ووقت الدراسة'", "titleKey: 'routes.parentAttendance'"],
  ["title: 'تقدّم الدروس'", "titleKey: 'routes.parentLessons'"],
  ["title: 'تفاصيل الدرس'", "titleKey: 'routes.parentLessonDetail'"],
  ["title: 'التنبيهات'", "titleKey: 'routes.parentNotifications'"],
  ["title: 'رؤى الذكاء الاصطناعي'", "titleKey: 'routes.parentInsights'"],
  ["title: 'التقارير والتصدير'", "titleKey: 'routes.parentReports'"],
  ["title: 'المواد والأساتذة'", "titleKey: 'routes.parentSubjectsTeachers'"],
  ["title: 'ربط طالب'", "titleKey: 'routes.parentLinkStudent'"],
  ["title: 'إعدادات المسؤول'", "titleKey: 'routes.adminSettings'"],
]

// Settings title appears multiple times — map by order after other unique replacements
for (const [from, to] of replacements) {
  s = s.split(from).join(to)
}

// Remaining settings routes (student, teacher, parent, admin)
s = s.replaceAll("titleKey: 'routes.teacherSettings'", "titleKey: 'routes.teacherSettings'")
const settingsKeys = [
  'routes.teacherSettings',
  'routes.studentSettings',
  'routes.parentSettings',
  'routes.adminSettings',
]
let settingsIdx = 0
s = s.replace(/title: 'الإعدادات'/g, () => {
  const key = settingsKeys[settingsIdx] || 'routes.teacherSettings'
  settingsIdx += 1
  return `titleKey: '${key}'`
})

// Student/parent messages duplicates already replaced to teacherMessages — fix remaining
s = s.replace(/titleKey: 'routes\.teacherMessages'/g, (match, offset) => {
  const before = s.slice(Math.max(0, offset - 200), offset)
  if (before.includes("/student/")) return "titleKey: 'routes.studentMessages'"
  if (before.includes('/parent/')) return "titleKey: 'routes.parentMessages'"
  return match
})

// Routine/planner duplicates for parent vs student
s = s.replace("path: '/parent/student-planner'", "path: '/parent/student-planner'")
// parent routine title was mapped to studentRoutine — fix parent planner path block
s = s.replace(
  /path: '\/parent\/student-planner'[\s\S]*?titleKey: 'routes\.studentRoutine'/,
  (block) => block.replace("titleKey: 'routes.studentRoutine'", "titleKey: 'routes.parentPlanner'"),
)

fs.writeFileSync(path, s)
console.log('Router titles migrated')
