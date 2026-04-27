<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { onClickOutside } from '@vueuse/core'

const props = defineProps({
  align: { type: String, default: 'right' },
  width: { type: String, default: 'w-72' }
})

const isOpen = ref(false)
const containerRef = ref(null)

const close = () => {
  isOpen.value = false
}

const toggle = () => {
  isOpen.value = !isOpen.value
}

onClickOutside(containerRef, () => {
  isOpen.value = false
})

const handleEsc = (e) => {
  if (e.key === 'Escape') {
    isOpen.value = false
  }
}

onMounted(() => window.addEventListener('keydown', handleEsc))
onUnmounted(() => window.removeEventListener('keydown', handleEsc))

defineExpose({ close, open: () => isOpen.value = true, toggle })
</script>

<template>
  <div class="relative" ref="containerRef">
    <div @click="toggle" class="cursor-pointer">
      <slot name="trigger" :is-open="isOpen" />
    </div>

    <Transition name="popover">
      <div 
        v-show="isOpen"
        :class="[
          'absolute top-full mt-2 bg-popover rounded-xl shadow-xl border border-border p-4 z-50 overflow-y-auto max-h-[80vh] custom-scrollbar',
          props.align === 'right' ? 'right-0' : 'left-0',
          props.width
        ]"
      >
        <slot :close="close" />
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.popover-enter-active { animation: popIn 0.2s ease-out; }
.popover-leave-active { animation: popOut 0.15s ease-in; }

@keyframes popIn {
  from { opacity: 0; transform: translateY(-10px) scale(0.95); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}
@keyframes popOut {
  from { opacity: 1; transform: translateY(0) scale(1); }
  to { opacity: 0; transform: translateY(-10px) scale(0.95); }
}
</style>
