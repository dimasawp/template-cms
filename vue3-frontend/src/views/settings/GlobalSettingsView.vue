<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { settingService } from '@/services/settingService'
import { useToast } from '@/composables/useToast'
import { useConfirmation } from '@/composables/useConfirmation'
import { useAuthStore } from '@/stores/auth'
import PageHeader from '@/components/common/PageHeader.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Label from '@/components/ui/Label.vue'
import SkeletonLoader from '@/components/ui/SkeletonLoader.vue'
import ConfirmationDialog from '@/components/ui/ConfirmationDialog.vue'

const { toast } = useToast()
const confirm = useConfirmation()
const auth = useAuthStore()

const canEdit = auth.hasPermission('settings.update')

const isLoading = ref(true)
const isSaving = ref(false)

const form = ref({
  site_name: '',
  maintenance_mode: 'false',
  maintenance_scheduled_at: null as string | null,
  contact_email: '',
  enable_user_avatars: 'true',
  allow_username_change: 'true',
  registration_enabled: 'true'
})

const selectedSchedule = ref('0') // minutes

async function fetchSettings() {
  isLoading.value = true
  try {
    const { data: res } = await settingService.getRaw()
    const configs = res.data || []
    
    // map to form
    const st = { ...form.value } as Record<string, string>
    configs.forEach((item: any) => {
      if (st[item.setting_key] !== undefined) {
        st[item.setting_key] = item.setting_value || ''
      }
    })
    form.value = st as any
    
  } catch (err: any) {
    toast({ title: 'Error', description: 'Gagal mengambil pengaturan', variant: 'destructive' })
  } finally {
    isLoading.value = false
  }
}

async function handleSave() {
  // Check if maintenance mode is turning ON
  if (form.value.maintenance_mode === 'true') {
    const ok = await confirm.confirm({
      title: 'Aktifkan Mode Perawatan?',
      message: 'Perhatian! Menghidupkan Mode Perawatan akan menutup akses publik ke seluruh website. Pastikan Anda sudah siap.',
      variant: 'warning'
    })
    if (!ok) return
  }

  isSaving.value = true
  try {
    // Calculate scheduled_at
    let scheduledAt = null
    if (form.value.maintenance_mode === 'true') {
      const minutes = parseInt(selectedSchedule.value)
      if (minutes > 0) {
        const date = new Date()
        date.setMinutes(date.getMinutes() + minutes)
        scheduledAt = date.toISOString()
      } else {
        // Now
        scheduledAt = new Date().toISOString()
      }
    }

    const payload = [
      { setting_key: 'site_name', setting_value: form.value.site_name },
      { setting_key: 'maintenance_mode', setting_value: form.value.maintenance_mode === 'true' ? 'true' : 'false' },
      { setting_key: 'maintenance_scheduled_at', setting_value: scheduledAt || '' },
      { setting_key: 'contact_email', setting_value: form.value.contact_email },
      { setting_key: 'enable_user_avatars', setting_value: form.value.enable_user_avatars === 'true' ? 'true' : 'false' },
      { setting_key: 'allow_username_change', setting_value: form.value.allow_username_change === 'true' ? 'true' : 'false' },
      { setting_key: 'registration_enabled', setting_value: form.value.registration_enabled === 'true' ? 'true' : 'false' }
    ]
    await settingService.bulkUpdate(payload)
    toast({ title: 'Berhasil', description: 'Pengaturan global berhasil disimpan', variant: 'success' })
  } catch (err: any) {
    toast({ title: 'Gagal', description: 'Gagal menyimpan pengaturan', variant: 'destructive' })
  } finally {
    isSaving.value = false
  }
}

onMounted(() => {
  fetchSettings()
})
</script>

<template>
  <div>
    <PageHeader title="Global Settings" description="Konfigurasi utama aplikasi konten" />

    <div v-if="isLoading" class="space-y-4 max-w-2xl">
      <SkeletonLoader class="h-10 w-full" />
      <SkeletonLoader class="h-10 w-full" />
      <SkeletonLoader class="h-10 w-full" />
    </div>

    <form v-else @submit.prevent="handleSave" class="space-y-6 max-w-2xl bg-card p-6 rounded-lg border shadow-sm">
      <div class="space-y-4">
        <div>
          <Label for="siteName">Site Name (Nama Website)</Label>
          <Input id="siteName" v-model="form.site_name" :disabled="!canEdit" placeholder="Misal: Portal Web CMS" class="mt-1" />
          <p class="text-xs text-muted-foreground mt-1">Nama ini akan muncul di judul browser dan header email.</p>
        </div>

        <div>
          <Label for="contactEmail">Dukungan Email (Sistem)</Label>
          <Input id="contactEmail" type="email" v-model="form.contact_email" :disabled="!canEdit" placeholder="admin@example.com" class="mt-1" />
          <p class="text-xs text-muted-foreground mt-1">Alamat email default untuk komunikasi sistem.</p>
        </div>

        <div class="flex items-center gap-2 pt-2 border-t mt-4">
          <input 
            type="checkbox" 
            id="maintenance" 
            :checked="form.maintenance_mode === 'true'"
            :disabled="!canEdit"
            @change="form.maintenance_mode = ($event.target as HTMLInputElement).checked ? 'true' : 'false'"
            class="rounded w-4 h-4 text-primary" 
          />
          <div class="flex-1">
            <Label for="maintenance" class="font-semibold text-destructive cursor-pointer">Maintenance Mode</Label>
            <p class="text-xs text-muted-foreground">Aktifkan untuk menutup akses publik website sementara waktu.</p>
            
            <!-- Schedule Dropdown -->
            <div v-if="form.maintenance_mode === 'true'" class="mt-3 p-3 bg-muted/50 rounded-lg border border-dashed border-destructive/30">
              <Label class="text-xs font-bold uppercase text-destructive/70 mb-2 block">Jadwal Lockdown</Label>
              <select 
                v-model="selectedSchedule"
                :disabled="!canEdit"
                class="w-full bg-background border rounded-md px-3 py-1.5 text-sm outline-none focus:ring-2 focus:ring-primary/20"
              >
                <option value="0">Aktifkan Sekarang (Tanpa Peringatan)</option>
                <option value="5">Beri Peringatan 5 Menit</option>
                <option value="10">Beri Peringatan 10 Menit</option>
                <option value="30">Beri Peringatan 30 Menit</option>
                <option value="60">Beri Peringatan 1 Jam</option>
              </select>
              <p class="text-[10px] text-muted-foreground mt-2 italic">
                *User akan melihat banner hitung mundur sebelum sistem benar-benar terkunci.
              </p>
            </div>
          </div>
        </div>

        <div class="flex items-center gap-2 pt-2 border-t mt-2">
          <input 
            type="checkbox" 
            id="enableAvatars" 
            :checked="form.enable_user_avatars === 'true'"
            :disabled="!canEdit"
            @change="form.enable_user_avatars = ($event.target as HTMLInputElement).checked ? 'true' : 'false'"
            class="rounded w-4 h-4 text-primary" 
          />
          <div>
            <Label for="enableAvatars" class="font-semibold cursor-pointer">Enable User Avatars</Label>
            <p class="text-xs text-muted-foreground">Izinkan pengguna mengunggah dan menampilkan foto profil.</p>
          </div>
        </div>

        <div class="flex items-center gap-2 pt-2 border-t mt-2">
          <input 
            type="checkbox" 
            id="allowUsernameChange" 
            :checked="form.allow_username_change === 'true'"
            :disabled="!canEdit"
            @change="form.allow_username_change = ($event.target as HTMLInputElement).checked ? 'true' : 'false'"
            class="rounded w-4 h-4 text-primary" 
          />
          <div>
            <Label for="allowUsernameChange" class="font-semibold cursor-pointer">Izinkan Pengguna Mengubah Username</Label>
            <p class="text-xs text-muted-foreground">Jika dimatikan, pengguna tidak dapat mengubah username mereka sendiri di halaman profil.</p>
          </div>
        </div>

        <div class="flex items-center gap-2 pt-2 border-t mt-2">
          <input 
            type="checkbox" 
            id="registrationEnabled" 
            :checked="form.registration_enabled === 'true'"
            :disabled="!canEdit"
            @change="form.registration_enabled = ($event.target as HTMLInputElement).checked ? 'true' : 'false'"
            class="rounded w-4 h-4 text-primary" 
          />
          <div>
            <Label for="registrationEnabled" class="font-semibold cursor-pointer">Izinkan Pendaftaran Mandiri (Self-Registration)</Label>
            <p class="text-xs text-muted-foreground">Jika diaktifkan, tombol pendaftaran akan muncul di halaman login dan URL /register bisa diakses publik.</p>
          </div>
        </div>
      </div>

      <div v-if="canEdit" class="flex justify-end border-t pt-4">
        <Button type="submit" :loading="isSaving">Simpan Perubahan</Button>
      </div>
    </form>

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
