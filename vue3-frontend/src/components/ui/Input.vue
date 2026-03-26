<script setup lang="ts">
import { ref, computed } from 'vue'
import { cn } from '@/lib/utils'
import { Eye, EyeOff } from 'lucide-vue-next'

const props = defineProps<{ class?: string; type?: string; modelValue?: string | number; placeholder?: string; disabled?: boolean }>()
defineEmits<{ 'update:modelValue': [value: string | number] }>()

const showPassword = ref(false)

const inputType = computed(() => {
  if (props.type === 'password') {
    return showPassword.value ? 'text' : 'password'
  }
  return props.type || 'text'
})
</script>

<template>
  <div class="relative w-full">
    <input
      :type="inputType"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :class="cn(
        'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50',
        props.type === 'password' && 'pr-10',
        props.class
      )"
      @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
    />
    <button 
      v-if="props.type === 'password'"
      type="button" 
      @click="showPassword = !showPassword" 
      class="absolute right-0 top-0 h-full flex items-center justify-center w-10 text-muted-foreground hover:text-foreground transition-colors"
      tabindex="-1"
    >
      <Eye v-if="!showPassword" class="h-4 w-4" />
      <EyeOff v-else class="h-4 w-4" />
    </button>
  </div>
</template>
