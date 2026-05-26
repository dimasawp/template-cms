<script setup>
import { ref, computed, onMounted } from 'vue'
import auditService from '@/services/auditService'
import { useDataTable } from '@/composables/useDataTable'
import { 
  Terminal, 
  Eye, 
  ArrowUpDown, 
  ArrowUp, 
  ArrowDown, 
  Filter, 
  ChevronDown,
  X,
  Search,
  Globe
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
import Popover from '@/components/ui/Popover.vue'
import DataTableToolbar from '@/components/common/DataTableToolbar.vue'
import EmptyState from '@/components/ui/EmptyState.vue'

const { 
  items: logs, 
  isLoading, 
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

const showDetailModal = ref(false)
const selectedLog = ref(null)

const moduleCategories = [
  {
    label: 'Accounts & Access',
    modules: ['AUTH', 'USERS', 'ROLES']
  },
  {
    label: 'System & Settings',
    modules: ['SETTINGS', 'NOTIFICATIONS', 'SYSTEM']
  }
]

const openDetail = (log) => {
  selectedLog.value = log
  showDetailModal.value = true
}

const hasActiveFilters = computed(() => {
  return !!filters.module || !!filters.action
})

const formatDateTime = (dateStr) => {
  return format(new Date(dateStr), 'dd MMM yyyy, HH:mm:ss', { locale: id })
}

const badgeVariantMap = {
  'LOGIN': 'primary',
  'CREATE': 'success',
  'UPDATE': 'warning',
  'DELETE': 'destructive',
  'RESET': 'destructive'
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

onMounted(() => {
  fetchItems()
})
</script>

<template>
  <div class="space-y-6 animate-in fade-in duration-700">
    <PageHeader title="Audit Trail" description="Monitor all system activities and data changes." />

    <!-- Toolbar -->
    <DataTableToolbar
      v-model:search-model-value="filters.search"
      search-placeholder="Search audit logs (user, description)..."
      :is-loading="isLoading"
      @refresh="fetchItems"
    >
      <template #actions-start>
        <!-- Filter Popover -->
        <Popover align="right" width="w-80">
          <template #trigger="{ isOpen }">
            <Button 
              variant="outline" 
              size="sm" 
              class="h-10 px-3 flex items-center gap-2 border-input hover:bg-accent transition-colors shadow-sm"
              :class="hasActiveFilters ? 'bg-primary/10 border-primary/20 text-primary' : 'bg-background text-foreground'"
            >
              <Filter class="h-4 w-4" />
              <span>Filter</span>
              <ChevronDown class="h-3 w-3 transition-transform" :class="{'rotate-180': isOpen}" />
            </Button>
          </template>

          <template #default="{ close }">
             <PopoverHeader title="Filter Audit" @close="close" />

            <div class="space-y-5">
              <div>
                <Label class="text-[10px] uppercase tracking-wider text-muted-foreground mb-2.5 block font-bold">Module / Feature</Label>
                <div class="max-h-60 overflow-y-auto pr-1 custom-scrollbar space-y-1">
                  <button 
                    @click="handleFilterModule('')"
                    class="w-full text-left px-3 py-2 rounded-lg text-xs font-medium transition-colors flex items-center justify-between"
                    :class="!filters.module ? 'bg-accent text-primary font-bold' : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'"
                  >
                    All Modules
                    <div v-if="!filters.module" class="w-1.5 h-1.5 rounded-full bg-primary shadow-[0_0_8px_rgba(79,70,229,0.4)]"></div>
                  </button>

                  <div v-for="cat in moduleCategories" :key="cat.label" class="space-y-1 pt-2">
                    <span class="text-[9px] font-bold text-muted-foreground/60 px-3 uppercase tracking-widest">{{ cat.label }}</span>
                    <button 
                      v-for="m in cat.modules" 
                      :key="m"
                      @click="handleFilterModule(m)"
                      class="w-full text-left px-3 py-2 rounded-lg text-xs font-medium transition-colors flex items-center justify-between"
                      :class="filters.module === m ? 'bg-accent text-primary font-bold' : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'"
                    >
                      {{ m }}
                      <div v-if="filters.module === m" class="w-1.5 h-1.5 rounded-full bg-primary shadow-[0_0_8px_rgba(79,70,229,0.4)]"></div>
                    </button>
                  </div>
                </div>
              </div>

              <div>
                <Label class="text-[10px] uppercase tracking-wider text-muted-foreground mb-2.5 block font-bold">Action</Label>
                <div class="grid grid-cols-2 gap-2">
                  <button 
                    v-for="a in ['', 'CREATE', 'UPDATE', 'DELETE', 'RESET', 'LOGIN']" 
                    :key="a"
                    @click="filters.action = a || undefined"
                    class="px-2 py-2 rounded-lg text-[10px] font-bold border transition-all"
                    :class="[
                      (a === '' && !filters.action) || filters.action === a
                      ? 'bg-primary text-white border-primary shadow-md'
                      : 'bg-background border-border text-muted-foreground hover:bg-muted'
                    ]"
                  >
                    {{ a || 'ALL' }}
                  </button>
                </div>
              </div>
            </div>
          </template>
        </Popover>

        <!-- Sort Popover -->
        <Popover align="right" width="w-56">
          <template #trigger="{ isOpen }">
            <Button 
              variant="outline" 
              size="sm" 
              class="h-10 px-3 flex items-center gap-2 border-input hover:bg-accent transition-colors shadow-sm text-foreground"
            >
              <ArrowUpDown class="h-4 w-4 text-muted-foreground" />
              <span>Sort</span>
              <ChevronDown class="h-3 w-3 transition-transform" :class="{'rotate-180': isOpen}" />
            </Button>
          </template>

          <template #default="{ close }">
            <PopoverHeader title="Sort Data" @close="close" />

            <div class="space-y-4">
              <div>
                <Label class="text-[10px] uppercase tracking-wider text-muted-foreground mb-2.5 block font-bold">Sort By</Label>
                <div class="space-y-1">
                  <button 
                    v-for="f in [{id:'action', label:'Action'}, {id:'module', label:'Module'}, {id:'created_at', label:'Time'}]" 
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
                <Label class="text-[10px] uppercase tracking-wider text-muted-foreground mb-2.5 block font-bold">Direction</Label>
                <div class="grid grid-cols-2 gap-2">
                  <button 
                    @click="setSortDirection('asc')"
                    class="flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-xs font-bold border transition-all"
                    :class="sort.direction === 'asc' ? 'bg-primary text-white border-primary shadow-md' : 'bg-background text-muted-foreground border-border hover:bg-muted'"
                  >
                    <ArrowUp class="w-3 h-3" />
                    ASC
                  </button>
                  <button 
                    @click="setSortDirection('desc')"
                    class="flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-xs font-bold border transition-all"
                    :class="sort.direction === 'desc' ? 'bg-primary text-white border-primary shadow-md' : 'bg-background text-muted-foreground border-border hover:bg-muted'"
                  >
                    <ArrowDown class="w-3 h-3" />
                    DESC
                  </button>
                </div>
              </div>
            </div>
          </template>
        </Popover>
      </template>
    </DataTableToolbar>

    <!-- Active Filter Chips -->
    <div v-if="hasActiveFilters" class="mb-4 flex flex-wrap items-center gap-2 px-1 animate-in fade-in slide-in-from-top-1 duration-300">
      <div class="flex items-center gap-1.5 px-2.5 py-1.5 bg-muted/50 border border-border rounded-lg text-[10px] font-bold text-muted-foreground uppercase tracking-wider shadow-sm">
        <Filter class="h-3 w-3" />
        Active Filters
      </div>
      
      <div v-if="filters.module" class="flex items-center gap-1.5 px-3 py-1.5 bg-primary/10 text-primary border border-primary/20 rounded-full text-[11px] font-bold shadow-sm transition-all hover:bg-primary/20">
        <span class="opacity-70">Module:</span>
        <span>{{ filters.module }}</span>
        <button @click="filters.module = undefined; fetchItems()" class="ml-1 hover:text-primary-foreground transition-colors"><X class="h-3.5 w-3.5" /></button>
      </div>
      
      <div v-if="filters.action" class="flex items-center gap-1.5 px-3 py-1.5 bg-primary/10 text-primary border border-primary/20 rounded-full text-[11px] font-bold shadow-sm transition-all hover:bg-primary/20">
        <span class="opacity-70">Action:</span>
        <span>{{ filters.action }}</span>
        <button @click="filters.action = undefined; fetchItems()" class="ml-1 hover:text-primary-foreground transition-colors"><X class="h-3.5 w-3.5" /></button>
      </div>

      <button @click="Object.keys(filters).forEach(k => { if(k !== 'search') delete filters[k] }); fetchItems()" class="text-[11px] text-muted-foreground hover:text-destructive font-bold px-2 py-1.5 rounded-lg hover:bg-destructive/5 transition-all ml-1">
        Clear All
      </button>
    </div>

    <!-- Content Area -->
    <div v-if="isLoading" class="space-y-3">
      <SkeletonLoader v-for="i in 5" :key="i" class="h-14 w-full" />
    </div>

    <EmptyState 
      v-else-if="logs.length === 0" 
      :icon="Terminal" 
      title="Audit Log Empty" 
      description="No activity history found for these filter criteria."
    >
      <template #actions>
        <Button variant="outline" size="sm" @click="Object.keys(filters).forEach(k => delete filters[k]); fetchItems()">
          Reset Filters
        </Button>
      </template>
    </EmptyState>
    
    <div v-else class="rounded-md border border-border overflow-x-auto bg-card shadow-sm">
      <table class="w-full text-sm">
        <thead class="bg-muted/80 text-muted-foreground border-b border-border">
          <tr>
            <th 
              class="px-6 py-4 font-bold cursor-pointer hover:bg-muted transition-colors group text-left w-[180px]"
              @click="setSortField('created_at')"
            >
              <div class="flex items-center gap-2">
                Time
                <component :is="getSortIcon('created_at')" class="w-3.5 h-3.5 text-muted-foreground group-hover:text-primary" />
              </div>
            </th>
            <th class="px-6 py-4 font-bold text-muted-foreground text-left">User</th>
            <th 
              class="px-6 py-4 font-bold text-muted-foreground cursor-pointer hover:bg-muted transition-colors group text-left w-[120px]"
              @click="setSortField('action')"
            >
              <div class="flex items-center gap-2">
                Action
                <component :is="getSortIcon('action')" class="w-3.5 h-3.5 text-muted-foreground group-hover:text-primary" />
              </div>
            </th>
            <th 
              class="px-6 py-4 font-bold text-muted-foreground cursor-pointer hover:bg-muted transition-colors group text-left w-[150px]"
              @click="setSortField('module')"
            >
              <div class="flex items-center gap-2">
                Module
                <component :is="getSortIcon('module')" class="w-3.5 h-3.5 text-muted-foreground group-hover:text-primary" />
              </div>
            </th>
            <th class="px-6 py-4 font-bold text-muted-foreground text-left">Description</th>
            <th class="px-6 py-4 font-bold text-center w-24">Detail</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-border">
          <tr v-for="log in logs" :key="log.id" class="hover:bg-muted/50 transition-colors group">
            <td class="px-6 py-3 text-muted-foreground whitespace-nowrap text-xs">
              {{ formatDateTime(log.created_at) }}
            </td>
            <td class="px-6 py-3">
              <div class="flex items-center gap-2">
                <div class="w-7 h-7 rounded-full bg-muted flex items-center justify-center text-foreground font-bold text-[9px] border border-border">
                  {{ log.user?.username.substring(0, 2).toUpperCase() || 'SY' }}
                </div>
                <div class="flex flex-col">
                  <span class="font-bold text-foreground leading-none text-xs">{{ log.user?.full_name || 'System' }}</span>
                  <span class="text-[9px] text-muted-foreground font-mono">@{{ log.user?.username || 'system' }}</span>
                </div>
              </div>
            </td>
            <td class="px-6 py-3">
              <Badge :variant="getBadgeVariant(log.action)" size="sm" class="text-[10px] font-bold">
                {{ log.action }}
              </Badge>
            </td>
            <td class="px-6 py-3 text-foreground/80 font-bold whitespace-nowrap uppercase text-[10px] tracking-wider">
              {{ log.module }}
            </td>
            <td class="px-6 py-3 text-muted-foreground truncate text-xs" :title="log.description || ''">
              {{ log.description }}
            </td>
            <td class="px-6 py-3 text-center border-l border-border/50 bg-muted/5">
              <button 
                @click="openDetail(log)"
                class="p-1.5 hover:bg-accent rounded-lg transition-all border border-transparent hover:border-border"
              >
                <Eye class="w-4 h-4" />
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="logs.length > 0" class="mt-4 flex items-center justify-between">
      <p class="text-sm text-muted-foreground">Total: {{ pagination.total }}</p>
      <Pagination :current-page="pagination.page" :total-pages="pagination.totalPages" @page-change="goToPage" />
    </div>

    <!-- Detail Modal -->
    <Dialog 
      :open="showDetailModal" 
      :title="`Activity Log Detail #${selectedLog?.id}`"
      max-width="max-w-3xl"
      @close="showDetailModal = false"
    >
      <div class="space-y-6">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="bg-muted/40 p-4 rounded-xl border border-border shadow-sm">
            <div class="text-[11px] uppercase font-bold text-muted-foreground mb-1.5 flex items-center gap-1.5">
              <Eye class="w-3.5 h-3.5" /> User
            </div>
            <div class="text-sm font-bold text-foreground truncate">{{ selectedLog?.user?.full_name || 'System' }}</div>
          </div>
          <div class="bg-muted/40 p-4 rounded-xl border border-border shadow-sm">
            <div class="text-[11px] uppercase font-bold text-muted-foreground mb-1.5 flex items-center gap-1.5">
              <Globe class="w-3.5 h-3.5" /> IP Address
            </div>
            <div class="text-sm font-bold text-foreground">{{ selectedLog?.ip_address || '-' }}</div>
          </div>
          <div class="bg-muted/40 p-4 rounded-xl border border-border shadow-sm col-span-2">
            <div class="text-[11px] uppercase font-bold text-muted-foreground mb-1.5 flex items-center gap-1.5">
              <Terminal class="w-3.5 h-3.5" /> User Agent
            </div>
            <div class="text-xs font-medium text-muted-foreground line-clamp-1" :title="selectedLog?.user_agent">{{ selectedLog?.user_agent || '-' }}</div>
          </div>
        </div>

        <!-- Payload Comparison -->
        <div class="space-y-4" v-if="selectedLog?.payload_before || selectedLog?.payload_after">
          <h4 class="text-sm font-bold text-foreground border-l-4 border-primary pl-3">Data Changes (JSON)</h4>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <div class="text-xs font-bold text-muted-foreground uppercase mb-2 text-center">Before</div>
              <pre class="bg-slate-900 text-slate-100 p-4 rounded-xl text-xs overflow-auto max-h-[400px] leading-relaxed shadow-inner border border-border/10">{{ JSON.stringify(selectedLog?.payload_before, null, 2) || 'None' }}</pre>
            </div>
            <div>
              <div class="text-xs font-bold text-primary uppercase mb-2 text-center">After</div>
              <pre class="bg-slate-900 border border-primary/30 text-indigo-100 p-4 rounded-xl text-xs overflow-auto max-h-[400px] leading-relaxed shadow-inner">{{ JSON.stringify(selectedLog?.payload_after, null, 2) || 'None' }}</pre>
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
