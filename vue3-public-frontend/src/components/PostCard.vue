<script setup>
import { computed, inject } from 'vue'
import { RouterLink } from 'vue-router'

const props = defineProps({
  post: { type: Object, required: true }
})

const categoriesMap = inject('categoriesMap', {})
const categoryName = computed(() => {
  const c = categoriesMap[props.post.category]
  return c ? c.name : null
})

const formattedDate = computed(() => {
  if (!props.post.created_at) return ''
  const date = new Date(props.post.created_at)
  return new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', year: 'numeric' }).format(date)
})

const getImageUrl = (path) => {
  if (!path) return 'https://via.placeholder.com/600x400?text=No+Image'
  if (path.startsWith('http')) return path
  const baseUrl = import.meta.env.VITE_API_BASE_URL?.replace('/api/v1', '') || 'http://localhost:8000'
  const cleanPath = path.startsWith('/') ? path.substring(1) : path
  const cleanBase = baseUrl.endsWith('/') ? baseUrl : baseUrl + '/'
  return `${cleanBase}${cleanPath}`
}
</script>

<template>
  <RouterLink
    :to="{ name: 'post-detail', params: { slug: post.slug } }"
    class="group flex h-full flex-col overflow-hidden rounded-lg border border-border bg-background transition-all duration-300 hover:-translate-y-2 hover:border-primary hover:shadow-lg"
  >
    <div class="aspect-[16/10] w-full overflow-hidden bg-border">
      <img
        :src="getImageUrl(post.thumbnail)"
        :alt="post.title"
        loading="lazy"
        class="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
      />
    </div>
    <div class="flex flex-1 flex-col p-5">
      <div class="mb-3 flex items-center justify-between text-sm">
        <span v-if="categoryName" class="font-semibold uppercase tracking-wider text-primary">{{ categoryName }}</span>
        <span class="text-muted-foreground">{{ formattedDate }}</span>
      </div>
      <h3 class="line-clamp-3 text-lg font-bold">{{ post.title }}</h3>
      <p v-if="post.content" class="mt-2 line-clamp-2 text-sm text-muted-foreground">{{ post.content.replace(/<[^>]*>/g, '').substring(0, 150) }}</p>
    </div>
  </RouterLink>
</template>
