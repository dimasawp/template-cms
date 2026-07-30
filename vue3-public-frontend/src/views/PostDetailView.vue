<script setup>
import { ref, computed, onMounted, inject } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { publicService } from '@/services/api'
import Badge from '@/components/ui/Badge.vue'
import SkeletonLoader from '@/components/ui/SkeletonLoader.vue'
import Button from '@/components/ui/Button.vue'
import PostCard from '@/components/PostCard.vue'

const route = useRoute()
const post = ref(null)
const loading = ref(true)
const relatedPosts = ref([])
const relatedLoading = ref(false)

const categoriesMap = inject('categoriesMap', {})

const categoryName = computed(() => {
  if (!post.value?.category_id) return null
  const c = categoriesMap[post.value.category_id]
  return c ? c.name : null
})

const formattedDate = computed(() => {
  if (!post.value?.created_at) return ''
  const date = new Date(post.value.created_at)
  return new Intl.DateTimeFormat('en-US', { month: 'long', day: 'numeric', year: 'numeric' }).format(date)
})

const getImageUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  const baseUrl = import.meta.env.VITE_API_BASE_URL?.replace('/api/v1', '') || 'http://localhost:8000'
  const cleanPath = path.startsWith('/') ? path.substring(1) : path
  const cleanBase = baseUrl.endsWith('/') ? baseUrl : baseUrl + '/'
  return `${cleanBase}${cleanPath}`
}

const fetchPostDetail = async () => {
  try {
    const res = await publicService.getPostDetail(route.params.slug)
    post.value = res.data.data
    document.title = post.value.title
    const metaDesc = document.querySelector('meta[name="description"]')
    if (metaDesc) {
      metaDesc.content = post.value.content ? post.value.content.replace(/<[^>]*>/g, '').substring(0, 160) : ''
    }
  } catch (error) {
    console.error('Failed to fetch post detail', error)
  } finally {
    loading.value = false
  }
}

const fetchRelatedPosts = async () => {
  if (!post.value?.slug) return
  relatedLoading.value = true
  try {
    const res = await publicService.getRelatedPosts(post.value.slug)
    relatedPosts.value = res.data.data.items
  } catch (error) {
    console.error('Failed to fetch related posts', error)
  } finally {
    relatedLoading.value = false
  }
}

onMounted(async () => {
  await fetchPostDetail()
  if (post.value) {
    fetchRelatedPosts()
  }
})
</script>

<template>
  <div class="mx-auto max-w-6xl px-5 py-10">
    <div v-if="loading" class="mx-auto max-w-3xl">
      <div class="mb-6 text-center">
        <SkeletonLoader class="mx-auto mb-4 h-6 w-24 rounded-full" />
        <SkeletonLoader class="mx-auto mb-4 h-12 w-3/4" />
        <SkeletonLoader class="mx-auto h-4 w-1/2" />
      </div>
      <SkeletonLoader class="mb-10 aspect-[16/9] w-full rounded-lg" />
      <div class="space-y-4">
        <SkeletonLoader v-for="n in 6" :key="n" class="h-5 w-full" />
      </div>
    </div>

    <div v-else-if="!post" class="mx-auto max-w-lg rounded-lg border border-border bg-background py-20 text-center text-muted-foreground">
      <h2 class="text-2xl font-bold">Post not found</h2>
      <p>The post you are looking for does not exist or has been removed.</p>
      <RouterLink to="/" class="mt-5 inline-block">
        <Button>Return Home</Button>
      </RouterLink>
    </div>

    <article v-else class="mx-auto max-w-3xl">
      <header class="mb-8 text-center">
        <div v-if="categoryName" class="mb-4">
          <Badge variant="primary">{{ categoryName }}</Badge>
        </div>
        <h1 class="mb-2 text-[clamp(2rem,4vw,3.5rem)] font-extrabold leading-tight">{{ post.title }}</h1>
        <div class="text-sm text-muted-foreground">
          <span v-if="post.author">By {{ post.author.full_name || post.author.username }} &bull; </span>
          <span>Published on {{ formattedDate }}</span>
        </div>
      </header>

      <div v-if="post.thumbnail" class="mb-10 aspect-[16/9] w-full overflow-hidden rounded-lg shadow-lg">
        <img :src="getImageUrl(post.thumbnail)" :alt="post.title" class="h-full w-full object-cover" />
      </div>

      <div class="mb-10 rounded-lg border border-border bg-background p-10" v-html="post.content">
      </div>

      <div v-if="post.additional_contents && post.additional_contents.length > 0">
        <h3 class="mb-5 text-2xl font-bold">Additional Media</h3>

        <div class="flex flex-col gap-8">
          <div
            v-for="(block, index) in post.additional_contents"
            :key="index"
            class="rounded-lg border border-border bg-background p-8"
          >
            <h4 v-if="block.title" class="mb-4 text-lg font-semibold text-primary">{{ block.title }}</h4>

            <div
              v-if="block.url && block.url.includes('<iframe')"
              v-html="block.url"
            ></div>

            <div v-else-if="block.url">
              <iframe v-if="block.source_type === 'url' || block.type === 'iframe'" :src="block.url" class="aspect-video w-full rounded-lg border border-border" allowfullscreen></iframe>
              <a v-else :href="block.url" target="_blank" rel="noopener" class="text-primary underline">View Attachment</a>
            </div>
          </div>
        </div>
      </div>
    </article>

    <section v-if="relatedPosts.length > 0" class="mx-auto mt-20 max-w-6xl border-t border-border pt-12">
      <h3 class="mb-8 text-2xl font-bold">Related Articles</h3>
      <div class="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
        <PostCard v-for="rp in relatedPosts" :key="rp.id" :post="rp" />
      </div>
    </section>
  </div>
</template>

<style>
.post-content h2 { @apply mb-4 mt-8 text-3xl font-bold; }
.post-content h3 { @apply mb-4 mt-6 text-2xl font-bold; }
.post-content p  { @apply mb-6 text-lg leading-relaxed; }
.post-content ul,
.post-content ol { @apply mb-6 pl-8 text-lg; }
.post-content ul  { @apply list-disc; }
.post-content ol  { @apply list-decimal; }
.post-content img { @apply my-5 w-full rounded-lg; }
.post-content iframe { @apply my-5 aspect-video w-full rounded-lg border-none; }
</style>
