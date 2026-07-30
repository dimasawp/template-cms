import { ref } from 'vue'
import { publicService } from '@/services/api'

const settings = ref({})
const loaded = ref(false)
let promise = null

export function usePublicSettings() {
  async function fetch() {
    if (loaded.value) return
    if (promise) return promise
    promise = (async () => {
      try {
        const { data: res } = await publicService.getSettings()
        settings.value = res.data || {}
        loaded.value = true
      } catch (e) {
        console.error('Failed to fetch settings', e)
      }
    })()
    return promise
  }

  return { settings, loaded, fetch }
}
