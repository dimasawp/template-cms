<script setup>
import { ref, onMounted, provide } from 'vue'
import { RouterView, RouterLink } from 'vue-router'
import { useSettingsStore } from '@/stores/settings'
import { useCategoriesStore } from '@/stores/categories'
import { storeToRefs } from 'pinia'

const settings = useSettingsStore()
const categories = useCategoriesStore()
const { siteName } = storeToRefs(settings)
const { mapById } = storeToRefs(categories)

provide('categoriesMap', mapById)

const isDark = ref(false)

function toggleDark() {
  isDark.value = !isDark.value
  document.documentElement.classList.toggle('dark', isDark.value)
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}

onMounted(async () => {
  const saved = localStorage.getItem('theme')
  if (saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    isDark.value = true
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }

  await Promise.all([settings.fetch(), categories.fetch()])
})

</script>

<template>
  <header class="sticky top-0 z-50 flex items-center justify-between border-b border-border bg-background/85 px-5 py-3.5 shadow-sm backdrop-blur-md">
    <div class="mx-auto flex w-full max-w-6xl items-center justify-between px-5">
      <RouterLink to="/" class="bg-gradient-to-r from-primary to-pink-500 bg-clip-text text-2xl font-bold text-transparent">
        {{ siteName }}
      </RouterLink>
      <nav class="flex items-center gap-5">
        <RouterLink to="/" class="font-medium">Home</RouterLink>
        <a href="http://localhost:5173" target="_blank" class="font-medium text-muted-foreground">Admin Panel &rarr;</a>
        <button @click="toggleDark" class="flex items-center justify-center rounded-full bg-none p-1.5 text-foreground" aria-label="Toggle theme">
          <svg v-if="!isDark" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>
        </button>
      </nav>
    </div>
  </header>

  <main class="min-h-[calc(100vh-140px)]">
    <RouterView />
  </main>

  <footer class="mt-10 border-t border-border py-10 text-center text-muted-foreground">
    <div class="mx-auto max-w-6xl px-5">
      &copy; {{ new Date().getFullYear() }} {{ siteName }}. Built with Tailwind CSS &amp; Pinia.
    </div>
  </footer>
</template>
