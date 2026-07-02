<template>
  <v-card v-if="data" class="glass-card pa-5 mb-6" variant="flat">
    <div class="d-flex align-center gap-2 mb-4">
      <v-icon color="secondary">mdi-translate</v-icon>
      <h3 class="text-h6 font-weight-bold mb-0">{{ t('parent.language.title') }}</h3>
      <v-chip size="small" variant="tonal" color="secondary" class="ms-auto">
        {{ data.overall_level || t('parent.common.emDash') }}
      </v-chip>
    </div>

    <v-row class="mb-4">
      <v-col v-for="skill in levelSkills" :key="skill.key" cols="6" sm="3">
        <div class="skill-box pa-3 rounded-lg text-center">
          <div class="text-caption text-medium-emphasis">{{ skill.label }}</div>
          <div class="text-h6 font-weight-bold">{{ skill.level || t('parent.common.emDash') }}</div>
          <div class="text-caption text-secondary mt-1">{{ t('parent.language.growth', { percent: growthPercent(skill.key) }) }}</div>
        </div>
      </v-col>
    </v-row>

    <v-row class="mb-2">
      <v-col v-if="summary" cols="12" sm="6" md="4">
        <div class="metric-box pa-3 rounded-lg">
          <div class="text-caption text-medium-emphasis">{{ t('parent.language.analyticsSummary') }}</div>
          <div class="text-body-2 mt-1">
            {{ t('parent.language.strongestSkill') }} <strong>{{ summary.strongest_skill_ar || t('parent.common.emDash') }}</strong>
          </div>
          <div class="text-body-2">
            {{ t('parent.language.needsFocus') }} <strong>{{ summary.weakest_skill_ar || t('parent.common.emDash') }}</strong>
          </div>
          <div class="text-body-2 mt-1">
            {{ t('parent.language.scenariosAchievements', {
              scenarios: summary.completed_scenarios ?? 0,
              achievements: summary.achievements_count ?? 0,
            }) }}
          </div>
        </div>
      </v-col>
      <v-col cols="6" sm="4" md="2">
        <div class="metric-box pa-3 rounded-lg text-center">
          <div class="text-caption text-medium-emphasis">{{ t('parent.language.knownWords') }}</div>
          <div class="text-h6 font-weight-bold">{{ data.vocabulary_count }}</div>
        </div>
      </v-col>
      <v-col cols="6" sm="4" md="2">
        <div class="metric-box pa-3 rounded-lg text-center">
          <div class="text-caption text-medium-emphasis">{{ t('parent.language.vocabularyLearned') }}</div>
          <div class="text-h6 font-weight-bold">{{ data.vocabulary_learned }}</div>
        </div>
      </v-col>
      <v-col cols="6" sm="4" md="2">
        <div class="metric-box pa-3 rounded-lg text-center">
          <div class="text-caption text-medium-emphasis">{{ t('parent.language.currentStreak') }}</div>
          <div class="text-h6 font-weight-bold">🔥 {{ data.current_streak }}</div>
          <div class="text-caption">{{ t('parent.language.longestStreak', { n: data.longest_streak }) }}</div>
        </div>
      </v-col>
      <v-col cols="6" sm="4" md="2">
        <div class="metric-box pa-3 rounded-lg text-center">
          <div class="text-caption text-medium-emphasis">{{ t('parent.language.activitiesDone') }}</div>
          <div class="text-h6 font-weight-bold">{{ data.completed_activities }}</div>
        </div>
      </v-col>
      <v-col cols="6" sm="4" md="2">
        <div class="metric-box pa-3 rounded-lg text-center">
          <div class="text-caption text-medium-emphasis">{{ t('parent.language.writingDone') }}</div>
          <div class="text-h6 font-weight-bold">{{ data.writing_completed }}</div>
        </div>
      </v-col>
      <v-col cols="6" sm="4" md="2">
        <div class="metric-box pa-3 rounded-lg text-center">
          <div class="text-caption text-medium-emphasis">{{ t('parent.language.speakingDone') }}</div>
          <div class="text-h6 font-weight-bold">{{ data.speaking_completed }}</div>
        </div>
      </v-col>
    </v-row>

    <v-card
      v-if="data.latest_certificate"
      class="glass-card pa-4 mb-2"
      variant="flat"
    >
      <div class="d-flex align-center flex-wrap gap-3">
        <v-icon color="secondary">mdi-certificate</v-icon>
        <div class="flex-grow-1">
          <div class="text-caption text-medium-emphasis">{{ t('parent.language.latestCertificate') }}</div>
          <div class="text-body-1 font-weight-bold">
            {{ data.latest_certificate.certificate_level }}
            · {{ data.latest_certificate.certificate_number }}
          </div>
          <div class="text-caption">{{ formatDate(data.latest_certificate.issued_at) }}</div>
        </div>
        <v-btn
          v-if="data.latest_certificate.pdf_url"
          size="small"
          variant="tonal"
          color="secondary"
          prepend-icon="mdi-download"
          :href="data.latest_certificate.pdf_url"
          target="_blank"
        >
          {{ t('parent.common.pdf') }}
        </v-btn>
      </div>
    </v-card>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  data: { type: Object, default: null },
})

const { t, locale } = useI18n()

const summary = computed(() => props.data?.language_analytics_summary || null)

const levelSkills = computed(() => [
  { key: 'reading', label: t('parent.language.reading'), level: props.data?.reading_level },
  { key: 'listening', label: t('parent.language.listening'), level: props.data?.listening_level },
  { key: 'writing', label: t('parent.language.writing'), level: props.data?.writing_level },
  { key: 'speaking', label: t('parent.language.speaking'), level: props.data?.speaking_level },
])

function growthPercent(skillKey) {
  const g = props.data?.skill_growth?.[skillKey]
  return g?.growth_percent ?? 0
}

function dateLocale() {
  return locale.value === 'ar' ? 'ar-SA' : 'en-US'
}

function formatDate(value) {
  if (!value) return t('parent.common.emDash')
  return new Date(value).toLocaleDateString(dateLocale(), {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}
</script>

<style scoped>
.skill-box,
.metric-box {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.06);
}
</style>
