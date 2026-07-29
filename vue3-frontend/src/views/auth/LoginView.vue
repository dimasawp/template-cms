<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useTheme } from '@/composables/useTheme'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Label from '@/components/ui/Label.vue'
import CaptchaInput from '@/components/CaptchaInput.vue'
import { LogIn, Sun, Moon, ShieldAlert } from 'lucide-vue-next'

import { useSettingsStore } from '@/stores/settings'

const router = useRouter()
const auth = useAuthStore()
const settingsStore = useSettingsStore()
const { isDark, toggleTheme } = useTheme()

const username = ref('')
const password = ref('')
const captchaRef = ref(null)

async function handleLogin() {
  const payload = { username: username.value, password: password.value }
  if (settingsStore.captchaEnabled && captchaRef.value) {
    payload.captcha_token = captchaRef.value.token
    payload.captcha_answer = captchaRef.value.answer
  }
  const ok = await auth.login(payload)
  if (ok) router.push('/dashboard')
}
</script>

<template>
  <div class="relative flex min-h-screen items-center justify-center bg-muted p-4">
    <!-- Theme Toggle -->
    <div class="absolute right-4 top-4">
      <button @click="toggleTheme" class="p-2 rounded-md hover:bg-card/50 transition-colors">
        <Sun v-if="isDark" class="h-5 w-5" />
        <Moon v-else class="h-5 w-5" />
      </button>
    </div>
    <div class="w-full max-w-sm rounded-xl bg-card shadow-lg p-8">
      <div class="text-center mb-8">
        <h1 class="text-2xl font-bold text-primary">{{ settingsStore.siteName }}</h1>
        <p class="mt-2 text-sm text-muted-foreground">Sign in to dashboard</p>
      </div>

      <!-- Maintenance Warning -->
      <div v-if="settingsStore.maintenanceMode" class="mb-6 p-4 rounded-xl border border-amber-500/20 bg-amber-500/10 text-amber-600 shadow-sm flex items-start gap-3 text-start">
        <ShieldAlert class="h-5 w-5 shrink-0 mt-0.5 text-amber-500" />
        <div class="text-xs">
          <p class="font-bold mb-1">Maintenance Mode Active</p>
          <p class="opacity-90 leading-relaxed">
            The system is currently undergoing maintenance. Access is restricted to Administrators only.
          </p>
        </div>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <Label for="username">Username</Label>
          <Input id="username" v-model="username" placeholder="superadmin" class="mt-1" />
        </div>
        <div>
          <Label for="password">Password</Label>
          <Input id="password" v-model="password" type="password" placeholder="••••••" class="mt-1" />
        </div>

        <CaptchaInput v-if="settingsStore.captchaEnabled" ref="captchaRef" />

        <p v-if="auth.error" class="text-sm text-destructive">{{ auth.error }}</p>

        <Button class="w-full" :loading="auth.isLoading" type="submit">
          <LogIn v-if="!auth.isLoading" class="mr-2 h-4 w-4" /> Sign In
        </Button>
      </form>

      <p v-if="settingsStore.registrationEnabled" class="mt-6 text-center text-xs text-muted-foreground flex flex-col items-center">
        <span>
          Don't have an account? 
          <router-link to="/register" class="text-primary font-bold hover:underline ml-1">Register here</router-link>
        </span>
      </p>
    </div>
  </div>
</template>
