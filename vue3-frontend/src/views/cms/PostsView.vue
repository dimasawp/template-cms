<script setup>
import { ref, computed, onMounted } from 'vue'
import { watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useDataTable } from '@/composables/useDataTable'
import { useToast } from '@/composables/useToast'
import { useConfirmation } from '@/composables/useConfirmation'
import { useAuthStore } from '@/stores/auth'
import { postService } from '@/services/postService'
import { categoryService } from '@/services/categoryService'
import PageHeader from '@/components/common/PageHeader.vue'
import Pagination from '@/components/common/Pagination.vue'
import Button from '@/components/ui/Button.vue'
import Label from '@/components/ui/Label.vue'
import ConfirmationDialog from '@/components/ui/ConfirmationDialog.vue'
import SkeletonLoader from '@/components/ui/SkeletonLoader.vue'
import Badge from '@/components/ui/Badge.vue'
import StatusIndicator from '@/components/ui/StatusIndicator.vue'
import PopoverHeader from '@/components/ui/PopoverHeader.vue'
import Popover from '@/components/ui/Popover.vue'
import { formatWIB } from '@/helpers/dateHelper'
import EmptyState from '@/components/ui/EmptyState.vue'
import DataTableToolbar from '@/components/common/DataTableToolbar.vue'
import { 
  Pencil, 
  Trash2, 
  ArrowUpDown, 
  ArrowUp, 
  ArrowDown, 
  FileText,
  Filter,
  ChevronDown,
  X
} from 'lucide-vue-next'

const { toast } = useToast()
const confirm = useConfirmation()
const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const { items: posts, isLoading, pagination, filters, sort, fetchItems, goToPage, setSortField, setSortDirection } = useDataTable({
  fetchData: async (params) => {
    const { data: res } = await postService.getAll(params)
    return { items: res.data.items, total: res.data.pagination.total }
  },
  perPage: 10
})

// Categories for filter & display
const allCategories = ref([])
const flatCategories = ref([])

async function fetchCategories() {
  try {
    const { data: res } = await categoryService.getAll({ per_page: 1000 })
    flatCategories.value = res.data.items
    allCategories.value = formatCategoryTree(res.data.items)
    syncCategoryFromRoute()
  } catch {}
}

function syncCategoryFromRoute() {
  if (route.query.category && flatCategories.value.length > 0) {
    const cat = flatCategories.value.find(c => c.slug === route.query.category)
    if (cat) {
      filters.category_id = cat.id
    } else {
      delete filters.category_id
    }
  } else {
    delete filters.category_id
  }
  fetchItems()
}

watch(() => route.query.category, () => {
  syncCategoryFromRoute()
})

function formatCategoryTree(items) {
  const itemMap = new Map()
  items.forEach(item => {
    itemMap.set(item.id, { ...item, children: [] })
  })

  const tree = []
  itemMap.forEach(item => {
    if (item.parent_id && itemMap.has(item.parent_id)) {
      itemMap.get(item.parent_id).children.push(item)
    } else {
      tree.push(item)
    }
  })

  const flat = []
  function traverse(nodes, depth = 0, prefix = '') {
    nodes.forEach((node, index) => {
      const isLast = index === nodes.length - 1;
      let branch = '';
      if (depth > 0) {
        branch = isLast ? '└─ ' : '├─ ';
      }
      
      flat.push({
        ...node,
        level: depth + 1,
        isLast,
        prefix,
        branch,
        displayName: prefix + branch + node.name
      })
      
      const nextPrefix = prefix + (depth > 0 ? (isLast ? '\u00A0\u00A0\u00A0\u00A0' : '│\u00A0\u00A0\u00A0') : '');
      traverse(node.children, depth + 1, nextPrefix)
    })
  }
  traverse(tree)
  return flat
}

const getCategoryName = (catId) => {
  const cat = allCategories.value.find(c => c.id === catId)
  if (!cat) return `ID: ${catId}`
  
  const path = [cat.name]
  let currentParentId = cat.parent_id
  let depth = 0
  
  while (currentParentId && depth < 10) {
    const parent = allCategories.value.find(c => c.id === currentParentId)
    if (parent) {
      path.unshift(parent.name)
      currentParentId = parent.parent_id
      depth++
    } else {
      break
    }
  }
  
  if (path.length > 3) {
    return `${path[0]} → ... → ${path[path.length - 2]} → ${path[path.length - 1]}`
  }
  
  return path.join(' → ')
}

const handleFilterStatus = (val) => {
  if (val) filters.status = val
  else delete filters.status
  pagination.page = 1
  fetchItems()
}

const handleFilterCategory = (catId) => {
  if (catId) filters.category_id = catId
  else delete filters.category_id
  pagination.page = 1
  fetchItems()
}

const handleFilterLevel = (level) => {
  if (level) filters.category_level = level
  else delete filters.category_level
  pagination.page = 1
  fetchItems()
}

const hasActiveFilters = computed(() => {
  return !!filters.status || !!filters.category_id || !!filters.category_level
})

const getSortIcon = (field) => {
  if (sort.field !== field) return ArrowUpDown
  return sort.direction === 'asc' ? ArrowUp : ArrowDown
}

function openCreate() {
  router.push('/posts/create')
}

function openEdit(post) {
  router.push(`/posts/${post.id}/edit`)
}

async function handleDelete(post) {
  const ok = await confirm.confirm({ title: 'Delete Post', message: `Are you sure you want to delete "${post.title}"?`, variant: 'destructive' })
  if (!ok) return
  try {
    await postService.delete(post.id)
    toast({ title: 'Post deleted', variant: 'success' })
    fetchItems()
  } catch {
    toast({ title: 'Failed to delete', variant: 'destructive' })
  }
}

onMounted(() => {
  fetchCategories()
})
</script>

<template>
  <div>
    <PageHeader title="Post Management" description="Manage articles and static pages" />

    <DataTableToolbar
      v-model:search-model-value="filters.search"
      search-placeholder="Search posts (title)..."
      :is-loading="isLoading"
      :show-add-button="auth.hasPermission('posts.create')"
      add-button-label="New Post"
      @refresh="fetchItems"
      @add="openCreate"
    >
      <template #actions-start>
        <!-- Filter Popover -->
        <Popover align="right" width="w-72">
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
            <PopoverHeader title="Filter Posts" @close="close" />
            <div class="space-y-5">
              <div>
                <Label class="text-[10px] uppercase tracking-wider text-muted-foreground mb-2.5 block font-bold">Status</Label>
                <div class="grid grid-cols-2 gap-2">
                  <button 
                    v-for="s in [{id:'', label:'ALL'}, {id:'PUBLISHED', label:'PUBLISHED'}, {id:'DRAFT', label:'DRAFT'}, {id:'ARCHIVED', label:'ARCHIVED'}]" 
                    :key="s.id"
                    @click="handleFilterStatus(s.id)"
                    class="px-2 py-2 rounded-lg text-[10px] font-bold border transition-all"
                    :class="[
                      (s.id === '' && !filters.status) || (filters.status === s.id) 
                      ? 'bg-primary text-white border-primary shadow-md' 
                      : 'bg-background text-muted-foreground border-border hover:bg-muted'
                    ]"
                  >
                    {{ s.label }}
                  </button>
                </div>
              </div>

              <div>
                <Label class="text-[10px] uppercase tracking-wider text-muted-foreground mb-2.5 block font-bold">Category</Label>
                <div class="space-y-1 max-h-48 overflow-y-auto custom-scrollbar font-mono">
                  <button 
                    @click="handleFilterCategory('')"
                    class="w-full text-left px-3 py-2.5 rounded-lg text-xs font-medium transition-colors flex items-center justify-between"
                    :class="!filters.category_id ? 'bg-accent text-primary shadow-sm' : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'"
                  >
                    All Categories
                    <div v-if="!filters.category_id" class="w-1.5 h-1.5 rounded-full bg-primary shadow-[0_0_8px_rgba(79,70,229,0.4)]"></div>
                  </button>
                  <button 
                    v-for="cat in allCategories"
                    :key="cat.id"
                    @click="handleFilterCategory(cat.id)"
                    class="w-full text-left px-3 py-2.5 rounded-lg text-xs transition-colors flex items-center justify-between"
                    :class="filters.category_id == cat.id ? 'bg-accent text-primary shadow-sm font-bold' : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground font-medium'"
                  >
                    <span>{{ cat.displayName }}</span>
                    <div v-if="filters.category_id == cat.id" class="w-1.5 h-1.5 rounded-full bg-primary shadow-[0_0_8px_rgba(79,70,229,0.4)]"></div>
                  </button>
                </div>
              </div>

              <div>
                <Label class="text-[10px] uppercase tracking-wider text-muted-foreground mb-2.5 block font-bold">Category Level</Label>
                <div class="grid grid-cols-4 gap-2">
                  <button 
                    v-for="l in [{id:'', label:'ALL'}, {id:1, label:'Lvl 1'}, {id:2, label:'Lvl 2'}, {id:3, label:'Lvl 3'}]" 
                    :key="l.id"
                    @click="handleFilterLevel(l.id)"
                    class="px-2 py-2 rounded-lg text-[10px] font-bold border transition-all"
                    :class="[
                      (l.id === '' && filters.category_level === undefined) || (filters.category_level === l.id) 
                      ? 'bg-primary text-white border-primary shadow-md' 
                      : 'bg-background text-muted-foreground border-border hover:bg-muted'
                    ]"
                  >
                    {{ l.label }}
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
                    v-for="f in [{id:'title', label:'Title'}, {id:'created_at', label:'Created At'}, {id:'updated_at', label:'Updated At'}]" 
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

      <div v-if="filters.status" class="flex items-center gap-1.5 px-3 py-1.5 bg-primary/10 text-primary border border-primary/20 rounded-full text-[11px] font-bold shadow-sm transition-all hover:bg-primary/20">
        <span class="opacity-70">Status:</span>
        <span>{{ filters.status }}</span>
        <button @click="handleFilterStatus('')" class="ml-1 hover:text-primary-foreground transition-colors"><X class="h-3.5 w-3.5" /></button>
      </div>

      <div v-if="filters.category_id" class="flex items-center gap-1.5 px-3 py-1.5 bg-primary/10 text-primary border border-primary/20 rounded-full text-[11px] font-bold shadow-sm transition-all hover:bg-primary/20">
        <span class="opacity-70">Category:</span>
        <span>{{ getCategoryName(filters.category_id) }}</span>
        <button @click="handleFilterCategory('')" class="ml-1 hover:text-primary-foreground transition-colors"><X class="h-3.5 w-3.5" /></button>
      </div>

      <div v-if="filters.category_level" class="flex items-center gap-1.5 px-3 py-1.5 bg-primary/10 text-primary border border-primary/20 rounded-full text-[11px] font-bold shadow-sm transition-all hover:bg-primary/20">
        <span class="opacity-70">Level:</span>
        <span>Level {{ filters.category_level }}</span>
        <button @click="handleFilterLevel('')" class="ml-1 hover:text-primary-foreground transition-colors"><X class="h-3.5 w-3.5" /></button>
      </div>

      <button @click="Object.keys(filters).forEach(k => { if(k !== 'search') delete filters[k] }); fetchItems()" class="text-[11px] text-muted-foreground hover:text-destructive font-bold px-2 py-1.5 rounded-lg hover:bg-destructive/5 transition-all ml-1">
        Clear All
      </button>
    </div>

    <div v-if="isLoading" class="space-y-3 mt-4">
      <SkeletonLoader v-for="i in 5" :key="i" class="h-14 w-full" />
    </div>

    <EmptyState 
      v-if="!isLoading && posts.length === 0" 
      :icon="FileText" 
      title="No posts found" 
      description="No articles have been published yet. Click New Post to get started."
    />

    <div v-else-if="!isLoading" class="rounded-md border border-border overflow-x-auto bg-card shadow-sm mt-4">
      <table class="w-full text-sm">
        <thead class="bg-muted/80 text-muted-foreground border-b border-border">
          <tr>
            <th class="px-6 py-4 font-bold text-left w-[35%]">Title</th>
            <th class="px-6 py-4 font-bold hidden md:table-cell text-left w-[20%]">Category</th>
            <th class="px-6 py-4 font-bold text-center w-[120px]">Status</th>
            <th class="px-6 py-4 font-bold hidden lg:table-cell text-left">Date</th>
            <th v-if="auth.hasPermission('posts.update') || auth.hasPermission('posts.delete')" class="px-6 py-4 font-bold text-center w-28">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="post in posts" :key="post.id" class="border-t hover:bg-muted/50 transition-colors">
            <td class="px-6 py-3 font-bold text-primary">{{ post.title }}</td>
            <td class="px-6 py-3 hidden md:table-cell text-muted-foreground text-left">
              <Badge v-if="post.category_id" variant="outline">{{ getCategoryName(post.category_id) }}</Badge>
              <span v-else class="text-xs text-muted-foreground">—</span>
            </td>
            <td class="px-6 py-3 text-center">
              <Badge :variant="post.status === 'PUBLISHED' ? 'success' : post.status === 'ARCHIVED' ? 'warning' : 'secondary'">{{ post.status }}</Badge>
            </td>
            <td class="px-6 py-3 hidden lg:table-cell text-xs text-muted-foreground text-left">
              {{ formatWIB(post.created_at) }}
            </td>
            <td v-if="auth.hasPermission('posts.update') || auth.hasPermission('posts.delete')" class="px-6 py-3 text-center border-l border-border/50 bg-muted/5">
              <div class="flex items-center justify-center gap-1">
                <button v-if="auth.hasPermission('posts.update')" @click="openEdit(post)" class="p-1.5 rounded-lg hover:bg-accent transition-colors border border-transparent hover:border-border"><Pencil class="h-4 w-4" /></button>
                <button v-if="auth.hasPermission('posts.delete')" @click="handleDelete(post)" class="p-1.5 rounded-lg hover:bg-accent text-destructive transition-colors border border-transparent hover:border-border"><Trash2 class="h-4 w-4" /></button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="mt-4 flex items-center justify-between">
      <p class="text-sm text-muted-foreground">Total: {{ pagination.total }}</p>
      <Pagination :current-page="pagination.page" :total-pages="pagination.totalPages" @page-change="goToPage" />
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
