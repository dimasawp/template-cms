<script setup>
import { ref, computed, onMounted } from 'vue'
import { useDataTable } from '@/composables/useDataTable'
import { useToast } from '@/composables/useToast'
import { useConfirmation } from '@/composables/useConfirmation'
import { useAuthStore } from '@/stores/auth'
import { categoryService } from '@/services/categoryService'
import PageHeader from '@/components/common/PageHeader.vue'
import Pagination from '@/components/common/Pagination.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Label from '@/components/ui/Label.vue'
import FormField from '@/components/ui/FormField.vue'
import ConfirmationDialog from '@/components/ui/ConfirmationDialog.vue'
import Dialog from '@/components/ui/Dialog.vue'
import SkeletonLoader from '@/components/ui/SkeletonLoader.vue'
import Badge from '@/components/ui/Badge.vue'
import StatusIndicator from '@/components/ui/StatusIndicator.vue'
import PopoverHeader from '@/components/ui/PopoverHeader.vue'
import Popover from '@/components/ui/Popover.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import DataTableToolbar from '@/components/common/DataTableToolbar.vue'
import CategoryTreeItem from './CategoryTreeItem.vue'
import { 
  Pencil, 
  Trash2, 
  ArrowUpDown, 
  ArrowUp, 
  ArrowDown,
  Filter,
  ChevronDown,
  X,
  Search,
  FolderTree,
  List,
  GitBranchPlus
} from 'lucide-vue-next'

const { toast } = useToast()
const confirm = useConfirmation()
const auth = useAuthStore()

const { items: categories, isLoading, pagination, filters, sort, fetchItems, goToPage, setSortField, setSortDirection } = useDataTable({
  fetchData: async (params) => {
    const { data: res } = await categoryService.getAll(params)
    return { items: res.data.items, total: res.data.pagination.total }
  },
  perPage: 10
})

const handleFilterStatus = (val) => {
  filters.is_active = val === '' ? null : (val === 'active')
  pagination.page = 1
  fetchItems()
}

const handleFilterLevel = (val) => {
  filters.level = val === '' ? null : parseInt(val)
  pagination.page = 1
  fetchItems()
}

const getSortIcon = (field) => {
  if (sort.field !== field) return ArrowUpDown
  return sort.direction === 'asc' ? ArrowUp : ArrowDown
}

// ── Modal state ─────────────────────────────────────────────────────
const showModal = ref(false)
const isEditing = ref(false)
const saving = ref(false)
const form = ref({ name: '', slug: '', description: '', parent_id: '', is_active: true, is_menu: false })
const editId = ref(null)

const allCategories = ref([])
const categoryTree = ref([])
const isFetchingAll = ref(false)
const showTree = ref(true)

const hasActiveFilters = computed(() => {
  return filters.is_active !== undefined && filters.is_active !== null || filters.level !== undefined && filters.level !== null
})

function generateSlug() {
  if (!isEditing.value) {
    form.value.slug = form.value.name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)+/g, '')
  }
}

async function fetchAllCategories() {
  isFetchingAll.value = true
  try {
    const { data: res } = await categoryService.getAll({ per_page: 1000 })
    const formatted = formatCategoryTree(res.data.items)
    allCategories.value = formatted.flat
    categoryTree.value = formatted.tree
  } catch (err) {
    console.error("Failed to fetch all categories", err)
  } finally {
    isFetchingAll.value = false
  }
}

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

  // Sort children by order_index
  const sortTree = (nodes) => {
    nodes.sort((a, b) => a.order_index - b.order_index)
    nodes.forEach(n => {
      if (n.children.length > 0) sortTree(n.children)
    })
  }
  sortTree(tree)

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
        level: depth,
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
  return { flat, tree }
}

function isInvalidParent(targetCatId, currentCatId) {
  if (targetCatId === currentCatId) return true
  let currentTarget = allCategories.value.find(c => c.id === targetCatId)
  while (currentTarget && currentTarget.parent_id) {
    if (currentTarget.parent_id === currentCatId) return true
    currentTarget = allCategories.value.find(c => c.id === currentTarget.parent_id)
  }
  return false
}

function openCreate() {
  isEditing.value = false
  editId.value = null
  form.value = { name: '', slug: '', description: '', parent_id: '', is_active: true, is_menu: false }
  showModal.value = true
  fetchAllCategories()
}

function openEdit(cat) {
  isEditing.value = true
  editId.value = cat.id
  form.value = { 
    name: cat.name, 
    slug: cat.slug, 
    description: cat.description || '', 
    parent_id: cat.parent_id || '', 
    is_active: cat.is_active,
    is_menu: cat.is_menu
  }
  showModal.value = true
  fetchAllCategories()
}

async function handleSave() {
  saving.value = true
  try {
    const payload = { ...form.value }
    if (!payload.parent_id) payload.parent_id = null
    
    if (isEditing.value && editId.value) {
      await categoryService.update(editId.value, payload)
      toast({ title: 'Category updated', variant: 'success' })
    } else {
      await categoryService.create(payload)
      toast({ title: 'Category created', variant: 'success' })
    }
    showModal.value = false
    fetchItems()
    fetchAllCategories()
  } catch (err) {
    toast({ title: 'Error', description: err.response?.data?.message || 'Failed to save', variant: 'destructive' })
  } finally {
    saving.value = false
  }
}

async function handleDelete(cat) {
  const ok = await confirm.confirm({ title: 'Delete Category', message: `Are you sure you want to delete "${cat.name}"?`, variant: 'destructive' })
  if (!ok) return
  try {
    await categoryService.delete(cat.id)
    toast({ title: 'Category deleted', variant: 'success' })
    fetchItems()
    fetchAllCategories()
  } catch {
    toast({ title: 'Failed to delete', variant: 'destructive' })
  }
}

async function handleTreeChange() {
  const items = []
  
  // Find the root sortable container
  const rootContainer = document.querySelector('.sortable-root > .sortable-container')
  if (!rootContainer) {
    console.error("Root sortable container not found")
    return
  }
  
  function traverseDOM(container, parentId = null) {
    const children = container.querySelectorAll(':scope > .tree-item-wrapper')
    children.forEach((child, index) => {
      const id = child.getAttribute('data-id')
      if (id) {
        items.push({
          id: parseInt(id),
          parent_id: parentId,
          order_index: index
        })
      }
      const childrenContainer = child.querySelector(':scope > .tree-children-container > .sortable-container')
      if (childrenContainer) {
        traverseDOM(childrenContainer, parseInt(id))
      }
    })
  }
  
  traverseDOM(rootContainer)
  
  try {
    await categoryService.reorder({ items })
    toast({ title: 'Order saved', variant: 'success' })
    fetchAllCategories() // Refresh to ensure Vue state matches saved DOM state
  } catch (err) {
    toast({ title: 'Failed to reorder', variant: 'destructive' })
    fetchAllCategories() // revert
  }
}

onMounted(() => {
  fetchAllCategories()
})

</script>

<template>
  <div>
    <PageHeader title="Category Management" description="Manage categories for content and posts" />

    <DataTableToolbar
      v-model:search-model-value="filters.search"
      search-placeholder="Search categories (name, slug)..."
      :is-loading="isLoading"
      :show-add-button="auth.hasPermission('categories.create')"
      add-button-label="Add Category"
      @refresh="() => { fetchItems(); fetchAllCategories() }"
      @add="openCreate"
    >
      <template #actions-start>
        <!-- Tree / Flat Toggle (Segmented Control) -->
        <div class="flex items-center p-1 bg-muted/50 border border-border rounded-lg h-10">
          <button 
            @click="showTree = true"
            class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-md transition-all"
            :class="showTree ? 'bg-background text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'"
          >
            <GitBranchPlus class="h-3.5 w-3.5" />
            Tree
          </button>
          <button 
            @click="showTree = false"
            class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-md transition-all"
            :class="!showTree ? 'bg-background text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'"
          >
            <List class="h-3.5 w-3.5" />
            List
          </button>
        </div>

        <!-- Filter Popover -->
        <Popover align="right" width="w-72" v-if="!showTree">
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
            <PopoverHeader title="Filter Categories" @close="close" />
            <div class="space-y-5">
              <div>
                <Label class="text-[10px] uppercase tracking-wider text-muted-foreground mb-2.5 block font-bold">Active Status</Label>
                <div class="grid grid-cols-3 gap-2">
                  <button 
                    v-for="s in [{id:'', label:'ALL'}, {id:'active', label:'ACTIVE'}, {id:'inactive', label:'INACTIVE'}]" 
                    :key="s.id"
                    @click="handleFilterStatus(s.id)"
                    class="px-2 py-2 rounded-lg text-[10px] font-bold border transition-all"
                    :class="[
                      (s.id === '' && filters.is_active === null) || (s.id === 'active' && filters.is_active === true) || (s.id === 'inactive' && filters.is_active === false) 
                      ? 'bg-primary text-white border-primary shadow-md' 
                      : 'bg-background text-muted-foreground border-border hover:bg-muted'
                    ]"
                  >
                    {{ s.label }}
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
                      (l.id === '' && filters.level === null) || (filters.level === l.id) 
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
        <Popover align="right" width="w-56" v-if="!showTree">
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
                    v-for="f in [{id:'name', label:'Name'}, {id:'slug', label:'Slug'}, {id:'created_at', label:'Created At'}]" 
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
      
      <div v-if="filters.is_active !== undefined && filters.is_active !== null" class="flex items-center gap-1.5 px-3 py-1.5 bg-primary/10 text-primary border border-primary/20 rounded-full text-[11px] font-bold shadow-sm transition-all hover:bg-primary/20">
        <span class="opacity-70">Status:</span>
        <span>{{ filters.is_active ? 'Active' : 'Inactive' }}</span>
        <button @click="handleFilterStatus('')" class="ml-1 hover:text-primary-foreground transition-colors"><X class="h-3.5 w-3.5" /></button>
      </div>

      <div v-if="filters.level !== undefined && filters.level !== null" class="flex items-center gap-1.5 px-3 py-1.5 bg-primary/10 text-primary border border-primary/20 rounded-full text-[11px] font-bold shadow-sm transition-all hover:bg-primary/20">
        <span class="opacity-70">Level:</span>
        <span>Lvl {{ filters.level }}</span>
        <button @click="handleFilterLevel('')" class="ml-1 hover:text-primary-foreground transition-colors"><X class="h-3.5 w-3.5" /></button>
      </div>

      <button @click="Object.keys(filters).forEach(k => { if(k !== 'search') delete filters[k] }); fetchItems()" class="text-[11px] text-muted-foreground hover:text-destructive font-bold px-2 py-1.5 rounded-lg hover:bg-destructive/5 transition-all ml-1">
        Clear All
      </button>
    </div>

    <div v-if="isLoading" class="space-y-3">
      <SkeletonLoader v-for="i in 5" :key="i" class="h-14 w-full" />
    </div>

    <EmptyState 
      v-if="!isLoading && categories.length === 0 && allCategories.length === 0" 
      :icon="FolderTree" 
      title="No categories found" 
      description="No categories have been added yet. Click Add Category to get started."
    >
      <template #actions>
        <Button variant="outline" size="sm" @click="Object.keys(filters).forEach(k => delete filters[k]); fetchItems()">
          Reset Filters
        </Button>
      </template>
    </EmptyState>

    <!-- TREE VIEW -->
    <div v-if="showTree" class="rounded-md border border-border bg-card shadow-sm overflow-hidden">
      <div class="bg-muted/80 text-muted-foreground border-b border-border flex items-center justify-between p-3 px-6 text-sm font-bold">
        <div>Category Structure</div>
        <div class="text-xs font-normal opacity-70">Drag handles to reorder</div>
      </div>
      <div class="sortable-root">
        <CategoryTreeItem 
          v-if="categoryTree && categoryTree.length > 0"
          :categories="categoryTree" 
          @change="handleTreeChange"
          @edit="openEdit"
          @delete="handleDelete"
        />
      </div>
    </div>

    <!-- FLAT VIEW -->
    <div v-if="!showTree">
      <div v-if="!isLoading && categories.length > 0" class="rounded-md border border-border overflow-x-auto bg-card shadow-sm">
        <table class="w-full text-sm">
          <thead class="bg-muted/80 text-muted-foreground border-b border-border">
            <tr>
              <th class="px-6 py-4 font-bold text-left w-[25%]">Category Name</th>
              <th class="px-6 py-4 font-bold hidden md:table-cell text-left w-[25%]">Slug</th>
              <th class="px-6 py-4 font-bold hidden lg:table-cell text-left">Parent</th>
              <th class="px-6 py-4 font-bold text-center w-[120px]">Status</th>
              <th v-if="auth.hasPermission('categories.update') || auth.hasPermission('categories.delete')" class="px-6 py-4 font-bold text-center w-28">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="cat in categories" :key="cat.id" class="border-t hover:bg-muted/50 transition-colors">
              <td class="px-6 py-3 font-bold text-primary">{{ cat.name }}</td>
              <td class="px-6 py-3 hidden md:table-cell text-muted-foreground text-left">{{ cat.slug }}</td>
              <td class="px-6 py-3 hidden lg:table-cell font-semibold text-foreground text-left">
                <Badge v-if="cat.parent_id" variant="outline">
                  {{ allCategories.find(c => c.id === cat.parent_id)?.name || `ID: ${cat.parent_id}` }}
                </Badge>
                <span v-else class="text-xs text-muted-foreground">—</span>
              </td>
              <td class="px-6 py-3 text-center">
                <StatusIndicator :active="cat.is_active" />
              </td>
              <td v-if="auth.hasPermission('categories.update') || auth.hasPermission('categories.delete')" class="px-6 py-3 text-center border-l border-border/50 bg-muted/5">
                <div class="flex items-center justify-center gap-1">
                  <button v-if="auth.hasPermission('categories.update')" @click="openEdit(cat)" class="p-1.5 rounded-lg hover:bg-accent transition-colors border border-transparent hover:border-border"><Pencil class="h-4 w-4" /></button>
                  <button v-if="auth.hasPermission('categories.delete')" @click="handleDelete(cat)" class="p-1.5 rounded-lg hover:bg-accent text-destructive transition-colors border border-transparent hover:border-border"><Trash2 class="h-4 w-4" /></button>
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
    </div>

    <Dialog 
      :open="showModal" 
      :title="isEditing ? 'Edit Category' : 'Add Category'" 
      max-width="max-w-lg"
      @close="showModal = false"
    >
      <form @submit.prevent="handleSave" class="space-y-6">
        <FormField label="Category Name" htmlFor="name">
          <Input id="name" v-model="form.name" placeholder="e.g. Featured News" @input="generateSlug" required />
        </FormField>
        
        <FormField label="URL Slug" htmlFor="slug">
          <Input id="slug" v-model="form.slug" placeholder="featured-news" required />
        </FormField>

        <FormField label="Description" htmlFor="desc">
          <textarea 
            id="desc" 
            v-model="form.description" 
            class="w-full flex min-h-[80px] rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus:ring-2 focus:ring-primary focus:border-primary disabled:cursor-not-allowed disabled:opacity-50 transition-all shadow-sm"
            placeholder="Short description of the category"
          ></textarea>
        </FormField>

        <FormField label="Parent Category" htmlFor="parent">
          <div class="relative">
            <select 
              id="parent" 
              v-model="form.parent_id" 
              class="w-full flex h-10 items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 appearance-none shadow-sm"
              :disabled="isFetchingAll"
            >
              <option value="">— Leave empty if this is a root category —</option>
              <option 
                v-for="cat in allCategories" 
                :key="cat.id" 
                :value="cat.id"
                :disabled="!cat.is_active || (isEditing && isInvalidParent(cat.id, editId))"
              >
                {{ cat.displayName }} {{ !cat.is_active ? '(Inactive)' : '' }}
              </option>
            </select>
            <ChevronDown class="absolute right-3 top-3 h-4 w-4 opacity-50 pointer-events-none" />
          </div>
        </FormField>

        <div class="grid grid-cols-2 gap-4">
          <div class="flex items-center gap-3 p-4 bg-muted/40 border border-border rounded-xl cursor-pointer hover:bg-muted/60 transition-colors" @click="form.is_active = !form.is_active">
            <input type="checkbox" v-model="form.is_active" id="is_active" class="rounded w-4 h-4 text-primary focus:ring-primary shadow-sm" @click.stop />
            <div class="flex flex-col">
              <Label for="is_active" class="cursor-pointer font-bold text-foreground">Active Status</Label>
              <span class="text-[10px] text-muted-foreground">Show in public API</span>
            </div>
          </div>
          
          <div class="flex items-center gap-3 p-4 bg-muted/40 border border-border rounded-xl cursor-pointer hover:bg-muted/60 transition-colors" @click="form.is_menu = !form.is_menu">
            <input type="checkbox" v-model="form.is_menu" id="is_menu" class="rounded w-4 h-4 text-primary focus:ring-primary shadow-sm" @click.stop />
            <div class="flex flex-col">
              <Label for="is_menu" class="cursor-pointer font-bold text-foreground">Set as Menu</Label>
              <span class="text-[10px] text-muted-foreground">Show in CMS sidebar</span>
            </div>
          </div>
        </div>
      </form>
      <template #footer>
        <Button variant="outline" type="button" @click="showModal = false">Cancel</Button>
        <Button type="primary" @click="handleSave" :loading="saving">Save Category</Button>
      </template>
    </Dialog>

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
