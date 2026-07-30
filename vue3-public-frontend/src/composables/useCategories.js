import { ref } from 'vue'
import { publicService } from '@/services/api'

const categories = ref([])
const mapById = ref({})
const loaded = ref(false)
let promise = null

export function useCategories() {
  async function fetch() {
    if (loaded.value) return
    if (promise) return promise
    promise = (async () => {
      try {
        const { data: res } = await publicService.getCategories()
        const items = res.data?.items || []
        categories.value = items
        const m = {}
        for (const c of items) {
          m[c.id] = c
        }
        mapById.value = m
        loaded.value = true
      } catch (e) {
        console.error('Failed to fetch categories', e)
      }
    })()
    return promise
  }

  return { categories, mapById, loaded, fetch }
}
