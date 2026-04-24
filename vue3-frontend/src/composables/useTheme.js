import { ref, watch } from 'vue'

// Synchronously read initial state so watch doesn't overwrite it on mount
const saved = localStorage.getItem('theme')
const initialDark = saved ? saved === 'dark' : window.matchMedia('(prefers-color-scheme: dark)').matches
const isDark = ref(initialDark)

function applyTheme(dark) {
  const root = document.documentElement
  root.classList.remove('light', 'dark')
  root.classList.add(dark ? 'dark' : 'light')
}

export function initTheme() {
  applyTheme(isDark.value)
}

// Watch for changes and update localStorage + DOM
watch(isDark, (newVal) => {
  applyTheme(newVal)
  localStorage.setItem('theme', newVal ? 'dark' : 'light')
}, { immediate: true })

export function useTheme() {
  const toggleTheme = () => {
    isDark.value = !isDark.value
  }

  return { isDark, toggleTheme }
}
