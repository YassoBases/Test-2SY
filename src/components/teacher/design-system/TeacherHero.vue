<template>

  <header :class="heroClasses">

    <div class="tds-hero__main">

      <span v-if="eyebrow" class="tds-hero__eyebrow">{{ eyebrow }}</span>



      <h1 class="tds-hero__title">{{ title }}</h1>



      <p v-if="subtitle" class="tds-hero__subtitle">{{ subtitle }}</p>



      <div v-if="$slots.meta" class="tds-hero__meta">

        <slot name="meta" />

      </div>

    </div>



    <div v-if="$slots.actions" class="tds-hero__actions">

      <slot name="actions" />

    </div>

  </header>

</template>



<script setup>

import { computed } from 'vue'



const props = defineProps({

  eyebrow: { type: String, default: '' },

  title: { type: String, required: true },

  subtitle: { type: String, default: '' },

  variant: {

    type: String,

    default: 'page',

    validator: (v) => ['page', 'compact'].includes(v),

  },

})



const heroClasses = computed(() => [

  'tds-scope',

  'tds-hero',

  props.variant === 'compact' && 'tds-hero--compact',

])

</script>

