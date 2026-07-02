<template>
  <v-card class="glass-card glass-card--solid glass-card--elevated pa-5 pa-md-8" variant="flat">
    <div class="d-flex align-center gap-3 mb-4">
      <v-avatar color="primary" variant="tonal" size="48">
        <v-icon>mdi-link-variant</v-icon>
      </v-avatar>
      <div>
        <h3 class="text-h6 font-weight-bold mb-1">{{ t('parent.link.formTitle') }}</h3>
        <p class="text-body-2 text-medium-emphasis mb-0">
          {{ t('parent.link.formHint') }}
        </p>
      </div>
    </div>

    <v-alert
      v-if="linkSuccess"
      type="success"
      variant="tonal"
      class="mb-4 rounded-lg"
      closable
      @click:close="$emit('clear-success')"
    >
      {{ linkSuccess }}
    </v-alert>

    <v-alert
      v-if="linkError"
      type="error"
      variant="tonal"
      class="mb-4 rounded-lg"
      closable
      @click:close="$emit('clear-error')"
    >
      {{ linkError }}
    </v-alert>

    <v-form @submit.prevent="onSubmit">
      <v-text-field
        v-model="code"
        :label="t('parent.link.codeLabel')"
        :placeholder="t('parent.link.codePlaceholder')"
        prepend-inner-icon="mdi-key-variant"
        variant="outlined"
        class="mb-4"
        :disabled="linking"
        autocomplete="off"
        autocapitalize="characters"
        @update:model-value="onCodeInput"
      />

      <v-btn
        type="submit"
        size="large"
        block
        class="btn-glow"
        :loading="linking"
        :disabled="!code.trim()"
      >
        {{ t('parent.link.submit') }}
      </v-btn>
    </v-form>

    <p v-if="showDashboardLink && hasStudents" class="text-center mt-4 mb-0">
      <router-link :to="dashboardRoute" class="text-primary text-body-2">
        {{ t('parent.link.goToDashboard') }}
      </router-link>
    </p>
  </v-card>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ROUTES } from '../../constants/app.js'

defineProps({
  linking: { type: Boolean, default: false },
  linkError: { type: String, default: '' },
  linkSuccess: { type: String, default: '' },
  hasStudents: { type: Boolean, default: false },
  showDashboardLink: { type: Boolean, default: true },
})

const emit = defineEmits(['submit', 'clear-error', 'clear-success'])

const { t } = useI18n()

const dashboardRoute = ROUTES.PARENT_DASHBOARD
const code = ref('')

function onCodeInput(val) {
  code.value = String(val || '')
    .trim()
    .toUpperCase()
    .replace(/[^A-Z0-9]/g, '')
}

function onSubmit() {
  emit('submit', code.value)
}
</script>
