<template>
  <section class="glass-card pa-5 pa-md-6 spk-package-panel" aria-labelledby="spk-pkg-material-title">
    <div class="text-overline text-medium-emphasis mb-2">
      {{ t('student.languages.speakingJourney.packageLesson.section.reading') }}
    </div>
    <div class="d-flex flex-wrap align-center gap-2 mb-2">
      <h3 id="spk-pkg-material-title" class="text-h6 font-weight-bold mb-0">
        {{ material?.title || t('student.languages.speakingJourney.packageLesson.materialFallback') }}
      </h3>
      <v-chip size="small" variant="tonal" color="primary">
        {{ kindLabel }}
      </v-chip>
    </div>
    <p v-if="settingLine" class="text-body-2 text-medium-emphasis mb-4">
      {{ settingLine }}
    </p>

    <div class="spk-material-body mb-5" :data-kind="material?.kind || 'custom'">
      <template v-if="isDialogue">
        <div
          v-for="(block, idx) in blocks"
          :key="block.block_ref || idx"
          class="spk-turn"
          :class="{ 'spk-turn--alt': idx % 2 === 1 }"
        >
          <div v-if="block.speaker" class="spk-turn__speaker">{{ block.speaker }}</div>
          <p class="spk-turn__text mb-0">{{ block.text }}</p>
        </div>
      </template>
      <template v-else-if="isMenu">
        <ul class="spk-menu-list">
          <li v-for="(block, idx) in blocks" :key="block.block_ref || idx">
            {{ block.text }}
          </li>
        </ul>
      </template>
      <template v-else>
        <article class="spk-story">
          <p
            v-for="(block, idx) in blocks"
            :key="block.block_ref || idx"
            class="spk-story__beat mb-4"
            :class="{ 'spk-story__beat--heading': block.kind === 'heading' }"
          >
            {{ block.text }}
          </p>
        </article>
      </template>
    </div>

    <v-btn color="primary" size="large" class="spk-pressable" :loading="advancing" @click="$emit('continue')">
      {{ t('student.languages.speakingJourney.packageLesson.continue') }}
    </v-btn>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  material: { type: Object, default: null },
  storySpine: { type: Object, default: null },
  advancing: { type: Boolean, default: false },
})
defineEmits(['continue'])
const { t } = useI18n()

const blocks = computed(() => props.material?.body_blocks || [])
const kind = computed(() => props.material?.kind || 'custom')
const isDialogue = computed(() =>
  ['dialogue', 'whatsapp', 'conversation_transcript'].includes(kind.value),
)
const isMenu = computed(() => kind.value === 'restaurant_menu')
const kindLabel = computed(() =>
  t(`student.languages.speakingJourney.packageLesson.materialKind.${kind.value}`, kind.value),
)
const settingLine = computed(() => {
  const setting = props.storySpine?.setting || ''
  const chars = (props.storySpine?.characters || [])
    .map((c) => (typeof c === 'string' ? c : c?.name))
    .filter(Boolean)
  const parts = []
  if (setting) parts.push(setting)
  if (chars.length) parts.push(chars.join(' · '))
  return parts.join(' · ')
})
</script>

<style scoped>
.spk-story__beat {
  line-height: 1.7;
  max-width: 42rem;
}
.spk-story__beat--heading {
  font-size: 1.125rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}
</style>
