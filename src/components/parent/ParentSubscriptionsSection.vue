<template>
  <v-card class="glass-card pa-4 pa-md-6 mb-6" variant="flat">
    <h3 class="text-h6 font-weight-bold mb-1 d-flex align-center gap-2">
      <v-icon color="secondary">mdi-credit-card-clock-outline</v-icon>
      {{ t('parent.subscriptions.title') }}
    </h3>
    <p class="text-body-2 text-medium-emphasis mb-4">
      {{ t('parent.subscriptions.hint') }}
    </p>

    <v-alert v-if="!items.length" type="info" variant="tonal" class="rounded-lg">
      {{ t('parent.subscriptions.empty') }}
    </v-alert>

    <div v-else class="d-flex flex-column gap-3">
      <v-card
        v-for="sub in items"
        :key="sub.course_id"
        class="sub-row pa-4"
        variant="flat"
      >
        <div class="d-flex flex-column flex-sm-row justify-space-between gap-2">
          <div class="min-width-0">
            <div class="text-subtitle-1 font-weight-bold text-truncate">{{ sub.course_title }}</div>
            <div class="text-caption text-medium-emphasis">{{ sub.subject_name }}</div>
          </div>
          <v-chip
            :color="subscriptionStatusColor(sub.subscription_status)"
            size="small"
            variant="flat"
            label
            class="align-self-start"
          >
            {{ statusLabel(sub.subscription_status) }}
          </v-chip>
        </div>
        <div class="text-caption text-medium-emphasis mt-2 d-flex flex-wrap gap-x-4 gap-y-1">
          <span v-if="sub.activated_at">{{ t('parent.subscriptions.started', { date: formatSubscriptionDate(sub.activated_at) }) }}</span>
          <span v-if="sub.expires_at">{{ t('parent.subscriptions.expires', { date: formatSubscriptionDate(sub.expires_at) }) }}</span>
          <span v-if="sub.days_until_expiry != null && sub.subscription_status !== 'expired'">
            {{ t('parent.subscriptions.daysRemaining', { n: sub.days_until_expiry }) }}
          </span>
        </div>
      </v-card>
    </div>
  </v-card>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import {
  formatSubscriptionDate,
  subscriptionStatusColor,
} from '../../utils/subscriptionStatus.js'

defineProps({
  items: { type: Array, default: () => [] },
})

const { t } = useI18n()

function statusLabel(status) {
  const key = `parent.subscriptions.status.${status}`
  const translated = t(key)
  return translated !== key ? translated : status || t('parent.common.emDash')
}
</script>

<style scoped>
.sub-row {
  border: 1px solid rgba(var(--v-theme-on-surface), 0.08);
  border-radius: 12px;
  background: rgba(var(--v-theme-surface), 0.35);
}

.min-width-0 {
  min-width: 0;
}
</style>
