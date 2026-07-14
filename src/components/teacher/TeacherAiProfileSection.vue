<template>
  <TeacherWorkspaceCard
    class="teacher-expressions tds-scope"
    :title="$t('teacher.aiProfile.title')"
    :meta="$t('teacher.aiProfile.meta')"
    :aria-label="$t('teacher.aiProfile.title')"
  >
    <TeacherFormHint variant="info" class="teacher-expressions__intro">
      {{ $t('teacher.aiProfile.hint') }}
    </TeacherFormHint>

    <v-alert
      v-if="error"
      type="error"
      variant="tonal"
      density="compact"
      class="teacher-expressions__alert rounded-lg"
      closable
      @click:close="error = ''"
    >
      {{ error }}
    </v-alert>
    <v-alert
      v-if="success"
      type="success"
      variant="tonal"
      density="compact"
      class="teacher-expressions__alert rounded-lg"
      closable
      @click:close="success = ''"
    >
      {{ success }}
    </v-alert>

    <v-skeleton-loader v-if="loading" type="article" class="rounded-lg" />

    <TeacherForm v-else>
      <TeacherFormField mode="plain">
        <div v-if="form.phrases.length" class="teacher-expressions__chips" role="list">
          <div
            v-for="(phrase, index) in form.phrases"
            :key="`${index}-${phrase}`"
            class="teacher-expressions__chip"
            role="listitem"
          >
            <span class="teacher-expressions__chip-text">{{ phrase }}</span>
            <button
              type="button"
              class="teacher-expressions__chip-action"
              :aria-label="$t('teacher.actions.editPhrase')"
              @click="startEditPhrase(index)"
            >
              <v-icon icon="mdi-pencil-outline" size="14" />
            </button>
            <button
              type="button"
              class="teacher-expressions__chip-action teacher-expressions__chip-action--danger"
              :aria-label="$t('teacher.aiProfile.deletePhrase')"
              @click="removePhrase(index)"
            >
              <v-icon icon="mdi-close" size="14" />
            </button>
          </div>
        </div>

        <p v-else class="teacher-expressions__empty">
          {{ $t('teacher.aiProfile.emptyHint') }}
        </p>

        <div class="teacher-expressions__input">
          <v-text-field
            v-model="phraseInput"
            :label="phraseInputLabel"
            :placeholder="$t('teacher.aiProfile.example')"
            variant="outlined"
            density="comfortable"
            hide-details="auto"
            class="teacher-expressions__input-field"
            @keyup.enter="commitPhrase"
          />
          <TeacherButton variant="secondary" size="sm" :disabled="!phraseInput.trim()" @click="commitPhrase">
            {{ phraseActionLabel }}
          </TeacherButton>
          <TeacherButton
            v-if="editingPhraseIndex !== null"
            variant="ghost"
            size="sm"
            @click="cancelEditPhrase"
          >
            {{ $t('common.cancel') }}
          </TeacherButton>
        </div>
      </TeacherFormField>
    </TeacherForm>

    <div v-if="!loading" class="teacher-expressions__footer">
      <TeacherButton variant="primary" :loading="saving" prepend-icon="mdi-check" @click="save">
        {{ $t('teacher.actions.savePhrases') }}
      </TeacherButton>
    </div>
  </TeacherWorkspaceCard>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { fetchTeacherAiProfile, updateTeacherAiProfile } from '../../api/teacherSetup.js'
import { getErrorMessage } from '../../api/client.js'
import {
  TEACHER_SIGNATURE_MAX_LENGTH,
  defaultTeacherAiEnums,
  parseSignaturePhrases,
  serializeSignaturePhrases,
} from '../../data/teacherAiProfileOptions.js'
import {
  TeacherWorkspaceCard,
  TeacherForm,
  TeacherFormField,
  TeacherFormHint,
  TeacherButton,
} from './design-system/index.js'

const { t } = useI18n()

const phraseInputLabel = computed(() =>
  editingPhraseIndex.value === null ? t('teacher.aiProfile.newPhrase') : t('teacher.actions.editPhrase'),
)
const phraseActionLabel = computed(() =>
  editingPhraseIndex.value === null ? t('common.add') : t('common.update'),
)

const loading = ref(true)
const saving = ref(false)
const error = ref('')
const success = ref('')
const phraseInput = ref('')
const editingPhraseIndex = ref(null)

const preservedProfile = reactive({
  teacherBio: null,
  teacherDisplayName: null,
})

const form = reactive({
  phrases: [],
})

function normalizePhrase(value) {
  return (value || '').trim()
}

function commitPhrase() {
  const next = normalizePhrase(phraseInput.value)
  if (!next) return

  if (editingPhraseIndex.value !== null) {
    form.phrases.splice(editingPhraseIndex.value, 1, next)
    editingPhraseIndex.value = null
  } else if (!form.phrases.includes(next)) {
    form.phrases.push(next)
  }

  phraseInput.value = ''
}

function startEditPhrase(index) {
  editingPhraseIndex.value = index
  phraseInput.value = form.phrases[index]
}

function cancelEditPhrase() {
  editingPhraseIndex.value = null
  phraseInput.value = ''
}

function removePhrase(index) {
  form.phrases.splice(index, 1)
  if (editingPhraseIndex.value === index) {
    cancelEditPhrase()
  } else if (editingPhraseIndex.value !== null && editingPhraseIndex.value > index) {
    editingPhraseIndex.value -= 1
  }
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const data = await fetchTeacherAiProfile()
    preservedProfile.teacherBio = data.teacher_bio || null
    preservedProfile.teacherDisplayName = data.teacher_display_name || null
    form.phrases = parseSignaturePhrases(data.teacher_signature_phrase)
    phraseInput.value = ''
    editingPhraseIndex.value = null
  } catch (e) {
    error.value = getErrorMessage(e, t('teacher.errors.loadPhrases'))
  } finally {
    loading.value = false
  }
}

async function save() {
  saving.value = true
  error.value = ''
  success.value = ''

  const phrasesRaw = form.phrases
    .map((phrase) => phrase.trim())
    .filter(Boolean)
    .join('\n')
  if (phrasesRaw.length > TEACHER_SIGNATURE_MAX_LENGTH) {
    error.value = t('teacher.aiProfile.phrasesTooLongTemplate', { max: TEACHER_SIGNATURE_MAX_LENGTH })
    saving.value = false
    return
  }

  try {
    await updateTeacherAiProfile({
      ...defaultTeacherAiEnums(),
      teacherDisplayName: preservedProfile.teacherDisplayName,
      teacherBio: preservedProfile.teacherBio,
      teacherSignaturePhrase: serializeSignaturePhrases(form.phrases),
    })
    success.value = t('teacher.aiProfile.phrasesSavedFull')
  } catch (e) {
    error.value = getErrorMessage(e, t('teacher.errors.savePhrases'))
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.teacher-expressions {
  margin-bottom: var(--em-space-xl);
  border: 1px solid var(--em-border-bright);
  box-shadow: none;
}

.teacher-expressions__intro {
  margin-bottom: var(--em-space-md);
}

.teacher-expressions__alert {
  margin-bottom: var(--em-space-md);
}

.teacher-expressions__chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: var(--em-space-sm);
}

.teacher-expressions__chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  max-width: 100%;
  padding: 4px 6px 4px 10px;
  border-radius: 999px;
  border: 1px solid color-mix(in srgb, var(--em-primary) 22%, var(--em-border-subtle));
  background: color-mix(in srgb, var(--em-primary) 6%, transparent);
  transition:
    border-color var(--em-duration-fast, 0.15s) ease,
    background var(--em-duration-fast, 0.15s) ease;
}

.teacher-expressions__chip:hover {
  border-color: color-mix(in srgb, var(--em-primary) 38%, var(--em-border-bright));
  background: color-mix(in srgb, var(--em-primary) 10%, transparent);
}

.teacher-expressions__chip-text {
  font-size: 0.8125rem;
  line-height: 1.35;
  color: var(--em-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.teacher-expressions__chip-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border: none;
  border-radius: 50%;
  background: transparent;
  color: var(--em-text-muted, rgba(var(--v-theme-on-surface), 0.55));
  cursor: pointer;
  flex-shrink: 0;
}

.teacher-expressions__chip-action:hover {
  background: rgba(var(--v-theme-on-surface), 0.06);
  color: var(--em-text);
}

.teacher-expressions__chip-action--danger:hover {
  color: rgb(var(--v-theme-error));
}

.teacher-expressions__empty {
  margin: 0 0 var(--em-space-sm);
  font-size: 0.8125rem;
  line-height: 1.5;
  color: var(--em-text-muted, rgba(var(--v-theme-on-surface), 0.55));
}

.teacher-expressions__input {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--em-space-sm);
}

.teacher-expressions__input-field {
  flex: 1 1 180px;
  min-width: 0;
}

.teacher-expressions__footer {
  display: flex;
  justify-content: flex-end;
  margin-top: var(--em-space-md);
  padding-top: var(--em-space-md);
  border-top: 1px solid var(--em-border-subtle);
}

:global([data-theme='morning']) .teacher-expressions.tds-scope {
  border-color: var(--em-border-bright);
  box-shadow: none;
}
</style>
