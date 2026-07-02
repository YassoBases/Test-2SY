<template>
  <v-card
    class="glass-card glass-card--elevated pa-5 mb-6 subjects-card"
    variant="flat"
    :to="ROUTES.PARENT_SUBJECTS_TEACHERS"
    hover
  >
    <div class="d-flex align-center justify-space-between mb-3 flex-wrap gap-2">
      <div class="d-flex align-center gap-2">
        <v-icon color="primary">mdi-book-account-outline</v-icon>
        <h3 class="text-subtitle-1 font-weight-bold mb-0">{{ t('parent.subjectsTeachers.title') }}</h3>
      </div>
      <v-chip size="x-small" variant="tonal" append-icon="mdi-chevron-left">{{ t('parent.subjectsTeachers.viewAll') }}</v-chip>
    </div>
    <p class="text-caption text-medium-emphasis mb-0">
      {{ t('parent.subjectsTeachers.cardHint') }}
    </p>
  </v-card>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import { ROUTES } from '../../../constants/app.js'

const { t } = useI18n()
</script>

<style scoped>
.subjects-card {
  text-decoration: none;
  cursor: pointer;
  border: 1px solid rgba(34, 211, 238, 0.15);
}
</style>
