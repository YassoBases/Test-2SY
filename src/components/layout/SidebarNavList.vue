<template>
  <v-list nav density="comfortable" class="px-3 py-4 sidebar-nav">
    <template v-for="group in navGroups" :key="group.key">
      <p v-if="group.label" class="sidebar-nav__group-label">{{ group.label }}</p>
      <v-list-item
        v-for="item in group.items"
        :key="navItemKey(item)"
        :to="item.to"
        :prepend-icon="item.icon"
        :title="itemTitle(item)"
        :active="isNavItemActive(route, item)"
        rounded="lg"
        class="sidebar-nav__item"
        active-class="sidebar-nav__item--active"
      >
        <template v-if="item.premium" #append>
          <v-chip size="x-small" color="amber-darken-2" variant="flat" class="font-weight-bold">
            {{ t('common.premium') }}
          </v-chip>
        </template>
      </v-list-item>
    </template>
  </v-list>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { isNavItemActive, navItemKey } from '../../utils/navActive.js'

const { t } = useI18n()

const SECTION_LABEL_KEYS = {
  learning: 'common.navSections.learning',
  planning: 'common.navSections.planning',
  account: 'common.navSections.account',
}

const props = defineProps({
  items: { type: Array, default: () => [] },
})

const route = useRoute()

function itemTitle(item) {
  if (item.titleKey) return t(item.titleKey)
  return item.title || ''
}

const navGroups = computed(() => {
  const groups = []
  let currentKey = null
  let currentItems = []

  const flush = () => {
    if (!currentItems.length) return
    groups.push({
      key: currentKey || 'default',
      label: SECTION_LABEL_KEYS[currentKey] ? t(SECTION_LABEL_KEYS[currentKey]) : '',
      items: currentItems,
    })
    currentItems = []
  }

  for (const item of props.items) {
    const sectionKey = item.section || null
    if (sectionKey !== currentKey) {
      flush()
      currentKey = sectionKey
    }
    currentItems.push(item)
  }
  flush()

  return groups.length ? groups : [{ key: 'default', label: '', items: props.items }]
})
</script>
