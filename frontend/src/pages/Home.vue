
<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { call } from 'frappe-ui'

const router = useRouter()

const message = ref('Checking your login...')

onMounted(async () => {
  try {
    const response = await call(
      'project_management.api.portal.get_portal_session'
    )

    if (!response.logged_in) {
      router.replace('/login')
      return
    }

    if (response.role === 'client') {
      router.replace('/client/dashboard')
      return
    }

    if (response.role === 'vendor') {
      router.replace('/vendor/dashboard')
      return
    }

    message.value = 'You do not have permission to access this portal.'

  } catch (error) {
    message.value = 'Unable to check your login. Please try again.'
  }
})
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-slate-50">
    <div class="rounded-xl bg-white p-8 text-center shadow-sm">
      <p class="text-lg text-slate-700">
        {{ message }}
      </p>

      <RouterLink
        to="/login"
        class="mt-4 inline-block text-blue-600 hover:underline"
      >
        Go to Login
      </RouterLink>
    </div>
  </div>
</template>
