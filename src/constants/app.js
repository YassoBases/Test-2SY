export const MIN_ACADEMIC_GRADE = 1
export const MAX_ACADEMIC_GRADE = 12
export const ACADEMIC_GRADES = Array.from(
  { length: MAX_ACADEMIC_GRADE - MIN_ACADEMIC_GRADE + 1 },
  (_, i) => MIN_ACADEMIC_GRADE + i,
)

export const GRADE_LABELS = {
  1: 'الصف الأول',
  2: 'الصف الثاني',
  3: 'الصف الثالث',
  4: 'الصف الرابع',
  5: 'الصف الخامس',
  6: 'الصف السادس',
  7: 'الصف السابع',
  8: 'الصف الثامن',
  9: 'الصف التاسع',
  10: 'الصف العاشر',
  11: 'الصف الحادي عشر',
  12: 'الصف الثاني عشر',
}

export function gradeLabel(grade) {
  return GRADE_LABELS[grade] || `الصف ${grade}`
}

export const MAX_PDF_SIZE_BYTES = 500 * 1024 * 1024
export const MAX_PDF_SIZE_LABEL = '500 MB'
export const VOICE_SAMPLE_MIN_SECONDS = 60
/** @deprecated use VOICE_SAMPLE_MIN_SECONDS */
export const VOICE_SAMPLE_SECONDS = VOICE_SAMPLE_MIN_SECONDS
export const ACCEPTED_PDF_TYPES = ['application/pdf']

export const ROUTES = {
  WELCOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  FORGOT_PASSWORD: '/forgot-password',
  RESET_PASSWORD: '/reset-password',
  VERIFY_EMAIL: '/verify-email',
  LOGIN_VERIFY_2FA: '/login/verify-2fa',
  PARENT_REGISTER: '/register/parent',
  TEACHER_DASHBOARD: '/teacher/dashboard',
  TEACHER_STUDENTS: '/teacher/students',
  TEACHER_STUDENT_PROFILE: (id) => `/teacher/students/${id}`,
  /** @deprecated use TEACHER_GRADES — upload lives inside class management */
  TEACHER_UPLOAD: '/teacher/grades',
  TEACHER_GRADES: '/teacher/grades',
  /** Primary student hub — course list (My courses) */
  STUDENT_COURSES: '/student/dashboard#courses',
  TEACHER_LESSONS: '/teacher/lessons',
  /** @deprecated alias — use STUDENT_COURSES */
  STUDENT_DASHBOARD: '/student/dashboard#courses',
  STUDENT_COURSE: (id) => `/student/course/${id}`,
  STUDENT_COURSE_QUIZZES: (id) => `/student/course/${id}?tab=quizzes`,
  STUDENT_ROUTINE: '/student/routine',
  STUDENT_PLANNER: '/student/planner',
  STUDENT_ACHIEVEMENTS: '/student/achievements',
  STUDENT_PROFILE: '/student/profile',
  STUDENT_LESSON: (id = '1') => `/student/lesson/${id}`,
  STUDENT_MANUAL_QUIZ: (quizId, courseId) =>
    `/student/manual-quiz/${quizId}${courseId != null ? `?courseId=${courseId}` : ''}`,
  PARENT_DASHBOARD: '/parent/dashboard',
  PARENT_PERFORMANCE: '/parent/student-performance',
  PARENT_ATTENDANCE: '/parent/student-attendance',
  PARENT_LESSONS: '/parent/student-lessons',
  PARENT_LESSON_DETAIL: (id) => `/parent/student-lessons/${id}`,
  PARENT_PLANNER: '/parent/student-planner',
  PARENT_NOTIFICATIONS: '/parent/student-notifications',
  PARENT_INSIGHTS: '/parent/student-insights',
  PARENT_REPORTS: '/parent/student-reports',
  PARENT_SUBJECTS_TEACHERS: '/parent/subjects-teachers',
  PARENT_LINK: '/parent/link',
  ONBOARDING_GRADE: '/student/onboarding/grade',
  ONBOARDING_PERSONALIZE: '/student/onboarding/personalize',
  ONBOARDING_SUBJECTS: '/student/onboarding/subjects',
  ONBOARDING_TEACHERS: '/student/onboarding/teachers',
  STUDENT_PAYMENT: '/student/payment',
  STUDENT_PAYMENT_SUCCESS: '/student/payment/success',
  STUDENT_SUBSCRIPTIONS: '/student/subscriptions',
  STUDENT_LANGUAGES: '/student/languages',
  STUDENT_LANGUAGES_READING: '/student/languages/reading',
  STUDENT_LANGUAGES_LISTENING: '/student/languages/listening',
  STUDENT_LANGUAGES_PROGRESS: '/student/languages/progress',
  STUDENT_LANGUAGES_VOCABULARY: '/student/languages/vocabulary',
  STUDENT_LANGUAGES_DICTIONARY: '/student/languages/dictionary',
  STUDENT_LANGUAGES_WRITING: '/student/languages/writing',
  STUDENT_LANGUAGES_SPEAKING: '/student/languages/speaking',
  STUDENT_LANGUAGES_CURRICULUM: '/student/languages/curriculum',
  STUDENT_LANGUAGES_LESSONS: '/student/languages/lessons',
  STUDENT_LANGUAGES_CERTIFICATES: '/student/languages/certificates',
  STUDENT_LANGUAGES_HISTORY: '/student/languages/history',
  STUDENT_LANGUAGES_INSIGHTS: '/student/languages/insights',
  STUDENT_LANGUAGES_EXAM: '/student/languages/exam',
  STUDENT_LANGUAGES_PLACEMENT: '/student/languages/placement',
  STUDENT_LANGUAGES_PLACEMENT_HISTORY: '/student/languages/placement-history',
  STUDENT_LANGUAGES_SUBSCRIBE: '/student/languages/subscribe',
  VERIFY_CERTIFICATE: (number) => `/verify-certificate/${number}`,
  TEACHER_SETUP: '/teacher/setup',
  TEACHER_PROFILE: '/teacher/profile',
  TEACHER_MESSAGES: '/teacher/messages',
  STUDENT_MESSAGES: '/student/messages',
  PARENT_MESSAGES: '/parent/messages',
  STUDENT_SETTINGS: '/student/settings',
  TEACHER_SETTINGS: '/teacher/settings',
  PARENT_SETTINGS: '/parent/settings',
  ADMIN_SETTINGS: '/admin/settings',
}

/** Settings path for the signed-in primary role. */
export function settingsRouteForRole(role) {
  const map = {
    student: ROUTES.STUDENT_SETTINGS,
    teacher: ROUTES.TEACHER_SETTINGS,
    parent: ROUTES.PARENT_SETTINGS,
    admin: ROUTES.ADMIN_SETTINGS,
  }
  return map[role] || ROUTES.STUDENT_SETTINGS
}

export const LESSON_STATUS = {
  PROCESSED: 'processed',
  PROCESSING: 'processing',
  DRAFT: 'draft',
  ERROR: 'error',
}
