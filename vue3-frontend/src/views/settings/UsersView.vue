<script setup lang="ts">
import { ref } from 'vue'
import { useDataTable } from '@/composables/useDataTable'
import { useToast } from '@/composables/useToast'
import { useConfirmation } from '@/composables/useConfirmation'
import { userService } from '@/services/userService'
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

const { items: users, isLoading, pagination, search, fetchItems, goToPage, setSearch } = useDataTable<any>({
  fetchData: async (params) => {
    const { data: res } = await userService.getAll(params)
    return { items: res.data.items, total: res.data.pagination.total }
  },
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

let searchTimeout: ReturnType<typeof setTimeout>
function onSearch(val: string) {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => setSearch(val), 400)
}
</script>

<template>
  <div>
    <PageHeader title="User Management" description="Kelola pengguna sistem" />

    <!-- Toolbar -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-4">
      <div class="relative w-full sm:w-72">
        <Search class="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
        <Input placeholder="Cari user..." class="pl-9" @input="onSearch(($event.target as HTMLInputElement).value)" />
      </div>
      <div class="flex gap-2">
        <Button variant="outline" size="icon" @click="fetchItems"><RotateCw class="h-4 w-4" /></Button>
        <Button @click="openCreate"><Plus class="mr-1 h-4 w-4" /> Tambah User</Button>
      </div>
    </div>

    <!-- Loading skeleton -->
    <div v-if="isLoading" class="space-y-3">
      <SkeletonLoader v-for="i in 5" :key="i" class="h-14 w-full" />
    </div>

    <!-- Table -->
    <div v-else class="rounded-md border overflow-x-auto">
      <table class="w-full text-sm">
        <thead class="bg-muted/50">
          <tr>
            <th class="px-4 py-3 text-left font-medium">Username</th>
            <th class="px-4 py-3 text-left font-medium hidden md:table-cell">Email</th>
            <th class="px-4 py-3 text-left font-medium hidden lg:table-cell">Full Name</th>
            <th class="px-4 py-3 text-left font-medium">Role</th>
            <th class="px-4 py-3 text-center font-medium">Status</th>
            <th class="px-4 py-3 text-center font-medium w-24">Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in users" :key="u.id" class="border-t hover:bg-muted/30 transition-colors">
            <td class="px-4 py-3 font-medium">{{ u.username }}</td>
            <td class="px-4 py-3 hidden md:table-cell text-muted-foreground">{{ u.email || '—' }}</td>
            <td class="px-4 py-3 hidden lg:table-cell">{{ u.full_name || '—' }}</td>
            <td class="px-4 py-3">
              <span class="px-2 py-0.5 rounded-full text-xs font-medium bg-primary/10 text-primary">{{ u.role_name }}</span>
            </td>
            <td class="px-4 py-3 text-center">
              <span :class="u.is_active ? 'text-green-600' : 'text-red-500'" class="text-xs font-medium">{{ u.is_active ? 'Active' : 'Inactive' }}</span>
            </td>
            <td class="px-4 py-3 text-center">
              <div class="flex items-center justify-center gap-1">
                <button @click="openEdit(u)" class="p-1 rounded hover:bg-accent"><Pencil class="h-4 w-4" /></button>
                <button @click="handleDelete(u)" class="p-1 rounded hover:bg-accent text-destructive"><Trash2 class="h-4 w-4" /></button>
              </div>
            </td>
          </tr>
          <tr v-if="users.length === 0">
            <td colspan="6" class="px-4 py-8 text-center text-muted-foreground">Tidak ada data</td>
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
    <Teleport to="body">
      <Transition name="dialog">
        <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center">
          <div class="fixed inset-0 bg-black/50" @click="showModal = false" />
          <div class="relative z-10 w-full max-w-md rounded-lg bg-background p-6 shadow-xl">
            <h3 class="text-lg font-semibold">{{ isEditing ? 'Edit User' : 'Tambah User' }}</h3>
            <form @submit.prevent="handleSave" class="mt-4 space-y-3">
              <div><Label>Username</Label><Input v-model="form.username" class="mt-1" /></div>
              <div><Label>Email</Label><Input v-model="form.email" type="email" class="mt-1" /></div>
              <div><Label>Full Name</Label><Input v-model="form.full_name" class="mt-1" /></div>
              <div><Label>Password {{ isEditing ? '(kosongkan jika tidak diubah)' : '' }}</Label><Input v-model="form.password" type="password" class="mt-1" /></div>
              <div class="flex items-center gap-2">
                <input type="checkbox" v-model="form.is_active" id="is_active" class="rounded" />
                <Label for="is_active">Active</Label>
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
