<template>
  <section class="mb-8">
    <div class="d-flex align-center justify-space-between mb-3 flex-wrap gap-2">
      <div class="d-flex align-center gap-2">
        <v-icon color="primary">mdi-message-text-outline</v-icon>
        <h3 class="text-h6 font-weight-bold mb-0">{{ t('parent.messaging.title') }}</h3>
      </div>
      <v-btn
        variant="tonal"
        color="primary"
        size="small"
        rounded="lg"
        :to="ROUTES.PARENT_MESSAGES"
      >
        {{ t('parent.messaging.openMessages') }}
      </v-btn>
    </div>

    <v-card class="glass-card pa-4" variant="flat">
      <v-progress-linear v-if="loading" indeterminate color="primary" class="mb-2" />
      <template v-else-if="summary">
        <v-row dense class="mb-3">
          <v-col cols="6">
            <div class="metric-card text-center pa-3">
              <div class="text-h5 font-weight-bold text-primary">{{ summary.total_teachers }}</div>
              <div class="text-caption text-medium-emphasis">{{ t('parent.messaging.teachers') }}</div>
            </div>
          </v-col>
          <v-col cols="6">
            <div class="metric-card text-center pa-3">
              <div class="text-h5 font-weight-bold" :class="summary.total_unread ? 'text-error' : ''">
                {{ summary.total_unread }}
              </div>
              <div class="text-caption text-medium-emphasis">{{ t('parent.messaging.unread') }}</div>
            </div>
          </v-col>
        </v-row>
        <div v-if="summary.recent?.length" class="text-caption text-medium-emphasis mb-2">
          {{ t('parent.messaging.recentChats') }}
        </div>
        <v-list v-if="summary.recent?.length" density="compact" class="bg-transparent pa-0">
          <v-list-item
            v-for="item in summary.recent"
            :key="item.thread_id"
            rounded="lg"
            class="mb-1"
            :to="{ path: ROUTES.PARENT_MESSAGES, query: { thread: item.thread_id } }"
          >
            <template #prepend>
              <TeacherAvatar
                :name="item.teacher_name"
                :image-url="item.teacher_image_url"
                :size="36"
              />
            </template>
            <v-list-item-title class="text-body-2 font-weight-medium">
              {{ item.teacher_name }}
            </v-list-item-title>
            <v-list-item-subtitle class="text-caption">
              {{ item.subject_name }} — {{ item.student_name }}
            </v-list-item-subtitle>
            <template #append>
              <v-chip v-if="item.unread_count" size="x-small" color="error" variant="flat">
                {{ item.unread_count }}
              </v-chip>
            </template>
          </v-list-item>
        </v-list>
        <p v-else class="text-caption text-medium-emphasis mb-0">
          {{ t('parent.messaging.empty') }}
        </p>
      </template>
    </v-card>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { fetchParentMessagingSummary } from '../../api/parentMessaging.js'
import { ROUTES } from '../../constants/app.js'
import TeacherAvatar from '../onboarding/TeacherAvatar.vue'

const { t } = useI18n()

const loading = ref(true)
const summary = ref(null)

onMounted(async () => {
  try {
    summary.value = await fetchParentMessagingSummary()
  } catch {
    summary.value = { total_teachers: 0, total_unread: 0, recent: [] }
  } finally {
    loading.value = false
  }
})
</script>
