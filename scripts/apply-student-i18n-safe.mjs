/**
 * Safe exact-string i18n patches for student Vue files.
 * Only replaces full exact matches — no substring corruption.
 */
import { readFileSync, writeFileSync, readdirSync, statSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = join(dirname(fileURLToPath(import.meta.url)), '..')

/** @type {Record<string, Array<[string, string]>>} */
const FILE_PATCHES = {
  'src/components/student/home/MySubjectsSection.vue': [
    ['eyebrow="بوابتك التعليمية"', ':eyebrow="t(\'student.home.subjects.eyebrow\')"'],
    ['title="موادك"', ':title="t(\'student.home.subjects.title\')"'],
    ['subtitle="كل مادة مع معلمها — اختر وتابع"', ':subtitle="t(\'student.home.subjects.subtitle\')"'],
    [':description="grade ? \'لا توجد مواد لصفك حالياً.\' : \'حدّد صفك لعرض المواد.\'"', ':description="grade ? t(\'student.home.subjects.empty.noCourses\') : t(\'student.home.subjects.empty.noGrade\')"'],
    [':action-label="grade ? \'الاشتراكات\' : \'تحديد الصف\'"', ':action-label="grade ? t(\'student.home.subjects.empty.subscriptions\') : t(\'student.home.subjects.empty.setGrade\')"'],
  ],
  'src/components/student/home/ContinueLearningSection.vue': [
    ['title="تابع من حيث توقفت"', ':title="t(\'student.home.continue.title\')"'],
    ['subtitle="روابط سريعة"', ':subtitle="t(\'student.home.continue.subtitle\')"'],
    ['title="لا يوجد نشاط بعد"', ':title="t(\'student.home.continue.empty.title\')"'],
    ['description="اشترك في مادة أو ابدأ أول درس ليظهر هنا."', ':description="t(\'student.home.continue.empty.description\')"'],
    ['action-label="الاشتراكات"', ':action-label="t(\'student.home.continue.empty.action\')"'],
  ],
  'src/components/student/home/HomeAchievementsSection.vue': [
    ['title="الإنجازات"', ':title="t(\'student.home.achievements.title\')"'],
    ['subtitle="لحظة صغيرة للاحتفال بخطوتك التالية"', ':subtitle="t(\'student.home.achievements.subtitle\')"'],
    ['<p class="achievement-card__label">آخر إنجاز</p>', '<p class="achievement-card__label">{{ t(\'student.home.achievements.recent.label\') }}</p>'],
    ['<div class="achievement-card__title">ابدأ التعلّم لفتح شارتك الأولى</div>', '<div class="achievement-card__title">{{ t(\'student.home.achievements.recent.empty\') }}</div>'],
    ['<p class="achievement-card__label">الهدف التالي</p>', '<p class="achievement-card__label">{{ t(\'student.home.achievements.next.label\') }}</p>'],
    ['<div class="achievement-card__title">أنت على الطريق الصحيح!</div>', '<div class="achievement-card__title">{{ t(\'student.home.achievements.next.empty\') }}</div>'],
    ['          عرض كل الإنجازات', '          {{ t(\'student.home.achievements.viewAll\') }}'],
  ],
  'src/components/student/ChatPanel.vue': [
    ['<p class="chat-panel__hint">اسأل أي سؤال حول هذا الدرس</p>', '<p class="chat-panel__hint">{{ t(\'student.chat.headerHint\') }}</p>'],
    ['text="مسح المحادثة"', ':text="t(\'student.chat.clear.tooltip\')"'],
    ['aria-label="مسح المحادثة"', ':aria-label="t(\'student.chat.clear.aria\')"'],
    ["return trimmed || 'المعلّm'", "return trimmed || t('student.common.teacher')"],
    ['? \'انتظر اكتمال تجهيز الدرس…\'', '? t(\'student.chat.input.waitForLesson\')'],
    ['return `اسأل ${displayTeacherName.value}…`', 'return t(\'student.chat.input.placeholder\', { teacher: displayTeacherName.value })'],
    ['<p class="chat-panel__empty-title">ابدأ محادثة مع {{ displayTeacherName }}</p>', '<p class="chat-panel__empty-title">{{ t(\'student.chat.empty.title\', { teacher: displayTeacherName }) }}</p>'],
    ['<p class="chat-panel__empty-hint text-medium-emphasis">اسأل أي سؤال حول هذا الدرس — الشرح بأسلوب معلمك.</p>', '<p class="chat-panel__empty-hint text-medium-emphasis">{{ t(\'student.chat.empty.hint\') }}</p>'],
  ],
  'src/components/student/ChatInput.vue': [
    ["placeholder: { type: String, default: 'اسأل معلّmك…' }", "placeholder: { type: String, default: '' }"],
    [':placeholder="placeholder"', ':placeholder="resolvedPlaceholder"'],
    ["recording ? 'إيقاف التسجيل' : 'تسجيل سؤال صوتي'", "recording ? t('student.chat.voice.stopRecording') : t('student.chat.voice.recordQuestion')"],
    ['aria-label="إرسال"', ':aria-label="t(\'student.chat.send.aria\')"'],
  ],
}

function ensureI18n(content) {
  if (content.includes('useI18n')) return content
  let out = content.replace(/(<script setup>\n)/, "$1import { useI18n } from 'vue-i18n'\n")
  out = out.replace(/(<script setup>\n(?:import[^\n]+\n)*)/, (m) => `${m}\nconst { t } = useI18n()\n`)
  return out
}

function walk(dir, out = []) {
  for (const name of readdirSync(dir)) {
    const p = join(dir, name)
    if (statSync(p).isDirectory()) walk(p, out)
    else if (name.endsWith('.vue')) out.push(p)
  }
  return out
}

// Fix ChatInput computed
const chatInputExtra = readFileSync(join(root, 'src/components/student/ChatInput.vue'), 'utf8')
if (!chatInputExtra.includes('resolvedPlaceholder')) {
  const patched = chatInputExtra
    .replace("import { nextTick, onUnmounted, ref } from 'vue'", "import { computed, nextTick, onUnmounted, ref } from 'vue'\nimport { useI18n } from 'vue-i18n'")
    .replace('const props = defineProps({', "const { t } = useI18n()\n\nconst props = defineProps({")
    .replace('const emit = defineEmits', "const resolvedPlaceholder = computed(() => props.placeholder || t('student.chat.input.defaultPlaceholder'))\n\nconst emit = defineEmits")
  writeFileSync(join(root, 'src/components/student/ChatInput.vue'), patched, 'utf8')
  console.log('Patched ChatInput extras')
}

for (const [rel, pairs] of Object.entries(FILE_PATCHES)) {
  const path = join(root, rel)
  let c = readFileSync(path, 'utf8')
  c = ensureI18n(c)
  for (const [from, to] of pairs) {
    if (!c.includes(from)) {
      console.warn(`[skip] ${rel}: ${from.slice(0, 50)}`)
      continue
    }
    c = c.split(from).join(to)
  }
  writeFileSync(path, c, 'utf8')
  console.log('Patched', rel)
}

console.log('Done.')
