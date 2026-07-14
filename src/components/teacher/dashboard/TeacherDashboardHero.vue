<template>
  <section class="teacher-hero teacher-home__section teacher-home__section--hero" :aria-label="$t('teacher.dashboard.welcome')">
    <div class="teacher-hero__row">
      <div class="teacher-hero__avatar" aria-hidden="true">{{ initials }}</div>
      <div class="teacher-hero__main">
        <p class="teacher-hero__eyebrow">{{ greeting }}</p>
        <h1 class="teacher-hero__title">{{ displayName }}</h1>
        <p class="teacher-hero__subtitle">{{ displaySubtitle }}</p>
        <div class="teacher-hero__actions">
          <v-btn
            class="btn-glow"
            color="secondary"
            variant="flat"
            size="default"
            rounded="lg"
            :to="primaryTo"
            prepend-icon="mdi-school-outline"
          >
            {{ displayPrimaryLabel }}
          </v-btn>
          <v-btn
            variant="tonal"
            color="secondary"
            size="default"
            rounded="lg"
            :to="secondaryTo"
            prepend-icon="mdi-message-text-outline"
          >
            {{ displaySecondaryLabel }}
          </v-btn>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import { ROUTES } from '../../../constants/app.js'

const props = defineProps({
  name: { type: String, default: '' },
  subtitle: { type: String, default: '' },
  primaryLabel: { type: String, default: '' },
  primaryTo: { type: String, default: ROUTES.TEACHER_GRADES },
  secondaryLabel: { type: String, default: '' },
  secondaryTo: { type: String, default: ROUTES.TEACHER_MESSAGES },
})

const displayName = computed(() => props.name || t('teacher.dashboard.teacher'))
const displaySubtitle = computed(() => props.subtitle || t('teacher.dashboard.subtitle'))
const displayPrimaryLabel = computed(() => props.primaryLabel || t('teacher.dashboard.manageClasses'))
const displaySecondaryLabel = computed(() => props.secondaryLabel || t('teacher.dashboard.sendMessage'))

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return t('teacher.dashboard.goodMorning')
  if (hour < 17) return t('teacher.dashboard.goodEvening')
  return t('teacher.dashboard.goodEvening')
})

const initials = computed(() => {
  const parts = props.name.trim().split(/\s+/).filter(Boolean)
  if (parts.length >= 2) return `${parts[0][0]}${parts[1][0]}`
  return props.name.slice(0, 2) || t('teacher.dashboard.teacherInitial')
})
</script>
