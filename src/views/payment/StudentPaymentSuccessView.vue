<template>
  <div class="success-page">
    <div class="success-page__inner mx-auto text-center">
      <div class="success-ring" aria-hidden="true">
        <div class="success-ring__pulse" />
        <div class="success-ring__core">
          <v-icon size="56" color="secondary">mdi-check-decagram</v-icon>
        </div>
      </div>

      <h1 class="text-h5 font-weight-bold mb-2 success-title">{{ t('auth.payment.success.title') }}</h1>
      <p class="text-body-2 text-medium-emphasis mb-2">
        {{ t('auth.payment.success.subtitle') }}
      </p>
      <p v-if="payment?.reference" class="text-caption text-medium-emphasis mb-6">
        {{ t('auth.payment.success.reference', { reference: payment.reference }) }}
      </p>

      <v-card
        v-if="unlocked.length"
        class="glass-card glass-card--elevated pa-4 mb-6 text-start"
        variant="flat"
      >
        <h3 class="text-subtitle-2 font-weight-bold mb-3 d-flex align-center gap-2">
          <v-icon size="20" color="secondary">mdi-book-lock-open-outline</v-icon>
          {{ t('auth.payment.success.unlockedTitle') }}
        </h3>
        <div
          v-for="item in unlocked"
          :key="item.id"
          class="unlocked-row d-flex align-center gap-3 py-2"
        >
          <TeacherAvatar
            :name="item.teacher_name"
            :image-url="item.teacher_image_url"
            :size="40"
          />
          <div class="flex-grow-1 min-width-0">
            <div class="text-body-2 font-weight-medium">{{ formatCourseLine(item) }}</div>
          </div>
          <v-icon color="success" size="22">mdi-check-circle</v-icon>
        </div>
        <v-divider class="my-3" />
        <div class="d-flex justify-space-between text-subtitle-2 font-weight-bold">
          <span>{{ t('auth.payment.success.paidTotal') }}</span>
          <span class="text-secondary">{{ formatSyrianPrice(payment?.total_amount) }}</span>
        </div>
      </v-card>

      <v-btn
        size="x-large"
        rounded="lg"
        class="btn-glow px-10 success-cta"
        @click="goDashboard"
      >
        <v-icon start>mdi-rocket-launch-outline</v-icon>
        {{ t('auth.payment.success.goDashboard') }}
      </v-btn>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import TeacherAvatar from '../../components/onboarding/TeacherAvatar.vue'
import { ROUTES } from '../../constants/app.js'
import { fetchMe } from '../../api/auth.js'
import { formatCourseLine, formatSyrianPrice } from '../../utils/format.js'
import { getLastPaymentResult } from '../../utils/paymentResult.js'
import { getSession, isApiMode, setSession } from '../../utils/session.js'
import { mergeUserIntoSession } from '../../utils/studentFlow.js'

const { t } = useI18n()
const router = useRouter()
const payment = getLastPaymentResult()

const unlocked = computed(() => payment?.unlocked_items ?? [])

onMounted(() => {
  document.documentElement.classList.add('payment-success-active')
  document.body.classList.add('payment-success-active')
})

onUnmounted(() => {
  document.documentElement.classList.remove('payment-success-active')
  document.body.classList.remove('payment-success-active')
})

async function goDashboard() {
  if (isApiMode()) {
    try {
      const me = await fetchMe()
      setSession(mergeUserIntoSession(getSession(), me))
    } catch {
      setSession(
        mergeUserIntoSession(getSession(), {
          needs_payment: false,
          payment_complete: true,
          onboarding_complete: true,
        }),
      )
    }
  }
  await router.push(ROUTES.STUDENT_COURSES)
}
</script>

<style scoped>
.success-page {
  min-height: 100dvh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 1rem;
}

.success-page__inner {
  max-width: 480px;
  width: 100%;
}

.success-ring {
  position: relative;
  width: 128px;
  height: 128px;
  margin: 0 auto 1.75rem;
}

.success-ring__pulse {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(34, 211, 238, 0.35), transparent 68%);
  animation: success-pulse 2.2s ease-in-out infinite;
}

.success-ring__core {
  position: relative;
  z-index: 1;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(15, 18, 35, 0.75);
  border: 2px solid rgba(34, 211, 238, 0.45);
  box-shadow:
    0 0 48px rgba(124, 108, 240, 0.4),
    0 0 80px rgba(34, 211, 238, 0.2);
  animation: success-pop 0.65s cubic-bezier(0.34, 1.4, 0.64, 1) both;
}

.success-title {
  animation: success-fade 0.5s ease 0.15s both;
}

.success-cta {
  animation: success-fade 0.5s ease 0.35s both;
}

.unlocked-row + .unlocked-row {
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

@keyframes success-pulse {
  0%,
  100% {
    transform: scale(1);
    opacity: 0.85;
  }
  50% {
    transform: scale(1.12);
    opacity: 0.45;
  }
}

@keyframes success-pop {
  from {
    transform: scale(0.6);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes success-fade {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.min-width-0 {
  min-width: 0;
}
</style>

<style>
html.payment-success-active,
body.payment-success-active {
  overflow: hidden;
}
</style>
