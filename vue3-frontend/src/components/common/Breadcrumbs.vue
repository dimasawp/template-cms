<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { ChevronRight, Home } from 'lucide-vue-next'

const route = useRoute()

const breadcrumbs = computed(() => {
  if (route.meta.breadcrumbs) {
    return route.meta.breadcrumbs.map((bc, index, arr) => ({
      ...bc,
      active: index === arr.length - 1
    }))
  }

  // Get all matched routes that have a name or specific title
  const matched = route.matched.filter(m => {
    // Skip the root layout if it doesn't have a specific title/name we want to show
    if (m.path === '/') return false
    return true
  })
  
  return matched.map((m, index) => {
    // 1. Priority: meta.title
    // 2. Secondary: name
    // 3. Fallback: path segment
    let label = m.meta.title || m.name || m.path.split('/').filter(Boolean).pop() || 'Home'
    
    // Formatting: kebab-case to Title Case
    if (typeof label === 'string') {
      label = label.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    }

    // Special override for dashboard to avoid double "Dashboard / Dashboard"
    if (m.name === 'dashboard') return null

    return {
      label,
      path: m.path,
      active: index === matched.length - 1
    }
  }).filter(Boolean)
})
</script>

<template>
  <nav 
    v-if="route.name !== 'dashboard' && breadcrumbs.length > 0" 
    class="flex items-center space-x-2 text-[11px] font-medium text-muted-foreground/80 mb-4 animate-in fade-in slide-in-from-left-1 duration-500"
  >
    <router-link 
      to="/dashboard" 
      class="hover:text-primary transition-colors flex items-center gap-1 group"
    >
      <Home class="w-3.5 h-3.5 group-hover:scale-110 transition-transform" />
      <span>Dashboard</span>
    </router-link>
    
    <div v-for="(bc, index) in breadcrumbs" :key="index" class="flex items-center space-x-2">
      <ChevronRight class="w-3 h-3 text-muted-foreground/30" />
      <router-link 
        v-if="!bc.active" 
        :to="bc.path" 
        class="hover:text-primary transition-colors"
      >
        {{ bc.label }}
      </router-link>
      <span v-else class="text-foreground font-bold">{{ bc.label }}</span>
    </div>
  </nav>
</template>
