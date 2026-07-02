<template>
  <v-card class="glass-card pa-4 pa-md-6 mb-6" variant="flat">
    <h3 class="text-h6 font-weight-bold mb-1 d-flex align-center gap-2">
      <v-icon color="primary">mdi-account-supervisor</v-icon>
      {{ t('student.parents.title') }}
    </h3>
    <p class="text-body-2 text-medium-emphasis mb-4">
      {{ t('student.parents.subtitle') }}
    </p>

    <v-alert v-if="error" type="error" variant="tonal" class="mb-4 rounded-lg">{{ error }}</v-alert>

    <div v-if="loading" class="py-6 text-center">
      <v-progress-circular indeterminate color="primary" size="32" />
    </div>

    <v-alert v-else-if="!parents.length" type="info" variant="tonal" class="rounded-lg">
      {{ t('student.parents.empty') }}
    </v-alert>

    <template v-else>
      <v-row class="mb-4">
        <v-col cols="6" sm="4">
          <v-sheet class="summary-tile pa-3 text-center rounded-lg" variant="flat">
            <div class="text-h6 font-weight-bold">{{ summary.total_linked }}</div>
            <div class="text-caption text-medium-emphasis">{{ t('student.parents.summary.total') }}</div>
          </v-sheet>
        </v-col>
        <v-col cols="6" sm="4">
          <v-sheet class="summary-tile pa-3 text-center rounded-lg" variant="flat">
            <div class="text-h6 font-weight-bold text-success">{{ summary.active_linked }}</div>
            <div class="text-caption text-medium-emphasis">{{ t('student.parents.summary.recent') }}</div>
          </v-sheet>
        </v-col>
      </v-row>

      <div class="d-flex flex-column gap-3">
        <v-card
          v-for="p in parents"
          :key="p.parent_id"
          class="parent-row pa-4"
          variant="flat"
        >
          <div class="d-flex flex-column flex-sm-row gap-3 align-sm-center">
            <v-avatar color="primary" variant="tonal" size="44">
              <span class="text-body-1 font-weight-bold">{{ p.display_name?.charAt(0) || t('student.parents.defaultInitial') }}</span>
            </v-avatar>
            <div class="flex-grow-1 min-width-0">
              <div class="d-flex flex-wrap align-center gap-2 mb-1">
                <span class="text-subtitle-1 font-weight-bold text-truncate">{{ p.display_name }}</span>
                <v-chip size="x-small" variant="tonal" color="primary" label>
                  {{ relationshipLabelAr(p.relationship_label) }}
                </v-chip>
                <v-chip
                  v-if="p.is_active"
                  size="x-small"
                  color="success"
                  variant="flat"
                  label
                >
                  {{ t('student.parents.status.active') }}
                </v-chip>
              </div>
              <div class="text-caption text-medium-emphasis d-flex flex-wrap gap-x-4 gap-y-1">
                <span>
                  <v-icon size="14" class="me-1">mdi-link</v-icon>
                  {{ t('student.parents.linkedAt', { date: formatSubscriptionDate(p.linked_at) }) }}
                </span>
                <span v-if="p.last_viewed_at">
                  <v-icon size="14" class="me-1">mdi-eye</v-icon>
                  {{ t('student.parents.lastSeen', { date: formatSubscriptionDate(p.last_viewed_at) }) }}
                </span>
                <span v-else class="text-medium-emphasis">{{ t('student.parents.noActivity') }}</span>
              </div>
            </div>
          </div>
        </v-card>
      </div>
    </template>
  </v-card>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { fetchLinkedParents } from '../../api/student.js'
import { getErrorMessage } from '../../api/client.js'
import { formatSubscriptionDate, relationshipLabelAr } from '../../utils/subscriptionStatus.js'

const { t } = useI18n()
const loading = ref(false)
const error = ref('')
const parents = ref([])
const summary = ref({ total_linked: 0, active_linked: 0 })

onMounted(load)

async function load() {
  loading.value = true
  error.value = ''
  try {
    const data = await fetchLinkedParents()
    parents.value = data.parents || []
    summary.value = data.summary || { total_linked: 0, active_linked: 0 }
  } catch (err) {
    error.value = getErrorMessage(err, t('student.parents.errors.load'))
    parents.value = []
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.summary-tile {
  background: rgba(var(--v-theme-on-surface), 0.04);
  border: 1px solid rgba(var(--v-theme-on-surface), 0.08);
}

.parent-row {
  border: 1px solid rgba(var(--v-theme-on-surface), 0.08);
  border-radius: 12px;
  background: rgba(var(--v-theme-surface), 0.35);
}

.min-width-0 {
  min-width: 0;
}
</style>
