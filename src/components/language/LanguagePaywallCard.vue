<template>
  <v-card class="glass-card glass-card--elevated pa-6" variant="flat">
    <div class="d-flex align-center gap-3 mb-4">
      <v-avatar color="secondary" variant="tonal" size="48">
        <v-icon>mdi-translate</v-icon>
      </v-avatar>
      <div>
        <div class="text-h6 font-weight-bold">Learn English</div>
        <v-chip v-if="status === 'expiring_soon'" color="warning" size="small" variant="flat" class="mt-1">
          Ends soon
        </v-chip>
        <v-chip v-else-if="status === 'expired'" color="error" size="small" variant="flat" class="mt-1">
          finished
        </v-chip>
        <v-chip v-else color="amber-darken-2" size="small" variant="flat" class="mt-1">
          distinct
        </v-chip>
      </div>
    </div>

    <p v-if="product?.description_ar" class="text-body-2 text-medium-emphasis mb-4">
      {{ product.description_ar }}
    </p>
    <p v-else class="text-body-2 text-medium-emphasis mb-4">
      An annual subscription that includes a placement test and a personalized course in reading, listening, writing, and speaking.
    </p>

    <ul class="text-body-2 mb-6 ps-6">
      <li>Level test for four skills</li>
      <li>Custom learning path</li>
      <li>Continue Guardian</li>
    </ul>

    <div v-if="product" class="text-h5 font-weight-bold text-secondary mb-4">
      {{ formatPrice(product.price, product.currency) }}
      <span class="text-caption text-medium-emphasis"> / {{ product.term_days }} day</span>
    </div>

    <v-btn block size="large" rounded="lg" class="btn-glow" :loading="loading" @click="$emit('subscribe')">
      <v-icon start>mdi-credit-card</v-icon>
      {{ status === 'expired' || status === 'expiring_soon' ? 'Subscription renewal' : 'Subscribe now' }}
    </v-btn>
  </v-card>
</template>

<script setup>
defineProps({
  product: { type: Object, default: null },
  status: { type: String, default: 'pending' },
  loading: { type: Boolean, default: false },
})

defineEmits(['subscribe'])

function formatPrice(amount, currency = 'SYP') {
  if (currency === 'SYP') {
    return new Intl.NumberFormat('de-DE').format(amount) + ' L.S'
  }
  return `${amount} ${currency}`
}
</script>
