<template>
  <div class="slide-up-enter-active page-container">
    <PageHeader
      eyebrow="Premium subscription"
      eyebrow-icon="mdi-translate"
      title="Learn English"
      subtitle="Activate your subscription to access the level test and personal path"
    />

    <v-alert v-if="error" type="error" variant="tonal" class="mb-4 rounded-lg">{{ error }}</v-alert>
    <v-alert v-if="success" type="success" variant="tonal" class="mb-4 rounded-lg">{{ success }}</v-alert>

    <v-row justify="center">
      <v-col cols="12" md="8" lg="6">
        <LanguagePaywallCard
          :product="access?.product"
          :status="access?.status"
          :loading="subscribing"
          @subscribe="onSubscribe"
        />
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import PageHeader from '../../../components/common/PageHeader.vue'
import LanguagePaywallCard from '../../../components/language/LanguagePaywallCard.vue'
import { useLanguageAccess } from '../../../composables/useLanguageAccess.js'
import { subscribeLanguage } from '../../../api/language.js'
import { getErrorMessage } from '../../../api/client.js'
import { ROUTES } from '../../../constants/app.js'

const router = useRouter()
const { access, loadAccess, clearLanguageAccessCache } = useLanguageAccess()
const error = ref('')
const success = ref('')
const subscribing = ref(false)

onMounted(async () => {
  try {
    const a = await loadAccess(true)
    if (a.subscribed) {
      router.replace(ROUTES.STUDENT_LANGUAGES)
    }
  } catch (e) {
    error.value = getErrorMessage(e, 'The product could not be loaded')
  }
})

async function onSubscribe() {
  subscribing.value = true
  error.value = ''
  success.value = ''
  try {
    await subscribeLanguage('card')
    clearLanguageAccessCache()
    success.value = 'Subscription has been activated — You will be directed to start the level test soon (next stage).'
    setTimeout(() => router.push(ROUTES.STUDENT_LANGUAGES), 1500)
  } catch (e) {
    error.value = getErrorMessage(e, 'Subscription failed')
  } finally {
    subscribing.value = false
  }
}
</script>

<style scoped>
.page-container {
  max-width: 900px;
  margin: 0 auto;
}
</style>
