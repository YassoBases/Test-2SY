<template>
  <section class="g4-section" aria-labelledby="g4-examples-title">
    <div class="g4-section__head">
      <h2 id="g4-examples-title" class="g4-section__title">
        {{ t('student.grammarV4.examples.title') }}
      </h2>
      <AppButton
        variant="primary"
        :loading="loading"
        prepend-icon="mdi-auto-fix"
        @click="$emit('more', 'daily')"
      >
        {{ t('student.grammarV4.examples.more') }}
      </AppButton>
    </div>

    <v-alert v-if="error" type="error" variant="tonal" class="mb-4 rounded-lg">{{ error }}</v-alert>

    <div v-for="cat in categories" :key="cat.key" class="cat">
      <h3>{{ t(cat.labelKey) }}</h3>
      <div
        v-for="ex in groups[cat.key] || []"
        :key="ex.id"
        class="ex"
      >
        <p class="ex__en eng-island" dir="ltr">{{ ex.en }}</p>
        <p v-if="ex.ar" class="ex__ar" dir="rtl">{{ ex.ar }}</p>
        <p class="ex__why">{{ ex.explanation }}</p>
        <AppButton
          variant="ghost"
          size="small"
          prepend-icon="mdi-volume-high"
          @click="$emit('play', ex.en, 'en-US')"
        >
          {{ t('student.grammarV4.playAudio') }}
        </AppButton>
      </div>
      <AppButton
        variant="secondary"
        size="small"
        class="cat__more"
        :loading="loading"
        @click="$emit('more', cat.key)"
      >
        {{ t('student.grammarV4.examples.moreIn', { cat: t(cat.labelKey) }) }}
      </AppButton>
    </div>
  </section>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import AppButton from '../ui/AppButton.vue'

defineProps({
  groups: { type: Object, default: () => ({}) },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
})

defineEmits(['more', 'play'])
const { t } = useI18n()

const categories = [
  { key: 'easy', labelKey: 'student.grammarV4.examples.easy' },
  { key: 'daily', labelKey: 'student.grammarV4.examples.daily' },
  { key: 'school', labelKey: 'student.grammarV4.examples.school' },
  { key: 'university', labelKey: 'student.grammarV4.examples.university' },
  { key: 'work', labelKey: 'student.grammarV4.examples.work' },
  { key: 'travel', labelKey: 'student.grammarV4.examples.travel' },
  { key: 'mistakes', labelKey: 'student.grammarV4.examples.mistakes' },
]
</script>

<style scoped>
.g4-section__head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-block-end: 16px;
}

.g4-section__title {
  margin: 0;
  font-size: 1.5rem;
  font-family: var(--font-display, Tajawal, sans-serif);
}

.cat {
  margin-block-end: 28px;
}

.cat h3 {
  margin: 0 0 12px;
  font-size: 1.05rem;
}

.ex {
  padding: 18px 20px;
  border-radius: 16px;
  background: var(--surface-elevated, #fff);
  margin-block-end: 10px;
}

.ex__en {
  margin: 0 0 8px;
  font-size: 1.15rem;
  font-weight: 600;
  line-height: 1.5;
}

.ex__ar {
  margin: 0 0 8px;
  font-size: 1.05rem;
  line-height: 1.6;
}

.ex__why {
  margin: 0 0 8px;
  font-size: 0.9rem;
  color: var(--text-muted, #3f4f63);
}

.cat__more {
  margin-block-start: 4px;
}

.eng-island {
  unicode-bidi: isolate;
}
</style>
