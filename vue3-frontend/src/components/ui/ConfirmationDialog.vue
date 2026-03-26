<script setup lang="ts">
import Button from './Button.vue'

defineProps<{
  open: boolean
  title: string
  message: string
  variant?: 'default' | 'destructive'
  confirmLabel?: string
  cancelLabel?: string
}>()

defineEmits<{ confirm: []; cancel: [] }>()
</script>

<template>
  <Teleport to="body">
    <Transition name="dialog">
      <div v-if="open" class="fixed inset-0 z-50 flex items-center justify-center">
        <div class="fixed inset-0 bg-black/50" @click="$emit('cancel')" />
        <div class="relative z-10 w-full max-w-md rounded-lg bg-background p-6 shadow-xl">
          <h3 class="text-lg font-semibold">{{ title }}</h3>
          <p class="mt-2 text-sm text-muted-foreground">{{ message }}</p>
          <div class="mt-6 flex justify-end gap-2">
            <Button variant="outline" @click="$emit('cancel')">{{ cancelLabel || 'Batal' }}</Button>
            <Button :variant="variant === 'destructive' ? 'destructive' : 'default'" @click="$emit('confirm')">
              {{ confirmLabel || 'Ya, Lanjutkan' }}
            </Button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.dialog-enter-active { animation: fadeIn 0.2s ease; }
.dialog-leave-active { animation: fadeOut 0.15s ease; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes fadeOut { from { opacity: 1; } to { opacity: 0; } }
</style>
