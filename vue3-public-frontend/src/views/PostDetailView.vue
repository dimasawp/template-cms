<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { publicService } from '@/services/api'

const route = useRoute()
const post = ref(null)
const loading = ref(true)

const fetchPostDetail = async () => {
  try {
    const res = await publicService.getPostDetail(route.params.slug)
    post.value = res.data.data
  } catch (error) {
    console.error('Failed to fetch post detail', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchPostDetail()
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
</script>

<template>
  <div class="container" style="padding-top: 40px; padding-bottom: 80px;">
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
    </div>
    
    <div v-else-if="!post" class="empty-state glass">
      <h2>Post not found</h2>
      <p>The post you are looking for does not exist or has been removed.</p>
      <RouterLink to="/" class="btn" style="margin-top: 20px;">Return Home</RouterLink>
    </div>

    <article v-else class="post-detail animate-fade-in">
      <!-- Header -->
      <header class="post-header" style="margin-bottom: 30px; text-align: center;">
        <div style="margin-bottom: 15px;">
          <span v-if="post.category" style="background: var(--color-primary); color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 500;">
            Category ID: {{ post.category }}
          </span>
        </div>
        <h1 class="post-title" style="font-size: 2.5rem; margin-bottom: 10px;">{{ post.title }}</h1>
        <div class="post-meta" style="color: var(--color-text-muted); font-size: 0.95rem;">
          <span v-if="post.author">By {{ post.author.full_name || post.author.username }} &bull; </span>
          <span>Published on {{ formattedDate }}</span>
        </div>
      </header>

      <!-- Thumbnail -->
      <div class="post-hero-image" v-if="post.thumbnail">
        <img :src="getImageUrl(post.thumbnail)" :alt="post.title" />
      </div>

      <!-- Main Content (Jodit HTML) -->
      <!-- SECURITY WARNING: v-html is used because we trust the HTML from our CMS. -->
      <!-- In a fully public system, you might want to sanitize this HTML using DOMPurify. -->
      <div class="post-content glass" style="padding: 40px; margin-bottom: 40px;" v-html="post.content">
      </div>

      <!-- Additional Contents (Iframes, etc) -->
      <div v-if="post.additional_contents && post.additional_contents.length > 0" class="additional-contents">
        <h3 style="font-size: 1.5rem; margin-bottom: 20px; font-weight: 700;">Additional Media</h3>
        
        <div class="blocks-grid">
          <div 
            v-for="(block, index) in post.additional_contents" 
            :key="index"
            class="content-block glass"
          >
            <!-- Render Block Title if exists -->
            <h4 v-if="block.title" class="block-title">{{ block.title }}</h4>

            <!-- Check if the block content contains an iframe. We render it securely. -->
            <div 
              v-if="block.url && block.url.includes('<iframe')" 
              class="iframe-wrapper"
              v-html="block.url"
            ></div>
            
            <!-- Fallback for other block contents -->
            <div v-else-if="block.url" class="html-wrapper">
              <iframe v-if="block.source_type === 'url' || block.type === 'iframe'" :src="block.url" allowfullscreen></iframe>
              <a v-else :href="block.url" target="_blank" rel="noopener">View Attachment</a>
            </div>
          </div>
        </div>
      </div>
      
    </article>
  </div>
</template>

<style scoped>
.post-detail {
  max-width: 800px;
  margin: 0 auto;
}

.post-header {
  text-align: center;
  margin-bottom: 40px;
}

.post-title {
  font-size: clamp(2rem, 4vw, 3.5rem);
  font-weight: 800;
  line-height: 1.2;
  margin-bottom: 16px;
  color: var(--color-text);
}

.post-meta {
  color: var(--color-text-muted);
  font-size: 1rem;
}

.post-hero-image {
  width: 100%;
  aspect-ratio: 16 / 9;
  border-radius: var(--radius);
  overflow: hidden;
  margin-bottom: 40px;
  box-shadow: var(--shadow-lg);
}

.post-hero-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Post Content overrides */
:deep(.post-content h2) {
  font-size: 2rem;
  margin-top: 2rem;
  margin-bottom: 1rem;
}
:deep(.post-content h3) {
  font-size: 1.5rem;
  margin-top: 1.5rem;
  margin-bottom: 1rem;
}
:deep(.post-content p) {
  font-size: 1.125rem;
  line-height: 1.8;
  margin-bottom: 1.5rem;
  color: var(--color-text);
}
:deep(.post-content ul), :deep(.post-content ol) {
  margin-bottom: 1.5rem;
  padding-left: 2rem;
  font-size: 1.125rem;
}

/* Additional Contents */
.additional-contents {
  margin-top: 60px;
}

.blocks-grid {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.content-block {
  padding: 30px;
  border-radius: var(--radius);
}

.block-title {
  font-size: 1.25rem;
  margin-bottom: 15px;
  font-weight: 600;
  color: var(--color-primary);
}

/* Make iframes responsive */
:deep(.iframe-wrapper iframe), :deep(.html-wrapper iframe) {
  width: 100%;
  height: auto;
  aspect-ratio: 16 / 9;
  border-radius: var(--radius);
  border: 1px solid var(--color-border);
}

.loading-state, .empty-state {
  padding: 80px 20px;
  text-align: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
