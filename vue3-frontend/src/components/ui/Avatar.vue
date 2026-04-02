<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  src?: string | null
  name?: string | null
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  className?: string
}>()

const sizeClasses = {
  xs: 'h-6 w-6 text-[10px]',
  sm: 'h-8 w-8 text-xs',
  md: 'h-10 w-10 text-sm',
  lg: 'h-12 w-12 text-base',
  xl: 'h-20 w-20 text-xl',
}

const initials = computed(() => {
  if (!props.name) return '?'
  const parts = props.name.trim().split(' ')
  if (parts.length === 1) return parts[0].charAt(0).toUpperCase()
  return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase()
})

const bgColor = computed(() => {
  if (!props.name) return 'bg-gray-500'
  const colors = [
    'bg-red-500', 'bg-blue-500', 'bg-green-500', 'bg-yellow-500', 
    'bg-purple-500', 'bg-pink-500', 'bg-indigo-500', 'bg-orange-500'
  ]
  let hash = 0
  for (let i = 0; i < props.name.length; i++) {
    hash = props.name.charCodeAt(i) + ((hash << 5) - hash)
  }
  return colors[Math.abs(hash) % colors.length]
})

const fullUrl = computed(() => {
  if (!props.src) return null
  if (props.src.startsWith('http')) return props.src
  // Assuming backend serves files from /storage
  const baseUrl = import.meta.env.VITE_API_BASE_URL?.replace('/api/v1', '') || 'http://localhost:8000'
  return `${baseUrl}/${props.src}`
})
</script>

<template>
  <div 
    :class="[
      'flex shrink-0 items-center justify-center rounded-full overflow-hidden font-bold text-white shadow-sm',
      sizeClasses[props.size || 'md'],
      !fullUrl ? bgColor : '',
      props.className
    ]"
  >
    <img 
      v-if="fullUrl" 
      :src="fullUrl" 
      :alt="props.name || 'Avatar'" 
      class="h-full w-full object-cover"
    />
    <span v-else>{{ initials }}</span>
  </div>
</template>
