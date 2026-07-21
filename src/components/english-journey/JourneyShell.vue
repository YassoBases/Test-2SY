<template>
  <div class="journey-shell page-container">
    <nav class="journey-shell__nav" aria-label="English Journey">
      <RouterLink
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        class="journey-shell__link"
        :class="{ 'journey-shell__link--active': isActive(item) }"
      >
        <v-icon :icon="item.icon" size="18" aria-hidden="true" />
        <span>{{ t(item.labelKey) }}</span>
      </RouterLink>
    </nav>

    <div class="journey-shell__body">
      <div class="journey-shell__main">
        <slot />
      </div>
      <aside
        class="journey-shell__aside"
        :class="{ 'journey-shell__aside--open': sidebarOpen }"
      >
        <button
          type="button"
          class="journey-shell__aside-toggle"
          :aria-expanded="sidebarOpen"
          @click="sidebarOpen = !sidebarOpen"
        >
          <v-icon :icon="sidebarOpen ? 'mdi-chevron-down' : 'mdi-robot-outline'" size="20" />
          <span>{{ t('student.englishJourney.sidebar.collapsed') }}</span>
        </button>
        <div class="journey-shell__aside-panel">
          <slot name="sidebar" />
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ROUTES } from '../../constants/app.js'

const { t } = useI18n()
const route = useRoute()
const sidebarOpen = ref(false)

const navItems = [
  { to: ROUTES.STUDENT_ENGLISH_JOURNEY, labelKey: 'student.englishJourney.shell.journey', icon: 'mdi-map', match: 'exact' },
  { to: ROUTES.STUDENT_LANGUAGES_READING, labelKey: 'student.englishJourney.shell.practice', icon: 'mdi-dumbbell', match: 'practice' },
  { to: ROUTES.STUDENT_ENGLISH_JOURNEY_REVIEW, labelKey: 'student.englishJourney.shell.review', icon: 'mdi-book-refresh', match: 'review' },
  { to: ROUTES.STUDENT_ENGLISH_JOURNEY_ACHIEVEMENTS, labelKey: 'student.englishJourney.shell.achievements', icon: 'mdi-trophy-outline', match: 'achievements' },
  { to: ROUTES.STUDENT_PROFILE, labelKey: 'student.englishJourney.shell.profile', icon: 'mdi-account-outline', match: 'profile' },
]

function isActive(item) {
  const path = route.path
  if (item.match === 'exact') return path === ROUTES.STUDENT_ENGLISH_JOURNEY
  if (item.match === 'review') return path.startsWith(ROUTES.STUDENT_ENGLISH_JOURNEY_REVIEW)
  if (item.match === 'achievements') return path.startsWith(ROUTES.STUDENT_ENGLISH_JOURNEY_ACHIEVEMENTS)
  if (item.match === 'profile') return path.startsWith(ROUTES.STUDENT_PROFILE)
  if (item.match === 'practice') {
    return (
      path.startsWith('/student/languages/reading') ||
      path.startsWith('/student/languages/listening') ||
      path.startsWith('/student/languages/speaking') ||
      path.startsWith('/student/languages/writing') ||
      path.startsWith('/student/languages/vocabulary')
    )
  }
  return false
}
</script>

<style scoped>
.journey-shell__nav {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-block-end: 24px;
}

.journey-shell__link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  border-radius: 12px;
  color: var(--text-muted, #3f4f63);
  text-decoration: none;
  font-size: 0.875rem;
  transition: background 220ms ease-out, color 220ms ease-out;
}

.journey-shell__link--active {
  background: color-mix(in srgb, var(--color-primary, #6366f1) 14%, transparent);
  color: var(--color-primary-deep, #4f46e5);
  font-weight: 600;
}

.journey-shell__body {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(240px, 300px);
  gap: 24px;
  align-items: start;
}

.journey-shell__aside-toggle {
  display: none;
}

@media (max-width: 960px) {
  .journey-shell__body {
    grid-template-columns: 1fr;
  }

  .journey-shell__aside {
    position: sticky;
    bottom: 0;
    z-index: 4;
    margin-block-start: 16px;
  }

  .journey-shell__aside-toggle {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    width: 100%;
    padding: 12px 16px;
    border: none;
    border-radius: 16px 16px 0 0;
    background: var(--surface-elevated, #fff);
    color: inherit;
    box-shadow: 0 -4px 20px rgba(12, 25, 41, 0.08);
    cursor: pointer;
  }

  .journey-shell__aside-panel {
    display: none;
    padding-block-end: 12px;
  }

  .journey-shell__aside--open .journey-shell__aside-panel {
    display: block;
  }
}

@media (prefers-reduced-motion: reduce) {
  .journey-shell__link {
    transition: none;
  }
}
</style>
