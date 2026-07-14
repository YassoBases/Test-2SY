<template>
  <div class="badge-grid">
    <div
      v-for="badge in badges"
      :key="badge.achievement_key"
      class="badge-card"
      :class="badge.unlocked ? 'badge-card--unlocked' : 'badge-card--locked'"
    >
      <div class="badge-card__icon-wrap">
        <span class="badge-card__icon">{{ badge.icon }}</span>
        <v-icon
          v-if="!badge.unlocked"
          class="badge-card__lock"
          size="16"
          color="medium-emphasis"
        >
          mdi-lock
        </v-icon>
      </div>
      <div class="badge-card__title">{{ badge.title }}</div>
      <div class="badge-card__desc">{{ badge.description }}</div>
      <div v-if="badge.unlocked && badge.unlocked_at" class="badge-card__date text-caption text-medium-emphasis">
        {{ formatDate(badge.unlocked_at) }}
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  badges: {
    type: Array,
    default: () => [],
  },
})

function formatDate(value) {
  if (!value) return ''
  try {
    return new Date(value).toLocaleDateString('ar-SY', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  } catch {
    return ''
  }
}
</script>

<style scoped>
.badge-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 14px;
}

.badge-card {
  border-radius: 14px;
  padding: 16px 12px;
  text-align: center;
  border: 1px solid rgba(124, 108, 240, 0.15);
  background: rgba(255, 255, 255, 0.02);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.badge-card--locked {
  filter: grayscale(1);
  opacity: 0.65;
}

.badge-card--unlocked {
  border-color: rgba(34, 211, 238, 0.35);
  box-shadow: 0 0 18px rgba(124, 108, 240, 0.25), 0 0 8px rgba(34, 211, 238, 0.15);
}

.badge-card__icon-wrap {
  position: relative;
  display: inline-flex;
  margin-bottom: 8px;
}

.badge-card__icon {
  font-size: 2rem;
  line-height: 1;
}

.badge-card__lock {
  position: absolute;
  bottom: -2px;
  right: -6px;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 50%;
  padding: 2px;
}

.badge-card__title {
  font-size: 0.85rem;
  font-weight: 700;
  margin-bottom: 4px;
}

.badge-card__desc {
  font-size: 0.72rem;
  color: rgba(255, 255, 255, 0.55);
  line-height: 1.4;
}

.badge-card__date {
  margin-top: 8px;
}
</style>
