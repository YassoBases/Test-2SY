<template>
  <v-card class="mission-card pa-5 mb-4" variant="flat">
    <div class="d-flex align-start gap-3 mb-4">
      <v-avatar color="secondary" variant="tonal" size="48" class="flex-shrink-0">
        <v-icon size="26">{{ icon }}</v-icon>
      </v-avatar>
      <div class="flex-grow-1 min-width-0">
        <div class="text-overline text-medium-emphasis">{{ title }}</div>
        <div v-if="subtitle" class="text-h6 font-weight-bold mt-1">{{ subtitle }}</div>
      </div>
    </div>

    <div v-if="focusItems.length" class="mb-4">
      <div class="text-body-2 font-weight-medium mb-2">{{ focusTitle }}</div>
      <ul class="mission-list pa-0">
        <li v-for="(item, idx) in focusItems" :key="idx" class="d-flex align-start gap-2">
          <v-icon color="success" size="18" class="flex-shrink-0 mt-1">mdi-check</v-icon>
          <span>{{ item }}</span>
        </li>
      </ul>
    </div>

    <div v-if="whyText" class="mission-why mb-4">
      <div class="text-body-2 font-weight-medium mb-1">{{ whyTitle }}</div>
      <p class="text-body-2 text-medium-emphasis mb-0">{{ whyText }}</p>
    </div>

    <div v-if="metaRows.length" class="mission-meta mb-4">
      <div v-for="row in metaRows" :key="row.label" class="mission-meta-row">
        <span class="mission-meta-label">{{ row.label }}</span>
        <span class="mission-meta-value">{{ row.value }}</span>
      </div>
    </div>

    <div v-if="rewardText" class="mission-reward">
      <v-icon size="18" color="secondary" class="me-1">mdi-gift-outline</v-icon>
      <span class="text-body-2 font-weight-medium">{{ rewardLabel }}</span>
      <span class="text-body-2 text-medium-emphasis ms-1">{{ rewardText }}</span>
    </div>
  </v-card>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
  icon: { type: String, default: 'mdi-target' },
  focusTitle: { type: String, default: '' },
  focusItems: { type: Array, default: () => [] },
  whyTitle: { type: String, default: '' },
  whyText: { type: String, default: '' },
  metaRows: { type: Array, default: () => [] },
  rewardLabel: { type: String, default: '' },
  rewardText: { type: String, default: '' },
})
</script>

<style scoped>
.mission-card {
  border-radius: 20px;
  background: linear-gradient(
    145deg,
    rgba(var(--v-theme-secondary), 0.08),
    rgba(var(--v-theme-surface), 0.95)
  );
  border: 1px solid rgba(var(--v-theme-on-surface), 0.06);
}
.mission-list {
  margin: 0;
  list-style: none;
}
.mission-list li + li {
  margin-top: 0.5rem;
}
.mission-why {
  padding: 0.75rem 1rem;
  border-radius: 12px;
  background: rgba(var(--v-theme-on-surface), 0.04);
}
.mission-meta-row {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.35rem 0;
  border-bottom: 1px solid rgba(var(--v-theme-on-surface), 0.06);
}
.mission-meta-row:last-child {
  border-bottom: none;
}
.mission-meta-label {
  font-size: 0.875rem;
  color: rgba(var(--v-theme-on-surface), 0.65);
}
.mission-meta-value {
  font-size: 0.875rem;
  font-weight: 600;
  text-align: end;
}
.mission-reward {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  padding-top: 0.5rem;
}
.min-width-0 {
  min-width: 0;
}
</style>
