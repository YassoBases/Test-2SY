<template>
  <div v-if="isDev" class="dev-skip">
    <v-btn
      color="warning"
      variant="tonal"
      rounded="lg"
      size="small"
      prepend-icon="mdi-flask-outline"
      :loading="busy"
      @click="dialog = true"
    >
      Start From Scratch
    </v-btn>

    <v-dialog v-model="dialog" max-width="420" scrim="rgba(15,23,42,0.45)">
      <v-card class="glass-card pa-5" variant="flat">
        <div class="text-caption text-medium-emphasis mb-1">Developer only · DEBUG</div>
        <h3 class="text-h6 font-weight-bold mb-1">Skip Placement Test</h3>
        <p class="text-body-2 text-medium-emphasis mb-4">
          Marks placement complete, initializes an empty Knowledge Model (no fake mastery),
          and starts curriculum from the first node of the selected CEFR.
        </p>

        <div class="text-caption font-weight-bold mb-2">Starting level</div>
        <v-radio-group v-model="startingCefr" hide-details class="mb-4">
          <v-radio v-for="lvl in LEVELS" :key="lvl" :label="lvl" :value="lvl" color="warning" />
        </v-radio-group>

        <v-alert v-if="error" type="error" variant="tonal" density="compact" class="mb-3">{{ error }}</v-alert>

        <div class="d-flex justify-end flex-wrap gap-2">
          <v-btn variant="text" :disabled="busy" @click="dialog = false">Cancel</v-btn>
          <v-btn color="warning" variant="flat" :loading="busy" @click="confirm">
            Create Student Runtime
          </v-btn>
        </div>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { getErrorMessage } from '../../api/client.js'
import { devSkipPlacementApi } from '../../api/language.js'
import { useLanguageAccess } from '../../composables/useLanguageAccess.js'
import { ROUTES } from '../../constants/app.js'

const LEVELS = ['A1', 'A2', 'B1', 'B2', 'C1']
const isDev = import.meta.env.DEV

const emit = defineEmits(['done'])
const router = useRouter()
const { loadAccess } = useLanguageAccess()

const dialog = ref(false)
const busy = ref(false)
const startingCefr = ref('A1')
const error = ref('')

async function confirm() {
  if (busy.value) return
  busy.value = true
  error.value = ''
  try {
    // Keep skip fast: do NOT wait for Claude package authoring here.
    const result = await devSkipPlacementApi({
      startingCefr: startingCefr.value,
      bootstrapLearning: false,
    })
    await loadAccess(true)
    dialog.value = false
    emit('done', result)
    const redirect = result?.redirect || ROUTES.STUDENT_LANGUAGES_SPEAKING
    await router.push({ path: redirect, query: { autostart: '1' } })
  } catch (e) {
    error.value = getErrorMessage(e, 'Could not create student runtime')
  } finally {
    busy.value = false
  }
}
</script>

<style scoped>
.dev-skip {
  display: inline-flex;
}
</style>
