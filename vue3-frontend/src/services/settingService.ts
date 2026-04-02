import api from './api'

export const settingService = {
  getPublic: () => api.get('/settings'),
  getRaw: () => api.get('/settings/raw'),
  update: (key: string, payload: { setting_value: string, description?: string }) => api.put(`/settings/${key}`, payload),
  bulkUpdate: (data: any[]) => api.post('/settings/bulk', { settings: data }),
}
