<script setup lang="ts">
defineProps<{
  title: string
  value: string | number
  description?: string
  icon?: string
  trend?: 'up' | 'down' | 'neutral'
  trendValue?: string
}>()
</script>

<template>
  <div class="rounded-lg border bg-card text-card-foreground shadow-sm p-6">
    <div class="flex items-center justify-between">
      <p class="text-sm font-medium text-muted-foreground">{{ title }}</p>
      <slot name="icon" />
    </div>
    <div class="mt-2">
      <p class="text-2xl font-bold">{{ value }}</p>
      <p v-if="description || trendValue" class="mt-1 text-xs text-muted-foreground">
        <span v-if="trendValue" :class="{ 'text-green-600': trend === 'up', 'text-red-600': trend === 'down' }">{{ trendValue }}</span>
        {{ description }}
      </p>
    </div>
  </div>
</template>
