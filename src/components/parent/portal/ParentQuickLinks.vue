<template>
  <v-row dense>
    <v-col v-for="link in links" :key="link.to" cols="6" sm="4" md="3">
      <v-card
        :to="link.to"
        class="glass-card quick-link pa-4 h-100"
        variant="flat"
        hover
      >
        <v-icon :color="link.color" size="28" class="mb-2">{{ link.icon }}</v-icon>
        <div class="text-subtitle-2 font-weight-bold">{{ link.title }}</div>
        <div class="text-caption text-medium-emphasis">{{ link.caption }}</div>
      </v-card>
    </v-col>
  </v-row>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { ROUTES } from '../../../constants/app.js'

const { t } = useI18n()

const links = computed(() => [
  {
    title: t('parent.nav.performance.title'),
    caption: t('parent.nav.performance.caption'),
    icon: 'mdi-school-outline',
    color: 'primary',
    to: ROUTES.PARENT_PERFORMANCE,
  },
  {
    title: t('parent.nav.attendance.title'),
    caption: t('parent.nav.attendance.caption'),
    icon: 'mdi-clock-check-outline',
    color: 'secondary',
    to: ROUTES.PARENT_ATTENDANCE,
  },
  {
    title: t('parent.nav.lessons.title'),
    caption: t('parent.nav.lessons.caption'),
    icon: 'mdi-book-check-outline',
    color: 'success',
    to: ROUTES.PARENT_LESSONS,
  },
  {
    title: t('parent.nav.subjectsTeachers.title'),
    caption: t('parent.nav.subjectsTeachers.caption'),
    icon: 'mdi-book-education-outline',
    color: 'primary',
    to: ROUTES.PARENT_SUBJECTS_TEACHERS,
  },
  {
    title: t('parent.nav.planner.title'),
    caption: t('parent.nav.planner.caption'),
    icon: 'mdi-calendar-star',
    color: 'warning',
    to: ROUTES.PARENT_PLANNER,
  },
  {
    title: t('parent.nav.notifications.title'),
    caption: t('parent.nav.notifications.caption'),
    icon: 'mdi-bell-alert-outline',
    color: 'error',
    to: ROUTES.PARENT_NOTIFICATIONS,
  },
  {
    title: t('parent.nav.insights.title'),
    caption: t('parent.nav.insights.caption'),
    icon: 'mdi-creation',
    color: 'info',
    to: ROUTES.PARENT_INSIGHTS,
  },
  {
    title: t('parent.nav.reports.title'),
    caption: t('parent.nav.reports.caption'),
    icon: 'mdi-file-chart-outline',
    color: 'primary',
    to: ROUTES.PARENT_REPORTS,
  },
  {
    title: t('parent.nav.messages.title'),
    caption: t('parent.nav.messages.caption'),
    icon: 'mdi-message-text-outline',
    color: 'primary',
    to: ROUTES.PARENT_MESSAGES,
  },
])
</script>

<style scoped>
.quick-link {
  border: 1px solid rgba(255, 255, 255, 0.06);
  text-decoration: none;
  transition: border-color 0.2s ease, transform 0.15s ease;
}

.quick-link:hover {
  border-color: rgba(34, 211, 238, 0.35);
  transform: translateY(-2px);
}
</style>
