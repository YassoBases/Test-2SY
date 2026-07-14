<template>
  <img
    :src="logoSrc"
    :alt="t('common.brand.name')"
    class="edumind-logo"
    :class="sizeClass"
    loading="eager"
    decoding="async"
  />
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import logoSrc from '../../assets/edumind-logo.png'

const { t } = useI18n()

const props = defineProps({
  size: {
    type: String,
    default: 'landing',
    validator: (v) => ['landing', 'auth', 'compact', 'sidebar', 'loading', 'inline', 'empty'].includes(v),
  },
})

const sizeClass = computed(() => `edumind-logo--${props.size}`)
</script>

<style scoped>
.edumind-logo {
  display: block;
  width: auto;
  height: auto;
  object-fit: contain;
  object-position: center;
  background: transparent;
  filter:
    drop-shadow(0 0 14px rgba(34, 211, 238, 0.28))
    drop-shadow(0 2px 10px rgba(0, 0, 0, 0.35));
}

[data-theme='morning'] .edumind-logo {
  filter:
    drop-shadow(0 1px 6px rgba(99, 102, 241, 0.2))
    drop-shadow(0 2px 8px rgba(15, 23, 42, 0.08));
}

.edumind-logo--landing {
  width: min(300px, 78vw);
  max-height: clamp(76px, 15vh, 104px);
}

.edumind-logo--auth {
  width: min(220px, 58vw);
  max-height: 72px;
}

.edumind-logo--compact {
  width: min(160px, 44vw);
  max-height: 52px;
}

.edumind-logo--sidebar {
  width: min(168px, 100%);
  max-height: 48px;
}

.edumind-logo--loading {
  width: auto;
  max-height: 34px;
  filter: drop-shadow(0 1px 6px rgba(99, 102, 241, 0.18));
}

.edumind-logo--inline {
  width: auto;
  max-height: 26px;
  filter: drop-shadow(0 1px 4px rgba(99, 102, 241, 0.12));
}

.edumind-logo--empty {
  width: auto;
  max-height: 38px;
  filter: drop-shadow(0 1px 5px rgba(99, 102, 241, 0.14));
}
</style>
