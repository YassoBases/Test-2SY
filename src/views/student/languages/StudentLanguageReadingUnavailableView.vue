<template>
  <div class="page-container slide-up-enter-active">
    <PageHeader
      eyebrow="Learn languages"
      eyebrow-icon="mdi-book-open-page-variant"
      title="Reading"
      subtitle="Reading practice is not available right now."
    />
    <LanguageModuleTabs />

    <v-card class="glass-card pa-5" variant="flat">
      <div class="d-flex align-start gap-3">
        <v-avatar color="secondary" variant="tonal" size="44">
          <v-icon icon="mdi-tools" size="22" />
        </v-avatar>
        <div>
          <h3 class="text-subtitle-1 font-weight-bold mb-1">Reading practice is offline</h3>
          <p class="text-body-2 text-medium-emphasis mb-4">
            This section has been removed while a new reading experience is prepared.
          </p>
          <v-btn color="secondary" variant="flat" :to="ROUTES.STUDENT_LANGUAGES">
            Back to languages
          </v-btn>
        </div>
      </div>
    </v-card>
  </div>
</template>

<script setup>
import PageHeader from '../../../components/common/PageHeader.vue'
import LanguageModuleTabs from '../../../components/language/LanguageModuleTabs.vue'
import { ROUTES } from '../../../constants/app.js'
</script>

<style scoped>
.page-container {
  max-width: 760px;
  margin: 0 auto;
}
</style>
