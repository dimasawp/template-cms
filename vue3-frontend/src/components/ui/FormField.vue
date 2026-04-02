<script setup lang="ts">
import Label from './Label.vue'

defineProps<{
  label?: string
  error?: string
  required?: boolean
  description?: string
  htmlFor?: string
}>()
</script>

<template>
  <div class="space-y-1.5 w-full">
    <div v-if="label" class="flex items-center justify-between">
      <Label :for="htmlFor">
        {{ label }}
        <span v-if="required" class="text-destructive ml-0.5">*</span>
      </Label>
      <slot name="label-right" />
    </div>
    
    <div class="relative">
      <slot />
    </div>

    <p v-if="description && !error" class="text-[11px] text-muted-foreground leading-snug">
      {{ description }}
    </p>
    
    <p v-if="error" class="text-xs font-medium text-destructive animate-in fade-in slide-in-from-top-1 duration-200">
      {{ error }}
    </p>
  </div>
</template>
