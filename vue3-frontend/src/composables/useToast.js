import { ref } from 'vue'

const toasts = ref([])

export function useToast() {
  function toast(options) {
    const id = Math.random().toString(36).substring(2, 9)
    toasts.value.push({ ...options, id })
    setTimeout(() => dismiss(id), 5000)
    return id
  }

  function dismiss(id) {
    toasts.value = toasts.value.filter((t) => t.id !== id)
  }

  return { toasts, toast, dismiss }
}
