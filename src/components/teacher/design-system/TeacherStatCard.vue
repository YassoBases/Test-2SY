<template>

  <article :class="cardClasses">

    <div class="tds-stat-card__main">

      <p v-if="label" class="tds-stat-card__label">{{ label }}</p>

      <p class="tds-stat-card__value" :dir="valueDir">

        <slot>{{ value }}</slot>

      </p>

      <p v-if="subtitle || $slots.subtitle" class="tds-stat-card__subtitle">

        <slot name="subtitle">{{ subtitle }}</slot>

      </p>

    </div>



    <div v-if="icon" class="tds-stat-card__icon" :class="iconToneClass">

      <v-icon :icon="icon" :size="iconSize" />

    </div>

  </article>

</template>



<script setup>

import { computed } from 'vue'



const props = defineProps({

  label: { type: String, default: '' },

  value: { type: [String, Number], default: '' },

  subtitle: { type: String, default: '' },

  icon: { type: String, default: '' },

  iconSize: { type: [Number, String], default: 24 },

  tone: {

    type: String,

    default: 'primary',

    validator: (v) => ['primary', 'secondary', 'success', 'warning', 'error'].includes(v),

  },

  interactive: { type: Boolean, default: false },

  valueDir: { type: String, default: 'auto' },

  /** Compact layout (summary/KPI strip). Default is analytics padding. */

  compact: { type: Boolean, default: false },

})



const cardClasses = computed(() => [

  'tds-scope',

  'tds-stat-card',

  props.compact && 'tds-stat-card--compact',

  props.interactive && 'tds-stat-card--interactive',

])



const iconToneClass = computed(() => `tds-stat-card__icon--${props.tone}`)

</script>

