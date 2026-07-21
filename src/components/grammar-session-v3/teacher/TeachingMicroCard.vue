<template>
  <article class="micro-card">
    <header class="micro-card__head">
      <span class="micro-card__kind">{{ kindLabel }}</span>
      <span class="micro-card__step">
        {{ t('student.grammarTeacher.cards.step', { current: index + 1, total }) }}
      </span>
    </header>

    <TeacherMessage :name="teacherName" :voice-state="voiceState" compact>
      <p>{{ card.teacherLine }}</p>
    </TeacherMessage>

    <div class="micro-card__content eng-island" dir="ltr">
      <template v-if="card.kind === 'checkpoint'">
        <p class="micro-card__bad">{{ card.incorrect }}</p>
        <p class="micro-card__good">{{ card.correct }}</p>
      </template>
      <p v-else>{{ card.body }}</p>
    </div>

    <div class="micro-card__actions">
      <AppButton
        variant="secondary"
        prepend-icon="mdi-chat-question-outline"
        @click="$emit('ask')"
      >
        {{ t('student.grammarTeacher.ask.cta') }}
      </AppButton>
      <AppButton
        v-if="!isLast"
        variant="primary"
        append-icon="mdi-arrow-right"
        @click="$emit('next-card')"
      >
        {{ t('student.grammarTeacher.cards.next') }}
      </AppButton>
      <p v-else class="micro-card__done">
        {{ t('student.grammarTeacher.cards.doneHint') }}
      </p>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import AppButton from '../../ui/AppButton.vue'
import TeacherMessage from './TeacherMessage.vue'

const props = defineProps({
  card: { type: Object, required: true },
  index: { type: Number, default: 0 },
  total: { type: Number, default: 1 },
  isLast: { type: Boolean, default: false },
  teacherName: { type: String, default: 'Alex' },
  voiceState: { type: String, default: 'idle' },
})

defineEmits(['ask', 'next-card'])
const { t } = useI18n()

const kindLabel = computed(() =>
  t(props.card.titleKey || 'student.grammarTeacher.cards.concept'),
)
</script>

<style scoped>
.micro-card {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 8px 0;
}

.micro-card__head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.micro-card__kind {
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--color-primary-deep, #4f46e5);
}

.micro-card__step {
  font-size: 0.8rem;
  color: var(--text-muted, #3f4f63);
}

.micro-card__content {
  padding: 22px 24px;
  border-radius: 16px;
  background: var(--surface-elevated, #fff);
  font-size: 1.2rem;
  line-height: 1.6;
  box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--text-muted, #3f4f63) 12%, transparent);
}

.micro-card__content p {
  margin: 0;
}

.micro-card__bad {
  color: #ef4444;
  margin-block-end: 8px !important;
}

.micro-card__good {
  color: #10b981;
}

.micro-card__actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
}

.micro-card__done {
  margin: 0;
  font-size: 0.875rem;
  color: var(--text-muted, #3f4f63);
}

.eng-island {
  unicode-bidi: isolate;
}
</style>
