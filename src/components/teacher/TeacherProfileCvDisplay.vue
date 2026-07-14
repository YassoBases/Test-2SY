<template>
  <div>
    <section v-if="profile.qualifications?.length" class="mb-4">
      <div class="text-overline text-medium-emphasis mb-2">{{ $t('teacher.portfolio.qualifications') }}</div>
      <div
        v-for="item in profile.qualifications"
        :key="`q-${item.id}`"
        class="cv-entry pa-3 rounded-lg mb-2"
      >
        <div class="text-body-2 font-weight-bold">{{ item.title }}</div>
        <div v-if="qualificationMeta(item)" class="text-caption text-medium-emphasis">
          {{ qualificationMeta(item) }}
        </div>
        <p v-if="item.description" class="text-caption mb-0 mt-1">{{ item.description }}</p>
      </div>
    </section>

    <section v-if="profile.teaching_experiences?.length" class="mb-4">
      <div class="text-overline text-medium-emphasis mb-2">{{ $t('teacher.portfolio.experience') }}</div>
      <div
        v-for="item in profile.teaching_experiences"
        :key="`e-${item.id}`"
        class="cv-entry pa-3 rounded-lg mb-2"
      >
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
      >
        <div class="text-body-2 font-weight-bold">
          {{ item.title }}
          <span v-if="item.year" class="text-caption text-medium-emphasis ms-1">({{ item.year }})</span>
        </div>
        <p v-if="item.description" class="text-caption mb-0 mt-1">{{ item.description }}</p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

defineProps({
  profile: { type: Object, required: true },
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
</script>

<style scoped>
.cv-entry {
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.03);
}
</style>
