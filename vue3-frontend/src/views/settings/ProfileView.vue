<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { authService } from '@/services/authService'
import { settingService } from '@/services/settingService'
import { useToast } from '@/composables/useToast'
import PageHeader from '@/components/common/PageHeader.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Label from '@/components/ui/Label.vue'
import Avatar from '@/components/ui/Avatar.vue'
import SkeletonLoader from '@/components/ui/SkeletonLoader.vue'
import { User, Mail, Shield, Key, Camera, Loader2, Info } from 'lucide-vue-next'
import { useConfirmation } from '@/composables/useConfirmation'
import ConfirmationDialog from '@/components/ui/ConfirmationDialog.vue'

const auth = useAuthStore()
const { toast } = useToast()
const confirm = useConfirmation()

const isLoading = ref(true)
const isSavingProfile = ref(false)
const isSavingPassword = ref(false)
const isUploadingAvatar = ref(false)
const enableAvatars = ref(true)
const canChangeUsername = ref(true)

const profileForm = ref({
  username: '',
  full_name: '',
  email: '',
})

const passwordForm = ref({
  old_password: '',
  new_password: '',
  confirm_password: '',
})

async function fetchData() {
  isLoading.value = true
  
  // 1. Try to fetch global settings (via public endpoint)
  try {
    const { data: sRes } = await settingService.getPublic()
    const settings = sRes.data || {}
    
    enableAvatars.value = settings.enable_user_avatars === 'true'
    canChangeUsername.value = settings.allow_username_change === 'true'
  } catch (err) {
    // If failed, use safe/conservative defaults
    console.warn('Could not fetch global settings, using defaults')
    enableAvatars.value = false // More conservative
    canChangeUsername.value = false
  }

  // 2. Fetch User Data (Crucial)
  try {
    await auth.fetchCurrentUser()
    if (auth.user) {
      profileForm.value.username = auth.user.username || ''
      profileForm.value.full_name = auth.user.full_name || ''
      profileForm.value.email = auth.user.email || ''
    }
  } catch (err) {
    toast({ title: 'Error', description: 'Gagal memuat data profil', variant: 'destructive' })
  } finally {
    isLoading.value = false
  }
}

async function handleUpdateProfile() {
  isSavingProfile.value = true
  try {
    await apiUpdateProfile(profileForm.value)
    toast({ title: 'Berhasil', description: 'Profil berhasil diperbarui', variant: 'success' })
    auth.fetchCurrentUser()
  } catch (err: any) {
    toast({ title: 'Gagal', description: err.response?.data?.message || 'Gagal memperbarui profil', variant: 'destructive' })
  } finally {
    isSavingProfile.value = false
  }
}

// Manual helper since it's not yet in axios but will be
const apiUpdateProfile = (data: any) => authService.updateMe(data)
// (Note: we'll add updateMe to authService.ts shortly)

async function handleChangePassword() {
  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    return toast({ title: 'Mismatch', description: 'Konfirmasi password tidak cocok', variant: 'destructive' })
  }

  const ok = await confirm.confirm({
    title: 'Ganti Password Akun?',
    message: 'Apakah Anda yakin ingin mengganti kunci akses akun Anda? Untuk keamanan, sistem menyarankan Anda login ulang setelah ini.',
    variant: 'warning'
  })

  if (!ok) return

  isSavingPassword.value = true
  try {
    await authService.changePassword({
      old_password: passwordForm.value.old_password,
      new_password: passwordForm.value.new_password
    })
    toast({ title: 'Berhasil', description: 'Password berhasil diganti', variant: 'success' })
    passwordForm.value = { old_password: '', new_password: '', confirm_password: '' }
    
    // Auto logout for security after 2 seconds
    setTimeout(() => {
      auth.logout()
      window.location.reload()
    }, 2000)
  } catch (err: any) {
    toast({ title: 'Gagal', description: err.response?.data?.message || 'Gagal mengganti password', variant: 'destructive' })
  } finally {
    isSavingPassword.value = false
  }
}

async function onFileSelected(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return

  const formData = new FormData()
  formData.append('file', file)

  isUploadingAvatar.value = true
  try {
    await authService.uploadAvatar(formData)
    toast({ title: 'Berhasil', description: 'Foto profil diperbarui', variant: 'success' })
    auth.fetchCurrentUser()
  } catch (err) {
    toast({ title: 'Gagal', description: 'Gagal mengupload foto', variant: 'destructive' })
  } finally {
    isUploadingAvatar.value = false
  }
}

onMounted(fetchData)
</script>

<template>
  <div class="max-w-4xl mx-auto">
    <PageHeader title="Akun Saya" description="Kelola informasi pribadi dan keamanan akun Anda" />

    <div v-if="isLoading" class="space-y-6">
      <SkeletonLoader class="h-40 w-full" />
      <SkeletonLoader class="h-60 w-full" />
    </div>

    <div v-else class="grid gap-6 md:grid-cols-3">
      <!-- Left: Photo & Basic Info -->
      <div class="md:col-span-1 space-y-6">
        <div class="bg-card rounded-lg border p-6 flex flex-col items-center text-center shadow-sm">
          <div class="relative group">
            <Avatar 
              :src="auth.user?.avatar" 
              :name="auth.user?.full_name || auth.username" 
              size="xl" 
              class="ring-4 ring-background"
            />
            <label 
              v-if="enableAvatars"
              class="absolute bottom-0 right-0 p-1.5 bg-primary text-white rounded-full cursor-pointer shadow-lg hover:scale-105 transition-transform"
              title="Ganti Foto"
            >
              <input type="file" class="hidden" accept="image/*" @change="onFileSelected" />
              <Camera v-if="!isUploadingAvatar" class="h-4 w-4" />
              <Loader2 v-else class="h-4 w-4 animate-spin" />
            </label>
          </div>
          
          <h3 class="mt-4 font-bold text-lg leading-tight">{{ auth.user?.full_name }}</h3>
          <p class="text-sm text-muted-foreground">@{{ auth.username }}</p>
          
          <div class="mt-4 inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-primary/10 text-primary text-[10px] font-bold uppercase tracking-wider">
            <Shield class="h-3 w-3" />
            {{ auth.user?.role_name }}
          </div>
        </div>

        <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-100 dark:border-blue-900/30 rounded-lg p-4 text-sm text-blue-800 dark:text-blue-200">
          <p class="font-bold flex items-center gap-2 mb-1">
            <Info class="h-4 w-4" /> Tips Keamanan
          </p>
          <p class="text-xs leading-relaxed opacity-90">Gunakan password yang kuat (minimal 8 karakter dengan kombinasi angka dan simbol) dan jangan gunakan password yang sama dengan aplikasi lain.</p>
        </div>
      </div>

      <!-- Right: Forms -->
      <div class="md:col-span-2 space-y-6">
        <!-- Profile Form -->
        <div class="bg-card rounded-lg border shadow-sm">
          <div class="px-6 py-4 border-b flex items-center gap-2">
            <User class="h-5 w-5 text-muted-foreground" />
            <h3 class="font-bold">Informasi Profil</h3>
          </div>
          <form @submit.prevent="handleUpdateProfile" class="p-6 space-y-4">
            <div class="grid gap-4 sm:grid-cols-2">
              <div class="space-y-2">
                <Label for="username">Username (ID)</Label>
                <div class="relative">
                  <Input 
                    id="username" 
                    v-model="profileForm.username" 
                    class="pl-9" 
                    :disabled="!canChangeUsername"
                    :class="!canChangeUsername ? 'bg-muted opacity-80 cursor-not-allowed' : ''"
                  />
                  <span class="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">@</span>
                </div>
                <p v-if="!canChangeUsername" class="text-[10px] text-muted-foreground italic">
                  Pengubahan username dinonaktifkan oleh kebijakan sistem.
                </p>
              </div>
              <div class="space-y-2">
                <Label for="fullname">Nama Lengkap</Label>
                <Input id="fullname" v-model="profileForm.full_name" placeholder="Nama Anda" />
              </div>
            </div>
            <div class="space-y-2">
              <Label for="email">Alamat Email</Label>
              <div class="relative">
                <Input id="email" type="email" v-model="profileForm.email" placeholder="email@example.com" class="pl-9" />
                <Mail class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              </div>
            </div>
            <div class="pt-2 flex justify-end">
              <Button type="submit" :loading="isSavingProfile">Simpan Perubahan</Button>
            </div>
          </form>
        </div>

        <!-- Password Form -->
        <div class="bg-card rounded-lg border shadow-sm">
          <div class="px-6 py-4 border-b flex items-center gap-2">
            <Key class="h-5 w-5 text-muted-foreground" />
            <h3 class="font-bold">Keamanan Password</h3>
          </div>
          <form @submit.prevent="handleChangePassword" class="p-6 space-y-4">
            <div class="space-y-2">
              <Label for="old_pass">Password Saat Ini</Label>
              <Input id="old_pass" type="password" v-model="passwordForm.old_password" placeholder="••••••••" required />
            </div>
            <div class="grid gap-4 sm:grid-cols-2">
              <div class="space-y-2">
                <Label for="new_pass">Password Baru</Label>
                <Input id="new_pass" type="password" v-model="passwordForm.new_password" placeholder="Minimal 6 karakter" required />
              </div>
              <div class="space-y-2">
                <Label for="conf_pass">Konfirmasi Password Baru</Label>
                <Input id="conf_pass" type="password" v-model="passwordForm.confirm_password" placeholder="Ulangi password baru" required />
              </div>
            </div>
            <div class="pt-2 flex justify-end">
              <Button type="submit" variant="secondary" :loading="isSavingPassword">Ganti Password</Button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <ConfirmationDialog
      :open="confirm.isOpen.value"
      :title="confirm.title.value"
      :message="confirm.message.value"
      :variant="confirm.variant.value"
      @confirm="confirm.onConfirm"
      @cancel="confirm.onCancel"
    />
  </div>
</template>
