<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { authService } from '@/services/authService'
import { useToast } from '@/composables/useToast'
import { useConfirmation } from '@/composables/useConfirmation'
import { useAuthStore } from '@/stores/auth'
import PageHeader from '@/components/common/PageHeader.vue'
import Button from '@/components/ui/Button.vue'
import SkeletonLoader from '@/components/ui/SkeletonLoader.vue'
import ConfirmationDialog from '@/components/ui/ConfirmationDialog.vue'
import { 
  Monitor, 
  Tablet, 
  Smartphone, 
  LogOut, 
  RefreshCw, 
  ShieldAlert, 
  Search, 
  Trash2, 
  CheckSquare, 
  Square 
} from 'lucide-vue-next'

const { toast } = useToast()
const confirm = useConfirmation()
const auth = useAuthStore()

const sessions = ref<any[]>([])
const isLoading = ref(true)
const searchQuery = ref('')
const selectedIds = ref<number[]>([])

async function fetchSessions() {
  isLoading.value = true
  try {
    const { data: res } = await authService.getSessions()
    sessions.value = res.data
  } catch (err: any) {
    toast({ title: 'Error', description: 'Gagal memuat sesi aktif', variant: 'destructive' })
  } finally {
    isLoading.value = false
  }
}

const filteredSessions = computed(() => {
  if (!searchQuery.value) return sessions.value
  const q = searchQuery.value.toLowerCase()
  return sessions.value.filter(s => 
    s.full_name?.toLowerCase().includes(q) || 
    s.username?.toLowerCase().includes(q) ||
    s.ip_address?.includes(q)
  )
})

const isAllSelected = computed(() => {
  return filteredSessions.value.length > 0 && 
         filteredSessions.value.every(s => selectedIds.value.includes(s.id))
})

function toggleSelectAll() {
  if (isAllSelected.value) {
    // If all currently visible are selected, unselect only these
    const visibleIds = filteredSessions.value.map(s => s.id)
    selectedIds.value = selectedIds.value.filter(id => !visibleIds.includes(id))
  } else {
    // Select all visible that are not already selected
    const visibleIds = filteredSessions.value.map(s => s.id)
    const newSelection = [...new Set([...selectedIds.value, ...visibleIds])]
    selectedIds.value = newSelection
  }
}

function toggleSelect(id: number) {
  const index = selectedIds.value.indexOf(id)
  if (index > -1) {
    selectedIds.value.splice(index, 1)
  } else {
    selectedIds.value.push(id)
  }
}

async function handleRevoke(session: any) {
  const ok = await confirm.confirm({
    title: 'Revoke Session?',
    message: `Apakah Anda yakin ingin menghentikan sesi untuk user "${session.username}"?`,
    variant: 'destructive',
  })

  if (!ok) return

  try {
    await authService.revokeSession(session.id)
    toast({ title: 'Berhasil', description: 'Sesi telah dihentikan', variant: 'success' })
    fetchSessions()
  } catch (err: any) {
    toast({ title: 'Gagal', description: 'Gagal menghentikan sesi', variant: 'destructive' })
  }
}

async function handleBulkRevoke() {
  const count = selectedIds.value.length
  if (count === 0) return

  const ok = await confirm.confirm({
    title: 'Mass Revoke?',
    message: `Apakah Anda yakin ingin menghentikan ${count} sesi terpilih sekaligus?`,
    variant: 'destructive',
  })

  if (!ok) return

  try {
    await authService.bulkRevokeSessions(selectedIds.value)
    toast({ title: 'Berhasil', description: `${count} sesi telah dihentikan`, variant: 'success' })
    selectedIds.value = []
    fetchSessions()
  } catch (err: any) {
    toast({ title: 'Gagal', description: 'Gagal menghentikan sesi masal', variant: 'destructive' })
  }
}

function parseUserAgent(ua: string) {
  if (!ua) return 'Unknown Device'
  if (ua.includes('Windows')) return 'Windows PC'
  if (ua.includes('Macintosh')) return 'Mac'
  if (ua.includes('Android')) return 'Android Phone'
  if (ua.includes('iPhone')) return 'iPhone'
  if (ua.includes('Linux')) return 'Linux PC'
  return ua.split(' ')[0] || 'Unknown'
}

function getDeviceIcon(ua: string) {
  if (!ua) return Monitor
  if (ua.includes('Android') || ua.includes('iPhone')) return Smartphone
  if (ua.includes('iPad')) return Tablet
  return Monitor
}

onMounted(fetchSessions)
</script>

<template>
  <div class="space-y-6 text-sm">
    <PageHeader title="Active Sessions" description="Pantau dan kelola admin yang sedang login ke sistem" />

    <!-- Controls -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div class="relative flex-1 max-w-md">
        <span class="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-400">
          <Search class="h-4 w-4" />
        </span>
        <input 
          v-model="searchQuery"
          type="text" 
          placeholder="Cari berdasarkan nama, username, atau IP..."
          class="block w-full pl-10 pr-3 py-2 border border-input rounded-lg bg-background text-foreground focus:ring-2 focus:ring-primary outline-none transition-all shadow-sm"
        />
      </div>

      <div class="flex items-center gap-2">
        <Button v-if="selectedIds.length > 0 && auth.hasPermission('sessions.delete')" variant="destructive" size="sm" @click="handleBulkRevoke">
          <Trash2 class="mr-2 h-4 w-4" />
          Hentikan {{ selectedIds.length }} Sesi
        </Button>
        <Button v-if="auth.hasPermission('sessions.delete')" variant="outline" size="sm" @click="toggleSelectAll">
          <component :is="isAllSelected ? CheckSquare : Square" class="mr-2 h-4 w-4" />
          {{ isAllSelected ? 'Batal Pilih' : 'Pilih Semua' }}
        </Button>
        <Button variant="outline" size="sm" @click="fetchSessions" :disabled="isLoading">
          <RefreshCw class="mr-2 h-4 w-4" :class="{ 'animate-spin': isLoading }" />
          Refresh
        </Button>
      </div>
    </div>

    <!-- Info Alert -->
    <div class="flex items-start gap-4 rounded-xl border border-amber-500/20 bg-amber-500/10 p-4 text-amber-500 shadow-sm">
      <ShieldAlert class="h-5 w-5 shrink-0" />
      <div class="text-xs">
        <p class="font-bold mb-1">Keamanan Sesi Real-time</p>
        <p class="opacity-90 leading-relaxed">
          Sistem kini mendukung <strong>Instant Kick</strong>. Begitu sesi dihentikan, user tersebut tidak akan bisa melakukan aksi apa pun di CMS dan akan langsung diarahkan ke halaman login.
        </p>
      </div>
    </div>

    <div v-if="isLoading" class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      <SkeletonLoader v-for="i in 6" :key="i" class="h-32 w-full rounded-xl" />
    </div>

    <div v-else class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      <div 
        v-for="s in filteredSessions" 
        :key="s.id" 
        :class="[
          'relative flex flex-col gap-3 rounded-xl border p-5 transition-all group',
          auth.hasPermission('sessions.delete') ? 'cursor-pointer' : 'cursor-default',
          selectedIds.includes(s.id) ? 'border-primary ring-2 ring-primary/20 bg-primary/5' : 'bg-card border-border hover:border-primary/50'
        ]"
        @click="auth.hasPermission('sessions.delete') ? toggleSelect(s.id) : null"
      >
        <!-- Selection Checkbox -->
        <div class="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity" :class="{'opacity-100': selectedIds.includes(s.id)}">
          <div :class="['w-5 h-5 rounded border flex items-center justify-center transition-colors', selectedIds.includes(s.id) ? 'bg-primary border-primary' : 'bg-background border-border']">
            <CheckSquare v-if="selectedIds.includes(s.id)" class="w-3.5 h-3.5 text-white" />
          </div>
        </div>

        <div class="flex items-start justify-between pr-6">
          <div class="flex items-center gap-3">
            <div :class="['rounded-full p-2.5 transition-colors', selectedIds.includes(s.id) ? 'bg-primary text-white' : 'bg-muted text-muted-foreground']">
              <component :is="getDeviceIcon(s.user_agent)" class="h-5 w-5" />
            </div>
            <div>
              <h4 class="font-bold text-foreground">{{ s.full_name }}</h4>
              <p class="text-[11px] text-muted-foreground font-mono">@{{ s.username }}</p>
            </div>
          </div>
          
          <button 
            v-if="auth.hasPermission('sessions.delete')"
            @click.stop="handleRevoke(s)"
            class="p-2 text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded-lg transition-all"
            title="Kick User"
          >
            <LogOut class="h-5 w-5" />
          </button>
        </div>

        <div class="mt-2 space-y-2.5 border-t border-border pt-3">
          <div class="flex justify-between items-center text-[11px]">
            <span class="text-muted-foreground font-medium">IP ADDRESS</span>
            <span class="font-bold text-foreground bg-muted px-2 py-0.5 rounded">{{ s.ip_address || 'Unknown' }}</span>
          </div>
          <div class="flex justify-between items-center text-[11px]">
            <span class="text-muted-foreground font-medium">DEVICE / OS</span>
            <span class="text-foreground font-semibold max-w-[150px] truncate" :title="s.user_agent">{{ parseUserAgent(s.user_agent) }}</span>
          </div>
          <div class="flex justify-between items-center text-[11px]">
            <span class="text-muted-foreground font-medium">LOGIN TIME</span>
            <span class="text-foreground">{{ new Date(s.created_at + 'Z').toLocaleString('id-ID') }}</span>
          </div>
        </div>
      </div>

      <div v-if="filteredSessions.length === 0" class="col-span-full flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-border py-16 text-muted-foreground">
        <div class="bg-muted p-4 rounded-full mb-4">
          <Monitor class="h-10 w-10 opacity-40" />
        </div>
        <p class="font-medium">Tidak ada sesi aktif yang cocok dengan kriteria Anda.</p>
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
