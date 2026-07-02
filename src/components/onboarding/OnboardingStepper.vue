<template>
  <div class="onboarding-stepper mb-6">
    <div class="d-flex justify-center gap-2 flex-wrap">
      <div
        v-for="(s, i) in steps"
        :key="s.key"
        class="step-pill"
        :class="{
          'step-pill--active': i === currentIndex,
          'step-pill--done': i < currentIndex,
        }"
      >
        <span class="step-pill__num">{{ i + 1 }}</span>
        <span class="step-pill__label">{{ s.label }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  current: { type: String, required: true },
})

const { t } = useI18n()

const stepKeys = ['grade', 'personalize', 'subjects', 'teachers']
const stepIndexMap = { grade: 0, personalize: 1, subjects: 2, teachers: 3 }

const steps = computed(() =>
  stepKeys.map((key) => ({
    key,
    label: t(`auth.onboarding.stepper.${key}`),
  })),
)

const currentIndex = computed(() => stepIndexMap[props.current] ?? 0)
</script>

<style scoped>
.step-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(232, 236, 255, 0.45);
  font-size: 0.75rem;
  transition: all 0.25s ease;
}

.step-pill--active {
  border-color: rgba(34, 211, 238, 0.45);
  color: var(--em-cyan);
  background: rgba(34, 211, 238, 0.08);
  box-shadow: 0 0 20px rgba(34, 211, 238, 0.15);
}

.step-pill--done {
  border-color: rgba(124, 108, 240, 0.35);
  color: rgba(232, 236, 255, 0.7);
}

.step-pill__num {
  width: 1.25rem;
  height: 1.25rem;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.65rem;
  font-weight: 700;
  background: rgba(255, 255, 255, 0.08);
}
</style>
