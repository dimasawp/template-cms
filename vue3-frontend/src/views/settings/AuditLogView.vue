<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { onClickOutside } from '@vueuse/core'
import auditService from '@/services/auditService'
import { useDataTable } from '@/composables/useDataTable'
import { 
  Globe, 
  Terminal, 
  Eye, 
  ArrowUpDown, 
  ArrowUp, 
  ArrowDown, 
  Filter, 
  ChevronDown,
  X
} from 'lucide-vue-next'
import { format } from 'date-fns'
import { id } from 'date-fns/locale'
import Pagination from '@/components/common/Pagination.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import Button from '@/components/ui/Button.vue'
import Label from '@/components/ui/Label.vue'
import SkeletonLoader from '@/components/ui/SkeletonLoader.vue'
import Dialog from '@/components/ui/Dialog.vue'
import Badge from '@/components/ui/Badge.vue'
import PopoverHeader from '@/components/ui/PopoverHeader.vue'
import DataTableToolbar from '@/components/common/DataTableToolbar.vue'

const { 
  items: logs, 
  isLoading: loading, 
  pagination, 
  filters,
  sort,
  fetchItems,
  goToPage,
  setSortField,
  setSortDirection 
} = useDataTable({
  fetchData: async (params) => {
    const { data: res } = await auditService.getLogs(params)
    return { items: res.data.items, total: res.data.pagination.total }
  },
  perPage: 10
})

const showFilters = ref(false)
const showSort = ref(false)

const selectedLog = ref(null)
const showDetailModal = ref(false)

const moduleCategories = [
  {
    label: 'Akun & Akses',
    modules: ['AUTH', 'USERS', 'ROLES']
  },
  {
    label: 'Sistem & Pengaturan',
    modules: ['SETTINGS', 'NOTIFICATIONS', 'SYSTEM']
  }
]

const openDetail = (log) => {
  selectedLog.value = log
  showDetailModal.value = true
}

const formatDateTime = (dateStr) => {
  return format(new Date(dateStr), 'dd MMM yyyy, HH:mm:ss', { locale: id })
}

const badgeVariantMap = {
  'LOGIN': 'primary',
  'CREATE': 'success',
  'UPDATE': 'warning',
  'DELETE': 'destructive'
}

const getBadgeVariant = (action) => {
  return badgeVariantMap[action.toUpperCase()] || 'secondary'
}


const handleFilterModule = (val) => {
  filters.module = val || undefined
}

const getSortIcon = (field) => {
  if (sort.field !== field) return ArrowUpDown
  return sort.direction === 'asc' ? ArrowUp : ArrowDown
}

// ── Interaction Logic ────────────────────────────────────────────────
const filterRef = ref(null)
const sortRef = ref(null)
const modalRef = ref(null)

onClickOutside(filterRef, () => { showFilters.value = false })
onClickOutside(sortRef, () => { showSort.value = false })
onClickOutside(modalRef, () => { showDetailModal.value = false })

const handleEsc = (e) => {
  if (e.key === 'Escape') {
    showFilters.value = false
    showSort.value = false
    showDetailModal.value = false
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleEsc)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleEsc)
})
</script>

<template>
  <div>
    <PageHeader title="Audit Trail" description="Monitor seluruh aktifitas dan perubahan data sistem." />

    <!-- Toolbar -->
    <DataTableToolbar
      v-model:search-model-value="filters.search"
      search-placeholder="Cari audit log (user, deskripsi)..."
      :is-loading="loading"
      @refresh="fetchItems"
    >
      <template #actions-start>
        <!-- Filter Button & Popover -->
        <div class="relative">
          <Button 
            variant="outline" 
            size="sm" 
            class="h-10 px-3 flex items-center gap-2 border-input hover:bg-accent transition-colors shadow-sm"
            :class="Object.keys(filters).length > 0 ? 'bg-primary/10 border-primary/20 text-primary' : 'bg-background text-foreground'"
            @click="showFilters = !showFilters; showSort = false"
          >
            <Filter class="h-4 w-4" />
            <span>Filter</span>
            <ChevronDown class="h-3 w-3 transition-transform" :class="{'rotate-180': showFilters}" />
          </Button>

          <!-- Popover Menu -->
          <div v-if="showFilters" ref="filterRef" class="absolute right-0 top-full mt-2 w-80 bg-popover rounded-xl shadow-xl border border-border p-4 z-50">
            <PopoverHeader title="Filter Audit" @close="showFilters = false" />

            <div class="space-y-5">
              <div>
                <Label class="text-[10px] uppercase tracking-wider text-muted-foreground mb-2.5 block font-bold">Modul / Fitur</Label>
                <div class="max-h-60 overflow-y-auto pr-1 custom-scrollbar space-y-3">
                  <button 
                    @click="handleFilterModule('')"
                    class="w-full text-left px-3 py-2 rounded-lg text-xs font-medium transition-colors flex items-center justify-between"
                    :class="!filters.module ? 'bg-accent text-primary' : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'"
                  >
                    Semua Modul
                    <div v-if="!filters.module" class="w-1.5 h-1.5 rounded-full bg-primary shadow-[0_0_8px_rgba(79,70,229,0.4)]"></div>
                  </button>
                  
                  <div v-for="cat in moduleCategories" :key="cat.label" class="space-y-1">
                    <span class="px-3 text-[9px] font-bold text-slate-300 uppercase tracking-widest">{{ cat.label }}</span>
                    <button 
                      v-for="m in cat.modules" 
                      :key="m"
                      @click="handleFilterModule(m)"
                      class="w-full text-left px-3 py-1.5 rounded-lg text-xs font-medium transition-colors flex items-center justify-between"
                      :class="filters.module === m ? 'bg-accent text-primary' : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'"
                    >
                      {{ m }}
                      <div v-if="filters.module === m" class="w-1.5 h-1.5 rounded-full bg-primary shadow-[0_0_8px_rgba(79,70,229,0.4)]"></div>
                    </button>
                  </div>
                </div>
              </div>

              <div>
                <Label class="text-[10px] uppercase tracking-wider text-muted-foreground mb-2.5 block font-bold">Tipe Aksi</Label>
                <div class="grid grid-cols-2 gap-2">
                  <button 
                    v-for="a in ['LOGIN', 'CREATE', 'UPDATE', 'DELETE']" 
                    :key="a"
                    @click="filters.action = (filters.action === a ? undefined : a)"
                    class="px-2 py-2 rounded-lg text-[10px] font-bold border transition-all text-left flex items-center justify-between"
                    :class="[
                      filters.action === a
                      ? 'bg-accent border-primary/20 text-primary shadow-sm'
                      : 'bg-background border-border text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                    ]"
                  >
                    {{ a }}
                    <div v-if="filters.action === a" class="w-1.5 h-1.5 rounded-full bg-primary shadow-[0_0_8px_rgba(79,70,229,0.4)]"></div>
                  </button>
                </div>
              </div>

              <div class="pt-2">
                <Button variant="outline" size="sm" class="w-full h-9 text-[11px] font-bold border-input text-muted-foreground shadow-sm hover:bg-accent hover:text-accent-foreground" @click="filters.module = undefined; filters.action = undefined">
                  Reset Semua Filter
                </Button>
              </div>
            </div>
          </div>
        </div>

        <!-- Sort Button & Popover -->
        <div class="relative">
          <Button 
            variant="outline" 
            size="sm" 
            class="h-10 px-3 flex items-center gap-2 border-input hover:bg-accent transition-colors shadow-sm text-foreground"
            @click="showSort = !showSort; showFilters = false"
          >
            <ArrowUpDown class="h-4 w-4 text-muted-foreground" />
            <span>Urutkan</span>
            <ChevronDown class="h-3 w-3 transition-transform" :class="{'rotate-180': showSort}" />
          </Button>

          <!-- Popover Menu -->
          <div v-if="showSort" ref="sortRef" class="absolute right-0 top-full mt-2 w-56 bg-popover rounded-xl shadow-xl border border-border p-4 z-50">
            <PopoverHeader title="Urutkan Data" @close="showSort = false" />

            <div class="space-y-4">
              <div>
                <Label class="text-[10px] uppercase tracking-wider text-muted-foreground mb-2.5 block font-bold">Berdasarkan</Label>
                <div class="space-y-1">
                  <button 
                    v-for="f in [{id:'action', label:'Aksi'}, {id:'module', label:'Modul'}, {id:'created_at', label:'Waktu'}]" 
                    :key="f.id"
                    @click="setSortField(f.id)"
                    class="w-full text-left px-3 py-2.5 rounded-lg text-xs font-medium transition-colors flex items-center justify-between"
                    :class="sort.field === f.id ? 'bg-accent text-primary shadow-sm' : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'"
                  >
                    {{ f.label }}
                    <div v-if="sort.field === f.id" class="w-1.5 h-1.5 rounded-full bg-primary shadow-[0_0_8px_rgba(79,70,229,0.4)]"></div>
                  </button>
                </div>
              </div>

              <div class="pt-2 border-t border-slate-100">
                <Label class="text-[10px] uppercase tracking-wider text-muted-foreground mb-2.5 block font-bold">Urutan</Label>
                <div class="grid grid-cols-2 gap-2">
                  <button 
                    @click="setSortDirection('asc')"
                    class="flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-xs font-medium transition-colors border shadow-sm"
                    :class="sort.direction === 'asc' ? 'bg-accent border-primary/20 text-primary shadow-sm' : 'bg-background border-border text-muted-foreground hover:bg-accent hover:text-accent-foreground'"
                  >
                    <ArrowUp class="w-3 h-3" />
                    Asc
                  </button>
                  <button 
                    @click="setSortDirection('desc')"
                    class="flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-xs font-medium transition-colors border shadow-sm"
                    :class="sort.direction === 'desc' ? 'bg-accent border-primary/20 text-primary shadow-sm' : 'bg-background border-border text-muted-foreground hover:bg-accent hover:text-accent-foreground'"
                  >
                    <ArrowDown class="w-3 h-3" />
                    Desc
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </DataTableToolbar>

      <!-- Active Filter Chips -->
      <div v-if="Object.keys(filters).length > 0" class="flex flex-wrap items-center gap-2">
        <span class="text-[11px] font-medium text-muted-foreground mr-1">Filter Aktif:</span>
        
        <div v-if="filters.module" class="flex items-center gap-1.5 px-2 py-1 bg-primary/10 text-primary border border-primary/20 rounded-full text-[11px] font-bold">
          <span>Modul: {{ filters.module }}</span>
          <button @click="filters.module = undefined; fetchItems()" class="hover:text-primary-foreground"><X class="h-3 w-3" /></button>
        </div>
        
        <div v-if="filters.action" class="flex items-center gap-1.5 px-2 py-1 bg-primary/10 text-primary border border-primary/20 rounded-full text-[11px] font-bold">
          <span>Aksi: {{ filters.action }}</span>
          <button @click="filters.action = undefined; fetchItems()" class="hover:text-primary-foreground"><X class="h-3 w-3" /></button>
        </div>

        <button @click="Object.keys(filters).forEach(k => delete filters[k]); fetchItems()" class="text-[11px] text-muted-foreground hover:text-destructive font-bold ml-2 border-b border-transparent hover:border-destructive/30 transition-all">
          Hapus Semua
        </button>
      </div>

    <!-- Table -->
    <div class="bg-card rounded-xl border border-border shadow-sm overflow-hidden min-h-[400px] flex flex-col">
      <div class="overflow-x-auto flex-1">
        <table class="w-full text-left border-collapse text-sm">
          <thead>
            <tr class="bg-muted/80 border-b border-border">
              <th 
                class="px-6 py-4 font-bold text-muted-foreground cursor-pointer hover:bg-muted transition-colors group"
                @click="setSortField('created_at')"
              >
                <div class="flex items-center gap-2">
                  Waktu
                  <component 
                    :is="getSortIcon('created_at')" 
                    class="w-3.5 h-3.5 transition-colors" 
                    :class="sort.field === 'created_at' ? 'text-primary' : 'text-muted-foreground/30 group-hover:text-muted-foreground/50'" 
                  />
                </div>
              </th>
              <th class="px-6 py-4 font-bold text-muted-foreground">User</th>
              <th 
                class="px-6 py-4 font-bold text-muted-foreground cursor-pointer hover:bg-muted transition-colors group"
                @click="setSortField('action')"
              >
                <div class="flex items-center gap-2">
                  Aksi
                  <component 
                    :is="getSortIcon('action')" 
                    class="w-3.5 h-3.5 transition-colors" 
                    :class="sort.field === 'action' ? 'text-primary' : 'text-muted-foreground/30 group-hover:text-muted-foreground/50'" 
                  />
                </div>
              </th>
              <th 
                class="px-6 py-4 font-bold text-muted-foreground cursor-pointer hover:bg-muted transition-colors group"
                @click="setSortField('module')"
              >
                <div class="flex items-center gap-2">
                  Modul
                  <component 
                    :is="getSortIcon('module')" 
                    class="w-3.5 h-3.5 transition-colors" 
                    :class="sort.field === 'module' ? 'text-primary' : 'text-muted-foreground/30 group-hover:text-muted-foreground/50'" 
                  />
                </div>
              </th>
              <th class="px-6 py-4 font-bold text-muted-foreground">Deskripsi</th>
              <th class="px-6 py-4 font-bold text-muted-foreground text-right w-24">Detail</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border">
            <tr v-if="loading">
              <td colspan="6" class="px-6 py-12">
                <div class="space-y-4">
                  <SkeletonLoader v-for="i in 5" :key="i" class="h-10 w-full" />
                </div>
              </td>
            </tr>
            <tr v-else-if="logs.length === 0">
              <td colspan="6" class="px-6 py-20 text-center">
                <div class="flex flex-col items-center opacity-40">
                  <Search class="w-12 h-12 mb-3" />
                  <p class="italic text-muted-foreground">Data aktifitas tidak ditemukan</p>
                </div>
              </td>
            </tr>
            <tr v-for="log in logs" :key="log.id" class="hover:bg-muted/50 transition-colors group border-border">
              <td class="px-6 py-4 text-muted-foreground whitespace-nowrap text-xs">
                {{ formatDateTime(log.created_at) }}
              </td>
              <td class="px-6 py-4">
                <div class="flex items-center gap-2">
                  <div class="w-8 h-8 rounded-full bg-muted flex items-center justify-center text-foreground font-bold text-[10px] border border-border transition-colors group-hover:border-primary/30">
                    {{ log.user?.username.substring(0, 2).toUpperCase() || 'SYS' }}
                  </div>
                  <div>
                    <div class="font-bold text-foreground leading-none mb-1">{{ log.user?.full_name || 'System' }}</div>
                    <div class="text-[10px] text-muted-foreground font-mono">@{{ log.user?.username || 'system' }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4">
                <Badge :variant="getBadgeVariant(log.action)" size="sm">
                  {{ log.action }}
                </Badge>
              </td>
              <td class="px-6 py-4 text-foreground/80 font-bold whitespace-nowrap uppercase text-[10px] tracking-wider">
                {{ log.module }}
              </td>
              <td class="px-6 py-4 text-muted-foreground max-w-xs truncate text-xs" :title="log.description || ''">
                {{ log.description }}
              </td>
              <td class="px-6 py-4 text-center border-l border-border/50 bg-muted/5">
                <button 
                  @click="openDetail(log)"
                  class="p-1.5 text-primary hover:bg-accent hover:shadow-sm rounded-lg transition-all border border-transparent hover:border-border"
                >
                  <Eye class="w-4 h-4" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="px-6 py-4 bg-muted/30 border-t border-border flex items-center justify-between mt-auto">
        <div class="text-xs text-muted-foreground">
          Showing <span class="font-bold text-foreground">{{ logs.length }}</span> of <span class="font-bold text-foreground">{{ pagination.total }}</span> activities
        </div>
        <Pagination 
          :current-page="pagination.page" 
          :total-pages="pagination.totalPages" 
          @page-change="goToPage"
        />
      </div>
    </div>

    <!-- Detail Modal -->
    <Dialog 
      :open="showDetailModal" 
      :title="`Detail Log Aktifitas #${selectedLog?.id}`"
      max-width="max-w-3xl"
      @close="showDetailModal = false"
    >
      <div class="space-y-6">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="bg-muted/40 p-3 rounded-xl border border-border">
            <div class="text-[10px] uppercase font-bold text-muted-foreground mb-1 flex items-center gap-1">
              <Eye class="w-3 h-3" /> User
            </div>
            <div class="text-xs font-bold text-foreground truncate">{{ selectedLog?.user?.full_name || 'System' }}</div>
          </div>
          <div class="bg-muted/40 p-3 rounded-xl border border-border">
            <div class="text-[10px] uppercase font-bold text-muted-foreground mb-1 flex items-center gap-1">
              <Globe class="w-3 h-3" /> IP Address
            </div>
            <div class="text-xs font-bold text-foreground">{{ selectedLog?.ip_address || '-' }}</div>
          </div>
          <div class="bg-muted/40 p-3 rounded-xl border border-border col-span-2">
            <div class="text-[10px] uppercase font-bold text-muted-foreground mb-1 flex items-center gap-1">
              <Terminal class="w-3 h-3" /> User Agent
            </div>
            <div class="text-[10px] font-medium text-muted-foreground line-clamp-1">{{ selectedLog?.user_agent || '-' }}</div>
          </div>
        </div>

        <!-- Payload Comparison -->
        <div class="space-y-4" v-if="selectedLog?.payload_before || selectedLog?.payload_after">
          <h4 class="text-sm font-bold text-foreground border-l-4 border-primary pl-3">Data Changes (JSON)</h4>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <div class="text-[10px] font-bold text-muted-foreground uppercase mb-2 text-center">Before</div>
              <pre class="bg-slate-900 text-slate-100 p-4 rounded-xl text-[10px] overflow-auto max-h-60 leading-relaxed shadow-inner">{{ JSON.stringify(selectedLog?.payload_before, null, 2) || 'None' }}</pre>
            </div>
            <div>
              <div class="text-[10px] font-bold text-primary uppercase mb-2 text-center">After</div>
              <pre class="bg-slate-900 border border-indigo-500/30 text-indigo-100 p-4 rounded-xl text-[10px] overflow-auto max-h-60 leading-relaxed shadow-inner">{{ JSON.stringify(selectedLog?.payload_after, null, 2) || 'None' }}</pre>
            </div>
          </div>
        </div>
        
        <div v-else class="text-center py-8 bg-muted/40 rounded-2xl border-2 border-dashed border-border">
          <div class="text-muted-foreground text-xs italic">No payload data recorded for this action.</div>
        </div>
      </div>

      <template #footer>
        <Button variant="outline" @click="showDetailModal = false">Close</Button>
      </template>
    </Dialog>
  </div>
</template>

<style scoped>
pre {
  scrollbar-width: thin;
  scrollbar-color: #475569 transparent;
}
pre::-webkit-scrollbar {
  width: 4px;
  height: 4px;
}
pre::-webkit-scrollbar-thumb {
  background: #475569;
  border-radius: 10px;
}
</style>
