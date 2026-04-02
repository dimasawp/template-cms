<script setup lang="ts">
import { onMounted } from 'vue'
import { notificationService } from '@/services/notificationService'
import { useToast } from '@/composables/useToast'
import { useDataTable } from '@/composables/useDataTable'
import PageHeader from '@/components/common/PageHeader.vue'
import Pagination from '@/components/common/Pagination.vue'
import Button from '@/components/ui/Button.vue'
import SkeletonLoader from '@/components/ui/SkeletonLoader.vue'
import { Bell, CheckCheck, RefreshCw, Info, AlertTriangle, AlertCircle } from 'lucide-vue-next'

const { toast } = useToast()

const { items: notifications, isLoading, pagination, fetchItems, goToPage } = useDataTable<any>({
  fetchData: async (params) => {
    const { data: res } = await notificationService.getAll(params)
    return { items: res.data.items, total: res.data.pagination.total }
  },
})

async function markAllRead() {
  try {
    await notificationService.markAllRead()
    toast({ title: 'Berhasil', description: 'Semua notifikasi telah ditandai dibaca', variant: 'success' })
    fetchItems()
  } catch (err) {
    toast({ title: 'Gagal', description: 'Gagal memperbarui status', variant: 'destructive' })
  }
}

async function markRead(id: number) {
  try {
    await notificationService.markRead(id)
    fetchItems()
  } catch (err) {
    /* ignore */
  }
}

function getIcon(type: string) {
  switch (type) {
    case 'warning': return AlertTriangle
    case 'error':   return AlertCircle
    default:        return Info
  }
}

function getColorClass(type: string) {
  switch (type) {
    case 'warning': return 'text-yellow-600 bg-yellow-50 dark:bg-yellow-900/20'
    case 'error':   return 'text-red-600 bg-red-50 dark:bg-red-900/20'
    default:        return 'text-blue-600 bg-blue-50 dark:bg-blue-900/20'
  }
}

onMounted(fetchItems)
</script>

<template>
  <div>
    <PageHeader title="Pemberitahuan System" description="Daftar notifikasi aktivitas dan peringatan sistem" />

    <div class="mb-4 flex flex-col sm:flex-row justify-between items-center gap-3">
      <div class="flex items-center gap-2">
        <Button variant="outline" size="sm" @click="fetchItems" :disabled="isLoading">
          <RefreshCw class="mr-2 h-4 w-4" :class="{ 'animate-spin': isLoading }" />
          Refresh
        </Button>
      </div>
      <Button variant="ghost" size="sm" @click="markAllRead" class="text-primary hover:text-primary">
        <CheckCheck class="mr-2 h-4 w-4" />
        Tandai Semua Dibaca
      </Button>
    </div>

    <div v-if="isLoading" class="space-y-3">
      <SkeletonLoader v-for="i in 5" :key="i" class="h-20 w-full" />
    </div>

    <div v-else class="space-y-3">
      <div 
        v-for="n in notifications" 
        :key="n.id" 
        :class="[
          'flex items-start gap-4 p-4 rounded-lg border transition-all',
          n.read_at ? 'bg-background opacity-70' : 'bg-card border-primary/20 shadow-sm'
        ]"
      >
        <div :class="['p-2 rounded-full', getColorClass(n.type)]">
          <component :is="getIcon(n.type)" class="h-5 w-5" />
        </div>
        
        <div class="flex-1 min-w-0">
          <div class="flex justify-between items-start gap-2">
            <h4 class="font-bold text-sm leading-tight" :class="{ 'text-muted-foreground font-medium': n.read_at }">
              {{ n.title }}
            </h4>
            <span class="text-[10px] text-muted-foreground whitespace-nowrap">
              {{ new Date(n.created_at + 'Z').toLocaleString('id-ID') }}
            </span>
          </div>
          <p class="text-sm mt-1 text-muted-foreground line-clamp-2">{{ n.message }}</p>
          
          <div class="mt-2 flex items-center gap-3">
            <router-link v-if="n.link" :to="n.link" class="text-xs font-medium text-primary hover:underline">
              Lihat Detail
            </router-link>
            <button 
              v-if="!n.read_at" 
              @click="markRead(n.id)" 
              class="text-[10px] text-muted-foreground hover:text-foreground underline underline-offset-2"
            >
              Tandai dibaca
            </button>
          </div>
        </div>

        <div v-if="!n.read_at" class="w-2 h-2 rounded-full bg-primary mt-1.5" />
      </div>

      <div v-if="notifications.length === 0" class="flex flex-col items-center justify-center py-20 text-muted-foreground">
        <Bell class="h-12 w-12 opacity-20 mb-4" />
        <p>Belum ada notifikasi untuk Anda.</p>
      </div>

      <!-- Pagination -->
      <div v-if="notifications.length > 0" class="mt-6 flex flex-col sm:flex-row items-center justify-between gap-4 border-t pt-4">
        <p class="text-sm text-muted-foreground">Total: {{ pagination.total }} pemberitahuan</p>
        <Pagination 
          :current-page="pagination.page" 
          :total-pages="pagination.totalPages" 
          @page-change="goToPage" 
        />
      </div>
    </div>
  </div>
</template>
