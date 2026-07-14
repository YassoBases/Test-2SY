<template>
  <div class="page-container slide-up-enter-active">
    <PageHeader
      eyebrow="Learn languages"
      eyebrow-icon="mdi-certificate"
      title="Certificates"
      subtitle="Testimonials CEFR When you master all the skills of the level"
    />
    <LanguageModuleTabs />

    <v-alert v-if="loadError" type="error" variant="tonal" class="mb-4 rounded-lg">{{ loadError }}</v-alert>

    <LoadingState v-if="loading" variant="cards" :count="3" class="mb-6" />

    <template v-else-if="data">
      <section class="section-block">
        <div class="section-block__head">
          <h3 class="section-block__title">Eligibility of certificates</h3>
        </div>
        <v-card class="glass-card pa-5" variant="flat">
          <v-row>
            <v-col v-for="item in data.eligibility" :key="item.level" cols="12" sm="4">
              <div class="eligibility-box pa-4 rounded-lg h-100">
                <div class="d-flex align-center justify-space-between mb-2">
                  <span class="text-h6 font-weight-bold">{{ item.level }}</span>
                  <v-chip
                    size="small"
                    :color="item.issued ? 'success' : item.eligible ? 'secondary' : 'default'" variant="tonal"
                  >
                    {{ statusLabel(item) }}
                  </v-chip>
                </div>
                <p class="text-body-2 text-medium-emphasis mb-0">
                  {{ requirementText(item.level) }}
                </p>
              </div>
            </v-col>
          </v-row>
        </v-card>
      </section>

      <section class="section-block">
        <div class="section-block__head">
          <h3 class="section-block__title">Your testimonials</h3>
        </div>
        <v-card v-if="data.certificates.length" class="glass-card pa-5" variant="flat">
        <v-table density="comfortable" class="cert-table">
          <thead>
            <tr>
              <th>level</th>
              <th>Certificate number</th>
              <th>Release date</th>
              <th>verification code</th>
              <th class="text-end">procedures</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="cert in data.certificates" :key="cert.id">
              <td>
                <v-chip size="small" color="secondary" variant="tonal">{{ cert.certificate_level }}</v-chip>
              </td>
              <td class="font-mono text-body-2">{{ cert.certificate_number }}</td>
              <td>{{ formatDate(cert.issued_at) }}</td>
              <td class="font-mono text-body-2">{{ cert.verification_code }}</td>
              <td class="text-end">
                <v-btn
                  v-if="cert.pdf_url"
                  size="small"
                  variant="tonal"
                  color="secondary"
                  prepend-icon="mdi-download"
                  :href="cert.pdf_url"
                  target="_blank"
                >
                  PDF
                </v-btn>
                <v-btn
                  v-if="cert.verification_url"
                  size="small"
                  variant="text"
                  class="ms-1"
                  :href="cert.verification_url"
                  target="_blank"
                >
                  Verification
                </v-btn>
              </td>
            </tr>
          </tbody>
        </v-table>
        </v-card>
        <EmptyState
          v-else
          icon="mdi-certificate-outline"
          title="No certificates yet"
          description="Complete all skills for the level required to obtain your first certification."
        />
      </section>
    </template>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import PageHeader from '../../../components/common/PageHeader.vue'
import LoadingState from '../../../components/common/LoadingState.vue'
import EmptyState from '../../../components/common/EmptyState.vue'
import LanguageModuleTabs from '../../../components/language/LanguageModuleTabs.vue'
import { fetchLanguageCertificates } from '../../../api/language.js'

const loading = ref(true)
const loadError = ref('')
const data = ref(null)

function formatDate(value) {
  if (!value) return '—'
  return new Date(value).toLocaleDateString('ar-SA', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

function statusLabel(item) {
  if (item.issued) return 'Outgoing'
  if (item.eligible) return 'eligible'
  return 'Not yet qualified'
}

function requirementText(level) {
  return `Reading, listening, writing and speaking ≥ ${level}`
}

async function load() {
  loading.value = true
  loadError.value = ''
  try {
    data.value = await fetchLanguageCertificates()
  } catch (err) {
    loadError.value = err.response?.data?.detail?.message || err.message || 'Unable to load certificates'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.eligibility-box {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.cert-table :deep(th) {
  font-weight: 600;
}

.font-mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  letter-spacing: 0.02em;
}
</style>
