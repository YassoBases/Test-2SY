<template>
  <div class="tds-scope tds-table-wrap">
    <v-table :class="tableClasses" :density="density" :hover="hover">
      <slot />
    </v-table>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  density: {
    type: String,
    default: 'comfortable',
    validator: (v) => ['default', 'comfortable', 'compact'].includes(v),
  },
  hover: { type: Boolean, default: true },
})

const tableClasses = computed(() => ['tds-table', 'bg-transparent'])
</script>
