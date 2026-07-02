/** Backend API activity keys and Arabic lexicon for schedule parsing (not UI copy). */
export const ROUTINE_ACTIVITIES = ['رياضة', 'دروس خاصة', 'نشاط ديني', 'موسيقى', 'لغات']

export const ROUTINE_ACTIVITY_ICONS = {
  'رياضة': 'mdi-basketball',
  'دروس خاصة': 'mdi-account-school-outline',
  'نشاط ديني': 'mdi-mosque',
  'موسيقى': 'mdi-music-note-outline',
  'لغات': 'mdi-translate',
}

export const ROUTINE_ACTIVITY_LABEL_KEYS = {
  'رياضة': 'sport',
  'دروس خاصة': 'tutoring',
  'نشاط ديني': 'religious',
  'موسيقى': 'music',
  'لغات': 'languages',
}

export const ROUTINE_TUTORING_ACTIVITY = 'دروس خاصة'
export const ROUTINE_DAY_TYPE_SCHOOL = 'مدرسة'
export const ROUTINE_DAY_TYPE_WEEKEND = 'عطلة'

export const ROUTINE_ACTIVITY_ICON_GROUPS = [
  { keys: ['مدرس'], icon: 'mdi-school-outline', color: 'blue' },
  { keys: ['درس', 'مذاكر', 'واجب', 'حفظ', 'مراجع'], icon: 'mdi-book-open-page-variant-outline', color: 'purple' },
  { keys: ['نوم', 'نام', 'ينام'], icon: 'mdi-power-sleep', color: 'indigo' },
  { keys: ['أكل', 'غدا', 'فطور', 'عشا', 'طعام', 'وجبة'], icon: 'mdi-food-outline', color: 'orange' },
  { keys: ['رياض', 'جري', 'تمرين', 'ملعب'], icon: 'mdi-run', color: 'green' },
  { keys: ['صلا'], icon: 'mdi-hands-pray', color: 'teal' },
  { keys: ['لعب', 'تلفزيون', 'جوال', 'موبايل', 'ترفيه', 'يوتيوب'], icon: 'mdi-gamepad-variant-outline', color: 'pink' },
  { keys: ['عائل', 'أهل', 'عيلة', 'بيت'], icon: 'mdi-home-heart-outline', color: 'deep-purple' },
  { keys: ['استحم', 'دش', 'نظاف'], icon: 'mdi-shower', color: 'cyan' },
]

export const ROUTINE_TIME_SLOT_RE = /(الساعة\s*\d{1,2}(?::\d{2})?(?:\s*(?:صباحاً|صباحا|مساءً|مساء|ظهراً|ظهرا|عصراً|عصرا))?|\b\d{1,2}:\d{2}\b)([^.،؛\n]{0,22})/g

export const ROUTINE_QUESTION_KEYWORDS = ['هل ', 'شو ', 'متى ', 'كيف ', 'قديه ', 'وين ', 'قلي ', 'ساعدني']

export const ROUTINE_TIME_HOUR_PREFIX = 'الساعة'
export const ROUTINE_QUESTION_MARKER_LINE = '[سؤال]'
export const ROUTINE_QUESTION_PREFIX = 'سؤال'
export const ROUTINE_QUESTION_MARK = '؟'
