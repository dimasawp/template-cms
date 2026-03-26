<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useTheme } from '@/composables/useTheme'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Label from '@/components/ui/Label.vue'
import { LogIn, Sun, Moon } from 'lucide-vue-next'

const router = useRouter()
const auth = useAuthStore()
const { isDark, toggleTheme } = useTheme()

const username = ref('')
const password = ref('')

async function handleLogin() {
  const ok = await auth.login({ username: username.value, password: password.value })
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
        <h1 class="text-2xl font-bold text-primary">CMS Template</h1>
        <p class="mt-2 text-sm text-muted-foreground">Masuk ke dashboard</p>
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

        <p v-if="auth.error" class="text-sm text-destructive">{{ auth.error }}</p>

        <Button class="w-full" :loading="auth.isLoading" type="submit">
          <LogIn v-if="!auth.isLoading" class="mr-2 h-4 w-4" /> Masuk
        </Button>
      </form>

      <p class="mt-6 text-center text-xs text-muted-foreground">
        <router-link to="/forgot-password" class="text-primary hover:underline">Lupa password?</router-link>
      </p>
    </div>
  </div>
</template>
