<template>
  <AppSection
    id="next-mission"
    :title="t('student.home.missionDetail.title')"
    :subtitle="t('student.home.missionDetail.subtitle')"
    spacing="md"
    :divider="false"
    class="next-mission-section home-hub-section home-hub-section--mission"
  >
    <AppCard class="next-mission em-hover-lift" solid padding="md">
      <div class="next-mission__accent" aria-hidden="true" />

      <div class="next-mission__layout">
        <div class="next-mission__main">
          <p class="next-mission__headline">{{ mission.headline }}</p>
          <h2 class="next-mission__title">{{ mission.lessonTitle }}</h2>

          <div v-if="mission.courseName" class="next-mission__context">
            <TeacherAvatar
              :name="mission.teacherName"
              :image-url="mission.teacherImageUrl"
              :size="44"
            />
            <div class="next-mission__meta">
              <span class="next-mission__course">{{ mission.courseName }}</span>
              <span class="next-mission__teacher">{{ t('student.home.missionDetail.withTeacher', { name: mission.teacherName }) }}</span>
            </div>
          </div>

          <div v-if="mission.kind !== 'empty' && mission.lessonCount" class="next-mission__progress">
            <AnimatedProgressBar
              :value="mission.progress"
              color="secondary"
              :height="5"
              :delay="80"
            />
            <p class="next-mission__progress-detail">
              {{ t('student.home.missionDetail.progress', { done: mission.completedLessons, total: mission.lessonCount }) }}
            </p>
          </div>
        </div>

        <div class="next-mission__cta-wrap">
          <AppButton
            variant="secondary"
            size="default"
            block
            :to="mission.to"
            prepend-icon="mdi-play-circle"
            class="next-mission__cta em-press"
          >
            {{ mission.ctaLabel }}
          </AppButton>
        </div>
      </div>
    </AppCard>
  </AppSection>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import TeacherAvatar from '../../onboarding/TeacherAvatar.vue'
import { AppButton, AppCard, AppSection } from '../../ui/index.js'
import AnimatedProgressBar from './AnimatedProgressBar.vue'

const { t } = useI18n()

defineProps({
  mission: {
    type: Object,
    required: true,
  },
})
</script>

<style scoped>
.next-mission-section :deep(.app-section__title) {
  font-size: 1rem;
  font-weight: 700;
  color: var(--em-text-muted);
}

.next-mission-section :deep(.app-section__subtitle) {
  font-size: var(--em-text-caption);
}

.next-mission-section :deep(.app-section__head) {
  margin-bottom: 0.65rem;
  padding-bottom: 0;
  border-bottom: none;
}

.next-mission {
  position: relative;
  overflow: hidden;
}

.next-mission__accent {
  position: absolute;
  inset: 0 auto 0 0;
  width: 3px;
  background: var(--em-primary);
  border-radius: 3px 0 0 3px;
  opacity: 0.65;
}

.next-mission__layout {
  position: relative;
  display: grid;
  gap: 16px;
}

@media (min-width: 768px) {
  .next-mission__layout {
    grid-template-columns: 1fr auto;
    align-items: center;
    gap: 20px;
  }
}

.next-mission__headline {
  margin: 0 0 6px;
  font-size: var(--em-text-caption);
  font-weight: 700;
  color: var(--em-text-muted);
}

.next-mission__title {
  margin: 0 0 12px;
  font-family: var(--font-display);
  font-size: clamp(1.05rem, 2.8vw, 1.25rem);
  font-weight: 700;
  line-height: 1.35;
  color: var(--em-text);
  max-width: 42ch;
}

.next-mission__context {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
  max-width: 360px;
}

.next-mission__course {
  display: block;
  font-weight: 700;
  font-size: var(--em-text-sm);
  color: var(--em-text);
}

.next-mission__teacher {
  display: block;
  font-size: var(--em-text-caption);
  color: var(--em-text-muted);
  margin-top: 1px;
}

.next-mission__progress {
  max-width: 360px;
}

.next-mission__progress-detail {
  margin: 8px 0 0;
  font-size: var(--em-text-caption);
  color: var(--em-text-helper);
  line-height: 1.4;
}

.next-mission__cta-wrap {
  min-width: 160px;
}
</style>
