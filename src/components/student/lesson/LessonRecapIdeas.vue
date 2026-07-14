<template>

  <div class="lesson-recap-ideas">

    <article

      v-for="(idea, index) in displayIdeas"

      :key="`${index}-${idea.text}`"

      class="lesson-recap-ideas__card"

    >

      <v-icon :icon="idea.icon" size="20" color="secondary" class="lesson-recap-ideas__icon" />

      <p class="lesson-recap-ideas__text mb-0">{{ idea.text }}</p>

    </article>

  </div>

</template>



<script setup>

import { computed } from 'vue'



const CARD_ICONS = [

  'mdi-check-circle-outline',

  'mdi-lightbulb-on-outline',

  'mdi-bookmark-outline',

  'mdi-star-outline',

  'mdi-eye-outline',

]



const props = defineProps({

  ideas: { type: Array, default: () => [] },

  maxCards: { type: Number, default: 5 },

})



function shorten(text, max = 140) {

  const trimmed = (text || '').trim()

  if (trimmed.length <= max) return trimmed

  return `${trimmed.slice(0, max - 1)}…`

}



const displayIdeas = computed(() =>

  (props.ideas || [])

    .slice(0, props.maxCards)

    .map((point, index) => ({

      text: shorten(point),

      icon: CARD_ICONS[index % CARD_ICONS.length],

    })),

)

</script>

