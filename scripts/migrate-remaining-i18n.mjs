import fs from 'fs'
import path from 'path'

const root = path.resolve(import.meta.dirname, '..')

const langFiles = {
  'src/components/language/home/LanguageHomeJourneyStrip.vue': [
    ['مسارك يظهر بعد تحديد المستوى', "{{ t('common.languageLearn.journeyPending') }}"],
    ["import { useI18n } from 'vue-i18n'\n\ndefineProps", "defineProps"],
  ],
  'src/components/language/home/LanguageHomeMissionHero.vue': [
    ['مهمتك اليوم', "{{ t('common.languageLearn.missionEyebrow') }}"],
    ['{{ dailyPlan.completed_today }} من {{ dailyPlan.goal }} مكتمل', "{{ t('common.languageLearn.missionProgress', { done: dailyPlan.completed_today, goal: dailyPlan.goal }) }}"],
    ['التالي', "{{ t('common.languageLearn.next') }}"],
    ['أحسنت! أنهيت مهمة اليوم — يمكنك التمرّن أو مراجعة المسار.', "{{ t('common.languageLearn.missionDone') }}"],
    ['افتح المسار التعليمي لبدء مهمتك اليومية.', "{{ t('common.languageLearn.openPathHint') }}"],
    ['تابع المهمة', "{{ t('common.languageLearn.continueMission') }}"],
    ['عرض المسار', "{{ t('common.languageLearn.viewPath') }}"],
    ['ابدأ من المسار', "{{ t('common.languageLearn.startFromPath') }}"],
    ["import { computed } from 'vue'", "import { computed } from 'vue'\nimport { useI18n } from 'vue-i18n'"],
    ['defineEmits([\'start\'])', "defineEmits(['start'])\n\nconst { t } = useI18n()"],
  ],
}

for (const [rel, pairs] of Object.entries(langFiles)) {
  const file = path.join(root, rel)
  let content = fs.readFileSync(file, 'utf8')
  if (!content.includes('useI18n') && rel.includes('JourneyStrip')) {
    content = content.replace(
      '<script setup>\ndefineProps',
      "<script setup>\nimport { useI18n } from 'vue-i18n'\n\nconst { t } = useI18n()\n\ndefineProps",
    )
  }
  for (const [from, to] of pairs) {
    content = content.replace(from, to)
  }
  fs.writeFileSync(file, content)
  console.log('Updated', rel)
}
