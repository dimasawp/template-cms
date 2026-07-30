<script setup>
import { computed } from 'vue'

const props = defineProps({
  categories: { type: Array, default: () => [] },
  activeSlug: { type: String, default: null },
})

const emit = defineEmits(['select'])

const menuCategories = computed(() =>
  props.categories.filter((c) => c.is_menu)
)

function onSelect(slug) {
  emit('select', slug === props.activeSlug ? null : slug)
}
</script>

<template>
  <div class="mb-6 flex flex-wrap gap-2">
    <button
      class="rounded-full border px-4 py-1.5 text-sm font-medium transition-colors"
      :class="!activeSlug
        ? 'border-primary bg-primary text-primary-foreground'
        : 'border-border bg-background text-muted-foreground hover:border-primary hover:text-primary'"
      @click="onSelect(null)"
    >
      All
    </button>
    <button
      v-for="c in menuCategories"
      :key="c.id"
      class="rounded-full border px-4 py-1.5 text-sm font-medium transition-colors"
      :class="activeSlug === c.slug
        ? 'border-primary bg-primary text-primary-foreground'
        : 'border-border bg-background text-muted-foreground hover:border-primary hover:text-primary'"
      @click="onSelect(c.slug)"
    >
      {{ c.name }}
    </button>
  </div>
</template>
