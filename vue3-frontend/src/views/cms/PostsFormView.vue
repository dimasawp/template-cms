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
  is_published: true
})

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
      is_published: post.is_published
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
          
          <div class="pt-2">
            <Label class="text-sm font-semibold mb-2 block">Article Content</Label>
            <!-- JODIT VUE3 COMPONENT -->
            <jodit-editor v-model="form.content" :config="editorConfig" />
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
            <div class="flex items-center gap-3 p-4 bg-muted/40 border border-border rounded-xl cursor-pointer hover:bg-muted/60 transition-colors" @click="form.is_published = !form.is_published">
              <input type="checkbox" v-model="form.is_published" id="is_published" class="rounded w-4 h-4 text-primary focus:ring-primary shadow-sm" @click.stop />
              <div class="flex flex-col">
                <Label for="is_published" class="cursor-pointer font-bold text-foreground">Publish Immediately</Label>
                <span class="text-[10px] text-muted-foreground">Visible to the public</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
