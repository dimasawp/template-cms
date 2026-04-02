<script setup lang="ts">
import PageHeader from '@/components/common/PageHeader.vue'

// UI Components
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import CardBasic from '@/components/ui/CardBasic.vue'
import CardImage from '@/components/ui/CardImage.vue'
import CardStats from '@/components/ui/CardStats.vue'
import SkeletonLoader from '@/components/ui/SkeletonLoader.vue'
import Avatar from '@/components/ui/Avatar.vue'
import Dialog from '@/components/ui/Dialog.vue'
import ConfirmationDialog from '@/components/ui/ConfirmationDialog.vue'
import Badge from '@/components/ui/Badge.vue'
import StatusIndicator from '@/components/ui/StatusIndicator.vue'
import FormField from '@/components/ui/FormField.vue'
import PopoverHeader from '@/components/ui/PopoverHeader.vue'
import DataTableToolbar from '@/components/common/DataTableToolbar.vue'
import { Filter, ChevronDown } from 'lucide-vue-next'
import { useToast } from '@/composables/useToast'
import { useConfirmation } from '@/composables/useConfirmation'
import { ref } from 'vue'

const { toast } = useToast()

const isLoading = ref(false)
const showDemoModal = ref(false)

const confirm = useConfirmation()

const toggleLoading = () => {
  isLoading.value = true
  setTimeout(() => (isLoading.value = false), 2000)
}

const handleDemoConfirm = async () => {
  const ok = await confirm.confirm({
    title: 'Hapus Data Masal?',
    message: 'Aksi ini tidak dapat dibatalkan. Seluruh data terpilih akan dihapus selamanya dari sistem.',
    variant: 'destructive'
  })
  if (ok) {
    alert('Aksi dikonfirmasi!')
  }
}
</script>

<template>
  <div>
    <PageHeader title="UI Components Documentation" description="Daftar komponen UI yang tersedia dan cara menggunakannya." />

    <div class="mt-6 flex flex-col space-y-12 pb-12">
      <!-- Buttons -->
      <section>
        <h2 class="text-xl font-semibold border-b pb-2 mb-4">Buttons</h2>
        <div class="flex flex-wrap items-center gap-4 bg-card border border-border rounded-lg p-6 shadow-sm">
          <Button variant="default">Default</Button>
          <Button variant="destructive">Destructive</Button>
          <Button variant="outline">Outline</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="ghost">Ghost</Button>
          <Button variant="link">Link</Button>
          <Button @click="toggleLoading" :isLoading="isLoading">Loading Button</Button>
        </div>
      </section>

      <!-- Badge & Status (Lego UI) -->
      <section>
        <h2 class="text-xl font-semibold border-b pb-2 mb-4">Badges & Status Indicators</h2>
        <div class="grid gap-6 md:grid-cols-2">
          <div class="bg-card border border-border rounded-lg p-6 space-y-4">
            <h3 class="text-xs font-bold text-muted-foreground uppercase mb-4">Badge Variants</h3>
            <div class="flex flex-wrap gap-2">
              <Badge variant="primary">Primary</Badge>
              <Badge variant="success">Success</Badge>
              <Badge variant="warning">Warning</Badge>
              <Badge variant="destructive">Destructive</Badge>
              <Badge variant="indigo">Indigo</Badge>
              <Badge variant="secondary">Secondary</Badge>
              <Badge variant="outline">Outline</Badge>
            </div>
            <p class="text-[10px] text-muted-foreground italic">Gunakan Badge untuk menandai role, kategori, atau tipe data.</p>
          </div>
          
          <div class="bg-card border border-border rounded-lg p-6 space-y-4 flex flex-col justify-center">
            <h3 class="text-xs font-bold text-muted-foreground uppercase mb-4">Status Indicators (Active/Inactive)</h3>
            <div class="flex gap-8">
              <div class="space-y-4">
                <StatusIndicator :active="true" />
                <StatusIndicator :active="false" />
              </div>
              <div class="space-y-4">
                <StatusIndicator :active="true" label="Online" />
                <StatusIndicator :active="false" label="Offline" />
              </div>
            </div>
            <p class="text-[10px] text-muted-foreground italic">Menjamin konsistensi warna dot dan teks di seluruh tabel.</p>
          </div>
        </div>
      </section>

      <!-- FormField (Lego UI) -->
      <section>
        <h2 class="text-xl font-semibold border-b border-border pb-2 mb-4">Forms & Layouts</h2>
        <div class="bg-card border border-border rounded-lg p-6">
          <div class="grid gap-6 md:grid-cols-2 max-w-2xl">
            <FormField label="Username" htmlFor="username-demo" required description="Gunakan username unik untuk login.">
              <Input id="username-demo" placeholder="contoh: jhon_doe" />
            </FormField>
            
            <FormField label="Password" htmlFor="password-demo" error="Password minimal 8 karakter.">
              <Input id="password-demo" type="password" placeholder="••••••••" />
            </FormField>
            
            <FormField label="Role Akses" htmlFor="role-demo">
              <select class="w-full h-10 px-3 rounded-md border border-input bg-background text-foreground text-sm focus:ring-2 focus:ring-primary transition-all outline-none">
                <option>Admin</option>
                <option>User</option>
              </select>
              <template #label-right>
                <button class="text-[10px] text-primary font-bold hover:underline">Butuh Bantuan?</button>
              </template>
            </FormField>
          </div>
        </div>
      </section>

      <!-- Cards -->
      <section>
        <h2 class="text-xl font-semibold border-b border-border pb-2 mb-4">Cards</h2>
        <div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <CardBasic title="Card Basic" description="Card sederhana untuk konten teks.">
            <div>Ini adalah konten di dalam CardBasic. Anda bisa meletakkan apa saja di sini.</div>
            <template #footer>
              <Button class="w-full">Action</Button>
            </template>
          </CardBasic>

          <CardImage 
            title="Card Image" 
            description="Card dengan gambar di bagian atas." 
            image="https://images.unsplash.com/photo-1579546929518-9e396f3cc809?q=80&w=600&auto=format&fit=crop"
          >
            <div>Konten untuk card image. Cocok untuk artikel atau produk.</div>
            <template #footer>
              <Button variant="outline" class="w-full">View Details</Button>
            </template>
          </CardImage>

          <CardStats 
            title="Card Stats" 
            value="1,234" 
            description="+20.1% dari bulan lalu" 
            trend="up"
          >
            <!-- Slot untuk icon (opsional) -->
          </CardStats>
        </div>
      </section>

      <!-- Feedback & Loaders -->
      <section>
        <h2 class="text-xl font-semibold border-b border-border pb-2 mb-4">Feedback & Notifications</h2>
        <div class="grid gap-6 md:grid-cols-2">
          <!-- Skeleton -->
          <div class="bg-card border border-border rounded-lg p-6 flex flex-col space-y-3">
            <h3 class="font-medium mb-4">Skeleton Loader</h3>
            <div class="flex items-center space-x-4">
              <SkeletonLoader class="h-12 w-12 rounded-full" />
              <div class="space-y-2">
                <SkeletonLoader class="h-4 w-[250px]" />
                <SkeletonLoader class="h-4 w-[200px]" />
              </div>
            </div>
            <SkeletonLoader class="h-[100px] w-full rounded-xl mt-4" />
          </div>
          
          <!-- Toaster Trigger -->
          <div class="bg-card border border-border rounded-lg p-6 flex flex-col justify-center items-center text-center space-y-4">
            <h3 class="font-medium">Toaster (Toast Notifications)</h3>
            <p class="text-sm text-muted-foreground">Komponen notifikasi global yang melayang di pojok layar.</p>
            <div class="flex flex-wrap gap-2 justify-center">
              <Button variant="outline" size="sm" @click="toast({ title: 'Success!', description: 'Data has been updated.', variant: 'success' })">Success Toast</Button>
              <Button variant="outline" size="sm" @click="toast({ title: 'Error Happened', description: 'Failed to sync data.', variant: 'destructive' })">Error Toast</Button>
              <Button variant="outline" size="sm" @click="toast({ title: 'Generic Info', description: 'This is a normal message.' })">Info Toast</Button>
            </div>
          </div>
        </div>
      </section>

      <!-- Avatars & Profiles -->
      <section>
        <h2 class="text-xl font-semibold border-b border-border pb-2 mb-4">Avatars & Profiles</h2>
        <div class="bg-card border border-border rounded-lg p-6">
          <div class="flex flex-wrap items-end gap-6 justify-center py-8 bg-muted/40 rounded-xl border border-dashed border-border">
            <div class="flex flex-col items-center gap-1.5">
               <Avatar name="Small User" size="xs" />
               <span class="text-[10px] text-muted-foreground font-bold">XS</span>
            </div>
            <div class="flex flex-col items-center gap-1.5">
               <Avatar name="Admin User" size="sm" />
               <span class="text-[10px] text-muted-foreground font-bold">SM</span>
            </div>
            <div class="flex flex-col items-center gap-1.5">
               <Avatar name="Dimas Awang" size="md" />
               <span class="text-[10px] text-muted-foreground font-bold">MD</span>
            </div>
            <div class="flex flex-col items-center gap-1.5">
               <Avatar name="Super Admin" size="lg" />
               <span class="text-[10px] text-muted-foreground font-bold">LG</span>
            </div>
            <div class="flex flex-col items-center gap-1.5">
               <Avatar name="Profile Master" size="xl" />
               <span class="text-[10px] text-muted-foreground font-bold">XL</span>
            </div>
          </div>
          <p class="mt-4 text-center text-xs text-muted-foreground italic">
            Avatar otomatis menghasilkan inisial dan warna background berdasarkan nama jika gambar tidak tersedia.
          </p>
        </div>
      </section>

      <!-- Navigation & Data -->
      <section>
        <h2 class="text-xl font-semibold border-b border-border pb-2 mb-4">Navigation & Pagination</h2>
        <div class="bg-card border border-border rounded-lg p-6 flex flex-col items-center gap-6">
           <div class="w-full max-w-md p-4 bg-muted/40 rounded-xl border border-dashed border-border flex flex-col items-center gap-4">
             <h3 class="text-xs font-bold text-muted-foreground uppercase">Pagination Component</h3>
             <div class="flex items-center gap-2">
               <Button variant="outline" size="sm" class="h-8 w-8 p-0">1</Button>
               <Button variant="outline" size="sm" class="h-8 w-8 p-0 bg-primary text-primary-foreground border-primary hover:bg-primary/90">2</Button>
               <Button variant="outline" size="sm" class="h-8 w-8 p-0">3</Button>
               <div class="px-1 text-muted-foreground">...</div>
               <Button variant="outline" size="sm" class="h-8 w-8 p-0">10</Button>
             </div>
             <p class="text-[10px] text-muted-foreground italic text-center">Standard navigation for list and table views.</p>
           </div>
        </div>
      </section>

      <!-- Data Table Tools (Lego UI) -->
      <section>
        <h2 class="text-xl font-semibold border-b border-border pb-2 mb-4">Data Table Tools</h2>
        <div class="space-y-6">
          <!-- Popover Header -->
          <div class="bg-card border border-border rounded-lg p-6">
            <h3 class="text-xs font-bold text-muted-foreground uppercase mb-4">Popover Header</h3>
            <div class="max-w-xs bg-popover border border-border rounded-xl shadow-xl p-4">
              <PopoverHeader title="Contoh Judul Dropdown" @close="() => {}" />
              <div class="py-4 text-center text-xs text-muted-foreground italic">Konten dropdown di sini...</div>
            </div>
          </div>
          
          <!-- DataTable Toolbar -->
          <div class="bg-card border border-border rounded-lg p-6">
            <h3 class="text-xs font-bold text-muted-foreground uppercase mb-4">DataTable Toolbar (Complete Bar)</h3>
            <div class="p-4 bg-muted/40 rounded-xl border border-dashed border-border">
              <DataTableToolbar
                search-placeholder="Cari data apa pun..."
                addButtonLabel="Tambah Item Baru"
                showAddButton
                searchModelValue=""
                @refresh="() => {}"
                @add="() => {}"
              >
                <template #actions-start>
                  <Button variant="outline" size="sm" class="h-10 px-3 flex items-center gap-2 border-input">
                    <Filter class="h-4 w-4" />
                    <span>Filter</span>
                    <ChevronDown class="h-3 w-3" />
                  </Button>
                </template>
              </DataTableToolbar>
            </div>
            <p class="mt-4 text-[10px] text-muted-foreground italic">Menangani Search, Sync, Refresh, Filter, dan Add dalam satu baris responsif.</p>
          </div>
        </div>
      </section>

      <!-- Overlays & Dialogs -->
      <section>
        <h2 class="text-xl font-semibold border-b border-border pb-2 mb-4">Overlays & Dialogs</h2>
        <div class="grid gap-6 md:grid-cols-2">
          <!-- Standard Dialog -->
          <div class="bg-card border border-border rounded-lg p-6 flex flex-col items-center justify-center text-center space-y-4">
            <h3 class="font-medium text-foreground">Standard Dialog (Modal)</h3>
            <p class="text-sm text-muted-foreground">Komponen modal premium dengan dukungan Esc key, tombol close X, dan click-outside.</p>
            <Button variant="outline" @click="showDemoModal = true">Buka Demo Modal</Button>
            
            <Dialog 
              :open="showDemoModal" 
              title="Standard Dialog Example" 
              @close="showDemoModal = false"
            >
              <div class="space-y-4 py-2 text-start">
                <p class="text-sm text-muted-foreground leading-relaxed">
                  Ini adalah contoh konten modal yang sudah terstandarisasi. Anda bisa memasukkan form atau informasi apa pun di sini.
                </p>
                <div class="p-4 bg-primary/10 border border-primary/20 rounded-xl text-xs text-primary">
                   🚀 <strong>Info UX:</strong> Coba tekan tombol <strong>Esc</strong> atau klik di luar kotak ini untuk menutup modal dengan cepat.
                </div>
              </div>
              <template #footer>
                <Button variant="outline" @click="showDemoModal = false">Tutup</Button>
                <Button type="primary" @click="showDemoModal = false">Simpan Data</Button>
              </template>
            </Dialog>
          </div>

          <!-- Confirmation Dialog -->
          <div class="bg-card border border-border rounded-lg p-6 flex flex-col items-center justify-center text-center space-y-4">
            <h3 class="font-medium text-foreground">Confirmation Dialog</h3>
            <p class="text-sm text-muted-foreground">Digunakan untuk aksi berbahaya seperti penghapusan atau logout.</p>
            <Button variant="destructive" @click="handleDemoConfirm">Picu Aksi Berbahaya</Button>
          </div>
        </div>
      </section>
    </div>

    <!-- Global Component Handlers -->
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
