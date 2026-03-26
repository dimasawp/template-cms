<script setup lang="ts">
import PageHeader from '@/components/common/PageHeader.vue'

// UI Components
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Label from '@/components/ui/Label.vue'
import CardBasic from '@/components/ui/CardBasic.vue'
import CardImage from '@/components/ui/CardImage.vue'
import CardStats from '@/components/ui/CardStats.vue'
import SkeletonLoader from '@/components/ui/SkeletonLoader.vue'
import { ref } from 'vue'

const isLoading = ref(false)
const inputValue = ref('')

const toggleLoading = () => {
  isLoading.value = true
  setTimeout(() => (isLoading.value = false), 2000)
}
</script>

<template>
  <div>
    <PageHeader title="UI Components Documentation" description="Daftar komponen UI yang tersedia dan cara menggunakannya." />

    <div class="mt-6 flex flex-col space-y-12 pb-12">
      <!-- Buttons -->
      <section>
        <h2 class="text-xl font-semibold border-b pb-2 mb-4">Buttons</h2>
        <div class="flex flex-wrap items-center gap-4 bg-card border rounded-lg p-6">
          <Button variant="default">Default</Button>
          <Button variant="destructive">Destructive</Button>
          <Button variant="outline">Outline</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="ghost">Ghost</Button>
          <Button variant="link">Link</Button>
          <Button @click="toggleLoading" :isLoading="isLoading">Loading Button</Button>
        </div>
      </section>

      <!-- Inputs & Labels -->
      <section>
        <h2 class="text-xl font-semibold border-b pb-2 mb-4">Forms & Inputs</h2>
        <div class="grid max-w-sm gap-4 bg-card border rounded-lg p-6">
          <div class="grid w-full items-center gap-1.5">
            <Label for="email">Email</Label>
            <Input type="email" id="email" placeholder="Email" v-model="inputValue" />
            <p class="text-sm text-muted-foreground mt-1 text-xs">Nilai input: {{ inputValue }}</p>
          </div>
          <div class="grid w-full items-center gap-1.5">
            <Label for="error-input" class="text-destructive">Input with Error</Label>
            <Input type="text" id="error-input" error="Field ini wajib diisi." />
          </div>
        </div>
      </section>

      <!-- Cards -->
      <section>
        <h2 class="text-xl font-semibold border-b pb-2 mb-4">Cards</h2>
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

      <!-- Feedback / Skeletons / Toasters (visual demo placeholder) -->
      <section>
        <h2 class="text-xl font-semibold border-b pb-2 mb-4">Feedback & Loaders</h2>
        <div class="grid gap-6 md:grid-cols-2">
          <!-- Skeleton -->
          <div class="bg-card border rounded-lg p-6 flex flex-col space-y-3">
            <h3 class="font-medium mb-2">Skeleton Loader</h3>
            <SkeletonLoader class="h-[125px] w-full rounded-xl" />
            <div class="space-y-2">
              <SkeletonLoader class="h-4 w-[250px]" />
              <SkeletonLoader class="h-4 w-[200px]" />
            </div>
          </div>
          
          <!-- Toaster Info -->
          <div class="bg-card border rounded-lg p-6 flex flex-col justify-center items-center text-center space-y-4">
            <h3 class="font-medium">Toaster</h3>
            <p class="text-sm text-muted-foreground">Toaster adalah komponen global yang dikelola melalui <code>useToast()</code>. Klik tombol di bawah untuk mencoba memicu toast.</p>
            <div class="flex flex-wrap gap-2 justify-center">
               <!-- In a real app we'd trigger a toast here, but we just show the visual concept or trigger it if useToast is available -->
               <div class="px-4 py-2 border rounded shadow-sm bg-background border-border flex items-center gap-2">
                 <div class="w-2 h-2 rounded-full bg-green-500"></div> Success Toast Example
               </div>
            </div>
          </div>
        </div>
      </section>

    </div>
  </div>
</template>
