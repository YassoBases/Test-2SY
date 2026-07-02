<template>
  <article class="lesson-workspace-row">
    <div class="lesson-workspace-row__content">
      <h3 class="lesson-workspace-row__title">{{ lesson.title }}</h3>

      <p v-if="metaDate" class="lesson-workspace-row__meta">
        <span class="lesson-workspace-row__meta-label">{{ $t('teacher.lessons.addedOn') }}</span>
        {{ metaDate }}
      </p>
      <p v-if="lesson.course_label" class="lesson-workspace-row__meta">{{ lesson.course_label }}</p>

      <div class="lesson-workspace-row__badges">
        <TeacherLessonStatusBadge :status="lesson.status" />
        <TeacherLessonTypeChip
          :content-type="lesson.content_type"
          :label="lesson.content_type_label"
        />
      </div>
    </div>

    <div class="lesson-workspace-row__aside">
      <TeacherLessonProgressMini
        :percent="lesson.completion_percent"
        variant="row"
        :label="$t('teacher.lessons.studentCompletion')"
      />

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
            class="lesson-workspace-row__menu-btn"
            :aria-label="$t('teacher.actions.manageLesson')"
          >
            <v-icon size="18">mdi-dots-vertical</v-icon>
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
  </article>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import TeacherLessonProgressMini from './TeacherLessonProgressMini.vue'
import TeacherLessonStatusBadge from './TeacherLessonStatusBadge.vue'
import TeacherLessonTypeChip from './TeacherLessonTypeChip.vue'
import { formatLessonMetaDate } from '../../../utils/lessonWorkspaceDisplay.js'

const props = defineProps({
  lesson: { type: Object, required: true },
  previewTo: { type: [Object, String], default: null },
  editTo: { type: [Object, String], default: null },
  showAi: { type: Boolean, default: false },
  aiLoading: { type: Boolean, default: false },
})

defineEmits(['ai'])

const metaDate = computed(() => formatLessonMetaDate(props.lesson?.created_at))
</script>
