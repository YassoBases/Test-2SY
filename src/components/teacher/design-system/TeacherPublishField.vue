<template>

  <div :class="rootClasses">

    <p v-if="hint && mode === 'inline'" class="tds-publish-field__hint">{{ hint }}</p>



    <template v-if="mode === 'stack'">

      <p v-if="label" class="tds-publish-field__label">{{ label }}</p>

      <p v-if="description" class="tds-publish-field__description">{{ description }}</p>

      <div class="tds-publish-field__control">

        <v-switch

          :model-value="modelValue"

          color="secondary"

          hide-details

          :density="switchDensity"

          @update:model-value="$emit('update:modelValue', $event)"

        />

      </div>

    </template>



    <template v-else>

      <div class="tds-publish-field__inline">

        <p v-if="label" class="tds-publish-field__label">{{ label }}</p>

        <v-switch

          :model-value="modelValue"

          color="secondary"

          hide-details

          :density="switchDensity"

          @update:model-value="$emit('update:modelValue', $event)"

        />

      </div>

    </template>

  </div>

</template>



<script setup>

import { computed } from 'vue'



const props = defineProps({

  modelValue: { type: Boolean, default: false },

  label: { type: String, default: '' },

  description: { type: String, default: '' },

  hint: { type: String, default: '' },

  mode: {

    type: String,

    default: 'stack',

    validator: (v) => ['stack', 'inline'].includes(v),

  },

  switchDensity: { type: String, default: 'comfortable' },

})



defineEmits(['update:modelValue'])



const rootClasses = computed(() => [

  'tds-publish-field',

  props.mode === 'stack' && 'tds-publish-field--stack',

  props.mode === 'inline' && 'tds-publish-field--inline',

])

</script>

