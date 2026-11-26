
<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { call } from 'frappe-ui'

const router = useRouter()

const username = ref('')
const password = ref('')

const loading = ref(false)
const errorMessage = ref('')

async function login() {
  if (!username.value || !password.value) {
    errorMessage.value = 'Please enter username and password.'
    return
  }

  loading.value = true
  errorMessage.value = ''

  try {
    await call('/api/method/login', {
      usr: username.value,
      pwd: password.value
    })

    router.replace('/')
  } catch (error) {
    errorMessage.value = 'Invalid username or password.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-slate-100 px-4">

    <div class="w-full max-w-md rounded-2xl bg-white p-8 shadow-lg">

      <div class="mb-8 text-center">
        <h1 class="text-3xl font-bold text-slate-800">
          Project Portal
        </h1>

        <p class="mt-2 text-sm text-slate-500">
          Login to access your project information
        </p>
      </div>

      <form @submit.prevent="login" class="space-y-5">

        <div>
          <label class="mb-2 block text-sm font-medium text-slate-700">
            Username or Email
          </label>

          <input
            v-model="username"
            type="text"
            placeholder="Enter username or email"
            class="w-full rounded-lg border border-slate-300 px-4 py-3 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
          />
        </div>

        <div>
          <label class="mb-2 block text-sm font-medium text-slate-700">
            Password
          </label>

          <input
            v-model="password"
            type="password"
            placeholder="Enter password"
            class="w-full rounded-lg border border-slate-300 px-4 py-3 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
          />
        </div>

        <p
          v-if="errorMessage"
          class="text-sm text-red-600"
        >
          {{ errorMessage }}
        </p>

        <button
          type="submit"
          :disabled="loading"
          class="w-full rounded-lg bg-blue-600 px-4 py-3 font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {{ loading ? 'Logging in...' : 'Login' }}
        </button>

      </form>

    </div>
  </div>
</template>
