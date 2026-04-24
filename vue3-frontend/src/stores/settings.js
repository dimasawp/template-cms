import { defineStore } from 'pinia'
import { ref } from 'vue'
import { settingService } from '@/services/settingService'

export const useSettingsStore = defineStore('settings', () => {
  const siteName = ref('CMS Template')
  const maintenanceMode = ref(false)
  const registrationEnabled = ref(true)
  const enableWebsockets = ref(true)
  const appVersion = ref('1.1.0')
  const isLoading = ref(false)

  async function fetchSettings() {
    isLoading.value = true
    try {
      const { data: res } = await settingService.getPublic()
      const settings = res.data || {}
      
      if (settings.site_name) siteName.value = settings.site_name
      if (settings.maintenance_mode) maintenanceMode.value = settings.maintenance_mode === 'true'
      if (settings.registration_enabled) registrationEnabled.value = settings.registration_enabled === 'true'
      if (settings.enable_websockets !== undefined) enableWebsockets.value = settings.enable_websockets
      if (settings.app_version) appVersion.value = settings.app_version
    } catch (error) {
      console.error('Failed to fetch settings:', error)
    } finally {
      isLoading.value = false
    }
  }

  return {
    siteName,
    maintenanceMode,
    registrationEnabled,
    enableWebsockets,
    appVersion,
    isLoading,
    fetchSettings
  }
})
