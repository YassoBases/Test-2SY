<template>

  <AppSection

    class="teacher-home__section teacher-home__section--activity"

    :eyebrow="$t('teacher.dashboard.recentUpdates')"

    :title="$t('teacher.analytics.recentActivity')"

    :subtitle="$t('teacher.dashboard.recentActivityDesc')"

    spacing="sm"

    :divider="false"

  >

    <div class="teacher-activity-panel glass-card">

      <div v-if="items.length" class="teacher-activity" role="list">

        <div

          v-for="(item, idx) in items"

          :key="item.id || idx"

          class="teacher-activity__item"

          role="listitem"

        >

          <span class="teacher-activity__marker" aria-hidden="true">

            <v-icon size="12">{{ item.icon || 'mdi-circle-small' }}</v-icon>

          </span>

          <div class="teacher-activity__content">

            <div class="teacher-activity__text">{{ item.title }}</div>

            <div v-if="item.time" class="teacher-activity__time">{{ item.time }}</div>

          </div>

        </div>

      </div>

      <p v-else class="teacher-activity__empty mb-0">

        {{ $t('teacher.dashboard.noActivity') }}

      </p>

    </div>

  </AppSection>

</template>



<script setup>
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import { AppSection } from '../../ui/index.js'



defineProps({

  items: { type: Array, default: () => [] },

})

</script>


