<template>
  <div class="portfolio-display">
    <!-- 3. Teaching impact -->
    <section v-if="hasImpact" class="mb-4">
      <div class="text-overline text-medium-emphasis mb-2">{{ $t('teacher.portfolio.impact') }}</div>
      <v-list class="bg-transparent pa-0" density="compact">
        <v-list-item
          v-for="(line, i) in profile.teaching_impact?.highlights"
          :key="`impact-${i}`"
          prepend-icon="mdi-chart-line"
          class="px-0"
        >
          <v-list-item-title class="text-body-2">{{ line }}</v-list-item-title>
        </v-list-item>
      </v-list>
    </section>

    <!-- 4–6 CV sections -->
    <section v-if="profile.qualifications?.length" class="mb-4">
      <div class="text-overline text-medium-emphasis mb-2">{{ $t('teacher.portfolio.qualifications') }}</div>
      <div v-for="item in profile.qualifications" :key="`q-${item.id}`" class="cv-entry pa-3 rounded-lg mb-2">
        <div class="text-body-2 font-weight-bold">{{ item.title }}</div>
        <div v-if="qualificationMeta(item)" class="text-caption text-medium-emphasis">{{ qualificationMeta(item) }}</div>
        <p v-if="item.description" class="text-caption mb-0 mt-1">{{ item.description }}</p>
      </div>
    </section>

    <section v-if="profile.teaching_experiences?.length" class="mb-4">
      <div class="text-overline text-medium-emphasis mb-2">{{ $t('teacher.portfolio.experience') }}</div>
      <div v-for="item in profile.teaching_experiences" :key="`e-${item.id}`" class="cv-entry pa-3 rounded-lg mb-2">
        <div class="text-body-2 font-weight-bold">{{ item.title }}</div>
        <div class="text-caption text-medium-emphasis">{{ experienceMeta(item) }}</div>
        <p v-if="item.description" class="text-caption mb-0 mt-1">{{ item.description }}</p>
      </div>
    </section>

    <section v-if="profile.achievements?.length" class="mb-4">
      <div class="text-overline text-medium-emphasis mb-2">{{ $t('teacher.portfolio.achievements') }}</div>
      <div
        v-for="item in profile.achievements"
        :key="`a-${item.id}`"
        class="cv-entry pa-3 rounded-lg mb-2"
        :class="{ 'cv-entry--pinned': item.is_pinned }"
      >
        <div class="d-flex align-center gap-2">
          <v-icon v-if="item.is_pinned" color="warning" size="18">mdi-pin</v-icon>
          <div class="text-body-2 font-weight-bold">
            {{ item.title }}
            <span v-if="item.year" class="text-caption text-medium-emphasis ms-1">({{ item.year }})</span>
          </div>
        </div>
        <p v-if="item.description" class="text-caption mb-0 mt-1">{{ item.description }}</p>
      </div>
    </section>

    <!-- 7. Teaching philosophy -->
    <section v-if="hasPhilosophy" class="mb-4">
      <div class="text-overline text-medium-emphasis mb-2">{{ $t('teacher.portfolio.methodology') }}</div>
      <div v-if="profile.teaching_philosophy?.teaching_style" class="mb-3">
        <div class="text-caption font-weight-bold mb-1">{{ $t('teacher.portfolio.teachingStyle') }}</div>
        <p class="text-body-2 mb-0">{{ profile.teaching_philosophy.teaching_style }}</p>
      </div>
      <div v-if="profile.teaching_philosophy?.lesson_approach" class="mb-3">
        <div class="text-caption font-weight-bold mb-1">{{ $t('teacher.portfolio.lessonApproach') }}</div>
        <p class="text-body-2 mb-0">{{ profile.teaching_philosophy.lesson_approach }}</p>
      </div>
      <div v-if="profile.teaching_philosophy?.exam_preparation_strategy">
        <div class="text-caption font-weight-bold mb-1">{{ $t('teacher.portfolio.examStrategy') }}</div>
        <p class="text-body-2 mb-0">{{ profile.teaching_philosophy.exam_preparation_strategy }}</p>
      </div>
    </section>

    <!-- 8. Why study with me -->
    <section v-if="profile.why_study_points?.length" class="mb-4">
      <div class="text-overline text-medium-emphasis mb-2">{{ $t('teacher.portfolio.whyChoose') }}</div>
      <v-list class="bg-transparent pa-0" density="compact">
        <v-list-item
          v-for="point in profile.why_study_points"
          :key="point.id"
          prepend-icon="mdi-check-circle-outline"
          class="px-0"
        >
          <v-list-item-title class="text-body-2 font-weight-medium">{{ point.title }}</v-list-item-title>
          <v-list-item-subtitle v-if="point.description">{{ point.description }}</v-list-item-subtitle>
        </v-list-item>
      </v-list>
    </section>

    <!-- 9. Academic statistics -->
    <section v-if="profile.academic_statistics" class="mb-4">
      <div class="text-overline text-medium-emphasis mb-2">{{ $t('teacher.portfolio.academicStats') }}</div>
      <v-row dense>
        <v-col v-for="stat in statItems" :key="stat.label" cols="6">
          <div class="stat-box text-center pa-2 rounded-lg">
            <div class="text-subtitle-1 font-weight-bold">{{ stat.value }}</div>
            <div class="text-caption text-medium-emphasis">{{ stat.label }}</div>
          </div>
        </v-col>
      </v-row>
    </section>

    <!-- 10. Professional documents -->
    <section v-if="profile.professional_documents?.length" class="mb-2">
      <div class="text-overline text-medium-emphasis mb-2">{{ $t('teacher.portfolio.proDocuments') }}</div>
      <v-list class="bg-transparent pa-0" density="compact">
        <v-list-item
          v-for="doc in profile.professional_documents"
          :key="doc.id"
          class="cv-entry rounded-lg mb-2"
        >
          <template #prepend>
            <v-icon>{{ docIcon(doc) }}</v-icon>
          </template>
          <v-list-item-title class="text-body-2">{{ doc.title }}</v-list-item-title>
          <v-list-item-subtitle>{{ docTypeLabel(doc.document_type) }}</v-list-item-subtitle>
          <template #append>
            <v-btn
              size="small"
              variant="tonal"
              :href="docUrl(doc.file_url)"
              target="_blank"
              rel="noopener"
              prepend-icon="mdi-download"
            >
              {{ $t('teacher.portfolio.view') }}
            </v-btn>
          </template>
        </v-list-item>
      </v-list>
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import { getApiBaseUrl } from '../../api/client.js'

const props = defineProps({
  profile: { type: Object, required: true },
})

const hasImpact = computed(() => (props.profile.teaching_impact?.highlights?.length ?? 0) > 0)

const hasPhilosophy = computed(() => {
  const p = props.profile.teaching_philosophy
  return p && (p.teaching_style || p.lesson_approach || p.exam_preparation_strategy)
})

const statItems = computed(() => {
  const s = props.profile.academic_statistics
  if (!s) return []
  return [
    { label: t('teacher.portfolio.activeStudents'), value: s.active_students },
    { label: t('teacher.portfolio.totalStudents'), value: s.total_students },
    { label: t('teacher.portfolio.publishedCourses'), value: s.courses_published },
    { label: t('teacher.grades.lessonsPublished'), value: s.lessons_published },
    { label: t('teacher.grades.lessonCompletionRate'), value: `${s.average_lesson_completion_rate}%` },
    {
      label: t('teacher.portfolio.avgTests'),
      value: s.average_quiz_score != null ? `${s.average_quiz_score}%` : '—',
    },
  ]
})

function qualificationMeta(item) {
  return [item.institution, item.year].filter(Boolean).join(' · ')
}

function experienceMeta(item) {
  const from = item.year_from || '—'
  const to = item.year_to || t('teacher.labels.now')
  const org = item.organization ? `${item.organization} · ` : ''
  return `${org}${from} — ${to}`
}

function docTypeLabel(type) {
  return { certificate: t('teacher.portfolio.certificate'), degree: t('teacher.portfolio.degree'), training: t('teacher.portfolio.training') }[type] || type
}

function docIcon(doc) {
  if (doc.mime_type?.includes('pdf')) return 'mdi-file-pdf-box'
  return 'mdi-file-image'
}

function docUrl(path) {
  if (!path) return '#'
  if (path.startsWith('http')) return path
  const base = getApiBaseUrl()?.replace(/\/api\/?$/, '') || ''
  return `${base}${path}`
}
</script>

<style scoped>
.cv-entry {
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.03);
}

.cv-entry--pinned {
  border-color: rgba(251, 191, 36, 0.35);
}

.stat-box {
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.03);
}
</style>
