<script setup lang="ts">
import { AlertTriangle, AlertCircle, Info } from 'lucide-vue-next'
import Button from './Button.vue'
import Dialog from './Dialog.vue'

defineProps<{
  open: boolean
  title: string
  message: string
  variant?: 'default' | 'destructive' | 'warning' | 'info'
  confirmLabel?: string
  cancelLabel?: string
  loading?: boolean
}>()

defineEmits<{ confirm: []; cancel: [] }>()

const variantIcons = {
  default: Info,
  destructive: AlertTriangle,
  warning: AlertCircle,
  info: Info
}

const iconColors = {
  default: 'text-primary bg-primary/10 border-primary/20',
  destructive: 'text-rose-500 bg-rose-500/10 border-rose-500/20',
  warning: 'text-amber-500 bg-amber-500/10 border-amber-500/20',
  info: 'text-blue-500 bg-blue-500/10 border-blue-500/20'
}
</script>

<template>
  <Dialog 
    :open="open" 
    :title="title" 
    maxWidth="max-w-sm" 
    @close="$emit('cancel')"
  >
    <div class="flex flex-col items-center text-center py-2 px-1">
      <!-- Icon Container -->
      <div :class="['p-4 rounded-2xl border mb-6 transition-all scale-110 shadow-sm', iconColors[variant || 'default']]">
        <component :is="variantIcons[variant || 'default']" class="w-8 h-8" />
      </div>
      
      <!-- Content -->
      <p class="text-[14px] text-muted-foreground leading-relaxed font-medium px-2">
        {{ message }}
      </p>
    </div>

    <template #footer>
      <div class="grid grid-cols-2 gap-3 w-full capitalize">
        <Button 
          variant="outline" 
          @click="$emit('cancel')"
          :disabled="loading"
          class="rounded-xl font-bold h-11"
        >
          {{ cancelLabel || 'Batal' }}
        </Button>
        <Button 
          :variant="variant === 'destructive' ? 'destructive' : 'default'" 
          @click="$emit('confirm')"
          :loading="loading"
          class="rounded-xl font-bold h-11"
          :class="variant === 'destructive' ? 'shadow-lg shadow-rose-500/20' : 'shadow-lg shadow-primary/20'"
        >
          {{ confirmLabel || 'Ya, Lanjutkan' }}
        </Button>
      </div>
    </template>
  </Dialog>
</template>
