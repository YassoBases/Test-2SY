<template>
  <section class="account-security mb-6">
    <div class="d-flex align-center justify-space-between flex-wrap gap-2 mb-4">
      <div class="d-flex align-center gap-2">
        <v-icon color="secondary">mdi-shield-account</v-icon>
        <h3 class="text-h6 font-weight-bold mb-0">{{ t('settings.security.title') }}</h3>
      </div>
      <v-chip
        v-if="account && !loading"
        size="small"
        :color="account.email_verified ? 'success' : 'warning'"
        variant="tonal"
        prepend-icon="mdi-shield-check"
      >
        {{ account.email_verified ? t('settings.security.accountSecure') : t('settings.security.emailVerificationRequired') }}
      </v-chip>
    </div>

    <v-card class="glass-card pa-5 pa-md-6 mb-4" variant="flat">
      <div v-if="loading && !account" class="py-6 text-center">
        <v-progress-circular indeterminate color="primary" size="32" />
      </div>

      <template v-else-if="account">
        <div class="account-info-grid mb-5">
          <div class="info-pill">
            <div class="info-pill__label">{{ t('settings.security.currentEmail') }}</div>
            <div class="info-pill__value text-truncate">{{ account.email }}</div>
          </div>
          <div class="info-pill">
            <div class="info-pill__label">{{ t('settings.security.verificationStatus') }}</div>
            <div class="info-pill__value d-flex align-center gap-2 flex-wrap">
              <v-chip
                size="x-small"
                :color="account.email_verified ? 'success' : 'warning'"
                variant="flat"
              >
                {{ account.email_verified ? t('settings.security.verified') : t('settings.security.notVerified') }}
              </v-chip>
            </div>
          </div>
          <div class="info-pill">
            <div class="info-pill__label">{{ t('settings.security.accountType') }}</div>
            <div class="info-pill__value">{{ roleLabel(account.role) }}</div>
          </div>
          <div class="info-pill">
            <div class="info-pill__label">{{ t('settings.security.createdAt') }}</div>
            <div class="info-pill__value">{{ formatCreatedAt(account.created_at) }}</div>
          </div>
        </div>

        <v-alert
          v-if="!account.email_verified"
          type="warning"
          variant="tonal"
          density="comfortable"
          class="mb-5 rounded-lg verification-banner"
        >
          <div class="d-flex flex-column flex-sm-row align-sm-center justify-space-between gap-3">
            <div>
              <div class="font-weight-bold mb-1">{{ t('settings.security.emailNotVerifiedTitle') }}</div>
              <div class="text-body-2">
                {{ t('settings.security.emailNotVerifiedBody') }}
              </div>
            </div>
            <v-btn
              color="primary"
              variant="flat"
              rounded="lg"
              prepend-icon="mdi-email-sync"
              :loading="resendingVerification"
              @click="handleResendVerification"
            >
              {{ t('settings.security.resendConfirmation') }}
            </v-btn>
          </div>
        </v-alert>

        <v-divider class="mb-5 opacity-20" />

        <v-row>
          <v-col cols="12" md="6">
            <h4 class="text-subtitle-1 font-weight-bold mb-3 d-flex align-center gap-2">
              <v-icon size="20">mdi-email-edit-outline</v-icon>
              {{ t('settings.security.changeEmailTitle') }}
            </h4>
            <v-text-field
              v-model="emailForm.newEmail"
              :label="t('settings.security.newEmailLabel')"
              type="email"
              variant="outlined"
              density="comfortable"
              autocomplete="email"
              :error-messages="emailErrors.newEmail"
              class="mb-2"
            />
            <v-text-field
              v-model="emailForm.currentPassword"
              :label="t('settings.security.currentPasswordConfirm')"
              :type="showEmailPassword ? 'text' : 'password'"
              variant="outlined"
              density="comfortable"
              autocomplete="current-password"
              :error-messages="emailErrors.currentPassword"
              :append-inner-icon="showEmailPassword ? 'mdi-eye-off' : 'mdi-eye'"
              class="mb-3"
              @click:append-inner="showEmailPassword = !showEmailPassword"
            />
            <v-btn
              class="btn-glow"
              rounded="lg"
              :loading="savingEmail"
              @click="submitEmail"
            >
              {{ t('settings.security.saveNewEmail') }}
            </v-btn>
          </v-col>

          <v-col cols="12" md="6">
            <h4 class="text-subtitle-1 font-weight-bold mb-3 d-flex align-center gap-2">
              <v-icon size="20">mdi-lock-reset</v-icon>
              {{ t('settings.security.changePasswordTitle') }}
            </h4>
            <v-text-field
              v-model="passwordForm.currentPassword"
              :label="t('settings.security.currentPassword')"
              :type="showCurrentPassword ? 'text' : 'password'"
              variant="outlined"
              density="comfortable"
              autocomplete="current-password"
              :error-messages="passwordErrors.currentPassword"
              :append-inner-icon="showCurrentPassword ? 'mdi-eye-off' : 'mdi-eye'"
              class="mb-2"
              @click:append-inner="showCurrentPassword = !showCurrentPassword"
            />
            <v-text-field
              v-model="passwordForm.newPassword"
              :label="t('settings.security.newPassword')"
              :type="showNewPassword ? 'text' : 'password'"
              variant="outlined"
              density="comfortable"
              autocomplete="new-password"
              :error-messages="passwordErrors.newPassword"
              :append-inner-icon="showNewPassword ? 'mdi-eye-off' : 'mdi-eye'"
              class="mb-1"
              @click:append-inner="showNewPassword = !showNewPassword"
            />
            <div v-if="passwordForm.newPassword" class="mb-2">
              <div class="d-flex align-center justify-space-between text-caption mb-1">
                <span class="text-medium-emphasis">{{ t('settings.security.passwordStrength') }}</span>
                <v-chip size="x-small" :color="strength.color" variant="tonal">{{ strength.labelKey ? t(strength.labelKey) : '' }}</v-chip>
              </div>
              <v-progress-linear
                :model-value="strengthPercent(passwordForm.newPassword)"
                :color="strength.color"
                height="6"
                rounded
              />
            </div>
            <v-text-field
              v-model="passwordForm.confirmPassword"
              :label="t('settings.security.confirmNewPassword')"
              :type="showConfirmPassword ? 'text' : 'password'"
              variant="outlined"
              density="comfortable"
              autocomplete="new-password"
              :error-messages="passwordErrors.confirmPassword"
              :append-inner-icon="showConfirmPassword ? 'mdi-eye-off' : 'mdi-eye'"
              class="mb-3"
              @click:append-inner="showConfirmPassword = !showConfirmPassword"
            />
            <v-btn
              class="btn-glow"
              rounded="lg"
              :loading="savingPassword"
              @click="submitPassword"
            >
              {{ t('settings.security.updatePassword') }}
            </v-btn>
          </v-col>
        </v-row>

        <v-divider class="my-5 opacity-20" />

        <div class="two-factor-section mb-5">
          <div class="d-flex align-center justify-space-between flex-wrap gap-3 mb-3">
            <div>
              <h4 class="text-subtitle-1 font-weight-bold mb-1 d-flex align-center gap-2">
                <v-icon size="20">mdi-two-factor-authentication</v-icon>
                {{ t('settings.security.twoFactorTitle') }}
              </h4>
              <p class="text-body-2 text-medium-emphasis mb-0">
                {{ t('settings.security.twoFactorDescription') }}
              </p>
            </div>
            <v-switch
              :model-value="account.two_factor_enabled"
              color="primary"
              hide-details
              :disabled="twoFactorBusy || !!twoFactorChallenge"
              :label="account.two_factor_enabled ? t('settings.security.enabled') : t('settings.security.disabled')"
              @update:model-value="onTwoFactorToggle"
            />
          </div>

          <v-alert
            v-if="account.two_factor_enabled"
            type="success"
            variant="tonal"
            density="comfortable"
            class="rounded-lg mb-3"
          >
            {{ t('settings.security.twoFactorEnabledViaEmail') }}
          </v-alert>

          <v-card v-if="twoFactorChallenge" variant="outlined" class="pa-4 rounded-lg two-factor-setup">
            <p class="text-body-2 mb-3">
              {{ t('settings.security.enterOtpSentTo') }} <strong>{{ twoFactorChallenge.maskedEmail }}</strong>
            </p>
            <v-otp-input
              v-model="twoFactorCode"
              length="6"
              type="number"
              class="mb-3 otp-rtl"
            />
            <div class="d-flex flex-wrap gap-2">
              <v-btn
                color="primary"
                rounded="lg"
                :loading="confirmingTwoFactor"
                :disabled="twoFactorCode.length !== 6"
                @click="submitTwoFactorConfirm"
              >
                {{ t('settings.security.confirmActivation') }}
              </v-btn>
              <v-btn variant="text" rounded="lg" @click="cancelTwoFactorSetup">{{ t('common.cancel') }}</v-btn>
            </div>
          </v-card>

          <v-dialog v-model="disableDialog" max-width="420">
            <v-card class="pa-5 rounded-xl">
              <h4 class="text-h6 font-weight-bold mb-2">{{ t('settings.security.disable2faTitle') }}</h4>
              <p class="text-body-2 text-medium-emphasis mb-4">{{ t('settings.security.disable2faBody') }}</p>
              <v-text-field
                v-model="disablePassword"
                :label="t('settings.security.currentPassword')"
                :type="showDisablePassword ? 'text' : 'password'"
                variant="outlined"
                density="comfortable"
                :append-inner-icon="showDisablePassword ? 'mdi-eye-off' : 'mdi-eye'"
                @click:append-inner="showDisablePassword = !showDisablePassword"
              />
              <div class="d-flex justify-end gap-2 mt-2">
                <v-btn variant="text" @click="disableDialog = false">{{ t('common.cancel') }}</v-btn>
                <v-btn color="error" :loading="disablingTwoFactor" @click="submitDisableTwoFactor">
                  {{ t('settings.security.disable2fa') }}
                </v-btn>
              </div>
            </v-card>
          </v-dialog>

          <v-dialog v-model="enableDialog" max-width="420">
            <v-card class="pa-5 rounded-xl">
              <h4 class="text-h6 font-weight-bold mb-2">{{ t('settings.security.enable2faTitle') }}</h4>
              <p class="text-body-2 text-medium-emphasis mb-4">
                {{ t('settings.security.enable2faBody') }}
              </p>
              <v-text-field
                v-model="enablePassword"
                :label="t('settings.security.currentPassword')"
                :type="showEnablePassword ? 'text' : 'password'"
                variant="outlined"
                density="comfortable"
                :append-inner-icon="showEnablePassword ? 'mdi-eye-off' : 'mdi-eye'"
                @click:append-inner="showEnablePassword = !showEnablePassword"
              />
              <div class="d-flex justify-end gap-2 mt-2">
                <v-btn variant="text" @click="enableDialog = false">{{ t('common.cancel') }}</v-btn>
                <v-btn color="primary" :loading="enablingTwoFactor" @click="submitEnableTwoFactor">
                  {{ t('settings.security.sendCode') }}
                </v-btn>
              </div>
            </v-card>
          </v-dialog>
        </div>

        <div class="future-security">
          <div class="text-subtitle-2 font-weight-bold mb-2">{{ t('settings.security.advancedFeaturesTitle') }}</div>
          <div class="d-flex flex-wrap gap-2">
            <v-chip v-for="item in futureFeatures" :key="item" size="small" variant="outlined" disabled>
              {{ item }}
            </v-chip>
          </div>
          <p class="text-caption text-medium-emphasis mt-2 mb-0">
            {{ t('settings.security.advancedFeaturesBody') }}
          </p>
        </div>
      </template>
    </v-card>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAccountSecurity } from '../../composables/useAccountSecurity.js'
import { useToast } from '../../composables/useToast.js'
import { validateChangeEmail, validateChangePassword } from '../../utils/validate.js'
import { scorePassword, strengthPercent } from '../../utils/passwordStrength.js'
import { isApiMode } from '../../utils/session.js'

const {
  account,
  loading,
  savingEmail,
  savingPassword,
  resendingVerification,
  enablingTwoFactor,
  confirmingTwoFactor,
  disablingTwoFactor,
  twoFactorChallenge,
  loadAccount,
  roleLabel,
  formatCreatedAt,
  changeEmail,
  changePassword,
  resendVerification,
  requestEnableTwoFactor,
  confirmEnableTwoFactor,
  disableTwoFactor,
  cancelTwoFactorSetup,
} = useAccountSecurity()

const { showSuccess, showError } = useToast()
const { t } = useI18n()

const emailForm = reactive({ newEmail: '', currentPassword: '' })
const passwordForm = reactive({ currentPassword: '', newPassword: '', confirmPassword: '' })
const emailErrors = reactive({ newEmail: '', currentPassword: '' })
const passwordErrors = reactive({ currentPassword: '', newPassword: '', confirmPassword: '' })

const showEmailPassword = ref(false)
const showCurrentPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)

const enableDialog = ref(false)
const disableDialog = ref(false)
const enablePassword = ref('')
const disablePassword = ref('')
const showEnablePassword = ref(false)
const showDisablePassword = ref(false)
const twoFactorCode = ref('')

const twoFactorBusy = computed(
  () => enablingTwoFactor.value || confirmingTwoFactor.value || disablingTwoFactor.value,
)

const futureFeatures = computed(() => [
  t('settings.security.authenticatorApp'),
  t('settings.security.loginHistory'),
  t('settings.security.advancedSessions'),
])

const strength = computed(() => scorePassword(passwordForm.newPassword))

function clearEmailErrors() {
  emailErrors.newEmail = ''
  emailErrors.currentPassword = ''
}

function clearPasswordErrors() {
  passwordErrors.currentPassword = ''
  passwordErrors.newPassword = ''
  passwordErrors.confirmPassword = ''
}

async function handleResendVerification() {
  try {
    const result = await resendVerification()
    showSuccess(result.detail || t('settings.security.confirmationSent'))
  } catch (err) {
    showError(err.message)
  }
}

async function submitEmail() {
  clearEmailErrors()
  const errors = validateChangeEmail(emailForm)
  Object.assign(emailErrors, errors)
  if (Object.keys(errors).length) return

  if (emailForm.newEmail.trim().toLowerCase() === account.value?.email?.toLowerCase()) {
    emailErrors.newEmail = t('settings.security.sameEmailError')
    return
  }

  try {
    await changeEmail({
      newEmail: emailForm.newEmail,
      currentPassword: emailForm.currentPassword,
    })
    emailForm.newEmail = ''
    emailForm.currentPassword = ''
    await loadAccount()
    showSuccess(t('settings.security.emailUpdated'))
  } catch (err) {
    showError(err.message)
  }
}

async function submitPassword() {
  clearPasswordErrors()
  const errors = validateChangePassword(passwordForm)
  Object.assign(passwordErrors, errors)
  if (Object.keys(errors).length) return

  try {
    await changePassword({ ...passwordForm })
    passwordForm.currentPassword = ''
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
    showSuccess(t('settings.security.passwordUpdated'))
  } catch (err) {
    showError(err.message)
  }
}

function onTwoFactorToggle(enabled) {
  if (enabled) {
    enablePassword.value = ''
    enableDialog.value = true
  } else if (account.value?.two_factor_enabled) {
    disablePassword.value = ''
    disableDialog.value = true
  }
}

async function submitEnableTwoFactor() {
  if (!enablePassword.value) {
    showError(t('settings.security.enterPassword'))
    return
  }
  try {
    await requestEnableTwoFactor(enablePassword.value)
    enableDialog.value = false
    enablePassword.value = ''
    twoFactorCode.value = ''
    showSuccess(t('settings.security.otpSent'))
  } catch (err) {
    showError(err.message)
  }
}

async function submitTwoFactorConfirm() {
  if (twoFactorCode.value.length !== 6) return
  try {
    await confirmEnableTwoFactor(twoFactorCode.value)
    twoFactorCode.value = ''
    showSuccess(t('settings.security.twoFactorEnabled'))
  } catch (err) {
    showError(err.message)
  }
}

async function submitDisableTwoFactor() {
  if (!disablePassword.value) {
    showError(t('settings.security.enterPassword'))
    return
  }
  try {
    await disableTwoFactor(disablePassword.value)
    disableDialog.value = false
    disablePassword.value = ''
    showSuccess(t('settings.security.twoFactorDisabled'))
  } catch (err) {
    showError(err.message)
  }
}

onMounted(() => {
  if (isApiMode()) loadAccount()
})
</script>

<style scoped>
.account-info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}

.info-pill {
  padding: 12px 14px;
  border-radius: 12px;
  background: rgba(124, 108, 240, 0.06);
  border: 1px solid rgba(124, 108, 240, 0.12);
}

.info-pill__label {
  font-size: 0.72rem;
  color: rgba(255, 255, 255, 0.55);
  margin-bottom: 4px;
}

.info-pill__value {
  font-size: 0.95rem;
  font-weight: 600;
}

.verification-banner {
  border: 1px solid rgba(251, 191, 36, 0.25);
}

.future-security {
  padding: 12px 14px;
  border-radius: 12px;
  border: 1px dashed rgba(124, 108, 240, 0.25);
  background: rgba(255, 255, 255, 0.02);
}

.two-factor-section {
  padding: 14px 16px;
  border-radius: 12px;
  border: 1px solid rgba(124, 108, 240, 0.18);
  background: rgba(124, 108, 240, 0.04);
}

.two-factor-setup {
  border-color: rgba(34, 211, 238, 0.25) !important;
  background: rgba(34, 211, 238, 0.04);
}

.otp-rtl :deep(input) {
  direction: ltr;
  text-align: center;
}
</style>
