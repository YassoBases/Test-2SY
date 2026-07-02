<template>
  <div class="page-container slide-up-enter-active">
    <PageHeader
      eyebrow="Learn languages"
      eyebrow-icon="mdi-history"
      title="History"
      subtitle="Review your past conversations and role-play scenarios"
    />
    <LanguageModuleTabs />

    <v-alert v-if="loadError" type="error" variant="tonal" class="mb-4 rounded-lg">{{ loadError }}</v-alert>

    <v-tabs v-model="tab" color="secondary" class="mb-4">
      <v-tab value="conversations">Conversations</v-tab>
      <v-tab value="scenarios">Scenarios</v-tab>
    </v-tabs>

    <LoadingState v-if="loading" variant="cards" :count="3" class="mb-6" />

    <template v-else>
      <!-- Conversations -->
      <template v-if="tab === 'conversations'">
        <EmptyState
          v-if="!conversations.length"
          compact
          icon="mdi-robot-happy-outline"
          title="No conversations yet"
          description="Your AI speaking conversations will appear here once you have some."
        />
        <v-row v-else>
          <v-col v-for="c in conversations" :key="c.session_id" cols="12" md="6">
            <v-card class="glass-card pa-4 h-100" variant="flat">
              <div class="d-flex align-center justify-space-between mb-1">
                <span class="text-subtitle-2 font-weight-bold">{{ formatDate(c.started_at) }}</span>
                <v-chip size="x-small" :color="c.status === 'active' ? 'success' : 'default'" variant="tonal">
                  {{ c.status }}
                </v-chip>
              </div>
              <div class="text-caption text-medium-emphasis mb-3">
                {{ c.turn_count }} turn{{ c.turn_count === 1 ? '' : 's' }}
                <span v-if="c.level_at_start"> · level {{ c.level_at_start }}</span>
              </div>
              <v-btn size="small" variant="tonal" color="secondary" :disabled="!c.turn_count" @click="openConversation(c.session_id)">
                View transcript
              </v-btn>
            </v-card>
          </v-col>
        </v-row>
      </template>

      <!-- Scenarios -->
      <template v-else>
        <EmptyState
          v-if="!scenarios.length"
          compact
          icon="mdi-account-group-outline"
          title="No scenarios yet"
          description="Your completed role-play scenarios will appear here."
        />
        <v-row v-else>
          <v-col v-for="s in scenarios" :key="s.session_id" cols="12" md="6">
            <v-card class="glass-card pa-4 h-100" variant="flat">
              <div class="d-flex align-center justify-space-between mb-1 gap-2">
                <span class="text-subtitle-2 font-weight-bold">{{ s.title_ar || s.title_en || 'Scenario' }}</span>
                <v-chip
                  v-if="s.goal_achieved !== null && s.goal_achieved !== undefined"
                  size="x-small"
                  :color="s.goal_achieved ? 'success' : 'warning'"
                  variant="tonal"
                >
                  {{ s.goal_achieved ? 'Goal met' : 'In progress' }}
                </v-chip>
              </div>
              <div class="text-caption text-medium-emphasis mb-3">
                {{ formatDate(s.started_at) }} · {{ s.turn_count }} turns
                <span v-if="s.estimated_cefr"> · {{ s.estimated_cefr }}</span>
              </div>
              <v-btn size="small" variant="tonal" color="secondary" @click="openScenario(s.session_id)">
                View details
              </v-btn>
            </v-card>
          </v-col>
        </v-row>
      </template>
    </template>

    <!-- Conversation transcript dialog -->
    <v-dialog v-model="convOpen" max-width="640" scrollable>
      <v-card class="pa-4" dir="ltr">
        <div class="d-flex align-center justify-space-between mb-3">
          <span class="text-h6">Conversation</span>
          <v-btn icon="mdi-close" variant="text" size="small" @click="convOpen = false" />
        </div>
        <div v-if="detailLoading" class="text-center py-6"><v-progress-circular indeterminate color="secondary" /></div>
        <div v-else-if="convDetail" style="max-height: 60vh; overflow-y: auto;">
          <div v-for="t in convDetail.turns" :key="t.turn_index" class="mb-4">
            <div class="msg-you pa-2 rounded-lg mb-1">
              <span class="text-caption text-medium-emphasis">You:</span> {{ t.you }}
            </div>
            <div class="msg-ai pa-2 rounded-lg">
              <span class="text-caption text-medium-emphasis">Tutor:</span> {{ t.reply }}
            </div>
            <LanguageSpeakingCorrectionBlock
              v-if="t.correction_display && t.correction_display.has_errors"
              :display="t.correction_display"
              class="mt-2"
            />
          </div>
        </div>
      </v-card>
    </v-dialog>

    <!-- Scenario detail dialog -->
    <v-dialog v-model="scenOpen" max-width="640" scrollable>
      <v-card class="pa-4" dir="ltr">
        <div class="d-flex align-center justify-space-between mb-3">
          <span class="text-h6">{{ scenDetail?.scenario?.title_ar || scenDetail?.scenario?.title_en || 'Scenario' }}</span>
          <v-btn icon="mdi-close" variant="text" size="small" @click="scenOpen = false" />
        </div>
        <div v-if="detailLoading" class="text-center py-6"><v-progress-circular indeterminate color="secondary" /></div>
        <div v-else-if="scenDetail" style="max-height: 60vh; overflow-y: auto;">
          <div v-if="scenDetail.summary?.scores" class="scores-grid mb-3">
            <div v-for="sc in scenScoreRows" :key="sc.key" class="score-pill text-center pa-2 rounded-lg">
              <div class="text-caption text-medium-emphasis">{{ sc.label }}</div>
              <div class="text-body-1 font-weight-bold">{{ sc.value }}</div>
            </div>
          </div>
          <p v-if="scenDetail.summary?.overall_impression" class="text-body-2 mb-3">
            {{ scenDetail.summary.overall_impression }}
          </p>

          <div class="text-caption font-weight-bold text-medium-emphasis mb-1">Transcript</div>
          <div v-for="(m, i) in scenDetail.messages" :key="i" class="mb-1">
            <div :class="m.role === 'user' ? 'msg-you' : 'msg-ai'" class="pa-2 rounded-lg">
              <span class="text-caption text-medium-emphasis">{{ m.role === 'user' ? 'You' : 'AI' }}:</span> {{ m.text }}
            </div>
          </div>
        </div>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import PageHeader from '../../../components/common/PageHeader.vue'
import LoadingState from '../../../components/common/LoadingState.vue'
import EmptyState from '../../../components/common/EmptyState.vue'
import LanguageModuleTabs from '../../../components/language/LanguageModuleTabs.vue'
import LanguageSpeakingCorrectionBlock from '../../../components/language/LanguageSpeakingCorrectionBlock.vue'
import {
  fetchConversationSessions,
  fetchConversationSessionDetail,
  fetchScenarioSessions,
  fetchScenarioSession,
} from '../../../api/language.js'
import { useLanguageAccess } from '../../../composables/useLanguageAccess.js'
import { useLanguageGate } from '../../../composables/useLanguageGate.js'

const { access, loadAccess } = useLanguageAccess()
const { handleLanguageApiError, getErrorMessage } = useLanguageGate()

const tab = ref('conversations')
const loading = ref(true)
const loadError = ref('')
const conversations = ref([])
const scenarios = ref([])

const convOpen = ref(false)
const scenOpen = ref(false)
const detailLoading = ref(false)
const convDetail = ref(null)
const scenDetail = ref(null)

const scenScoreRows = computed(() => {
  const s = scenDetail.value?.summary?.scores || {}
  return [
    { key: 'task_completion', label: 'Task', value: s.task_completion ?? 0 },
    { key: 'fluency', label: 'Fluency', value: s.fluency ?? 0 },
    { key: 'grammar', label: 'Grammar', value: s.grammar ?? 0 },
    { key: 'vocabulary', label: 'Vocabulary', value: s.vocabulary ?? 0 },
    { key: 'interaction', label: 'Interaction', value: s.interaction ?? 0 },
  ]
})

onMounted(async () => {
  try {
    await loadAccess(true)
    const [conv, scen] = await Promise.all([fetchConversationSessions(), fetchScenarioSessions()])
    conversations.value = conv.sessions || []
    scenarios.value = scen.sessions || []
  } catch (e) {
    if (!handleLanguageApiError(e, access.value)) {
      loadError.value = getErrorMessage(e, 'Unable to load history')
    }
  } finally {
    loading.value = false
  }
})

async function openConversation(sessionId) {
  convOpen.value = true
  convDetail.value = null
  detailLoading.value = true
  try {
    convDetail.value = await fetchConversationSessionDetail(sessionId)
  } catch (e) {
    loadError.value = getErrorMessage(e, 'Could not load the conversation')
    convOpen.value = false
  } finally {
    detailLoading.value = false
  }
}

async function openScenario(sessionId) {
  scenOpen.value = true
  scenDetail.value = null
  detailLoading.value = true
  try {
    scenDetail.value = await fetchScenarioSession(sessionId)
  } catch (e) {
    loadError.value = getErrorMessage(e, 'Could not load the scenario')
    scenOpen.value = false
  } finally {
    detailLoading.value = false
  }
}

function formatDate(iso) {
  try {
    return new Date(iso).toLocaleString('de-DE')
  } catch {
    return iso
  }
}
</script>

<style scoped>
.page-container {
  max-width: 1100px;
  margin: 0 auto;
}
.msg-you {
  background: rgba(var(--v-theme-secondary), 0.1);
  border: 1px solid rgba(var(--v-theme-secondary), 0.22);
}
.msg-ai {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
}
.scores-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
}
.score-pill {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
}
@media (max-width: 480px) {
  .scores-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>
