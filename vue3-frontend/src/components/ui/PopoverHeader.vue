<script setup>
import { X } from 'lucide-vue-next'

defineProps(['title'])

defineEmits(['close'])
</script>

<template>
  <div class="flex items-center justify-between mb-4 pb-2 border-b border-border">
    <span class="font-semibold text-foreground text-sm">{{ title }}</span>
    <button 
      @click="$emit('close')" 
      class="text-muted-foreground hover:text-foreground transition-colors p-1 rounded-md hover:bg-accent"
      type="button"
    >
      <X class="h-4 w-4" />
    </button>
  </div>
</template>
