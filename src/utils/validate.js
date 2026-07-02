export function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(email || '').trim())
}

export function validateLogin({ email, password }) {
  const errors = {}
  if (!email?.trim()) errors.email = 'يرجى إدخال البريد الإلكتروني'
  else if (!isValidEmail(email)) errors.email = 'صيغة البريد الإلكتروني غير صحيحة'
  if (!password) errors.password = 'يرجى إدخال كلمة المرور'
  else if (password.length < 6) errors.password = 'كلمة المرور يجب أن تكون 6 أحرف على الأقل'
  return errors
}

export function validateRegister({ name, email, password, confirmPassword, role }) {
  const errors = {}
  if (!name?.trim()) errors.name = 'يرجى إدخال الاسم الكامل'
  if (!email?.trim()) errors.email = 'يرجى إدخال البريد الإلكتروني'
  else if (!isValidEmail(email)) errors.email = 'صيغة البريد الإلكتروني غير صحيحة'
  if (!password) errors.password = 'يرجى إدخال كلمة المرور'
  else if (password.length < 6) errors.password = 'كلمة المرور يجب أن تكون 6 أحرف على الأقل'
  if (password !== confirmPassword) errors.confirmPassword = 'كلمتا المرور غير متطابقتين'
  if (!role) errors.role = 'يرجى اختيار نوع الحساب'
  return errors
}

export function validateChangePassword({ currentPassword, newPassword, confirmPassword }) {
  const errors = {}
  if (!currentPassword) errors.currentPassword = 'أدخل كلمة المرور الحالية'
  if (!newPassword) errors.newPassword = 'أدخل كلمة المرور الجديدة'
  else if (newPassword.length < 6) errors.newPassword = 'كلمة المرور يجب أن تكون 6 أحرف على الأقل'
  if (!confirmPassword) errors.confirmPassword = 'أكّد كلمة المرور الجديدة'
  else if (newPassword !== confirmPassword) errors.confirmPassword = 'كلمتا المرور غير متطابقتين'
  return errors
}

export function validateChangeEmail({ newEmail, currentPassword }) {
  const errors = {}
  if (!newEmail?.trim()) errors.newEmail = 'أدخل البريد الإلكتروني الجديد'
  else if (!isValidEmail(newEmail)) errors.newEmail = 'صيغة البريد الإلكتروني غير صحيحة'
  if (!currentPassword) errors.currentPassword = 'أدخل كلمة المرور الحالية للتأكيد'
  return errors
}

export function validateForgotPassword({ email }) {
  const errors = {}
  if (!email?.trim()) errors.email = 'يرجى إدخال البريد الإلكتروني'
  else if (!isValidEmail(email)) errors.email = 'صيغة البريد الإلكتروني غير صحيحة'
  return errors
}

export function validateResetPassword({ token, newPassword, confirmPassword }) {
  const errors = {}
  if (!token?.trim()) errors.token = 'رابط غير صالح'
  if (!newPassword) errors.newPassword = 'يرجى إدخال كلمة المرور الجديدة'
  else if (newPassword.length < 6) errors.newPassword = 'كلمة المرور يجب أن تكون 6 أحرف على الأقل'
  if (!confirmPassword) errors.confirmPassword = 'يرجى تأكيد كلمة المرور'
  else if (newPassword !== confirmPassword) errors.confirmPassword = 'كلمتا المرور غير متطابقتين'
  return errors
}
