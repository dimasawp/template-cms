<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  variant?: 'primary' | 'success' | 'destructive' | 'warning' | 'indigo' | 'outline' | 'secondary'
  size?: 'sm' | 'md'
}>()

const variantClasses = {
  primary: 'bg-primary/10 text-primary border-primary/20',
  success: 'bg-green-500/10 text-green-600 dark:text-green-400 border-green-500/20',
  destructive: 'bg-red-500/10 text-red-600 dark:text-red-400 border-red-500/20',
  warning: 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20',
  indigo: 'bg-indigo-500/10 text-indigo-700 dark:text-indigo-400 border-indigo-500/20',
  secondary: 'bg-muted text-muted-foreground border-border/50',
  outline: 'bg-transparent text-foreground border-border',
}

const sizeClasses = {
  sm: 'px-2 py-0.5 text-[10px]',
  md: 'px-2.5 py-1 text-xs',
}

const classes = computed(() => {
  return [
    'inline-flex items-center font-bold rounded-full border transition-colors',
    variantClasses[props.variant || 'primary'],
    sizeClasses[props.size || 'md'],
  ]
})
</script>

<template>
  <span :class="classes">
    <slot />
  </span>
</template>
