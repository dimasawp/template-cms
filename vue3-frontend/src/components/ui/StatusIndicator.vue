<script setup>
import { computed } from 'vue'

const props = defineProps(['active', 'label', 'showDot'])

const statusLabel = computed(() => props.label || (props.active ? 'Active' : 'Inactive'))

const dotClasses = computed(() => {
  return [
    'h-1.5 w-1.5 rounded-full mr-2 shrink-0',
    props.active 
      ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]' 
      : 'bg-muted-foreground shadow-[0_0_8px_rgba(148,163,184,0.1)]'
  ]
})

const textClasses = computed(() => {
  return [
    'text-xs font-bold transition-colors inline-flex items-center',
    props.active ? 'text-green-600 dark:text-green-400' : 'text-muted-foreground'
  ]
})
</script>

<template>
  <div :class="textClasses">
    <div v-if="showDot !== false" :class="dotClasses" />
    <span>{{ statusLabel }}</span>
  </div>
</template>
