<template>
  <div />
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ROUTES } from '../../../constants/app.js'

const router = useRouter()

onMounted(() => {
  router.replace({ path: ROUTES.STUDENT_LANGUAGES_LISTENING, query: { tab: 'promotion' } })
})
</script>
