<template>

  <div :class="shellClasses" dir="rtl">

    <header v-if="$slots.header || $slots['header-actions']" :class="headerClasses">

      <div :class="headerInnerClasses">

        <div v-if="$slots.header" class="tds-workspace-shell__header-main">

          <slot name="header" />

        </div>

        <div v-if="$slots['header-actions']" class="tds-workspace-shell__header-actions">

          <slot name="header-actions" />

        </div>

      </div>

    </header>



    <main :class="mainClasses">

      <div :class="bodyClasses">

        <slot />

      </div>

    </main>



    <TeacherWorkspaceFooter

      v-if="$slots.footer"

      :sticky="footerSticky"

      :width="footerWidth"

    >

      <slot name="footer" />

    </TeacherWorkspaceFooter>

  </div>

</template>



<script setup>

import { computed } from 'vue'

import TeacherWorkspaceFooter from './TeacherWorkspaceFooter.vue'



const props = defineProps({

  mode: {

    type: String,

    default: 'page',

    validator: (v) => ['page', 'fullscreen', 'dialog'].includes(v),

  },

})



const shellClasses = computed(() => [

  'tds-scope',

  'tds-workspace-shell',

  `tds-workspace-shell--${props.mode}`,

])



const headerClasses = computed(() => ['tds-workspace-shell__header'])



const headerInnerClasses = computed(() => [

  'tds-workspace-shell__header-inner',

  props.mode === 'fullscreen' && 'tds-workspace-shell__header-inner--fullscreen',

  props.mode === 'dialog' && 'tds-workspace-shell__header-inner--dialog',

])



const mainClasses = computed(() => ['tds-workspace-shell__main'])



const bodyClasses = computed(() => [

  'tds-workspace-shell__body',

  props.mode === 'fullscreen' && 'tds-workspace-shell__body--fullscreen',

])



const footerSticky = computed(() => props.mode === 'page')



const footerWidth = computed(() => {

  if (props.mode === 'page') return 'page'

  if (props.mode === 'fullscreen') return 'fullscreen'

  return 'fluid'

})

</script>

