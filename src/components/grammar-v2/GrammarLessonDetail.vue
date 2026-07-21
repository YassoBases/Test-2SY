<template>
  <div class="lesson-detail">
    <div class="lesson-detail__toolbar">
      <AppButton variant="ghost" prepend-icon="mdi-arrow-left" @click="$emit('back')">
        {{ t('student.grammarV2.lesson.back') }}
      </AppButton>
      <div class="lesson-detail__chips">
        <span v-if="lesson.grammar_target" class="chip eng-island" dir="ltr">
          {{ lesson.grammar_target }}
        </span>
        <span v-if="lesson.estimated_minutes != null" class="chip">
          {{ t('student.grammarV2.common.minutes', { n: lesson.estimated_minutes }) }}
        </span>
      </div>
    </div>

    <ul v-if="skills.length" class="lesson-detail__skills">
      <li v-for="skill in skills" :key="skill" class="eng-island" dir="ltr">{{ skill }}</li>
    </ul>

    <AppCard
      v-for="section in sections"
      :key="section.key"
      class="lesson-detail__section"
      solid
      padding="lg"
    >
      <h2 class="lesson-detail__section-title">{{ section.title }}</h2>
      <template v-if="section.kind === 'text'">
        <p class="lesson-detail__body eng-island" dir="ltr">{{ section.body }}</p>
      </template>
      <ol v-else-if="section.kind === 'list'" class="lesson-detail__list eng-island" dir="ltr">
        <li v-for="(item, i) in section.items" :key="i">{{ item }}</li>
      </ol>
      <ul v-else-if="section.kind === 'ul'" class="lesson-detail__list eng-island" dir="ltr">
        <li v-for="(item, i) in section.items" :key="i">{{ item }}</li>
      </ul>
      <div v-else-if="section.kind === 'mistakes'" class="eng-island" dir="ltr">
        <div v-for="(m, i) in section.items" :key="i" class="mistake">
          <div class="mistake__bad">{{ m.incorrect }}</div>
          <div class="mistake__good">{{ m.correct }}</div>
        </div>
      </div>
      <div v-else-if="section.kind === 'chips'" class="lesson-detail__chip-row eng-island" dir="ltr">
        <span v-for="(p, i) in section.items" :key="i" class="chip">{{ p }}</span>
      </div>
    </AppCard>

    <div class="lesson-detail__actions">
      <AppButton
        variant="primary"
        size="large"
        :loading="completing"
        @click="$emit('finish')"
      >
        {{ t('student.grammarV2.lesson.finish') }}
      </AppButton>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import AppCard from '../ui/AppCard.vue'
import AppButton from '../ui/AppButton.vue'

const props = defineProps({
  lesson: { type: Object, required: true },
  skills: { type: Array, default: () => [] },
  completing: { type: Boolean, default: false },
})

defineEmits(['back', 'finish'])
const { t } = useI18n()

const sections = computed(() => {
  const L = props.lesson || {}
  const out = []
  if (L.lesson_goal) {
    out.push({
      key: 'goal',
      kind: 'text',
      title: t('student.grammarV2.lesson.goal'),
      body: L.lesson_goal,
    })
  }
  if (L.teacher_opening) {
    out.push({
      key: 'explain',
      kind: 'text',
      title: t('student.grammarV2.lesson.explanation'),
      body: L.teacher_opening,
    })
  }
  if (L.warmup) {
    out.push({
      key: 'warmup',
      kind: 'text',
      title: t('student.grammarV2.lesson.warmup'),
      body: L.warmup,
    })
  }
  if (L.main_activity) {
    out.push({
      key: 'main',
      kind: 'text',
      title: t('student.grammarV2.lesson.mainActivity'),
      body: L.main_activity,
    })
  }
  if (L.follow_up_questions?.length) {
    out.push({
      key: 'questions',
      kind: 'list',
      title: t('student.grammarV2.lesson.followUp'),
      items: L.follow_up_questions,
    })
  }
  if (L.teacher_hints?.length) {
    out.push({
      key: 'hints',
      kind: 'ul',
      title: t('student.grammarV2.lesson.hints'),
      items: L.teacher_hints,
    })
  }
  if (L.common_mistakes?.length) {
    out.push({
      key: 'mistakes',
      kind: 'mistakes',
      title: t('student.grammarV2.lesson.mistakes'),
      items: L.common_mistakes,
    })
  }
  if (L.expected_patterns?.length) {
    out.push({
      key: 'patterns',
      kind: 'chips',
      title: t('student.grammarV2.lesson.patterns'),
      items: L.expected_patterns,
    })
  }
  if (L.completion_message) {
    out.push({
      key: 'reflect',
      kind: 'text',
      title: t('student.grammarV2.lesson.reflection'),
      body: L.completion_message,
    })
  }
  return out
})
</script>

<style scoped>
.lesson-detail__toolbar {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 12px;
  margin-block-end: 16px;
}

.lesson-detail__chips,
.lesson-detail__chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chip {
  padding: 4px 10px;
  border-radius: 10px;
  background: color-mix(in srgb, var(--color-primary, #6366f1) 12%, transparent);
  font-size: 0.8125rem;
}

.lesson-detail__skills {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  list-style: none;
  margin: 0 0 16px;
  padding: 0;
}

.lesson-detail__skills li {
  padding: 6px 12px;
  border-radius: 12px;
  background: rgba(59, 130, 246, 0.12);
  font-size: 0.8125rem;
}

.lesson-detail__section {
  margin-block-end: 16px;
}

.lesson-detail__section-title {
  margin: 0 0 10px;
  font-size: 1.05rem;
}

.lesson-detail__body {
  margin: 0;
  line-height: 1.6;
}

.lesson-detail__list {
  margin: 0;
  padding-inline-start: 1.25rem;
}

.mistake {
  margin-block-end: 10px;
}

.mistake__bad {
  color: #ef4444;
  font-size: 0.875rem;
}

.mistake__good {
  color: #10b981;
  font-size: 0.875rem;
}

.lesson-detail__actions {
  margin-block-start: 8px;
}

.eng-island {
  unicode-bidi: isolate;
}
</style>
