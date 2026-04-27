<script setup>
import { ref, onMounted, computed } from 'vue'
import { 
  RotateCcw, 
  Save, 
  ShieldAlert, 
  Info, 
  Settings2, 
  Globe, 
  UserCircle2,
  Lock,
  AlertCircle,
  KeyRound,
  Layout
} from 'lucide-vue-next'
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

const isSuperAdmin = computed(() => {
  return auth.userRole?.toLowerCase().includes('admin') || auth.userRole?.toLowerCase().includes('super')
})

const canEdit = auth.hasPermission('settings.update')

const isLoading = ref(true)
const isSaving = ref(false)
const isResetting = ref(false)
const activeTab = ref('system') // Default to system since general is empty

const form = ref({
  // General
  site_name: '',
  contact_email: '',
  enable_user_avatars: 'true',
  allow_username_change: 'true',
  // System
  maintenance_mode: 'false',
  maintenance_scheduled_at: null,
  registration_enabled: 'true'
})

const selectedSchedule = ref('0') // minutes

async function fetchSettings() {
  isLoading.value = true
  try {
    const { data: res } = await settingService.getRaw()
    const configs = res.data || []
    
    // map to form
    const st = { ...form.value }
    configs.forEach((item) => {
      if (st[item.setting_key] !== undefined) {
        st[item.setting_key] = item.setting_value || ''
      }
    })
    form.value = st
    
  } catch (err) {
    toast({ title: 'Error', description: 'Gagal mengambil pengaturan', variant: 'destructive' })
  } finally {
    isLoading.value = false
  }
}

async function handleSave() {
  if (activeTab.value === 'general') return

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
  } catch (err) {
    toast({ title: 'Gagal', description: 'Gagal menyimpan pengaturan', variant: 'destructive' })
  } finally {
    isSaving.value = false
  }
}

async function handleReset() {
  const ok = await confirm.confirm({
    title: 'Reset Pengaturan?',
    message: `Apakah Anda yakin ingin mengembalikan semua pengaturan ${activeTab.value === 'system' ? 'sistem' : 'umum'} ke nilai awal (default)? Tindakan ini tidak dapat dibatalkan.`,
    variant: 'destructive'
  })

  if (!ok) return

  isResetting.value = true
  try {
    await settingService.reset(activeTab.value)
    toast({ title: 'Berhasil', description: `Pengaturan ${activeTab.value === 'system' ? 'sistem' : 'umum'} telah dikembalikan ke default`, variant: 'success' })
    await fetchSettings()
  } catch (err) {
    toast({ title: 'Gagal', description: 'Gagal mereset pengaturan', variant: 'destructive' })
  } finally {
    isResetting.value = false
  }
}

onMounted(() => {
  fetchSettings()
})
</script>

<template>
  <div class="space-y-6 animate-in fade-in duration-700">
    <PageHeader 
      title="Global Settings" 
      description="Pusat konfigurasi utama dan metadata sistem aplikasi" 
    />

    <!-- Tabs Navigation -->
    <div class="flex items-center gap-1 bg-muted/30 p-1 rounded-xl w-fit border border-border/50">
      <button 
        type="button"
        @click="activeTab = 'general'"
        :class="[
          'flex items-center gap-2 px-4 py-2 text-sm font-bold rounded-lg transition-all',
          activeTab === 'general' ? 'bg-card text-primary shadow-sm' : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
        ]"
      >
        <Globe class="w-4 h-4" />
        Informasi Publik
      </button>
      <button 
        v-if="isSuperAdmin"
        type="button"
        @click="activeTab = 'system'"
        :class="[
          'flex items-center gap-2 px-4 py-2 text-sm font-bold rounded-lg transition-all',
          activeTab === 'system' ? 'bg-card text-primary shadow-sm' : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
        ]"
      >
        <Settings2 class="w-4 h-4" />
        Konfigurasi Sistem
      </button>
    </div>

    <div v-if="isLoading" class="space-y-6">
      <SkeletonLoader class="h-64 w-full rounded-2xl" />
    </div>

    <div v-else class="grid grid-cols-1 lg:grid-cols-12 gap-8">
      <!-- Main Form Area -->
      <div class="lg:col-span-8 space-y-6">
        <form @submit.prevent="handleSave" class="space-y-6">
          
          <!-- TAB: GENERAL -->
          <div v-if="activeTab === 'general'" class="space-y-6 animate-in slide-in-from-left-2 duration-300">
            <div class="bg-card border border-border border-dashed rounded-2xl p-12 text-center space-y-4">
              <div class="inline-flex p-4 bg-muted rounded-full">
                <Globe class="w-8 h-8 text-muted-foreground/40" />
              </div>
              <div class="max-w-xs mx-auto">
                <h3 class="text-sm font-bold">Informasi Publik</h3>
                <p class="text-xs text-muted-foreground mt-1">Belum ada pengaturan kategori umum yang tersedia saat ini. Semua konfigurasi utama berada di tab Sistem.</p>
              </div>
            </div>
          </div>

          <!-- TAB: SYSTEM -->
          <div v-if="activeTab === 'system' && isSuperAdmin" class="space-y-6 animate-in slide-in-from-right-2 duration-300">
            <div class="bg-card border border-border rounded-2xl overflow-hidden shadow-sm">
              <!-- Header Card -->
              <div class="px-6 py-4 border-b bg-muted/10 flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <div class="p-2 bg-primary/10 rounded-lg text-primary">
                    <Settings2 class="w-5 h-5" />
                  </div>
                  <div>
                    <h3 class="text-sm font-bold">Pusat Konfigurasi Sistem</h3>
                    <p class="text-[10px] text-muted-foreground font-medium uppercase tracking-wider">Identitas, Fitur & Akses Utama</p>
                  </div>
                </div>
              </div>

              <!-- Card Body -->
              <div class="p-6 space-y-8">
                <!-- Group: Identitas -->
                <div class="space-y-4">
                  <div class="flex items-center gap-2 text-xs font-bold text-primary/70 uppercase tracking-widest px-1">
                    <Layout class="w-3.5 h-3.5" />
                    Branding & Kontak
                  </div>
                  <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div class="space-y-1.5">
                      <Label for="siteName" class="text-[11px] font-bold">Nama Aplikasi</Label>
                      <Input id="siteName" v-model="form.site_name" :disabled="!canEdit" placeholder="Misal Web CMS" />
                    </div>
                    <div class="space-y-1.5">
                      <Label for="contactEmail" class="text-[11px] font-bold">Email Dukungan</Label>
                      <Input id="contactEmail" type="email" v-model="form.contact_email" :disabled="!canEdit" placeholder="admin@example.com" />
                    </div>
                  </div>
                </div>

                <!-- Group: Fitur & Akses (Toggles) -->
                <div class="space-y-4 pt-6 border-t">
                  <div class="flex items-center gap-2 text-xs font-bold text-primary/70 uppercase tracking-widest px-1">
                    <KeyRound class="w-3.5 h-3.5" />
                    Fitur & Hak Akses
                  </div>
                  
                  <div class="space-y-3">
                    <!-- Toggle: Maintenance Mode -->
                    <div class="flex items-center justify-between p-3 bg-muted/30 rounded-xl border border-border/50 hover:border-destructive/30 transition-all">
                      <div class="flex-1 pr-4">
                        <Label for="maintenance" class="text-sm font-bold text-destructive flex items-center gap-2">
                          Maintenance Mode
                          <span v-if="form.maintenance_mode === 'true'" class="flex h-2 w-2 rounded-full bg-destructive animate-pulse"></span>
                        </Label>
                        <p class="text-[11px] text-muted-foreground mt-0.5">Tutup akses publik saat perbaikan sistem.</p>
                      </div>
                      <button 
                        type="button"
                        @click="form.maintenance_mode = form.maintenance_mode === 'true' ? 'false' : 'true'"
                        :disabled="!canEdit"
                        class="relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 focus:outline-none"
                        :class="form.maintenance_mode === 'true' ? 'bg-destructive' : 'bg-slate-400 dark:bg-slate-700'"
                      >
                        <span 
                          class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"
                          :class="form.maintenance_mode === 'true' ? 'translate-x-5' : 'translate-x-0'"
                        ></span>
                      </button>
                    </div>

                    <!-- Maintenance Schedule -->
                    <div v-if="form.maintenance_mode === 'true'" class="animate-in slide-in-from-top-2 duration-300">
                      <div class="mx-3 p-4 bg-destructive/5 rounded-b-xl border-x border-b border-destructive/10 space-y-3">
                        <Label class="text-[10px] font-black uppercase text-destructive/70 tracking-widest">Jadwal Lockdown</Label>
                        <select 
                          v-model="selectedSchedule"
                          :disabled="!canEdit"
                          class="w-full bg-card border border-destructive/20 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-destructive/30"
                        >
                          <option value="0">Tutup Sekarang (Instan)</option>
                          <option value="5">Beri Peringatan 5 Menit</option>
                          <option value="10">Beri Peringatan 10 Menit</option>
                          <option value="30">Beri Peringatan 30 Menit</option>
                        </select>
                      </div>
                    </div>

                    <!-- Toggle: Registration -->
                    <div class="flex items-center justify-between p-3 hover:bg-muted/50 rounded-xl transition-colors">
                      <div class="flex-1 pr-4">
                        <Label class="text-sm font-bold">Registrasi Mandiri (Public Register)</Label>
                        <p class="text-[11px] text-muted-foreground mt-0.5">Izinkan pengunjung umum mendaftar akun baru.</p>
                      </div>
                      <button 
                        type="button"
                        @click="form.registration_enabled = form.registration_enabled === 'true' ? 'false' : 'true'"
                        :disabled="!canEdit"
                        class="relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 focus:outline-none"
                        :class="form.registration_enabled === 'true' ? 'bg-primary' : 'bg-slate-400 dark:bg-slate-700'"
                      >
                        <span 
                          class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"
                          :class="form.registration_enabled === 'true' ? 'translate-x-5' : 'translate-x-0'"
                        ></span>
                      </button>
                    </div>

                    <!-- Toggle: Avatar -->
                    <div class="flex items-center justify-between p-3 hover:bg-muted/50 rounded-xl transition-colors border-t border-dashed">
                      <div class="flex-1 pr-4">
                        <Label class="text-sm font-bold">Aktifkan Foto Profil</Label>
                        <p class="text-[11px] text-muted-foreground mt-0.5">Admin dapat mengunggah dan menampilkan foto profil.</p>
                      </div>
                      <button 
                        type="button"
                        @click="form.enable_user_avatars = form.enable_user_avatars === 'true' ? 'false' : 'true'"
                        :disabled="!canEdit"
                        class="relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 focus:outline-none"
                        :class="form.enable_user_avatars === 'true' ? 'bg-primary' : 'bg-slate-400 dark:bg-slate-700'"
                      >
                        <span 
                          class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"
                          :class="form.enable_user_avatars === 'true' ? 'translate-x-5' : 'translate-x-0'"
                        ></span>
                      </button>
                    </div>

                    <!-- Toggle: Username Change -->
                    <div class="flex items-center justify-between p-3 hover:bg-muted/50 rounded-xl transition-colors border-t border-dashed">
                      <div class="flex-1 pr-4">
                        <Label class="text-sm font-bold">Izinkan Ganti Username</Label>
                        <p class="text-[11px] text-muted-foreground mt-0.5">Admin dapat mengubah username mandiri di halaman profil.</p>
                      </div>
                      <button 
                        type="button"
                        @click="form.allow_username_change = form.allow_username_change === 'true' ? 'false' : 'true'"
                        :disabled="!canEdit"
                        class="relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 focus:outline-none"
                        :class="form.allow_username_change === 'true' ? 'bg-primary' : 'bg-slate-400 dark:bg-slate-700'"
                      >
                        <span 
                          class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"
                          :class="form.allow_username_change === 'true' ? 'translate-x-5' : 'translate-x-0'"
                        ></span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Form Actions -->
          <div v-if="canEdit && activeTab !== 'general'" class="flex justify-end items-center gap-3 pt-2">
            <Button type="submit" :loading="isSaving" class="px-8 font-bold shadow-lg shadow-primary/10">
              <Save class="w-4 h-4 mr-2" />
              Simpan Konfigurasi Sistem
            </Button>
          </div>
        </form>
      </div>

      <!-- Sidebar Info Area -->
      <div class="lg:col-span-4 space-y-6">
        <div class="bg-primary/5 border border-primary/10 rounded-2xl p-6 space-y-4">
          <div class="flex items-center gap-2 text-primary">
            <Info class="w-5 h-5" />
            <h4 class="text-sm font-black uppercase tracking-widest">Informasi</h4>
          </div>
          <p class="text-xs text-muted-foreground leading-relaxed font-medium">
            Pengaturan di halaman ini berdampak langsung pada operasional sistem secara keseluruhan. Pastikan Anda memahami setiap opsi sebelum melakukan perubahan.
          </p>
        </div>

        <div v-if="isSuperAdmin" class="bg-destructive/5 border border-destructive/10 rounded-2xl p-6 space-y-5">
          <div class="flex items-center gap-2 text-destructive">
            <ShieldAlert class="w-5 h-5" />
            <h4 class="text-sm font-black uppercase tracking-widest">Zona Berbahaya</h4>
          </div>
          <p class="text-xs text-muted-foreground font-medium">
            Kembalikan pengaturan di tab <span class="font-bold text-destructive underline">{{ activeTab === 'system' ? 'Sistem' : 'Umum' }}</span> ke nilai awal pabrik.
          </p>
          <Button 
            type="button" variant="outline" 
            class="w-full border-destructive/20 text-destructive hover:bg-destructive/10 font-bold"
            :loading="isResetting" @click="handleReset"
          >
            <RotateCcw class="w-4 h-4 mr-2" />
            Reset {{ activeTab === 'system' ? 'Sistem' : 'Umum' }}
          </Button>
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
