<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { onClickOutside } from '@vueuse/core'
import { useDataTable } from '@/composables/useDataTable'
import { useToast } from '@/composables/useToast'
import { useConfirmation } from '@/composables/useConfirmation'
import { useAuthStore } from '@/stores/auth'
import { userService } from '@/services/userService'
import PageHeader from '@/components/common/PageHeader.vue'
import Pagination from '@/components/common/Pagination.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Label from '@/components/ui/Label.vue'
import ConfirmationDialog from '@/components/ui/ConfirmationDialog.vue'
import Dialog from '@/components/ui/Dialog.vue'
import SkeletonLoader from '@/components/ui/SkeletonLoader.vue'
import Badge from '@/components/ui/Badge.vue'
import StatusIndicator from '@/components/ui/StatusIndicator.vue'
import FormField from '@/components/ui/FormField.vue'
import PopoverHeader from '@/components/ui/PopoverHeader.vue'
import DataTableToolbar from '@/components/common/DataTableToolbar.vue'
import { 
  Pencil, 
  Trash2, 
  ArrowUpDown, 
  ArrowUp, 
  ArrowDown,
  Filter,
  ChevronDown,
  X
} from 'lucide-vue-next'

const showFilters = ref(false)
const showSort = ref(false)

const { toast } = useToast()
const confirm = useConfirmation()
const auth = useAuthStore()

const { items: users, isLoading, pagination, filters, sort, fetchItems, goToPage, setSortField, setSortDirection } = useDataTable<any>({
  fetchData: async (params) => {
    const { data: res } = await userService.getAll(params)
    return { items: res.data.items, total: res.data.pagination.total }
  },
  perPage: 10
})

const roles_list = ref<any[]>([])
async function fetchRoles() {
  try {
    const { data: res } = await userService.getRoles()
    roles_list.value = res.data.items
  } catch {}
}

const handleFilterRole = (roleId: string) => {
  filters.role_id = roleId || undefined
}

const handleFilterStatus = (status: string) => {
  if (status === 'active') filters.is_active = true
  else if (status === 'inactive') filters.is_active = false
  else delete filters.is_active
  pagination.page = 1
  fetchItems()
}

const getSortIcon = (field: string) => {
  if (sort.field !== field) return ArrowUpDown
  return sort.direction === 'asc' ? ArrowUp : ArrowDown
}

// ── Interaction Logic ────────────────────────────────────────────────
const filterRef = ref(null)
const sortRef = ref(null)

onClickOutside(filterRef, () => { showFilters.value = false })
onClickOutside(sortRef, () => { showSort.value = false })

const handleEsc = (e: KeyboardEvent) => {
  if (e.key === 'Escape') {
    showFilters.value = false
    showSort.value = false
  }
}

onMounted(() => {
  fetchRoles()
  window.addEventListener('keydown', handleEsc)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleEsc)
})

// ── Modal state ─────────────────────────────────────────────────────
const showModal = ref(false)
const isEditing = ref(false)
const saving = ref(false)
const form = ref({ username: '', email: '', full_name: '', password: '', role_id: 1, is_active: true })
const editId = ref<number | null>(null)

function openCreate() {
  isEditing.value = false
  editId.value = null
  form.value = { username: '', email: '', full_name: '', password: '', role_id: 1, is_active: true }
  showModal.value = true
}

function openEdit(user: any) {
  isEditing.value = true
  editId.value = user.id
  form.value = { username: user.username, email: user.email || '', full_name: user.full_name || '', password: '', role_id: user.role_id, is_active: user.is_active }
  showModal.value = true
}

async function handleSave() {
  saving.value = true
  try {
    const payload: any = { ...form.value }
    if (!payload.password) delete payload.password
    if (isEditing.value && editId.value) {
      await userService.update(editId.value, payload)
      toast({ title: 'User updated', variant: 'success' })
    } else {
      await userService.create(payload)
      toast({ title: 'User created', variant: 'success' })
    }
    showModal.value = false
    fetchItems()
  } catch (err: any) {
    toast({ title: 'Error', description: err.response?.data?.message || 'Failed to save', variant: 'destructive' })
  } finally {
    saving.value = false
  }
}

async function handleDelete(user: any) {
  const ok = await confirm.confirm({ title: 'Hapus User', message: `Yakin ingin menghapus "${user.username}"?`, variant: 'destructive' })
  if (!ok) return
  try {
    await userService.delete(user.id)
    toast({ title: 'User deleted', variant: 'success' })
    fetchItems()
  } catch {
    toast({ title: 'Failed to delete', variant: 'destructive' })
  }
}

</script>

<template>
  <div>
    <PageHeader title="User Management" description="Kelola pengguna sistem" />

    <!-- Toolbar -->
    <DataTableToolbar
      v-model:search-model-value="filters.search"
      search-placeholder="Cari user (nama, email, username)..."
      :is-loading="isLoading"
      :show-add-button="auth.hasPermission('users.create')"
      add-button-label="Tambah User"
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
          <div v-if="showFilters" ref="filterRef" class="absolute right-0 top-full mt-2 w-72 bg-popover rounded-xl shadow-xl border border-border p-4 z-50">
            <PopoverHeader title="Filter User" @close="showFilters = false" />

            <div class="space-y-5">
              <div>
                <Label class="text-[10px] uppercase tracking-wider text-muted-foreground mb-2.5 block font-bold">Role Akses</Label>
                <div class="max-h-48 overflow-y-auto pr-1 custom-scrollbar space-y-1">
                  <button 
                    @click="handleFilterRole('')"
                    class="w-full text-left px-3 py-2 rounded-lg text-xs font-medium transition-colors flex items-center justify-between"
                    :class="!filters.role_id ? 'bg-accent text-primary' : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'"
                  >
                    Semua Role
                    <div v-if="!filters.role_id" class="w-1.5 h-1.5 rounded-full bg-primary shadow-[0_0_8px_rgba(79,70,229,0.4)]"></div>
                  </button>
                  <button 
                    v-for="r in roles_list" 
                    :key="r.id"
                    @click="handleFilterRole(String(r.id))"
                    class="w-full text-left px-3 py-2 rounded-lg text-xs font-medium transition-colors flex items-center justify-between"
                    :class="filters.role_id == String(r.id) ? 'bg-accent text-primary' : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'"
                  >
                    {{ r.name }}
                    <div v-if="filters.role_id == String(r.id)" class="w-1.5 h-1.5 rounded-full bg-primary shadow-[0_0_8px_rgba(79,70,229,0.4)]"></div>
                  </button>
                </div>
              </div>

              <div>
                <Label class="text-[10px] uppercase tracking-wider text-muted-foreground mb-2.5 block font-bold">Status Akun</Label>
                <div class="grid grid-cols-3 gap-2">
                  <button 
                    v-for="s in ['all', 'active', 'inactive']" 
                    :key="s"
                    @click="handleFilterStatus(s)"
                    class="px-2 py-2 rounded-lg text-[11px] font-semibold border capitalize transition-all"
                    :class="[
                      (s === 'all' && filters.is_active === undefined) || 
                      (s === 'active' && filters.is_active === true) || 
                      (s === 'inactive' && filters.is_active === false)
                      ? 'bg-accent border-primary/20 text-primary shadow-sm'
                      : 'bg-background border-border text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                    ]"
                  >
                    {{ s }}
                  </button>
                </div>
              </div>

              <div class="pt-2">
                <Button variant="outline" size="sm" class="w-full h-9 text-[11px] font-bold border-input hover:bg-accent hover:text-accent-foreground text-muted-foreground" @click="Object.keys(filters).forEach(k => delete filters[k]); fetchItems(); showFilters = false">
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
                    v-for="f in [{id:'username', label:'Username'}, {id:'full_name', label:'Nama Lengkap'}, {id:'created_at', label:'Tanggal Dibuat'}]" 
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
        
        <div v-if="filters.role_id" class="flex items-center gap-1.5 px-2 py-1 bg-primary/10 text-primary border border-primary/20 rounded-full text-[11px] font-bold">
          <span>Role: {{ roles_list.find(r => r.id == filters.role_id)?.name }}</span>
          <button @click="handleFilterRole('')" class="hover:text-primary-foreground"><X class="h-3 w-3" /></button>
        </div>
        
        <div v-if="filters.is_active !== undefined" class="flex items-center gap-1.5 px-2 py-1 bg-primary/10 text-primary border border-primary/20 rounded-full text-[11px] font-bold">
          <span>Status: {{ filters.is_active ? 'Active' : 'Inactive' }}</span>
          <button @click="handleFilterStatus('all')" class="hover:text-primary-foreground"><X class="h-3 w-3" /></button>
        </div>

        <button @click="Object.keys(filters).forEach(k => delete filters[k]); fetchItems()" class="text-[11px] text-muted-foreground hover:text-destructive font-bold ml-2 border-b border-transparent hover:border-destructive/30 transition-all">
          Hapus Semua
        </button>
      </div>

    <!-- Loading skeleton -->
    <div v-if="isLoading" class="space-y-3">
      <SkeletonLoader v-for="i in 5" :key="i" class="h-14 w-full" />
    </div>

    <!-- Table -->
    <div v-else class="rounded-md border border-border overflow-x-auto bg-card shadow-sm">
      <table class="w-full text-sm">
        <thead class="bg-muted/80 text-muted-foreground border-b border-border">
          <tr>
            <th 
              class="px-6 py-4 font-bold cursor-pointer hover:bg-muted transition-colors group text-left"
              @click="setSortField('username')"
            >
              <div class="flex items-center gap-2">
                Username
                <component :is="getSortIcon('username')" class="w-3.5 h-3.5 text-muted-foreground group-hover:text-primary" />
              </div>
            </th>
            <th 
              class="px-6 py-4 font-bold hidden md:table-cell cursor-pointer hover:bg-muted transition-colors group text-left"
              @click="setSortField('email')"
            >
              <div class="flex items-center gap-2">
                Email
                <component :is="getSortIcon('email')" class="w-3.5 h-3.5 text-muted-foreground group-hover:text-primary" />
              </div>
            </th>
            <th class="px-6 py-4 font-bold hidden lg:table-cell text-left">Full Name</th>
            <th class="px-6 py-4 font-bold text-left">Role</th>
            <th class="px-6 py-4 font-bold text-center">Status</th>
            <th 
              class="px-6 py-4 font-bold cursor-pointer hover:bg-muted transition-colors group text-left"
              @click="setSortField('created_at')"
            >
              <div class="flex items-center gap-2">
                Dibuat Pada
                <component :is="getSortIcon('created_at')" class="w-3.5 h-3.5 text-muted-foreground group-hover:text-primary" />
              </div>
            </th>
            <th v-if="auth.hasPermission('users.update') || auth.hasPermission('users.delete')" class="px-6 py-4 font-bold text-center w-28">Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in users" :key="u.id" class="border-t hover:bg-muted/50 transition-colors">
            <td class="px-6 py-3 font-bold text-primary">{{ u.username }}</td>
            <td class="px-6 py-3 hidden md:table-cell text-muted-foreground text-left">{{ u.email || '—' }}</td>
            <td class="px-6 py-3 hidden lg:table-cell font-semibold text-foreground text-left">{{ u.full_name || '—' }}</td>
            <td class="px-6 py-3 text-left">
              <Badge variant="indigo">{{ u.role_name }}</Badge>
            </td>
            <td class="px-6 py-3 text-center">
              <StatusIndicator :active="u.is_active" />
            </td>
            <td class="px-6 py-3 text-xs text-muted-foreground whitespace-nowrap text-left">
              {{ u.last_login_at ? new Date(u.last_login_at + 'Z').toLocaleString('id-ID') : 'Belum pernah' }}
            </td>
            <td v-if="auth.hasPermission('users.update') || auth.hasPermission('users.delete')" class="px-6 py-3 text-center border-l border-border/50 bg-muted/5">
              <div class="flex items-center justify-center gap-1">
                <button v-if="auth.hasPermission('users.update')" @click="openEdit(u)" class="p-1.5 rounded-lg hover:bg-accent transition-colors border border-transparent hover:border-border"><Pencil class="h-4 w-4" /></button>
                <button v-if="auth.hasPermission('users.delete')" @click="handleDelete(u)" class="p-1.5 rounded-lg hover:bg-accent text-destructive transition-colors border border-transparent hover:border-border"><Trash2 class="h-4 w-4" /></button>
              </div>
            </td>
          </tr>
          <tr v-if="users.length === 0">
            <td :colspan="auth.hasPermission('users.update') || auth.hasPermission('users.delete') ? 7 : 6" class="px-4 py-8 text-center text-muted-foreground">Tidak ada data</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div class="mt-4 flex items-center justify-between">
      <p class="text-sm text-muted-foreground">Total: {{ pagination.total }}</p>
      <Pagination :current-page="pagination.page" :total-pages="pagination.totalPages" @page-change="goToPage" />
    </div>

    <!-- Create/Edit Modal -->
    <Dialog 
      :open="showModal" 
      :title="isEditing ? 'Edit User' : 'Tambah User'" 
      @close="showModal = false"
    >
      <form @submit.prevent="handleSave" class="space-y-4">
        <div class="grid gap-4 sm:grid-cols-2">
          <FormField label="Username" htmlFor="username">
            <Input id="username" v-model="form.username" placeholder="johndoe" />
          </FormField>
          
          <FormField label="Full Name" htmlFor="fullname">
            <Input id="fullname" v-model="form.full_name" placeholder="John Doe" />
          </FormField>
        </div>
        
        <FormField label="Email" htmlFor="email">
          <Input id="email" v-model="form.email" type="email" placeholder="john@example.com" />
        </FormField>

        <FormField 
          :label="`Password ${isEditing ? '(kosongkan jika tidak diubah)' : ''}`" 
          htmlFor="password"
        >
          <Input id="password" v-model="form.password" type="password" placeholder="••••••••" />
        </FormField>

        <FormField label="Role Akses" htmlFor="role">
          <select 
            id="role" 
            v-model="form.role_id"
            class="w-full flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 disabled:cursor-not-allowed disabled:opacity-50 transition-all shadow-sm"
          >
            <option v-for="r in roles_list" :key="r.id" :value="r.id">{{ r.name }}</option>
          </select>
        </FormField>

        <div class="flex items-center gap-3 p-3 bg-muted/40 border border-border rounded-lg cursor-pointer hover:bg-muted/60 transition-colors" @click="form.is_active = !form.is_active">
          <input type="checkbox" v-model="form.is_active" id="is_active" class="rounded w-4 h-4 text-primary focus:ring-primary shadow-sm" @click.stop />
          <div class="flex flex-col">
            <Label for="is_active" class="cursor-pointer font-bold text-foreground">Status Akun Aktif</Label>
            <span class="text-[10px] text-muted-foreground">Izinkan pengguna ini masuk ke dalam sistem</span>
          </div>
        </div>
      </form>

      <template #footer>
        <Button variant="outline" type="button" @click="showModal = false">Batal</Button>
        <Button type="primary" @click="handleSave" :loading="saving">
          {{ isEditing ? 'Simpan Perubahan' : 'Buat User Baru' }}
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
