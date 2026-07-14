<template>

  <section :class="sectionClasses" :aria-labelledby="titleId">

    <header v-if="title || description || $slots.head" class="tds-form__section-head">

      <slot name="head">

        <h3 v-if="title" :id="titleId" class="tds-form__section-title">{{ title }}</h3>

        <p v-if="description" class="tds-form__section-desc">{{ description }}</p>

      </slot>

    </header>



    <div :class="bodyClasses">

      <slot />

    </div>

  </section>

</template>



<script setup>

import { computed, useId } from 'vue'



const props = defineProps({

  title: { type: String, default: '' },

  description: { type: String, default: '' },

  columns: {

    type: Number,

    default: 1,

    validator: (v) => [1, 2].includes(v),

  },

  animated: { type: Boolean, default: false },

  variant: {

    type: String,

    default: 'default',

    validator: (v) => ['default', 'lesson', 'compact'].includes(v),

  },

  stack: { type: Boolean, default: false },

})



const titleId = useId()



const sectionClasses = computed(() => [

  'tds-form__section',

  props.animated && 'tds-form__section--animated',

  props.variant === 'lesson' && 'tds-form__section--lesson',

  props.variant === 'compact' && 'tds-form__section--compact',

])



const bodyClasses = computed(() => [

  props.stack ? 'tds-form__field-stack' : 'tds-form__grid',

  !props.stack && props.columns === 2 && 'tds-form__grid--2',

])

</script>

