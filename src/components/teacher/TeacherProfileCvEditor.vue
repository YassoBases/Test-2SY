<template>
  <TeacherWorkspaceCard
    class="teacher-professional-page-placeholder tds-scope"
    :title="$t('teacher.cv.pageTitle')"
    :aria-label="$t('teacher.cv.comingSoonTitle')"
  >
    <p class="teacher-professional-page-placeholder__text">
      {{ $t('teacher.cv.comingSoonDesc') }}
    </p>

    <span class="teacher-professional-page-placeholder__badge">{{ $t('teacher.status.comingSoon') }}</span>

    <p class="teacher-professional-page-placeholder__preview" aria-hidden="true">
      {{ $t('teacher.cv.sectionsNav') }}
    </p>
  </TeacherWorkspaceCard>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import { TeacherWorkspaceCard } from './design-system/index.js'
</script>

<style scoped>
.teacher-professional-page-placeholder {
  margin-bottom: var(--em-space-xl);
  border: 1px solid var(--em-border-bright);
  box-shadow: none;
}

.teacher-professional-page-placeholder__text {
  margin: 0 0 var(--em-space-md);
  font-size: 0.875rem;
  line-height: 1.5;
  color: var(--em-text-muted);
  max-width: 36rem;
}

.teacher-professional-page-placeholder__badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 0.6875rem;
  font-weight: 700;
  color: var(--em-primary-deep, var(--em-primary));
  border: 1px solid color-mix(in srgb, var(--em-primary) 28%, var(--em-border-subtle));
  background: color-mix(in srgb, var(--em-primary) 6%, transparent);
}

.teacher-professional-page-placeholder__preview {
  margin: var(--em-space-sm) 0 0;
  font-size: 0.75rem;
  line-height: 1.4;
  color: var(--em-text-muted);
  opacity: 0.75;
}

:global([data-theme='morning']) .teacher-professional-page-placeholder.tds-workspace {
  border-color: var(--em-border-bright);
  box-shadow: none;
}
</style>
