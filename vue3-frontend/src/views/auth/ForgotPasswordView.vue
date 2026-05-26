<script setup>
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Label from '@/components/ui/Label.vue'
import { ref } from 'vue'

const email = ref('')
const submitted = ref(false)

function handleSubmit() {
  // TODO: integrate with backend forgot-password endpoint
  submitted.value = true
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-muted p-4">
    <div class="w-full max-w-sm rounded-xl bg-card shadow-lg p-8">
      <h1 class="text-2xl font-bold text-primary text-center">Reset Password</h1>
      <p class="mt-2 text-sm text-muted-foreground text-center">Enter your registered email or username</p>

      <div v-if="submitted" class="mt-6 text-center text-sm text-green-600">
        If the email is found, we will send password reset instructions.
      </div>

      <form v-else @submit.prevent="handleSubmit" class="mt-6 space-y-4">
        <div>
          <Label for="email">Email / Username</Label>
          <Input id="email" v-model="email" placeholder="admin@example.com" class="mt-1" />
        </div>
        <Button class="w-full" type="submit">Send Reset Link</Button>
      </form>

      <p class="mt-6 text-center text-xs text-muted-foreground">
        <router-link to="/login" class="text-primary hover:underline">← Back to login</router-link>
      </p>
    </div>
  </div>
</template>
