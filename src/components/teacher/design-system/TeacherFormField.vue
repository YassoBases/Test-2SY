<template>

  <div :class="fieldClasses">

    <!--

      Supported modes:

      - plain: external label + outlined control (lesson / quiz flows)

      - floating: Vuetify floating label + optional size tuning (dialog forms)

    -->

    <div v-if="mode === 'plain' && (label || $slots['header-actions'])" class="tds-form__field-header">

      <span v-if="label" class="tds-form__field-label">{{ label }}</span>

      <slot name="header-actions" />

    </div>



    <p v-if="mode === 'plain' && (helperBefore || $slots['helper-before'])" class="tds-form__field-helper">

      <slot name="helper-before">{{ helperBefore }}</slot>

    </p>



    <slot />



    <TeacherFormHint v-if="hint || $slots.hint" :variant="hintVariant">

      <slot name="hint">{{ hint }}</slot>

    </TeacherFormHint>

  </div>

</template>



<script setup>

import { computed } from 'vue'

import TeacherFormHint from './TeacherFormHint.vue'



const props = defineProps({

  /**

   * plain — explicit label above control (lesson / quiz editors)

   * floating — Vuetify floating labels (dialog forms)

   */

  mode: {

    type: String,

    default: 'floating',

    validator: (v) => ['plain', 'floating'].includes(v),

  },

  /** Size tuning when mode is floating. */

  size: {

    type: String,

    default: '',

    validator: (v) => ['', 'hero', 'description', 'secondary'].includes(v),

  },

  label: { type: String, default: '' },

  hint: { type: String, default: '' },

  helperBefore: { type: String, default: '' },

  hintVariant: {

    type: String,

    default: 'info',

    validator: (v) => ['info', 'warning', 'error', 'success'].includes(v),

  },

})



const fieldClasses = computed(() => [

  'tds-form__field',

  props.mode === 'plain' && 'tds-form__field--plain',

  props.mode === 'floating' && props.size && `tds-form__field--${props.size}`,

])

</script>

