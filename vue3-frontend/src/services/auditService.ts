import api from './api'

export interface AuditLog {
  id: number
  user_id: number | null
  action: string
  module: string
  item_id: string | null
  description: string | null
  payload_before: any | null
  payload_after: any | null
  ip_address: string | null
  user_agent: string | null
  created_at: string
  user: {
    id: number
    username: string
    full_name: string | null
  } | null
}

const auditService = {
  getLogs(params: { page?: number; limit?: number; module?: string; user_id?: number; action?: string }) {
    return api.get('/audit', { params })
  },

  getModules() {
    return api.get('/audit/modules')
  }
}

export default auditService
