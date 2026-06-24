<script setup>
import { ref, onMounted } from 'vue'
import { RouterView, RouterLink } from 'vue-router'

const isDark = ref(false)

const toggleTheme = () => {
  isDark.value = !isDark.value
  if (isDark.value) {
    document.documentElement.classList.add('dark')
    localStorage.setItem('theme', 'dark')
  } else {
    document.documentElement.classList.remove('dark')
    localStorage.setItem('theme', 'light')
  }
}

onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'dark' || (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    isDark.value = true
    document.documentElement.classList.add('dark')
  } else {
    isDark.value = false
    document.documentElement.classList.remove('dark')
  }
})
</script>

<template>
  <header class="navbar glass">
    <div class="container" style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
      <RouterLink to="/" class="navbar-brand">CMS Public</RouterLink>
      <nav style="display: flex; gap: 20px; align-items: center;">
        <RouterLink to="/" style="font-weight: 500;">Home</RouterLink>
        <a href="http://localhost:5173" target="_blank" style="font-weight: 500; color: var(--color-text-muted)">Admin Panel &rarr;</a>
        
        <button @click="toggleTheme" class="theme-toggle" aria-label="Toggle Theme" style="background: none; border: none; cursor: pointer; color: var(--color-text); display: flex; align-items: center; justify-content: center; padding: 6px; border-radius: 50%;">
          <svg v-if="!isDark" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>
        </button>
      </nav>
    </div>
  </header>

  <main style="min-height: calc(100vh - 140px);">
    <RouterView />
  </main>

  <footer style="text-align: center; padding: 40px 20px; color: var(--color-text-muted); border-top: 1px solid var(--color-border); margin-top: 40px;">
    <div class="container">
      &copy; {{ new Date().getFullYear() }} CMS Public Template. Built with Vue 3 & Vanilla CSS.
    </div>
  </footer>
</template>
