<template>
  <div class="page-container slide-up-enter-active">
    <PageHeader
      eyebrow="Learn languages"
      eyebrow-icon="mdi-book-open-page-variant"
      title="Lessons"
      subtitle="Short grammar & vocabulary lessons that teach — with examples and quick practice"
    />
    <LanguageModuleTabs />

    <v-alert v-if="loadError" type="error" variant="tonal" class="mb-4 rounded-lg">{{ loadError }}</v-alert>
    <LoadingState v-if="loading" variant="cards" :count="3" class="mb-6" />

    <template v-else>
      <v-alert
        v-if="level"
        type="info"
        variant="tonal"
        density="comfortable"
        class="mb-4 rounded-lg"
        icon="mdi-school"
      >
        Lessons for your level: <strong>{{ level }}</strong>
      </v-alert>

      <EmptyState v-if="!lessons.length" preset="languageLessons" />

      <template v-else>
        <section v-for="group in groups" :key="group.type" class="section-block">
          <div class="section-block__head d-flex align-center">
            <v-icon :icon="group.icon" color="secondary" class="me-2" />
            <h3 class="section-block__title mb-0">{{ group.label }}</h3>
            <v-chip size="small" variant="tonal" class="ms-2">{{ group.items.length }}</v-chip>
          </div>

          <v-expansion-panels variant="accordion" multiple>
            <v-expansion-panel
              v-for="lesson in group.items"
              :key="lesson.id"
              class="glass-card mb-2 rounded-lg"
            >
              <v-expansion-panel-title>
                <span class="text-subtitle-1 font-weight-medium" dir="ltr">{{ lesson.title }}</span>
              </v-expansion-panel-title>
              <v-expansion-panel-text>
                <p class="text-body-1 mb-4" dir="ltr">{{ lesson.explanation }}</p>

                <div v-if="lesson.examples?.length" class="mb-4">
                  <div class="text-overline text-medium-emphasis mb-1">Examples</div>
                  <ul class="examples-list" dir="ltr">
                    <li v-for="(ex, i) in lesson.examples" :key="i" class="text-body-2 mb-1">{{ ex }}</li>
                  </ul>
                </div>

                <div v-if="lesson.practice?.length">
                  <div class="text-overline text-medium-emphasis mb-1">Practice</div>
                  <v-list density="comfortable" class="bg-transparent pa-0">
                    <v-list-item
                      v-for="(pr, i) in lesson.practice"
                      :key="i"
                      class="practice-item rounded-lg mb-2 px-3"
                    >
                      <div class="text-body-2 mb-1" dir="ltr">
                        <strong>{{ i + 1 }}.</strong> {{ pr.question }}
                      </div>
                      <v-btn
                        v-if="!revealed[`${lesson.id}-${i}`]"
                        size="x-small"
                        variant="text"
                        color="secondary"
                        @click="reveal(lesson.id, i)"
                      >
                        Show answer
                      </v-btn>
                      <div v-else class="text-body-2 text-success" dir="ltr">
                        <v-icon icon="mdi-check-circle" size="small" class="me-1" />{{ pr.answer }}
                      </div>
                    </v-list-item>
                  </v-list>
                </div>
              </v-expansion-panel-text>
            </v-expansion-panel>
          </v-expansion-panels>
        </section>
      </template>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import PageHeader from '../../../components/common/PageHeader.vue'
import LoadingState from '../../../components/common/LoadingState.vue'
import EmptyState from '../../../components/common/EmptyState.vue'
import LanguageModuleTabs from '../../../components/language/LanguageModuleTabs.vue'
import { fetchLessons } from '../../../api/language.js'
import { useLanguageGate } from '../../../composables/useLanguageGate.js'
import { useLanguageAccess } from '../../../composables/useLanguageAccess.js'

const router = useRouter()
const { access, loadAccess } = useLanguageAccess()
const { handleLanguageApiError, getErrorMessage } = useLanguageGate()

const loading = ref(true)
const loadError = ref('')
const level = ref('')
const lessons = ref([])
const revealed = reactive({})

const groups = computed(() => {
  const defs = [
    { type: 'grammar', label: 'Grammar', icon: 'mdi-format-letter-case' },
    { type: 'vocabulary', label: 'Vocabulary', icon: 'mdi-book-alphabet' },
  ]
  return defs
    .map((d) => ({ ...d, items: lessons.value.filter((l) => l.type === d.type) }))
    .filter((g) => g.items.length)
})

function reveal(lessonId, index) {
  revealed[`${lessonId}-${index}`] = true
}

onMounted(async () => {
  try {
    await loadAccess(true)
    if (access.value?.redirect) {
      router.push(access.value.redirect)
      return
    }
    const res = await fetchLessons()
    level.value = res.level || ''
    lessons.value = res.lessons || []
  } catch (e) {
    if (!handleLanguageApiError(e, access.value)) {
      loadError.value = getErrorMessage(e, 'Unable to load lessons')
    }
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.page-container {
  max-width: 1100px;
  margin: 0 auto;
}
.examples-list {
  list-style: disc;
  padding-inline-start: 1.25rem;
}
.practice-item {
  background: rgba(255, 255, 255, 0.04);
  display: block;
}
</style>
