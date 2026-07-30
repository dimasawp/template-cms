<script setup>
import { ref, onMounted } from 'vue'
import { publicService } from '@/services/api'
import { useCategoriesStore } from '@/stores/categories'
import { storeToRefs } from 'pinia'
import PostCard from '@/components/PostCard.vue'
import CategoryNav from '@/components/CategoryNav.vue'
import SkeletonLoader from '@/components/ui/SkeletonLoader.vue'

const categories = useCategoriesStore()
const { items } = storeToRefs(categories)

const posts = ref([])
const loading = ref(true)
const page = ref(1)
const totalPages = ref(1)
const perPage = 12
const activeCategorySlug = ref(null)
const searchQuery = ref('')
const debounceTimer = ref(null)

const isSearching = ref(false)

async function loadPosts() {
  loading.value = true
  try {
    const params = { per_page: perPage, page: page.value }
    if (activeCategorySlug.value) {
      params.category_slug = activeCategorySlug.value
    }
    if (searchQuery.value.trim()) {
      params.search = searchQuery.value.trim()
    }
    const res = await publicService.getPosts(params)
    posts.value = res.data.data.items
    const pag = res.data.data.pagination
    totalPages.value = pag.total_pages
  } catch (error) {
    console.error('Failed to fetch posts', error)
  } finally {
    loading.value = false
  }
}

function onCategorySelect(slug) {
  activeCategorySlug.value = slug
  page.value = 1
  loadPosts()
}

function goToPage(p) {
  page.value = p
  loadPosts()
}

function onSearchInput(e) {
  const val = e.target.value
  isSearching.value = val.trim().length > 0
  clearTimeout(debounceTimer.value)
  debounceTimer.value = setTimeout(() => {
    searchQuery.value = val
    page.value = 1
    loadPosts()
  }, 300)
}

function clearSearch() {
  searchQuery.value = ''
  isSearching.value = false
  page.value = 1
  loadPosts()
}

onMounted(async () => {
  await categories.fetch()
  loadPosts()
  document.title = 'Home - CMS Public'
})
</script>

<template>
  <div>
    <section class="relative overflow-hidden border-b border-border bg-background px-5 py-24 text-center">
      <div class="relative z-10 mx-auto max-w-3xl">
        <h1 class="bg-gradient-to-r from-foreground to-primary bg-clip-text text-[clamp(2.5rem,5vw,4.5rem)] font-extrabold leading-none tracking-tight text-transparent">
          Discover Amazing Content.
        </h1>
        <p class="mx-auto mt-5 max-w-xl text-lg text-muted-foreground">
          Browse our latest articles and stay up to date.
        </p>
        <div class="relative mx-auto mt-8 max-w-xl">
          <input
            type="text"
            placeholder="Search articles..."
            class="w-full rounded-lg border border-border bg-background px-4 py-3 pl-10 text-foreground placeholder:text-muted-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
            :value="searchQuery"
            @input="onSearchInput"
          />
          <svg class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
          <button
            v-if="isSearching"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
            @click="clearSearch"
          >
            &times;
          </button>
        </div>
      </div>
      <div class="absolute -left-[10%] -top-[10%] h-[40vw] w-[40vw] animate-pulse rounded-full bg-primary/30 blur-3xl" />
      <div class="absolute -bottom-[20%] -right-[10%] h-[30vw] w-[30vw] animate-pulse rounded-full bg-pink-500/30 blur-3xl" />
    </section>

    <section class="mx-auto max-w-6xl px-5 py-16">
      <div class="mb-10 flex items-end justify-between">
        <div>
          <h2 class="text-4xl font-bold">
            {{ isSearching ? `Search: "${searchQuery}"` : 'Latest Posts' }}
          </h2>
          <p class="text-muted-foreground">
            {{ isSearching ? 'Showing results for your search.' : 'Read our most recent published articles.' }}
          </p>
        </div>
      </div>

      <CategoryNav
        v-if="!isSearching"
        :categories="items"
        :active-slug="activeCategorySlug"
        @select="onCategorySelect"
      />

      <div v-if="loading" class="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
        <div v-for="n in 6" :key="n" class="overflow-hidden rounded-lg border border-border">
          <SkeletonLoader class="aspect-[16/10] w-full !rounded-none" />
          <div class="space-y-3 p-5">
            <SkeletonLoader class="h-4 w-1/3" />
            <SkeletonLoader class="h-5 w-full" />
            <SkeletonLoader class="h-5 w-2/3" />
          </div>
        </div>
      </div>

      <div v-else-if="posts.length === 0" class="rounded-lg border border-border bg-background py-20 text-center text-muted-foreground">
        <h3 class="text-xl font-semibold">No posts found</h3>
        <p v-if="isSearching">No results for "{{ searchQuery }}". Try a different keyword.</p>
        <p v-else>There are no published posts in this category at the moment.</p>
        <button v-if="isSearching" class="mt-4 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground" @click="clearSearch">
          Reset search
        </button>
      </div>

      <div v-else>
        <div class="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
          <PostCard
            v-for="post in posts"
            :key="post.id"
            :post="post"
          />
        </div>

        <div v-if="totalPages > 1" class="mt-12 flex items-center justify-center gap-2">
          <button
            class="rounded-lg border border-border bg-background px-4 py-2 text-sm text-foreground transition-colors hover:border-primary hover:text-primary disabled:cursor-not-allowed disabled:opacity-40"
            :disabled="page <= 1"
            @click="goToPage(page - 1)"
          >
            &larr; Prev
          </button>
          <button
            v-for="p in totalPages"
            :key="p"
            class="rounded-lg border px-4 py-2 text-sm transition-colors"
            :class="p === page
              ? 'border-primary bg-primary text-primary-foreground'
              : 'border-border bg-background text-foreground hover:border-primary hover:text-primary'"
            @click="goToPage(p)"
          >
            {{ p }}
          </button>
          <button
            class="rounded-lg border border-border bg-background px-4 py-2 text-sm text-foreground transition-colors hover:border-primary hover:text-primary disabled:cursor-not-allowed disabled:opacity-40"
            :disabled="page >= totalPages"
            @click="goToPage(page + 1)"
          >
            Next &rarr;
          </button>
        </div>
      </div>
    </section>
  </div>
</template>
