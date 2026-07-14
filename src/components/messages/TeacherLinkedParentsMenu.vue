<template>
  <v-menu location="bottom start" :close-on-content-click="false">
    <template #activator="{ props: menuProps }">
      <slot name="activator" :props="menuProps" />
    </template>

    <v-card class="teacher-linked-parents-menu" min-width="300" max-width="360">
      <v-card-title class="teacher-linked-parents-menu__title text-body-2 font-weight-bold py-2 px-3">
        {{ t('messages.linkedParents.title') }}
      </v-card-title>
      <v-divider />
      <v-list density="compact" class="py-1">
        <v-list-item
          v-for="parent in parents"
          :key="parent.parent_id"
          class="teacher-linked-parents-menu__item"
        >
          <template #prepend>
            <ParticipantAvatar :name="parent.full_name" role="parent" :size="40" />
          </template>

          <v-list-item-title class="text-body-2 font-weight-bold">
            {{ parent.full_name }}
          </v-list-item-title>
          <v-list-item-subtitle class="teacher-linked-parents-menu__meta">
            <span>{{ relationshipLabelAr(parent.relationship_label) }}</span>
            <span v-if="parent.presence" class="teacher-linked-parents-menu__presence">
              <span
                class="teacher-linked-parents-menu__presence-dot"
                :class="{ 'teacher-linked-parents-menu__presence-dot--online': parent.presence.online }"
              />
              {{ parent.presence.text }}
            </span>
          </v-list-item-subtitle>

          <template #append>
            <div class="teacher-linked-parents-menu__actions">
              <v-btn
                size="x-small"
                variant="tonal"
                color="primary"
                :loading="openingParentId === parent.parent_id"
                :disabled="Boolean(openingParentId && openingParentId !== parent.parent_id)"
                @click="onMessage(parent)"
              >
                {{ t('messages.linkedParents.message') }}
              </v-btn>
              <v-btn size="x-small" variant="text" @click="onProfile(parent)">
                {{ t('messages.linkedParents.viewProfile') }}
              </v-btn>
            </div>
          </template>
        </v-list-item>
      </v-list>
    </v-card>
  </v-menu>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import ParticipantAvatar from './ParticipantAvatar.vue'
import { relationshipLabelAr } from '../../utils/subscriptionStatus.js'

defineProps({
  parents: { type: Array, default: () => [] },
  openingParentId: { type: Number, default: null },
})

const emit = defineEmits(['message-parent', 'view-profile'])

const { t } = useI18n()

function onMessage(parent) {
  emit('message-parent', parent.parent_id)
}

function onProfile() {
  emit('view-profile')
}
</script>
