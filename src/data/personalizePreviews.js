/** ONBOARDING-4.1 — Static preview snippets for personalization choices (no AI). */

export const goalPreviews = {
  programmer: 'مثلاً: «اليوم رح نتعلّم فكرة بتساعدك بمشاريع البرمجة لاحقاً...»',
  doctor: 'مثلاً: «هالمفهوم مهم إذا حابب تدرس طب يوماً ما...»',
  engineer: 'مثلاً: «رح نربط الدرس بأمثلة هندسية من الحياة...»',
  scientist: 'مثلاً: «خلينا نكتشف ليش هالظاهرة بتصير بالعلوم...»',
  teacher: 'مثلاً: «رح أشرحلك بطريقة تقدر تعيدها لغيرك بسهولة...»',
  entrepreneur: 'مثلاً: «شوف كيف هالفكرة ممكن تتحول لمشروع صغير...»',
  undecided: 'مثلاً: «ما في مشكلة — رح نكتشف مع بعض شو بيعجبك...»',
}

export const learningStylePreviews = {
  visual: 'مثلاً: «تخيّل معي شكل المثلث... هيك بصير أوضح...»',
  practical: 'مثلاً: «مثل لما بتشتري من المحل — نفس الفكرة هون...»',
  theoretical: 'مثلاً: «أول شي نفهم القاعدة، بعدين نطبّقها...»',
  step_by_step: 'مثلاً: «لنبدأ من الأساس ثم ننتقل إلى الجزء التالي...»',
}

export const difficultyPreviews = {
  easy: 'مثلاً: «خلينا نمشي بخطوات هادية مع أمثلة كتيرة...»',
  medium: 'مثلاً: «رح نوازن بين الشرح والأسئلة — لا بطيء ولا سريع...»',
  hard: 'مثلاً: «جاهز؟ رح ندخل بتفاصيل أعمق وتحديات إضافية...»',
}

export const explanationPreviews = {
  short: 'مثلاً: «باختصار، الفكرة الأساسية هي...»',
  normal: 'مثلاً: «الفكرة هي كذا، وهاي التفاصيل المهمة...»',
  detailed: 'مثلاً: «خلينا نشرح كل جزء بالتفصيل حتى يصير واضح...»',
}

export const personalityPreviews = {
  friendly_teacher: 'مثلاً: «أحسنت! يلّا نكمل — أنت قادر...»',
  coach: 'مثلاً: «خطوة خطوة — أنت عم تتقدّم، كمّل!»',
  mentor: 'مثلاً: «فكّر معي: ليش هالقاعدة مهمة؟»',
  strict_teacher: 'مثلاً: «انتبه للتفاصيل — هون الفرق الأساسي...»',
  exam_prep: 'مثلاً: «هاي النقطة كتير بتيجي بالامتحان — ركّز عليها...»',
  kid_friendly: 'مثلاً: «تخيّل معي قصة بسيطة... هيك بصير أسهل...»',
}

export const agePreviews = {
  12: 'مثلاً: «رح أستخدم كلمات بسيطة وأمثلة قريبة من عمرك...»',
  15: 'مثلاً: «رح أشرح بأسلوب يناسب مرحلتك الدراسية...»',
  19: 'مثلاً: «رح ندخل بالتفاصيل بشكل أوضح وأعمق...»',
}

export const interestsPreviewDefault =
  'مثلاً: «تخيّل إن هالمسألة مرتبطة بـ{topic} — هيك بتصير أوضح...»'

export function buildInterestsPreview(interests, hobbies, labelFor) {
  const topics = [...(interests || []), ...(hobbies || [])]
    .map(labelFor)
    .filter(Boolean)
    .slice(0, 2)

  if (!topics.length) return null
  if (topics.length === 1) {
    return interestsPreviewDefault.replace('{topic}', topics[0])
  }
  return `مثلاً: «تخيّل هالدرس مرتبط بـ${topics[0]} و${topics[1]} — هيك بتتذكّره أسهل...»`
}
