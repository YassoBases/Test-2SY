<template>
  <div class="grammar-review">
    <h1 class="grammar-review__title">{{ t('student.grammarV2.review.title') }}</h1>

    <AppEmptyState
      v-if="!groups.length"
      icon="mdi-book-open-page-variant-outline"
      :title="t('student.grammarV2.review.empty')"
      :description="t('student.grammarV2.review.emptyHint')"
      :action-label="t('student.grammarV2.review.backHome')"
      :action-to="homeTo"
    />

    <section v-for="group in groups" :key="group.cefr" class="grammar-review__group">
      <h2 class="grammar-review__cefr eng-island" dir="ltr">{{ group.cefr }}</h2>
      <div class="grammar-review__grid">
        <GrammarStageCard
          v-for="stage in group.stages"
          :key="stage.grammar_id"
          :stage="stage"
          @select="$emit('select-stage', $event)"
        />
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import AppEmptyState from '../ui/AppEmptyState.vue'
import GrammarStageCard from './GrammarStageCard.vue'
import { ROUTES } from '../../constants/app.js'

const props = defineProps({
  completedByLevel: { type: Object, default: () => ({}) },
})

defineEmits(['select-stage'])
const { t } = useI18n()
const homeTo = ROUTES.STUDENT_GRAMMAR
const CEFR_ORDER = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']

const groups = computed(() =>
  CEFR_ORDER.filter((cefr) => (props.completedByLevel[cefr] || []).length).map((cefr) => ({
    cefr,
    stages: props.completedByLevel[cefr],
  })),
)
</script>

<style scoped>
.grammar-review__title {
  margin: 0 0 20px;
  font-size: 1.5rem;
}

.grammar-review__group {
  margin-block-end: 28px;
}

.grammar-review__cefr {
  margin: 0 0 12px;
  font-size: 1.25rem;
  color: var(--color-primary-deep, #4f46e5);
}

.grammar-review__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 12px;
}

.eng-island {
  unicode-bidi: isolate;
}
</style>
