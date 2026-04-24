<script setup>
import { onMounted, onUnmounted } from 'vue'
import { X } from 'lucide-vue-next'

const props = defineProps(['maxWidth'])

const emit = defineEmits()

const handleEsc = (e) => {
  if (e.key === 'Escape' && props.open) {
    emit('close')
  }
}

onMounted(() => window.addEventListener('keydown', handleEsc))
onUnmounted(() => window.removeEventListener('keydown', handleEsc))
</script>

<template>
  <Teleport to="body">
    <Transition name="dialog">
      <div v-if="open" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <!-- Overlay (Transparent) -->
        <div class="fixed inset-0" @click="$emit('close')" />
        
        <!-- Content -->
        <div 
          :class="['relative z-10 w-full bg-background rounded-xl border border-border shadow-2xl flex flex-col', maxWidth || 'max-w-md']" 
          @click.stop
        >
          <!-- Header -->
          <div class="flex items-center justify-between px-6 py-4 border-b border-border">
            <h3 class="text-lg font-bold text-foreground">{{ title }}</h3>
            <button 
              @click="$emit('close')" 
              class="p-2 -mr-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-accent transition-all"
              title="Close (Esc)"
            >
              <X class="h-5 w-5" />
            </button>
          </div>
          
          <!-- Body -->
          <div class="px-6 py-4 overflow-y-auto max-h-[80vh]">
            <slot />
          </div>
          
          <!-- Footer -->
          <div v-if="$slots.footer" class="px-6 py-4 border-t border-border bg-muted/30 rounded-b-xl flex justify-end gap-2">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.dialog-enter-active { animation: fadeIn 0.2s ease-out; }
.dialog-leave-active { animation: fadeOut 0.15s ease-in; }

@keyframes fadeIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

@keyframes fadeOut {
  from { opacity: 1; transform: scale(1); }
  to { opacity: 0; transform: scale(0.95); }
}
</style>
