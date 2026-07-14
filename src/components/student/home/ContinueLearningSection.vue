<template>
  <AppSection
    id="continue-learning"
    :title="t('student.home.continue.title')"
    :subtitle="t('student.home.continue.subtitle')"
    spacing="md"
    :divider="false"
    class="home-hub-section home-hub-section--continue"
  >
    <div v-if="items.length" class="continue-grid">
      <AppCard
        v-for="(item, index) in items"
        :key="item.key"
        class="continue-card home-stagger-item"
        :style="{ '--stagger-delay': `${index * 60}ms` }"
        interactive
        padding="md"
        :to="item.to"
      >
        <div class="continue-card__icon">
          <v-icon :icon="item.icon" size="20" color="primary" />
        </div>
        <div class="continue-card__body">
          <div class="continue-card__label">{{ item.label }}</div>
          <div class="continue-card__title">{{ item.title }}</div>
          <div class="continue-card__meta">{{ item.meta }}</div>
        </div>
        <v-icon class="continue-card__arrow" size="18">mdi-chevron-left</v-icon>
      </AppCard>
    </div>
    <AppEmptyState
      v-else
      compact
      icon="mdi-book-open-outline"
      :title="t('student.home.continue.empty.title')"
      :description="t('student.home.continue.empty.description')"
      :action-label="t('student.home.continue.empty.action')"
      :action-to="ROUTES.STUDENT_SUBSCRIPTIONS"
      action-icon="mdi-credit-card"
    />
  </AppSection>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import { AppCard, AppEmptyState, AppSection } from '../../ui/index.js'
import { ROUTES } from '../../../constants/app.js'

const { t } = useI18n()

defineProps({
  items: { type: Array, default: () => [] },
})
</script>

<style scoped>
.continue-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
}

@media (min-width: 640px) {
  .continue-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
}

@media (min-width: 960px) {
  .continue-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.continue-card {
  position: relative;
  min-height: 108px;
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  gap: 12px;
  overflow: hidden;
}

.continue-card__icon {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--em-surface-secondary);
  border: 1px solid var(--em-border-subtle);
}

.continue-card__body {
  flex: 1;
  min-width: 0;
  padding-top: 2px;
}

.continue-card__label {
  font-size: 0.6875rem;
  font-weight: 600;
  color: var(--em-text-helper);
  margin-bottom: 3px;
}

.continue-card__title {
  font-weight: 700;
  font-size: 0.9rem;
  line-height: 1.35;
  color: var(--em-text);
  margin-bottom: 4px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.continue-card__meta {
  font-size: 0.75rem;
  color: var(--em-text-muted);
  line-height: 1.35;
}

.continue-card__arrow {
  flex-shrink: 0;
  margin-top: 4px;
  color: var(--em-text-subtle);
  transition: transform var(--em-duration-fast) var(--em-ease-out);
}

.continue-card:hover .continue-card__arrow {
  transform: translateX(-2px);
  color: var(--em-primary);
}
</style>
