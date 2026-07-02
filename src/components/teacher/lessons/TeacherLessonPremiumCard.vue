<template>
  <article class="lesson-premium-card">
    <div class="lesson-premium-card__menu">
      <v-menu
        location="bottom end"
        transition="lesson-menu-transition"
        :close-on-content-click="true"
      >
        <template #activator="{ props: menuProps }">
          <v-btn
            v-bind="menuProps"
            icon
            variant="text"
            size="x-small"
            class="lesson-premium-card__menu-btn"
            :aria-label="$t('teacher.actions.manageLesson')"
          >
            <v-icon size="16">mdi-dots-vertical</v-icon>
          </v-btn>
        </template>

        <v-list class="lesson-workspace-menu" density="compact" nav>
          <v-list-item
            v-if="previewTo"
            :to="previewTo"
            prepend-icon="mdi-eye-outline"
            :title="$t('common.edit')"
          />
          <v-list-item
            v-if="editTo"
            :to="editTo"
            prepend-icon="mdi-pencil-outline"
            :title="$t('common.edit')"
          />
          <v-list-item
            v-if="showAi"
            prepend-icon="mdi-robot-outline"
            :title="$t('teacher.lessons.aiToolsTitle')"
            :disabled="aiLoading"
            @click="$emit('ai')"
          />
        </v-list>
      </v-menu>
    </div>

    <div class="lesson-premium-card__main">
      <h3 class="lesson-premium-card__title">{{ lesson.title }}</h3>

      <p v-if="lastUpdated" class="lesson-premium-card__updated">
        {{ $t('teacher.labels.lastEditAt', { date: lastUpdated }) }}
      </p>

      <p class="lesson-premium-card__meta">
        <span class="lesson-premium-card__meta-type">
          <v-icon :icon="typeMeta.icon" size="14" class="lesson-premium-card__meta-icon" />
          {{ typeMeta.label }}
        </span>
        <span class="lesson-premium-card__meta-sep" aria-hidden="true">•</span>
        <span
          class="lesson-premium-card__meta-status"
          :class="`lesson-premium-card__meta-status--${statusMeta.tone}`"
        >
          {{ statusMeta.label }}
        </span>
      </p>
    </div>

    <div class="lesson-premium-card__progress">
      <p class="lesson-premium-card__progress-title">{{ $t('teacher.lessons.studentCompletion') }}</p>
      <p v-if="completion.total > 0" class="lesson-premium-card__progress-detail">
        {{ $t('teacher.lessons.fromOfStudents', { completed: completion.completed, total: completion.total }) }}
      </p>
      <p v-else class="lesson-premium-card__progress-detail">{{ $t('teacher.lessons.noActiveStudents') }}</p>
      <div class="lesson-premium-card__progress-row">
        <div class="lesson-premium-card__progress-track" aria-hidden="true">
          <div
            class="lesson-premium-card__progress-fill"
            :style="{ width: `${completion.percent}%` }"
          />
        </div>
        <span class="lesson-premium-card__progress-percent">{{ completion.percent }}%</span>
      </div>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import {
  formatLessonMetaDate,
  lessonCompletionFromPercent,
  lessonStatusMeta,
  lessonTypeMeta,
} from '../../../utils/lessonWorkspaceDisplay.js'

const props = defineProps({
  lesson: { type: Object, required: true },
  activeStudents: { type: Number, default: 0 },
  previewTo: { type: [Object, String], default: null },
  editTo: { type: [Object, String], default: null },
  showAi: { type: Boolean, default: false },
  aiLoading: { type: Boolean, default: false },
})

defineEmits(['ai'])

const lastUpdated = computed(() =>
  formatLessonMetaDate(props.lesson?.updated_at || props.lesson?.created_at),
)
const typeMeta = computed(() => lessonTypeMeta(props.lesson?.content_type, props.lesson?.content_type_label))
const statusMeta = computed(() => lessonStatusMeta(props.lesson?.status))
const completion = computed(() =>
  lessonCompletionFromPercent(props.lesson?.completion_percent, props.activeStudents),
)
</script>
