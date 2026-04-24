<script setup>
import { onMounted, watch } from 'vue'
import { useSettingsStore } from '@/stores/settings'

const settings = useSettingsStore()

onMounted(() => {
  settings.fetchSettings()
})

// Sync Browser Title
watch(() => settings.siteName, (newName) => {
  document.title = newName
}, { immediate: true })
</script>

<template>
  <router-view />
</template>
