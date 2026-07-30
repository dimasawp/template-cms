import { defineStore } from 'pinia'
import { publicService } from '@/services/api'

export const useCategoriesStore = defineStore('categories', {
  state: () => ({
    items: [],
    mapById: {},
    loaded: false,
  }),
  getters: {
    menuCategories(state) {
      return state.items.filter((c) => c.is_menu)
    },
  },
  actions: {
    async fetch() {
      if (this.loaded) return
      try {
        const { data: res } = await publicService.getCategories()
        const items = res.data?.items || []
        this.items = items
        const m = {}
        for (const c of items) {
          m[c.id] = c
        }
        this.mapById = m
        this.loaded = true
      } catch (e) {
        console.error('Failed to fetch categories', e)
      }
    },
  },
})
