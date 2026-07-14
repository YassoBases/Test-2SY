<template>

  <v-dialog

    :model-value="modelValue"

    :max-width="maxWidth"

    :persistent="persistent"

    :scrollable="scrollable"

    :transition="transition"

    @update:model-value="$emit('update:modelValue', $event)"

  >

    <v-card class="tds-scope tds-dialog" variant="flat">

      <TeacherWorkspaceShell mode="dialog">

        <template v-if="$slots.header || closable" #header>

          <slot name="header" />

        </template>



        <template v-if="closable" #header-actions>

          <slot name="header-actions">

            <v-btn

              icon

              variant="text"

              :disabled="closeDisabled"

              :aria-label="$t('common.close')"

              @click="close"

            >

              <v-icon>mdi-close</v-icon>

            </v-btn>

          </slot>

        </template>



        <div class="tds-dialog__content">

          <slot />

        </div>



        <template v-if="$slots.footer" #footer>

          <slot name="footer" />

        </template>

      </TeacherWorkspaceShell>

    </v-card>

  </v-dialog>

</template>



<script setup>
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import TeacherWorkspaceShell from './TeacherWorkspaceShell.vue'



const props = defineProps({

  modelValue: { type: Boolean, default: false },

  maxWidth: { type: [Number, String], default: 760 },

  persistent: { type: Boolean, default: false },

  scrollable: { type: Boolean, default: true },

  closable: { type: Boolean, default: true },

  closeDisabled: { type: Boolean, default: false },

  transition: { type: String, default: 'dialog-bottom-transition' },

})



const emit = defineEmits(['update:modelValue', 'close'])



function close() {

  if (!props.closeDisabled) {

    emit('update:modelValue', false)

    emit('close')

  }

}

</script>

