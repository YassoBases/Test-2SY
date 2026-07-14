<template>
  <AppSection
    id="my-subjects"
    :eyebrow="t('student.home.subjects.eyebrow')"
    :title="t('student.home.subjects.title')"
    :subtitle="t('student.home.subjects.subtitle')"
    spacing="lg"
    class="home-hub-section home-hub-section--subjects"
  >
    <div v-if="courses.length" class="catalog-rail" role="list">
      <SubjectCatalogCard
        v-for="(course, index) in courses"
        :key="course.id"
        role="listitem"
        :course="course"
        :stagger-delay="index * 80"
      />
    </div>

    <AppEmptyState
      v-else
      preset="courses"
      :description="grade ? t('student.home.subjects.empty.noCourses') : t('student.home.subjects.empty.noGrade')"
      :action-label="grade ? t('student.home.subjects.empty.subscriptions') : t('student.home.subjects.empty.setGrade')"
      :action-to="grade ? ROUTES.STUDENT_SUBSCRIPTIONS : ROUTES.ONBOARDING_GRADE"
      :action-icon="grade ? 'mdi-credit-card' : 'mdi-school'"
    />
  </AppSection>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import { AppEmptyState, AppSection } from '../../ui/index.js'
import { ROUTES } from '../../../constants/app.js'
import SubjectCatalogCard from './SubjectCatalogCard.vue'

const { t } = useI18n()

defineProps({
  courses: { type: Array, default: () => [] },
  grade: { type: [Number, String], default: null },
})
</script>

<style scoped>
.catalog-rail {
  display: flex;
  gap: 16px;
  overflow-x: auto;
  padding: 6px 2px 12px;
  scroll-snap-type: x mandatory;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: thin;
  overscroll-behavior-x: contain;
}

.catalog-rail :deep(.catalog-card) {
  touch-action: manipulation;
}

@media (min-width: 960px) {
  .catalog-rail {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 18px;
    overflow-x: visible;
  }

  .catalog-rail :deep(.catalog-card) {
    flex: none;
    min-width: 0;
  }
}
</style>
