<template>
  <div class="course-image-upload">
    <div class="course-image-upload__head">
      <span class="course-image-upload__label">{{ label }}</span>
      <span class="course-image-upload__hint">{{ hint }}</span>
    </div>

    <div
      v-if="!previewUrl"
      class="course-image-upload__zone"
      role="button"
      tabindex="0"
      :aria-label="label"
      @click="triggerPick"
      @keydown.enter.space.prevent="triggerPick"
    >
      <span class="course-image-upload__icon" aria-hidden="true">
        <v-icon :icon="icon" size="40" />
      </span>
      <p class="course-image-upload__cta">{{ $t('teacher.actions.selectImage') }}</p>
      <p class="course-image-upload__formats">{{ $t('teacher.course.imageFormats') }}</p>
    </div>

    <div v-else class="course-image-upload__preview">
      <img :src="previewUrl" :alt="label" class="course-image-upload__img" />
      <div class="course-image-upload__preview-actions">
        <v-btn
          size="small"
          variant="tonal"
          rounded="lg"
          prepend-icon="mdi-image-edit-outline"
          @click="triggerPick"
        >
          {{ $t('common.update') }}
        </v-btn>
        <v-btn
          size="small"
          variant="text"
          color="error"
          rounded="lg"
          prepend-icon="mdi-delete-outline"
          @click="clear"
        >
          {{ $t('common.delete') }}
        </v-btn>
      </div>
    </div>

    <input
      ref="fileInput"
      type="file"
      accept="image/*"
      class="d-none"
      @change="onPick"
    />
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()


const props = defineProps({
  modelValue: { type: [File, Object, Array], default: null },
  label: { type: String, required: true },
  hint: { type: String, default: '' },
  icon: { type: String, default: 'mdi-image-outline' },
})

const emit = defineEmits(['update:modelValue'])

const fileInput = ref(null)
const objectUrl = ref('')

const file = computed(() => {
  const v = props.modelValue
  if (!v) return null
  return Array.isArray(v) ? v[0] : v
})

const previewUrl = computed(() => objectUrl.value)

function revokeUrl() {
  if (objectUrl.value) {
    URL.revokeObjectURL(objectUrl.value)
    objectUrl.value = ''
  }
}

function setPreview(f) {
  revokeUrl()
  if (f) objectUrl.value = URL.createObjectURL(f)
}

watch(file, (f) => setPreview(f), { immediate: true })

onBeforeUnmount(revokeUrl)

function triggerPick() {
  fileInput.value?.click()
}

function onPick(e) {
  const picked = e.target.files?.[0]
  if (!picked) return
  emit('update:modelValue', picked)
  e.target.value = ''
}

function clear() {
  emit('update:modelValue', null)
  if (fileInput.value) fileInput.value.value = ''
}
</script>
