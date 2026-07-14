<template>
  <v-navigation-drawer
    :model-value="drawer"
    :temporary="mobile"
    :permanent="!mobile"
    width="280"
    class="sidebar glass-sidebar"
    @update:model-value="$emit('update:drawer', $event)"
  >
    <div class="sidebar-brand pa-6">
      <BrandMark :tagline="t('common.brand.parentTagline')" />
    </div>

    <v-divider class="border-opacity-25" />

    <SidebarNavList :items="items" />

    <template #append>
      <div class="pa-4">
        <v-btn
          variant="text"
          color="grey"
          size="small"
          block
          class="mt-1"
          prepend-icon="mdi-logout"
          @click="logout"
        >
          {{ t('common.logout') }}
        </v-btn>
      </div>
    </template>
  </v-navigation-drawer>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import { useDisplay } from 'vuetify'
import { parentNavItems } from '../../config/navigation.js'
import { useAuth } from '../../composables/useAuth.js'
import BrandMark from './BrandMark.vue'
import SidebarNavList from './SidebarNavList.vue'

const { t } = useI18n()

defineProps({
  drawer: { type: Boolean, default: true },
})

defineEmits(['update:drawer'])

const { mobile } = useDisplay()
const { logout } = useAuth()
const items = parentNavItems
</script>
