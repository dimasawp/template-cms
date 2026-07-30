<script setup>
import { ref, computed, onMounted } from 'vue'
import { onClickOutside } from '@vueuse/core'
import { useDataTable } from '@/composables/useDataTable'
import { useToast } from '@/composables/useToast'
import { useConfirmation } from '@/composables/useConfirmation'
import { useAuthStore } from '@/stores/auth'
import { roleService } from '@/services/roleService'
import PageHeader from '@/components/common/PageHeader.vue'
import Pagination from '@/components/common/Pagination.vue'
import { formatWIB } from '@/helpers/dateHelper'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Label from '@/components/ui/Label.vue'
import ConfirmationDialog from '@/components/ui/ConfirmationDialog.vue'
import Dialog from '@/components/ui/Dialog.vue'
import Badge from '@/components/ui/Badge.vue'
import FormField from '@/components/ui/FormField.vue'
import PopoverHeader from '@/components/ui/PopoverHeader.vue'
import Popover from '@/components/ui/Popover.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import DataTableToolbar from '@/components/common/DataTableToolbar.vue'
import { Pencil, Trash2, ArrowUpDown, ArrowUp, ArrowDown, Filter, ChevronDown, ShieldAlert, Search } from 'lucide-vue-next'
import StatusIndicator from '@/components/ui/StatusIndicator.vue'

const { toast } = useToast()
const confirm = useConfirmation()
const auth = useAuthStore()

const { items: roles, isLoading, pagination, filters, sort, fetchItems, goToPage, setSortField, setSortDirection } = useDataTable({
  fetchData: async (params) => {
    const { data: res } = await roleService.getAll(params)
    return { items: res.data.items, total: res.data.pagination.total }
  },
  perPage: 10
})



const getSortIcon = (field) => {
  if (sort.field !== field) return ArrowUpDown
  return sort.direction === 'asc' ? ArrowUp : ArrowDown
}

// All permissions for the matrix
const allPermissions = ref([])
async function loadPermissions() {
  try {
    const { data: res } = await roleService.permissions()
    allPermissions.value = res.data
  } catch { /* ignore */ }
}

onMounted(() => {
  loadPermissions()
})


// ── Modal state ─────────────────────────────────────────────────────
const showModal = ref(false)
const isEditing = ref(false)
const saving = ref(false)
const form = ref({ name: '', description: '', is_active: true, permission_ids: [] })
const editId = ref(null)
const permissionSearch = ref('')

const groupedPermissions = computed(() => {
  const groups = {}
  allPermissions.value
    .filter(p => p.name.toLowerCase().includes(permissionSearch.value.toLowerCase()))
    .forEach(p => {
      const [groupName] = p.name.split('.')
      if (!groups[groupName]) groups[groupName] = []
      groups[groupName].push(p)
    })
  return groups
})

function openCreate() {
  isEditing.value = false
  editId.value = null
  form.value = { name: '', description: '', is_active: true, permission_ids: [] }
  showModal.value = true
}

function openEdit(role) {
  isEditing.value = true
  editId.value = role.id
  form.value = { 
    name: role.name, 
    description: role.description || '', 
    is_active: role.is_active,
    permission_ids: role.permissions.map(p => p.id) 
  }
  showModal.value = true
}

function togglePermission(id) {
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
  } catch (err) {
    toast({ title: 'Error', description: err.response?.data?.message || 'Failed', variant: 'destructive' })
  } finally {
    saving.value = false
  }
}

async function handleDelete(role) {
  const ok = await confirm.confirm({ title: 'Delete Role', message: `Are you sure you want to delete the role "${role.name}"?`, variant: 'destructive' })
  if (!ok) return
  try {
    await roleService.delete(role.id)
    toast({ title: 'Role deleted', variant: 'success' })
    fetchItems()
  } catch (err) {
    toast({ title: 'Error', description: err.response?.data?.message || 'Failed', variant: 'destructive' })
  }
}

const hasActiveFilters = computed(() => {
  return filters.is_active !== undefined
})

function handleFilterStatus(status) {
  if (status === 'active') filters.is_active = true
  else if (status === 'inactive') filters.is_active = false
  else delete filters.is_active
  pagination.page = 1
  fetchItems()
}

// Live Search and pagination handled by useDataTable watcher
</script>

<template>
  <div>
    <PageHeader title="Role & Permission Management" description="Manage roles and access rights" />

    <!-- Toolbar -->
    <DataTableToolbar
      v-model:search-model-value="filters.search"
      search-placeholder="Search roles..."
      :is-loading="isLoading"
      :show-add-button="auth.hasPermission('roles.create')"
      add-button-label="Add Role"
      @refresh="fetchItems"
      @add="openCreate"
    >
      <template #actions-start>
        <!-- Filter Popover -->
        <Popover align="right" width="w-64">
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
             <PopoverHeader title="Filter Roles" @close="close" />

            <div class="space-y-4">
              <div>
                <Label class="text-[10px] uppercase tracking-wider text-muted-foreground mb-2.5 block font-bold">Role Status</Label>
                <div class="grid grid-cols-3 gap-2">
                  <button 
                    v-for="s in [{id:'', label:'ALL'}, {id:'active', label:'ACTIVE'}, {id:'inactive', label:'INACTIVE'}]" 
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
                    v-for="f in [{id:'name', label:'Role Name'}, {id:'created_at', label:'Created At'}, {id:'updated_at', label:'Last Updated'}]" 
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

    <div v-if="isLoading" class="space-y-3">
      <SkeletonLoader v-for="i in 4" :key="i" class="h-14 w-full" />
    </div>

    <EmptyState 
      v-if="!isLoading && roles.length === 0" 
      :icon="ShieldAlert" 
      title="No Roles Found" 
      description="No role data found in the system. Please add a new role to start managing access."
    >
      <template #actions>
        <Button type="primary" @click="openCreate">Add New Role</Button>
      </template>
    </EmptyState>

    <div v-else class="rounded-md border border-border overflow-x-auto bg-card shadow-sm">
      <table class="w-full text-sm">
        <thead class="bg-muted/80 text-muted-foreground border-b border-border">
          <tr class="border-b border-border bg-muted/30">
            <th 
              class="px-6 py-4 font-bold text-muted-foreground cursor-pointer hover:bg-muted transition-colors group text-left w-[20%]"
              @click="setSortField('name')"
            >
              <div class="flex items-center gap-2">
                Role Name
                <component :is="getSortIcon('name')" class="w-3.5 h-3.5 text-muted-foreground group-hover:text-primary" />
              </div>
            </th>
            <th class="px-6 py-4 font-bold text-muted-foreground text-left w-[30%]">Description</th>
            <th class="px-6 py-4 font-bold text-muted-foreground text-left w-[120px]">Permissions</th>
            <th class="px-6 py-4 font-bold text-muted-foreground text-center w-[120px]">Status</th>
            <th 
              class="px-6 py-4 font-bold text-muted-foreground cursor-pointer hover:bg-muted transition-colors group text-left w-[180px]"
              @click="setSortField('created_at')"
            >
              <div class="flex items-center gap-2">
                Created At
                <component :is="getSortIcon('created_at')" class="w-3.5 h-3.5 text-muted-foreground group-hover:text-primary" />
              </div>
            </th>
            <th 
              class="px-6 py-4 font-bold text-muted-foreground cursor-pointer hover:bg-muted transition-colors group text-left w-[180px]"
              @click="setSortField('updated_at')"
            >
              <div class="flex items-center gap-2">
                Last Updated
                <component :is="getSortIcon('updated_at')" class="w-3.5 h-3.5 text-muted-foreground group-hover:text-primary" />
              </div>
            </th>
            <th v-if="auth.hasPermission('roles.update') || auth.hasPermission('roles.delete')" class="px-6 py-4 font-bold text-center w-28">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in roles" :key="r.id" class="border-t hover:bg-muted/50 transition-colors">
            <td class="px-6 py-3">
              <div class="flex flex-col">
                <span class="text-sm font-bold text-foreground">{{ r.name }}</span>
                <span class="text-[10px] text-muted-foreground">{{ r.user_count }} users assigned</span>
              </div>
            </td>
            <td class="px-6 py-3 text-xs text-muted-foreground">{{ r.description || '—' }}</td>
            <td class="px-6 py-3 text-left">
              <Badge variant="outline" class="font-bold border-primary/20 text-primary bg-primary/5">
                {{ r.permission_count || 0 }} features
              </Badge>
            </td>
            <td class="px-6 py-3 text-center">
              <StatusIndicator :active="r.is_active" />
            </td>
            <td class="px-6 py-3 text-xs text-muted-foreground whitespace-nowrap">
              {{ r.created_at ? formatWIB(r.created_at) : '—' }}
            </td>
            <td class="px-6 py-3 text-xs text-muted-foreground whitespace-nowrap">
              {{ r.updated_at ? formatWIB(r.updated_at) : '—' }}
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
      :title="isEditing ? 'Role & Permission Configuration' : 'Add New Role'" 
      max-width="max-w-5xl"
      @close="showModal = false"
    >
      <div class="grid grid-cols-1 md:grid-cols-2 gap-10 items-stretch">
        <!-- Left Column: Form -->
        <div class="flex flex-col space-y-8">
          <div class="space-y-6">
            <div class="flex flex-col gap-1.5">
              <Label class="text-[10px] font-black uppercase tracking-widest text-muted-foreground ml-1">Role Details</Label>
              <div class="p-6 bg-muted/20 rounded-2xl border border-border/50 space-y-6">
                <FormField label="Role Name" htmlFor="roleName" required>
                  <Input id="roleName" v-model="form.name" placeholder="e.g. Administrator" class="bg-background/50" />
                </FormField>
                
                <FormField label="Description" htmlFor="roleDesc">
                  <Input id="roleDesc" v-model="form.description" placeholder="Description of this role's responsibilities" class="bg-background/50" />
                </FormField>

                <div class="pt-4 border-t border-border/50">
                  <div class="flex items-center gap-3 p-3 bg-background/50 border border-border/30 rounded-xl cursor-pointer hover:bg-background transition-colors" @click="form.is_active = !form.is_active">
                    <input type="checkbox" v-model="form.is_active" id="role_active" class="rounded w-4 h-4 text-primary focus:ring-primary shadow-sm" @click.stop />
                    <div class="flex flex-col">
                      <Label for="role_active" class="cursor-pointer font-bold text-foreground text-[11px]">Active Role</Label>
                      <span class="text-[10px] text-muted-foreground">Allow this role to be used by users</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="flex flex-col gap-1.5">
              <div class="p-5 bg-primary/[0.03] rounded-2xl border border-primary/10 flex items-start gap-4">
                <div class="p-2 bg-primary/10 rounded-xl">
                  <ShieldAlert class="w-5 h-5 text-primary" />
                </div>
                <div class="space-y-1">
                  <h6 class="text-xs font-bold text-foreground">Principle of Least Privilege</h6>
                  <p class="text-[11px] text-muted-foreground leading-relaxed">
                    Grant access only to the features genuinely required by the user. This is crucial for maintaining system data integrity.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column: Permissions Grouped -->
        <div class="flex flex-col h-full">
          <div class="flex flex-col gap-4 mb-4">
            <div class="flex items-center justify-between">
              <Label class="text-[10px] font-black uppercase tracking-widest text-muted-foreground ml-1">Permissions</Label>
              <button 
                type="button" 
                @click="form.permission_ids = form.permission_ids.length === allPermissions.length ? [] : allPermissions.map(p => p.id)"
                class="text-[10px] font-black uppercase tracking-wider text-primary hover:text-primary/80 transition-colors"
              >
                {{ form.permission_ids.length === allPermissions.length ? 'Deselect All' : 'Select All' }}
              </button>
            </div>
            
            <div class="flex items-center gap-3">
              <div class="relative flex-1">
                <Input 
                  v-model="permissionSearch" 
                  placeholder="Search feature or module..." 
                  class="h-10 text-xs pr-10 bg-background/50"
                />
                <Search class="absolute right-3.5 top-3 h-4 w-4 text-muted-foreground" />
              </div>
              <div class="h-10 px-4 bg-muted/50 rounded-md border border-border/50 flex items-center shadow-sm">
                <span class="text-[10px] font-black text-primary whitespace-nowrap uppercase tracking-tighter">
                  {{ form.permission_ids.length }} Selected
                </span>
              </div>
            </div>
          </div>

          <div class="flex-1 bg-muted/20 rounded-2xl border border-border/50 p-5 overflow-y-auto max-h-[480px] custom-scrollbar space-y-8">
            <div v-for="(perms, group) in groupedPermissions" :key="group" class="space-y-4">
              <div class="flex items-center gap-3">
                <span class="text-[10px] font-black uppercase tracking-[0.2em] text-primary px-3 py-1 bg-primary/10 rounded-lg border border-primary/10">
                  {{ group }}
                </span>
                <div class="h-px flex-1 bg-gradient-to-r from-primary/20 to-transparent"></div>
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <label 
                  v-for="p in perms" 
                  :key="p.id" 
                  class="flex items-start gap-3 p-3.5 rounded-xl border border-border/30 hover:border-primary/30 hover:bg-primary/5 transition-all cursor-pointer group relative bg-background/40"
                  :class="form.permission_ids.includes(p.id) ? 'border-primary/40 bg-primary/5 ring-1 ring-primary/10' : ''"
                >
                  <input 
                    type="checkbox" 
                    :checked="form.permission_ids.includes(p.id)" 
                    @change="togglePermission(p.id)" 
                    class="rounded w-4 h-4 text-primary border-input focus:ring-primary shadow-sm mt-0.5" 
                  />
                  <div class="flex flex-col min-w-0">
                    <span class="text-[11px] font-bold truncate transition-colors" :class="form.permission_ids.includes(p.id) ? 'text-primary' : 'text-foreground'">{{ p.name }}</span>
                    <span v-if="p.description" class="text-[9px] text-muted-foreground line-clamp-1 group-hover:line-clamp-2 leading-tight mt-1">{{ p.description }}</span>
                  </div>
                </label>
              </div>
            </div>

            <div v-if="Object.keys(groupedPermissions).length === 0" class="h-full flex flex-col items-center justify-center py-16 text-center">
              <div class="p-4 bg-muted/50 rounded-full mb-4">
                <Search class="w-8 h-8 text-muted-foreground/20" />
              </div>
              <p class="text-xs text-muted-foreground font-medium">No results found for that search</p>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <Button variant="outline" type="button" @click="showModal = false">Cancel</Button>
        <Button type="primary" @click="handleSave" :loading="saving">
          {{ isEditing ? 'Save Changes' : 'Create Role' }}
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
