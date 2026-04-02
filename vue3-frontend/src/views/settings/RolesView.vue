<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { onClickOutside } from '@vueuse/core'
import { useDataTable } from '@/composables/useDataTable'
import { useToast } from '@/composables/useToast'
import { useConfirmation } from '@/composables/useConfirmation'
import { useAuthStore } from '@/stores/auth'
import { roleService } from '@/services/roleService'
import PageHeader from '@/components/common/PageHeader.vue'
import Pagination from '@/components/common/Pagination.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Label from '@/components/ui/Label.vue'
import ConfirmationDialog from '@/components/ui/ConfirmationDialog.vue'
import Dialog from '@/components/ui/Dialog.vue'
import Badge from '@/components/ui/Badge.vue'
import FormField from '@/components/ui/FormField.vue'
import PopoverHeader from '@/components/ui/PopoverHeader.vue'
import DataTableToolbar from '@/components/common/DataTableToolbar.vue'
import { Pencil, Trash2, ArrowUpDown, ArrowUp, ArrowDown, Filter, ChevronDown } from 'lucide-vue-next'

const { toast } = useToast()
const confirm = useConfirmation()
const auth = useAuthStore()

const { items: roles, isLoading, pagination, filters, sort, fetchItems, goToPage, setSortField, setSortDirection } = useDataTable<any>({
  fetchData: async (params) => {
    const { data: res } = await roleService.getAll(params)
    return { items: res.data.items, total: res.data.pagination.total }
  },
  perPage: 10
})

const showFilters = ref(false)
const showSort = ref(false)

const getSortIcon = (field: string) => {
  if (sort.field !== field) return ArrowUpDown
  return sort.direction === 'asc' ? ArrowUp : ArrowDown
}

// All permissions for the matrix
const allPermissions = ref<any[]>([])
async function loadPermissions() {
  try {
    const { data: res } = await roleService.permissions()
    allPermissions.value = res.data
  } catch { /* ignore */ }
}

// ── Interaction Logic ────────────────────────────────────────────────
const filterRef = ref(null)
const sortRef = ref(null)

onClickOutside(filterRef, () => { showFilters.value = false })
onClickOutside(sortRef, () => { showSort.value = false })

onMounted(() => {
  loadPermissions()
})

// ── Modal state ─────────────────────────────────────────────────────
const showModal = ref(false)
const isEditing = ref(false)
const saving = ref(false)
const form = ref({ name: '', description: '', permission_ids: [] as number[] })
const editId = ref<number | null>(null)

function openCreate() {
  isEditing.value = false
  editId.value = null
  form.value = { name: '', description: '', permission_ids: [] }
  showModal.value = true
}

function openEdit(role: any) {
  isEditing.value = true
  editId.value = role.id
  form.value = { name: role.name, description: role.description || '', permission_ids: role.permissions.map((p: any) => p.id) }
  showModal.value = true
}

function togglePermission(id: number) {
  const idx = form.value.permission_ids.indexOf(id)
  if (idx >= 0) form.value.permission_ids.splice(idx, 1)
  else form.value.permission_ids.push(id)
}

async function handleSave() {
  saving.value = true
  try {
    if (isEditing.value && editId.value) {
      await roleService.update(editId.value, form.value)
      toast({ title: 'Role updated', variant: 'success' })
    } else {
      await roleService.create(form.value)
      toast({ title: 'Role created', variant: 'success' })
    }
    showModal.value = false
    fetchItems()
  } catch (err: any) {
    toast({ title: 'Error', description: err.response?.data?.message || 'Failed', variant: 'destructive' })
  } finally {
    saving.value = false
  }
}

async function handleDelete(role: any) {
  const ok = await confirm.confirm({ title: 'Hapus Role', message: `Yakin ingin menghapus role "${role.name}"?`, variant: 'destructive' })
  if (!ok) return
  try {
    await roleService.delete(role.id)
    toast({ title: 'Role deleted', variant: 'success' })
    fetchItems()
  } catch (err: any) {
    toast({ title: 'Gagal', description: err.response?.data?.message || 'Failed', variant: 'destructive' })
  }
}

// Live Search and pagination handled by useDataTable watcher
</script>

<template>
  <div>
    <PageHeader title="Role & Permission Management" description="Kelola role dan hak akses" />

    <!-- Toolbar -->
    <DataTableToolbar
      v-model:search-model-value="filters.search"
      search-placeholder="Cari role..."
      :is-loading="isLoading"
      :show-add-button="auth.hasPermission('roles.create')"
      add-button-label="Tambah Role"
      @refresh="fetchItems"
      @add="openCreate"
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
          <div v-if="showFilters" ref="filterRef" class="absolute right-0 top-full mt-2 w-64 bg-popover rounded-xl shadow-xl border border-border p-4 z-50">
            <PopoverHeader title="Filter Role" @close="showFilters = false" />

            <div class="space-y-4">
              <div class="py-4 text-center text-muted-foreground text-xs italic bg-muted/30 rounded-lg border border-dashed border-border">
                Belum ada filter spesifik untuk role.
              </div>
              <div class="pt-2">
                <Button variant="outline" size="sm" class="w-full h-9 text-[11px] font-bold border-input text-foreground shadow-sm hover:bg-accent" @click="showFilters = false">
                  Tutup
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
                    v-for="f in [{id:'name', label:'Nama Role'}, {id:'created_at', label:'Tanggal Dibuat'}]" 
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

    <div v-if="isLoading" class="space-y-3">
      <SkeletonLoader v-for="i in 4" :key="i" class="h-14 w-full" />
    </div>

    <div v-else class="rounded-md border border-border overflow-x-auto bg-card shadow-sm">
      <table class="w-full text-sm">
        <thead class="bg-muted/80 text-muted-foreground border-b border-border">
          <tr>
            <th 
              class="px-6 py-4 font-bold text-foreground cursor-pointer hover:bg-muted/50 transition-colors group text-left"
              @click="setSortField('name')"
            >
              <div class="flex items-center gap-2">
                Nama Role
                <component 
                  :is="getSortIcon('name')" 
                  class="w-3.5 h-3.5 transition-colors" 
                  :class="sort.field === 'name' ? 'text-primary' : 'text-muted-foreground/40 group-hover:text-muted-foreground'" 
                />
              </div>
            </th>
            <th class="px-6 py-4 font-bold text-foreground hidden md:table-cell text-left">Deskripsi</th>
            <th class="px-6 py-4 font-bold text-foreground text-center font-bold">Permissions</th>
            <th class="px-6 py-4 font-bold text-foreground text-center">Users</th>
            <th 
              class="px-6 py-4 font-bold text-foreground text-center cursor-pointer hover:bg-muted/50 transition-colors group"
              @click="setSortField('created_at')"
            >
              <div class="flex items-center justify-center gap-2">
                Dibuat Pada
                <component 
                  :is="getSortIcon('created_at')" 
                  class="w-3.5 h-3.5 transition-colors text-center" 
                  :class="sort.field === 'created_at' ? 'text-primary' : 'text-muted-foreground/40 group-hover:text-muted-foreground'" 
                />
              </div>
            </th>
            <th v-if="auth.hasPermission('roles.update') || auth.hasPermission('roles.delete')" class="px-6 py-4 font-bold text-foreground text-center w-28">Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in roles" :key="r.id" class="border-t hover:bg-muted/50 transition-colors">
            <td class="px-6 py-3 font-bold text-primary text-left">{{ r.name }}</td>
            <td class="px-6 py-3 hidden md:table-cell text-muted-foreground text-left">{{ r.description || '—' }}</td>
            <td class="px-6 py-3 text-center">
              <Badge variant="indigo" size="sm">{{ r.permissions?.length || 0 }} Perms</Badge>
            </td>
            <td class="px-6 py-3 text-center">
              <Badge variant="secondary" size="sm">{{ r.user_count || 0 }} Users</Badge>
            </td>
            <td class="px-6 py-3 text-center text-xs text-muted-foreground whitespace-nowrap">
              {{ new Date(r.created_at + 'Z').toLocaleDateString('id-ID') }}
            </td>
            <td v-if="auth.hasPermission('roles.update') || auth.hasPermission('roles.delete')" class="px-6 py-3 text-center border-l border-border/50 bg-muted/5">
              <div class="flex items-center justify-center gap-1">
                <button v-if="auth.hasPermission('roles.update')" @click="openEdit(r)" class="p-1.5 rounded-lg hover:bg-accent transition-colors border border-transparent hover:border-border"><Pencil class="h-4 w-4" /></button>
                <button v-if="auth.hasPermission('roles.delete')" @click="handleDelete(r)" class="p-1.5 rounded-lg hover:bg-accent text-destructive transition-colors border border-transparent hover:border-border"><Trash2 class="h-4 w-4" /></button>
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

    <!-- Modal -->
    <Dialog 
      :open="showModal" 
      :title="isEditing ? 'Edit Role' : 'Tambah Role'" 
      max-width="max-w-lg"
      @close="showModal = false"
    >
      <form @submit.prevent="handleSave" class="space-y-4">
        <FormField label="Nama Role" htmlFor="roleName" required>
          <Input id="roleName" v-model="form.name" placeholder="Misal: Manager" />
        </FormField>
        
        <FormField label="Deskripsi" htmlFor="roleDesc">
          <Input id="roleDesc" v-model="form.description" placeholder="Deskripsi singkat role ini" />
        </FormField>
        
        <div class="pt-4 pb-2 border-t border-border">
          <Label class="text-[10px] font-bold uppercase tracking-widest text-muted-foreground mb-4 block">Hak Akses (Permissions)</Label>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 bg-muted/40 p-4 rounded-xl border border-border max-h-72 overflow-y-auto custom-scrollbar">
            <label 
              v-for="p in allPermissions" 
              :key="p.id" 
              class="flex items-center gap-3 p-3 rounded-lg border border-transparent hover:border-border hover:bg-background hover:shadow-sm transition-all cursor-pointer group"
              :class="form.permission_ids.includes(p.id) ? 'bg-background border-border shadow-sm' : ''"
            >
              <input 
                type="checkbox" 
                :checked="form.permission_ids.includes(p.id)" 
                @change="togglePermission(p.id)" 
                class="rounded w-4 h-4 text-primary border-input focus:ring-primary shadow-sm" 
              />
              <div class="flex flex-col">
                <span class="text-xs font-bold transition-colors" :class="form.permission_ids.includes(p.id) ? 'text-primary' : 'text-foreground'">{{ p.name }}</span>
                <span v-if="p.description" class="text-[9px] text-muted-foreground">{{ p.description }}</span>
              </div>
            </label>
          </div>
          <p class="mt-3 text-[10px] text-muted-foreground italic text-center">Centang untuk memberikan hak akses spesifik pada role ini.</p>
        </div>
      </form>

      <template #footer>
        <Button variant="outline" type="button" @click="showModal = false">Batal</Button>
        <Button type="primary" @click="handleSave" :loading="saving">
          {{ isEditing ? 'Simpan Perubahan' : 'Buat Role Baru' }}
        </Button>
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

<style scoped>
/* Transition logic moved to Dialog.vue */
</style>
