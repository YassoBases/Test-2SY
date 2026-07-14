<template>
  <div class="lesson-concept-recap">
    <div class="lesson-concept-recap__teacher d-flex align-center gap-2 mb-3">
      <TeacherAvatar
        :name="teacherName"
        :image-url="teacherImageUrl"
        :size="36"
        class="flex-shrink-0"
      />
      <p class="lesson-concept-recap__framing text-body-2 mb-0">
        {{ t('student.lesson.concepts.framing') }}
      </p>
    </div>

    <div class="lesson-concept-recap__chips d-flex flex-wrap gap-2">
      <v-menu
        v-for="concept in concepts"
        :key="concept"
        location="bottom"
        :close-on-content-click="true"
      >
        <template #activator="{ props: menuProps }">
          <button
            type="button"
            class="lesson-concept-recap__chip"
            v-bind="menuProps"
            :disabled="disabled"
          >
            {{ concept }}
            <v-icon size="14" class="lesson-concept-recap__chip-icon">mdi-chevron-down</v-icon>
          </button>
        </template>
        <v-list density="compact" class="lesson-concept-recap__menu py-1">
          <v-list-item
            v-for="item in actionItems"
            :key="item.action"
            :prepend-icon="item.icon"
            :title="item.label"
            rounded="lg"
            @click="emitAction(concept, item.action)"
          />
        </v-list>
      </v-menu>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import TeacherAvatar from '../../onboarding/TeacherAvatar.vue'

const { t } = useI18n()

defineProps({
  concepts: { type: Array, default: () => [] },
  teacherName: { type: String, default: '' },
  teacherImageUrl: { type: String, default: null },
  disabled: { type: Boolean, default: false },
})

const emit = defineEmits(['concept-action'])

const actionItems = computed(() => [
  { action: 'explain', label: t('student.lesson.concepts.explain'), icon: 'mdi-text-box-outline' },
  { action: 'example', label: t('student.lesson.concepts.example'), icon: 'mdi-lightbulb-outline' },
  { action: 'quiz', label: t('student.lesson.concepts.quiz'), icon: 'mdi-clipboard-check-outline' },
  { action: 'ask', label: t('student.lesson.concepts.ask'), icon: 'mdi-message-text-outline' },
])

function emitAction(concept, action) {
  emit('concept-action', { concept, action })
}
</script>
