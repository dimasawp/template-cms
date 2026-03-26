import { ref } from 'vue'

export interface Toast {
  id: string
  title: string
  description?: string
  variant?: 'default' | 'destructive' | 'success'
}

const toasts = ref<Toast[]>([])

export function useToast() {
  function toast(options: Omit<Toast, 'id'>) {
    const id = Math.random().toString(36).substring(2, 9)
    toasts.value.push({ ...options, id })
    setTimeout(() => dismiss(id), 5000)
    return id
  }

  function dismiss(id: string) {
    toasts.value = toasts.value.filter((t) => t.id !== id)
  }

  return { toasts, toast, dismiss }
}
