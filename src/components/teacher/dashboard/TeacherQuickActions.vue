<template>
  <AppSection
    class="teacher-home__section teacher-home__section--actions"
    :eyebrow="$t('teacher.dashboard.quickAccess')"
    :title="$t('teacher.dashboard.workActions')"
    :subtitle="$t('teacher.dashboard.quickDesc')"
    spacing="sm"
    :divider="false"
  >
    <div class="teacher-quick-actions">
      <router-link
        v-for="action in actions"
        :key="action.title"
        :to="action.to"
        class="teacher-quick-action em-hover-lift"
        :class="{ 'teacher-quick-action--primary': action.primary }"
      >
        <span class="teacher-quick-action__icon" aria-hidden="true">
          <v-icon size="18">{{ action.icon }}</v-icon>
        </span>
        <span class="teacher-quick-action__title">{{ action.title }}</span>
        <span v-if="action.hint" class="teacher-quick-action__hint">{{ action.hint }}</span>
      </router-link>
    </div>
  </AppSection>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import { AppSection } from '../../ui/index.js'
import { ROUTES } from '../../../constants/app.js'

const actions = [
  { title: t('teacher.actions.createClass'), icon: 'mdi-plus', to: ROUTES.TEACHER_GRADES, hint: t('teacher.dashboard.newClass'), primary: true },
  { title: t('teacher.actions.addLesson'), icon: 'mdi-book-plus-outline', to: ROUTES.TEACHER_GRADES, hint: t('teacher.dashboard.fromClasses'), primary: true },
  { title: t('teacher.actions.createQuiz'), icon: 'mdi-clipboard-text-outline', to: '/teacher/quizzes', primary: true },
  { title: t('teacher.actions.sendMessage'), icon: 'mdi-message-text-outline', to: ROUTES.TEACHER_MESSAGES },
]
</script>
