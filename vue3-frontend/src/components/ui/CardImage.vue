<script setup lang="ts">
defineProps<{ title: string; description?: string; image: string; class?: string }>()
</script>
<template>
  <div :class="['rounded-lg border bg-card text-card-foreground shadow-sm overflow-hidden', $props.class]">
    <img :src="image" :alt="title" class="w-full h-48 object-cover" />
    <div class="p-4">
      <h3 class="font-semibold">{{ title }}</h3>
      <p v-if="description" class="mt-1 text-sm text-muted-foreground">{{ description }}</p>
      <slot />
    </div>
  </div>
</template>
