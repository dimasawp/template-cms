<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

const props = defineProps({
  post: {
    type: Object,
    required: true
  }
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
  <RouterLink :to="{ name: 'post-detail', params: { slug: post.slug } }" class="post-card animate-fade-in glass">
    <div class="post-thumbnail">
      <img :src="getImageUrl(post.thumbnail)" :alt="post.title" loading="lazy" />
    </div>
    <div class="post-content">
      <div class="post-meta">
        <span class="post-category" v-if="post.category">Category ID: {{ post.category }}</span>
        <div class="post-meta-right">
          <span v-if="post.author" class="post-author">By {{ post.author.full_name || post.author.username }} &bull; </span>
          <span class="post-date">{{ formattedDate }}</span>
        </div>
      </div>
      <h3 class="post-title">{{ post.title }}</h3>
    </div>
  </RouterLink>
</template>

<style scoped>
.post-card {
  display: flex;
  flex-direction: column;
  border-radius: var(--radius);
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  text-decoration: none;
  color: inherit;
  height: 100%;
}

.post-card:hover {
  transform: translateY(-8px);
  box-shadow: var(--shadow-lg);
  border-color: var(--color-primary);
}

.post-thumbnail {
  width: 100%;
  aspect-ratio: 16 / 10;
  overflow: hidden;
  background-color: var(--color-border);
}

.post-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.6s ease;
}

.post-card:hover .post-thumbnail img {
  transform: scale(1.05);
}

.post-content {
  padding: 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.post-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-size: 0.85rem;
}

.post-category {
  color: var(--color-primary);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.post-date, .post-author {
  color: var(--color-text-muted);
}

.post-meta-right {
  display: flex;
  gap: 4px;
}

.post-title {
  font-size: 1.25rem;
  font-weight: 700;
  line-height: 1.4;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
