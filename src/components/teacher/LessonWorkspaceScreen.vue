<template>
  <component :is="teleport ? 'Teleport' : 'div'" :to="teleport ? 'body' : undefined">
    <div
      v-if="open"
      class="lesson-workspace-screen"
      :class="[
        { 'lesson-workspace-screen--layered': layered, 'lesson-workspace-screen--inline': !teleport },
        workspaceClass,
      ]"
      dir="rtl"
    >
      <header v-if="title || eyebrow || subtitle" class="lesson-workspace-header">
        <div class="lesson-workspace-header-inner">
          <div>
            <p v-if="eyebrow" class="text-caption text-medium-emphasis mb-1">{{ eyebrow }}</p>
            <h2 class="text-h5 font-weight-bold mb-0">{{ title }}</h2>
            <p v-if="subtitle" class="text-body-2 text-medium-emphasis mb-0 mt-1">{{ subtitle }}</p>
          </div>
          <v-btn variant="text" prepend-icon="mdi-close" :disabled="busy" @click="$emit('close')">
            {{ $t('common.close') }}
          </v-btn>
        </div>
      </header>

      <header v-else class="lesson-workspace-header lesson-workspace-header--minimal">
        <div class="lesson-workspace-header-inner">
          <div />
          <v-btn variant="text" prepend-icon="mdi-close" :disabled="busy" @click="$emit('close')">
            {{ $t('common.close') }}
          </v-btn>
        </div>
      </header>

      <main class="lesson-workspace-main">
        <slot />
      </main>

      <footer v-if="$slots.footer" class="lesson-workspace-footer">
        <div class="lesson-workspace-footer-inner">
          <slot name="footer" />
        </div>
      </footer>
    </div>
  </component>
</template>

<script setup>
import { onUnmounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()


const props = defineProps({
  open: { type: Boolean, default: false },
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' },
  eyebrow: { type: String, default: '' },
  busy: { type: Boolean, default: false },
  layered: { type: Boolean, default: false },
  /** When true, render inline instead of Teleport (for modal-only use). */
  teleport: { type: Boolean, default: true },
  workspaceClass: { type: String, default: '' },
})

defineEmits(['close'])

watch(
  () => props.open,
  (open) => {
    if (props.teleport) {
      document.body.style.overflow = open ? 'hidden' : ''
    }
  },
  { immediate: true },
)

onUnmounted(() => {
  document.body.style.overflow = ''
})
</script>

<style>
.lesson-workspace-screen {
  position: fixed;
  inset: 0;
  z-index: 2400;
  display: flex;
  flex-direction: column;
  background: rgb(var(--v-theme-background));
  color: rgb(var(--v-theme-on-background));
}

.lesson-workspace-screen--layered {
  z-index: 2500;
}

.lesson-workspace-header {
  flex-shrink: 0;
  background: rgb(var(--v-theme-surface));
  border-bottom: 1px solid rgba(var(--v-border-color), 0.16);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.lesson-workspace-header-inner {
  max-width: 920px;
  margin: 0 auto;
  padding: 20px 24px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.lesson-workspace-header--minimal .lesson-workspace-header-inner {
  padding: 12px 24px;
  justify-content: flex-end;
}

.lesson-workspace-main {
  flex: 1;
  overflow-y: auto;
  padding: 24px 16px 32px;
  max-width: 920px;
  width: 100%;
  margin: 0 auto;
}

.lesson-workspace-footer {
  flex-shrink: 0;
  background: rgb(var(--v-theme-surface));
  border-top: 1px solid rgba(var(--v-border-color), 0.16);
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.06);
}

.lesson-workspace-footer-inner {
  max-width: 920px;
  margin: 0 auto;
  padding: 16px 24px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  flex-wrap: wrap;
}

@media (max-width: 599px) {
  .lesson-workspace-header-inner {
    padding: 16px;
  }

  .lesson-workspace-main {
    padding: 16px 16px 24px;
  }

  .lesson-workspace-footer-inner {
    padding: 12px 16px;
  }
}

.lesson-workspace-panel {
  background: rgb(var(--v-theme-surface)) !important;
  border: 1px solid rgba(var(--v-border-color), 0.14);
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.05);
  border-radius: 12px;
}
</style>
