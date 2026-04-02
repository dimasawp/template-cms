import { ref } from 'vue'

export function useConfirmation() {
  const isOpen = ref(false)
  const title = ref('')
  const message = ref('')
  const variant = ref<'default' | 'destructive' | 'warning' | 'info'>('default')

  let _resolve: ((value: boolean) => void) | null = null

  function confirm(opts: { title: string; message: string; variant?: 'default' | 'destructive' | 'warning' | 'info' }): Promise<boolean> {
    title.value = opts.title
    message.value = opts.message
    variant.value = opts.variant || 'default'
    isOpen.value = true

    return new Promise((resolve) => { _resolve = resolve })
  }

  function onConfirm() {
    isOpen.value = false
    _resolve?.(true)
  }

  function onCancel() {
    isOpen.value = false
    _resolve?.(false)
  }

  return { isOpen, title, message, variant, confirm, onConfirm, onCancel }
}
