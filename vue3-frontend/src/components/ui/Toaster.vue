<script setup>
import { useToast } from '@/composables/useToast'
import { X } from 'lucide-vue-next'

const { toasts, dismiss } = useToast()

function variantClass(t) {
  if (t.variant === 'destructive') return 'border-red-500 bg-red-50 dark:bg-red-950 text-red-800 dark:text-red-200'
  if (t.variant === 'success') return 'border-green-500 bg-green-50 dark:bg-green-950 text-green-800 dark:text-green-200'
  return 'border-border bg-background text-foreground'
}
</script>

<template>
  <div class="fixed bottom-4 right-4 z-50 flex flex-col gap-2 w-80">
    <TransitionGroup name="toast">
      <div v-for="t in toasts" :key="t.id" :class="['rounded-lg border p-4 shadow-lg', variantClass(t)]">
        <div class="flex items-start justify-between">
          <div>
            <p class="font-semibold text-sm">{{ t.title }}</p>
            <p v-if="t.description" class="mt-1 text-xs opacity-80">{{ t.description }}</p>
          </div>
          <button @click="dismiss(t.id)" class="ml-2 opacity-60 hover:opacity-100">
            <X class="h-4 w-4" />
          </button>
        </div>
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.toast-enter-active { animation: slideIn 0.3s ease-out; }
.toast-leave-active { animation: slideOut 0.2s ease-in; }
@keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
@keyframes slideOut { from { opacity: 1; } to { opacity: 0; transform: translateX(100%); } }
</style>
