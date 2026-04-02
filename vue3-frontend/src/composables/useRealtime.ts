import { ref, onMounted, onUnmounted } from 'vue'
import { settingService } from '@/services/settingService'

export interface MaintenanceStatus {
  maintenance_mode: string
  maintenance_scheduled_at: string | null
}

export function useRealtime() {
  const status = ref<MaintenanceStatus>({
    maintenance_mode: 'false',
    maintenance_scheduled_at: null
  })
  
  const isWsConnected = ref(false)
  let socket: WebSocket | null = null
  let pollingInterval: any = null
  let reconnectTimeout: any = null

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
      // Try to reconnect WS after 30 seconds
      reconnectTimeout = setTimeout(connectWS, 30000)
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
    // Initial fetch to be safe
    fetchStatus()
    
    // Start with WS attempt
    connectWS()
  })

  onUnmounted(() => {
    if (socket) socket.close()
    if (pollingInterval) clearInterval(pollingInterval)
    if (reconnectTimeout) clearTimeout(reconnectTimeout)
  })

  return { status, isWsConnected }
}
