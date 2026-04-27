<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
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
  UserX
} from 'lucide-vue-next'



const { toast } = useToast()
const confirm = useConfirmation()
const auth = useAuthStore()

const { items: users, isLoading, pagination, filters, sort, fetchItems, goToPage, setSortField, setSortDirection } = useDataTable({
  fetchData: async (params) => {
    const { data: res } = await userService.getAll(params)
    return { items: res.data.items, total: res.data.pagination.total }
  },
  perPage: 10
})

const roles_list = ref([])
async function fetchRoles() {
  try {
    const { data: res } = await userService.getRoles()
    roles_list.value = res.data.items
  } catch {}
}

const handleFilterRole = (roleId) => {
  filters.role_id = roleId || undefined
}

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

onMounted(() => {
  fetchRoles()
})


// ── Modal state ─────────────────────────────────────────────────────
const showModal = ref(false)
const isEditing = ref(false)
const saving = ref(false)
const form = ref({ username: '', email: '', full_name: '', password: '', role_id: 1, is_active: true })
const editId = ref(null)
const selectedUser = ref(null)

const hasActiveFilters = computed(() => {
  return !!filters.role_id || filters.is_active !== undefined
})

function openCreate() {
  isEditing.value = false
  editId.value = null
  selectedUser.value = null
  form.value = { username: '', email: '', full_name: '', password: '', role_id: 1, is_active: true }
  showModal.value = true
}

function openEdit(user) {
  isEditing.value = true
  editId.value = user.id
  selectedUser.value = user
  form.value = { username: user.username, email: user.email || '', full_name: user.full_name || '', password: '', role_id: user.role_id, is_active: user.is_active }
  showModal.value = true
}

async function handleSave() {
  saving.value = true
  try {
    const payload = { ...form.value }
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
  } catch (err) {
    toast({ title: 'Error', description: err.response?.data?.message || 'Failed to save', variant: 'destructive' })
  } finally {
    saving.value = false
  }
}

async function handleDelete(user) {
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
            <PopoverHeader title="Filter User" @close="close" />

            <div class="space-y-5">
              <div>
                <Label class="text-[10px] uppercase tracking-wider text-muted-foreground mb-2.5 block font-bold">Berdasarkan Role</Label>
                <div class="max-h-48 overflow-y-auto pr-1 custom-scrollbar space-y-1">
                  <button 
                    @click="handleFilterRole('')"
                    class="w-full text-left px-3 py-2 rounded-lg text-xs font-medium transition-colors flex items-center justify-between"
                    :class="!filters.role_id ? 'bg-accent text-primary font-bold' : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'"
                  >
                    Semua Role
                    <div v-if="!filters.role_id" class="w-1.5 h-1.5 rounded-full bg-primary shadow-[0_0_8px_rgba(79,70,229,0.4)]"></div>
                  </button>

                  <button 
                    v-for="r in roles_list" 
                    :key="r.id"
                    @click="handleFilterRole(r.id)"
                    class="w-full text-left px-3 py-2 rounded-lg text-xs font-medium transition-colors flex items-center justify-between"
                    :class="filters.role_id === r.id ? 'bg-accent text-primary font-bold' : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'"
                  >
                    {{ r.name }}
                    <div v-if="filters.role_id === r.id" class="w-1.5 h-1.5 rounded-full bg-primary shadow-[0_0_8px_rgba(79,70,229,0.4)]"></div>
                  </button>
                </div>
              </div>

              <div>
                <Label class="text-[10px] uppercase tracking-wider text-muted-foreground mb-2.5 block font-bold">Status Akun</Label>
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

        <!-- Sort Popover -->
        <Popover align="right" width="w-56">
          <template #trigger="{ isOpen }">
            <Button 
              variant="outline" 
              size="sm" 
              class="h-10 px-3 flex items-center gap-2 border-input hover:bg-accent transition-colors shadow-sm text-foreground"
            >
              <ArrowUpDown class="h-4 w-4 text-muted-foreground" />
              <span>Urutkan</span>
              <ChevronDown class="h-3 w-3 transition-transform" :class="{'rotate-180': isOpen}" />
            </Button>
          </template>

          <template #default="{ close }">
            <PopoverHeader title="Urutkan Data" @close="close" />

            <div class="space-y-4">
              <div>
                <Label class="text-[10px] uppercase tracking-wider text-muted-foreground mb-2.5 block font-bold">Berdasarkan</Label>
                <div class="space-y-1">
                  <button 
                    v-for="f in [{id:'full_name', label:'Nama Lengkap'}, {id:'username', label:'Username'}, {id:'email', label:'Email'}, {id:'created_at', label:'Tgl Daftar'}]" 
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
          Filter Aktif
        </div>

        <div v-if="filters.role_id" class="flex items-center gap-1.5 px-3 py-1.5 bg-primary/10 text-primary border border-primary/20 rounded-full text-[11px] font-bold shadow-sm transition-all hover:bg-primary/20">
          <span class="opacity-70">Role:</span>
          <span>{{ roles_list.find(r => r.id == filters.role_id)?.name }}</span>
          <button @click="handleFilterRole('')" class="ml-1 hover:text-primary-foreground transition-colors"><X class="h-3.5 w-3.5" /></button>
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

    <!-- Loading skeleton -->
    <div v-if="isLoading" class="space-y-3">
      <SkeletonLoader v-for="i in 5" :key="i" class="h-14 w-full" />
    </div>

    <EmptyState 
      v-if="!isLoading && users.length === 0" 
      :icon="Search" 
      title="Tidak ada pengguna ditemukan" 
      description="Coba ubah kriteria pencarian atau filter Anda untuk menemukan pengguna yang dicari."
    >
      <template #actions>
        <Button variant="outline" size="sm" @click="Object.keys(filters).forEach(k => delete filters[k]); fetchItems()">
          Reset Semua Filter
        </Button>
      </template>
    </EmptyState>

    <!-- Table -->
    <div v-else class="rounded-md border border-border overflow-x-auto bg-card shadow-sm">
      <table class="w-full text-sm">
        <thead class="bg-muted/80 text-muted-foreground border-b border-border">
          <tr>
            <th 
              class="px-6 py-4 font-bold cursor-pointer hover:bg-muted transition-colors group text-left w-[15%]"
              @click="setSortField('username')"
            >
              <div class="flex items-center gap-2">
                Username
                <component :is="getSortIcon('username')" class="w-3.5 h-3.5 text-muted-foreground group-hover:text-primary" />
              </div>
            </th>
            <th 
              class="px-6 py-4 font-bold hidden md:table-cell cursor-pointer hover:bg-muted transition-colors group text-left w-[20%]"
              @click="setSortField('email')"
            >
              <div class="flex items-center gap-2">
                Email
                <component :is="getSortIcon('email')" class="w-3.5 h-3.5 text-muted-foreground group-hover:text-primary" />
              </div>
            </th>
            <th class="px-6 py-4 font-bold hidden lg:table-cell text-left w-[15%]">Full Name</th>
            <th class="px-6 py-4 font-bold text-muted-foreground text-left w-[120px]">Role</th>
            <th class="px-6 py-4 font-bold text-muted-foreground text-center w-[120px]">Status</th>
            <th 
              class="px-6 py-4 font-bold text-muted-foreground cursor-pointer hover:bg-muted transition-colors group text-left w-[180px]"
              @click="setSortField('created_at')"
            >
              <div class="flex items-center gap-2">
                Dibuat Pada
                <component :is="getSortIcon('created_at')" class="w-3.5 h-3.5 text-muted-foreground group-hover:text-primary" />
              </div>
            </th>
            <th 
              class="px-6 py-4 font-bold text-muted-foreground cursor-pointer hover:bg-muted transition-colors group text-left w-[180px]"
              @click="setSortField('updated_at')"
            >
              <div class="flex items-center gap-2">
                Update Terakhir
                <component :is="getSortIcon('updated_at')" class="w-3.5 h-3.5 text-muted-foreground group-hover:text-primary" />
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
              {{ u.created_at ? new Date(u.created_at + 'Z').toLocaleString('id-ID', { dateStyle: 'medium', timeStyle: 'short' }) : '—' }}
            </td>
            <td class="px-6 py-3 text-xs text-muted-foreground whitespace-nowrap text-left">
              {{ u.updated_at ? new Date(u.updated_at + 'Z').toLocaleString('id-ID', { dateStyle: 'medium', timeStyle: 'short' }) : '—' }}
            </td>
            <td v-if="auth.hasPermission('users.update') || auth.hasPermission('users.delete')" class="px-6 py-3 text-center border-l border-border/50 bg-muted/5">
              <div class="flex items-center justify-center gap-1">
                <button v-if="auth.hasPermission('users.update')" @click="openEdit(u)" class="p-1.5 rounded-lg hover:bg-accent transition-colors border border-transparent hover:border-border"><Pencil class="h-4 w-4" /></button>
                <button v-if="auth.hasPermission('users.delete')" @click="handleDelete(u)" class="p-1.5 rounded-lg hover:bg-accent text-destructive transition-colors border border-transparent hover:border-border"><Trash2 class="h-4 w-4" /></button>
              </div>
            </td>
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
      :title="isEditing ? 'Edit Profile Pengguna' : 'Tambah Pengguna Baru'" 
      :max-width="isEditing ? 'max-w-4xl' : 'max-w-lg'"
      @close="showModal = false"
    >
      <div :class="{'grid grid-cols-1 lg:grid-cols-12 gap-10': isEditing}">
        <!-- Left Column: Form -->
        <form @submit.prevent="handleSave" class="space-y-6" :class="{'lg:col-span-7': isEditing}">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
            <FormField label="Username" htmlFor="username">
              <Input id="username" v-model="form.username" placeholder="Contoh: johndoe" />
            </FormField>
            
            <FormField label="Nama Lengkap" htmlFor="fullname">
              <Input id="fullname" v-model="form.full_name" placeholder="Contoh: John Doe" />
            </FormField>
          </div>
          
          <FormField label="Alamat Email" htmlFor="email">
            <Input id="email" v-model="form.email" type="email" placeholder="john@example.com" />
          </FormField>

          <FormField 
            label="Kata Sandi" 
            htmlFor="password"
            :description="isEditing ? 'Biarkan kosong jika tidak ingin mengubah password' : ''"
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

          <div class="flex items-center gap-3 p-4 bg-muted/40 border border-border rounded-xl cursor-pointer hover:bg-muted/60 transition-colors" @click="form.is_active = !form.is_active">
            <input type="checkbox" v-model="form.is_active" id="is_active" class="rounded w-4 h-4 text-primary focus:ring-primary shadow-sm" @click.stop />
            <div class="flex flex-col">
              <Label for="is_active" class="cursor-pointer font-bold text-foreground">Status Akun Aktif</Label>
              <span class="text-[10px] text-muted-foreground">Izinkan pengguna ini masuk ke dalam sistem</span>
            </div>
          </div>
        </form>

        <!-- Right Column: User Info (Only on Edit) -->
        <div v-if="isEditing && selectedUser" class="lg:col-span-5 flex flex-col bg-muted/20 rounded-2xl border border-border/50 overflow-hidden min-h-[450px]">
          <div class="p-6 space-y-8 flex-1">
            <div class="flex items-center gap-4">
              <div class="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center text-primary font-black text-xl">
                {{ selectedUser.username.charAt(0).toUpperCase() }}
              </div>
              <div>
                <h4 class="font-bold text-foreground">{{ selectedUser.full_name || selectedUser.username }}</h4>
                <p class="text-xs text-muted-foreground">{{ selectedUser.email }}</p>
              </div>
            </div>

            <div class="space-y-6">
              <div class="space-y-2">
                <div class="flex items-center gap-2 text-[10px] uppercase font-black tracking-widest text-muted-foreground">
                  <div class="w-1.5 h-1.5 rounded-full bg-primary/50"></div>
                  Login Terakhir
                </div>
                <p class="text-sm font-bold text-foreground bg-background/50 p-3 rounded-xl border border-border/30">
                  {{ selectedUser.last_login_at ? new Date(selectedUser.last_login_at + 'Z').toLocaleString('id-ID', { dateStyle: 'long', timeStyle: 'short' }) : 'Belum pernah login' }}
                </p>
              </div>

              <div class="grid grid-cols-2 gap-4">
                <div class="space-y-1.5">
                  <Label class="text-[10px] uppercase text-muted-foreground font-black tracking-wider">Terdaftar</Label>
                  <p class="text-xs font-bold text-foreground">
                    {{ new Date(selectedUser.created_at + 'Z').toLocaleDateString('id-ID', { day: 'numeric', month: 'long', year: 'numeric' }) }}
                  </p>
                </div>
                <div class="space-y-1.5">
                  <Label class="text-[10px] uppercase text-muted-foreground font-black tracking-wider">Pembaruan</Label>
                  <p class="text-xs font-bold text-foreground">
                    {{ new Date(selectedUser.updated_at + 'Z').toLocaleDateString('id-ID', { day: 'numeric', month: 'long', year: 'numeric' }) }}
                  </p>
                </div>
              </div>

              <div class="pt-6 border-t border-border/50">
                <Label class="text-[10px] uppercase text-muted-foreground font-black tracking-wider mb-3 block">Keamanan & Identitas</Label>
                <div class="flex flex-wrap gap-2">
                  <Badge :variant="selectedUser.is_active ? 'success' : 'destructive'" class="px-2 py-0.5 text-[9px] font-black uppercase">
                    {{ selectedUser.is_active ? 'Verified' : 'Banned' }}
                  </Badge>
                  <Badge variant="outline" class="px-2 py-0.5 text-[9px] font-bold">UID: #{{ selectedUser.id }}</Badge>
                  <Badge variant="indigo" class="px-2 py-0.5 text-[9px] font-bold uppercase">{{ selectedUser.role_name }}</Badge>
                </div>
              </div>
            </div>
          </div>

          <div class="p-6 bg-primary/5 border-t border-primary/10">
            <p class="text-[10px] text-primary/80 font-medium leading-relaxed italic text-center">
              Perubahan status akun akan langsung berdampak pada hak akses sistem pengguna ini.
            </p>
          </div>
        </div>
      </div>

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
