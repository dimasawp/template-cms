import { ref, onMounted, onUnmounted, watch } from 'vue'
import { settingService } from '@/services/settingService'
import { useSettingsStore } from '@/stores/settings'

export function useRealtime() {
  const status = ref({
    maintenance_mode: 'false',
    maintenance_scheduled_at: null
  })
  
  const isWsConnected = ref(false)
  let socket = null
  let pollingInterval = null
  let reconnectTimeout = null

  const settingsStore = useSettingsStore()

  const fetchStatus = async () => {
    try {
      const { data: res } = await settingService.getPublic()
      status.value = {
        maintenance_mode: res.data.maintenance_mode || 'false',
        maintenance_scheduled_at: res.data.maintenance_scheduled_at || null
      }
    } catch { /* ignore */ }
  }

  const connectWS = () => {
    // Only connect if enabled by backend CONFIG
    if (!settingsStore.enableWebsockets) {
      console.log('[Realtime] WebSocket is disabled in config. Using polling.')
      startPolling()
      return
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = import.meta.env.VITE_API_BASE_URL 
      ? import.meta.env.VITE_API_BASE_URL.replace(/^https?:\/\//, '')
      : 'localhost:8000/api/v1'
    
    const wsUrl = `${protocol}//${host}/ws/notifications`
    
    socket = new WebSocket(wsUrl)

    socket.onopen = () => {
      console.log('[WS] Connected to notifications')
      isWsConnected.value = true
      if (pollingInterval) clearInterval(pollingInterval)
      if (reconnectTimeout) clearTimeout(reconnectTimeout)
    }

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'MAINTENANCE_UPDATE') {
          status.value = data.payload
        }
      } catch (err) {
        console.error('[WS] Error parsing message', err)
      }
    }

    socket.onclose = () => {
      console.warn('[WS] Connection closed. Falling back to polling...')
      isWsConnected.value = false
      startPolling()
      
      // Only attempt reconnect if still enabled
      if (settingsStore.enableWebsockets) {
        reconnectTimeout = setTimeout(connectWS, 30000)
      }
    }

    socket.onerror = () => {
      isWsConnected.value = false
    }
  }

  const startPolling = () => {
    if (pollingInterval) return
    console.log('[Realtime] Starting fallback polling...')
    fetchStatus() // Initial fetch
    pollingInterval = setInterval(fetchStatus, 60000) // Every 1 minute
  }

  onMounted(() => {
    // Wait until settings are initialized to know if WS is enabled or not
    if (settingsStore.isInitialized) {
      connectWS()
    } else {
      const stopWatch = watch(() => settingsStore.isInitialized, (initialized) => {
        if (initialized) {
          connectWS()
          stopWatch()
        }
      })
    }
    
    // Ensure we have initial status regardless of WS
    fetchStatus()
  })

  onUnmounted(() => {
    if (socket) socket.close()
    if (pollingInterval) clearInterval(pollingInterval)
    if (reconnectTimeout) clearTimeout(reconnectTimeout)
  })

  return { status, isWsConnected }
}
