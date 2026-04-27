<script setup>
defineProps({
  icon: { type: Object, default: null },
  title: { type: String, default: 'Data Tidak Ditemukan' },
  description: { type: String, default: 'Coba ubah kriteria pencarian atau filter Anda.' }
})
</script>

<template>
  <div class="flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-border py-20 text-muted-foreground bg-muted/5">
    <div v-if="icon" class="bg-muted p-5 rounded-full mb-5 text-muted-foreground/40 shadow-inner">
      <component :is="icon" class="h-10 w-10" />
    </div>
    <h3 class="text-lg font-bold text-foreground mb-1">{{ title }}</h3>
    <p v-if="description" class="max-w-xs text-center text-sm opacity-70 leading-relaxed px-4">
      {{ description }}
    </p>
    <div v-if="$slots.actions" class="mt-6">
      <slot name="actions" />
    </div>
  </div>
</template>
