<template>

  <footer :class="footerClasses">

    <div :class="innerClasses">

      <slot />

    </div>

  </footer>

</template>



<script setup>

import { computed } from 'vue'



const props = defineProps({

  sticky: { type: Boolean, default: false },

  /** Matches parent shell width: page (760), fullscreen (840), dialog (fluid). */

  width: {

    type: String,

    default: 'fluid',

    validator: (v) => ['fluid', 'page', 'fullscreen'].includes(v),

  },

})



const footerClasses = computed(() => [

  'tds-workspace-footer',

  props.sticky && 'tds-workspace-footer--sticky',

])



const innerClasses = computed(() => [

  'tds-workspace-footer__inner',

  props.width === 'page' && 'tds-workspace-footer__inner--page',

  props.width === 'fullscreen' && 'tds-workspace-footer__inner--fullscreen',

])

</script>

