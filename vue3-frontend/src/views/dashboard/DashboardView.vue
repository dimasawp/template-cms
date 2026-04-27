<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { dashboardService } from '@/services/dashboardService'
import { 
  Users, 
  Shield, 
  Terminal, 
  Activity, 
  Plus, 
  RefreshCw, 
  CheckCircle2, 
  ShieldCheck,
  Calendar,
  Clock
} from 'lucide-vue-next'
import { format } from 'date-fns'
import { id } from 'date-fns/locale'
import Button from '@/components/ui/Button.vue'
import Badge from '@/components/ui/Badge.vue'

const auth = useAuthStore()
const stats = ref({
  total_users: 0,
  active_users: 0,
  total_roles: 0,
  total_logs: 0,
  system_status: 'Online'
})
const isLoading = ref(true)
const currentTime = ref(new Date())
let timer = null

const formattedDate = computed(() => {
  return format(currentTime.value, 'EEEE, d MMMM yyyy', { locale: id })
})

const formattedTime = computed(() => {
  return format(currentTime.value, 'HH.mm.ss')
})

async function fetchStats() {
  isLoading.value = true
  try {
    const { data: res } = await dashboardService.getStats()
    stats.value = res.data
  } catch (err) {
    console.error('Failed to fetch dashboard stats:', err)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchStats()
  timer = setInterval(() => {
    currentTime.value = new Date()
  }, 1000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<template>
  <div class="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-700">
    <!-- Header Section -->
    <div class="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-2">
      <div>
        <h1 class="text-2xl font-bold text-foreground tracking-tight">Dashboard</h1>
        <div class="flex items-center gap-3 text-muted-foreground mt-1 text-sm">
          <div class="flex items-center gap-1.5 font-medium">
            <Calendar class="w-4 h-4" />
            {{ formattedDate }}
          </div>
          <div class="w-1.5 h-1.5 rounded-full bg-border"></div>
          <div class="flex items-center gap-1.5 font-mono font-bold">
            <Clock class="w-4 h-4" />
            {{ formattedTime }} WIB
          </div>
        </div>
      </div>
      
      <div class="flex items-center gap-2">
        <Button class="bg-primary hover:bg-primary/90 text-white font-bold shadow-lg shadow-primary/20">
          <Plus class="w-4 h-4 mr-2" />
          Tambah User
        </Button>
        <Button variant="outline" size="icon" @click="fetchStats" :loading="isLoading" class="border-border shadow-sm">
          <RefreshCw class="w-4 h-4" />
        </Button>
      </div>
    </div>

    <!-- Welcome Greeting Card -->
    <div class="relative overflow-hidden bg-card dark:bg-slate-900/50 border border-border rounded-2xl p-6 shadow-sm group">
      <div class="absolute -right-12 -top-12 w-64 h-64 bg-primary/5 rounded-full blur-3xl group-hover:bg-primary/10 transition-colors"></div>
      
      <div class="relative flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary border border-primary/20">
            <Users class="w-6 h-6" />
          </div>
          <div>
            <h2 class="text-xl font-bold text-foreground flex items-center gap-2">
              Halo, {{ auth.user?.full_name || auth.username }} 👋
            </h2>
            <p class="text-sm text-muted-foreground mt-0.5 font-medium">
              Selamat datang di Panel Kendali Sistem — Akses Anda: 
              <span class="text-primary font-bold uppercase">{{ auth.userRole }}</span>
            </p>
          </div>
        </div>

        <div class="flex items-center gap-3">
          <div class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[10px] font-black uppercase tracking-widest">
            <div class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></div>
            System Online
          </div>
          <div class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-[10px] font-black uppercase tracking-widest">
            <ShieldCheck class="w-3.5 h-3.5" />
            Verified
          </div>
        </div>
      </div>
    </div>

    <!-- Stats Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
      <!-- Card 1: Role (Replacing Posts) -->
      <div class="bg-card border border-border rounded-2xl p-5 shadow-sm hover:shadow-md transition-all group">
        <div class="flex items-start justify-between">
          <div>
            <p class="text-xs font-bold text-muted-foreground uppercase tracking-wider">Total Role Akses</p>
            <h3 class="text-3xl font-bold text-foreground mt-3">{{ stats.total_roles }}</h3>
            <p class="text-[10px] text-muted-foreground mt-2 font-medium">Daftar Peran & Akses</p>
          </div>
          <div class="p-3 bg-blue-500/10 rounded-xl text-blue-500 group-hover:bg-blue-500 group-hover:text-white transition-all duration-300">
            <Shield class="w-5 h-5" />
          </div>
        </div>
      </div>

      <!-- Card 2: Log Sesi -->
      <div class="bg-card border border-border rounded-2xl p-5 shadow-sm hover:shadow-md transition-all group">
        <div class="flex items-start justify-between">
          <div>
            <p class="text-xs font-bold text-muted-foreground uppercase tracking-wider">Log Sesi</p>
            <h3 class="text-3xl font-bold text-foreground mt-3">{{ stats.active_users }}</h3>
            <p class="text-[10px] text-muted-foreground mt-2 font-medium">Akses Pengguna Aktif</p>
          </div>
          <div class="p-3 bg-pink-500/10 rounded-xl text-pink-500 group-hover:bg-pink-500 group-hover:text-white transition-all duration-300">
            <Activity class="w-5 h-5" />
          </div>
        </div>
      </div>

      <!-- Card 3: Total User -->
      <div class="bg-card border border-border rounded-2xl p-5 shadow-sm hover:shadow-md transition-all group">
        <div class="flex items-start justify-between">
          <div>
            <p class="text-xs font-bold text-muted-foreground uppercase tracking-wider">Total User</p>
            <h3 class="text-3xl font-bold text-foreground mt-3">{{ stats.total_users }}</h3>
            <p class="text-[10px] text-muted-foreground mt-2 font-medium">Daftar Administrator</p>
          </div>
          <div class="p-3 bg-purple-500/10 rounded-xl text-purple-500 group-hover:bg-purple-500 group-hover:text-white transition-all duration-300">
            <Users class="w-5 h-5" />
          </div>
        </div>
      </div>

      <!-- Card 4: Audit Log -->
      <div class="bg-card border border-border rounded-2xl p-5 shadow-sm hover:shadow-md transition-all group">
        <div class="flex items-start justify-between">
          <div>
            <p class="text-xs font-bold text-muted-foreground uppercase tracking-wider">Audit Log</p>
            <h3 class="text-3xl font-bold text-foreground mt-3">Check</h3>
            <p class="text-[10px] text-muted-foreground mt-2 font-medium">Monitoring Tindakan</p>
          </div>
          <div class="p-3 bg-slate-500/10 rounded-xl text-slate-500 group-hover:bg-slate-500 group-hover:text-white transition-all duration-300">
            <Terminal class="w-5 h-5" />
          </div>
        </div>
      </div>
    </div>
    
    <!-- Quick Actions / Info -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-2">
      <div class="lg:col-span-2 bg-card/50 border border-border border-dashed rounded-2xl p-8 flex flex-col items-center justify-center text-center space-y-4">
        <div class="w-16 h-16 bg-muted rounded-full flex items-center justify-center text-muted-foreground">
          <Activity class="w-8 h-8 opacity-20" />
        </div>
        <div>
          <h4 class="font-bold text-foreground">Aktivitas Terbaru</h4>
          <p class="text-sm text-muted-foreground max-w-xs mx-auto">Modul visualisasi grafik sedang dalam tahap pengembangan.</p>
        </div>
      </div>

      <div class="bg-primary/5 border border-primary/10 rounded-2xl p-6 flex flex-col justify-between">
        <div>
          <div class="flex items-center gap-2 text-primary font-black text-xs uppercase tracking-widest mb-4">
            <CheckCircle2 class="w-4 h-4" />
            Tips Keamanan
          </div>
          <p class="text-sm font-medium text-foreground leading-relaxed">
            Selalu periksa <span class="font-bold underline decoration-primary/30">Audit Log</span> secara berkala untuk memastikan tidak ada aktivitas mencurigakan dari akun administrator lain.
          </p>
        </div>
        <router-link to="/settings/audit-logs">
          <Button variant="link" class="p-0 h-auto text-primary font-bold text-xs">
            Lihat Semua Log →
          </Button>
        </router-link>
      </div>
    </div>
  </div>
</template>
