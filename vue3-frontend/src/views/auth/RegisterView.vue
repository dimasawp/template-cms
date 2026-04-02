<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authService } from '@/services/authService'
import { useToast } from '@/composables/useToast'
import { useTheme } from '@/composables/useTheme'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Label from '@/components/ui/Label.vue'
import { UserPlus, Sun, Moon, ArrowLeft } from 'lucide-vue-next'

const router = useRouter()
const { toast } = useToast()
const { isDark, toggleTheme } = useTheme()

const isLoading = ref(false)
const form = ref({
  username: '',
  email: '',
  full_name: '',
  password: '',
  confirm_password: '',
})

async function handleRegister() {
  if (form.value.password !== form.value.confirm_password) {
    return toast({ title: 'Gagal', description: 'Konfirmasi password tidak cocok', variant: 'destructive' })
  }

  isLoading.value = true
  try {
    await authService.register({
      username: form.value.username,
      email: form.value.email,
      full_name: form.value.full_name,
      password: form.value.password,
    })
    
    toast({ title: 'Berhasil', description: 'Pendaftaran berhasil! Silakan masuk.', variant: 'success' })
    router.push('/login')
  } catch (err: any) {
    toast({ 
      title: 'Gagal', 
      description: err.response?.data?.detail || 'Gagal melakukan pendaftaran', 
      variant: 'destructive' 
    })
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="relative flex min-h-screen items-center justify-center bg-muted p-4">
    <!-- Theme & Back Actions -->
    <div class="absolute left-4 top-4">
      <router-link to="/login" class="flex items-center gap-2 p-2 rounded-md hover:bg-card/50 transition-colors text-sm font-medium text-muted-foreground hover:text-primary">
        <ArrowLeft class="h-4 w-4" /> Kembali ke Login
      </router-link>
    </div>
    
    <div class="absolute right-4 top-4">
      <button @click="toggleTheme" class="p-2 rounded-md hover:bg-card/50 transition-colors">
        <Sun v-if="isDark" class="h-5 w-5" />
        <Moon v-else class="h-5 w-5" />
      </button>
    </div>

    <div class="w-full max-w-md rounded-xl bg-card shadow-lg p-8">
      <div class="text-center mb-8">
        <h1 class="text-2xl font-bold text-primary tracking-tight">Buat Akun Baru</h1>
        <p class="mt-2 text-sm text-muted-foreground italic">Bergabunglah dengan ekosistem CMS Template</p>
      </div>

      <form @submit.prevent="handleRegister" class="space-y-4">
        <div class="grid gap-4 sm:grid-cols-2">
          <div class="space-y-1">
            <Label for="username">Username</Label>
            <Input id="username" v-model="form.username" placeholder="johndoe" required />
          </div>
          <div class="space-y-1">
            <Label for="fullname">Nama Lengkap</Label>
            <Input id="fullname" v-model="form.full_name" placeholder="John Doe" required />
          </div>
        </div>

        <div class="space-y-1">
          <Label for="email">Alamat Email</Label>
          <Input id="email" type="email" v-model="form.email" placeholder="john@example.com" required />
        </div>

        <div class="grid gap-4 sm:grid-cols-2">
          <div class="space-y-1">
            <Label for="password">Password</Label>
            <Input id="password" v-model="form.password" type="password" placeholder="••••••" required />
          </div>
          <div class="space-y-1">
            <Label for="confirm">Konfirmasi</Label>
            <Input id="confirm" v-model="form.confirm_password" type="password" placeholder="••••••" required />
          </div>
        </div>

        <div class="pt-2">
          <Button class="w-full h-11" :loading="isLoading" type="submit">
            <UserPlus v-if="!isLoading" class="mr-2 h-4 w-4" /> Daftar Sekarang
          </Button>
        </div>
      </form>

      <div class="mt-8 pt-6 border-t text-center">
        <p class="text-xs text-muted-foreground">
          Sudah punya akun? 
          <router-link to="/login" class="text-primary font-bold hover:underline">Masuk di sini</router-link>
        </p>
      </div>
    </div>
  </div>
</template>
