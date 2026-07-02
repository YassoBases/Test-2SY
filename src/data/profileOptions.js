/** Academic subject interests — learning preferences for the AI tutor. */
export const interestOptions = [
  { title: 'رياضيات', value: 'math', icon: 'mdi-calculator' },
  { title: 'علوم', value: 'science', icon: 'mdi-flask' },
  { title: 'برمجة', value: 'programming', icon: 'mdi-code-tags' },
  { title: 'اللغة العربية', value: 'arabic', icon: 'mdi-book-open-variant' },
  { title: 'الإنجليزية', value: 'english', icon: 'mdi-translate' },
  { title: 'فيزياء', value: 'physics', icon: 'mdi-atom' },
  { title: 'كيمياء', value: 'chemistry', icon: 'mdi-test-tube' },
  { title: 'تاريخ', value: 'history', icon: 'mdi-earth' },
]

/** Personal hobbies — used for examples and analogies in lesson chat. */
export const hobbyOptions = [
  { title: 'سيارات', value: 'cars', icon: 'mdi-car-sports' },
  { title: 'كرة قدم', value: 'football', icon: 'mdi-soccer' },
  { title: 'ألعاب', value: 'gaming', icon: 'mdi-gamepad-variant' },
  { title: 'رسم', value: 'drawing', icon: 'mdi-palette' },
  { title: 'موسيقى', value: 'music', icon: 'mdi-music' },
  { title: 'روبوتات', value: 'robotics', icon: 'mdi-robot' },
  { title: 'طيران', value: 'aviation', icon: 'mdi-airplane' },
  { title: 'أعمال', value: 'business', icon: 'mdi-briefcase' },
  { title: 'ذكاء اصطناعي', value: 'ai', icon: 'mdi-brain' },
]

export const learningStyleOptions = [
  { value: 'visual', title: 'بصري', description: 'شرح وصفي وتصوّري', icon: 'mdi-eye' },
  { value: 'practical', title: 'عملي', description: 'ربط بالحياة اليومية', icon: 'mdi-handshake' },
  { value: 'theoretical', title: 'نظري', description: 'تركيز على المفاهيم', icon: 'mdi-brain' },
  { value: 'step_by_step', title: 'خطوة بخطوة', description: 'تقسيم مرقّم واضح', icon: 'mdi-format-list-numbered' },
]

export const futureGoalOptions = [
  { value: 'engineer', title: 'مهندس', icon: 'mdi-tools' },
  { value: 'doctor', title: 'طبيب', icon: 'mdi-stethoscope' },
  { value: 'programmer', title: 'مبرمج', icon: 'mdi-code-braces' },
  { value: 'entrepreneur', title: 'رائد أعمال', icon: 'mdi-storefront' },
  { value: 'scientist', title: 'عالم', icon: 'mdi-flask-round-bottom' },
  { value: 'teacher', title: 'معلّم', icon: 'mdi-school' },
  { value: 'undecided', title: 'لم أحدد بعد', icon: 'mdi-help-circle' },
]

export const preferredExplanationStyleOptions = [
  { value: 'short', title: 'مختصر', description: 'إجابات قصيرة ومركّزة', icon: 'mdi-format-quote-close' },
  { value: 'normal', title: 'متوسط', description: 'توازن بين الإيجاز والتفصيل', icon: 'mdi-format-quote-open' },
  { value: 'detailed', title: 'مفصّل', description: 'شرح أعمق عند الحاجة', icon: 'mdi-format-list-bulleted' },
]

export const personalityModeOptions = [
  { value: 'friendly_teacher', title: 'معلم ودود', description: 'دافئ ومشجّع', icon: 'mdi-emoticon-happy-outline' },
  { value: 'strict_teacher', title: 'معلم صارم', description: 'مباشر ومركّز على الدقة', icon: 'mdi-gavel' },
  { value: 'coach', title: 'مدرب تحفيزي', description: 'محفّز وخطوة بخطوة', icon: 'mdi-whistle' },
  { value: 'mentor', title: 'مرشد', description: 'هادئ وعميق', icon: 'mdi-compass-outline' },
  { value: 'exam_prep', title: 'تحضير امتحانات', description: 'تركيز على ما يهم بالاختبار', icon: 'mdi-clipboard-text-outline' },
  { value: 'kid_friendly', title: 'مبسّط للأطفال', description: 'مفردات بسيطة وجمل قصيرة', icon: 'mdi-emoticon-outline' },
]

export const difficultyLevels = [
  {
    value: 'easy',
    title: 'سهل',
    description: 'شرح بطيء مع أمثلة كثيرة',
    icon: 'mdi-speedometer-slow',
  },
  {
    value: 'medium',
    title: 'متوسط',
    description: 'توازن بين التفصيل والسرعة',
    icon: 'mdi-speedometer-medium',
  },
  {
    value: 'hard',
    title: 'متقدم',
    description: 'تحديات إضافية ومفاهيم أعمق',
    icon: 'mdi-speedometer',
  },
]

export const defaultProfilePrefs = {
  interests: ['math', 'science'],
  hobbies: [],
  difficulty: 'medium',
  age: null,
  learning_style: 'theoretical',
  future_goal: 'undecided',
  preferred_explanation_style: 'normal',
  personality_mode: 'friendly_teacher',
}

export function labelForOption(options, value) {
  return options.find((o) => o.value === value)?.title ?? value
}

/** UI-5.0 — student identity hub copy */
export const futureGoalIdentityOptions = [
  { value: 'programmer', title: 'أريد أن أصبح مهندس برمجيات', icon: 'mdi-code-braces' },
  { value: 'doctor', title: 'أريد دراسة الطب', icon: 'mdi-stethoscope' },
  { value: 'engineer', title: 'أريد أن أصبح مهندساً', icon: 'mdi-tools' },
  { value: 'scientist', title: 'أريد أن أتفوق في العلوم', icon: 'mdi-flask-round-bottom' },
  { value: 'teacher', title: 'أريد أن أصبح معلّماً', icon: 'mdi-school' },
  { value: 'entrepreneur', title: 'أريد بناء مشروعي الخاص', icon: 'mdi-storefront' },
  { value: 'undecided', title: 'ما زلت أستكشف اهتماماتي', icon: 'mdi-compass-outline' },
]

export const explanationIdentityOptions = [
  { value: 'short', title: 'أحب الشرح السريع', emoji: '⚡', icon: 'mdi-lightning-bolt' },
  { value: 'normal', title: 'شرح متوازن', emoji: '⚖️', icon: 'mdi-scale-balance' },
  { value: 'detailed', title: 'أحب الشرح التفصيلي', emoji: '📚', icon: 'mdi-book-open-variant' },
]

export const learningStyleIdentityOptions = [
  { value: 'visual', title: 'أحب الأمثلة والصور', emoji: '🖼️', icon: 'mdi-eye' },
  { value: 'practical', title: 'أربط الدرس بحياتي', emoji: '🌍', icon: 'mdi-handshake' },
  { value: 'theoretical', title: 'أفهم المفاهيم أولاً', emoji: '🧠', icon: 'mdi-brain' },
  { value: 'step_by_step', title: 'خطوة بخطوة', emoji: '📝', icon: 'mdi-format-list-numbered' },
]

export const personalityIdentityOptions = [
  { value: 'friendly_teacher', title: 'معلّم ودود', emoji: '😊', icon: 'mdi-emoticon-happy-outline' },
  { value: 'coach', title: 'مدرب يشجّعني', emoji: '💪', icon: 'mdi-whistle' },
  { value: 'mentor', title: 'أفضل أسلوب المرشد', emoji: '🤝', icon: 'mdi-compass-outline' },
  { value: 'strict_teacher', title: 'مباشر ودقيق', emoji: '🎯', icon: 'mdi-gavel' },
  { value: 'exam_prep', title: 'يركّز على الاختبار', emoji: '📋', icon: 'mdi-clipboard-text-outline' },
  { value: 'kid_friendly', title: 'شرح مبسّط', emoji: '✨', icon: 'mdi-emoticon-outline' },
]

export const difficultyIdentityOptions = [
  { value: 'easy', title: 'أحب الشرح الهادئ', description: 'بطيء مع أمثلة كثيرة', icon: 'mdi-speedometer-slow' },
  { value: 'medium', title: 'مستوى متوازن', description: 'لا بطيء ولا صعب جداً', icon: 'mdi-speedometer-medium' },
  { value: 'hard', title: 'أحب التحدي', description: 'مفاهيم أعمق وأسئلة أصعب', icon: 'mdi-speedometer' },
]

export const ageBandOptions = [
  { value: 12, label: '10–13 سنة', min: 10, max: 13 },
  { value: 15, label: '14–17 سنة', min: 14, max: 17 },
  { value: 19, label: '18+ سنة', min: 18, max: 25 },
]

export function ageBandLabel(age) {
  if (age == null || age === '') return null
  const n = Number(age)
  if (Number.isNaN(n)) return null
  if (n >= 18) return '18+ سنة'
  if (n >= 14) return '14–17 سنة'
  if (n >= 10) return '10–13 سنة'
  if (n >= 5) return 'أقل من 10 سنوات'
  return null
}

export function goalIdentityTitle(value) {
  return futureGoalIdentityOptions.find((o) => o.value === value)?.title
    ?? labelForOption(futureGoalOptions, value)
}
