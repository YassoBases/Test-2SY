<template>

  <TeacherAvatar

    :name="displayName"

    :image-url="imageUrl"

    :size="size"

    class="flex-shrink-0"

  />

</template>



<script setup>

import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import TeacherAvatar from '../onboarding/TeacherAvatar.vue'

const { t } = useI18n()


const props = defineProps({

  name: { type: String, default: '' },

  imageUrl: { type: String, default: null },

  size: { type: [Number, String], default: 42 },

})



const displayName = computed(() => {

  const trimmed = (props.name || '').trim()

  return trimmed || t('student.common.teacher')

})

</script>


