import { defineStore } from 'pinia'
import { publicService } from '@/services/api'

export const useSettingsStore = defineStore('settings', {
  state: () => ({
    data: {},
    loaded: false,
  }),
  getters: {
    siteName(state) {
      return state.data.site_name || 'CMS Public'
    },
  },
  actions: {
    async fetch() {
      if (this.loaded) return
      try {
        const { data: res } = await publicService.getSettings()
        this.data = res.data || {}
        this.loaded = true
      } catch (e) {
        console.error('Failed to fetch settings', e)
      }
    },
  },
})
