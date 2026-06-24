<script setup>
import { ref, watch, computed, onMounted, onUnmounted } from 'vue'
import Dialog from '@/components/ui/Dialog.vue'
import Button from '@/components/ui/Button.vue'
import { mediaService } from '@/services/mediaService'
import { UploadCloud, File, Copy, Trash2, CheckCircle2, Search, Filter, ChevronDown, ArrowUpDown, ArrowUp, ArrowDown, Eye } from 'lucide-vue-next'
import { notificationService } from '@/services/notificationService'
import Popover from '@/components/ui/Popover.vue'
import PopoverHeader from '@/components/ui/PopoverHeader.vue'
import Label from '@/components/ui/Label.vue'
import ConfirmationDialog from '@/components/ui/ConfirmationDialog.vue'
import { useConfirmation } from '@/composables/useConfirmation'

const confirm = useConfirmation()

const props = defineProps({
  open: Boolean,
  mode: {
    type: String,
    default: 'manage' // 'manage' or 'select'
  }
})

const emit = defineEmits(['close', 'select'])

const mediaItems = ref([])
const total = ref(0)
const loading = ref(false)
const search = ref('')
const filterType = ref('')
const sortBy = ref('created_at')
const sortOrder = ref('desc')
const uploading = ref(false)
const fileInput = ref(null)

const showUploadSuccess = ref(false)
const uploadedFileUrl = ref('')
const previewItem = ref(null)

const skip = ref(0)
const limit = 24
const hasMore = computed(() => mediaItems.value.length < total.value)

const fetchMedia = async (append = false) => {
  if (!append) {
    loading.value = true
    skip.value = 0
  } else {
    if (loading.value) return
    loading.value = true
  }

  try {
    const { data: res } = await mediaService.getAll({ 
      skip: skip.value, limit: limit, search: search.value,
      file_type: filterType.value,
      sort_by: sortBy.value,
      sort_order: sortOrder.value
    })
    
    if (append) {
      mediaItems.value = [...mediaItems.value, ...res.data.items]
    } else {
      mediaItems.value = res.data.items
    }
    total.value = res.data.total
  } catch (error) {
    console.error('Failed to fetch media', error)
  } finally {
    loading.value = false
  }
}

const loadMore = () => {
  if (hasMore.value && !loading.value) {
    skip.value += limit
    fetchMedia(true)
  }
}

const observerTarget = ref(null)
let observer = null

onMounted(() => {
  observer = new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting && hasMore.value && !loading.value) {
      loadMore()
    }
  }, { root: null, rootMargin: '100px', threshold: 0.1 })
})

watch(observerTarget, (el) => {
  if (el && observer) {
    observer.observe(el)
  }
})

onUnmounted(() => {
  if (observer) observer.disconnect()
})

watch(() => props.open, (newVal) => {
  if (newVal) {
    fetchMedia(false)
  }
})

let searchTimeout = null
const onSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    fetchMedia(false)
  }, 500)
}

const triggerUpload = () => {
  fileInput.value?.click()
}

const handleFileUpload = async (e) => {
  const file = e.target.files[0]
  if (!file) return

  uploading.value = true
  try {
    const res = await mediaService.upload(file)
    await fetchMedia(false)
    e.target.value = '' // Reset input
    
    // Show success popup
    uploadedFileUrl.value = getFullUrl(res.data.data.path)
    showUploadSuccess.value = true
  } catch (error) {
    console.error('Upload failed', error)
  } finally {
    uploading.value = false
  }
}

const getFullUrl = (path) => {
  const baseUrl = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1').replace('/api/v1', '')
  // Ensure path doesn't start with slash if baseUrl ends with it
  const cleanPath = path.startsWith('/') ? path.substring(1) : path
  const cleanBase = baseUrl.endsWith('/') ? baseUrl : baseUrl + '/'
  return `${cleanBase}${cleanPath}`
}

const copiedId = ref(null)
const copyUrl = async (item) => {
  const url = getFullUrl(item.path)
  try {
    await navigator.clipboard.writeText(url)
    copiedId.value = item.id
    setTimeout(() => { copiedId.value = null }, 2000)
  } catch (err) {
    console.error('Failed to copy', err)
  }
}

const deleteItem = async (item) => {
  const ok = await confirm.confirm({ 
    title: 'Delete File', 
    message: `Are you sure you want to delete "${item.original_name}"?`, 
    variant: 'destructive' 
  })
  if (!ok) return
  try {
    await mediaService.delete(item.id)
    await fetchMedia(false)
  } catch (error) {
    console.error('Delete failed', error)
  }
}

const selectItem = (item) => {
  if (props.mode === 'select') {
    emit('select', getFullUrl(item.path))
    emit('close')
  }
}

const formatSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const copiedUrl = ref(false)

const copyUploadedUrl = async () => {
  try {
    await navigator.clipboard.writeText(uploadedFileUrl.value)
    copiedUrl.value = true
    setTimeout(() => { copiedUrl.value = false }, 2000)
  } catch (err) {
    console.error('Failed to copy', err)
  }
}
</script>

<template>
  <Dialog :open="open" title="Media Library" maxWidth="max-w-[85vw] w-full h-[90vh]" @close="$emit('close')">
    <div class="flex flex-col h-full overflow-hidden space-y-4 relative">
      
      <!-- Toolbar -->
      <div class="flex items-center justify-between gap-4 shrink-0 flex-wrap">
        <div class="flex items-center gap-2">
          <div class="relative w-64">
            <Search class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <input 
              v-model="search" 
              @input="onSearch"
              type="text" 
              placeholder="Search files..." 
              class="pl-9 pr-4 py-2 w-full border rounded-lg bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            >
          </div>
          <!-- Filter Popover -->
          <Popover align="left" width="w-72">
            <template #trigger="{ isOpen }">
              <Button 
                variant="outline" 
                size="sm" 
                class="h-10 px-3 flex items-center gap-2 border-input hover:bg-accent transition-colors shadow-sm"
                :class="filterType ? 'bg-primary/10 border-primary/20 text-primary' : 'bg-background text-foreground'"
              >
                <Filter class="h-4 w-4" />
                <span>Filter</span>
                <ChevronDown class="h-3 w-3 transition-transform" :class="{'rotate-180': isOpen}" />
              </Button>
            </template>

            <template #default="{ close }">
              <PopoverHeader title="Filter Media" @close="close" />
              <div class="space-y-4">
                <div>
                  <Label class="text-[10px] uppercase tracking-wider text-muted-foreground mb-2.5 block font-bold">File Type</Label>
                  <div class="grid grid-cols-2 gap-2">
                    <button 
                      v-for="t in [{id:'', label:'ALL'}, {id:'image', label:'IMAGES'}, {id:'document', label:'DOCUMENTS'}]" 
                      :key="t.id"
                      @click="filterType = t.id; fetchMedia(false)"
                      class="px-2 py-2 rounded-lg text-[10px] font-bold border transition-all"
                      :class="[
                        filterType === t.id
                        ? 'bg-primary text-white border-primary shadow-md' 
                        : 'bg-background text-muted-foreground border-border hover:bg-muted'
                      ]"
                    >
                      {{ t.label }}
                    </button>
                  </div>
                </div>
              </div>
            </template>
          </Popover>

          <!-- Sort Popover -->
          <Popover align="left" width="w-56">
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
              <PopoverHeader title="Sort Media" @close="close" />

              <div class="space-y-4">
                <div>
                  <Label class="text-[10px] uppercase tracking-wider text-muted-foreground mb-2.5 block font-bold">Sort By</Label>
                  <div class="space-y-1">
                    <button 
                      v-for="f in [{id:'created_at', label:'Date'}, {id:'name', label:'Name'}, {id:'size', label:'Size'}]" 
                      :key="f.id"
                      @click="sortBy = f.id; fetchMedia(false)"
                      class="w-full text-left px-3 py-2.5 rounded-lg text-xs font-medium transition-colors flex items-center justify-between"
                      :class="sortBy === f.id ? 'bg-accent text-primary shadow-sm' : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'"
                    >
                      {{ f.label }}
                      <div v-if="sortBy === f.id" class="w-1.5 h-1.5 rounded-full bg-primary shadow-[0_0_8px_rgba(79,70,229,0.4)]"></div>
                    </button>
                  </div>
                </div>

                <div class="pt-2 border-t border-slate-100">
                  <Label class="text-[10px] uppercase tracking-wider text-muted-foreground mb-2.5 block font-bold">Direction</Label>
                  <div class="grid grid-cols-2 gap-2">
                    <button 
                      @click="sortOrder = 'asc'; fetchMedia(false)"
                      class="flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-xs font-bold border transition-all"
                      :class="sortOrder === 'asc' ? 'bg-primary text-white border-primary shadow-md' : 'bg-background text-muted-foreground border-border hover:bg-muted'"
                    >
                      <ArrowUp class="w-3 h-3" />
                      ASC
                    </button>
                    <button 
                      @click="sortOrder = 'desc'; fetchMedia(false)"
                      class="flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-xs font-bold border transition-all"
                      :class="sortOrder === 'desc' ? 'bg-primary text-white border-primary shadow-md' : 'bg-background text-muted-foreground border-border hover:bg-muted'"
                    >
                      <ArrowDown class="w-3 h-3" />
                      DESC
                    </button>
                  </div>
                </div>
              </div>
            </template>
          </Popover>
        </div>
        <div>
          <input type="file" ref="fileInput" class="hidden" @change="handleFileUpload">
          <Button @click="triggerUpload" :disabled="uploading" class="flex items-center gap-2">
            <UploadCloud v-if="!uploading" class="h-4 w-4" />
            <span v-else class="animate-spin h-4 w-4 border-2 border-current border-t-transparent rounded-full" />
            {{ uploading ? 'Uploading...' : 'Upload File' }}
          </Button>
        </div>
      </div>

      <!-- Grid -->
      <div v-if="loading && mediaItems.length === 0" class="flex justify-center py-12">
        <div class="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full" />
      </div>
      
      <div v-else-if="mediaItems.length === 0" class="text-center py-12 text-muted-foreground bg-muted/20 rounded-lg border border-dashed">
        <UploadCloud class="h-12 w-12 mx-auto mb-3 opacity-20" />
        <p>No media files found.</p>
        <p class="text-sm">Click 'Upload File' to add some.</p>
      </div>

      <div v-else class="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4 flex-1 overflow-y-auto pr-2 custom-scrollbar content-start">
        <div 
          v-for="item in mediaItems" :key="item.id"
          class="group relative border rounded-xl overflow-hidden bg-muted/20 hover:border-primary transition-colors flex flex-col"
          :class="{'cursor-pointer': mode === 'select'}"
          @click="selectItem(item)"
        >
          <!-- Thumbnail -->
          <div class="aspect-square bg-muted flex items-center justify-center relative overflow-hidden">
            <img 
              v-if="item.mime_type?.startsWith('image/')" 
              :src="getFullUrl(item.path)" 
              class="w-full h-full object-cover"
              loading="lazy"
            >
            <File v-else class="h-12 w-12 text-muted-foreground opacity-50" />
            
            <!-- Select Overlay (only in select mode) -->
            <div v-if="mode === 'select'" class="absolute inset-0 bg-primary/20 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
              <Button variant="default" size="sm">Select</Button>
            </div>
          </div>
          
          <!-- Details -->
          <div class="p-2 text-xs flex-1 flex flex-col justify-between border-t bg-card">
            <div class="truncate font-medium" :title="item.original_name">{{ item.original_name }}</div>
            <div class="text-muted-foreground mt-1">{{ formatSize(item.size) }}</div>
          </div>

          <!-- Actions Overlay (available in all modes) -->
          <div class="absolute top-2 right-2 flex flex-col gap-1 opacity-0 group-hover:opacity-100 transition-opacity z-10">
            <button 
              @click.stop="previewItem = item" 
              class="p-1.5 bg-background border shadow-sm rounded-md text-muted-foreground hover:text-primary transition-colors"
              title="Preview"
            >
              <Eye class="h-3.5 w-3.5" />
            </button>
            
            <template v-if="mode === 'manage'">
              <button 
                @click.stop="copyUrl(item)" 
                class="p-1.5 bg-background border shadow-sm rounded-md text-muted-foreground hover:text-primary transition-colors"
                title="Copy URL"
              >
                <CheckCircle2 v-if="copiedId === item.id" class="h-3.5 w-3.5 text-green-500" />
                <Copy v-else class="h-3.5 w-3.5" />
              </button>
              <button 
                @click.stop="deleteItem(item)" 
                class="p-1.5 bg-background border shadow-sm rounded-md text-muted-foreground hover:text-destructive transition-colors"
                title="Delete"
              >
                <Trash2 class="h-3.5 w-3.5" />
              </button>
            </template>
          </div>
        </div>
        
        <!-- Observer Target for Infinite Scroll -->
        <div ref="observerTarget" class="col-span-full h-10 flex items-center justify-center">
          <div v-if="loading && mediaItems.length > 0" class="animate-spin h-5 w-5 border-2 border-primary border-t-transparent rounded-full" />
        </div>
      </div>

    </div>
    
    <template #overlay>
      <!-- Preview Overlay -->
      <div v-if="previewItem" class="absolute inset-0 z-[60] bg-background/95 rounded-xl flex flex-col overflow-hidden">
        <div class="flex items-center justify-between p-4 border-b">
          <div class="flex flex-col">
            <h3 class="font-semibold truncate pr-4 text-foreground">{{ previewItem.original_name }}</h3>
            <span class="text-xs text-muted-foreground">{{ formatSize(previewItem.size) }}</span>
          </div>
          <Button variant="outline" size="sm" @click="previewItem = null">Close Preview</Button>
        </div>
        <div class="flex-1 overflow-auto flex items-center justify-center p-4 bg-muted/30">
          <img 
            v-if="previewItem.mime_type?.startsWith('image/')" 
            :src="getFullUrl(previewItem.path)" 
            class="max-w-full max-h-full object-contain shadow-sm border rounded-lg bg-white"
          >
          <iframe 
            v-else-if="previewItem.mime_type === 'application/pdf'" 
            :src="getFullUrl(previewItem.path)" 
            class="w-full h-full border rounded-lg bg-white"
          ></iframe>
          <div v-else class="text-center">
            <File class="h-16 w-16 mx-auto mb-4 text-muted-foreground opacity-50" />
            <p class="text-muted-foreground mb-4">Preview not available for this file type.</p>
            <Button @click="copyUrl(previewItem)">Copy Link to Download</Button>
          </div>
        </div>
      </div>

      <!-- Upload Success Overlay -->
      <div v-if="showUploadSuccess" class="absolute inset-0 z-[60] bg-background/80 rounded-xl flex items-center justify-center p-4">
        <div class="bg-card border shadow-xl rounded-xl p-6 max-w-md w-full text-center space-y-4">
          <div class="mx-auto w-12 h-12 bg-green-100 text-green-600 rounded-full flex items-center justify-center">
            <CheckCircle2 class="h-6 w-6" />
          </div>
          <h3 class="text-lg font-bold">Upload Successful!</h3>
          <p class="text-sm text-muted-foreground">Your file has been uploaded to the media library.</p>
          
          <div class="flex items-center gap-2 p-2 bg-muted rounded-lg border">
            <input type="text" :value="uploadedFileUrl" readonly class="bg-transparent border-none focus:outline-none text-xs w-full text-muted-foreground">
            <Button size="sm" @click="copyUploadedUrl" class="shrink-0 gap-1" :variant="copiedUrl ? 'secondary' : 'default'">
              <CheckCircle2 v-if="copiedUrl" class="h-3.5 w-3.5 text-green-600" />
              <Copy v-else class="h-3.5 w-3.5" /> 
              {{ copiedUrl ? 'Copied!' : 'Copy Link' }}
            </Button>
          </div>

          <Button variant="outline" class="w-full mt-2" @click="showUploadSuccess = false">Close</Button>
        </div>
      </div>
    </template>
    
    <template #footer v-if="mode === 'manage'">
      <Button variant="outline" @click="$emit('close')">Close</Button>
    </template>
    
    <ConfirmationDialog
      :open="confirm.isOpen.value"
      :title="confirm.title.value"
      :message="confirm.message.value"
      :variant="confirm.variant.value"
      @confirm="confirm.onConfirm"
      @cancel="confirm.onCancel"
    />
  </Dialog>
</template>
