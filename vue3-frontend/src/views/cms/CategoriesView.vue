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
  FolderTree
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

const handleFilterStatus = (status) => {
  if (status === 'active') filters.is_active = true
  else if (status === 'inactive') filters.is_active = false
  else delete filters.is_active
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
const form = ref({ name: '', slug: '', description: '', parent_id: '', is_active: true })
const editId = ref(null)

const hasActiveFilters = computed(() => {
  return filters.is_active !== undefined
})

function generateSlug() {
  if (!isEditing.value) {
    form.value.slug = form.value.name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)+/g, '')
  }
}

function openCreate() {
  isEditing.value = false
  editId.value = null
  form.value = { name: '', slug: '', description: '', parent_id: '', is_active: true }
  showModal.value = true
}

function openEdit(cat) {
  isEditing.value = true
  editId.value = cat.id
  form.value = { 
    name: cat.name, 
    slug: cat.slug, 
    description: cat.description || '', 
    parent_id: cat.parent_id || '', 
    is_active: cat.is_active 
  }
  showModal.value = true
}

async function handleSave() {
  saving.value = true
  try {
    const payload = { ...form.value }
    if (!payload.parent_id) payload.parent_id = null
    
    if (isEditing.value && editId.value) {
      await categoryService.update(editId.value, payload)
      toast({ title: 'Kategori diperbarui', variant: 'success' })
    } else {
      await categoryService.create(payload)
      toast({ title: 'Kategori dibuat', variant: 'success' })
    }
    showModal.value = false
    fetchItems()
  } catch (err) {
    toast({ title: 'Error', description: err.response?.data?.message || 'Gagal menyimpan', variant: 'destructive' })
  } finally {
    saving.value = false
  }
}

async function handleDelete(cat) {
  const ok = await confirm.confirm({ title: 'Hapus Kategori', message: `Yakin ingin menghapus "${cat.name}"?`, variant: 'destructive' })
  if (!ok) return
  try {
    await categoryService.delete(cat.id)
    toast({ title: 'Kategori dihapus', variant: 'success' })
    fetchItems()
  } catch {
    toast({ title: 'Gagal menghapus', variant: 'destructive' })
  }
}

</script>

<template>
  <div>
    <PageHeader title="Manajemen Kategori" description="Kelola kategori untuk konten dan postingan" />

    <DataTableToolbar
      v-model:search-model-value="filters.search"
      search-placeholder="Cari kategori (nama, slug)..."
      :is-loading="isLoading"
      :show-add-button="auth.hasPermission('categories.create')"
      add-button-label="Tambah Kategori"
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
            <PopoverHeader title="Filter Kategori" @close="close" />
            <div class="space-y-5">
              <div>
                <Label class="text-[10px] uppercase tracking-wider text-muted-foreground mb-2.5 block font-bold">Status Aktif</Label>
                <div class="grid grid-cols-3 gap-2">
                  <button 
                    v-for="s in [{id:'', label:'SEMUA'}, {id:'active', label:'AKTIF'}, {id:'inactive', label:'NONAKTIF'}]" 
                    :key="s.id"
                    @click="handleFilterStatus(s.id)"
                    class="px-2 py-2 rounded-lg text-[10px] font-bold border transition-all"
                    :class="[
                      (s.id === '' && filters.is_active === undefined) || (s.id === 'active' && filters.is_active === true) || (s.id === 'inactive' && filters.is_active === false) 
                      ? 'bg-primary text-white border-primary shadow-md' 
                      : 'bg-background text-muted-foreground border-border hover:bg-muted'
                    ]"
                  >
                    {{ s.label }}
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
        Filter Aktif
      </div>
      
      <div v-if="filters.is_active !== undefined" class="flex items-center gap-1.5 px-3 py-1.5 bg-primary/10 text-primary border border-primary/20 rounded-full text-[11px] font-bold shadow-sm transition-all hover:bg-primary/20">
        <span class="opacity-70">Status:</span>
        <span>{{ filters.is_active ? 'Active' : 'Inactive' }}</span>
        <button @click="handleFilterStatus('all')" class="ml-1 hover:text-primary-foreground transition-colors"><X class="h-3.5 w-3.5" /></button>
      </div>

      <button @click="Object.keys(filters).forEach(k => { if(k !== 'search') delete filters[k] }); fetchItems()" class="text-[11px] text-muted-foreground hover:text-destructive font-bold px-2 py-1.5 rounded-lg hover:bg-destructive/5 transition-all ml-1">
        Hapus Semua
      </button>
    </div>

    <div v-if="isLoading" class="space-y-3">
      <SkeletonLoader v-for="i in 5" :key="i" class="h-14 w-full" />
    </div>

    <EmptyState 
      v-if="!isLoading && categories.length === 0" 
      :icon="FolderTree" 
      title="Tidak ada kategori" 
      description="Belum ada kategori yang ditambahkan. Klik Tambah Kategori untuk memulai."
    >
      <template #actions>
        <Button variant="outline" size="sm" @click="Object.keys(filters).forEach(k => delete filters[k]); fetchItems()">
          Reset Filter
        </Button>
      </template>
    </EmptyState>

    <div v-else class="rounded-md border border-border overflow-x-auto bg-card shadow-sm">
      <table class="w-full text-sm">
        <thead class="bg-muted/80 text-muted-foreground border-b border-border">
          <tr>
            <th class="px-6 py-4 font-bold text-left w-[25%]">Nama Kategori</th>
            <th class="px-6 py-4 font-bold hidden md:table-cell text-left w-[25%]">Slug</th>
            <th class="px-6 py-4 font-bold hidden lg:table-cell text-left">Parent ID</th>
            <th class="px-6 py-4 font-bold text-center w-[120px]">Status</th>
            <th v-if="auth.hasPermission('categories.update') || auth.hasPermission('categories.delete')" class="px-6 py-4 font-bold text-center w-28">Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="cat in categories" :key="cat.id" class="border-t hover:bg-muted/50 transition-colors">
            <td class="px-6 py-3 font-bold text-primary">{{ cat.name }}</td>
            <td class="px-6 py-3 hidden md:table-cell text-muted-foreground text-left">{{ cat.slug }}</td>
            <td class="px-6 py-3 hidden lg:table-cell font-semibold text-foreground text-left">
              <Badge v-if="cat.parent_id" variant="outline">ID: {{ cat.parent_id }}</Badge>
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

    <Dialog 
      :open="showModal" 
      :title="isEditing ? 'Edit Kategori' : 'Tambah Kategori'" 
      max-width="max-w-lg"
      @close="showModal = false"
    >
      <form @submit.prevent="handleSave" class="space-y-6">
        <FormField label="Nama Kategori" htmlFor="name">
          <Input id="name" v-model="form.name" placeholder="Contoh: Berita Utama" @input="generateSlug" required />
        </FormField>
        
        <FormField label="URL Slug" htmlFor="slug">
          <Input id="slug" v-model="form.slug" placeholder="contoh-berita-utama" required />
        </FormField>

        <FormField label="Deskripsi" htmlFor="desc">
          <textarea 
            id="desc" 
            v-model="form.description" 
            class="w-full flex min-h-[80px] rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus:ring-2 focus:ring-primary focus:border-primary disabled:cursor-not-allowed disabled:opacity-50 transition-all shadow-sm"
            placeholder="Deskripsi singkat kategori"
          ></textarea>
        </FormField>

        <FormField label="Parent Kategori (ID)" htmlFor="parent">
          <Input id="parent" type="number" v-model="form.parent_id" placeholder="Kosongkan jika ini kategori utama" />
        </FormField>

        <div class="flex items-center gap-3 p-4 bg-muted/40 border border-border rounded-xl cursor-pointer hover:bg-muted/60 transition-colors" @click="form.is_active = !form.is_active">
          <input type="checkbox" v-model="form.is_active" id="is_active" class="rounded w-4 h-4 text-primary focus:ring-primary shadow-sm" @click.stop />
          <div class="flex flex-col">
            <Label for="is_active" class="cursor-pointer font-bold text-foreground">Status Aktif</Label>
            <span class="text-[10px] text-muted-foreground">Tampilkan kategori ini di menu publik</span>
          </div>
        </div>
      </form>
      <template #footer>
        <Button variant="outline" type="button" @click="showModal = false">Batal</Button>
        <Button type="primary" @click="handleSave" :loading="saving">Simpan Kategori</Button>
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
