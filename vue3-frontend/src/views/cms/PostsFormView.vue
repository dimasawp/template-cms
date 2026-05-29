<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { postService } from '@/services/postService'
import { categoryService } from '@/services/categoryService'
import PageHeader from '@/components/common/PageHeader.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Label from '@/components/ui/Label.vue'
import FormField from '@/components/ui/FormField.vue'
import JoditEditor from '@/components/ui/JoditEditor.vue'

const router = useRouter()
const route = useRoute()
const { toast } = useToast()

const isEditing = ref(false)
const saving = ref(false)
const categories = ref([])
const form = ref({
  title: '',
  slug: '',
  category_id: '',
  content: '',
  status: 'DRAFT',
  thumbnail: '',
  additional_contents: []
})

import { Plus, Trash2, Upload, XCircle } from 'lucide-vue-next'
import { uploadService } from '@/services/uploadService'

const uploadingThumbnail = ref(false)
const blockUploads = ref({})

async function handleThumbnailUpload(event) {
  const file = event.target.files[0]
  if (!file) return
  
  uploadingThumbnail.value = true
  try {
    const { data } = await uploadService.uploadFile(file)
    let path = data.data.path.replace(/\\/g, '/')
    if (!path.startsWith('/')) path = '/' + path
    const baseUrl = import.meta.env.VITE_API_BASE_URL.replace('/api/v1', '')
    form.value.thumbnail = baseUrl + path
    form.value.thumbnail_error = false // Reset error state
  } catch (e) {
    toast({ title: 'Error', message: 'Failed to upload thumbnail', variant: 'destructive' })
  } finally {
    uploadingThumbnail.value = false
    event.target.value = ''
  }
}

async function handleBlockFileUpload(event, index) {
  const file = event.target.files[0]
  if (!file) return
  
  blockUploads.value[index] = true
  try {
    const { data } = await uploadService.uploadFile(file)
    let path = data.data.path.replace(/\\/g, '/')
    if (!path.startsWith('/')) path = '/' + path
    const baseUrl = import.meta.env.VITE_API_BASE_URL.replace('/api/v1', '')
    form.value.additional_contents[index].url = baseUrl + path
  } catch (e) {
    toast({ title: 'Error', message: 'Failed to upload file', variant: 'destructive' })
  } finally {
    blockUploads.value[index] = false
    event.target.value = ''
  }
}

function addBlock() {
  form.value.additional_contents.push({
    id: 'block-' + Date.now().toString(36) + Math.random().toString(36).substr(2, 5),
    type: 'iframe',
    source_type: 'url',
    url: '',
    title: '',
    order: form.value.additional_contents.length + 1
  })
}

function removeBlock(index) {
  form.value.additional_contents.splice(index, 1)
}

const editorConfig = {
  minHeight: 400
}

function generateSlug() {
  if (!isEditing.value) {
    form.value.slug = form.value.title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)+/g, '')
  }
}

function formatCategoryTree(items) {
  const itemMap = new Map()
  items.forEach(item => {
    itemMap.set(item.id, { ...item, children: [] })
  })

  const tree = []
  itemMap.forEach(item => {
    if (item.parent_id && itemMap.has(item.parent_id)) {
      itemMap.get(item.parent_id).children.push(item)
    } else {
      tree.push(item)
    }
  })

  const flat = []
  function traverse(nodes, depth = 0, prefix = '') {
    nodes.forEach((node, index) => {
      const isLast = index === nodes.length - 1;
      let branch = '';
      if (depth > 0) {
        branch = isLast ? '└─ ' : '├─ ';
      }
      
      flat.push({
        ...node,
        level: depth,
        isLast,
        prefix,
        branch,
        displayName: prefix + branch + node.name
      })
      
      // Use standard spaces for HTML select element, 
      // where monospace is not guaranteed but spaces still work okayish.
      // Alternatively we can use non-breaking spaces for indenting.
      const nextPrefix = prefix + (depth > 0 ? (isLast ? '\u00A0\u00A0\u00A0\u00A0' : '│\u00A0\u00A0\u00A0') : '');
      traverse(node.children, depth + 1, nextPrefix)
    })
  }
  traverse(tree)
  return flat
}

async function loadCategories() {
  try {
    const { data } = await categoryService.getAll({ per_page: 1000 })
    categories.value = formatCategoryTree(data.data.items)
  } catch (e) {
    console.error("Failed to load categories", e)
  }
}

async function loadPost() {
  const id = route.params.id
  if (!id) return
  isEditing.value = true
  try {
    const { data } = await postService.getById(id)
    const post = data.data
    form.value = {
      title: post.title,
      slug: post.slug,
      category_id: post.category_id || '',
      content: post.content || '',
      status: post.status || 'DRAFT',
      thumbnail: post.thumbnail || '',
      additional_contents: post.additional_contents || []
    }
  } catch (e) {
    toast({ title: 'Error', message: 'Failed to load post', variant: 'destructive' })
    router.push('/posts')
  }
}

let isDraftLoaded = false

onMounted(async () => {
  await loadCategories()
  if (route.params.id) {
    await loadPost()
  }

  const draftKey = 'post_draft_' + (route.params.id || 'new')
  const draft = localStorage.getItem(draftKey)
  if (draft) {
    try {
      const parsedDraft = JSON.parse(draft)
      // Check if draft has content
      if (parsedDraft.title || parsedDraft.content) {
        // Delay to allow UI to render first
        setTimeout(() => {
          if (confirm('An unsaved draft was found. Would you like to restore it?')) {
            form.value = parsedDraft
          } else {
            localStorage.removeItem(draftKey)
          }
        }, 300)
      }
    } catch(e) {}
  }
  isDraftLoaded = true
})

watch(form, (newVal) => {
  if (isDraftLoaded) {
    const draftKey = 'post_draft_' + (route.params.id || 'new')
    localStorage.setItem(draftKey, JSON.stringify(newVal))
  }
}, { deep: true })

async function handleSave() {
  saving.value = true
  try {
    const payload = { ...form.value }
    if (payload.category_id === '') {
      payload.category_id = null
    }

    if (isEditing.value) {
      await postService.update(route.params.id, payload)
      toast({ title: 'Success', message: 'Post updated successfully' })
    } else {
      await postService.create(payload)
      toast({ title: 'Success', message: 'Post created successfully' })
    }
    
    // Clear draft on success
    localStorage.removeItem('post_draft_' + (route.params.id || 'new'))
    
    router.push('/posts')
  } catch (e) {
    toast({ title: 'Error', message: e.response?.data?.message || 'Failed to save post', variant: 'destructive' })
  } finally {
    saving.value = false
  }
}

</script>

<template>
  <div class="max-w-6xl mx-auto pb-10">
    <div class="flex items-center justify-between mb-6">
      <PageHeader :title="isEditing ? 'Edit Post' : 'Write New Post'" description="Use the editor below to compose your article content." />
      <div class="flex gap-3">
        <Button variant="outline" @click="router.push('/posts')">Cancel</Button>
        <Button @click="handleSave" :loading="saving">{{ isEditing ? 'Save Changes' : 'Publish Post' }}</Button>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2 space-y-6">
        <div class="bg-card border border-border p-6 rounded-xl shadow-sm space-y-5">
          <FormField label="Article Title" htmlFor="title">
            <Input id="title" v-model="form.title" @input="generateSlug" placeholder="Enter title..." class="text-lg font-bold h-12" />
          </FormField>
          
          <FormField label="Thumbnail Image" htmlFor="thumbnail">
            <div class="flex items-center gap-3">
              <div class="relative flex-1">
                <Input id="thumbnail" v-model="form.thumbnail" @input="form.thumbnail_error = false" placeholder="URL or Upload..." class="h-10 w-full pr-10" />
                <button type="button" v-if="form.thumbnail" @click="form.thumbnail = ''; form.thumbnail_error = false" class="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-destructive transition-colors">
                  <XCircle class="w-4 h-4" />
                </button>
              </div>
              <div class="relative">
                <input type="file" accept="image/*" @change="handleThumbnailUpload" class="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed" :disabled="uploadingThumbnail" />
                <Button type="button" variant="outline" class="h-10 shrink-0" :loading="uploadingThumbnail">
                  <Upload class="w-4 h-4 mr-2" /> Upload
                </Button>
              </div>
            </div>
            <div v-if="form.thumbnail" class="mt-3 rounded-lg border overflow-hidden w-full max-w-xs bg-muted/30">
               <img :src="form.thumbnail" class="w-full h-auto object-cover" @error="form.thumbnail_error = true" v-show="!form.thumbnail_error" />
               <div v-if="form.thumbnail_error" class="p-4 text-xs text-muted-foreground text-center">Invalid image URL</div>
            </div>
          </FormField>

          <div class="pt-2 border-t border-border mt-4">
            <Label class="text-sm font-semibold mb-2 block pt-4">Article Content</Label>
            <!-- JODIT VUE3 COMPONENT -->
            <jodit-editor v-model="form.content" :config="editorConfig" />
          </div>

          <!-- Additional Contents Block Builder -->
          <div class="pt-6 border-t border-border mt-6">
            <div class="flex items-center justify-between mb-4">
              <div>
                <Label class="text-sm font-semibold block">Additional Blocks</Label>
                <p class="text-xs text-muted-foreground mt-1">Add embedded content like YouTube videos or PDFs</p>
              </div>
              <Button type="button" variant="outline" size="sm" @click="addBlock" class="h-8">
                <Plus class="w-3.5 h-3.5 mr-2" /> Add Block
              </Button>
            </div>
            
            <div class="space-y-4">
              <div v-for="(block, index) in form.additional_contents" :key="block.id" class="p-4 bg-muted/30 border border-border rounded-xl relative group transition-all">
                <button type="button" @click="removeBlock(index)" class="absolute top-2 right-2 p-1.5 text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded-md transition-colors opacity-0 group-hover:opacity-100">
                  <Trash2 class="w-4 h-4" />
                </button>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mr-8">
                  <FormField label="Block Title (Optional)">
                    <Input v-model="block.title" placeholder="E.g. Tutorial Video" class="h-9 text-sm" />
                  </FormField>
                  <FormField label="Source Type">
                    <select v-model="block.source_type" class="w-full flex h-9 rounded-md border border-input bg-background px-3 py-1.5 text-sm ring-offset-background focus-visible:outline-none focus:ring-2 focus:ring-primary transition-colors">
                      <option value="url">URL Link</option>
                      <option value="file">Upload File</option>
                    </select>
                  </FormField>
                  <FormField label="Content URL / File" class="md:col-span-2">
                    <div class="flex items-center gap-2">
                      <div class="relative flex-1">
                        <Input v-model="block.url" placeholder="https://youtube.com/embed/... or Upload" class="h-9 w-full pr-9 text-sm font-mono text-muted-foreground" />
                        <button type="button" v-if="block.url" @click="block.url = ''" class="absolute right-2.5 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-destructive transition-colors">
                          <XCircle class="w-4 h-4" />
                        </button>
                      </div>
                      <div class="relative" v-if="block.source_type === 'file'">
                        <input type="file" @change="(e) => handleBlockFileUpload(e, index)" class="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed" :disabled="blockUploads[index]" />
                        <Button type="button" variant="outline" size="sm" class="h-9 shrink-0" :loading="blockUploads[index]">
                          <Upload class="w-4 h-4 mr-2" /> Upload
                        </Button>
                      </div>
                    </div>
                  </FormField>
                </div>
              </div>
              
              <div v-if="!form.additional_contents.length" class="text-center py-8 border-2 border-dashed border-border rounded-xl text-muted-foreground text-sm bg-muted/10">
                No additional blocks added.
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="lg:col-span-1 space-y-6">
        <div class="bg-card border border-border p-5 rounded-xl shadow-sm space-y-5">
          <h3 class="font-bold border-b border-border pb-3">Settings</h3>
          
          <FormField label="URL Slug" htmlFor="slug">
            <Input id="slug" v-model="form.slug" placeholder="example-title" />
          </FormField>

          <FormField label="Category" htmlFor="cat">
            <select 
              id="cat" 
              v-model="form.category_id"
              class="w-full flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus:ring-2 focus:ring-primary transition-all"
            >
              <option value="">No Category</option>
              <option 
                v-for="c in categories" 
                :key="c.id" 
                :value="c.id"
                :disabled="!c.is_active"
              >
                {{ c.displayName }} {{ !c.is_active ? '(Inactive)' : '' }}
              </option>
            </select>
          </FormField>

          <div class="pt-3 border-t border-border">
            <FormField label="Status" htmlFor="status">
              <select 
                id="status" 
                v-model="form.status"
                class="w-full flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus:ring-2 focus:ring-primary transition-all"
              >
                <option value="DRAFT">Draft</option>
                <option value="PUBLISHED">Published</option>
                <option value="ARCHIVED">Archived</option>
              </select>
            </FormField>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
