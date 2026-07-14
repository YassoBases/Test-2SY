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
      <BrandMark :tagline="t('common.brand.studentTagline')" />
    </div>

    <v-divider class="border-opacity-25" />

    <SidebarNavList :items="items" />

    <template #append>
      <div class="pa-4">
        <div class="sidebar-promo pa-4">
          <div class="d-flex align-center gap-2 mb-2">
            <v-icon color="secondary" size="20">mdi-robot-happy-outline</v-icon>
            <span class="text-body-2 font-weight-bold">{{ t('common.sidebarPromo.smartTeacherTitle') }}</span>
          </div>
          <div class="text-caption text-medium-emphasis">
            {{ t('common.sidebarPromo.smartTeacherBody') }}
          </div>
        </div>
        <v-btn
          variant="text"
          color="grey"
          size="small"
          block
          class="mt-3"
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
import { studentNavItems } from '../../config/navigation.js'
import { useAuth } from '../../composables/useAuth.js'
import BrandMark from './BrandMark.vue'
import SidebarNavList from './SidebarNavList.vue'

const { t } = useI18n()
const { logout } = useAuth()

defineProps({
  drawer: { type: Boolean, default: true },
})

defineEmits(['update:drawer'])

const items = studentNavItems
const { mobile } = useDisplay()
</script>
