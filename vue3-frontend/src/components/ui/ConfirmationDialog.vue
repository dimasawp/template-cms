<script setup>
import { AlertTriangle, AlertCircle, Info } from 'lucide-vue-next'
import Button from './Button.vue'
import Dialog from './Dialog.vue'

const props = defineProps(['open', 'title', 'message', 'variant', 'confirmLabel', 'cancelLabel', 'loading'])

defineEmits(['confirm', 'cancel'])

const variantIcons = {
  default: Info,
  destructive: AlertTriangle,
  warning: AlertTriangle,
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
    :open="props.open" 
    :title="props.title" 
    maxWidth="max-w-sm" 
    @close="$emit('cancel')"
  >
    <div class="flex flex-col items-center text-center py-2 px-1">
      <!-- Icon Container -->
      <div :class="['p-4 rounded-2xl border mb-6 transition-all scale-110 shadow-sm', iconColors[props.variant || 'default']]">
        <component :is="variantIcons[props.variant || 'default']" class="w-8 h-8" />
      </div>
      
      <!-- Content -->
      <p class="text-[14px] text-muted-foreground leading-relaxed font-medium px-2">
        {{ props.message }}
      </p>
    </div>

    <template #footer>
      <div class="grid grid-cols-2 gap-3 w-full capitalize">
        <Button 
          variant="outline" 
          @click="$emit('cancel')"
          :disabled="props.loading"
          class="rounded-xl font-bold h-11"
        >
          {{ props.cancelLabel || 'Batal' }}
        </Button>
        <Button 
          :variant="props.variant === 'destructive' ? 'destructive' : 'default'" 
          @click="$emit('confirm')"
          :loading="props.loading"
          class="rounded-xl font-bold h-11"
          :class="props.variant === 'destructive' ? 'shadow-lg shadow-rose-500/20' : 'shadow-lg shadow-primary/20'"
        >
          {{ props.confirmLabel || 'Ya, Lanjutkan' }}
        </Button>
      </div>
    </template>
  </Dialog>
</template>
