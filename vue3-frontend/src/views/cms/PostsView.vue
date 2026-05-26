<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useDataTable } from '@/composables/useDataTable'
import { useToast } from '@/composables/useToast'
import { useConfirmation } from '@/composables/useConfirmation'
import { useAuthStore } from '@/stores/auth'
import { postService } from '@/services/postService'
import PageHeader from '@/components/common/PageHeader.vue'
import Pagination from '@/components/common/Pagination.vue'
import Button from '@/components/ui/Button.vue'
import ConfirmationDialog from '@/components/ui/ConfirmationDialog.vue'
import SkeletonLoader from '@/components/ui/SkeletonLoader.vue'
import Badge from '@/components/ui/Badge.vue'
import StatusIndicator from '@/components/ui/StatusIndicator.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import DataTableToolbar from '@/components/common/DataTableToolbar.vue'
import { Pencil, Trash2, ArrowUpDown, ArrowUp, ArrowDown, FileText } from 'lucide-vue-next'

const { toast } = useToast()
const confirm = useConfirmation()
const auth = useAuthStore()
const router = useRouter()

const { items: posts, isLoading, pagination, filters, sort, fetchItems, goToPage, setSortField, setSortDirection } = useDataTable({
  fetchData: async (params) => {
    const { data: res } = await postService.getAll(params)
    return { items: res.data.items, total: res.data.pagination.total }
  },
  perPage: 10
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
  const ok = await confirm.confirm({ title: 'Hapus Postingan', message: `Yakin ingin menghapus "${post.title}"?`, variant: 'destructive' })
  if (!ok) return
  try {
    await postService.delete(post.id)
    toast({ title: 'Postingan dihapus', variant: 'success' })
    fetchItems()
  } catch {
    toast({ title: 'Gagal menghapus', variant: 'destructive' })
  }
}
</script>

<template>
  <div>
    <PageHeader title="Manajemen Postingan" description="Kelola artikel dan halaman statis" />

    <DataTableToolbar
      v-model:search-model-value="filters.search"
      search-placeholder="Cari postingan (judul)..."
      :is-loading="isLoading"
      :show-add-button="auth.hasPermission('posts.create')"
      add-button-label="Tulis Post Baru"
      @refresh="fetchItems"
      @add="openCreate"
    />

    <div v-if="isLoading" class="space-y-3 mt-4">
      <SkeletonLoader v-for="i in 5" :key="i" class="h-14 w-full" />
    </div>

    <EmptyState 
      v-if="!isLoading && posts.length === 0" 
      :icon="FileText" 
      title="Tidak ada postingan" 
      description="Belum ada artikel yang dipublikasikan. Klik Tulis Post Baru untuk mulai."
    />

    <div v-else-if="!isLoading" class="rounded-md border border-border overflow-x-auto bg-card shadow-sm mt-4">
      <table class="w-full text-sm">
        <thead class="bg-muted/80 text-muted-foreground border-b border-border">
          <tr>
            <th class="px-6 py-4 font-bold text-left w-[35%]">Judul Artikel</th>
            <th class="px-6 py-4 font-bold hidden md:table-cell text-left w-[20%]">Kategori ID</th>
            <th class="px-6 py-4 font-bold text-center w-[120px]">Status</th>
            <th class="px-6 py-4 font-bold hidden lg:table-cell text-left">Tanggal</th>
            <th v-if="auth.hasPermission('posts.update') || auth.hasPermission('posts.delete')" class="px-6 py-4 font-bold text-center w-28">Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="post in posts" :key="post.id" class="border-t hover:bg-muted/50 transition-colors">
            <td class="px-6 py-3 font-bold text-primary">{{ post.title }}</td>
            <td class="px-6 py-3 hidden md:table-cell text-muted-foreground text-left">
              <Badge v-if="post.category_id" variant="outline">{{ post.category_id }}</Badge>
              <span v-else class="text-xs text-muted-foreground">—</span>
            </td>
            <td class="px-6 py-3 text-center">
              <Badge :variant="post.is_published ? 'success' : 'secondary'">{{ post.is_published ? 'Published' : 'Draft' }}</Badge>
            </td>
            <td class="px-6 py-3 hidden lg:table-cell text-xs text-muted-foreground text-left">
              {{ new Date(post.created_at + 'Z').toLocaleString('id-ID') }}
            </td>
            <td v-if="auth.hasPermission('posts.update') || auth.hasPermission('posts.delete')" class="px-6 py-3 text-center border-l border-border/50 bg-muted/5">
              <div class="flex items-center justify-center gap-1">
                <button v-if="auth.hasPermission('posts.update')" @click="openEdit(post)" class="p-1.5 rounded-lg hover:bg-accent transition-colors"><Pencil class="h-4 w-4" /></button>
                <button v-if="auth.hasPermission('posts.delete')" @click="handleDelete(post)" class="p-1.5 rounded-lg hover:bg-accent text-destructive transition-colors"><Trash2 class="h-4 w-4" /></button>
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
