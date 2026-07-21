<template>
  <article class="content-card" :class="{ 'content-card--island': engIsland }">
    <h3 v-if="title" class="content-card__title">{{ title }}</h3>
    <div class="content-card__body" :dir="engIsland ? 'ltr' : undefined">
      <slot />
    </div>
  </article>
</template>

<script setup>
defineProps({
  title: { type: String, default: '' },
  engIsland: { type: Boolean, default: true },
})
</script>

<style scoped>
.content-card {
  padding: 20px 22px;
  border-radius: 16px;
  background: color-mix(in srgb, var(--color-primary, #6366f1) 6%, var(--surface-elevated, #fff));
}

.content-card__title {
  margin: 0 0 10px;
  font-size: 0.95rem;
  font-weight: 700;
}

.content-card__body {
  margin: 0;
  font-size: 1.05rem;
  line-height: 1.65;
}

.content-card--island .content-card__body {
  unicode-bidi: isolate;
}
</style>
