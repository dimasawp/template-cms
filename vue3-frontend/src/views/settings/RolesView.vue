<script setup lang="ts">
import { ref } from 'vue'
import { useDataTable } from '@/composables/useDataTable'
import { useToast } from '@/composables/useToast'
import { useConfirmation } from '@/composables/useConfirmation'
import { roleService } from '@/services/roleService'
import PageHeader from '@/components/common/PageHeader.vue'
import Pagination from '@/components/common/Pagination.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Label from '@/components/ui/Label.vue'
import ConfirmationDialog from '@/components/ui/ConfirmationDialog.vue'
import SkeletonLoader from '@/components/ui/SkeletonLoader.vue'
import { Plus, Pencil, Trash2, Search, RotateCw } from 'lucide-vue-next'

const { toast } = useToast()
const confirm = useConfirmation()

const { items: roles, isLoading, pagination, fetchItems, goToPage, setSearch } = useDataTable<any>({
  fetchData: async (params) => {
    const { data: res } = await roleService.getAll(params)
    return { items: res.data.items, total: res.data.pagination.total }
  },
})

// All permissions for the matrix
const allPermissions = ref<any[]>([])
async function loadPermissions() {
  try {
    const { data: res } = await roleService.permissions()
    allPermissions.value = res.data
  } catch { /* ignore */ }
}
loadPermissions()

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

let searchTimeout: ReturnType<typeof setTimeout>
function onSearch(val: string) {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => setSearch(val), 400)
}
</script>

<template>
  <div>
    <PageHeader title="Role & Permission Management" description="Kelola role dan hak akses" />

    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-4">
      <div class="relative w-full sm:w-72">
        <Search class="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
        <Input placeholder="Cari role..." class="pl-9" @input="onSearch(($event.target as HTMLInputElement).value)" />
      </div>
      <div class="flex gap-2">
        <Button variant="outline" size="icon" @click="fetchItems"><RotateCw class="h-4 w-4" /></Button>
        <Button @click="openCreate"><Plus class="mr-1 h-4 w-4" /> Tambah Role</Button>
      </div>
    </div>

    <div v-if="isLoading" class="space-y-3">
      <SkeletonLoader v-for="i in 4" :key="i" class="h-14 w-full" />
    </div>

    <div v-else class="rounded-md border overflow-x-auto">
      <table class="w-full text-sm">
        <thead class="bg-muted/50">
          <tr>
            <th class="px-4 py-3 text-left font-medium">Nama Role</th>
            <th class="px-4 py-3 text-left font-medium hidden md:table-cell">Deskripsi</th>
            <th class="px-4 py-3 text-center font-medium">Permissions</th>
            <th class="px-4 py-3 text-center font-medium">Users</th>
            <th class="px-4 py-3 text-center font-medium w-24">Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in roles" :key="r.id" class="border-t hover:bg-muted/30 transition-colors">
            <td class="px-4 py-3 font-medium">{{ r.name }}</td>
            <td class="px-4 py-3 hidden md:table-cell text-muted-foreground">{{ r.description || '—' }}</td>
            <td class="px-4 py-3 text-center">{{ r.permissions?.length || 0 }}</td>
            <td class="px-4 py-3 text-center">{{ r.user_count || 0 }}</td>
            <td class="px-4 py-3 text-center">
              <div class="flex items-center justify-center gap-1">
                <button @click="openEdit(r)" class="p-1 rounded hover:bg-accent"><Pencil class="h-4 w-4" /></button>
                <button @click="handleDelete(r)" class="p-1 rounded hover:bg-accent text-destructive"><Trash2 class="h-4 w-4" /></button>
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
    <Teleport to="body">
      <Transition name="dialog">
        <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center">
          <div class="fixed inset-0 bg-black/50" @click="showModal = false" />
          <div class="relative z-10 w-full max-w-lg rounded-lg bg-background p-6 shadow-xl max-h-[90vh] overflow-y-auto">
            <h3 class="text-lg font-semibold">{{ isEditing ? 'Edit Role' : 'Tambah Role' }}</h3>
            <form @submit.prevent="handleSave" class="mt-4 space-y-3">
              <div><Label>Nama Role</Label><Input v-model="form.name" class="mt-1" /></div>
              <div><Label>Deskripsi</Label><Input v-model="form.description" class="mt-1" /></div>
              <div>
                <Label>Permissions</Label>
                <div class="mt-2 grid grid-cols-2 gap-2">
                  <label v-for="p in allPermissions" :key="p.id" class="flex items-center gap-2 text-sm cursor-pointer hover:bg-muted/50 p-1 rounded">
                    <input type="checkbox" :checked="form.permission_ids.includes(p.id)" @change="togglePermission(p.id)" class="rounded" />
                    <span>{{ p.name }}</span>
                  </label>
                </div>
              </div>
              <div class="flex justify-end gap-2 pt-2">
                <Button variant="outline" type="button" @click="showModal = false">Batal</Button>
                <Button type="submit" :loading="saving">{{ isEditing ? 'Simpan' : 'Buat' }}</Button>
              </div>
            </form>
          </div>
        </div>
      </Transition>
    </Teleport>

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
.dialog-enter-active { animation: fadeIn 0.2s ease; }
.dialog-leave-active { animation: fadeOut 0.15s ease; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes fadeOut { from { opacity: 1; } to { opacity: 0; } }
</style>
