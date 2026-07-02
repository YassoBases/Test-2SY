<template>
  <v-card class="glass-card pa-5 pa-md-6 mb-5" variant="flat">
    <div class="d-flex align-center justify-space-between mb-4 flex-wrap gap-2">
      <div class="d-flex align-center gap-2">
        <v-icon :color="iconColor">{{ icon }}</v-icon>
        <h3 class="text-h6 font-weight-bold mb-0">{{ title }}</h3>
        <v-chip size="x-small" variant="tonal">{{ items.length }}</v-chip>
      </div>
      <v-btn size="small" variant="tonal" color="primary" prepend-icon="mdi-plus" @click="openCreate">
        {{ $t('common.add') }}
      </v-btn>
    </div>

    <v-list v-if="items.length" class="bg-transparent pa-0" density="comfortable">
      <v-list-item
        v-for="item in items"
        :key="item.id"
        class="entry-item rounded-lg mb-2 pa-3"
      >
        <v-list-item-title class="font-weight-bold">
          <v-icon v-if="section === 'achievement' && item.is_pinned" color="warning" size="16" class="me-1">mdi-pin</v-icon>
          {{ item.title }}
        </v-list-item-title>
        <v-list-item-subtitle class="text-wrap">
          <span v-if="subtitleFor(item)">{{ subtitleFor(item) }}</span>
          <p v-if="item.description" class="text-caption mt-1 mb-0">{{ item.description }}</p>
        </v-list-item-subtitle>
        <template #append>
          <div class="d-flex gap-1">
            <v-btn
              v-if="section === 'achievement'"
              icon
              size="small"
              variant="text"
              :color="item.is_pinned ? 'warning' : undefined"
              @click="togglePin(item)"
            >
              <v-icon>mdi-pin{{ item.is_pinned ? '' : '-outline' }}</v-icon>
            </v-btn>
            <v-btn icon size="small" variant="text" @click="openEdit(item)">
              <v-icon>mdi-pencil-outline</v-icon>
            </v-btn>
            <v-btn
              icon
              size="small"
              variant="text"
              color="error"
              :loading="deletingId === item.id"
              @click="confirmDelete(item)"
            >
              <v-icon>mdi-delete-outline</v-icon>
            </v-btn>
          </div>
        </template>
      </v-list-item>
    </v-list>

    <p v-else class="text-body-2 text-medium-emphasis mb-0">{{ displayEmptyText }}</p>

    <v-dialog v-model="dialogOpen" max-width="520" persistent>
      <v-card class="pa-5 rounded-xl">
        <h4 class="text-h6 font-weight-bold mb-4">{{ editingId ? $t('teacher.profileEntry.editTitle') : $t('teacher.profileEntry.addTitle') }} — {{ title }}</h4>
        <v-form @submit.prevent="save">
          <v-text-field
            v-model="form.title"
            :label="$t('teacher.labels.titleAsterisk')"
            variant="outlined"
            density="comfortable"
            class="mb-3"
          />
          <v-text-field
            v-if="showInstitution"
            v-model="form.institution"
            :label="$t('teacher.labels.orgInstitution')"
            variant="outlined"
            density="comfortable"
            class="mb-3"
          />
          <v-text-field
            v-if="showOrganization"
            v-model="form.organization"
            :label="$t('teacher.labels.institutionSchool')"
            variant="outlined"
            density="comfortable"
            class="mb-3"
          />
          <v-row v-if="showYearRange" dense class="mb-1">
            <v-col cols="6">
              <v-text-field
                v-model.number="form.year_from"
                :label="$t('teacher.labels.fromYear')"
                type="number"
                variant="outlined"
                density="comfortable"
              />
            </v-col>
            <v-col cols="6">
              <v-text-field
                v-model.number="form.year_to"
                :label="$t('teacher.labels.toYear')"
                type="number"
                variant="outlined"
                density="comfortable"
              />
            </v-col>
          </v-row>
          <v-text-field
            v-if="showYear"
            v-model.number="form.year"
            :label="$t('teacher.labels.year')"
            type="number"
            variant="outlined"
            density="comfortable"
            class="mb-3"
          />
          <v-textarea
            v-model="form.description"
            :label="$t('teacher.labels.details')"
            variant="outlined"
            rows="3"
            auto-grow
            class="mb-3"
          />
          <v-checkbox
            v-if="section === 'achievement'"
            v-model="form.is_pinned"
            :label="$t('teacher.cv.featureHighlight')"
            density="compact"
            class="mb-2"
          />
          <div class="d-flex justify-end gap-2">
            <v-btn variant="text" @click="dialogOpen = false">{{ $t('common.cancel') }}</v-btn>
            <v-btn color="primary" :loading="saving" type="submit">{{ $t('common.save') }}</v-btn>
          </div>
        </v-form>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()


const props = defineProps({
  title: { type: String, required: true },
  icon: { type: String, default: 'mdi-format-list-bulleted' },
  iconColor: { type: String, default: 'primary' },
  emptyText: { type: String, default: '' },
  items: { type: Array, default: () => [] },
  section: {
    type: String,
    required: true,
    validator: (v) => ['qualification', 'experience', 'achievement', 'why'].includes(v),
  },
  onCreate: { type: Function, required: true },
  onUpdate: { type: Function, required: true },
  onDelete: { type: Function, required: true },
})

const emit = defineEmits(['error'])

const displayEmptyText = computed(() => props.emptyText || t('teacher.cv.noItems'))

const dialogOpen = ref(false)
const editingId = ref(null)
const saving = ref(false)
const deletingId = ref(null)
const form = reactive({
  title: '',
  institution: '',
  organization: '',
  year: null,
  year_from: null,
  year_to: null,
  description: '',
  is_pinned: false,
})

const showInstitution = props.section === 'qualification'
const showOrganization = props.section === 'experience'
const showYear = props.section === 'qualification' || props.section === 'achievement'
const showYearRange = props.section === 'experience'

function resetForm() {
  form.title = ''
  form.institution = ''
  form.organization = ''
  form.year = null
  form.year_from = null
  form.year_to = null
  form.description = ''
  form.is_pinned = false
}

function subtitleFor(item) {
  if (props.section === 'qualification') {
    const parts = [item.institution, item.year].filter(Boolean)
    return parts.join(' · ')
  }
  if (props.section === 'experience') {
    const from = item.year_from || '—'
    const to = item.year_to || t('teacher.labels.now')
    const org = item.organization ? `${item.organization} · ` : ''
    return `${org}${from} — ${to}`
  }
  if (props.section === 'achievement' && item.year) return String(item.year)
  return ''
}

function openCreate() {
  editingId.value = null
  resetForm()
  dialogOpen.value = true
}

function openEdit(item) {
  editingId.value = item.id
  form.title = item.title || ''
  form.institution = item.institution || ''
  form.organization = item.organization || ''
  form.year = item.year ?? null
  form.year_from = item.year_from ?? null
  form.year_to = item.year_to ?? null
  form.description = item.description || ''
  form.is_pinned = Boolean(item.is_pinned)
  dialogOpen.value = true
}

function buildPayload() {
  const base = {
    title: form.title.trim(),
    description: form.description.trim() || null,
  }
  if (props.section === 'qualification') {
    return {
      ...base,
      institution: form.institution.trim() || null,
      year: form.year || null,
    }
  }
  if (props.section === 'experience') {
    return {
      ...base,
      organization: form.organization.trim() || null,
      year_from: form.year_from || null,
      year_to: form.year_to || null,
    }
  }
  if (props.section === 'achievement') {
    return { ...base, year: form.year || null, is_pinned: form.is_pinned }
  }
  if (props.section === 'why') {
    return base
  }
  return { ...base, year: form.year || null }
}

async function save() {
  if (!form.title.trim()) {
    emit('error', t('teacher.validation.enterTitle'))
    return
  }
  saving.value = true
  try {
    const payload = buildPayload()
    if (editingId.value) {
      await props.onUpdate(editingId.value, payload)
    } else {
      await props.onCreate(payload)
    }
    dialogOpen.value = false
  } catch (err) {
    emit('error', err)
  } finally {
    saving.value = false
  }
}

async function togglePin(item) {
  try {
    await props.onUpdate(item.id, { is_pinned: !item.is_pinned })
  } catch (err) {
    emit('error', err)
  }
}

async function confirmDelete(item) {
  if (!window.confirm(t('teacher.confirm.deleteItem'))) return
  deletingId.value = item.id
  try {
    await props.onDelete(item.id)
  } catch (err) {
    emit('error', err)
  } finally {
    deletingId.value = null
  }
}
</script>

<style scoped>
.entry-item {
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.02);
}
</style>
