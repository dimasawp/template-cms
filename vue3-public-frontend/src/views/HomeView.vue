<script setup>
import { ref, onMounted } from 'vue'
import { publicService } from '@/services/api'
import PostCard from '@/components/PostCard.vue'

const posts = ref([])
const loading = ref(true)

const fetchPosts = async () => {
  try {
    const res = await publicService.getPosts({ per_page: 12 })
    posts.value = res.data.data.items
  } catch (error) {
    console.error('Failed to fetch posts', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchPosts()
})
</script>

<template>
  <div>
    <!-- Hero Section -->
    <section class="hero glass">
      <div class="container hero-content">
        <h1 class="hero-title animate-fade-in">Discover Amazing Content.</h1>
        <p class="hero-subtitle animate-fade-in" style="animation-delay: 0.1s">
          This is a reference public frontend built with Vue 3 and Vanilla CSS to showcase how to consume the CMS API.
        </p>
      </div>
      <!-- Decorative background blur -->
      <div class="hero-blob blob-1"></div>
      <div class="hero-blob blob-2"></div>
    </section>

    <!-- Posts Section -->
    <section class="container" style="padding: 60px 20px;">
      <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 40px;">
        <div>
          <h2 style="font-size: 2rem; font-weight: 700;">Latest Posts</h2>
          <p style="color: var(--color-text-muted)">Read our most recent published articles.</p>
        </div>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
      </div>
      
      <div v-else-if="posts.length === 0" class="empty-state glass">
        <h3>No posts found</h3>
        <p>There are no published posts at the moment.</p>
      </div>

      <div v-else class="post-grid">
        <PostCard 
          v-for="(post, index) in posts" 
          :key="post.id" 
          :post="post" 
          :style="`animation-delay: ${index * 0.1}s`"
        />
      </div>
    </section>
  </div>
</template>

<style scoped>
.hero {
  position: relative;
  padding: 100px 20px;
  text-align: center;
  overflow: hidden;
  border-bottom: 1px solid var(--color-border);
  border-left: none;
  border-right: none;
  border-top: none;
  border-radius: 0;
}

.hero-content {
  position: relative;
  z-index: 10;
  max-width: 800px;
}

.hero-title {
  font-size: clamp(2.5rem, 5vw, 4.5rem);
  font-weight: 800;
  letter-spacing: -0.02em;
  margin-bottom: 20px;
  background: linear-gradient(135deg, var(--color-text) 0%, var(--color-primary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-subtitle {
  font-size: 1.25rem;
  color: var(--color-text-muted);
  max-width: 600px;
  margin: 0 auto;
}

.hero-blob {
  position: absolute;
  filter: blur(80px);
  z-index: 0;
  opacity: 0.5;
  border-radius: 50%;
  animation: float 10s ease-in-out infinite alternate;
}

.blob-1 {
  top: -10%;
  left: -10%;
  width: 40vw;
  height: 40vw;
  background: var(--color-primary);
}

.blob-2 {
  bottom: -20%;
  right: -10%;
  width: 30vw;
  height: 30vw;
  background: #ec4899;
  animation-delay: -5s;
}

@keyframes float {
  0% { transform: translate(0, 0) scale(1); }
  100% { transform: translate(30px, -50px) scale(1.1); }
}

.post-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 30px;
}

.loading-state, .empty-state {
  padding: 80px 20px;
  text-align: center;
}

.empty-state {
  border-radius: var(--radius);
  color: var(--color-text-muted);
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
