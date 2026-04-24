<script setup>
import { cn } from '@/lib/utils'
defineProps(['class'])
</script>
<template>
  <div :class="cn('animate-pulse rounded-md bg-muted', $props.class)" />
</template>
