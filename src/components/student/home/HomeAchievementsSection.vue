<template>
  <AppSection
    :title="t('student.home.achievements.title')"
    :subtitle="t('student.home.achievements.subtitle')"
    spacing="md"
    :divider="false"
    class="home-hub-section home-hub-section--achievements"
  >
    <div class="achievements-row">
      <AppCard v-if="recent" class="achievement-card achievement-card--recent" solid padding="sm">
        <p class="achievement-card__label">{{ t('student.home.achievements.recent.label') }}</p>
        <div class="achievement-card__badge">{{ recent.icon || '🏆' }}</div>
        <div class="achievement-card__title">{{ recent.title }}</div>
        <p v-if="recent.description" class="achievement-card__desc">{{ recent.description }}</p>
      </AppCard>
      <AppCard v-else class="achievement-card achievement-card--recent" solid padding="sm">
        <p class="achievement-card__label">{{ t('student.home.achievements.recent.label') }}</p>
        <div class="achievement-card__badge">✨</div>
        <div class="achievement-card__title">{{ t('student.home.achievements.recent.empty') }}</div>
      </AppCard>

      <AppCard class="achievement-card achievement-card--next" solid padding="sm">
        <p class="achievement-card__label">{{ t('student.home.achievements.next.label') }}</p>
        <template v-if="next">
          <div class="achievement-card__badge achievement-card__badge--locked">
            {{ next.icon || '🎯' }}
            <v-icon class="achievement-card__lock" size="14">mdi-lock</v-icon>
          </div>
          <div class="achievement-card__title">{{ next.title }}</div>
          <p v-if="next.description" class="achievement-card__desc">{{ next.description }}</p>
        </template>
        <template v-else>
          <div class="achievement-card__badge">🏅</div>
          <div class="achievement-card__title">{{ t('student.home.achievements.next.empty') }}</div>
        </template>
        <AppButton
          class="achievement-card__link"
          variant="ghost"
          size="small"
          :to="ROUTES.STUDENT_ACHIEVEMENTS"
        >
          {{ t('student.home.achievements.viewAll') }}
        </AppButton>
      </AppCard>
    </div>
  </AppSection>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import { AppButton, AppCard, AppSection } from '../../ui/index.js'

const { t } = useI18n()
import { ROUTES } from '../../../constants/app.js'

defineProps({
  recent: { type: Object, default: null },
  next: { type: Object, default: null },
})
</script>

<style scoped>
.achievements-row {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

@media (min-width: 768px) {
  .achievements-row {
    grid-template-columns: 1fr 1fr;
  }
}

.achievement-card {
  text-align: center;
}

.achievement-card--recent {
  border-color: rgba(52, 211, 153, 0.2);
}

.achievement-card--next {
  border-color: rgba(99, 102, 241, 0.16);
}

.achievement-card__label {
  margin: 0 0 8px;
  font-size: 0.6875rem;
  font-weight: 600;
  color: var(--em-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.achievement-card__badge {
  font-size: 2rem;
  line-height: 1;
  margin-bottom: 8px;
  position: relative;
  display: inline-block;
}

.achievement-card__badge--locked {
  filter: grayscale(0.35);
  opacity: 0.85;
}

.achievement-card__lock {
  position: absolute;
  bottom: -2px;
  left: -4px;
  background: var(--em-surface-solid);
  border-radius: 50%;
}

.achievement-card__title {
  font-weight: 700;
  font-size: 0.875rem;
  margin-bottom: 4px;
  line-height: 1.35;
}

.achievement-card__desc {
  margin: 0;
  font-size: 0.75rem;
  color: var(--em-text-muted);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.achievement-card__link {
  margin-top: 10px;
}
</style>
