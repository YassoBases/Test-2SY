<template>
  <div class="payment-page">
    <div class="payment-page__scroll">
      <div class="payment-page__inner mx-auto">
        <OnboardingAccountHeader />
        <OnboardingStepper current="payment" />
        <h1 class="text-h5 font-weight-bold text-center mb-2">{{ t('auth.payment.title') }}</h1>
        <p class="text-body-2 text-medium-emphasis text-center mb-6">
          {{ t('auth.payment.subtitle') }}
        </p>

        <v-alert v-if="error" type="error" variant="tonal" class="mb-4">{{ error }}</v-alert>

        <div v-if="loading" class="text-center py-10">
          <v-progress-circular indeterminate color="primary" />
        </div>

        <template v-else-if="checkout?.items?.length">
          <v-card class="glass-card glass-card--elevated pa-4 pa-md-5 mb-5" variant="flat">
            <h3 class="text-subtitle-1 font-weight-bold mb-4">{{ t('auth.payment.summaryTitle') }}</h3>

            <article
              v-for="item in checkout.items"
              :key="item.id"
              class="checkout-item"
            >
              <div class="checkout-item__row">
                <TeacherAvatar
                  :name="item.teacher_name"
                  :image-url="item.teacher_image_url"
                  :size="48"
                />
                <div class="checkout-item__body flex-grow-1 min-width-0">
                  <p class="checkout-item__primary text-body-2 font-weight-bold mb-1">
                    {{ formatCourseLine(item) }}
                  </p>
                  <p v-if="item.summary" class="checkout-item__summary text-caption text-medium-emphasis mb-0">
                    {{ item.summary }}
                  </p>
                </div>
              </div>
            </article>

            <v-divider class="my-4" />
            <div class="d-flex justify-space-between align-center">
              <span class="text-subtitle-1 font-weight-bold">{{ t('auth.payment.total') }}</span>
              <span class="text-h6 font-weight-bold text-secondary">
                {{ formatSyrianPrice(checkout.total_amount) }}
              </span>
            </div>
          </v-card>

          <h3 class="text-subtitle-1 font-weight-bold mb-3">{{ t('auth.payment.methodTitle') }}</h3>
          <v-row class="mb-4">
            <v-col v-for="m in methods" :key="m.value" cols="6" sm="3">
              <button
                type="button"
                class="method-card"
                :class="{ 'method-card--active': method === m.value }"
                @click="method = m.value"
              >
                <v-icon
                  size="28"
                  :color="method === m.value ? 'secondary' : 'grey-lighten-1'"
                >
                  {{ m.icon }}
                </v-icon>
                <span class="method-card__label">{{ m.label }}</span>
              </button>
            </v-col>
          </v-row>

          <v-btn
            block
            size="x-large"
            rounded="lg"
            class="btn-glow mb-6 d-md-none"
            :loading="paying"
            :disabled="!canPay"
            @click="pay"
          >
            <v-icon start>mdi-lock-check</v-icon>
            {{ t('auth.payment.continuePay') }}
          </v-btn>
        </template>

        <v-alert v-else-if="!loading" type="info" variant="tonal">
          {{ t('auth.payment.emptyCheckout') }}
        </v-alert>

        <OnboardingNavFooter v-if="!loading" :back-to="ROUTES.ONBOARDING_TEACHERS" />
      </div>
    </div>

    <footer v-if="checkout?.items?.length" class="payment-footer">
      <div class="payment-footer__inner mx-auto">
        <div class="payment-footer__total">
          <span class="text-caption text-medium-emphasis">{{ t('auth.payment.footerTotal') }}</span>
          <span class="text-subtitle-1 font-weight-bold text-secondary">
            {{ formatSyrianPrice(checkout.total_amount) }}
          </span>
        </div>
        <v-btn
          block
          size="x-large"
          rounded="lg"
          class="btn-glow payment-footer__cta"
          :loading="paying"
          :disabled="!canPay"
          @click="pay"
        >
          <v-icon start>mdi-lock-check</v-icon>
          {{ t('auth.payment.continuePay') }}
        </v-btn>
        <p v-if="!method" class="text-caption text-center text-medium-emphasis mb-0 mt-1">
          {{ t('auth.payment.chooseMethodFirst') }}
        </p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import OnboardingAccountHeader from '../../components/onboarding/OnboardingAccountHeader.vue'
import OnboardingNavFooter from '../../components/onboarding/OnboardingNavFooter.vue'
import OnboardingStepper from '../../components/onboarding/OnboardingStepper.vue'
import TeacherAvatar from '../../components/onboarding/TeacherAvatar.vue'
import { fetchCheckout, demoCheckout } from '../../api/payments.js'
import { fetchMe } from '../../api/auth.js'
import { getErrorMessage } from '../../api/client.js'
import { ROUTES } from '../../constants/app.js'
import { formatCourseLine, formatSyrianPrice } from '../../utils/format.js'
import { getSession, setSession, isApiMode } from '../../utils/session.js'
import { mergeUserIntoSession } from '../../utils/studentFlow.js'
import { setLastPaymentResult } from '../../utils/paymentResult.js'

const { t } = useI18n()
const router = useRouter()
const checkout = ref(null)
const method = ref(null)
const paying = ref(false)
const loading = ref(true)
const error = ref('')

const METHOD_META = [
  { value: 'card', icon: 'mdi-credit-card-outline' },
  { value: 'transfer', icon: 'mdi-bank-transfer' },
  { value: 'wallet', icon: 'mdi-wallet-outline' },
  { value: 'cash', icon: 'mdi-cash-multiple' },
]

const methods = computed(() =>
  METHOD_META.map((meta) => ({
    ...meta,
    label: t(`auth.payment.methods.${meta.value}`),
  })),
)

const canPay = computed(
  () => Boolean(method.value && checkout.value?.items?.length && !paying.value),
)

onMounted(async () => {
  try {
    checkout.value = await fetchCheckout()
  } catch (e) {
    error.value = getErrorMessage(e, t('auth.payment.errors.loadCheckout'))
  } finally {
    loading.value = false
  }
})

async function pay() {
  if (!canPay.value) return
  paying.value = true
  error.value = ''
  try {
    const result = await demoCheckout(method.value)
    setLastPaymentResult({
      reference: result.reference,
      total_amount: result.total_amount ?? checkout.value?.total_amount,
      currency: result.currency ?? checkout.value?.currency ?? 'SYP',
      unlocked_items: result.unlocked_items ?? checkout.value?.items ?? [],
    })

    let session = mergeUserIntoSession(getSession(), {
      needs_payment: false,
      payment_complete: true,
      onboarding_complete: true,
    })

    if (isApiMode()) {
      try {
        const me = await fetchMe()
        session = mergeUserIntoSession(session, me)
      } catch {
        /* keep local flags */
      }
    }
    setSession(session)

    await router.push(ROUTES.STUDENT_PAYMENT_SUCCESS)
  } catch (e) {
    error.value = getErrorMessage(e, t('auth.payment.errors.payFailed'))
  } finally {
    paying.value = false
  }
}
</script>

<style scoped>
.payment-page {
  min-height: 100dvh;
  display: flex;
  flex-direction: column;
  position: relative;
}

.payment-page__scroll {
  flex: 1;
  overflow-y: auto;
  padding: 2rem 1rem 10rem;
}

.payment-page__inner {
  max-width: 560px;
}

.checkout-item {
  padding: 1rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.checkout-item:last-of-type {
  border-bottom: none;
}

.checkout-item__row {
  display: flex;
  align-items: flex-start;
  gap: 0.85rem;
}

.checkout-item__primary {
  color: rgba(232, 236, 255, 0.95);
  line-height: 1.55;
}

.checkout-item__summary {
  line-height: 1.5;
}

.method-card {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  padding: 1rem 0.5rem;
  border-radius: 14px;
  cursor: pointer;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(15, 18, 35, 0.72);
  backdrop-filter: blur(16px);
  transition:
    transform 0.25s ease,
    border-color 0.25s ease,
    box-shadow 0.25s ease;
}

.method-card:hover {
  transform: translateY(-3px);
  border-color: rgba(124, 108, 240, 0.45);
  box-shadow: 0 8px 28px rgba(124, 108, 240, 0.18);
}

.method-card--active {
  border-color: rgba(34, 211, 238, 0.6) !important;
  box-shadow:
    0 0 32px rgba(34, 211, 238, 0.28),
    inset 0 0 0 1px rgba(34, 211, 238, 0.2);
}

.method-card__label {
  font-size: 0.72rem;
  font-weight: 600;
  color: rgba(220, 228, 255, 0.92);
  text-align: center;
}

.payment-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 2400;
  padding: 1rem 1.25rem calc(1rem + env(safe-area-inset-bottom, 0px));
  background: rgba(10, 12, 24, 0.92);
  backdrop-filter: blur(20px);
  border-top: 1px solid rgba(124, 108, 240, 0.25);
  box-shadow: 0 -16px 48px rgba(0, 0, 0, 0.55);
}

.payment-footer__inner {
  max-width: 560px;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.payment-footer__total {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.min-width-0 {
  min-width: 0;
}

@media (min-width: 960px) {
  .payment-page__scroll {
    padding-bottom: 7rem;
  }
}
</style>
