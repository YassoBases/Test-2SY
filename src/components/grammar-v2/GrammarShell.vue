<template>
  <div class="grammar-shell page-container">
    <nav class="grammar-shell__nav" :aria-label="t('student.grammarV2.shell.navLabel')">
      <RouterLink
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        class="grammar-shell__link"
        :class="{ 'grammar-shell__link--active': isActive(item) }"
      >
        <v-icon :icon="item.icon" size="18" aria-hidden="true" />
        <span>{{ t(item.labelKey) }}</span>
      </RouterLink>
    </nav>

    <div class="grammar-shell__body">
      <div class="grammar-shell__main">
        <slot />
      </div>
      <aside
        class="grammar-shell__aside"
        :class="{ 'grammar-shell__aside--open': sidebarOpen }"
      >
        <button
          type="button"
          class="grammar-shell__aside-toggle"
          :aria-expanded="sidebarOpen"
          @click="sidebarOpen = !sidebarOpen"
        >
          <v-icon :icon="sidebarOpen ? 'mdi-chevron-down' : 'mdi-book-open-page-variant'" size="20" />
          <span>{{ t('student.grammarV2.sidebar.collapsed') }}</span>
        </button>
        <div class="grammar-shell__aside-panel">
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
  { to: ROUTES.STUDENT_GRAMMAR, labelKey: 'student.grammarV2.shell.home', icon: 'mdi-home-outline', match: 'home' },
  { to: ROUTES.STUDENT_GRAMMAR_REVIEW, labelKey: 'student.grammarV2.shell.review', icon: 'mdi-book-refresh', match: 'review' },
]

function isActive(item) {
  const path = route.path
  if (item.match === 'home') {
    return path === ROUTES.STUDENT_GRAMMAR || path.startsWith('/student/grammar/topic')
  }
  if (item.match === 'review') return path.startsWith(ROUTES.STUDENT_GRAMMAR_REVIEW)
  return false
}
</script>

<style scoped>
.grammar-shell__nav {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-block-end: 24px;
}

.grammar-shell__link {
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

.grammar-shell__link--active {
  background: color-mix(in srgb, var(--color-primary, #6366f1) 14%, transparent);
  color: var(--color-primary-deep, #4f46e5);
  font-weight: 600;
}

.grammar-shell__body {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(240px, 300px);
  gap: 24px;
  align-items: start;
}

.grammar-shell__aside-toggle {
  display: none;
}

@media (max-width: 960px) {
  .grammar-shell__body {
    grid-template-columns: 1fr;
  }

  .grammar-shell__aside {
    position: sticky;
    bottom: 0;
    z-index: 4;
  }

  .grammar-shell__aside-toggle {
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

  .grammar-shell__aside-panel {
    display: none;
    padding-block-end: 12px;
  }

  .grammar-shell__aside--open .grammar-shell__aside-panel {
    display: block;
  }
}

@media (prefers-reduced-motion: reduce) {
  .grammar-shell__link {
    transition: none;
  }
}
</style>
