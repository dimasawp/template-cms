<script setup lang="ts">
defineProps<{ currentPage: number; totalPages: number }>()
defineEmits<{ 'page-change': [page: number] }>()
</script>
<template>
  <div v-if="totalPages > 1" class="flex items-center gap-1">
    <button
      :disabled="currentPage <= 1"
      class="px-3 py-1 rounded text-sm border border-input hover:bg-accent disabled:opacity-50"
      @click="$emit('page-change', currentPage - 1)"
    >
      ←
    </button>
    <template v-for="p in totalPages" :key="p">
      <button
        v-if="p === 1 || p === totalPages || (p >= currentPage - 1 && p <= currentPage + 1)"
        :class="[
          'px-3 py-1 rounded text-sm border',
          p === currentPage ? 'bg-primary text-primary-foreground' : 'border-input hover:bg-accent'
        ]"
        @click="$emit('page-change', p)"
      >
        {{ p }}
      </button>
      <span v-else-if="p === currentPage - 2 || p === currentPage + 2" class="px-1 text-muted-foreground">…</span>
    </template>
    <button
      :disabled="currentPage >= totalPages"
      class="px-3 py-1 rounded text-sm border border-input hover:bg-accent disabled:opacity-50"
      @click="$emit('page-change', currentPage + 1)"
    >
      →
    </button>
  </div>
</template>
