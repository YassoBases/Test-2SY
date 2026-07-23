<template>
  <section class="g4-section" aria-labelledby="g4-explain-title">
    <h2 id="g4-explain-title" class="g4-section__title">
      {{ t('student.grammarV4.explain.title') }}
    </h2>

    <div class="block">
      <h3 class="block__lang">{{ t('student.grammarV4.explain.english') }}</h3>
      <div v-for="p in englishBlocks" :key="p.key" class="block__card">
        <h4>{{ t(p.titleKey) }}</h4>
        <ul v-if="p.list?.length" class="eng-island" dir="ltr">
          <li v-for="(item, i) in p.list" :key="i">{{ item }}</li>
        </ul>
        <div v-else-if="p.mistakes?.length" class="eng-island" dir="ltr">
          <div v-for="(m, i) in p.mistakes" :key="i" class="mistake">
            <div class="mistake__bad">{{ m.incorrect }}</div>
            <div class="mistake__good">{{ m.correct }}</div>
          </div>
        </div>
        <p v-else class="eng-island" dir="ltr">{{ p.body }}</p>
        <AppButton
          v-if="p.body"
          variant="ghost"
          size="small"
          prepend-icon="mdi-volume-high"
          @click="$emit('play', p.body, 'en-US')"
        >
          {{ t('student.grammarV4.playAudio') }}
        </AppButton>
      </div>
    </div>

    <div class="block">
      <h3 class="block__lang">{{ t('student.grammarV4.explain.arabic') }}</h3>
      <div class="block__card" dir="rtl">
        <v-progress-linear v-if="arabicLoading" indeterminate color="primary" class="mb-3" />
        <v-alert v-else-if="arabicError" type="error" variant="tonal" class="mb-3 rounded-lg">
          {{ arabicError }}
          <AppButton class="mt-2" variant="secondary" size="small" @click="$emit('retry-arabic')">
            {{ t('student.grammarV4.retry') }}
          </AppButton>
        </v-alert>
        <p v-else-if="arabicText" class="arabic-body">{{ arabicText }}</p>
        <p v-else class="muted">{{ t('student.grammarV4.explain.arabicPending') }}</p>
        <AppButton
          v-if="arabicText"
          variant="ghost"
          size="small"
          prepend-icon="mdi-volume-high"
          @click="$emit('play', arabicText, 'ar-SA')"
        >
          {{ t('student.grammarV4.playAudio') }}
        </AppButton>
      </div>
    </div>
  </section>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import AppButton from '../ui/AppButton.vue'

defineProps({
  englishBlocks: { type: Array, default: () => [] },
  arabicText: { type: String, default: '' },
  arabicLoading: { type: Boolean, default: false },
  arabicError: { type: String, default: '' },
})

defineEmits(['play', 'retry-arabic'])
const { t } = useI18n()
</script>

<style scoped>
.g4-section__title {
  margin: 0 0 20px;
  font-size: 1.5rem;
  font-family: var(--font-display, Tajawal, sans-serif);
}

.block {
  margin-block-end: 28px;
}

.block__lang {
  margin: 0 0 12px;
  font-size: 1.05rem;
}

.block__card {
  padding: 20px 22px;
  border-radius: 16px;
  background: var(--surface-elevated, #fff);
  margin-block-end: 12px;
}

.block__card h4 {
  margin: 0 0 10px;
  font-size: 0.95rem;
  color: var(--text-muted, #3f4f63);
}

.block__card p,
.arabic-body {
  margin: 0 0 12px;
  font-size: 1.1rem;
  line-height: 1.7;
}

.block__card ul {
  margin: 0 0 12px;
  padding-inline-start: 1.2rem;
  line-height: 1.65;
}

.mistake {
  margin-block-end: 10px;
}

.mistake__bad {
  color: #ef4444;
}

.mistake__good {
  color: #10b981;
}

.muted {
  color: var(--text-muted, #3f4f63);
}

.eng-island {
  unicode-bidi: isolate;
}
</style>
