<template>
  <div>
    <div v-for="q in questions" :key="q.id" class="mb-6">
      <div class="text-body-1 font-weight-medium mb-2">{{ q.stem }}</div>
      <v-radio-group
        :model-value="answers[q.id]"
        @update:model-value="(v) => setAnswer(q.id, v)"
      >
        <v-radio
          v-for="(choice, idx) in q.choices || []"
          :key="idx"
          :label="String(choice)"
          :value="idx"
        />
      </v-radio-group>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  questions: { type: Array, default: () => [] },
  answers: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['update:answers'])

function setAnswer(qid, idx) {
  emit('update:answers', { ...props.answers, [qid]: idx })
}
</script>
