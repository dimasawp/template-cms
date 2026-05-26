<script setup>
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
    toast({ title: 'Error', description: 'Failed to load profile data', variant: 'destructive' })
  } finally {
    isLoading.value = false
  }
}

async function handleUpdateProfile() {
  isSavingProfile.value = true
  try {
    await apiUpdateProfile(profileForm.value)
    toast({ title: 'Success', description: 'Profile updated successfully', variant: 'success' })
    auth.fetchCurrentUser()
  } catch (err) {
    toast({ title: 'Error', description: err.response?.data?.message || 'Failed to update profile', variant: 'destructive' })
  } finally {
    isSavingProfile.value = false
  }
}

// Manual helper since it's not yet in axios but will be
const apiUpdateProfile = (data) => authService.updateMe(data)
// (Note: we'll add updateMe to authService.ts shortly)

async function handleChangePassword() {
  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    return toast({ title: 'Mismatch', description: 'Password confirmation does not match', variant: 'destructive' })
  }

  const ok = await confirm.confirm({
    title: 'Change Account Password?',
    message: 'Are you sure you want to change your account password? For security, the system requires you to re-login after this.',
    variant: 'warning'
  })

  if (!ok) return

  isSavingPassword.value = true
  try {
    await authService.changePassword({
      old_password: passwordForm.value.old_password,
      new_password: passwordForm.value.new_password
    })
    toast({ title: 'Success', description: 'Password changed successfully', variant: 'success' })
    passwordForm.value = { old_password: '', new_password: '', confirm_password: '' }
    
    // Auto logout for security after 2 seconds
    setTimeout(() => {
      auth.logout()
      window.location.reload()
    }, 2000)
  } catch (err) {
    toast({ title: 'Error', description: err.response?.data?.message || 'Failed to change password', variant: 'destructive' })
  } finally {
    isSavingPassword.value = false
  }
}

async function onFileSelected(event) {
  const file = (event.target).files?.[0]
  if (!file) return

  const formData = new FormData()
  formData.append('file', file)

  isUploadingAvatar.value = true
  try {
    await authService.uploadAvatar(formData)
    toast({ title: 'Success', description: 'Profile picture updated', variant: 'success' })
    auth.fetchCurrentUser()
  } catch (err) {
    toast({ title: 'Error', description: 'Failed to upload picture', variant: 'destructive' })
  } finally {
    isUploadingAvatar.value = false
  }
}

onMounted(fetchData)
</script>

<template>
  <div class="max-w-4xl mx-auto">
    <PageHeader title="My Account" description="Manage your personal information and account security" />

    <div v-if="isLoading" class="space-y-6">
      <SkeletonLoader class="h-40 w-full" />
      <SkeletonLoader class="h-60 w-full" />
    </div>

    <div v-else class="grid gap-6 md:grid-cols-3">
      <!-- Left & Basic Info -->
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
              title="Change Picture"
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
            <Info class="h-4 w-4" /> Security Tips
          </p>
          <p class="text-xs leading-relaxed opacity-90">Use a strong password (at least 8 characters with a mix of numbers and symbols) and don't reuse passwords from other sites.</p>
        </div>
      </div>

      <!-- Right -->
      <div class="md:col-span-2 space-y-6">
        <!-- Profile Form -->
        <div class="bg-card rounded-lg border shadow-sm">
          <div class="px-6 py-4 border-b flex items-center gap-2">
            <User class="h-5 w-5 text-muted-foreground" />
            <h3 class="font-bold">Profile Information</h3>
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
                  Username changes are disabled by system policy.
                </p>
              </div>
              <div class="space-y-2">
                <Label for="fullname">Full Name</Label>
                <Input id="fullname" v-model="profileForm.full_name" placeholder="Your Name" />
              </div>
            </div>
            <div class="space-y-2">
              <Label for="email">Email Address</Label>
              <div class="relative">
                <Input id="email" type="email" v-model="profileForm.email" placeholder="email@example.com" class="pl-9" />
                <Mail class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              </div>
            </div>
            <div class="pt-2 flex justify-end">
              <Button type="submit" :loading="isSavingProfile">Save Changes</Button>
            </div>
          </form>
        </div>

        <!-- Password Form -->
        <div class="bg-card rounded-lg border shadow-sm">
          <div class="px-6 py-4 border-b flex items-center gap-2">
            <Key class="h-5 w-5 text-muted-foreground" />
            <h3 class="font-bold">Password Security</h3>
          </div>
          <form @submit.prevent="handleChangePassword" class="p-6 space-y-4">
            <div class="space-y-2">
              <Label for="old_pass">Current Password</Label>
              <Input id="old_pass" type="password" v-model="passwordForm.old_password" placeholder="••••••••" required />
            </div>
            <div class="grid gap-4 sm:grid-cols-2">
              <div class="space-y-2">
                <Label for="new_pass">New Password</Label>
                <Input id="new_pass" type="password" v-model="passwordForm.new_password" placeholder="At least 6 characters" required />
              </div>
              <div class="space-y-2">
                <Label for="conf_pass">Confirm New Password</Label>
                <Input id="conf_pass" type="password" v-model="passwordForm.confirm_password" placeholder="Repeat new password" required />
              </div>
            </div>
            <div class="pt-2 flex justify-end">
              <Button type="submit" variant="secondary" :loading="isSavingPassword">Change Password</Button>
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
