<template>
  <section :class="rootClasses" :aria-label="ariaLabel">
    <header v-if="title || $slots.toolbar" class="tds-workspace__toolbar">
      <slot name="toolbar">
        <div class="tds-workspace__toolbar-row">
          <div>
            <h2 v-if="title" class="tds-workspace__toolbar-title">{{ title }}</h2>
            <p v-if="meta" class="tds-workspace__toolbar-meta">{{ meta }}</p>
          </div>
          <div v-if="$slots.actions" class="tds-workspace__toolbar-actions">
            <slot name="actions" />
          </div>
        </div>
      </slot>
    </header>

    <div :class="bodyClasses">
      <slot />
    </div>

    <footer v-if="$slots.footer" class="tds-workspace__footer">
      <slot name="footer" />
    </footer>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: { type: String, default: '' },
  meta: { type: String, default: '' },
  flush: { type: Boolean, default: false },
  ariaLabel: { type: String, default: '' },
})

const rootClasses = computed(() => ['tds-scope', 'tds-workspace'])

const bodyClasses = computed(() => [
  'tds-workspace__body',
  props.flush && 'tds-workspace__body--flush',
])
</script>
