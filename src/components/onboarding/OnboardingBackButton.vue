<template>
  <v-btn
    variant="text"
    size="small"
    class="onboarding-back-btn"
    prepend-icon="mdi-arrow-right"
    :disabled="!to"
    @click="goBack"
  >
    {{ t('common.back') }}
  </v-btn>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  to: { type: [String, Object], default: null },
})

const { t } = useI18n()
const router = useRouter()

function goBack() {
  if (!props.to) return
  router.push(props.to)
}
</script>

<style scoped>
.onboarding-back-btn {
  text-transform: none;
  letter-spacing: 0;
  font-size: 0.85rem;
  min-width: auto;
  padding-inline: 0.35rem;
}
</style>
